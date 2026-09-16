#!/usr/bin/env python3
"""Record and summarize a review run's timing events at its script and command seams.

The scripts every run invokes in fixed order append one event each to
``run-events.jsonl`` in the run's private directory: ``review_context.py``
(a ``--store`` build: ``context-built``), ``build_verifier_prompt.py``
(``verifier-brief-built``), ``account_verifier_return.py``
(``verifier-return-accounted``) and ``compose_review.py`` with ``--store``
(``payload-composed``; exit 0 is the validated payload). The private directory
is the parent of the store, bundle or ``--output`` path. Recording is
mechanical and silent: it prints nothing, never changes a script's output or
exit status, and any failure simply leaves the event out, which the summary
reports as a measurement gap. The model neither writes nor narrates events.

``wrap`` launches one existing forge fetch, focused test, or forge write that
the caller supplies and appends one event around it. It holds no forge request
logic, and stdout redirects stay outside it.

Usage::

    python3 scripts/run_events.py summarize <private-dir>/run-events.jsonl --output summary.json
        [--completion-mode result|publication|render-only] [--timing-sidecar timing.json]
    python3 scripts/run_events.py wrap --private-dir <dir> --event <name> [--data key=value ...] -- <command> [args...]

``summarize`` exit codes: ``0`` summary written; ``1`` summary written with
content violations (invalid lines, out-of-order or inconsistent boundaries), one
per stdout line; ``2`` the events file cannot be read, an output path already
exists or cannot be written, or an argument is invalid, named on stderr.

``wrap`` supersedes that convention for the child's status: it exits with the
child's own status (0, 1, 2, 42, ...), and a child killed by signal N exits
``128 + N``. Invalid wrapper arguments, including a missing required argument,
and a command that cannot be executed exit ``2`` with one ``run_events:`` line
on stderr; a child's own exit 2 adds no such line. ``--event`` is
``forge-fetched`` (``--data role=`` and ``--data connection=``),
``focused-test-ran`` (``--data head=``), or ``forge-written`` (``--data role=``).
The child inherits stdin, stdout, stderr, inheritable descriptors, the
environment and the working directory; the wrapper reads and writes none of
them. A missing, unwritable or otherwise unusable ``--private-dir`` changes
nothing about the child and prints nothing: the event is simply absent. A
command that cannot be executed still records its failed attempt.

Cancellation: SIGINT, SIGTERM or SIGHUP delivered to the wrapper is forwarded to
the child, and a second one kills it. A terminal Ctrl-C that already reached
the child's process group is therefore delivered to the child twice. The wrapper
always waits for the child, records ``data.cancelled``, and never exits 0 after
a cancellation: a child that exits 0 anyway yields ``128 + N``. A signal the
wrapper inherited as ignored stays ignored and is not forwarded. SIGKILL to the
wrapper alone cannot be forwarded; the child shares the wrapper's process group,
so a process-group kill reaches both.

Event schema (one JSON object per line, ``format: review-run-event/1``)::

    {
      "format": "review-run-event/1",
      "event": "context-built" | "verifier-brief-built" | "verifier-return-accounted" | "payload-composed"
               | "forge-fetched" | "focused-test-ran" | "forge-written",
      "exit": 0,                                  # the script's exit status
      "origin": {"script": "compose_review.py", "pid": 123,
                 "harness": {"name": "claude-code", "source": "env:CLAUDECODE", "session": "<id>"}},
      "clock": {"host": "<node name>", "boot": "<boot id>", "boot_source": "linux:boot_id",
                "implementation": "clock_gettime(CLOCK_MONOTONIC)"},
      "started_ns": 1, "ended_ns": 2,             # monotonic ns: script main entry and exit
      "ended_at": "2026-09-14T12:00:00.250000Z",  # wall clock (UTC) read with ended_ns
      "policy": {"workflow": "v5b-20", "commit": "<sha>", "commit_source": "git:skill-root"},
      "data": {...}
    }

``harness`` fields are null unless an environment marker names the harness;
``boot`` is null when the boot identity cannot be read. ``policy`` is read on
``context-built`` and ``payload-composed`` only, and ``commit`` is null unless
the installed skill root is a clean git checkout. ``data`` per event:

- ``context-built``: ``target`` (``worktree`` or ``commit-range``; a pull request
  and a range build identically), ``head``, ``merge_base``, ``prior_head``, ``store``.
- ``verifier-brief-built``: ``run_id``, ``batch_id``, ``phase``, ``mode``,
  ``candidates``, ``ledger_rows``, ``full_ledger_rows`` (null when the build
  refused its input before projection), ``bundle``.
- ``verifier-return-accounted``: ``run_id``, ``batch_id``, ``phase``, ``mode``,
  ``supplied`` {``candidates``, ``ledger_rows``}, ``returned`` {``confirmed``,
  ``refuted``, ``holds``, ``re_open``} counted over accounted records only,
  ``withheld`` {``candidates``, ``ledger_rows``}, ``structurally_complete``,
  ``conclusion_accounted``, ``bundle`` (null counts when no report was made).
- ``payload-composed``: ``target_kind`` (``pull-request`` when the composition
  omits it, the composer's default), ``head``, ``merge_base``, ``status``,
  ``coverage``, ``findings``, ``questions``.
- Wrapped events (``origin.script`` is ``run_events.py``, ``policy`` is null,
  ``exit`` is the wrapper's status) all carry ``argv0`` (the command's first
  argument), ``signal`` (the signal that killed the child, or null) and
  ``cancelled`` (the signal that cancelled the wrapper, or null). Their
  ``started_ns`` and ``ended_ns`` bracket launch to reap, which includes the
  wrapper's launch and reap overhead but not its interpreter start.
- ``forge-fetched``: ``role`` (``root``, ``continuation``, ``issue`` or ``ci``)
  and ``connection`` (``root`` for role root, ``ci`` for role ci, otherwise the
  requested connection's name).
- ``focused-test-ran``: ``head`` (full commit SHA the test ran at) and
  ``command``, the wrapped argv joined with spaces: display-only provenance,
  never an executable reconstruction.
- ``forge-written``: ``role`` (``review``, ``replies``, ``resolutions`` or
  ``summary``). A wrapped write loop is one event; its result file, not the
  event, records each write's outcome.

Summary. Durations subtract only monotonic readings from one clock domain
(same host, boot identity and clock implementation) whose script events are in
non-decreasing file order; anything else is null with its reason. Wrapped
events are exempt from file order: each takes its timestamp before appending, so
independent commands can finish and append in either order. A forge write that
started before the first validated payload ended, or that precedes it in the
file, is a violation. Wall-clock ``ended_at`` values are provenance, never
subtracted. The summary separates captured intervals between recorded
boundaries, labelled proxies, and fields no event can observe (root dispatch,
primary inspection, verifier idle wait, complete publication, caller mode,
usage). ``commands`` reports forge fetches, focused tests and publication
writes separately: each group's event count, every attempt with its status
(failures included), and the union of its intervals counted once. Overlapping
spans are never summed, and a group with no event is unknown, not zero. A verifier batch's
brief-to-accounting bracket contains dispatch, worker lifetime, the raw save
and the join; it is not the primary's waiting time, and overlapping brackets
report their union once beside their sum. A complete-ledger batch with zero
rows is an explicit zero; a batch whose row count was not recorded is unknown.
Usage and cost are always unavailable here: no script observes an
authoritative usage record, and absent values are null, never zero.

``--timing-sidecar`` writes the research metering timing sidecar
(``completion_mode``, ``root_dispatched_at``, ``payload_validated_at``,
``completed_at``) from the validated payload's ``ended_at``. Root dispatch is
null because no script observes it; ``completed_at`` equals the payload for
``result`` and ``render-only`` and is null for ``publication``: a wrapped write
times one command, and no event proves every required write and readback
finished.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import signal
import stat
import subprocess
import sys
import time

EVENT_FORMAT = "review-run-event/1"
SUMMARY_FORMAT = "review-run-summary/1"
EVENTS_NAME = "run-events.jsonl"
COMMAND_EVENTS = ("forge-fetched", "focused-test-ran", "forge-written")
EVENTS = ("context-built", "verifier-brief-built", "verifier-return-accounted", "payload-composed") + COMMAND_EVENTS
MODES = ("result", "publication", "render-only")
SKILL_ROOT = Path(__file__).resolve().parent.parent
FETCH_ROLES = ("root", "continuation", "issue", "ci")
WRITE_ROLES = ("review", "replies", "resolutions", "summary")
WRAP_KEYS = {"forge-fetched": ("role", "connection"), "focused-test-ran": ("head",), "forge-written": ("role",)}
COMMAND_FIELDS = {"forge-fetched": ("role", "connection"), "focused-test-ran": ("head", "command"),
                  "forge-written": ("role",)}
FULL_SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")
CONNECTION = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
FORWARDED_SIGNALS = ("SIGINT", "SIGTERM", "SIGHUP")

NOT_OBSERVED = {
    "root_dispatch": "the caller dispatches the review before any script runs",
    "collection": "only forge fetches run through run_events.py wrap are timed; packet normalization and any "
                  "unwrapped fetch record no event",
    "primary_inspection": "inspection and falsification run in the model between script calls",
    "focused_tests": "only focused tests run through run_events.py wrap are timed; verifier tests are never wrapped",
    "verifier_dispatch_and_join": "the worker is dispatched after the brief is built and joined before accounting; "
                                  "only those two script boundaries are recorded",
    "primary_idle_wait": "the primary may keep working while a batch runs, so no bracket measures waiting",
    "publication": "wrapped forge writes are timed one command or loop at a time, but no event proves every required "
                   "write and readback finished; complete-publication timing needs caller or runtime evidence",
    "caller_mode": "one-shot or session mode is not passed to any script",
    "usage": "no script observes an authoritative per-request usage record",
}


# --- Recording ---------------------------------------------------------------

def _harness() -> dict:
    if os.environ.get("CLAUDECODE"):
        return {"name": "claude-code", "source": "env:CLAUDECODE",
                "session": os.environ.get("CLAUDE_CODE_SESSION_ID") or None}
    return {"name": None, "source": None, "session": None}


def _boot() -> tuple:
    try:
        with open("/proc/sys/kernel/random/boot_id", encoding="utf-8") as handle:
            return handle.read().strip() or None, "linux:boot_id"
    except OSError:
        pass
    if sys.platform == "darwin":
        try:
            result = subprocess.run(["sysctl", "-n", "kern.bootsessionuuid"], capture_output=True,
                                    text=True, encoding="utf-8", timeout=2, check=False)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip(), "darwin:kern.bootsessionuuid"
        except (OSError, subprocess.SubprocessError):
            pass
    return None, None


def _policy() -> dict:
    policy = {"workflow": None, "commit": None, "commit_source": None}
    try:
        import validate_review
        policy["workflow"] = validate_review.WORKFLOW
    except Exception:
        pass
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}

    def git(*args):
        return subprocess.run(["git", "-C", str(SKILL_ROOT), *args], capture_output=True, text=True,
                              encoding="utf-8", env=env, timeout=5, check=False)
    try:
        head = git("rev-parse", "HEAD")
        if head.returncode == 0:
            dirty = git("status", "--porcelain", "--untracked-files=no", "--", ".")
            if dirty.returncode == 0 and not dirty.stdout.strip():
                policy.update(commit=head.stdout.strip(), commit_source="git:skill-root")
            else:
                policy["commit_source"] = "git:skill-root (modified or unreadable; commit withheld)"
    except (OSError, subprocess.SubprocessError):
        pass
    return policy


def _count(value):
    return len(value) if isinstance(value, list) else None


def _text(value):
    return value if isinstance(value, str) else None


def _absolute(value):
    return os.path.abspath(value) if isinstance(value, str) and value else None


def _data(name: str, stash: dict) -> tuple:
    """The private directory and event data from what a script stashed."""
    if name == "context-built":
        store = _absolute(stash.get("store"))
        return (os.path.dirname(store) if store else None), {
            "target": _text(stash.get("target")), "head": _text(stash.get("head")),
            "merge_base": _text(stash.get("merge_base")), "prior_head": _text(stash.get("prior_head")),
            "store": store}
    if name == "verifier-brief-built":
        bundle = _absolute(stash.get("output"))
        projected = stash.get("projected") if isinstance(stash.get("projected"), dict) else {}
        batch = projected.get("batch") if isinstance(projected.get("batch"), dict) else {}
        run = projected.get("run") if isinstance(projected.get("run"), dict) else {}
        return (os.path.dirname(bundle) if bundle else None), {
            "run_id": _text(run.get("id")), "batch_id": _text(batch.get("id")),
            "phase": _text(batch.get("phase")), "mode": _text(batch.get("mode")),
            "candidates": _count(projected.get("candidates")), "ledger_rows": _count(projected.get("ledger")),
            "full_ledger_rows": _count(stash.get("ledger")), "bundle": bundle}
    if name == "verifier-return-accounted":
        bundle = _absolute(stash.get("bundle"))
        manifest = stash.get("manifest") if isinstance(stash.get("manifest"), dict) else {}
        report = stash.get("report") if isinstance(stash.get("report"), dict) else None
        batch = manifest.get("batch") if isinstance(manifest.get("batch"), dict) else {}
        run = manifest.get("run") if isinstance(manifest.get("run"), dict) else {}
        data = {"run_id": _text(run.get("id")), "batch_id": _text(batch.get("id")),
                "phase": _text(batch.get("phase")), "mode": _text(batch.get("mode")),
                "supplied": {"candidates": _count(manifest.get("candidate_ids")),
                             "ledger_rows": _count(manifest.get("ledger_ids"))},
                "returned": {"confirmed": None, "refuted": None, "holds": None, "re_open": None},
                "withheld": {"candidates": None, "ledger_rows": None},
                "structurally_complete": None, "conclusion_accounted": None, "bundle": bundle}
        if report is not None:
            returned = report.get("return") if isinstance(report.get("return"), dict) else {}
            accounted = report.get("accounted") or {}
            tallies = {}
            for role, field in (("candidates", "verdict"), ("ledger", "ruling")):
                ids = set(accounted.get(role) or [])
                records = returned.get(role) if isinstance(returned.get(role), list) else []
                for record in records:
                    if isinstance(record, dict) and record.get("id") in ids:
                        tallies[record.get(field)] = tallies.get(record.get(field), 0) + 1
            data["returned"] = {"confirmed": tallies.get("confirmed", 0), "refuted": tallies.get("refuted", 0),
                                "holds": tallies.get("holds", 0), "re_open": tallies.get("re-open", 0)}
            withheld = report.get("withheld") or {}
            data["withheld"] = {"candidates": _count(withheld.get("candidates")),
                                "ledger_rows": _count(withheld.get("ledger"))}
            data["structurally_complete"] = report.get("structurally_complete")
            data["conclusion_accounted"] = report.get("conclusion_accounted")
        return (os.path.dirname(bundle) if bundle else None), data
    if name == "payload-composed":
        store = _absolute(stash.get("store"))
        composition = stash.get("composition") if isinstance(stash.get("composition"), dict) else {}
        run = composition.get("run") if isinstance(composition.get("run"), dict) else {}
        summary = composition.get("summary") if isinstance(composition.get("summary"), dict) else {}
        kind = run.get("target_kind", "pull-request") if composition else None
        return (os.path.dirname(store) if store else None), {
            "target_kind": _text(kind), "head": _text(run.get("head")), "merge_base": _text(run.get("merge_base")),
            "status": _text(summary.get("status")), "coverage": _text(run.get("coverage")),
            "findings": _count(composition.get("findings", [] if composition else None)),
            "questions": _count(composition.get("questions", [] if composition else None))}
    if name in COMMAND_EVENTS:
        argv = stash.get("argv") if isinstance(stash.get("argv"), list) else []
        data = dict(stash.get("data") or {})
        data.update(argv0=_text(argv[0]) if argv else None, signal=_text(stash.get("signal")),
                    cancelled=_text(stash.get("cancelled")))
        if name == "focused-test-ran":
            data["command"] = " ".join(argv)
        return _absolute(stash.get("private_dir")), data
    return None, {}


def record(stash: dict, status, started_ns: int, script: str) -> None:
    """Append one event for a finished script; never raises, prints, or blocks the result."""
    try:
        name = stash.get("event")
        if name not in EVENTS or not isinstance(status, int):
            return
        ended_ns = time.monotonic_ns()
        ended_at = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
        directory, data = _data(name, stash)
        if not directory:
            return
        boot, boot_source = _boot()
        event = {
            "format": EVENT_FORMAT, "event": name, "exit": status,
            "origin": {"script": script, "pid": os.getpid(), "harness": _harness()},
            "clock": {"host": platform.node() or None, "boot": boot, "boot_source": boot_source,
                      "implementation": time.get_clock_info("monotonic").implementation},
            "started_ns": started_ns, "ended_ns": ended_ns, "ended_at": ended_at,
            "policy": _policy() if name in ("context-built", "payload-composed") else None,
            "data": data,
        }
        line = (json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        # O_NONBLOCK: a FIFO or device at this path fails the open instead of blocking the script.
        flags = (os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
                 | getattr(os, "O_NONBLOCK", 0))
        descriptor = os.open(os.path.join(directory, EVENTS_NAME), flags, 0o600)
        try:
            info = os.fstat(descriptor)
            if stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid():
                os.write(descriptor, line)
        finally:
            os.close(descriptor)
    except Exception:
        return


# --- Summary -----------------------------------------------------------------

TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)")
DATA_STRINGS = ("head", "merge_base", "prior_head", "target", "target_kind", "run_id", "batch_id", "phase",
                "mode", "status", "coverage", "store", "bundle", "role", "connection", "argv0", "command",
                "signal", "cancelled")
DATA_COUNTS = ("candidates", "ledger_rows", "full_ledger_rows", "findings", "questions")
DATA_TALLIES = ("supplied", "returned", "withheld")


def _command_data_error(name: str, data: dict) -> str:
    """Why a wrapped event's caller-supplied data breaks its rule, or ''. Shared by wrap and summarize."""
    role = data.get("role")
    if name == "forge-fetched":
        connection = data.get("connection")
        if role not in FETCH_ROLES:
            return "forge-fetched role must be one of " + ", ".join(FETCH_ROLES)
        if not isinstance(connection, str) or not CONNECTION.fullmatch(connection):
            return "forge-fetched connection must name the requested connection, root, or ci"
        if role in ("root", "ci") and connection != role:
            return f"forge-fetched role={role} requires connection={role}"
        if role not in ("root", "ci") and connection in ("root", "ci"):
            return f"forge-fetched role={role} must name the requested connection, not {connection}"
    elif name == "focused-test-ran":
        head = data.get("head")
        if not isinstance(head, str) or not FULL_SHA.fullmatch(head):
            return "focused-test-ran head must be a full lowercase commit SHA"
    elif name == "forge-written" and role not in WRITE_ROLES:
        return "forge-written role must be one of " + ", ".join(WRITE_ROLES)
    return ""


