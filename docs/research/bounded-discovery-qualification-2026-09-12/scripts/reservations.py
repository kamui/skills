#!/usr/bin/env python3
"""Derive the extended target reservation set by rule, from the files that publish it.

#199 gap 8 and the proposed specification's gap-8 row: #148 section 7's reservation list is
extended with the four #138 targets, the two excluded registers' pull requests, and **every
pull request named in the revealed candidate inventory** — because that file publishes each
candidate's category and eligibility result, and the hypothesis and upstream confirmation
for those examined that far. The specification is explicit that a freeze *derives* the set
from the inventory rather than transcribing it, so this script is that derivation.

A bare ``#1234`` inside an inventory row is resolved against that row's own repository:
those are the later fixes and confirming issues, and the inventory publishes what each one
proves. They are reserved for the same reason the candidates are.

Usage::

    python3 scripts/reservations.py --research DIR [--out FILE]
    python3 scripts/reservations.py --self-test

``--research`` is this repository's ``docs/research`` directory. Sources read:
``bounded-discovery-prototype/targets/criteria.md`` (section 7),
``bounded-discovery-prototype/targets/exclusions.md``,
``bounded-discovery-decision-2026-09-11/revealed/targets/inventory.md``,
``.../revealed/targets/slots.json`` and the two ``excluded-*-register.md`` files.

Output: UTF-8 JSON with one entry per reserved pull request, its reason, and the source that
names it; plus the source digests, so a later freeze can tell whether the set it applied is
the set these files still publish.

Exit: 0 success, 1 when a required source is missing or names nothing with one line per
violation on stdout, 2 when an input cannot be read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

QUALIFIED = re.compile(r"\b([A-Za-z0-9][\w.-]*/[\w.-]+)#(\d+)\b")
BARE = re.compile(r"(?<![\w/])#(\d+)\b")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qualified_in(text: str):
    return [(repo, number) for repo, number in QUALIFIED.findall(text)]


def inventory_rows(text: str):
    """Yield each inventory row's qualified references and its own bare references.

    A row's first qualified reference is its candidate, and that candidate's repository is
    what a bare ``#1234`` later in the same row refers to.
    """
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        references = qualified_in(line)
        if not references:
            continue
        repo = references[0][0]
        without = QUALIFIED.sub(" ", line)
        yield repo, references, [(repo, number) for number in BARE.findall(without)]


def derive(research: Path):
    targets = research / "bounded-discovery-prototype" / "targets"
    revealed = research / "bounded-discovery-decision-2026-09-11" / "revealed" / "targets"
    sources = {
        "criteria": targets / "criteria.md",
        "exclusions": targets / "exclusions.md",
        "inventory": revealed / "inventory.md",
        "slots": revealed / "slots.json",
        "excluded_grpc_register": revealed / "excluded-grpc-go-8519-register.md",
        "excluded_jwt_register": revealed / "excluded-jwt-456-register.md",
    }
    violations = [name + " is missing: " + str(path)
                  for name, path in sources.items() if not path.exists()]
    if violations:
        return None, violations
    reserved: dict = {}

    def reserve(repo, number, reason, source):
        key = repo + "#" + number
        entry = reserved.setdefault(key, {"repository": repo, "number": int(number),
                                          "reasons": [], "named_by": []})
        if reason not in entry["reasons"]:
            entry["reasons"].append(reason)
        if source not in entry["named_by"]:
            entry["named_by"].append(source)

    criteria = sources["criteria"].read_text(encoding="utf-8")
    section = criteria.partition("## 7. Reservation list")[2].partition("## 8.")[0]
    for repo, number in qualified_in(section):
        reserve(repo, number, "used or reserved by an earlier grid (#148 section 7)",
                "targets/criteria.md section 7")
    if not section.strip():
        violations.append("criteria.md section 7 could not be located")

    for repo, number in qualified_in(sources["exclusions"].read_text(encoding="utf-8")):
        reserve(repo, number, "named in #148's exclusion log", "targets/exclusions.md")

    slots = json.loads(sources["slots"].read_text(encoding="utf-8"))
    slot_text = json.dumps(slots)
    for repo, number in qualified_in(slot_text):
        reserve(repo, number, "a revealed #138 target; its register and leak set are public",
                "revealed/targets/slots.json")

    for name in ("excluded_grpc_register", "excluded_jwt_register"):
        for repo, number in qualified_in(sources[name].read_text(encoding="utf-8")):
            reserve(repo, number, "a revealed excluded register",
                    "revealed/targets/" + sources[name].name)
            break

    inventory = sources["inventory"].read_text(encoding="utf-8")
    candidates = 0
    for repo, references, bares in inventory_rows(inventory):
        candidates += 1
        first = True
        for reference_repo, number in references:
            reserve(reference_repo, number,
                    ("a candidate in the revealed inventory, with its category and eligibility "
                     "result published" if first else
                     "named in a revealed inventory row"),
                    "revealed/targets/inventory.md")
            first = False
        for reference_repo, number in bares:
            reserve(reference_repo, number,
                    "named in a revealed inventory row as a later fix or confirming report",
                    "revealed/targets/inventory.md")
    if not candidates:
        violations.append("the revealed inventory yielded no candidate rows")

    body = {
        "schema_version": "bounded-discovery-qualification-v1",
        "ticket": 207,
        "rule": ("E1 Unused, extended by rule rather than by hand: #148 section 7's list, #148's "
                 "exclusion log, the four revealed #138 targets, the two revealed excluded "
                 "registers, and every pull request named in the revealed candidate inventory - "
                 "candidates and the later fixes and confirming reports their rows cite. A "
                 "candidate on this list cannot be reused blind, and closing an issue or renaming "
                 "a slot does not restore blindness."),
        "derived_at": datetime.now(timezone.utc).isoformat(),
        "sources_sha256": {name: digest(path) for name, path in sources.items()},
        "inventory_rows_read": candidates,
        "reserved_count": len(reserved),
        "reserved": {key: reserved[key] for key in sorted(reserved)},
    }
    return body, violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        if not args.research:
            print("--research is required")
            return 1
        body, violations = derive(args.research)
        for violation in violations:
            print(violation)
        if body is None:
            return 1
        out = args.out or (args.research / "bounded-discovery-qualification-2026-09-12" /
                           "targets" / "reservations.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
        print("reserved " + str(body["reserved_count"]) + " pull requests from " +
              str(body["inventory_rows_read"]) + " inventory rows -> " + str(out))
        return 1 if violations else 0
    except (OSError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2


def self_test():
    failures = []

    def check(name, condition):
        if not condition:
            failures.append(name)

    check("a qualified reference is read",
          qualified_in("see `owner/repo#12` here") == [("owner/repo", "12")])
    check("a bare reference alone is not qualified", qualified_in("see #12 here") == [])
    rows = list(inventory_rows(
        "| 1 | `a/b#7` head x | 2025-01-01 | 1 file | pass | h | `#99` (2026) and `#100` |\n"
        "not a row\n"
        "| 2 | `c/d#8` | — | — | E3 fail | — | — |\n"))
    check("each row yields its candidate", [row[1][0] for row in rows] ==
          [("a/b", "7"), ("c/d", "8")])
    check("a bare reference resolves to its row's repository",
          rows[0][2] == [("a/b", "99"), ("a/b", "100")])
    check("a row with no bare reference yields none", rows[1][2] == [])
    check("a non-row line is skipped", len(rows) == 2)

    for failure in failures:
        print("FAIL", failure)
    print(("FAILED " + str(len(failures))) if failures else "ok: 6 checks")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
