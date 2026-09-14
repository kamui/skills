#!/usr/bin/env python3
"""Record and summarize a review run's timing events at its script seams.

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

Usage::

    python3 scripts/run_events.py summarize <private-dir>/run-events.jsonl --output summary.json
        [--completion-mode result|publication|render-only] [--timing-sidecar timing.json]

Exit codes: ``0`` summary written; ``1`` summary written with content
violations (invalid lines, out-of-order or inconsistent boundaries), one per
stdout line; ``2`` the events file cannot be read, an output path already
exists or cannot be written, or an argument is invalid, named on stderr.

Event schema (one JSON object per line, ``format: review-run-event/1``)::

    {
      "format": "review-run-event/1",
      "event": "context-built" | "verifier-brief-built" | "verifier-return-accounted" | "payload-composed",
      "exit": 0,                                  # the script's exit status
      "origin": {"script": "compose_review.py", "pid": 123,
                 "harness": {"name": "claude-code", "source": "env:CLAUDECODE", "session": "<id>"}},
      "clock": {"host": "<node name>", "boot": "<boot id>", "boot_source": "linux:boot_id",
                "implementation": "clock_gettime(CLOCK_MONOTONIC)"},
      "started_ns": 1, "ended_ns": 2,             # monotonic ns: script main entry and exit
      "ended_at": "2026-09-14T12:00:00.250000Z",  # wall clock (UTC) read with ended_ns
      "policy": {"workflow": "v5b-17", "commit": "<sha>", "commit_source": "git:skill-root"},
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

Summary. Durations subtract only monotonic readings from one clock domain
(same host, boot identity and clock implementation) whose events are in
non-decreasing file order; anything else is null with its reason. Wall-clock
``ended_at`` values are provenance, never subtracted. The summary separates
captured intervals between recorded boundaries, labelled proxies, and fields
no script can observe (root dispatch, primary inspection, focused tests,
verifier idle wait, publication, caller mode, usage). A verifier batch's
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
``result`` and ``render-only`` and is null for ``publication``, whose forge
write no script performs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import time

EVENT_FORMAT = "review-run-event/1"
SUMMARY_FORMAT = "review-run-summary/1"
EVENTS_NAME = "run-events.jsonl"
EVENTS = ("context-built", "verifier-brief-built", "verifier-return-accounted", "payload-composed")
MODES = ("result", "publication", "render-only")
SKILL_ROOT = Path(__file__).resolve().parent.parent

NOT_OBSERVED = {
    "root_dispatch": "the caller dispatches the review before any script runs",
    "collection": "forge fetches and packet normalization record no event; only the context build is timed",
    "primary_inspection": "inspection and falsification run in the model between script calls",
    "focused_tests": "focused tests run as arbitrary commands no script wraps",
    "verifier_dispatch_and_join": "the worker is dispatched after the brief is built and joined before accounting; "
                                  "only those two script boundaries are recorded",
    "primary_idle_wait": "the primary may keep working while a batch runs, so no bracket measures waiting",
    "publication": "the publisher's forge write is not a script; its review timestamp is on another clock",
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
        flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
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

def _valid(event) -> str:
    """Why a parsed line is not a usable event, or ''."""
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
    if not isinstance(event.get("clock"), dict) or not isinstance(event.get("data"), dict):
        return "clock and data must be objects"
    if not isinstance(event.get("ended_at"), str):
        return "ended_at must be a string"
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
        for earlier, later in zip(events, events[1:]):
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

    last_join = None
    if payload is not None:
        joins = [a for key in order for a in batches[key]["accountings"] if a["_line"] < payload["_line"]]
        last_join = joins[-1] if joins else None
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
                                  "first recorded script entry to last exit; not root elapsed", "no events"),
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a review run's recorded timing events.")
    sub = parser.add_subparsers(dest="command", required=True)
    summary_parser = sub.add_parser("summarize", help="summarize one run-events.jsonl")
    summary_parser.add_argument("events")
    summary_parser.add_argument("--output", required=True, help="new summary JSON path; never overwritten")
    summary_parser.add_argument("--completion-mode", choices=MODES)
    summary_parser.add_argument("--timing-sidecar", help="new research timing sidecar path; needs --completion-mode")
    args = parser.parse_args()
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
