#!/usr/bin/env python3
"""Account a raw verifier JSON return against its pinned brief bundle.

Usage: python3 scripts/account_verifier_return.py --bundle <directory>
       --output accounting.json [--repair-of <original>] <return>
Schema: references/verifier.md's return encoding; bundle from build_verifier_prompt.py.
<return> is the primary's verbatim save of the worker's inline response. The bundle must
be a ``verifier-manifest/3`` bundle whose manifest still matches its input and brief and
whose brief prints its ``bundle_id``; an older or altered bundle is refused with no report.
A return whose ``bundle_id`` is not that bundle's answers another brief, even with the same
run, batch and task IDs, and withholds every task. ``--repair-of`` accounts a separate
repaired return, recording the original's path and hash; the original must carry the
bundle's ID, so a repair cannot pair a foreign return. The report's ``repair_of`` key
records it.
Exit 0: structurally complete, not confirmed; 1: content violations, one per
stdout line, with an accounting report partitioning each role; 2: unreadable
input or unwritable output, named on stderr. The raw return stays untouched;
judgments, corrections, safety rulings and asides are retained verbatim as JSON
values in the report, including on exit 1. No evidence or verdict is invented.
A task is accounted only by exactly one record in its own role that cites at
least one raw location, or, for an unresolved result, names its settling fact;
a missing, duplicated, foreign, or unusable record leaves the task withheld.
"""
from __future__ import annotations

import argparse
from collections import Counter
import os
from pathlib import Path
import sys

from build_verifier_prompt import (
    BASES, MANIFEST_FORMAT, ContentError, anchor, bundle_line, choice, digest,
    evidence_list, fields, json_text, make_manifest, obj, parse_json, read_json,
    require, seq, string, unique_ids,
)

ACCOUNTING_FORMAT = "verifier-accounting/3"


def exact_keys(value, required, optional, where):
    obj(value, where)
    require(set(required) <= value.keys(), where, "missing fields: " + ", ".join(sorted(set(required) - value.keys())))
    require(value.keys() <= set(required) | set(optional), where, "unknown fields: " + ", ".join(sorted(value.keys() - set(required) - set(optional))))


def safety(value, where):
    for i, ruling in enumerate(seq(value, where)):
        loc = f"{where}[{i}]"
        exact_keys(ruling, ("path", "conditions", "premise", "ruling", "evidence"), (), loc)
        fields(ruling, ("path", "conditions", "premise"), loc)
        choice(ruling["ruling"], {"holds", "fails", "unresolved"}, loc + ".ruling")
        evidence_list(ruling["evidence"], loc + ".evidence")


def cited(record, where):
    """A usable result cites at least one raw location; named unavailable evidence alone settles nothing."""
    require(any("text" in item for item in record["evidence"] if isinstance(item, dict)), where + ".evidence",
            "cite at least one raw location, or return unresolved with its settling fact")


def verdict(record, kind, where):
    exact_keys(record, ("id", "verdict", "basis", "evidence"),
               ("settling_fact", "corrections", "safety_rulings"), where)
    choice(record["verdict"], {"confirmed", "refuted"}, where + ".verdict")
    string(record["basis"], where + ".basis")
    if record["verdict"] == "refuted":
        choice(record["basis"], BASES, where + ".basis")
        require(not (record["basis"] == "pre-existing" and kind == "requirement"), where, "pre-existing is Code only")
        if record["basis"] == "unresolved":
            string(record.get("settling_fact"), where + ".settling_fact")
    evidence_list(record["evidence"], where + ".evidence")
    if not (record["verdict"] == "refuted" and record["basis"] == "unresolved"):
        cited(record, where)
    if "settling_fact" in record:
        string(record["settling_fact"], where + ".settling_fact")
    if "safety_rulings" in record:
        safety(record["safety_rulings"], where + ".safety_rulings")
    if "corrections" in record:
        corrections = record["corrections"]
        exact_keys(corrections, (), ("trigger", "impact", "priority", "action", "anchor", "fix", "change"), where + ".corrections")
        for name, value in corrections.items():
            loc = where + ".corrections." + name
            if name == "anchor":
                anchor(value, loc)
            elif name == "priority":
                choice(value, {"P0", "P1", "P2", "P3"}, loc)
            elif name == "action":
                choice(value, {"must-fix", "consider"}, loc)
            else:
                string(value, loc)


def ruling(record, where):
    exact_keys(record, ("id", "ruling", "evidence"), ("failed_step", "settling_fact"), where)
    choice(record["ruling"], {"holds", "fails", "unresolved"}, where + ".ruling")
    evidence_list(record["evidence"], where + ".evidence")
    for name in ("failed_step", "settling_fact"):
        if name in record:
            string(record[name], where + "." + name)
    if record["ruling"] == "fails":
        string(record.get("failed_step"), where + ".failed_step")
    if record["ruling"] == "unresolved":
        string(record.get("settling_fact"), where + ".settling_fact")
    else:
        cited(record, where)


