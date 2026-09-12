#!/usr/bin/env python3
"""The complete shutdown gate: nothing is unsealed until every probe established it.

#199 gap 5. The pilot's closeout gate passed a workspace sweep that exited 1 on a
directory it could not enter, swept a root the pilot never used, and excused an
unreachable container runtime. This gate has no corroborating class and no
exception: the recorded-root check, the process check, the container check and
the ledger checks are all required, each must complete, and each must establish
its own condition. A missing executable, a permission error, a timeout, an
unreachable runtime, a root record that is not the pinned one and a probe that
did not finish all block clearance.

Usage::

    python3 scripts/shutdown.py check --ledger FILE --roots-record FILE
        --roots-sha256 DIGEST --seal PATH --out GATE
        [--container-prefix PREFIX] [--container-cli NAME] [--marker TEXT ...]
        [--timeout SECONDS] [--probes-from FILE] [--raw-out FILE]
    python3 scripts/shutdown.py authorize --gate GATE [--max-age-seconds N]
    python3 scripts/shutdown.py --self-test

``--roots-sha256`` is the digest the dispatch record pinned for this study's
unsealed root record; a record that does not match it is not the one the study
ran under. ``--seal`` is the sealed evidence the gate would release: the root
record must lie outside it, or the gate would be reading what it is gating.
``--probes-from`` re-scores a retained raw capture instead of probing the host,
for replay; it never turns an incomplete capture into a pass.

``authorize`` is what a later step calls before opening the seal: it re-reads a
recorded gate and exits 0 only when that gate cleared and is still fresh.

Exit: 0 the gate cleared, 1 a check refused clearance with one line each on
stdout, 2 an input cannot be read or an output cannot be written.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ARTIFACT_ID = "bounded-discovery-shutdown-gate"
SCHEMA_VERSION = "bounded-discovery-v1"
DEFAULT_CONTAINER_PREFIX = "bd"
DEFAULT_MARKERS = ("run_cell.py",)
DEFAULT_TIMEOUT = 120

CHECKS = ("the root record is the one pinned before dispatch",
          "the root record is retained outside the evidence seal",
          "every recorded cell root is absent",
          "no reviewer or coordinator process is running",
          "no cell container is running",
          "every opened attempt is closed on the ledger",
          "no budget reservation is outstanding",
          "the ledger chain is unbroken through its last event",
          "the ledger records a terminal stop",
          "no ledger event was appended after the host was probed")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_roots_module():
    """roots.py is a sibling script, loaded by path because it is pinned, not installed."""
    path = Path(__file__).resolve().with_name("roots.py")
    spec = importlib.util.spec_from_file_location("bd_roots", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def capture(argv, timeout=DEFAULT_TIMEOUT) -> dict:
    """Run one probe, recording how it ended. Nothing here decides a check: a
    probe that did not run, timed out or exited non-zero has established nothing
    and its empty output is not an absence."""
    record = {"command": [str(part) for part in argv], "exit_code": None,
              "stdout": "", "stderr": "", "ran": False, "timed_out": False}
    try:
        done = subprocess.run([str(part) for part in argv], capture_output=True, text=True,
                              encoding="utf-8", timeout=timeout, check=False)
        record.update(exit_code=done.returncode, stdout=done.stdout or "",
                      stderr=done.stderr or "", ran=True)
    except subprocess.TimeoutExpired:
        record.update(stderr="probe did not finish within %s seconds" % timeout,
                      timed_out=True)
    except FileNotFoundError:
        record.update(stderr="command not found")
    except (OSError, subprocess.SubprocessError) as exc:
        record.update(stderr=str(exc))
    return record


def probe_completed(probe) -> bool:
    return bool(probe.get("ran")) and probe.get("exit_code") == 0


def probe_fields(probe) -> dict:
    """What a probe contributes to the public record. Raw output stays out of it:
    a process command line or a container name can name a target slot."""
    return {"command": probe.get("command"), "exit_code": probe.get("exit_code"),
            "probe_ran": bool(probe.get("ran")), "timed_out": bool(probe.get("timed_out")),
            "probe_completed": probe_completed(probe),
            "output_sha256": digest(probe.get("stdout", "") + probe.get("stderr", ""))}


def incomplete_detail(probe, subject) -> str:
    if probe.get("timed_out"):
        return "the %s probe timed out, so it established nothing" % subject
    if not probe.get("ran"):
        return ("the %s probe did not run (%s), so it established nothing"
                % (subject, probe.get("stderr", "").strip() or "no reason recorded"))
    return ("the %s probe exited %s, so what it did not inspect is unestablished"
            % (subject, probe.get("exit_code")))


def live_probes(container_cli, timeout) -> dict:
    return {"captured_at": now(), "self_pid": os.getpid(),
            "processes": capture(["ps", "-eo", "pid=,ppid=,command="], timeout),
            "containers": capture([container_cli, "ps", "-a", "--no-trunc",
                                   "--format", "{{.Names}}\t{{.Status}}"], timeout)}


def parse_processes(probe) -> dict:
    table = {}
    for line in probe.get("stdout", "").splitlines():
        fields = line.strip().split(None, 2)
        if len(fields) < 3 or not fields[0].isdigit() or not fields[1].isdigit():
            continue
        table[int(fields[0])] = (int(fields[1]), fields[2])
    return table


def own_ancestry(table, self_pid) -> set:
    """This gate's own pid and every ancestor of it: the gate names the recorded
    roots on its own command line, and a shell repeats them."""
    ancestry, pid, seen = {int(self_pid)}, int(self_pid), set()
    while pid in table and pid not in seen:
        seen.add(pid)
        pid = table[pid][0]
        if pid <= 0:
            break
        ancestry.add(pid)
    return ancestry


def reviewer_processes(probe, self_pid, markers) -> dict:
    table = parse_processes(probe)
    ancestry = own_ancestry(table, self_pid)
    live, excluded = [], []
    for pid, (_, command) in table.items():
        if not any(marker and marker in command for marker in markers):
            continue
        (excluded if pid in ancestry else live).append(pid)
    return {"live": sorted(live), "own_ancestry": sorted(excluded)}


def cell_containers(probe, prefix) -> list:
    found = []
    for line in probe.get("stdout", "").splitlines():
        name, _, status = line.partition("\t")
        if name.strip().startswith(prefix):
            found.append({"status": status.strip() or "unknown"})
    return found


def usd(value) -> Decimal:
    try:
        return Decimal(str(value or "0"))
    except InvalidOperation:
        raise ValueError("the ledger carries an unreadable USD amount")


def ledger_state(ledger) -> dict:
    opened, closed = [], []
    reservations = Decimal(0)
    stops = 0
    chain_ok, broken_at, previous = True, None, None
    for index, event in enumerate(ledger.get("events", [])):
        if chain_ok and event.get("previous_event_id") != previous:
            chain_ok, broken_at = False, index
        previous = event.get("event_id")
        operation = event.get("operation")
        if operation == "attempt-open":
            opened.append(event.get("attempt_id"))
        elif operation == "attempt-close":
            closed.append(event.get("attempt_id"))
        elif operation == "stop":
            stops += 1
        reservations += usd(event.get("reservation_delta_usd"))
    times = [event.get("observed_at") for event in ledger.get("events", [])
             if event.get("observed_at")]
    return {"opened": opened, "closed": closed,
            "unclosed": [a for a in opened if a not in closed],
            "reservation_balance": reservations, "stops": stops,
            "chain_intact": chain_ok, "broken_at": broken_at,
            "event_count": len(ledger.get("events", [])),
            "latest_event_at": max(times) if times else ""}


def record_checks(roots_record, roots_sha256, seal, roots_module) -> list:
    """The recorded-root checks: the pinned record, where it lives, and the roots."""
    checks = []
    record_path = Path(roots_record)
    try:
        actual = hashlib.sha256(record_path.read_bytes()).hexdigest()
        matched = actual == (roots_sha256 or "").strip().lower()
        checks.append({"check": CHECKS[0], "passed": matched, "probe_completed": True,
                       "record_sha256": actual, "pinned_sha256": roots_sha256,
                       "detail": ("the root record matches the digest pinned outside the seal"
                                  if matched else
                                  "the root record digest is %s, not the pinned %s; this is "
                                  "not the record the study dispatched under"
                                  % (actual, roots_sha256))})
    except OSError as exc:
        checks.append({"check": CHECKS[0], "passed": False, "probe_completed": False,
                       "detail": "the root record could not be read: %s" % exc})
        checks.append({"check": CHECKS[1], "passed": False, "probe_completed": False,
                       "detail": "the root record could not be read, so where it lives is "
                                 "unestablished"})
        checks.append({"check": CHECKS[2], "passed": False, "probe_completed": False,
                       "detail": "the root record could not be read, so no root was probed"})
        return checks

    seal_path = Path(seal)
    try:
        resolved_record = record_path.resolve(strict=True)
        resolved_seal = seal_path.resolve(strict=True)
        inside = resolved_record == resolved_seal or resolved_seal in resolved_record.parents
        checks.append({"check": CHECKS[1], "passed": not inside, "probe_completed": True,
                       "seal": str(resolved_seal), "record": str(resolved_record),
                       "detail": ("the root record is retained outside the sealed evidence"
                                  if not inside else
                                  "the root record lies inside the seal it would release, so "
                                  "it establishes nothing before the seal is opened")})
    except OSError as exc:
        checks.append({"check": CHECKS[1], "passed": False, "probe_completed": False,
                       "detail": "the record and the seal could not both be resolved: %s" % exc})

    try:
        result = roots_module.check(record_path)
        checks.append({"check": CHECKS[2], "passed": bool(result["passed"]),
                       "probe_completed": True, "roots": result["roots"],
                       "roots_present": len(result["present"]),
                       "detail": ("every recorded cell root is gone from its parent"
                                  if result["passed"] else
                                  "%d recorded cell root(s) survive" % len(result["present"]))})
    except (ValueError, TypeError, AttributeError) as exc:
        checks.append({"check": CHECKS[2], "passed": False, "probe_completed": True,
                       "detail": "the root record is not usable: %s" % exc})
    except OSError as exc:
        # A parent that cannot be enumerated - missing, or permission denied - has
        # inspected nothing. Retain every parent until this check completes.
        checks.append({"check": CHECKS[2], "passed": False, "probe_completed": False,
                       "detail": "a recorded root's parent could not be enumerated (%s), so "
                                 "its absence is unestablished" % exc})
    return checks


def build_gate(ledger, ledger_error, probes, roots_record, roots_sha256, seal,
               container_prefix, markers, roots_module, observed_at=None) -> dict:
    observed_at = observed_at or now()
    checks = record_checks(roots_record, roots_sha256, seal, roots_module)
    recorded_roots = next((check.get("roots") for check in checks
                           if check["check"] == CHECKS[2]), None) or []

    process_probe = probes.get("processes") or {}
    all_markers = tuple(markers) + tuple(recorded_roots) + (container_prefix,)
    processes = reviewer_processes(process_probe, probes.get("self_pid", os.getpid()),
                                   all_markers)
    completed = probe_completed(process_probe)
    check = {"check": CHECKS[3], "passed": completed and not processes["live"],
             "match_count": len(processes["live"]),
             "own_ancestry_match_count": len(processes["own_ancestry"]),
             "markers": sorted(set(all_markers)),
             "detail": (incomplete_detail(process_probe, "process") if not completed else
                        "no process outside this gate's own ancestry names a recorded cell "
                        "root, a cell container or the coordinator; %d in this gate's own "
                        "ancestry matched and were excluded"
                        % len(processes["own_ancestry"]) if not processes["live"] else
                        "%d process(es) still name a reviewer run" % len(processes["live"]))}
    check.update(probe_fields(process_probe))
    checks.append(check)

    container_probe = probes.get("containers") or {}
    completed = probe_completed(container_probe)
    running = cell_containers(container_probe, container_prefix)
    check = {"check": CHECKS[4], "passed": completed and not running,
             "match_count": len(running), "container_prefix": container_prefix,
             "detail": (("the container runtime could not be inspected: %s. An unreachable "
                         "runtime establishes nothing about what is running under it"
                         % incomplete_detail(container_probe, "container"))
                        if not completed else
                        "the runtime lists no container named %s*" % container_prefix
                        if not running else
                        "%d cell container(s) are still present" % len(running))}
    check.update(probe_fields(container_probe))
    checks.append(check)

    if ledger_error is not None:
        for name in CHECKS[5:]:
            checks.append({"check": name, "passed": False, "probe_completed": False,
                           "detail": "the ledger could not be read: %s" % ledger_error})
    else:
        state = ledger_state(ledger)
        checks.append({"check": CHECKS[5], "passed": not state["unclosed"],
                       "probe_completed": True,
                       "attempts_opened": len(state["opened"]),
                       "attempts_closed": len(state["closed"]),
                       "unclosed_count": len(state["unclosed"]),
                       "detail": "%d attempt-open events, %d attempt-close events, %d unclosed"
                                 % (len(state["opened"]), len(state["closed"]),
                                    len(state["unclosed"]))})
        header = usd(ledger.get("reserved_usd"))
        balance = state["reservation_balance"]
        checks.append({"check": CHECKS[6],
                       "passed": balance == 0 and header == 0, "probe_completed": True,
                       "reservation_delta_sum_usd": str(balance),
                       "header_reserved_usd": str(header),
                       "detail": "reservation deltas sum to %s and the ledger header carries "
                                 "reserved_usd %s; an in-flight dispatch would hold a live "
                                 "reservation" % (balance, header)})
        checks.append({"check": CHECKS[7], "passed": state["chain_intact"],
                       "probe_completed": True, "event_count": state["event_count"],
                       "detail": ("%d events chain from the open event" % state["event_count"]
                                  if state["chain_intact"] else
                                  "the chain breaks at event index %s" % state["broken_at"])})
        checks.append({"check": CHECKS[8], "passed": state["stops"] == 1,
                       "probe_completed": True, "stop_events": state["stops"],
                       "detail": ("the ledger carries its one terminal stop, so no further "
                                  "dispatch can be reserved" if state["stops"] == 1 else
                                  "the ledger carries %d stop events; a study whose ledger "
                                  "can still dispatch is not stopped" % state["stops"])})
        latest = state["latest_event_at"]
        captured = probes.get("captured_at") or observed_at
        quiet = bool(latest) and latest < captured
        checks.append({"check": CHECKS[9], "passed": quiet, "probe_completed": True,
                       "latest_event_at": latest, "probes_captured_at": captured,
                       "detail": ("the newest ledger event is %s, before the host was probed "
                                  "at %s" % (latest, captured) if quiet else
                                  "the newest ledger event is %r, which does not precede the "
                                  "probe at %s" % (latest, captured))})

    for check in checks:
        check["class"] = "required"
        check["established"] = bool(check["passed"] and check.get("probe_completed"))
        check["outcome"] = ("passed" if check["established"] else
                            "incomplete" if not check.get("probe_completed") else "failed")
    cleared = all(check["established"] for check in checks)
    return {
        "schema_version": SCHEMA_VERSION, "artifact_id": ARTIFACT_ID,
        "observed_at": observed_at, "probes_captured_at": probes.get("captured_at"),
        "all_reviewers_stopped": cleared, "seal_may_be_opened": cleared,
        "every_check_established": cleared,
        "check_classes": ("every check is required. A check establishes its condition only "
                          "when its probe completed and the condition held; an incomplete "
                          "probe, an unreachable runtime, a missing tool, a timeout and a "
                          "root record that is not the pinned one all block clearance"),
        "checks": checks,
        "blocking": [check["check"] for check in checks if not check["established"]],
        "raw_capture": ("retained separately and sealed with the evidence: a process command "
                        "line or a container name can name a target slot"),
    }


def command_check(args) -> int:
    roots_module = load_roots_module()
    ledger, ledger_error = None, None
    try:
        ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        ledger_error = str(exc)
    if args.probes_from:
        try:
            probes = json.loads(Path(args.probes_from).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            sys.stderr.write("cannot read %s: %s\n" % (args.probes_from, exc))
            return 2
    else:
        probes = live_probes(args.container_cli, args.timeout)
    gate = build_gate(ledger, ledger_error, probes, args.roots_record, args.roots_sha256,
                      args.seal, args.container_prefix, args.marker, roots_module)
    try:
        if args.raw_out:
            Path(args.raw_out).write_text(json.dumps(probes, indent=2, sort_keys=True) + "\n",
                                          encoding="utf-8")
        Path(args.out).write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n",
                                  encoding="utf-8")
    except OSError as exc:
        sys.stderr.write("cannot write the gate record: %s\n" % exc)
        return 2
    for check in gate["checks"]:
        if not check["established"]:
            print("gate check %s: %s - %s" % (check["outcome"], check["check"], check["detail"]))
    if gate["all_reviewers_stopped"]:
        return 0
    return 2 if ledger_error is not None else 1


def command_authorize(args) -> int:
    try:
        gate = json.loads(Path(args.gate).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.stderr.write("cannot read %s: %s\n" % (args.gate, exc))
        return 2
    problems = []
    if gate.get("artifact_id") != ARTIFACT_ID:
        problems.append("%s is not a shutdown gate record" % args.gate)
    checks = gate.get("checks") or []
    if not checks:
        problems.append("the gate record carries no checks, so it established nothing")
    missing = [name for name in CHECKS if name not in {check.get("check") for check in checks}]
    for name in missing:
        problems.append("the gate record is missing the required check: %s" % name)
    for check in checks:
        if not check.get("established"):
            problems.append("%s did not establish its condition: %s"
                            % (check.get("check"), check.get("detail")))
    if not gate.get("all_reviewers_stopped") and not problems:
        problems.append("the gate record does not clear the seal")
    if args.max_age_seconds:
        try:
            observed = datetime.fromisoformat(gate.get("observed_at"))
            age = (datetime.now(timezone.utc) - observed).total_seconds()
            if age > args.max_age_seconds or age < 0:
                problems.append("the gate was recorded %.0f seconds ago; re-probe before "
                                "opening the seal" % age)
        except (TypeError, ValueError):
            problems.append("the gate record carries no usable observation time")
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("operation", nargs="?", choices=("check", "authorize"))
    parser.add_argument("--ledger")
    parser.add_argument("--roots-record")
    parser.add_argument("--roots-sha256", help="the digest the dispatch record pinned")
    parser.add_argument("--seal", help="the sealed evidence this gate would release")
    parser.add_argument("--out")
    parser.add_argument("--raw-out", help="retain the raw probe capture here, outside the "
                                          "public record")
    parser.add_argument("--probes-from", help="re-score a retained raw capture")
    parser.add_argument("--container-prefix", default=DEFAULT_CONTAINER_PREFIX)
    parser.add_argument("--container-cli", default="docker")
    parser.add_argument("--marker", action="append", default=list(DEFAULT_MARKERS))
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--gate")
    parser.add_argument("--max-age-seconds", type=int)
    parser.add_argument("--self-test", action="store_true")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return subprocess.run([sys.executable,
                               str(Path(__file__).with_name("test_shutdown.py"))]).returncode
    if not args.operation:
        parser.error("an operation is required")
    if args.operation == "check" and not (args.ledger and args.roots_record
                                          and args.roots_sha256 and args.seal and args.out):
        parser.error("check requires --ledger, --roots-record, --roots-sha256, --seal "
                     "and --out")
    if args.operation == "authorize" and not args.gate:
        parser.error("authorize requires --gate")
    if args.operation == "check":
        return command_check(args)
    return command_authorize(args)


if __name__ == "__main__":
    sys.exit(main())
