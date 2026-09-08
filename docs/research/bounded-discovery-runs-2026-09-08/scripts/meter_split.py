#!/usr/bin/env python3
"""Price one attempt's transcripts per model and reconcile against a self-report.

A #138 cell mixes models: the primary runs on one model and arm B/C's finder and
verifiers on another. ``transcript_usage.py`` applies one price pair to every
transcript it is given, so a mixed-model attempt must be metered one model group
at a time and summed. This script is the mechanical adapter that does that.

For each transcript it asks ``agent_effort.py`` which models appear on that
transcript's assistant lines, refuses any transcript that mixes models (its
requests cannot be priced from one pair), groups the transcripts by model, runs
``transcript_usage.py --json`` once per group at that model's frozen rates, and
sums the group totals. Both helpers run by pinned path; no parser is copied.

Usage::

    python3 scripts/meter_split.py --rates rates.json --out split.json \\
        [--label LABEL] [--self-report USD] [--tolerance USD] \\
        [--role ROLE=TRANSCRIPT ...] TRANSCRIPT...

``--rates`` is the frozen rate card: ``{"observed_at": ..., "source": ...,
"models": {"<model id>": {"input_usd_per_mtok": "2", "output_usd_per_mtok": "10",
"cache_write_5m_mult": "1.25", "cache_write_1h_mult": "2.0",
"cache_read_mult": "0.1"}}}``. Multipliers default to the helper's own defaults.
``--role`` labels a transcript with the worker role it belongs to, so the output
carries the per-role split the method asks for; unlabelled transcripts are
reported under role ``unassigned``.

Output: a JSON document with the per-transcript, per-model and per-role costs,
the total, and — when ``--self-report`` is given — the difference against it.

Exit: 0 success, 1 on a content violation (mixed-model transcript, unpriced
model, reconciliation outside tolerance) with one line per violation on stdout,
2 when an input cannot be read or a helper fails, naming the command on stderr.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "tools"
EFFORT = TOOLS / "agent_effort.py"
USAGE = TOOLS / "transcript_usage.py"
# agent_effort.py prints: "<name> lines=<n> models=<m>×<n>[,<m>×<n>] efforts=..."
SCAN = re.compile(r"^(?P<name>\S+) lines=(?P<lines>\d+) models=(?P<models>\S+) efforts=(?P<efforts>\S+)$")


class Violation(ValueError):
    pass


def run(command, as_json=False):
    """Run a pinned helper. A helper that fails is an input error, not a finding."""
    result = subprocess.run([sys.executable, *command], capture_output=True, text=True, encoding="utf-8")
    failed = result.returncode != 0
    if not failed and as_json:
        try:
            return json.loads(result.stdout)
        except ValueError:
            failed = True
    if failed:
        print(" ".join(str(part) for part in command), file=sys.stderr)
        print((result.stderr or result.stdout).strip(), file=sys.stderr)
        raise SystemExit(2)
    return result.stdout


def observed_models(transcripts):
    """Map each transcript to the single model observed on its assistant lines."""
    output = run([EFFORT, *transcripts])
    seen = {}
    for line in output.splitlines():
        match = SCAN.match(line.strip())
        if not match:
            continue
        models = [part.rsplit("×", 1)[0] for part in match.group("models").split(",")]
        seen[match.group("name")] = models
    result, violations = {}, []
    for transcript in transcripts:
        models = seen.get(Path(transcript).name)
        if not models:
            violations.append("no assistant lines scanned for " + str(transcript))
        elif len(models) > 1:
            violations.append("transcript mixes models %s: %s" % (",".join(models), transcript))
        else:
            result[str(transcript)] = models[0]
    if violations:
        raise Violation("\n".join(violations))
    return result


def price_group(transcripts, rate):
    prices = "%s,%s" % (rate["input_usd_per_mtok"], rate["output_usd_per_mtok"])
    command = [USAGE, *transcripts, "--prices", prices, "--json"]
    for flag, key, default in (("--cache-write-mult", "cache_write_5m_mult", "1.25"),
                               ("--cache-write-1h-mult", "cache_write_1h_mult", "2.0"),
                               ("--cache-read-mult", "cache_read_mult", "0.1")):
        command += [flag, str(rate.get(key, default))]
    return run(command, as_json=True)


def split(transcripts, rates, roles, label, self_report, tolerance):
    models = observed_models(transcripts)
    unpriced = sorted({model for model in models.values() if model not in rates["models"]})
    if unpriced:
        raise Violation("\n".join("no frozen rate for model " + model for model in unpriced))
    groups, per_transcript, total = {}, {}, Decimal(0)
    for model in sorted(set(models.values())):
        members = [path for path in transcripts if models[str(path)] == model]
        rate = rates["models"][model]
        group = price_group(members, rate)
        groups[model] = {"transcripts": [str(path) for path in members],
                         "rates": rate, "cost_usd": str(group["total"]["cost"]),
                         "turns": group["total"]["turns"]}
        total += Decimal(str(group["total"]["cost"]))
        for member in members:
            one = price_group([member], rate)
            per_transcript[str(member)] = {"model": model, "role": roles.get(str(member), "unassigned"),
                                           "cost_usd": str(one["total"]["cost"]),
                                           "turns": one["total"]["turns"]}
    per_role = {}
    for path, record in per_transcript.items():
        entry = per_role.setdefault(record["role"], {"transcripts": [], "cost_usd": Decimal(0)})
        entry["transcripts"].append(path)
        entry["cost_usd"] += Decimal(record["cost_usd"])
    for entry in per_role.values():
        entry["cost_usd"] = str(entry["cost_usd"])
    report = {"schema_version": "bounded-discovery-v1", "label": label,
              "rates_observed_at": rates.get("observed_at"), "rates_source": rates.get("source"),
              "per_transcript": per_transcript, "per_model": groups, "per_role": per_role,
              "total_cost_usd": str(total)}
    if self_report is not None:
        difference = total - Decimal(self_report)
        report["self_report_usd"] = str(Decimal(self_report))
        report["difference_usd"] = str(difference)
        report["within_tolerance"] = abs(difference) <= Decimal(tolerance)
        report["tolerance_usd"] = str(Decimal(tolerance))
        if not report["within_tolerance"]:
            report["violation"] = "recomputed total differs from the self-report by more than the tolerance"
    return report


def self_test():
    """Check the argument surface and the scan parser without a paid session."""
    checks = []
    match = SCAN.match("root.jsonl lines=4 models=claude-sonnet-5×4 efforts=high×4")
    checks.append(("scan parses one model", match is not None and
                   match.group("models") == "claude-sonnet-5×4"))
    mixed = SCAN.match("m.jsonl lines=3 models=a×1,b×2 efforts=high×3")
    checks.append(("scan parses two models", mixed is not None and
                   [p.rsplit("×", 1)[0] for p in mixed.group("models").split(",")] == ["a", "b"]))
    checks.append(("helpers resolve", EFFORT.is_file() and USAGE.is_file()))
    try:
        run([USAGE, "--prices", "not,numbers", "/nonexistent-transcript.jsonl"], as_json=True)
        checks.append(("a failing helper exits 2", False))
    except SystemExit as exit_code:
        checks.append(("a failing helper exits 2", exit_code.code == 2))
    for name, ok in checks:
        print(("ok   " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in checks) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("transcripts", nargs="*")
    parser.add_argument("--rates")
    parser.add_argument("--out")
    parser.add_argument("--label", default="")
    parser.add_argument("--role", action="append", default=[],
                        metavar="ROLE=TRANSCRIPT", help="label one transcript with its worker role")
    parser.add_argument("--self-report", help="the runtime's own cost figure, for reconciliation")
    parser.add_argument("--tolerance", default="0.01")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.transcripts or not args.rates:
        parser.error("transcripts and --rates are required")
    try:
        rates = json.loads(Path(args.rates).read_text(encoding="utf-8"))
        for transcript in args.transcripts:
            if not Path(transcript).is_file():
                raise FileNotFoundError(transcript)
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 2
    roles = {}
    for pair in args.role:
        if "=" not in pair:
            parser.error("--role takes ROLE=TRANSCRIPT")
        role, path = pair.split("=", 1)
        roles[path] = role
    try:
        report = split(args.transcripts, rates, roles, args.label, args.self_report, args.tolerance)
    except Violation as exc:
        print(str(exc))
        return 1
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0 if report.get("within_tolerance", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
