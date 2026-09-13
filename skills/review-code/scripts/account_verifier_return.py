#!/usr/bin/env python3
"""Account a raw verifier JSON return against its pinned brief bundle.

Usage: python3 scripts/account_verifier_return.py --bundle <directory>
       --output accounting.json raw-return.json
Schema: references/verifier-return.md; bundle from build_verifier_prompt.py.
Exit 0: structurally complete, not confirmed; 1: content violations, one per
stdout line, with an accounting report partitioning each role; 2: unreadable
input or unwritable output, named on stderr. The raw return stays untouched;
judgments, corrections, safety rulings and asides are retained verbatim as JSON
values in the report, including on exit 1. No evidence or verdict is invented.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

from build_verifier_prompt import (
    BASES, ContentError, anchor, choice, digest, evidence_list, fields,
    json_text, make_manifest, obj, parse_json, read_json, require, seq, string,
    unique_ids,
)


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
    exact_keys(record, ("id", "ruling", "evidence"), ("failed_step", "safety_rulings"), where)
    choice(record["ruling"], {"holds", "re-open"}, where + ".ruling")
    evidence_list(record["evidence"], where + ".evidence")
    if record["ruling"] == "re-open":
        string(record.get("failed_step"), where + ".failed_step")
    elif "failed_step" in record:
        string(record["failed_step"], where + ".failed_step")
    if "safety_rulings" in record:
        safety(record["safety_rulings"], where + ".safety_rulings")


def account(data, manifest, manifest_hash, returned):
    expected = {"candidates": {item["id"]: item for item in data["candidates"]},
                "ledger": {item["id"]: item for item in data["ledger"]}}
    errors = []
    accounted = {"candidates": [], "ledger": []}
    withheld = {role: list(items) for role, items in expected.items()}
    report = {"format": "verifier-accounting/1", "manifest_sha256": manifest_hash,
              "structurally_complete": False, "violations": errors,
              "accounted": accounted, "withheld": withheld,
              "return": returned, "conclusion_accounted": False}
    try:
        obj(returned, "return")
        require(returned.get("manifest_sha256") == manifest_hash, "return.manifest_sha256", "wrong run/batch/brief pairing")
    except ContentError as error:
        errors.append(str(error))
        return report
    try:
        exact_keys(returned, ("manifest_sha256", "candidates", "ledger", "duplicate_groups", "observation"),
                   ("conclusion",), "return")
    except ContentError as error:
        errors.append(str(error))
    ledger_valid = True
    for role, items in expected.items():
        errors_before = len(errors)
        records = returned.get(role)
        if not isinstance(records, list):
            errors.append(f"{role}: expected array")
            if role == "ledger":
                ledger_valid = False
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
        if role == "ledger":
            ledger_valid = len(errors) == errors_before
    try:
        conclusion = returned.get("conclusion")
        if manifest["batch"]["mode"] == "complete-ledger":
            require(ledger_valid, "conclusion", "cannot cover missing or unusable ledger rulings")
            reopened = [row["id"] for row in returned["ledger"]
                        if row.get("id") in expected["ledger"] and row.get("ruling") == "re-open"]
            if reopened:
                exact_keys(conclusion, ("re_open",), (), "conclusion")
                ids = unique_ids(conclusion["re_open"], "conclusion.re_open")
                require(set(ids) == set(reopened), "conclusion", "re_open IDs must equal re-open rulings")
            else:
                require(conclusion == "clean verdict stands", "conclusion", "expected clean verdict stands")
            report["conclusion_accounted"] = True
        else:
            require("conclusion" not in returned, "conclusion", "only complete-ledger owns a batch conclusion")
    except ContentError as error:
        errors.append(str(error))
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_return")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--output", required=True, help="new accounting report, never the raw return")
    args = parser.parse_args()
    try:
        bundle = Path(args.bundle)
        data = read_json(bundle / "input.json")
        manifest_raw = (bundle / "manifest.json").read_bytes()
        manifest = parse_json(manifest_raw.decode("utf-8"))
        brief = (bundle / "brief.md").read_bytes()
        obj(manifest, "manifest")
        obj(data, "bundle input")
        for name in ("run", "batch", "candidates", "ledger"):
            require(name in data, "bundle input", f"missing {name}")
        seq(data["candidates"], "bundle candidates")
        seq(data["ledger"], "bundle ledger")
        for role in ("candidates", "ledger"):
            unique_ids([string(obj(item, role).get("id"), role + ".id") for item in data[role]], role)
        require(manifest == make_manifest(data, brief, manifest.get("full_ledger_sha256")),
                "bundle", "manifest does not match input/brief identity")
        manifest_hash = digest(manifest_raw)
        raw = Path(args.raw_return).read_bytes()
        try:
            returned = parse_json(raw.decode("utf-8"))
            report = account(data, manifest, manifest_hash, returned)
        except (ValueError, UnicodeError) as error:
            report = {"format": "verifier-accounting/1", "manifest_sha256": manifest_hash,
                      "structurally_complete": False, "violations": [f"return: {error}"],
                      "accounted": {"candidates": [], "ledger": []},
                      "withheld": {"candidates": manifest["candidate_ids"], "ledger": manifest["ledger_ids"]},
                      "conclusion_accounted": False}
        report["raw_return"] = str(Path(args.raw_return).resolve())
        report["raw_return_sha256"] = digest(raw)
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


if __name__ == "__main__":
    raise SystemExit(main())
