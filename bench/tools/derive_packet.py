#!/usr/bin/env python3
"""Derive a factual packet from a legacy #137-style packet by removing its run policy.

Usage::

    python3 bench/tools/derive_packet.py <packet.legacy.md> --out <packet.md>
    python3 bench/tools/derive_packet.py --self-test

The #137 packets baked run policy into the forge facts: an experiment label in the title, a
preamble telling the reviewer what it may not do, the local branch layout, the posting identity,
a diff instruction, a "mandatory note" about prior review rounds, a guidance-handling instruction,
and a whole "Run conditions" section carrying the execution allowance, the worker model and the
report rules. The suite gives policy to every arm separately (design §5), so the packet must
carry facts only. This tool removes exactly those elements and keeps every other byte, so the
derived packet is reproducible from the preserved legacy file and its hash can be checked.

Removed, in order of appearance: the parenthetical label at the end of the H1; the preamble
between the H1 and section 1 (replaced by two factual sentences); the local-branch phrases in the
Head SHA and Base ref rows; the Posting identity row; the "Compute the diff as" paragraph; the
"Mandatory note" blockquote in section 5; the "Read any present file" paragraph in section 7;
section 8 and everything after it. Every marker must be present exactly once, otherwise the
packet is refused: a silently partial derivation would be a policy leak.

Exit codes: 0 written, with the output SHA-256 on stdout; 1 the input does not have the legacy
structure, one line per missing or repeated marker on stdout and nothing written; 2 an input
cannot be read or the output cannot be written.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import sys
import tempfile

PREAMBLE = ("Forge state of the pull request frozen at the cutoff named in section 6; records first\n"
            "published after the cutoff are omitted. This packet carries facts only. The run supplies its\n"
            "policy (branch layout, execution allowance, what is unavailable) separately.\n")

H1 = re.compile(r"^# Review packet — `[^`]+#\d+`( \(.*\))?$")
HEAD_ROW = re.compile(r"^(\| Head SHA \| `[0-9a-f]{40}`) \(local branch `review-head`, checked out\) \|$")
BASE_ROW = re.compile(r"^(\| Base ref \| `[^`]+`) \(local branch `[^`]+`, force-pinned to the merge-base\) \|$")
POSTING_ROW = "| Posting identity |"
DIFF_LINE = "Compute the diff as `git diff "
MANDATORY = "> **Mandatory note"
READ_ANY = "Read any present file from the clone with `git show"
SECTION_ONE = "## 1. Pinned run identity"
SECTION_EIGHT = "## 8. Run conditions"


class StructureError(Exception):
    """The input is not a legacy packet; exit code 1 with the reasons."""


def derive(text: str) -> str:
    lines = text.split("\n")
    problems = []

    def find_one(predicate, name: str) -> int:
        hits = [index for index, line in enumerate(lines) if predicate(line)]
        if len(hits) != 1:
            problems.append(f"{name}: expected exactly one, found {len(hits)}")
            return -1
        return hits[0]

    h1 = find_one(lambda line: H1.match(line) is not None, "H1 title")
    one = find_one(lambda line: line.startswith(SECTION_ONE), "section 1 heading")
    head_row = find_one(lambda line: HEAD_ROW.match(line) is not None, "Head SHA row")
    base_row = find_one(lambda line: BASE_ROW.match(line) is not None, "Base ref row")
    posting = find_one(lambda line: line.startswith(POSTING_ROW), "Posting identity row")
    diff = find_one(lambda line: line.startswith(DIFF_LINE), "diff instruction")
    mandatory = find_one(lambda line: line.startswith(MANDATORY), "mandatory note")
    read_any = find_one(lambda line: line.startswith(READ_ANY), "guidance instruction")
    eight = find_one(lambda line: line.startswith(SECTION_EIGHT), "section 8 heading")
    if problems:
        raise StructureError("\n".join(problems))
    if not (h1 < one < head_row < base_row < posting < diff < mandatory < read_any < eight):
        raise StructureError("markers are out of order")
    if h1 != 0:
        raise StructureError("H1 must be the first line")

    drop = set()
    drop.update(range(1, one))  # the preamble, replaced below
    drop.add(posting)
    drop.add(diff)
    index = mandatory
    while index < len(lines) and lines[index].startswith(">"):
        drop.add(index)
        index += 1
    drop.add(read_any)
    drop.update(range(eight, len(lines)))

    out = []
    for index, line in enumerate(lines):
        if index in drop:
            continue
        if line == "" and out and out[-1] == "" and (index - 1) in drop:
            # The blank line that followed a dropped paragraph would otherwise double the one before it.
            continue
        if index == h1:
            out.append(H1.match(line).group(0).replace(H1.match(line).group(1) or "", ""))
            out.append("")
            out.extend(PREAMBLE.rstrip("\n").split("\n"))
            out.append("")
            continue
        if index == head_row:
            out.append(HEAD_ROW.match(line).group(1) + " |")
            continue
        if index == base_row:
            out.append(BASE_ROW.match(line).group(1) + " |")
            continue
        out.append(line)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"


SAMPLE = """# Review packet — `owner/repo#12` (target (x), issue #137 qualification grid)