def _timestamp(value) -> bool:
    """An ISO-8601 instant with seconds and timezone that the research sidecar reader accepts."""
    if not isinstance(value, str) or not TIMESTAMP.fullmatch(value):
        return False
    normalized = re.sub(r"\.(\d+)", lambda match: "." + match[1][:6].ljust(6, "0"), value)
    try:
        datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _optional(value, kinds) -> bool:
    return value is None or (isinstance(value, kinds) and not isinstance(value, bool))


def _strings(value, names) -> bool:
    return isinstance(value, dict) and all(_optional(value.get(name), str) for name in names)


def _valid(event) -> str:
    """Why a parsed line is not a usable event, or ''. Checks every field the summary reads."""
    if not isinstance(event, dict) or event.get("format") != EVENT_FORMAT:
        return f"not a {EVENT_FORMAT} object"
    if event.get("event") not in EVENTS:
        return f"unknown event {event.get('event')!r}"
    if type(event.get("exit")) is not int:
        return "exit must be an integer"
    started, ended = event.get("started_ns"), event.get("ended_ns")
    if type(started) is not int or type(ended) is not int:
        return "started_ns and ended_ns must be integers"
    if started > ended:
        return "started_ns is after ended_ns"
    if not _strings(event.get("clock"), ("host", "boot", "implementation")):
        return "clock must be an object whose host, boot and implementation are strings or null"
    if not _timestamp(event.get("ended_at")):
        return "ended_at must be an ISO-8601 timestamp with seconds and timezone"
    origin = event.get("origin")
    if origin is not None:
        if not _strings(origin, ("script",)) or not _optional(origin.get("pid"), int):
            return "origin must be an object with a string script and integer pid"
        if origin.get("harness") is not None and not _strings(origin["harness"], ("name", "source", "session")):
            return "origin.harness name, source and session must be strings or null"
    if event.get("policy") is not None and not _strings(event["policy"], ("workflow", "commit", "commit_source")):
        return "policy workflow, commit and commit_source must be strings or null"
    data = event.get("data")
    if not _strings(data, DATA_STRINGS):
        return "data must be an object whose identity fields are strings or null"
    if not all(_optional(data.get(name), int) and (data.get(name) or 0) >= 0 for name in DATA_COUNTS):
        return "data counts must be non-negative integers or null"
    for name in DATA_TALLIES:
        tally = data.get(name)
        if tally is not None and not (isinstance(tally, dict) and all(
                _optional(count, int) and (count or 0) >= 0 for count in tally.values())):
            return f"data.{name} must map to non-negative integers or null"
    for name in ("structurally_complete", "conclusion_accounted"):
        if data.get(name) is not None and not isinstance(data.get(name), bool):
            return f"data.{name} must be a boolean or null"
    if event["event"] in COMMAND_EVENTS:
        if not data.get("argv0"):
            return "data.argv0 must be a non-empty string"
        if event["event"] == "focused-test-ran" and not data.get("command"):
            return "focused-test-ran data.command must be a non-empty string"
        return _command_data_error(event["event"], data)
    return ""


