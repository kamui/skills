#!/usr/bin/env python3
"""Recheck every pin in the #149 freeze against the files it names.

A preregistration is only worth its hashes if someone can recompute them. This
walks ``manifest.json``, resolves every ``{uri, sha256, access}`` reference
against the working tree, and reports each one that no longer matches. It also
rechecks the three things the manifest asserts rather than stores:

* each slot's ``scope.json`` ``source_hash`` still equals the digest of that
  slot's ``packet.md`` — the SourcePacket binding #148 handed to #149;
* the pinned policy commit and skill tree still resolve in this repository;
* the ledger reconciles, its cap and grading reserve are frozen, and the
  pre-freeze spend the manifest quotes is the spend the ledger records.

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


def check_ledger(manifest, repo):
    problems = []
    path = repo / manifest["pins"]["ledger"]["uri"]
    if not path.is_file():
        return ["ledger missing: " + manifest["pins"]["ledger"]["uri"]]
    ledger = json.loads(path.read_text(encoding="utf-8"))
    budget = manifest["budget"]
    for field in ("frozen_total_cap_usd", "grading_closeout_reserve_usd"):
        if ledger[field] is None:
            problems.append("the ledger's %s is not frozen" % field)
        elif Decimal(ledger[field]) != Decimal(budget[field]):
            problems.append("the ledger's %s is %s, the manifest says %s"
                            % (field, ledger[field], budget[field]))
    if Decimal(ledger["pre_freeze_actual_usd"]) != Decimal(budget["pre_freeze_actual_usd"]):
        problems.append("pre-freeze spend is %s in the ledger and %s in the manifest"
                        % (ledger["pre_freeze_actual_usd"], budget["pre_freeze_actual_usd"]))
    if Decimal(ledger["uncertainty_usd"]) != Decimal(budget["retained_uncertainty_usd"]):
        problems.append("retained uncertainty is %s in the ledger and %s in the manifest"
                        % (ledger["uncertainty_usd"], budget["retained_uncertainty_usd"]))
    actual = sum((Decimal(event["actual_delta_usd"]) for event in ledger["events"]), Decimal(0))
    if actual != Decimal(ledger["actual_usd"]):
        problems.append("the ledger snapshot does not reconcile to its events")
    if not any(event["operation"] == "cap-freeze" for event in ledger["events"]):
        problems.append("the ledger has no cap-freeze event")
    occupied = actual + Decimal(ledger["reserved_usd"]) + Decimal(ledger["uncertainty_usd"])
    if occupied + Decimal(ledger["grading_closeout_reserve_usd"] or 0) > Decimal(ledger["frozen_total_cap_usd"] or 0):
        problems.append("incurred spend plus the protected reserve no longer fits the frozen cap")
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
