#!/usr/bin/env python3
"""Cross-probe mechanical checks and the evidence index for this qualification bundle.

``probe.py`` records one probe. This script reads what every probe left behind and
answers the questions that span them: was each session a fresh context, do the charged
figures reconcile against the runtime's own, and what does the evidence index say about
each requirement. It asserts nothing a probe record does not already contain.

Usage::

    python3 scripts/qualify.py freshness --bundle DIR [--out FILE]
    python3 scripts/qualify.py reconcile --bundle DIR [--out FILE]
    python3 scripts/qualify.py index     --bundle DIR [--out FILE]
    python3 scripts/qualify.py retention --bundle DIR [--out FILE]
    python3 scripts/qualify.py chain     --bundle DIR [--out FILE]
    python3 scripts/qualify.py --self-test

``freshness`` (probe P02) reads each probe's root transcript and reports, mechanically,
how many user text messages it opens with, how many the harness injected afterwards, how
many summary records it carries, whether it was resumed or forked, and what non-prompt
context the runtime attached to it. A session is fresh when it opens with exactly one user
text message, carries no summary record and has no resume marker; a later user text message
is a background worker's completion arriving, counted apart. The attached context is
reported rather than judged: a cell's context is not only its prompt, and a freeze that does
not know what else is in there cannot claim its arms saw the same thing.

``reconcile`` (probe P10) reports, per metered probe, the recomputed per-request total,
the runtime's self-report, the difference, and whichever model in the result envelope
accounts for a difference the transcripts never saw. A residual with no named cause is a
violation, not a rounding note.

``retention`` (probe P17) checks that every probe in the bundle retained its exact request
before the process was created - the argv verbatim and the requested model, effort, dollar
allowance, restriction flag and allow list read back from it - and that at least one launch
that never started kept its record anyway. Retention is what #199 gap 1 is about, and a
bundle where one launch went unrecorded fails here rather than at settlement.

``chain`` (probe P26) re-establishes the frozen-input chain as far as this bundle reaches: the
template against its pin, and each rendered prompt against the template it came from, with the
no-unfilled-placeholder assertion as a precondition. The third link the specification asks for -
the same digest published in a public cell summary - has nothing to check, because no cell ran.

``index`` walks every probe directory and emits the evidence index: probe id, status,
the exact command, the exit status, the digests of its retained output, and its ledger
settlement where it had one.

Exit: 0 success, 1 on a content violation with one line per violation on stdout,
2 when an input cannot be read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


class Violation(ValueError):
    pass


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def probe_dirs(bundle: Path):
    """Every directory under ``probes/`` that holds a launch record, at any depth.

    A probe that needed several launches keeps them in subdirectories - P22 has one per arm
    and outcome - and each of those is a launch that has to be retained, metered and read
    for freshness like any other.
    """
    return sorted(p.parent for p in (bundle / "probes").rglob("launch.json"))


def root_transcript(directory: Path):
    listing = directory / "transcripts.txt"
    if not listing.exists():
        return None
    for line in listing.read_text(encoding="utf-8").splitlines()[1:]:
        path = Path(line.split(" sha256 ")[0])
        if "/subagents/" not in str(path):
            return path
    return None


def scan_transcript(path: Path):
    """Count what opened the session and what the harness injected into it later.

    Opening messages and injected ones are counted apart, because a session that
    dispatches a background worker receives that worker's completion as a further user
    message. That is the harness talking, not a second prompt, and conflating the two
    would either fail a fresh session or pass a resumed one.
    """
    opening = injected = summaries = 0
    seen_assistant = False
    first = None
    attachments = []
    resumed = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            continue
        kind = row.get("type")
        if kind == "summary":
            summaries += 1
        elif kind == "attachment":
            name = (row.get("attachment") or {}).get("type")
            if name and name not in attachments:
                attachments.append(name)
        elif kind == "assistant":
            seen_assistant = True
        elif kind == "user":
            content = (row.get("message") or {}).get("content")
            if isinstance(content, str):
                if seen_assistant:
                    injected += 1
                else:
                    opening += 1
                    if first is None:
                        first = content[:60]
        if row.get("isCompactSummary") or row.get("resumedFrom"):
            resumed = True
    return {"opening_user_text_messages": opening,
            "harness_injected_user_text_messages": injected,
            "summary_records": summaries,
            "resumed_or_forked": resumed, "first_user_message_prefix": first,
            "attached_context_types": attachments}


def freshness(bundle: Path, out: Path):
    report, violations = {}, []
    for directory in probe_dirs(bundle):
        record = json.loads((directory / "launch.json").read_text(encoding="utf-8"))
        transcript = root_transcript(directory)
        if transcript is None:
            continue
        scan = scan_transcript(transcript)
        scan["session_id"] = record["requested"]["session_id"]
        report[directory.name] = scan
        if (scan["opening_user_text_messages"] != 1 or scan["summary_records"]
                or scan["resumed_or_forked"]):
            violations.append(directory.name + " is not a fresh context")
    body = {
        "probe": "P02",
        "rule": ("a worker's context is fresh when its transcript opens with exactly one user "
                 "text message before its first assistant line, carries no summary record and "
                 "was not resumed or forked. Checked mechanically; the model is never asked "
                 "whether it is fresh. A later user text message is the harness injecting a "
                 "background worker's completion, counted separately and reported."),
        "attached_context_note": ("attached_context_types lists the non-prompt context the runtime "
                                  "itself put into the session. It is reported, not judged: these "
                                  "must be identical across arms or they are a confound, and a "
                                  "freeze names them rather than discovering them at grading."),
        "sessions": report,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    out.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for violation in violations:
        print(violation)
    print(("fresh: " + str(len(report)) + " sessions") if not violations else "")
    return 1 if violations else 0


def reconcile(bundle: Path, out: Path):
    rows, violations = {}, []
    for directory in probe_dirs(bundle):
        metering = directory / "metering.json"
        if not metering.exists():
            continue
        data = json.loads(metering.read_text(encoding="utf-8"))
        if data.get("charged_usd") is None:
            continue
        rows[directory.name] = {
            "session_id": data["session_id"],
            "transcripts": data["transcripts"],
            "recomputed_usd": data["recomputed_usd"],
            "self_report_usd": data["self_report_usd"],
            "difference_usd": data["residual_usd"],
            "charged_usd": data["charged_usd"],
            "per_role_usd": data.get("per_role_usd"),
            "per_model_usd": data.get("per_model_usd"),
            "difference_named_by": data.get("residual_named_by"),
        }
        residual = data.get("residual_usd")
        if residual and abs(residual) > 1e-7 and not data.get("residual_named_by"):
            violations.append(directory.name + " has an unnamed reconciliation residual")
    body = {
        "probe": "P10",
        "rule": ("settle from the runtime self-report and from the retained per-request records; "
                 "when they differ, charge the larger and name the difference. A residual recorded "
                 "as noise is a violation."),
        "probes": rows,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    out.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for violation in violations:
        print(violation)
    print("reconciled: " + str(len(rows)) + " metered probes" if not violations else "")
    return 1 if violations else 0


def retention(bundle: Path, out: Path):
    rows, violations = [], []
    for directory in probe_dirs(bundle):
        record = json.loads((directory / "launch.json").read_text(encoding="utf-8"))
        exit_path = directory / "exit.txt"
        observed = exit_path.read_text(encoding="utf-8").strip() if exit_path.exists() else None
        rows.append({
            "probe": record["probe"],
            "directory": "probes/" + directory.name,
            "retained_before_process_creation": record.get("retained_before_process_creation"),
            "argv_length": len(record.get("argv") or []),
            "requested": record["requested"],
            "observed_exit": observed,
            "launch_started": observed != "launch-failed",
        })
        if not record.get("retained_before_process_creation"):
            violations.append(directory.name + " does not claim retention before creation")
        if not record.get("argv"):
            violations.append(directory.name + " retained no argv")
    if not any(not row["launch_started"] for row in rows):
        violations.append("no launch that failed to start is retained in this bundle")
    body = {
        "probe": "P17",
        "rule": ("the requested model, effort, dollar allowance, restriction flag and allow list "
                 "are retained before process creation, per launch, and a record survives a "
                 "launch that never starts. The recorded argv proves what was requested; "
                 "transcripts and result envelopes establish what actually ran."),
        "launches": rows,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    out.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    for violation in violations:
        print(violation)
    if not violations:
        print("retained: " + str(len(rows)) + " launches, " +
              str(sum(not row["launch_started"] for row in rows)) + " of them never started")
    return 1 if violations else 0


PLACEHOLDER = re.compile(r"\{[A-Z][A-Z0-9_]*\}")


def chain(bundle: Path, out: Path):
    template = bundle / "dispatch-payload-contract.md"
    if not template.exists():
        print("the template is missing: " + str(template))
        return 1
    body_text = template.read_text(encoding="utf-8")
    block = body_text.partition("## Your review payload")[2]
    rendered, violations = [], []
    for directory in probe_dirs(bundle):
        prompt = directory / "dispatch.md"
        if not prompt.exists():
            continue
        text = prompt.read_text(encoding="utf-8")
        left = PLACEHOLDER.findall(text)
        # Normalise the two values the renderer fills, read from the prompt itself rather
        # than guessed from the probe's name, so the comparison is of the frozen bytes.
        normalised = text
        for key, token in (("attempt_id", "{ATTEMPT_ID}"), ("arm", "{ARM}")):
            match = re.search(r'"%s":\s*"([^"]*)"' % key, text)
            if match:
                normalised = normalised.replace('"%s": "%s"' % (key, match.group(1)),
                                                '"%s": "%s"' % (key, token))
        carries_block = block.strip() and block.strip()[:200] in text
        rendered.append({
            "directory": "probes/" + str(directory.relative_to(bundle / "probes")),
            "prompt_sha256": digest_bytes(prompt.read_bytes()),
            "normalised_sha256": digest_bytes(normalised.encode("utf-8")),
            "unfilled_placeholders": left,
            "carries_the_pinned_block": bool(carries_block),
        })
        if left:
            violations.append(str(prompt) + " has unfilled placeholders: " + ", ".join(left))
        if not carries_block:
            violations.append(str(prompt) + " does not carry the pinned template block")
    if not rendered:
        violations.append("no rendered prompt was found to check")
    shapes = {row["normalised_sha256"] for row in rendered}
    body = {
        "probe": "P26",
        "rule": ("the rendered prompt is tied to the pinned template it came from, no placeholder "
                 "is left unfilled, and the arms differ only in the attempt id and the arm label. "
                 "The third link - the same digest published in a public cell summary - is not "
                 "checkable here, because no cell ran."),
        "template": "dispatch-payload-contract.md",
        "template_sha256": digest_bytes(template.read_bytes()),
        "rendered": rendered,
        "distinct_normalised_shapes": len(shapes),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    out.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    for violation in violations:
        print(violation)
    if not violations:
        print("chain: " + str(len(rendered)) + " rendered prompts, " +
              str(len(shapes)) + " distinct shape(s) once the attempt id and arm label are "
              "normalised, no unfilled placeholder")
    return 1 if violations else 0


def index(bundle: Path, out: Path):
    ledger = json.loads((bundle / "ledger.json").read_text(encoding="utf-8"))
    settled = {}
    for event in ledger["events"]:
        for reference in event.get("rate_usage_evidence") or []:
            if event["operation"] == "settle":
                settled.setdefault(reference.split(":")[0], []).append(
                    {"actual_usd": event["actual_delta_usd"],
                     "uncertainty_usd": event["uncertainty_usd"],
                     "reservation_id": event["reservation_id"]})
    entries, missing = [], []
    for directory in probe_dirs(bundle):
        record = json.loads((directory / "launch.json").read_text(encoding="utf-8"))
        verdict_path = directory / "verdict.json"
        verdict = json.loads(verdict_path.read_text(encoding="utf-8")) if verdict_path.exists() else None
        if verdict is None:
            missing.append(directory.name + " has no verdict")
        retained = {}
        for item in sorted(directory.iterdir()):
            if item.is_file():
                retained[item.name] = digest_bytes(item.read_bytes())
        relative = "probes/" + directory.name
        entries.append({
            "probe": record["probe"],
            "directory": relative,
            "purpose": record["purpose"],
            "command": record["command_line"],
            "cwd": record["cwd"],
            "requested": record["requested"],
            "observed_exit": (directory / "exit.txt").read_text(encoding="utf-8").strip()
            if (directory / "exit.txt").exists() else None,
            "status": verdict["status"] if verdict else None,
            "summary": verdict["summary"] if verdict else None,
            "ledger": settled.get(relative + "/metering.json")
            or settled.get(relative + "/uncertainty-bound.json") or None,
            "retained_sha256": retained,
        })
    body = {
        "schema_version": "bounded-discovery-qualification-v1",
        "ticket": 207,
        "what_this_is": ("the evidence index for every probe this qualification ran: the exact "
                         "command, the runtime it ran against, the retained output by digest, the "
                         "verdict read from that output, and the ledger settlement where the probe "
                         "was paid. It is an index of evidence, not a readiness claim."),
        "runtime_inventory": "probes/P00-runtime-inventory/inventory.json",
        "ledger": "ledger.json",
        "probes": entries,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    out.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    for item in missing:
        print(item)
    print("indexed: " + str(len(entries)) + " probes")
    return 1 if missing else 0


def self_test():
    import tempfile
    failures = []

    def check(name, condition):
        if not condition:
            failures.append(name)

    with tempfile.TemporaryDirectory() as temporary:
        bundle = Path(temporary)
        (bundle / "probes" / "PX").mkdir(parents=True)
        transcript = bundle / "t.jsonl"
        transcript.write_text("\n".join([
            json.dumps({"type": "user", "message": {"role": "user", "content": "the prompt"}}),
            json.dumps({"type": "attachment", "attachment": {"type": "budget_usd"}}),
            json.dumps({"type": "assistant", "message": {"role": "assistant"}}),
        ]) + "\n", encoding="utf-8")
        (bundle / "probes" / "PX" / "launch.json").write_text(json.dumps(
            {"probe": "PX", "purpose": "p", "command_line": "c", "cwd": "/", "argv": ["x"],
             "retained_before_process_creation": True,
             "requested": {"session_id": "sid"}}) + "\n", encoding="utf-8")
        (bundle / "probes" / "PX" / "transcripts.txt").write_text(
            "session sid transcripts: 1\n" + str(transcript) + " sha256 x\n", encoding="utf-8")
        (bundle / "probes" / "PX" / "exit.txt").write_text("0\n", encoding="utf-8")
        out = bundle / "freshness.json"
        check("a one-prompt transcript is fresh", freshness(bundle, out) == 0)
        body = json.loads(out.read_text(encoding="utf-8"))
        check("the attached context is reported",
              body["sessions"]["PX"]["attached_context_types"] == ["budget_usd"])
        check("the opening prompt is counted alone",
              body["sessions"]["PX"]["opening_user_text_messages"] == 1)

        with open(transcript, "a", encoding="utf-8") as stream:
            stream.write(json.dumps({"type": "user", "message": {"role": "user",
                                                                 "content": "bg done"}}) + "\n")
        check("an injected completion is not a second prompt", freshness(bundle, out) == 0)
        body = json.loads(out.read_text(encoding="utf-8"))
        check("the injected message is reported",
              body["sessions"]["PX"]["harness_injected_user_text_messages"] == 1)

        with open(transcript, "a", encoding="utf-8") as stream:
            stream.write(json.dumps({"type": "summary", "summary": "s"}) + "\n")
        check("a summary record is not fresh", freshness(bundle, out) == 1)

        (bundle / "probes" / "PX" / "metering.json").write_text(json.dumps(
            {"session_id": "sid", "transcripts": 1, "recomputed_usd": 1.0,
             "self_report_usd": 1.5, "residual_usd": 0.5, "charged_usd": 1.5,
             "residual_named_by": None}) + "\n", encoding="utf-8")
        check("an unnamed residual is a violation",
              reconcile(bundle, bundle / "r.json") == 1)
        (bundle / "probes" / "PX" / "metering.json").write_text(json.dumps(
            {"session_id": "sid", "transcripts": 1, "recomputed_usd": 1.0,
             "self_report_usd": 1.5, "residual_usd": 0.5, "charged_usd": 1.5,
             "residual_named_by": {"some-model": 0.5}}) + "\n", encoding="utf-8")
        check("a named residual reconciles",
              reconcile(bundle, bundle / "r.json") == 0)

        check("a bundle with no failed launch fails retention",
              retention(bundle, bundle / "ret.json") == 1)
        (bundle / "probes" / "PY").mkdir()
        (bundle / "probes" / "PY" / "launch.json").write_text(json.dumps(
            {"probe": "PY", "purpose": "p", "command_line": "c", "cwd": "/", "argv": ["x"],
             "retained_before_process_creation": True,
             "requested": {"session_id": None}}) + "\n", encoding="utf-8")
        (bundle / "probes" / "PY" / "exit.txt").write_text("launch-failed\n", encoding="utf-8")
        check("a retained failed launch satisfies retention",
              retention(bundle, bundle / "ret.json") == 0)
        (bundle / "probes" / "PY" / "verdict.json").write_text(json.dumps(
            {"status": "unestablished", "summary": "s"}) + "\n", encoding="utf-8")

        (bundle / "ledger.json").write_text(json.dumps({"events": []}) + "\n", encoding="utf-8")
        check("a probe with no verdict blocks the index",
              index(bundle, bundle / "i.json") == 1)
        (bundle / "probes" / "PX" / "verdict.json").write_text(json.dumps(
            {"status": "established", "summary": "s"}) + "\n", encoding="utf-8")
        check("a complete index exits 0", index(bundle, bundle / "i.json") == 0)

    for failure in failures:
        print("FAIL", failure)
    print(("FAILED " + str(len(failures))) if failures else "ok: 12 checks")
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", nargs="?",
                        choices=("freshness", "reconcile", "retention", "chain", "index"))
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        if not args.operation or not args.bundle:
            raise Violation("an operation, --bundle, or --self-test is required")
        defaults = {"freshness": "probes/freshness.json", "reconcile": "probes/reconciliation.json",
                    "retention": "probes/retention.json", "chain": "probes/frozen-inputs.json",
                    "index": "evidence-index.json"}
        out = args.out or args.bundle / defaults[args.operation]
        return {"freshness": freshness, "reconcile": reconcile, "retention": retention,
                "chain": chain, "index": index}[args.operation](args.bundle, out)
    except Violation as error:
        print(str(error))
        return 1
    except (OSError, json.JSONDecodeError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