def _domain(event):
    clock = event["clock"]
    if not clock.get("host") or not clock.get("boot") or not clock.get("implementation"):
        return None
    return (clock["host"], clock["boot"], clock["implementation"])


def _seconds(start_ns, end_ns):
    return round((end_ns - start_ns) / 1e9, 6)


def _union_seconds(spans):
    total, current = 0, None
    for start, end in sorted(spans):
        if current is None or start > current[1]:
            if current is not None:
                total += current[1] - current[0]
            current = [start, end]
        else:
            current[1] = max(current[1], end)
    if current is not None:
        total += current[1] - current[0]
    return round(total / 1e9, 6)


def summarize(lines, events_path: str, mode) -> tuple:
    violations, invalid, events = [], [], []
    for number, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except ValueError as error:
            reason = f"invalid JSON: {error}"
        else:
            reason = _valid(event)
        if reason:
            invalid.append({"line": number, "reason": reason})
            violations.append(f"line {number}: {reason}")
            continue
        event["_line"] = number
        events.append(event)

    gaps = []
    domains = {_domain(event) for event in events}
    if not events:
        clock_status, domain = "no-events", None
    elif None in domains:
        clock_status, domain = "unknown", None
        gaps.append("an event has no readable clock domain; durations are unavailable")
    elif len(domains) > 1:
        clock_status, domain = "mixed", None
        gaps.append("events span more than one host, boot or clock; durations are unavailable")
    else:
        clock_status, domain = "single-domain", domains.pop()
    if domain is not None:
        # Script events keep file order; independent wrapped commands may append in either order.
        core = [event for event in events if event["event"] not in COMMAND_EVENTS]
        for earlier, later in zip(core, core[1:]):
            if later["ended_ns"] < earlier["ended_ns"]:
                violations.append(f"line {later['_line']}: ended_ns precedes line {earlier['_line']}")
                clock_status, domain = "out-of-order", None
                break
    timed = domain is not None

    def duration(start_ns, end_ns, status, basis, reason=None):
        if not timed:
            return {"seconds": None, "status": "unavailable", "basis": basis,
                    "reason": f"clock {clock_status}"}
        if start_ns is None or end_ns is None:
            return {"seconds": None, "status": "unavailable", "basis": basis, "reason": reason}
        return {"seconds": _seconds(start_ns, end_ns), "status": status, "basis": basis}

    def by(name, exit_zero=False):
        return [e for e in events if e["event"] == name and (not exit_zero or e["exit"] == 0)]

    contexts = by("context-built", exit_zero=True)
    payloads = by("payload-composed", exit_zero=True)
    payload = payloads[-1] if payloads else None
    context = None
    if payload is not None:
        prior = [e for e in contexts if e["_line"] < payload["_line"]]
        context = prior[-1] if prior else None
        if context is None and contexts:
            violations.append(f"line {payload['_line']}: validated payload precedes every successful context build")
    elif contexts:
        context = contexts[-1]
    if not contexts:
        gaps.append("no successful context build was recorded")
    if payload is None:
        gaps.append("no validated payload was recorded (composition failed, was cancelled, or ran without --store)")

    heads = {e["data"].get("head") for e in (contexts + payloads) if e["data"].get("head")}
    if len(heads) > 1:
        violations.append("events name more than one reviewed head: " + ", ".join(sorted(heads)))

    failures = [{"line": e["_line"], "event": e["event"], "script": (e.get("origin") or {}).get("script"),
                 "exit": e["exit"], "ended_at": e["ended_at"]} for e in events if e["exit"] != 0]

    # Verification batches: a successful brief opens a batch; any readable accounting joins it.
    batches, order = {}, []
    for event in by("verifier-brief-built", exit_zero=True):
        key = event["data"].get("batch_id")
        if key in batches:
            violations.append(f"line {event['_line']}: batch {key!r} built twice")
            continue
        batches[key] = {"brief": event, "accountings": []}
        order.append(key)
    for event in by("verifier-return-accounted"):
        if event["exit"] not in (0, 1):
            continue
        key = event["data"].get("batch_id")
        if key is None:
            gaps.append(f"line {event['_line']}: accounting recorded no batch identity (bundle unreadable)")
            continue
        if key not in batches:
            gaps.append(f"batch {key!r} was accounted without a recorded brief")
            batches[key] = {"brief": None, "accountings": []}
            order.append(key)
        batches[key]["accountings"].append(event)

    rows, spans = [], []
    for key in order:
        brief, accountings = batches[key]["brief"], batches[key]["accountings"]
        source = brief or accountings[0]
        data = source["data"]
        latest = accountings[-1]["data"] if accountings else None
        ledger_rows = data.get("ledger_rows") if brief else (data.get("supplied") or {}).get("ledger_rows")
        candidates = data.get("candidates") if brief else (data.get("supplied") or {}).get("candidates")
        row = {"batch_id": key, "phase": data.get("phase"), "mode": data.get("mode"),
               "candidates": candidates if type(candidates) is int else None,
               "ledger_rows": ledger_rows if type(ledger_rows) is int else None,
               "brief_built_at": brief["ended_at"] if brief else None,
               "accounted_at": [a["ended_at"] for a in accountings],
               "returned": latest.get("returned") if latest else None,
               "withheld": latest.get("withheld") if latest else None,
               "structurally_complete": latest.get("structurally_complete") if latest else None}
        join = accountings[0] if accountings else None
        if brief is not None and join is not None and join["ended_ns"] < brief["ended_ns"]:
            violations.append(f"line {join['_line']}: batch {key!r} accounted before its brief was built")
            join = None
        if brief is not None and not accountings:
            gaps.append(f"batch {key!r} has no recorded accounting (failed, cancelled, or not joined)")
        bracket = duration(brief["ended_ns"] if brief else None, join["ended_ns"] if join else None, "proxy",
                           "brief built to first accounting: dispatch, worker lifetime, raw save and join; "
                           "not primary waiting time", "a boundary of this batch was not recorded")
        row["brief_to_accounting"] = bracket
        if bracket["seconds"] is not None:
            spans.append((brief["ended_ns"], join["ended_ns"]))
        rows.append(row)

    by_mode = {}
    for row in rows:
        by_mode[row["mode"] or "unknown"] = by_mode.get(row["mode"] or "unknown", 0) + 1
    verification = {
        "batches_recorded": len(rows),
        "note": "zero recorded batches is not proof that none ran unless the record is otherwise complete",
        "batches": rows, "by_mode": by_mode,
        "complete_ledger_zero_rows": sum(1 for r in rows if r["mode"] == "complete-ledger" and r["ledger_rows"] == 0),
        "complete_ledger_nonzero_rows": sum(1 for r in rows if r["mode"] == "complete-ledger" and (r["ledger_rows"] or 0) > 0),
        "ledger_rows_unknown": sum(1 for r in rows if r["ledger_rows"] is None),
        "bracket_sum_seconds": {"seconds": round(sum(e - s for s, e in spans) / 1e9, 6) if timed and spans else None,
                                "status": "proxy", "basis": "sum of batch brackets; overlapping brackets count twice; not elapsed"},
        "bracket_union_seconds": {"seconds": _union_seconds(spans) if timed and spans else None,
                                  "status": "proxy", "basis": "wall time covered by any batch bracket, counted once"},
    }

    # A forge write publishes a validated payload, so it cannot start before the first one exists.
    if payloads:
        first = payloads[0]
        for write in by("forge-written"):
            if write["_line"] < first["_line"] or (timed and write["started_ns"] < first["ended_ns"]):
                violations.append(f"line {write['_line']}: forge write precedes the validated payload "
                                  f"at line {first['_line']}")

    def command_group(name, basis):
        group = by(name)
        spans = [(e["started_ns"], e["ended_ns"]) for e in group]
        if not timed:
            union = {"seconds": None, "status": "unavailable", "basis": basis, "reason": f"clock {clock_status}"}
        elif not spans:
            union = {"seconds": None, "status": "unavailable", "basis": basis,
                     "reason": "no wrapped command of this kind was recorded; unknown, not zero"}
        else:
            union = {"seconds": _union_seconds(spans), "status": "captured", "basis": basis}
        by_role = {}
        for e in group:
            if e["data"].get("role"):
                by_role[e["data"]["role"]] = by_role.get(e["data"]["role"], 0) + 1
        attempts = [dict({field: e["data"].get(field) for field in COMMAND_FIELDS[name]},
                         line=e["_line"], exit=e["exit"], signal=e["data"].get("signal"),
                         cancelled=e["data"].get("cancelled"), argv0=e["data"].get("argv0"),
                         ended_at=e["ended_at"], seconds=_seconds(e["started_ns"], e["ended_ns"]) if timed else None)
                    for e in group]
        return {"event_count": len(group), "failed_attempts": sum(1 for e in group if e["exit"] != 0),
                "by_role": by_role, "union_seconds": union, "attempts": attempts}

    commands = {
        "note": "only commands run through run_events.py wrap are recorded; overlapping intervals count once "
                "and are never summed as elapsed time",
        "forge_fetches": command_group("forge-fetched", "wall time covered by any wrapped forge fetch, counted once"),
        "focused_tests": command_group("focused-test-ran", "wall time covered by any wrapped focused test, counted once"),
        "publication_writes": command_group(
            "forge-written", "wall time covered by any wrapped forge write, counted once; a wrapped loop is one "
                             "interval whose result file records each write; not complete publication"),
    }

    last_join = None
    if payload is not None:
        joins = [a for key in order for a in batches[key]["accountings"] if a["_line"] < payload["_line"]]
        # Latest in event order, not batch order: batches may be accounted in reverse.
        last_join = max(joins, key=lambda a: a["_line"]) if joins else None
    durations = {
        "context_build": duration(context["started_ns"] if context else None, context["ended_ns"] if context else None,
                                  "captured", "context build script span", "no successful context build"),
        "context_to_validated_payload": duration(
            context["ended_ns"] if context else None, payload["ended_ns"] if payload else None, "captured",
            "context build exit to validated payload exit: inspection, tests, verification, reconciliation and "
            "composition together; not separable", "a boundary was not recorded"),
        "last_accounting_to_validated_payload": duration(
            last_join["ended_ns"] if last_join else None, payload["ended_ns"] if payload else None, "proxy",
            "last verifier accounting to validated payload: reconciliation, remaining falsification and composition",
            "no accounting precedes a validated payload"),
        "observed_span": duration(min(e["started_ns"] for e in events) if events else None,
                                  max(e["ended_ns"] for e in events) if events else None, "proxy",
                                  "first recorded script or wrapped command start to last exit; excludes root "
                                  "dispatch, so not root elapsed", "no events"),
    }

    if mode is None:
        final = {"at": None, "status": "unavailable", "reason": "completion mode not supplied"}
        gaps.append("completion mode not supplied")
    elif mode == "publication":
        final = {"at": None, "status": "unavailable", "reason": NOT_OBSERVED["publication"]}
        gaps.append("publication completion is not observable by the review-code scripts")
    elif payload is None:
        final = {"at": None, "status": "unavailable", "reason": "no validated payload"}
    else:
        final = {"at": payload["ended_at"], "status": "captured",
                 "reason": f"{mode} completion ends at the validated record"}

    def identity(value, source):
        return {"value": value, "source": source if value is not None else None}
    first_policy = next((e["policy"] for e in reversed(payloads + contexts) if isinstance(e.get("policy"), dict)), {})
    harness = next(((e.get("origin") or {}).get("harness") for e in events
                    if isinstance((e.get("origin") or {}).get("harness"), dict)), {}) or {}
    target_kind = payload["data"].get("target_kind") if payload else None
    summary = {
        "format": SUMMARY_FORMAT, "events": events_path, "event_count": len(events), "invalid_lines": invalid,
        "complete": False, "gaps": gaps, "violations": violations,
        "identity": {
            "workflow": identity(first_policy.get("workflow"), "validate_review.WORKFLOW"),
            "policy_commit": identity(first_policy.get("commit"), first_policy.get("commit_source")),
            "harness": identity(harness.get("name"), harness.get("source")),
            "harness_session": identity(harness.get("session"), harness.get("source")),
            "reviewed_head": identity(sorted(heads)[0] if len(heads) == 1 else None, "context build and composition"),
            "target_kind": identity(target_kind or (context["data"].get("target") if context else None),
                                    "composition run.target_kind" if target_kind else "context build flags"),
            "caller_mode": {"value": None, "source": None, "reason": NOT_OBSERVED["caller_mode"]},
        },
        "clock": {"status": clock_status, "domain": list(domain) if domain else None},
        "boundaries": {
            "context_built_at": context["ended_at"] if context else None,
            "validated_payload_at": payload["ended_at"] if payload else None,
            "final_result": dict(final, completion_mode=mode),
        },
        "durations": durations,
        "verification": verification,
        "commands": commands,
        "script_failures": failures,
        "usage": {"status": "unavailable", "reason": NOT_OBSERVED["usage"], "input_tokens": None,
                  "cache_write_tokens": None, "cache_read_tokens": None, "output_tokens": None, "cost": None},
        "not_observed": NOT_OBSERVED,
    }
    summary["complete"] = not gaps and not violations
    sidecar = None
    if mode is not None:
        at = payload["ended_at"] if payload else None
        sidecar = {"completion_mode": mode, "root_dispatched_at": None, "payload_validated_at": at,
                   "completed_at": at if mode != "publication" else None}
    return summary, sidecar, violations


