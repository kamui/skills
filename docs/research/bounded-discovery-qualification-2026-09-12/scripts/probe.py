#!/usr/bin/env python3
"""Launch one qualification probe, retaining its exact request before the process starts.

Every probe in this bundle is recorded the same way, because the #199 gap-1 failure was
that nothing wrote down what a launch *asked for*. This script writes the launch record
with ``O_EXCL``, flushes and fsyncs it, and only then creates the process — so a launch
that never starts still has a record, and a record can never be a reconstruction.

Usage::

    python3 scripts/probe.py launch --probe-dir DIR --id P15 --purpose TEXT
        [--workdir DIR] [--session-id UUID] [--env KEY=VALUE ...]
        [--inventory FILE] [--expect-exit N] -- COMMAND [ARG ...]
    python3 scripts/probe.py meter --probe-dir DIR --rates FILE
        [--role ROLE=TRANSCRIPT_SUBSTRING ...] [--projects-dir DIR]
    python3 scripts/probe.py verdict --probe-dir DIR --status STATUS --summary TEXT
        [--establishes TEXT] [--residual TEXT] [--refuted-by TEXT]
    python3 scripts/probe.py --self-test

``launch`` writes ``launch.json`` (the retained request), then ``stdout.txt``,
``stderr.txt``, ``exit.txt`` and ``timing.json``. When the argv contains
``--output-format json`` the parsed envelope is also written to ``result.json``.

``meter`` locates the session transcript and its sub-agent transcripts from the
session id in ``launch.json``, digests each one, records the observed model and
effort per transcript with ``agent_effort.py``, prices them per model group with
``meter_split.py`` at the pinned rate card, and writes ``metering.json`` holding the
recomputed total, the runtime self-report, the envelope's per-model usage, the charged
figure (the larger of the two, which is the settlement rule) and the named residual.

``verdict`` writes ``verdict.json``. ``--status`` is ``established``,
``unestablished`` or ``refuted``; a probe whose process did not complete may only be
recorded ``unestablished``, and this script enforces that from ``exit.txt``.

Exit: 0 success, 1 on a content violation with one line per violation on stdout,
2 when an input cannot be read or a subprocess fails, naming the command on stderr.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[2]
TOOLS = RESEARCH / "tools"
RUNS = RESEARCH / "bounded-discovery-runs-2026-09-08" / "scripts"
STATUSES = ("established", "unestablished", "refuted")


class Violation(ValueError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def requested_settings(argv):
    """Read back what the argv asks the runtime for, without interpreting it."""
    wanted = {"model": None, "effort": None, "max_budget_usd": None, "restricted": False,
              "tools": None, "allowed_tools": [], "disallowed_tools": [], "add_dir": [],
              "permission_prompts": None, "session_id": None, "output_format": None,
              "agents_json_sha256": None, "print_mode": False, "resume": None}
    index = 0
    while index < len(argv):
        token = argv[index]
        pairs = {"--model": "model", "--effort": "effort", "--max-budget-usd": "max_budget_usd",
                 "--permission-prompts": "permission_prompts", "--session-id": "session_id",
                 "--output-format": "output_format", "--tools": "tools", "--resume": "resume"}
        if token in pairs and index + 1 < len(argv):
            wanted[pairs[token]] = argv[index + 1]
            index += 2
            continue
        if token == "--restricted":
            wanted["restricted"] = True
        elif token in ("-p", "--print"):
            wanted["print_mode"] = True
        elif token in ("--allowedTools", "--allowed-tools", "--disallowedTools",
                       "--disallowed-tools", "--add-dir"):
            key = {"--allowedTools": "allowed_tools", "--allowed-tools": "allowed_tools",
                   "--disallowedTools": "disallowed_tools",
                   "--disallowed-tools": "disallowed_tools", "--add-dir": "add_dir"}[token]
            index += 1
            while index < len(argv) and not argv[index].startswith("--"):
                wanted[key].append(argv[index])
                index += 1
            continue
        elif token == "--agents" and index + 1 < len(argv):
            wanted["agents_json_sha256"] = hashlib.sha256(
                argv[index + 1].encode("utf-8")).hexdigest()
            index += 2
            continue
        index += 1
    return wanted


def launch(args, argv):
    directory = Path(args.probe_dir)
    directory.mkdir(parents=True, exist_ok=True)
    record_path = directory / "launch.json"
    workdir = Path(args.workdir).resolve() if args.workdir else Path.cwd()
    additions = {}
    for item in args.env or []:
        key, _, value = item.partition("=")
        if not key or not _:
            raise Violation("--env takes KEY=VALUE")
        additions[key] = value
    settings = requested_settings(argv)
    if args.session_id:
        settings["session_id"] = args.session_id
    record = {
        "schema_version": "bounded-discovery-qualification-v1",
        "probe": args.id,
        "purpose": args.purpose,
        "retained_at": now(),
        "retained_before_process_creation": True,
        "cwd": str(workdir),
        "argv": list(argv),
        "command_line": " ".join(shlex.quote(token) for token in argv),
        "env_additions": {key: ("<set>" if "TOKEN" in key or "KEY" in key else value)
                          for key, value in additions.items()},
        "requested": settings,
        "runtime_inventory": args.inventory,
        "expect_exit": args.expect_exit,
    }
    body = json.dumps(record, indent=2) + "\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        handle = os.open(record_path, flags, 0o644)
    except FileExistsError:
        raise Violation("launch record already exists: " + str(record_path))
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())
    environment = dict(os.environ)
    environment.update(additions)
    started = time.time()
    try:
        # stdin is /dev/null, as the frozen dispatch shape has it: a headless session must
        # never be able to wait on an operator.
        completed = subprocess.run(argv, cwd=str(workdir), env=environment, text=True,
                                   capture_output=True, stdin=subprocess.DEVNULL)
    except OSError as error:
        (directory / "exit.txt").write_text("launch-failed\n", encoding="utf-8")
        (directory / "stderr.txt").write_text(str(error) + "\n", encoding="utf-8")
        (directory / "timing.json").write_text(json.dumps(
            {"started_at": started, "elapsed_seconds": time.time() - started,
             "launch_failed": True}, indent=2) + "\n", encoding="utf-8")
        print("process could not be created; the launch record is retained anyway")
        return 1
    elapsed = time.time() - started
    (directory / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (directory / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
    (directory / "exit.txt").write_text(str(completed.returncode) + "\n", encoding="utf-8")
    (directory / "timing.json").write_text(json.dumps(
        {"started_at": datetime.fromtimestamp(started, timezone.utc).isoformat(),
         "elapsed_seconds": round(elapsed, 3), "exit_code": completed.returncode},
        indent=2) + "\n", encoding="utf-8")
    if settings["output_format"] == "json" and completed.stdout.strip():
        try:
            (directory / "result.json").write_text(
                json.dumps(json.loads(completed.stdout), indent=2) + "\n", encoding="utf-8")
        except json.JSONDecodeError:
            print("stdout is not the JSON envelope the argv asked for")
    print("exit", completed.returncode, "in", round(elapsed, 3), "s ->", directory)
    return 0


def transcripts_for(session_id, projects_dir):
    root = Path(projects_dir).expanduser()
    found = []
    for candidate in sorted(root.glob("*/" + session_id + ".jsonl")):
        found.append(candidate)
        subagents = candidate.parent / session_id / "subagents"
        found.extend(sorted(subagents.glob("agent-*.jsonl")))
    return found


def run(command):
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode == 2:
        print(" ".join(command), file=sys.stderr)
        raise SystemExit(2)
    return result


def meter(args):
    directory = Path(args.probe_dir)
    record = json.loads((directory / "launch.json").read_text(encoding="utf-8"))
    session = record["requested"]["session_id"]
    if not session:
        raise Violation("this probe's launch record names no session id")
    found = transcripts_for(session, args.projects_dir)
    if not found:
        raise Violation("no transcript found for session " + session)
    lines = ["session " + session + " transcripts: " + str(len(found))]
    for path in found:
        lines.append(str(path) + " sha256 " + digest(path))
    (directory / "transcripts.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    effort = run([sys.executable, str(TOOLS / "agent_effort.py")] + [str(p) for p in found])
    (directory / "effort.txt").write_text(effort.stdout, encoding="utf-8")
    self_report = None
    envelope_models = {}
    result_path = directory / "result.json"
    if result_path.exists():
        envelope = json.loads(result_path.read_text(encoding="utf-8"))
        self_report = envelope.get("total_cost_usd")
        usage = envelope.get("modelUsage") or {}
        for model, entry in usage.items():
            envelope_models[model] = entry.get("costUSD")
    command = [sys.executable, str(RUNS / "meter_split.py"), "--rates", args.rates,
               "--out", str(directory / "usage-split.json"), "--label", record["probe"]]
    for role in args.role or []:
        name, _, fragment = role.partition("=")
        matches = [p for p in found if fragment in str(p)]
        if len(matches) != 1:
            raise Violation("--role " + role + " matched " + str(len(matches)) + " transcripts")
        command += ["--role", name + "=" + str(matches[0])]
    command += [str(p) for p in found]
    split = run(command)
    (directory / "meter-split-stdout.txt").write_text(split.stdout, encoding="utf-8")
    recomputed = None
    per_role = per_model = {}
    if (directory / "usage-split.json").exists():
        data = json.loads((directory / "usage-split.json").read_text(encoding="utf-8"))
        recomputed = data.get("total_cost_usd")
        per_role = {name: entry.get("cost_usd")
                    for name, entry in (data.get("per_role") or {}).items()}
        per_model = {name: entry.get("cost_usd")
                     for name, entry in (data.get("per_model") or {}).items()}
    charged = None
    if recomputed is not None and self_report is not None:
        charged = max(float(recomputed), float(self_report))
    elif recomputed is not None:
        charged = float(recomputed)
    elif self_report is not None:
        charged = float(self_report)
    metering = {
        "probe": record["probe"],
        "session_id": session,
        "transcripts": len(found),
        "recomputed_usd": recomputed,
        "per_role_usd": per_role,
        "per_model_usd": per_model,
        "self_report_usd": self_report,
        "envelope_model_usage_usd": envelope_models,
        "charged_usd": charged,
        "residual_usd": (None if recomputed is None or self_report is None
                         else round(float(self_report) - float(recomputed), 9)),
        # The envelope reports the long-context variant (``claude-opus-5[1m]``) where the
        # transcript says ``claude-opus-5``; the same model is not an unexplained residual,
        # so the comparison strips the suffix before asking what the transcripts never saw.
        "residual_named_by": ({model: cost for model, cost in envelope_models.items()
                               if model.partition("[")[0] not in
                               {name.partition("[")[0] for name in per_model}} or None),
        "settlement_rule": ("charge the larger of the runtime self-report and the recomputed "
                            "per-request total, and name the difference"),
        "metered_at": now(),
    }
    (directory / "metering.json").write_text(json.dumps(metering, indent=2) + "\n",
                                             encoding="utf-8")
    print(json.dumps(metering, indent=2))
    return 0 if split.returncode == 0 else 1


def verdict(args):
    directory = Path(args.probe_dir)
    if args.status not in STATUSES:
        raise Violation("status must be one of " + ", ".join(STATUSES))
    exit_path = directory / "exit.txt"
    completed = exit_path.exists() and exit_path.read_text(encoding="utf-8").strip() not in (
        "launch-failed",)
    record = json.loads((directory / "launch.json").read_text(encoding="utf-8")) if (
        directory / "launch.json").exists() else {}
    expected = record.get("expect_exit")
    observed = exit_path.read_text(encoding="utf-8").strip() if exit_path.exists() else None
    if args.status == "established" and not completed:
        raise Violation("a probe whose process did not complete establishes nothing")
    if (args.status == "established" and expected is not None
            and observed is not None and str(expected) != observed):
        raise Violation("exit " + observed + " is not the expected " + str(expected) +
                        "; an unexpected exit establishes nothing until it is explained")
    body = {
        "probe": record.get("probe", args.probe_dir),
        "status": args.status,
        "summary": args.summary,
        "establishes": args.establishes,
        "residual": args.residual,
        "refuted_by": args.refuted_by,
        "observed_exit": observed,
        "expected_exit": expected,
        "read_from": "the probe's own retained output, not asserted beside it",
        "recorded_at": now(),
    }
    (directory / "verdict.json").write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    print(args.status, "->", directory)
    return 0


def self_test():
    import tempfile
    failures = []

    def check(name, condition):
        if not condition:
            failures.append(name)

    here = [sys.executable, str(Path(__file__).resolve())]
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        one = base / "p-ok"
        result = subprocess.run(here + ["launch", "--probe-dir", str(one), "--id", "PT1",
                                        "--purpose", "echo", "--", "/bin/echo", "hello"],
                                text=True, capture_output=True)
        check("a launch that runs exits 0", result.returncode == 0)
        check("the record is written", (one / "launch.json").exists())
        check("stdout is retained", (one / "stdout.txt").read_text(encoding="utf-8") == "hello\n")
        check("the exit status is retained", (one / "exit.txt").read_text(encoding="utf-8") == "0\n")
        record = json.loads((one / "launch.json").read_text(encoding="utf-8"))
        check("the argv is verbatim", record["argv"] == ["/bin/echo", "hello"])
        check("retention precedes creation", record["retained_before_process_creation"])

        again = subprocess.run(here + ["launch", "--probe-dir", str(one), "--id", "PT1",
                                       "--purpose", "echo", "--", "/bin/echo", "hello"],
                               text=True, capture_output=True)
        check("a second launch into one record is refused", again.returncode == 1)

        two = base / "p-missing"
        result = subprocess.run(here + ["launch", "--probe-dir", str(two), "--id", "PT2",
                                        "--purpose", "absent binary", "--",
                                        str(base / "definitely-absent")],
                                text=True, capture_output=True)
        check("a failed launch exits 1", result.returncode == 1)
        check("a failed launch keeps its record", (two / "launch.json").exists())
        check("a failed launch records launch-failed",
              (two / "exit.txt").read_text(encoding="utf-8") == "launch-failed\n")
        result = subprocess.run(here + ["verdict", "--probe-dir", str(two), "--status",
                                        "established", "--summary", "x"],
                                text=True, capture_output=True)
        check("an incomplete probe cannot be established", result.returncode == 1
              and "establishes nothing" in result.stdout)
        result = subprocess.run(here + ["verdict", "--probe-dir", str(two), "--status",
                                        "unestablished", "--summary", "the binary is absent"],
                                text=True, capture_output=True)
        check("an incomplete probe records unestablished", result.returncode == 0)

        three = base / "p-exit"
        subprocess.run(here + ["launch", "--probe-dir", str(three), "--id", "PT3", "--purpose",
                               "false", "--expect-exit", "0", "--", "/usr/bin/false"],
                       text=True, capture_output=True)
        result = subprocess.run(here + ["verdict", "--probe-dir", str(three), "--status",
                                        "established", "--summary", "x"],
                                text=True, capture_output=True)
        check("an unexpected exit cannot be established", result.returncode == 1)

        settings = requested_settings(shlex.split(
            'claude -p --model claude-sonnet-5 --effort high --restricted '
            '--tools "Bash,Read" --allowedTools "Write" "Bash(git:*)" --add-dir /a /b '
            '--permission-prompts none --max-budget-usd 0.25 --output-format json prompt'))
        check("the model is read back", settings["model"] == "claude-sonnet-5")
        check("the effort is read back", settings["effort"] == "high")
        check("the restriction flag is read back", settings["restricted"] is True)
        check("the allowances are read back",
              settings["allowed_tools"] == ["Write", "Bash(git:*)"])
        check("the roots are read back", settings["add_dir"] == ["/a", "/b"])
        check("the ceiling is read back", settings["max_budget_usd"] == "0.25")
        check("the tool list is read back", settings["tools"] == "Bash,Read")

    for failure in failures:
        print("FAIL", failure)
    print(("FAILED " + str(len(failures))) if failures else "ok: 15 checks")
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", nargs="?", choices=("launch", "meter", "verdict"))
    parser.add_argument("--probe-dir")
    parser.add_argument("--id")
    parser.add_argument("--purpose")
    parser.add_argument("--workdir")
    parser.add_argument("--session-id")
    parser.add_argument("--env", action="append")
    parser.add_argument("--inventory", default="probes/P00-runtime-inventory/inventory.json")
    parser.add_argument("--expect-exit", type=int)
    parser.add_argument("--rates")
    parser.add_argument("--role", action="append")
    parser.add_argument("--projects-dir", default="~/.claude/projects")
    parser.add_argument("--status")
    parser.add_argument("--summary")
    parser.add_argument("--establishes")
    parser.add_argument("--residual")
    parser.add_argument("--refuted-by")
    parser.add_argument("--self-test", action="store_true")
    # The launched command follows a literal "--"; argparse never sees it, so a flag the
    # probe passes to `claude` can never be mistaken for a flag of this script.
    own, _, rest = (sys.argv[1:], None, [])
    if "--" in sys.argv[1:]:
        cut = sys.argv[1:].index("--")
        own, rest = sys.argv[1:cut + 1], sys.argv[cut + 2:]
    args = parser.parse_args(own)
    if args.self_test:
        return self_test()
    try:
        if args.operation == "launch":
            argv = rest
            if not argv:
                raise Violation("launch needs a command after --")
            return launch(args, argv)
        if args.operation == "meter":
            return meter(args)
        if args.operation == "verdict":
            return verdict(args)
        raise Violation("an operation or --self-test is required")
    except Violation as error:
        print(str(error))
        return 1
    except (OSError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