Phase 1 (target resolution) has already been performed by the orchestrator and is reproduced here in
full. **Do not attempt to re-resolve the target over the network — you have no network access.**

## 1. Pinned run identity

| | |
| --- | --- |
| Pull request | [`owner/repo#12`](https://github.com/owner/repo/pull/12) — "Title" |
| Head SHA | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` (local branch `review-head`, checked out) |
| Base ref | `master` (local branch `master`, force-pinned to the merge-base) |
| Posting identity | `kamui`, who did NOT author the PR → retrospective review with publication disabled |

Compute the diff as `git diff master review-head` (the `master` branch is pinned to the merge-base).

## 2. Changed-file manifest (verified against the pinned SHAs from the mirror)

```
M  a.txt (+1 −1)
```

## 3. Pull-request body, verbatim

````
> a quoted line inside the body stays
## a heading inside the body stays
````

## 5. Commits on the head, oldest first — messages verbatim

| # | SHA | Date | Author | Message |
| --- | --- | --- | --- | --- |
| 1 | `aaaaaaaaa` | 2024-01-01 | A | Title |

> **Mandatory note, same class as prior packets in this program.** Where later commits on the head
> applied the author's responses, that feedback is already fixed.

## 6. Prior review state through the frozen cutoff `2024-01-01T00:00:00Z` (the merge instant), reproduced verbatim

### Review submissions (0)

*(none)*

## 7. Repository guidance present at the merge-base

| Path | Present at merge-base | Blob |
| --- | --- | --- |
| `AGENTS.md` | no | — |

Read any present file from the clone with `git show <base-branch>:<path>` and treat it according to your own skill's guidance contract; record how you classified it.

## 8. Run conditions — binding on this run and on every sub-agent you spawn

1. **Offline.** No network.
2. **Execution allowance.** Focused tests permitted.
"""


def self_test() -> int:
    out = derive(SAMPLE)
    assert out.startswith("# Review packet — `owner/repo#12`\n\n" + PREAMBLE + "\n## 1. Pinned run identity\n"), out[:300]
    assert "| Head SHA | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` |\n" in out
    assert "| Base ref | `master` |\n" in out
    for gone in ("Posting identity", "Compute the diff", "Mandatory note", "Read any present file", "## 8.",
                 "Execution allowance", "issue #137", "no network access"):
        assert gone not in out, gone
    for kept in ("> a quoted line inside the body stays", "## a heading inside the body stays", "### Review submissions (0)",
                 "| `AGENTS.md` | no | — |", "M  a.txt (+1 −1)"):
        assert kept in out, kept
    assert "\n\n\n" not in out, "no triple blank lines"
    assert out.endswith("| `AGENTS.md` | no | — |\n"), out[-80:]
    assert derive(SAMPLE) == out, "derivation must be deterministic"
    for broken, reason in ((SAMPLE.replace("| Posting identity |", "| Poster |"), "Posting identity row"),
                           (SAMPLE + "\n## 8. Run conditions\n", "section 8 heading"),
                           (SAMPLE.replace("## 8. Run conditions", "## 8. Runconditions"), "section 8 heading")):
        try:
            derive(broken)
        except StructureError as error:
            assert reason in str(error), (reason, str(error))
        else:
            raise AssertionError(f"must refuse: {reason}")
    with tempfile.TemporaryDirectory() as temp:
        src = Path(temp, "legacy.md")
        src.write_text(SAMPLE, encoding="utf-8")
        dst = Path(temp, "packet.md")
        import subprocess
        run = subprocess.run([sys.executable, str(Path(__file__).resolve()), str(src), "--out", str(dst)],
                             capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 0 and run.stdout.strip().endswith(hashlib.sha256(out.encode("utf-8")).hexdigest()), run
        assert dst.read_text(encoding="utf-8") == out
        src.write_text("# not a packet\n", encoding="utf-8")
        run = subprocess.run([sys.executable, str(Path(__file__).resolve()), str(src), "--out", str(dst)],
                             capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 1 and "H1 title" in run.stdout, run
    print("self-test ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("legacy", nargs="?")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not (args.legacy and args.out):
        parser.error("give the legacy packet and --out")
    try:
        text = Path(args.legacy).read_text(encoding="utf-8")
    except OSError as error:
        print(f"derive_packet.py: {error}", file=sys.stderr)
        return 2
    try:
        derived = derive(text)
    except StructureError as error:
        print(str(error))
        return 1
    try:
        Path(args.out).write_text(derived, encoding="utf-8")
    except OSError as error:
        print(f"derive_packet.py: {error}", file=sys.stderr)
        return 2
    print(f"{args.out} sha256 {hashlib.sha256(derived.encode('utf-8')).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
