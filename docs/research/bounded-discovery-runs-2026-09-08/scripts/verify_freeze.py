#!/usr/bin/env python3
"""Recheck every pin in the #149 freeze against the files it names.

A preregistration is only worth its hashes if someone can recompute them. This
walks ``manifest.json``, resolves every ``{uri, sha256, access}`` reference
against the working tree, and reports each one that no longer matches. It also
rechecks the three things the manifest asserts rather than stores:

* each slot's ``scope.json`` ``source_hash`` still equals the digest of that
  slot's ``packet.md`` — the SourcePacket binding #148 handed to #149;
* the pinned policy commit and skill tree still resolve in this repository;
* the ledger still carries the frozen history and obeys the frozen limits.

The ledger is deliberately **not** pinned by file digest. It is a living artifact:
every cell appends a reservation and a settlement to it, so a digest pin would
fail this check on ordinary progress and block the next dispatch. What is pinned
instead is its **prefix** — the event chain up to and including the ``cap-freeze``
event, which is the history the freeze rests on and which nothing may rewrite.
Everything after that prefix is checked as behaviour rather than as bytes: the
chain is unbroken, the snapshot reconciles to the events, the cap and the
protected reserve are the frozen ones, the closed pre-freeze subtotal has not
moved, and incurred spend plus the protected reserve still fits the cap.

Usage::

    python3 scripts/verify_freeze.py [--manifest FILE] [--repo DIR] [--json]
    python3 scripts/verify_freeze.py --self-test

Run it from the repository root, or pass ``--repo``. Paths in the manifest are
repository-relative.

Exit: 0 when every pin resolves, 1 when any does not, with one line per mismatch
on stdout, 2 when the manifest or the repository cannot be read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE.parent / "manifest.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def refs(node, found=None):
    """Every {uri, sha256, access} object anywhere in the manifest."""
    found = [] if found is None else found
    if isinstance(node, dict):
        if {"uri", "sha256", "access"} <= set(node) and isinstance(node.get("uri"), str):
            found.append(node)
        for value in node.values():
            refs(value, found)
    elif isinstance(node, list):
        for value in node:
            refs(value, found)
    return found


def check_refs(manifest, repo):
    problems = []
    for ref in refs(manifest):
        path = repo / ref["uri"]
        if not path.is_file():
            problems.append("missing pinned file: " + ref["uri"])
            continue
        actual = digest(path)
        if actual != ref["sha256"]:
            problems.append("digest changed for %s: pinned %s, found %s"
                            % (ref["uri"], ref["sha256"], actual))
    return problems


def check_scope_bindings(manifest, repo):
    problems = []
    for slot, target in sorted(manifest["targets"].items()):
        packet = repo / target["source_packet"]["uri"]
        scope_path = repo / target["selected_scope"]["uri"]
        if not packet.is_file() or not scope_path.is_file():
            problems.append("%s: packet or scope missing, binding unverifiable" % slot)
            continue
        scope = json.loads(scope_path.read_text(encoding="utf-8"))
        packet_digest = digest(packet)
        if scope["source_hash"] != packet_digest:
            problems.append("%s: scope source_hash %s does not bind to packet.md %s"
                            % (slot, scope["source_hash"], packet_digest))
        if target["scope_source_binding"]["scope_source_hash"] != scope["source_hash"]:
            problems.append("%s: the manifest quotes a different scope source_hash" % slot)
    return problems


def check_git_pins(manifest, repo):
    problems = []
    for key, kind in (("policy_commit", "commit"), ("skill_tree", "tree")):
        oid = manifest["pins"][key]
        result = subprocess.run(["git", "-C", str(repo), "cat-file", "-t", oid],
                                capture_output=True, text=True, encoding="utf-8")
        if result.returncode or result.stdout.strip() != kind:
            problems.append("pinned %s %s does not resolve to a %s in this repository"
                            % (key, oid, kind))
    return problems


def prefix_digest(events, through_event_id):
    """Digest the event chain up to and including the named event, canonically."""
    prefix = []
    for event in events:
        prefix.append(event)
        if event["event_id"] == through_event_id:
            return hashlib.sha256(
                json.dumps(prefix, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest(), len(prefix)
    return None, 0


def check_ledger(manifest, repo):
    problems = []
    path = repo / manifest["pins"]["ledger"]["uri"]
    if not path.is_file():
        return ["ledger missing: " + manifest["pins"]["ledger"]["uri"]]
    ledger = json.loads(path.read_text(encoding="utf-8"))
    budget = manifest["budget"]
    events = ledger["events"]

    # The frozen history: nothing before and including the cap-freeze may be rewritten.
    pin = manifest["pins"].get("ledger_event_prefix") or {}
    prefix_sha, length = prefix_digest(events, pin.get("through_event_id"))
    if prefix_sha is None:
        problems.append("the pinned cap-freeze event %r is no longer in the ledger"
                        % pin.get("through_event_id"))
    elif prefix_sha != pin.get("events_sha256"):
        problems.append("the frozen ledger history changed: %d events now digest to %s, "
                        "the manifest pins %s" % (length, prefix_sha, pin.get("events_sha256")))

    # The chain itself, and the snapshot it claims to summarise.
    previous, seen = None, set()
    actual = reserved = uncertain = pre_actual = Decimal(0)
    for event in events:
        if event["event_id"] in seen or event["previous_event_id"] != previous:
            problems.append("the ledger event chain breaks at " + event["event_id"])
            break
        seen.add(event["event_id"])
        previous = event["event_id"]
        actual += Decimal(event["actual_delta_usd"])
        reserved += Decimal(event["reservation_delta_usd"])
        uncertain += Decimal(event["uncertainty_usd"])
        if event["phase"] == "pre-freeze":
            pre_actual += Decimal(event["actual_delta_usd"])
    for field, computed in (("actual_usd", actual), ("reserved_usd", reserved),
                            ("uncertainty_usd", uncertain),
                            ("pre_freeze_actual_usd", pre_actual)):
        if Decimal(ledger[field]) != computed:
            problems.append("the ledger snapshot does not reconcile to its events: %s is %s, "
                            "the events sum to %s" % (field, ledger[field], computed))

    # The frozen limits, and the closed pre-freeze subtotal.
    for field in ("frozen_total_cap_usd", "grading_closeout_reserve_usd"):
        if ledger[field] is None:
            problems.append("the ledger's %s is not frozen" % field)
        elif Decimal(ledger[field]) != Decimal(budget[field]):
            problems.append("the ledger's %s is %s, the manifest says %s"
                            % (field, ledger[field], budget[field]))
    if pre_actual != Decimal(budget["pre_freeze_actual_usd"]):
        problems.append("the closed pre-freeze subtotal moved: %s in the ledger, %s in the manifest"
                        % (pre_actual, budget["pre_freeze_actual_usd"]))
    if not any(event["operation"] == "cap-freeze" for event in events):
        problems.append("the ledger has no cap-freeze event")

    # Room left, which is the question the next dispatch actually asks.
    cap = Decimal(ledger["frozen_total_cap_usd"] or 0)
    protected = Decimal(ledger["grading_closeout_reserve_usd"] or 0)
    occupied = actual + reserved + uncertain
    if occupied + protected > cap:
        problems.append("incurred spend, reservations and uncertainty (%s) plus the protected "
                        "reserve (%s) no longer fit the frozen cap (%s)" % (occupied, protected, cap))
    return problems


def check_cells(manifest):
    problems = []
    ids = manifest["cells"]["cell_ids"]
    if len(ids) != manifest["cells"]["planned"] or len(set(ids)) != len(ids):
        problems.append("the cell list is not %d unique ids" % manifest["cells"]["planned"])
    for arm in ("A", "B", "C"):
        if sum(cell.split("-")[2] == arm for cell in ids) != 8:
            problems.append("arm %s does not have eight cells" % arm)
    equal = manifest["limits"]["whole_review_usd_equal_across_arms"]
    if not equal:
        problems.append("the whole-review allowance is not equal across the arms")
    b = manifest["arms"]["B"]["worker"]
    c = manifest["arms"]["C"]["worker"]
    finder = manifest["arms"]["C"]["finder"]
    if (b["model"], b["effort"]) != (c["model"], c["effort"]):
        problems.append("B and C verifier configurations differ")
    if (finder["model"], finder["effort"]) != (c["model"], c["effort"]):
        problems.append("C's finder is not the selected worker configuration")
    if manifest["arms"]["A"]["finder"] is not None or manifest["arms"]["B"]["finder"] is not None:
        problems.append("A or B has a finder")
    if Decimal(manifest["limits"]["finder"]["usd"]) >= Decimal(manifest["limits"]["whole_review_usd_per_attempt"]):
        problems.append("the finder sublimit is not inside the whole-review allowance")
    return problems


def verify(manifest, repo):
    return {"pinned files": check_refs(manifest, repo),
            "scope source bindings": check_scope_bindings(manifest, repo),
            "git pins": check_git_pins(manifest, repo),
            "ledger": check_ledger(manifest, repo),
            "cells and arm invariants": check_cells(manifest)}


def self_test():
    checks = []
    manifest = {"targets": {}, "pins": {"policy_commit": "0" * 40, "skill_tree": "0" * 40},
                "cells": {"planned": 2, "cell_ids": ["slot-1-A-replicate-1", "slot-1-A-replicate-1"]},
                "limits": {"whole_review_usd_equal_across_arms": False,
                           "whole_review_usd_per_attempt": "9.00", "finder": {"usd": "9.00"}},
                "arms": {"A": {"finder": {"model": "x", "effort": "high"}},
                         "B": {"worker": {"model": "x", "effort": "high"}, "finder": None},
                         "C": {"worker": {"model": "y", "effort": "high"},
                               "finder": {"model": "z", "effort": "low"}}}}
    problems = check_cells(manifest)
    for expected in ("unique ids", "eight cells", "not equal across the arms",
                     "verifier configurations differ", "not the selected worker configuration",
                     "A or B has a finder", "not inside the whole-review allowance"):
        checks.append(("rejects: " + expected, any(expected in problem for problem in problems)))
    found = refs({"a": {"uri": "x", "sha256": "y", "access": "z"}, "b": [{"uri": "p", "sha256": "q",
                                                                         "access": "r"}]})
    checks.append(("walks nested references", len(found) == 2))
    checks.append(("ignores objects that are not references", not refs({"uri": "x"})))

    # The ledger is a living artifact: a cell's reservation and settlement must pass, and a
    # rewrite of the frozen history must not.
    import copy
    import tempfile

    def event(eid, previous, phase, operation, actual="0", reservation="0", uncertainty="0"):
        return {"event_id": eid, "previous_event_id": previous, "observed_at": "2026-09-08T00:00:00Z",
                "ticket": 149, "actor": "kamui", "phase": phase, "operation": operation,
                "attempt_id": None, "helper_id": None, "request_refs": [], "reservation_id": eid,
                "actual_delta_usd": actual, "reservation_delta_usd": reservation,
                "uncertainty_usd": uncertainty, "rate_usage_evidence": [], "reason": "synthetic"}

    frozen = [event("e1", None, "pre-freeze", "open"),
              event("e2", "e1", "pre-freeze", "reserve", reservation="2"),
              event("e3", "e2", "pre-freeze", "settle", actual="1", reservation="-2"),
              event("e4", "e3", "pre-freeze", "cap-freeze")]
    pinned_sha, _ = prefix_digest(frozen, "e4")
    base = {"events": list(frozen), "actual_usd": "1", "reserved_usd": "0", "uncertainty_usd": "0",
            "pre_freeze_actual_usd": "1", "frozen_total_cap_usd": "150.00",
            "grading_closeout_reserve_usd": "10.00"}
    manifest = {"pins": {"ledger": {"uri": "ledger.json", "access": "coordinator-only"},
                         "ledger_event_prefix": {"through_event_id": "e4",
                                                 "events_sha256": pinned_sha}},
                "budget": {"frozen_total_cap_usd": "150.00", "grading_closeout_reserve_usd": "10.00",
                           "pre_freeze_actual_usd": "1"}}
    root = Path(tempfile.mkdtemp())

    def run_ledger(ledger):
        (root / "ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
        return check_ledger(manifest, root)

    checks.append(("a frozen ledger passes", not run_ledger(base)))
    live = copy.deepcopy(base)
    live["events"] += [event("e5", "e4", "review", "reserve", reservation="9"),
                       event("e6", "e5", "review", "settle", actual="4", reservation="-9")]
    live.update(actual_usd="5", pre_freeze_actual_usd="1")
    checks.append(("a cell's reservation and settlement pass", not run_ledger(live)))
    rewritten = copy.deepcopy(live)
    rewritten["events"][2]["actual_delta_usd"] = "0.50"
    rewritten.update(actual_usd="4.50", pre_freeze_actual_usd="0.50")
    checks.append(("a rewritten frozen history fails",
                   any("frozen ledger history changed" in p for p in run_ledger(rewritten))))
    broken = copy.deepcopy(live)
    broken["events"][5]["previous_event_id"] = "e4"
    checks.append(("a broken chain fails", any("chain breaks" in p for p in run_ledger(broken))))
    unreconciled = copy.deepcopy(live)
    unreconciled["actual_usd"] = "99"
    checks.append(("a snapshot that does not reconcile fails",
                   any("does not reconcile" in p for p in run_ledger(unreconciled))))
    overspent = copy.deepcopy(live)
    overspent["events"].append(event("e7", "e6", "review", "reserve", reservation="140"))
    overspent["reserved_usd"] = "140"
    checks.append(("spend past the cap fails",
                   any("no longer fit the frozen cap" in p for p in run_ledger(overspent))))
    for name, ok in checks:
        print(("ok   " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in checks) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--repo", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        repo = Path(args.repo).resolve(strict=True)
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 2
    report = verify(manifest, repo)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for group, problems in report.items():
            print("%-28s %s" % (group, "ok" if not problems else "%d problem(s)" % len(problems)))
            for problem in problems:
                print("  " + problem)
    return 0 if not any(report.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