def account(data, manifest, manifest_hash, returned):
    expected = {"candidates": {item["id"]: item for item in data["candidates"]},
                "premises": {item["id"]: item for item in data["premises"]}}
    errors = []
    accounted = {"candidates": [], "premises": []}
    withheld = {role: list(items) for role, items in expected.items()}
    report = {"format": ACCOUNTING_FORMAT, "bundle_id": manifest["bundle_id"], "manifest_sha256": manifest_hash,
              "structurally_complete": False, "violations": errors,
              "accounted": accounted, "withheld": withheld, "return": returned}
    try:
        obj(returned, "return")
        require(returned.get("bundle_id") == manifest["bundle_id"], "return.bundle_id",
                "not this bundle's ID; the return answers another brief")
    except ContentError as error:
        errors.append(str(error))
        return report
    try:
        exact_keys(returned, ("bundle_id", "candidates", "premises", "duplicate_groups", "observation"),
                   (), "return")
    except ContentError as error:
        errors.append(str(error))
    for role, items in expected.items():
        records = returned.get(role)
        if not isinstance(records, list):
            errors.append(f"{role}: expected array")
            continue
        counts = Counter(record.get("id") for record in records
                         if isinstance(record, dict) and isinstance(record.get("id"), str))
        for key in items:
            if counts[key] != 1:
                errors.append(f"{role}[{key}]: expected exactly one record; got {counts[key]}")
        for i, record in enumerate(records):
            loc = f"{role}[{i}]"
            try:
                key = string(obj(record, loc).get("id"), loc + ".id")
                require(key in items, loc, f"unknown or wrong-role ID {key}")
                if role == "candidates":
                    verdict(record, items[key]["kind"], loc)
                else:
                    ruling(record, loc)
                if counts[key] == 1:
                    accounted[role].append(key)
            except ContentError as error:
                errors.append(str(error))
        withheld[role] = [key for key in items if key not in accounted[role]]
    try:
        groups = seq(returned.get("duplicate_groups"), "duplicate_groups")
        for i, group in enumerate(groups):
            ids = unique_ids(group, f"duplicate_groups[{i}]")
            require(len(ids) >= 2 and set(ids) <= expected["candidates"].keys(),
                    f"duplicate_groups[{i}]", "expected at least two supplied candidate IDs")
        observation = returned.get("observation")
        if observation is not None:
            exact_keys(observation, ("fact", "evidence"), (), "observation")
            string(observation["fact"], "observation.fact")
            evidence_list(observation["evidence"], "observation.evidence")
    except ContentError as error:
        errors.append(str(error))
    report["structurally_complete"] = not errors
    return report


def withheld_report(manifest, manifest_hash, violations):
    return {"format": ACCOUNTING_FORMAT, "bundle_id": manifest["bundle_id"], "manifest_sha256": manifest_hash,
            "structurally_complete": False, "violations": violations,
            "accounted": {"candidates": [], "premises": []},
            "withheld": {"candidates": manifest["candidate_ids"], "premises": manifest["premise_ids"]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_return", help="the verbatim save of the worker's inline response, or a repaired return")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--output", required=True, help="new accounting report, never the raw return")
    parser.add_argument("--repair-of", metavar="ORIGINAL", help="the unmodified return this repaired file was made from")
    args = parser.parse_args()
    EVENT.update(event="verifier-return-accounted", bundle=args.bundle)
    try:
        bundle = Path(args.bundle)
        data = read_json(bundle / "input.json")
        manifest_raw = (bundle / "manifest.json").read_bytes()
        manifest = parse_json(manifest_raw.decode("utf-8"))
        brief = (bundle / "brief.md").read_bytes()
        obj(manifest, "manifest")
        require(manifest.get("format") == MANIFEST_FORMAT, "bundle",
                f"manifest format {manifest.get('format')!r} is not {MANIFEST_FORMAT}; rebuild the bundle with this skill's builder")
        bundle_id = string(manifest.get("bundle_id"), "manifest.bundle_id")
        obj(data, "bundle input")
        for name in ("run", "batch", "candidates", "premises"):
            require(name in data, "bundle input", f"missing {name}")
        for role in ("candidates", "premises"):
            seq(data[role], "bundle " + role)
            unique_ids([string(obj(item, role).get("id"), role + ".id") for item in data[role]], role)
        require(brief.decode("utf-8").count(bundle_line(bundle_id)) == 1, "bundle", "brief does not print the manifest's bundle ID once")
        require(manifest == make_manifest(data, brief, bundle_id), "bundle", "manifest does not match input/brief identity")
        manifest_hash = digest(manifest_raw)
        raw = Path(args.raw_return).read_bytes()
        repair = None
        if args.repair_of:
            if os.path.realpath(args.repair_of) == os.path.realpath(args.raw_return):
                raise OSError("--repair-of names the repaired file itself")
            original = Path(args.repair_of).read_bytes()
            repair = {"path": str(Path(args.repair_of).resolve()), "sha256": digest(original)}
        if repair is not None and bundle_id.encode("utf-8") not in original:
            report = withheld_report(manifest, manifest_hash, [
                "repair_of: the original return does not carry this bundle's ID; a repair cannot pair another brief's return"])
        else:
            try:
                returned = parse_json(raw.decode("utf-8"))
                report = account(data, manifest, manifest_hash, returned)
            except (ValueError, UnicodeError) as error:
                report = withheld_report(manifest, manifest_hash, [f"return: {error}"])
        EVENT.update(manifest=manifest, report=report)
        report["raw_return"] = str(Path(args.raw_return).resolve())
        report["raw_return_sha256"] = digest(raw)
        if repair is not None:
            report["repair_of"] = repair
        with open(args.output, "x", encoding="utf-8") as output:
            output.write(json_text(report))
        for error in report["violations"]:
            print(error)
        if report["structurally_complete"]:
            print("structurally complete; judgments and evidence still require primary reconciliation")
        return 0 if report["structurally_complete"] else 1
    except ContentError as error:
        print(error)
        return 1
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
        print(f"account_verifier_return: cannot read bundle/return or write report: {error}", file=sys.stderr)
        return 2


# What this accounting hands run_events.py; recording never changes the result.
EVENT = {}


if __name__ == "__main__":
    import time

    started_ns = time.monotonic_ns()
    status = main()
    try:
        import run_events

        run_events.record(EVENT, status, started_ns, "account_verifier_return.py")
    except Exception:
        pass
    raise SystemExit(status)
