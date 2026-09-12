#!/usr/bin/env python3
"""Derive the extended target reservation set by rule, from the files that publish it.

#199 gap 8 and the proposed specification's gap-8 row: #148 section 7's reservation list is
extended with the four #138 targets, the two excluded registers' pull requests, and **every
pull request named in the revealed candidate inventory** — because that file publishes each
candidate's category and eligibility result, and the hypothesis and upstream confirmation
for those examined that far. The specification is explicit that a freeze *derives* the set
from those files rather than transcribing it, so this script is that derivation.

How a reference is read, and why it matters:

- **Only a code span counts** in a Markdown source. These files cite this project's own
  tickets in running prose — "(#124 hunt", "#137 record" — and a rule that read every bare
  ``#1234`` would invent reservations in the wrong repository for each one. Every genuine
  pull-request reference in these files is backticked; every project citation is not.
- A code span is a **qualified** reference (``owner/repo#123``), a **repository** on its own
  (``owner/repo``, as in "``traefik/traefik`` (via ``#10244``)"), or a **bare** number
  (``#123``) that belongs to the repository most recently named in its own scope — the row,
  for a table; the running text, for section 7's comma list.
- A span that is plainly a path rather than a repository is not allowed to set the scope's
  repository. Two segments only, and not something ending in a file extension a repository
  name cannot have, so ``sealed/excluded-grpc-go-8519-register.md.enc`` is skipped while
  ``vercel/next.js`` and ``nats-io/nats.go`` are not.
- A **register** is about exactly one repository, named in its own header, so every ``#123``
  in it resolves there whether it is backticked or not. That is deliberately conservative:
  a register also cites this project's own tickets in prose ("clean per #137 hunt"), and no
  mechanical rule separates those from a genuine same-repository number. Reserving one that
  did not need it costs a future hunt one candidate; failing to reserve one that did costs
  the study its blind, so the rule errs toward reserving and marks every entry it could not
  prove ``conservative`` rather than asserting it.

Usage::

    python3 scripts/reservations.py --research DIR [--out FILE]
    python3 scripts/reservations.py --self-test

``--research`` is this repository's ``docs/research`` directory.

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

CODE_SPAN = re.compile(r"`([^`\n]+)`")
QUALIFIED = re.compile(r"^([A-Za-z0-9][\w.-]*/[\w.-]+)#(\d+)$")
REPOSITORY = re.compile(r"^([A-Za-z0-9][\w.-]*/[\w.-]+)$")
BARE = re.compile(r"^#(\d+)$")
ANY_NUMBER = re.compile(r"#(\d+)\b")
# Extensions a repository name cannot end in. Without this, a backticked path such as
# `sealed/excluded-grpc-go-8519-register.md.enc` would set the scope's repository and every
# bare number after it would be reserved in a repository that does not exist.
NOT_A_REPOSITORY = (".enc", ".md", ".json", ".jsonl", ".py", ".txt", ".sh", ".yml",
                    ".yaml", ".log", ".csv", ".lock", ".toml")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def looks_like_a_repository(span: str) -> bool:
    return (bool(REPOSITORY.match(span)) and span.count("/") == 1
            and not span.lower().endswith(NOT_A_REPOSITORY))


def references(text: str, repository=None):
    """Yield ``(repository, number, kind)`` for every reference in one scope."""
    current = repository
    for span in CODE_SPAN.findall(text):
        qualified = QUALIFIED.match(span)
        if qualified:
            current = qualified.group(1)
            yield current, qualified.group(2), "qualified"
            continue
        bare = BARE.match(span)
        if bare:
            if current:
                yield current, bare.group(1), "bare"
            continue
        if looks_like_a_repository(span):
            current = span


def per_line(text: str):
    """References scoped to one line, for a table whose rows each name their own repository."""
    for line in text.splitlines():
        for reference in references(line):
            yield reference


def register_numbers(text: str, repository: str):
    """Every number in a register, split by how well the file evidences it.

    ``strong``: backticked, qualified, or inside a link to this register's own repository.
    ``conservative``: any other bare number in the file. Both are reserved; only the first
    is asserted.
    """
    strong = set()
    for span in CODE_SPAN.findall(text):
        qualified = QUALIFIED.match(span)
        if qualified and qualified.group(1) == repository:
            strong.add(qualified.group(2))
        elif BARE.match(span):
            strong.add(BARE.match(span).group(1))
    for number in re.findall(r"\[#(\d+)\]\(https://github\.com/" +
                             re.escape(repository) + r"/", text):
        strong.add(number)
    everything = set(ANY_NUMBER.findall(text))
    return sorted(strong, key=int), sorted(everything - strong, key=int)


def register_repository(text: str):
    """The one repository a register is about, from the first repository span in it."""
    for span in CODE_SPAN.findall(text):
        qualified = QUALIFIED.match(span)
        if qualified:
            return qualified.group(1)
        if looks_like_a_repository(span):
            return span
    return None


def derive(research: Path):
    targets = research / "bounded-discovery-prototype" / "targets"
    revealed = research / "bounded-discovery-decision-2026-09-11" / "revealed" / "targets"
    sources = {
        "criteria": targets / "criteria.md",
        "exclusions": targets / "exclusions.md",
        "inventory": revealed / "inventory.md",
        "slots": revealed / "slots.json",
    }
    registers = sorted(list(revealed.glob("slot-*-register.md")) +
                       list(revealed.glob("excluded-*-register.md")))
    for register in registers:
        sources["register:" + register.stem] = register
    violations = [name + " is missing: " + str(path)
                  for name, path in sources.items() if not path.exists()]
    if not registers:
        violations.append("no register was found under " + str(revealed))
    if violations:
        return None, violations
    reserved: dict = {}

    def reserve(repository, number, reason, source):
        key = repository + "#" + number
        entry = reserved.setdefault(key, {"repository": repository, "number": int(number),
                                          "reasons": [], "named_by": []})
        if reason not in entry["reasons"]:
            entry["reasons"].append(reason)
        if source not in entry["named_by"]:
            entry["named_by"].append(source)

    criteria = sources["criteria"].read_text(encoding="utf-8")
    section = criteria.partition("## 7. Reservation list")[2].partition("## 8.")[0]
    if not section.strip():
        violations.append("criteria.md section 7 could not be located")
    for repository, number, _ in references(section):
        reserve(repository, number, "used or reserved by an earlier grid (#148 section 7)",
                "targets/criteria.md section 7")

    for repository, number, _ in per_line(sources["exclusions"].read_text(encoding="utf-8")):
        reserve(repository, number, "named in #148's exclusion log", "targets/exclusions.md")

    for repository, number in QUALIFIED_IN_TEXT.findall(
            sources["slots"].read_text(encoding="utf-8")):
        reserve(repository, number, "a revealed #138 slot", "revealed/targets/slots.json")

    for name, path in sources.items():
        if not name.startswith("register:"):
            continue
        text = path.read_text(encoding="utf-8")
        repository = register_repository(text)
        if not repository:
            violations.append(str(path) + " names no repository, so its numbers cannot resolve")
            continue
        reason = ("a revealed #138 target's register, or a pull request it names"
                  if path.name.startswith("slot-") else
                  "a revealed excluded register, or a pull request it names")
        strong, conservative = register_numbers(text, repository)
        for number in strong:
            reserve(repository, number, reason, "revealed/targets/" + path.name)
        for number in conservative:
            reserve(repository, number,
                    reason + ", read conservatively: the file cites it as a bare number in "
                    "prose, which no rule can separate from a citation of this project's own "
                    "tickets, so it is reserved rather than asserted",
                    "revealed/targets/" + path.name)
            reserved[repository + "#" + number]["confidence"] = "conservative"

    inventory = sources["inventory"].read_text(encoding="utf-8")
    rows = 0
    for line in inventory.splitlines():
        if not line.startswith("|"):
            continue
        found = list(references(line))
        if not found:
            continue
        rows += 1
        for index, (repository, number, kind) in enumerate(found):
            reserve(repository, number,
                    ("a candidate in the revealed inventory, with its category and eligibility "
                     "result published" if index == 0 and kind == "qualified" else
                     "named in a revealed inventory row as a later fix, a confirming report or "
                     "a related change"),
                    "revealed/targets/inventory.md")
    if not rows:
        violations.append("the revealed inventory yielded no candidate rows")

    body = {
        "schema_version": "bounded-discovery-qualification-v1",
        "ticket": 207,
        "rule": ("E1 Unused, extended by rule rather than by hand: #148 section 7's list, #148's "
                 "exclusion log, the revealed #138 slot registers, the two revealed excluded "
                 "registers, and every pull request named in the revealed candidate inventory - "
                 "candidates and the later fixes and confirming reports their rows cite. Only a "
                 "backticked reference counts in a Markdown list or table, because these files "
                 "also cite this project's own tickets in prose; a register is about one "
                 "repository and every number in it resolves there. A candidate on this list "
                 "cannot be reused blind, and closing an issue or renaming a slot does not "
                 "restore blindness."),
        "derived_at": datetime.now(timezone.utc).isoformat(),
        "sources_sha256": {name: digest(path) for name, path in sources.items()},
        "inventory_rows_read": rows,
        "reserved_count": len(reserved),
        "reserved": {key: reserved[key] for key in sorted(reserved)},
    }
    return body, violations


QUALIFIED_IN_TEXT = re.compile(r"\b([A-Za-z0-9][\w.-]*/[\w.-]+)#(\d+)\b")


def self_test():
    failures = []

    def check(name, condition):
        if not condition:
            failures.append(name)

    found = list(references("see `owner/repo#12`, `#13` and `#14` here"))
    check("a qualified reference is read", found[0] == ("owner/repo", "12", "qualified"))
    check("a bare reference follows its repository",
          [f[:2] for f in found[1:]] == [("owner/repo", "13"), ("owner/repo", "14")])
    check("an unbackticked project citation is ignored",
          list(references("`a/b#1` E9 fail (#124 hunt: nothing of its own)")) ==
          [("a/b", "1", "qualified")])
    check("a repository span alone anchors a bare number",
          [f[:2] for f in references("`traefik/traefik` (via `#10244`)")] ==
          [("traefik/traefik", "10244")])
    check("a dotted repository name still anchors",
          [f[:2] for f in references("`vercel/next.js` (via `#96725`)")] ==
          [("vercel/next.js", "96725")])
    check("a sealed path does not anchor",
          list(references("`golang-jwt/jwt#456` sealed `sealed/x-register.md.enc` then `#484`"))
          == [("golang-jwt/jwt", "456", "qualified"), ("golang-jwt/jwt", "484", "bare")])
    check("a bare number with no repository yet is dropped",
          list(references("`#99` with nothing before it")) == [])
    rows = list(per_line("| `a/b#7` | `#99` |\nnot a row\n| `c/d#8` | `#100` |"))
    check("a row's bare number does not leak into the next row",
          [r[:2] for r in rows] == [("a/b", "7"), ("a/b", "99"),
                                    ("c/d", "8"), ("c/d", "100")])
    check("a register's repository comes from its header",
          register_repository("# Target\n\n- Repository: `clap-rs/clap`, base `master`.") ==
          "clap-rs/clap")
    check("a register with only a path names no repository",
          register_repository("see `sealed/x.md.enc`") is None)
    strong, conservative = register_numbers(
        "- Pull request: [#456](https://github.com/golang-jwt/jwt/pull/456)\n"
        "- see `#510` and later commits #484, and clean per #137 hunt\n", "golang-jwt/jwt")
    check("a linked and a backticked number are strong", strong == ["456", "510"])
    check("a bare prose number is reserved conservatively", conservative == ["137", "484"])

    for failure in failures:
        print("FAIL", failure)
    print(("FAILED " + str(len(failures))) if failures else "ok: 12 checks")
    return 1 if failures else 0


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


if __name__ == "__main__":
    sys.exit(main())
