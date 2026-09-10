#!/usr/bin/env python3
"""Record one timing event in a cell's completion sidecar.

#149's dispatch prompt tells the reviewer primary to run this immediately after
``validate_review.py`` exits 0 on its final payload, so the sidecar is written by
the process that observed the event rather than reconstructed afterwards. The
schema is #130's, unchanged: ``completion_mode``, ``root_dispatched_at``,
``payload_validated_at`` and ``completed_at``, all on one timezone-aware clock.
A stopped attempt keeps ``stopped_at`` in its Attempt record, outside this file.

The coordinator creates the sidecar with ``--create`` immediately before
dispatching the root; the cell and the coordinator then fill the later events.
``payload_validated_at`` may be rewritten, because the prompt requires a
re-validated payload to replace it with the final successful validation. The
other two events are written once: a second write is a content violation rather
than a silent overwrite, so a double-dispatch or a double-completion shows up
here instead of being smoothed away.

Usage::

    python3 mark_event.py SIDECAR root_dispatched_at --create [--mode render-only]
    python3 mark_event.py SIDECAR payload_validated_at
    python3 mark_event.py SIDECAR completed_at
    python3 mark_event.py --self-test

Input schema (UTF-8 JSON): ``{"completion_mode": str, "root_dispatched_at": str
or null, "payload_validated_at": str or null, "completed_at": str or null}``.

Exit: 0 when the event was recorded, 1 on a content violation with one line per
violation on stdout, 2 when the sidecar cannot be read or written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

EVENTS = ("root_dispatched_at", "payload_validated_at", "completed_at")
REWRITABLE = ("payload_validated_at",)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def empty(mode: str) -> dict:
    return {"completion_mode": mode, "root_dispatched_at": None,
            "payload_validated_at": None, "completed_at": None}


def record(sidecar: dict, event: str, stamp: str) -> list:
    """Set one event, refusing to overwrite an event that is written once."""
    if event not in EVENTS:
        return ["%s is not one of %s" % (event, ", ".join(EVENTS))]
    if sidecar.get(event) is not None and event not in REWRITABLE:
        return ["%s is already %s; it is written once" % (event, sidecar[event])]
    if event != "root_dispatched_at" and not sidecar.get("root_dispatched_at"):
        return ["%s cannot precede root_dispatched_at, which is unset" % event]
    if event == "completed_at" and not sidecar.get("payload_validated_at"):
        return ["completed_at requires final payload validation"]
    sidecar[event] = stamp
    return []


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sidecar", nargs="?")
    parser.add_argument("event", nargs="?")
    parser.add_argument("--create", action="store_true",
                        help="create the sidecar; only with root_dispatched_at")
    parser.add_argument("--mode", default="render-only",
                        help="completion_mode for --create (default render-only)")
    parser.add_argument("--at", help="record this ISO 8601 instant instead of now, for an "
                                     "event the coordinator derives from retained records "
                                     "rather than observes as it happens")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.sidecar or not args.event:
        parser.error("SIDECAR and EVENT are required")

    path = Path(args.sidecar)
    if args.create:
        if args.event != "root_dispatched_at":
            print("--create only applies to root_dispatched_at")
            return 1
        if path.exists():
            print("%s already exists; --create refuses to replace a sidecar" % path)
            return 1
        document = empty(args.mode)
    else:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            sys.stderr.write("cannot read %s: %s\n" % (path, exc))
            return 2

    stamp = args.at or now()
    if args.at:
        try:
            datetime.fromisoformat(args.at)
        except ValueError:
            print("--at %s is not an ISO 8601 instant" % args.at)
            return 1
    if args.event in ("payload_validated_at", "completed_at"):
        payload = path.parent / "review-payload.md"
        report = path.parent / "research-report.md"
        if not payload.is_file() or not payload.stat().st_size or not report.is_file() or not report.stat().st_size:
            print("final payload and research report must both be nonempty")
            return 1
        payload_hash = hashlib.sha256(payload.read_bytes()).hexdigest()
        if args.event == "payload_validated_at":
            document["validated_payload_sha256"] = payload_hash
        elif document.get("validated_payload_sha256") != payload_hash:
            print("the final payload has changed since validation")
            return 1
    problems = record(document, args.event, stamp)
    if problems:
        for problem in problems:
            print(problem)
        return 1
    try:
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    except OSError as exc:
        sys.stderr.write("cannot write %s: %s\n" % (path, exc))
        return 2
    return 0


def self_test() -> int:
    import subprocess
    import tempfile

    script = str(Path(__file__).resolve())
    checks = []
    root = Path(tempfile.mkdtemp())

    def run(*args):
        return subprocess.run([sys.executable, script, *args], capture_output=True,
                              text=True, encoding="utf-8")

    sidecar = root / "timing.json"
    created = run(str(sidecar), "root_dispatched_at", "--create")
    document = json.loads(sidecar.read_text(encoding="utf-8"))
    checks.append(("--create writes the sidecar and the dispatch event",
                   created.returncode == 0 and document["completion_mode"] == "render-only"
                   and document["root_dispatched_at"] and document["completed_at"] is None))
    checks.append(("--create refuses an existing sidecar",
                   run(str(sidecar), "root_dispatched_at", "--create").returncode == 1))
    checks.append(("root_dispatched_at is written once",
                   run(str(sidecar), "root_dispatched_at").returncode == 1))

    (root / "review-payload.md").write_text("payload", encoding="utf-8")
    (root / "research-report.md").write_text("report", encoding="utf-8")
    first = run(str(sidecar), "payload_validated_at")
    stamp = json.loads(sidecar.read_text(encoding="utf-8"))["payload_validated_at"]
    second = run(str(sidecar), "payload_validated_at")
    rewritten = json.loads(sidecar.read_text(encoding="utf-8"))["payload_validated_at"]
    checks.append(("payload_validated_at is rewritable for a re-validated payload",
                   first.returncode == 0 and second.returncode == 0 and rewritten != stamp))

    checks.append(("completed_at is recorded",
                   run(str(sidecar), "completed_at").returncode == 0))
    checks.append(("completed_at is written once",
                   run(str(sidecar), "completed_at").returncode == 1))
    checks.append(("an unknown event is a content violation",
                   run(str(sidecar), "finished_at").returncode == 1))
    checks.append(("a missing sidecar is an input error",
                   run(str(root / "absent.json"), "completed_at").returncode == 2))
    derived = root / "derived.json"
    run(str(derived), "root_dispatched_at", "--create")
    run(str(derived), "payload_validated_at")
    run(str(derived), "completed_at", "--at", "2026-09-09T05:33:54.122000+00:00")
    checks.append(("--at records the given instant",
                   json.loads(derived.read_text(encoding="utf-8"))["completed_at"]
                   == "2026-09-09T05:33:54.122000+00:00"))
    checks.append(("--at rejects a non-instant",
                   run(str(derived), "payload_validated_at", "--at", "yesterday").returncode == 1))

    bare = root / "bare.json"
    bare.write_text(json.dumps(empty("render-only")) + "\n", encoding="utf-8")
    checks.append(("an event cannot precede root_dispatched_at",
                   run(str(bare), "payload_validated_at").returncode == 1))

    for name, passed in checks:
        print("%s %s" % ("ok  " if passed else "FAIL", name))
    return 0 if all(passed for _, passed in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