def _write_new(path: str, value) -> None:
    with open(path, "x", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


# --- Wrapping ----------------------------------------------------------------

class _ArgumentError(Exception):
    pass


class _WrapParser(argparse.ArgumentParser):
    def error(self, message):
        raise _ArgumentError(message)


def _wrap_arguments(argv):
    parser = _WrapParser(prog="run_events.py wrap", allow_abbrev=False,
                         description="Run one command and record its interval; exits with the command's status.")
    parser.add_argument("--private-dir", required=True, help="the run's private directory; unusable means no event")
    parser.add_argument("--event", required=True, choices=COMMAND_EVENTS)
    parser.add_argument("--data", action="append", default=[], metavar="KEY=VALUE",
                        help="forge-fetched: role, connection; focused-test-ran: head; forge-written: role")
    if "--" not in argv:
        parser.parse_args(argv)  # --help exits here; otherwise report a missing argument first
        raise _ArgumentError("expected -- followed by the command to run")
    split = argv.index("--")
    args = parser.parse_args(argv[:split])
    command = argv[split + 1:]
    if not command or not command[0]:
        raise _ArgumentError("expected a command after --")
    data = {}
    for item in args.data:
        key, separator, value = item.partition("=")
        if not separator or not key:
            raise _ArgumentError(f"--data {item!r} must be key=value")
        if key not in WRAP_KEYS[args.event]:
            raise _ArgumentError(f"--data {key} is not accepted for {args.event}; "
                                 f"accepted: {', '.join(WRAP_KEYS[args.event])}")
        if key in data:
            raise _ArgumentError(f"--data {key} given twice")
        data[key] = value
    reason = _command_data_error(args.event, data)
    if reason:
        raise _ArgumentError(reason)
    return args, data, command


def _signal_name(number: int) -> str:
    try:
        return signal.Signals(number).name
    except ValueError:
        return f"signal {number}"


def wrap(argv) -> int:
    try:
        args, data, command = _wrap_arguments(argv)
    except _ArgumentError as error:
        print(f"run_events: wrap: {error}", file=sys.stderr)
        return 2
    stash = {"event": args.event, "private_dir": args.private_dir, "data": data, "argv": command,
             "signal": None, "cancelled": None}
    state = {"child": None, "cancelled": None, "received": 0, "sent": 0}

    def deliver():
        child = state["child"]
        while child is not None and state["sent"] < state["received"]:
            state["sent"] += 1
            try:
                if state["sent"] == 1:
                    child.send_signal(state["cancelled"])
                else:
                    child.kill()
            except OSError:
                pass

    def cancel(number, _frame):
        if state["cancelled"] is None:
            state["cancelled"] = number
        state["received"] += 1
        deliver()

    for name in FORWARDED_SIGNALS:
        number = getattr(signal, name, None)
        if number is not None and signal.getsignal(number) is not signal.SIG_IGN:
            signal.signal(number, cancel)

    started_ns = time.monotonic_ns()
    try:
        child = subprocess.Popen(command, close_fds=False)
    except (OSError, ValueError) as error:
        record(stash, 2, started_ns, "run_events.py")
        reason = error.strerror if isinstance(error, OSError) and error.strerror else str(error)
        print(f"run_events: wrap: cannot execute {command[0]}: {reason}", file=sys.stderr)
        return 2
    state["child"] = child
    deliver()  # a cancellation that arrived during launch
    returncode = child.wait()
    status = returncode
    if returncode < 0:
        status = 128 - returncode
        stash["signal"] = _signal_name(-returncode)
    if state["cancelled"] is not None:
        stash["cancelled"] = _signal_name(state["cancelled"])
        if status == 0:
            status = 128 + state["cancelled"]
    record(stash, status, started_ns, "run_events.py")
    return status


def main() -> int:
    argv = sys.argv[1:]
    if argv[:1] == ["wrap"]:
        return wrap(argv[1:])
    parser = argparse.ArgumentParser(description="Summarize a review run's recorded timing events.")
    sub = parser.add_subparsers(dest="command", required=True)
    summary_parser = sub.add_parser("summarize", help="summarize one run-events.jsonl")
    summary_parser.add_argument("events")
    summary_parser.add_argument("--output", required=True, help="new summary JSON path; never overwritten")
    summary_parser.add_argument("--completion-mode", choices=MODES)
    summary_parser.add_argument("--timing-sidecar", help="new research timing sidecar path; needs --completion-mode")
    sub.add_parser("wrap", help="run one forge fetch, focused test, or forge write and record its interval; "
                                "see the module docstring")
    args = parser.parse_args(argv)
    if args.timing_sidecar and not args.completion_mode:
        parser.error("--timing-sidecar requires --completion-mode")
    try:
        with open(args.events, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except (OSError, UnicodeError) as error:
        print(f"run_events: cannot read events {args.events}: {error}", file=sys.stderr)
        return 2
    summary, sidecar, violations = summarize(lines, os.path.abspath(args.events), args.completion_mode)
    try:
        _write_new(args.output, summary)
        if args.timing_sidecar:
            _write_new(args.timing_sidecar, sidecar)
    except OSError as error:
        print(f"run_events: cannot write {error.filename}: {error.strerror}", file=sys.stderr)
        return 2
    for line in violations:
        print(line)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
