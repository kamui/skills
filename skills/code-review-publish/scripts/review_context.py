#!/usr/bin/env python3
"""Build the local review context for code-review-publish in one call.

Emits, for the pinned merge-base and head of one pull request, the changed-file
manifest, the complete merge-base diff with function context, the head and
merge-base line ranges of every hunk, and the last commits before the merge-base
that touched each changed path. It reads only the local git repository: it never
calls `gh`, never touches the network, and never prints a whole file.

Usage:
    python3 scripts/review_context.py --merge-base SHA --head SHA [--json]
    python3 scripts/review_context.py --merge-base SHA --head SHA \
        --prior-head SHA [--base-ref NAME] [--json]
    python3 scripts/review_context.py --merge-base SHA --head SHA [...] \
        --path P [--path P ...]
    python3 scripts/review_context.py --merge-base SHA --head SHA [...] \
        --store FILE [--chunk-bytes N]
    python3 scripts/review_context.py --from FILE
    python3 scripts/review_context.py --from FILE [--section diff|delta-diff] \
        --path P [--path P ...] [--chunk K]
    python3 scripts/review_context.py --self-test

Run it from inside the clone under review. Default output is Markdown with one
fenced block per section, in this order: `## manifest`, `## diff`, `## ranges`,
`## history`. `--json` emits the same content as one JSON object. With no
selection or store option the output is exactly the four sections above.

On a re-review, `--prior-head SHA` (the `head=` of the earlier review's run
trailer) appends four sections after `## history`. The script reports; it does
not decide the review's scope.

- `## delta-conditions`: `ancestor: yes|no` (`git merge-base --is-ancestor
  <prior-head> <head>`), `merge-base-unchanged: yes|no` (compare `git
  merge-base <base-ref> <prior-head>` with `git merge-base <base-ref> <head>`,
  or `unknown (no --base-ref)` when `--base-ref NAME` is not given), and
  `prior-head-reachable: yes|no` (`git cat-file -e <prior-head>`).
- `## delta-manifest`: the manifest format below, for `<prior-head>...<head>`.
- `## delta-diff`: `git diff <prior-head>...<head> --function-context`,
  verbatim, with the same notes as `## diff`.
- `## delta-overlap`: one line per delta hunk, `<path>:<start>-<end> overlaps
  <path>:<start>-<end>` for each `## ranges` line on the `@head` side that
  shares at least one line with it, or `<path>:<start>-<end> overlaps none`.

When the prior head is not reachable, the three sections after
`## delta-conditions` are empty, since no delta can be computed against it.

Manifest lines read `<status> <path> [<- <old path>] +<ins> -<del> new=<yes|no>
lines=<n>`, where `status` is `A`, `M`, `D`, or `R`; `new=yes` marks a path the
diff adds in full, so it is not read again; `lines` is the path's line count at
head, and `0` for a deletion. A binary path reports `+- --` for its counts.

Range lines read `<path>:<start>-<end> @head` and `<path>:<start>-<end>
@merge-base`, one pair per hunk, covering the lines the function-context hunk
spans on that side. A side a hunk covers no lines on -- the merge-base side of a
pure addition, the head side of a pure deletion -- has no line.

The diff is followed by `note: no function context for <path>; read enclosing
ranges by hand` for each modified path whose every hunk header carries an empty
section. A path the diff adds or deletes in full draws no note, since the diff
already holds every line of it. Every section passes `-M` to git, so the
manifest, diff, and ranges rest on one rename decision whatever `diff.renames`
is set to.

Selection and bounded recovery (large diffs):

`--path P`, repeatable, restricts `## diff` (and `## delta-diff` when present)
to the named repo-relative paths and adds a `## selection` section listing the
selected manifest lines. `## manifest`, `## ranges`, `## history`, and the
other delta sections stay complete, so unselected files remain accounted for.
A selection is a literal path, never a pattern or an option: it must equal a
manifest path, or the old path of a rename, byte for byte, and any other value
is an input error (exit 2). Write `--path=<path>` for a path that begins with
`-`. Git never sees a selection as a pathspec; the only pathspec the script
passes to git (the history query) is wrapped in `:(top,literal)`, so spaces,
leading dashes, brackets, and wildcard characters in a filename are neither
options nor globs.

`--store FILE` persists the complete context to FILE before any output, as one
private JSON object, and turns on bounded output: one call prints at most
`--chunk-bytes` bytes of diff text (default 24000; choose a value below the
harness's tool-output limit). FILE holds the pull request's whole diff, so it
is opened without following symlinks, refused unless it is an unshared regular
file this user owns, and set to mode 0600 before the first byte is written;
give it a path only this user can reach (`mktemp -d`), never a predictable
name in a shared directory. The store splits each diff section into per-file
blocks and each block into `\n`-aligned chunks of at most `--chunk-bytes`
bytes, and adds a `## chunks` inventory: one line per chunk, `<section>
<path>#<k>/<n> lines=<a>-<b> bytes=<len> consumed|missing`, plus one
`<section> coverage: complete|incomplete` line per section. A chunk is
`consumed` once a bounded call has printed it; nothing else marks it. The build
call charges its unbounded sections -- the manifest, ranges, history, the
inventory itself, and on a re-review build `delta-conditions`,
`delta-manifest`, and `delta-overlap` too -- against the bound before any diff,
so a diff is printed and consumed only when the whole call's output stayed
inside it; otherwise the section reads `withheld: ...` and the diff is read
from the store. A single line longer than the bound is its own chunk, marked
`oversized`.

`--from FILE` reads the store instead of git and never regenerates the diff.
Alone it prints the manifest, ranges, history, the small delta sections, and
the complete `## chunks` inventory. With `--path P` (repeatable) it prints the
selected blocks of `--section` (`diff` by default, or `delta-diff`) when they
fit the bound, or withholds them and lists their chunks; with exactly one
`--path` and `--chunk K` it prints chunk K of that path. Every bounded print
marks its chunks consumed in the store, so the inventory is an exhaustive
account: concatenating the chunks of a section in inventory order reproduces
the persisted diff byte for byte, and a `missing` chunk is diff text no bounded
call has printed. Continue at the missing chunk.

Exit codes:
    0  the context was written to stdout
    1  a --self-test assertion failed; unused in normal operation
    2  a git command failed, or the arguments are unusable (an unknown --path,
       an out-of-range --chunk, an unreadable store); the failing command or
       argument is named on stderr
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any, Optional

HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")
NOTE_LINE = re.compile(r"^note: no function context for (.*); read enclosing ranges by hand$")
STORE_FORMAT = "review-context-store/1"
DEFAULT_CHUNK_BYTES = 24000
SECTIONS = ("diff", "delta-diff")


class GitError(Exception):
    """A git subprocess failed, or could not be started."""

    def __init__(self, command: str, detail: str) -> None:
        super().__init__(f"{command}: {detail}")
        self.command = command
        self.detail = detail


class InputError(Exception):
    """An argument or store the script cannot use; reported on stderr, exit 2."""


def start_git(
    arguments: list[str], cwd: Optional[str] = None
) -> tuple[str, subprocess.CompletedProcess[str]]:
    """Run git and return the printable command with its completed process."""
    command = [
        "git",
        "-c",
        "core.quotepath=false",
        "-c",
        "diff.noprefix=false",
        "-c",
        "diff.mnemonicPrefix=false",
        "-c",
        "diff.srcPrefix=a/",
        "-c",
        "diff.dstPrefix=b/",
        *arguments,
    ]
    printable = " ".join(command)
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as error:
        raise GitError(printable, str(error)) from error
    return printable, completed


def run_git(arguments: list[str], cwd: Optional[str] = None) -> str:
    printable, completed = start_git(arguments, cwd)
    if completed.returncode != 0:
        raise GitError(printable, completed.stderr.strip() or "exited non-zero")
    return completed.stdout


def git_answers(arguments: list[str], cwd: Optional[str] = None) -> bool:
    """Run a git predicate: True on exit 0, False on exit 1, GitError otherwise."""
    printable, completed = start_git(arguments, cwd)
    if completed.returncode in (0, 1):
        return completed.returncode == 0
    raise GitError(
        printable, completed.stderr.strip() or f"exited {completed.returncode}"
    )


def literal_pathspec(path: str) -> str:
    """Wrap a repo-relative path so git treats it literally, from the top level."""
    return f":(top,literal){path}"


def parse_name_status(output: str) -> list[tuple[str, Optional[str], str]]:
    """Split `git diff --name-status -M -z` into (status, old path, path)."""
    fields = output.split("\0")
    entries: list[tuple[str, Optional[str], str]] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        if not status:
            continue
        if status[0] in ("R", "C") and index + 1 < len(fields):
            entries.append((status[0], fields[index], fields[index + 1]))
            index += 2
        elif index < len(fields):
            entries.append((status[0], None, fields[index]))
            index += 1
    return entries


def parse_numstat(output: str) -> dict[str, tuple[str, str]]:
    """Map each path at head to its (insertions, deletions) from `--numstat -z`."""
    fields = output.split("\0")
    stats: dict[str, tuple[str, str]] = {}
    index = 0
    while index < len(fields):
        record = fields[index]
        index += 1
        if not record:
            continue
        parts = record.split("\t")
        if len(parts) < 3:
            continue
        insertions, deletions, path = parts[0], parts[1], parts[2]
        if path == "" and index + 1 < len(fields):
            path = fields[index + 1]
            index += 2
        stats[path] = (insertions, deletions)
    return stats


def count_lines_at_head(head: str, path: str, cwd: Optional[str]) -> int:
    """Count the lines of `path` at `head`, as `git show <head>:<path> | wc -l`."""
    return run_git(["show", f"{head}:{path}"], cwd).count("\n")


def build_manifest(merge_base: str, head: str, cwd: Optional[str]) -> list[dict[str, Any]]:
    revisions = f"{merge_base}...{head}"
    name_status = parse_name_status(
        run_git(["diff", "--name-status", "-M", "-z", revisions], cwd)
    )
    numstat = parse_numstat(run_git(["diff", "--numstat", "-M", "-z", revisions], cwd))
    manifest: list[dict[str, Any]] = []
    for status, old_path, path in name_status:
        insertions, deletions = numstat.get(path, ("0", "0"))
        manifest.append(
            {
                "status": status,
                "path": path,
                "old_path": old_path,
                "insertions": insertions,
                "deletions": deletions,
                "new": status == "A",
                "lines": 0 if status == "D" else count_lines_at_head(head, path, cwd),
            }
        )
    return manifest


def strip_prefix(field: str) -> Optional[str]:
    """Turn a `--- a/path` or `+++ b/path` field into a path, or None for /dev/null."""
    field = field.split("\t")[0]
    if field == "/dev/null":
        return None
    if len(field) > 1 and field[1] == "/":
        return field[2:]
    return field


def parse_diff(diff_text: str) -> list[dict[str, Any]]:
    """Collect each file's paths and hunk headers from a unified diff."""
    files: list[dict[str, Any]] = []
    current: Optional[dict[str, Any]] = None
    in_header = False
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            current = {"old_path": None, "new_path": None, "hunks": []}
            files.append(current)
            in_header = True
            continue
        if current is None:
            continue
        if in_header and line.startswith("--- "):
            current["old_path"] = strip_prefix(line[4:])
            continue
        if in_header and line.startswith("+++ "):
            current["new_path"] = strip_prefix(line[4:])
            continue
        match = HUNK_HEADER.match(line)
        if match:
            in_header = False
            base_start = int(match.group(1))
            base_count = 1 if match.group(2) is None else int(match.group(2))
            head_start = int(match.group(3))
            head_count = 1 if match.group(4) is None else int(match.group(4))
            current["hunks"].append(
                {
                    "base_start": base_start,
                    "base_count": base_count,
                    "head_start": head_start,
                    "head_count": head_count,
                    "section": match.group(5).strip(),
                }
            )
    return files


def build_ranges(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranges: list[dict[str, Any]] = []
    for entry in files:
        head_path = entry["new_path"] or entry["old_path"]
        base_path = entry["old_path"] or entry["new_path"]
        for hunk in entry["hunks"]:
            if hunk["head_count"] > 0 and head_path:
                ranges.append(
                    {
                        "path": head_path,
                        "start": hunk["head_start"],
                        "end": hunk["head_start"] + hunk["head_count"] - 1,
                        "side": "head",
                    }
                )
            if hunk["base_count"] > 0 and base_path:
                ranges.append(
                    {
                        "path": base_path,
                        "start": hunk["base_start"],
                        "end": hunk["base_start"] + hunk["base_count"] - 1,
                        "side": "merge-base",
                    }
                )
    return ranges


def build_notes(files: list[dict[str, Any]]) -> list[str]:
    """Name each path whose every hunk header carries no enclosing context.

    A path the diff adds or deletes in full is skipped: its only hunk header is
    empty by construction, and the diff already holds every line of it, so
    there is no enclosing range left to read.
    """
    notes: list[str] = []
    for entry in files:
        if not entry["hunks"]:
            continue
        if entry["old_path"] is None or entry["new_path"] is None:
            continue
        if any(hunk["section"] for hunk in entry["hunks"]):
            continue
        path = entry["new_path"] or entry["old_path"]
        notes.append(
            f"note: no function context for {path}; read enclosing ranges by hand"
        )
    return notes


def notes_for(notes: list[str], paths: set[str]) -> list[str]:
    """Keep the notes that name one of `paths`."""
    kept: list[str] = []
    for note in notes:
        match = NOTE_LINE.match(note)
        if match and match.group(1) in paths:
            kept.append(note)
    return kept


def build_history(
    merge_base: str, manifest: list[dict[str, Any]], cwd: Optional[str]
) -> list[dict[str, Any]]:
    """List up to three commits before the merge-base for each changed path."""
    history: list[dict[str, Any]] = []
    for entry in manifest:
        path = entry["old_path"] or entry["path"]
        output = run_git(
            [
                "log",
                "-3",
                "--format=%h %ad %s",
                "--date=short",
                merge_base,
                "--",
                literal_pathspec(path),
            ],
            cwd,
        )
        history.append(
            {"path": path, "commits": [line for line in output.splitlines() if line]}
        )
    return history


def build_conditions(
    head: str,
    prior_head: str,
    base_ref: Optional[str],
    cwd: Optional[str],
) -> dict[str, str]:
    """Report the three delta conditions without deciding on them."""
    _, probe = start_git(["cat-file", "-e", f"{prior_head}^{{commit}}"], cwd)
    reachable = probe.returncode == 0
    ancestor = reachable and git_answers(
        ["merge-base", "--is-ancestor", prior_head, head], cwd
    )
    if base_ref is None:
        merge_base_unchanged = "unknown (no --base-ref)"
    elif not reachable:
        merge_base_unchanged = "no"
    else:
        pinned = run_git(["merge-base", base_ref, prior_head], cwd).strip()
        current = run_git(["merge-base", base_ref, head], cwd).strip()
        merge_base_unchanged = "yes" if pinned == current else "no"
    return {
        "ancestor": "yes" if ancestor else "no",
        "merge-base-unchanged": merge_base_unchanged,
        "prior-head-reachable": "yes" if reachable else "no",
    }


def build_overlap(
    delta_files: list[dict[str, Any]], full_ranges: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Pair each delta hunk's head range with the full-diff head ranges it touches.

    A hunk with no head-side lines (a whole-file deletion) is reported as the
    single line its header names, so every delta hunk yields exactly one entry.
    """
    head_ranges = [item for item in full_ranges if item["side"] == "head"]
    overlap: list[dict[str, Any]] = []
    for entry in delta_files:
        path = entry["new_path"] or entry["old_path"]
        if not path:
            continue
        for hunk in entry["hunks"]:
            start = hunk["head_start"]
            end = start + max(hunk["head_count"], 1) - 1
            matches = [
                {"path": item["path"], "start": item["start"], "end": item["end"]}
                for item in head_ranges
                if item["path"] == path and item["start"] <= end and start <= item["end"]
            ]
            overlap.append({"path": path, "start": start, "end": end, "overlaps": matches})
    return overlap


def build_delta(
    head: str,
    prior_head: str,
    base_ref: Optional[str],
    full_ranges: list[dict[str, Any]],
    cwd: Optional[str],
) -> dict[str, Any]:
    conditions = build_conditions(head, prior_head, base_ref, cwd)
    delta: dict[str, Any] = {
        "prior_head": prior_head,
        "base_ref": base_ref,
        "conditions": conditions,
        "manifest": [],
        "diff": "",
        "notes": [],
        "overlap": [],
    }
    if conditions["prior-head-reachable"] != "yes":
        return delta
    diff_text = run_git(
        ["diff", "-M", f"{prior_head}...{head}", "--function-context"], cwd
    )
    files = parse_diff(diff_text)
    delta["manifest"] = build_manifest(prior_head, head, cwd)
    delta["diff"] = diff_text
    delta["notes"] = build_notes(files)
    delta["overlap"] = build_overlap(files, full_ranges)
    return delta


# --- Per-file blocks and bounded chunks -------------------------------------


def unquote_git_path(token: str) -> str:
    """Decode the C-style quoting git applies to paths with `"`, `\\`, or controls."""
    if not (len(token) >= 2 and token.startswith('"') and token.endswith('"')):
        return token
    body = token[1:-1]
    simple = {
        "n": b"\n", "t": b"\t", "r": b"\r", "\\": b"\\", '"': b'"',
        "a": b"\a", "b": b"\b", "f": b"\f", "v": b"\v",
    }
    result = bytearray()
    index = 0
    while index < len(body):
        char = body[index]
        if char != "\\":
            result += char.encode("utf-8")
            index += 1
            continue
        index += 1
        if index >= len(body):
            result += b"\\"
            break
        escape = body[index]
        octal = re.match(r"[0-7]{1,3}", body[index:index + 3])
        if escape in simple:
            result += simple[escape]
            index += 1
        elif octal:
            result.append(int(octal.group(0), 8) & 0xFF)
            index += len(octal.group(0))
        else:
            result += escape.encode("utf-8")
            index += 1
    return result.decode("utf-8", errors="replace")


def strip_side(token: str) -> str:
    """Drop the one-character `a/` or `b/` prefix git puts on a header path."""
    if len(token) > 1 and token[1] == "/":
        return token[2:]
    return token


def split_diff_git_line(line: str) -> tuple[Optional[str], Optional[str]]:
    """Recover (old path, new path) from a `diff --git a/X b/Y` line.

    Unquoted paths may contain spaces, so the line is solved symmetrically:
    when both halves name the same path (every non-rename block), the split
    point is fixed by the line's length. Quoted paths are tokenized. A rename
    with unquoted, unequal paths is left to the `rename from`/`rename to` lines.
    """
    rest = line[len("diff --git "):]
    if rest.startswith('"'):
        tokens: list[str] = []
        index = 0
        while index < len(rest):
            if rest[index] == '"':
                end = index + 1
                while end < len(rest) and rest[end] != '"':
                    end += 2 if rest[end] == "\\" else 1
                tokens.append(unquote_git_path(rest[index:end + 1]))
                index = end + 2
            else:
                end = rest.find(" ", index)
                end = len(rest) if end < 0 else end
                tokens.append(rest[index:end])
                index = end + 1
        if len(tokens) == 2:
            return strip_side(tokens[0]), strip_side(tokens[1])
        return None, None
    if len(rest) >= 5 and (len(rest) - 5) % 2 == 0:
        half = (len(rest) - 5) // 2
        left, separator, right = rest[: 2 + half], rest[2 + half], rest[3 + half:]
        if separator == " " and left[1:2] == "/" and right[1:2] == "/" and left[2:] == right[2:]:
            return left[2:], right[2:]
    return None, None


def identify_block(text: str) -> tuple[Optional[str], Optional[str]]:
    """Name a block's (old path, new path) from its extended header."""
    lines = text.split("\n")
    old_path, new_path = split_diff_git_line(lines[0])
    rename_from: Optional[str] = None
    rename_to: Optional[str] = None
    for line in lines[1:]:
        if line.startswith(("--- ", "+++ ", "@@ ", "Binary files ", "GIT binary patch")):
            break
        for prefix in ("rename from ", "copy from "):
            if line.startswith(prefix):
                rename_from = unquote_git_path(line[len(prefix):])
        for prefix in ("rename to ", "copy to "):
            if line.startswith(prefix):
                rename_to = unquote_git_path(line[len(prefix):])
    if rename_from is not None and rename_to is not None:
        return rename_from, rename_to
    return old_path, new_path


def split_blocks(diff_text: str) -> list[dict[str, Any]]:
    """Split a diff into per-file blocks whose texts concatenate back to it.

    Each block carries its head path (`path`), the old path of a rename, its
    verbatim text, and its byte offset and length in the UTF-8 encoding of the
    whole diff. Text before the first `diff --git` line (git emits none) is
    kept as a `(preamble)` block so no byte is lost.
    """
    if not diff_text:
        return []
    starts = [match.start() for match in re.finditer(r"^diff --git ", diff_text, re.MULTILINE)]
    if not starts or starts[0] != 0:
        starts.insert(0, 0)
    blocks: list[dict[str, Any]] = []
    offset = 0
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(diff_text)
        text = diff_text[start:end]
        if text.startswith("diff --git "):
            old_path, new_path = identify_block(text)
            path = new_path or old_path or text.split("\n", 1)[0][len("diff --git "):]
            rename = old_path if (old_path and new_path and old_path != new_path) else None
        else:
            path, rename = "(preamble)", None
        length = len(text.encode("utf-8"))
        blocks.append(
            {"path": path, "old_path": rename, "text": text, "offset": offset, "bytes": length}
        )
        offset += length
    return blocks


def chunk_lines(text: str, chunk_bytes: int) -> list[tuple[int, int, int, bool]]:
    """Cut text into line-aligned chunks: (start line, end line, bytes, oversized).

    A line longer than the bound stands alone, flagged oversized; every other
    chunk holds as many whole lines as fit the bound. Line numbers are 1-based
    within the text. Lines are `\n`-terminated, the splitting `split_blocks` and
    `identify_block` use: a form feed or a Unicode line break inside a diff line
    is text, not a boundary.
    """
    lines = re.findall(r"[^\n]*\n|[^\n]+$", text)
    chunks: list[tuple[int, int, int, bool]] = []
    start, size, count = 1, 0, 0
    for number, line in enumerate(lines, 1):
        length = len(line.encode("utf-8"))
        if length > chunk_bytes:
            if count:
                chunks.append((start, number - 1, size, False))
            chunks.append((number, number, length, True))
            start, size, count = number + 1, 0, 0
            continue
        if count and size + length > chunk_bytes:
            chunks.append((start, number - 1, size, False))
            start, size, count = number, 0, 0
        size += length
        count += 1
    if count:
        chunks.append((start, len(lines), size, False))
    return chunks


def build_chunks(section: str, diff_text: str, chunk_bytes: int) -> list[dict[str, Any]]:
    """Inventory one diff section: every block cut into bounded chunks."""
    records: list[dict[str, Any]] = []
    for block in split_blocks(diff_text):
        pieces = chunk_lines(block["text"], chunk_bytes)
        cursor = block["offset"]
        for index, (start_line, end_line, size, oversized) in enumerate(pieces, 1):
            records.append(
                {
                    "section": section,
                    "path": block["path"],
                    "old_path": block["old_path"],
                    "index": index,
                    "count": len(pieces),
                    "start_line": start_line,
                    "end_line": end_line,
                    "offset": cursor,
                    "bytes": size,
                    "oversized": oversized,
                    "consumed": False,
                }
            )
            cursor += size
    return records


def section_text(context: dict[str, Any], section: str) -> str:
    if section == "diff":
        return context["diff"]
    delta = context.get("delta")
    return "" if delta is None else delta["diff"]


def section_manifest(context: dict[str, Any], section: str) -> list[dict[str, Any]]:
    if section == "diff":
        return context["manifest"]
    delta = context.get("delta")
    return [] if delta is None else delta["manifest"]


def chunk_text(section_bytes: bytes, chunk: dict[str, Any]) -> str:
    return section_bytes[chunk["offset"]: chunk["offset"] + chunk["bytes"]].decode("utf-8")


def resolve_selection(
    selections: list[str],
    manifest: list[dict[str, Any]],
    block_paths: list[str],
    section: str,
    revisions: str,
) -> list[str]:
    """Map literal `--path` values to block paths, in block order, or raise.

    A value must equal a manifest path or a rename's old path byte for byte;
    nothing is globbed, and nothing is treated as an option.
    """
    by_path = {entry["path"]: entry["path"] for entry in manifest}
    by_old = {entry["old_path"]: entry["path"] for entry in manifest if entry["old_path"]}
    known = set(block_paths)
    chosen: list[str] = []
    for value in selections:
        target = by_path.get(value) or by_old.get(value)
        if target is None and value in known:
            target = value
        if target is None:
            raise InputError(
                f"unknown path `{value}`: not a path or old path in the {section} "
                f"manifest for {revisions}; selections are literal, not patterns"
            )
        if target not in chosen:
            chosen.append(target)
    order = {path: position for position, path in enumerate(block_paths)}
    return sorted(chosen, key=lambda path: order.get(path, len(order)))


# --- Rendering ---------------------------------------------------------------


def fence_for(text: str) -> str:
    """Return a backtick fence longer than any backtick run the text contains."""
    longest = 0
    run = 0
    for character in text:
        if character == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return "`" * max(3, longest + 1)


def render_manifest_line(entry: dict[str, Any]) -> str:
    rename = f" <- {entry['old_path']}" if entry["old_path"] else ""
    return (
        f"{entry['status']} {entry['path']}{rename} "
        f"+{entry['insertions']} -{entry['deletions']} "
        f"new={'yes' if entry['new'] else 'no'} lines={entry['lines']}"
    )


def render_diff_section(name: str, diff_text: str, notes: list[str]) -> str:
    diff_fence = fence_for(diff_text)
    section = f"## {name}\n\n{diff_fence}diff\n{diff_text.rstrip(chr(10))}\n{diff_fence}"
    if notes:
        section += "\n\n" + "\n".join(notes)
    return section


def render_verbatim_diff_section(name: str, diff_text: str, notes: list[str]) -> str:
    """Fence diff text without trimming it, so chunks concatenate exactly."""
    diff_fence = fence_for(diff_text)
    terminator = "" if diff_text.endswith("\n") or not diff_text else "\n"
    section = f"## {name}\n\n{diff_fence}diff\n{diff_text}{terminator}{diff_fence}"
    trailer = list(notes)
    if terminator:
        trailer.append("note: the text above has no trailing newline; one was added before the fence")
    if trailer:
        section += "\n\n" + "\n".join(trailer)
    return section


def render_overlap_lines(overlap: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for item in overlap:
        prefix = f"{item['path']}:{item['start']}-{item['end']} overlaps "
        if not item["overlaps"]:
            lines.append(prefix + "none")
        for match in item["overlaps"]:
            lines.append(prefix + f"{match['path']}:{match['start']}-{match['end']}")
    return lines


def render_delta(delta: dict[str, Any]) -> list[str]:
    conditions_body = "\n".join(
        f"{name}: {value}" for name, value in delta["conditions"].items()
    )
    manifest_body = "\n".join(render_manifest_line(entry) for entry in delta["manifest"])
    overlap_body = "\n".join(render_overlap_lines(delta["overlap"]))
    return [
        f"## delta-conditions\n\n```\n{conditions_body}\n```",
        f"## delta-manifest\n\n```\n{manifest_body}\n```",
        render_diff_section("delta-diff", delta["diff"], delta["notes"]),
        f"## delta-overlap\n\n```\n{overlap_body}\n```",
    ]


def render_markdown(context: dict[str, Any]) -> str:
    manifest_body = "\n".join(
        render_manifest_line(entry) for entry in context["manifest"]
    )
    range_body = "\n".join(
        f"{item['path']}:{item['start']}-{item['end']} @{item['side']}"
        for item in context["ranges"]
    )
    history_body = "\n".join(
        f"{entry['path']}: {commit}"
        for entry in context["history"]
        for commit in entry["commits"]
    )
    sections = [
        f"## manifest\n\n```\n{manifest_body}\n```",
        render_diff_section("diff", context["diff"], context["notes"]),
        f"## ranges\n\n```\n{range_body}\n```",
        f"## history\n\n```\n{history_body}\n```",
    ]
    if context.get("delta") is not None:
        sections.extend(render_delta(context["delta"]))
    return "\n\n".join(sections) + "\n"


def fenced(name: str, lines: list[str]) -> str:
    return f"## {name}\n\n```\n" + "\n".join(lines) + "\n```"


def chunk_label(chunk: dict[str, Any]) -> str:
    return f"{chunk['path']}#{chunk['index']}/{chunk['count']}"


def render_chunk_line(chunk: dict[str, Any]) -> str:
    status = "consumed" if chunk["consumed"] else "missing"
    if chunk["oversized"]:
        status += " oversized"
    return (
        f"{chunk['section']} {chunk_label(chunk)} "
        f"lines={chunk['start_line']}-{chunk['end_line']} bytes={chunk['bytes']} {status}"
    )


def coverage_line(section: str, chunks: list[dict[str, Any]], list_missing: bool) -> str:
    """Sum a section's chunk states; name the missing ones only when they are not listed above."""
    total = len(chunks)
    consumed = sum(1 for chunk in chunks if chunk["consumed"])
    state = "complete" if consumed == total else "incomplete"
    line = f"{section} coverage: {state} ({consumed}/{total} chunks consumed)"
    if consumed != total and list_missing:
        missing = [chunk_label(chunk) for chunk in chunks if not chunk["consumed"]]
        shown = " ".join(missing[:20])
        more = f" and {len(missing) - 20} more" if len(missing) > 20 else ""
        line += f"; missing: {shown}{more}"
    return line


def chunks_section(
    chunks: list[dict[str, Any]], sections: tuple[str, ...], paths: Optional[list[str]]
) -> dict[str, Any]:
    """The `## chunks` inventory, restricted to `paths` when given."""
    lines: list[str] = []
    shown: list[dict[str, Any]] = []
    coverage: dict[str, str] = {}
    for section in sections:
        section_chunks = [chunk for chunk in chunks if chunk["section"] == section]
        for chunk in section_chunks:
            if paths is None or chunk["path"] in paths:
                lines.append(render_chunk_line(chunk))
                shown.append(chunk)
        summary = coverage_line(section, section_chunks, list_missing=paths is not None)
        lines.append(summary)
        coverage[section] = summary
    return {
        "name": "chunks",
        "json": {"chunks": shown, "coverage": coverage},
        "markdown": fenced("chunks", lines),
    }


def selection_section(manifest: list[dict[str, Any]], paths: list[str], total: int) -> dict[str, Any]:
    entries = [entry for entry in manifest if entry["path"] in paths]
    lines = [render_manifest_line(entry) for entry in entries]
    listed = {entry["path"] for entry in entries}
    lines.extend(f"? {path} (no manifest entry)" for path in paths if path not in listed)
    lines.append(f"unselected: {total - len(entries)} of {total} manifest paths")
    return {"name": "selection", "json": entries, "markdown": fenced("selection", lines)}


def withheld_section(name: str, message: str) -> dict[str, Any]:
    return {"name": name, "json": {"withheld": message}, "markdown": f"## {name}\n\n{message}"}


def diff_section(name: str, text: str, notes: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "json": {"text": text, "notes": notes},
        "markdown": render_verbatim_diff_section(name, text, notes),
    }


def render_view(sections: list[dict[str, Any]], as_json: bool) -> str:
    if as_json:
        return json.dumps(
            {section["name"]: section["json"] for section in sections},
            ensure_ascii=False,
            indent=2,
        ) + "\n"
    return "\n\n".join(section["markdown"] for section in sections) + "\n"


# --- Context and store -------------------------------------------------------


def build_context(
    merge_base: str,
    head: str,
    cwd: Optional[str] = None,
    prior_head: Optional[str] = None,
    base_ref: Optional[str] = None,
) -> dict[str, Any]:
    manifest = build_manifest(merge_base, head, cwd)
    diff_text = run_git(["diff", "-M", f"{merge_base}...{head}", "--function-context"], cwd)
    files = parse_diff(diff_text)
    ranges = build_ranges(files)
    context: dict[str, Any] = {
        "merge_base": merge_base,
        "head": head,
        "manifest": manifest,
        "diff": diff_text,
        "notes": build_notes(files),
        "ranges": ranges,
        "history": build_history(merge_base, manifest, cwd),
    }
    if prior_head is not None:
        context["delta"] = build_delta(head, prior_head, base_ref, ranges, cwd)
    return context


def context_sections(context: dict[str, Any]) -> tuple[str, ...]:
    return SECTIONS if context.get("delta") is not None else SECTIONS[:1]


def make_store(context: dict[str, Any], chunk_bytes: int) -> dict[str, Any]:
    chunks: list[dict[str, Any]] = []
    for section in context_sections(context):
        chunks.extend(build_chunks(section, section_text(context, section), chunk_bytes))
    return {
        "format": STORE_FORMAT,
        "chunk_bytes": chunk_bytes,
        "context": context,
        "chunks": chunks,
    }


def write_store(path: str, store: dict[str, Any]) -> None:
    """Write the store privately: created 0600, and vetted before any byte lands.

    The store holds the pull request's complete diff, so a path another local
    user can pre-create must never receive it. The open refuses a symlink
    (`O_NOFOLLOW`), and the descriptor is checked to be an unshared regular file
    this user owns and chmodded 0600 before the file is truncated and written.
    """
    flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    descriptor = -1
    try:
        descriptor = os.open(path, flags, 0o600)
        info = os.fstat(descriptor)
        owner = getattr(os, "geteuid", None)
        if not stat.S_ISREG(info.st_mode):
            raise InputError(f"cannot write store {path}: not a regular file")
        if owner is not None and info.st_uid != owner():
            raise InputError(
                f"cannot write store {path}: owned by uid {info.st_uid}, not this user"
            )
        if info.st_nlink > 1:
            raise InputError(f"cannot write store {path}: {info.st_nlink} hard links to it")
        os.fchmod(descriptor, stat.S_IRUSR | stat.S_IWUSR)
        os.ftruncate(descriptor, 0)
        handle = os.fdopen(descriptor, "w", encoding="utf-8")
        descriptor = -1
        with handle:
            json.dump(store, handle, ensure_ascii=False)
            handle.write("\n")
    except OSError as error:
        raise InputError(f"cannot write store {path}: {error}") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def load_store(path: str) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as handle:
            store = json.load(handle)
    except (OSError, ValueError) as error:
        raise InputError(f"cannot read store {path}: {error}") from error
    if not isinstance(store, dict) or store.get("format") != STORE_FORMAT:
        raise InputError(f"store {path} is not a {STORE_FORMAT} file")
    return store


def revisions_of(context: dict[str, Any], section: str) -> str:
    """Name the revision range a section's manifest and diff describe."""
    if section == "diff":
        return f"{context['merge_base']}...{context['head']}"
    return f"{context['delta']['prior_head']}...{context['head']}"


def emit_bounded(
    store: dict[str, Any],
    section: str,
    chunks: list[dict[str, Any]],
    budget: int,
    store_path: str,
    hint: str,
) -> tuple[dict[str, Any], int]:
    """Print `chunks` of `section` if they fit `budget`, marking them consumed.

    Returns the rendered section and the budget left. When they do not fit,
    the section is withheld and nothing is marked.
    """
    context = store["context"]
    size = sum(chunk["bytes"] for chunk in chunks)
    if size > budget:
        message = (
            f"withheld: {size} bytes of {section} across {len(chunks)} chunks exceed the "
            f"{budget}-byte bound left in this call (--chunk-bytes {store['chunk_bytes']}); "
            f"nothing was marked consumed. Read bounded chunks from the store: "
            f"python3 scripts/review_context.py --from {store_path}{hint} --path <path> --chunk <k>; "
            f"`## chunks` lists every chunk"
        )
        return withheld_section(section, message), budget
    section_bytes = section_text(context, section).encode("utf-8")
    text = "".join(chunk_text(section_bytes, chunk) for chunk in chunks)
    for chunk in chunks:
        chunk["consumed"] = True
    paths = {chunk["path"] for chunk in chunks}
    if section == "diff":
        notes = notes_for(context["notes"], paths)
    else:
        notes = notes_for(context["delta"]["notes"], paths)
    return diff_section(section, text, notes), budget - size


def small_sections(context: dict[str, Any]) -> list[dict[str, Any]]:
    """Every section except the diffs, as view sections."""
    sections = [
        {
            "name": "manifest",
            "json": context["manifest"],
            "markdown": fenced("manifest", [render_manifest_line(e) for e in context["manifest"]]),
        },
        {
            "name": "ranges",
            "json": context["ranges"],
            "markdown": fenced(
                "ranges",
                [f"{i['path']}:{i['start']}-{i['end']} @{i['side']}" for i in context["ranges"]],
            ),
        },
        {
            "name": "history",
            "json": context["history"],
            "markdown": fenced(
                "history",
                [f"{e['path']}: {c}" for e in context["history"] for c in e["commits"]],
            ),
        },
    ]
    delta = context.get("delta")
    if delta is not None:
        sections.extend(
            [
                {
                    "name": "delta-conditions",
                    "json": delta["conditions"],
                    "markdown": fenced(
                        "delta-conditions", [f"{n}: {v}" for n, v in delta["conditions"].items()]
                    ),
                },
                {
                    "name": "delta-manifest",
                    "json": delta["manifest"],
                    "markdown": fenced(
                        "delta-manifest", [render_manifest_line(e) for e in delta["manifest"]]
                    ),
                },
                {
                    "name": "delta-overlap",
                    "json": delta["overlap"],
                    "markdown": fenced("delta-overlap", render_overlap_lines(delta["overlap"])),
                },
            ]
        )
    return sections


def other_output_bytes(
    sections: list[dict[str, Any]], as_json: bool, chunk_count: int
) -> int:
    """Bytes a bounded build call prints besides its diffs, charged against the bound.

    The inventory is rendered here before the call consumes anything, so allow a
    byte per chunk: `consumed` is one character longer than `missing`, while the
    coverage lines only ever shrink as a section completes.
    """
    return len(render_view(sections, as_json).encode("utf-8")) + chunk_count


def live_view(
    context: dict[str, Any],
    selections: list[str],
    store: Optional[dict[str, Any]],
    store_path: Optional[str],
    as_json: bool = False,
) -> list[dict[str, Any]]:
    """Render a fresh build with selection and, when stored, the output bound."""
    small = {section["name"]: section for section in small_sections(context)}
    chunks = store["chunks"] if store is not None else []
    sections: list[dict[str, Any]] = [small["manifest"]]
    diffs: dict[str, dict[str, Any]] = {}
    chosen_blocks: dict[str, list[dict[str, Any]]] = {}
    selected_paths: Optional[list[str]] = None
    for section in context_sections(context):
        text = section_text(context, section)
        blocks = split_blocks(text)
        block_paths = [block["path"] for block in blocks]
        manifest = section_manifest(context, section)
        if selections:
            paths = resolve_selection(
                selections, manifest, block_paths, section, revisions_of(context, section)
            )
            if section == "diff":
                selected_paths = paths
                sections.append(selection_section(manifest, paths, len(manifest)))
            chosen_blocks[section] = [block for block in blocks if block["path"] in paths]
        else:
            chosen_blocks[section] = blocks
    if store is None:
        for section, chosen in chosen_blocks.items():
            notes_source = context["notes"] if section == "diff" else context["delta"]["notes"]
            joined = "".join(block["text"] for block in chosen)
            notes = notes_for(notes_source, {block["path"] for block in chosen})
            diffs[section] = diff_section(section, joined, notes)
    else:
        assert store_path is not None
        # Charge the unbounded sections first: a diff printed under a bound the
        # whole output then blows past would be marked consumed after the
        # harness truncated it, which is the state the inventory exists to rule
        # out. What the rest of the call costs is what the diff cannot have.
        rest = [*sections, small["ranges"], small["history"]]
        if context.get("delta") is not None:
            rest += [small["delta-conditions"], small["delta-manifest"], small["delta-overlap"]]
        rest.append(chunks_section(chunks, context_sections(context), selected_paths))
        budget = max(0, store["chunk_bytes"] - other_output_bytes(rest, as_json, len(chunks)))
        for section, chosen in chosen_blocks.items():
            wanted = {block["path"] for block in chosen}
            section_chunks = [c for c in chunks if c["section"] == section and c["path"] in wanted]
            hint = "" if section == "diff" else f" --section {section}"
            diffs[section], budget = emit_bounded(
                store, section, section_chunks, budget, store_path, hint
            )
    sections.append(diffs["diff"])
    sections.append(small["ranges"])
    sections.append(small["history"])
    if context.get("delta") is not None:
        sections.append(small["delta-conditions"])
        sections.append(small["delta-manifest"])
        sections.append(diffs["delta-diff"])
        sections.append(small["delta-overlap"])
    if store is not None:
        sections.append(chunks_section(chunks, context_sections(context), selected_paths))
    return sections


def store_view(
    store: dict[str, Any],
    store_path: str,
    section: str,
    selections: list[str],
    chunk_index: Optional[int],
) -> list[dict[str, Any]]:
    """Render a bounded read from the store; marks what it prints consumed."""
    context = store["context"]
    if section not in context_sections(context):
        raise InputError(f"store {store_path} has no {section} section (built without --prior-head)")
    chunks = store["chunks"]
    if not selections:
        sections = small_sections(context)
        sections.append(chunks_section(chunks, context_sections(context), None))
        return sections
    text = section_text(context, section)
    block_paths = [block["path"] for block in split_blocks(text)]
    manifest = section_manifest(context, section)
    paths = resolve_selection(selections, manifest, block_paths, section, revisions_of(context, section))
    section_chunks = [c for c in chunks if c["section"] == section and c["path"] in paths]
    if chunk_index is not None:
        available = [c for c in section_chunks if c["index"] == chunk_index]
        if not available:
            count = section_chunks[0]["count"] if section_chunks else 0
            raise InputError(
                f"chunk {chunk_index} is out of range for {paths[0]} in {section}: "
                f"it has {count} chunk(s)"
            )
        section_chunks = available
    hint = "" if section == "diff" else f" --section {section}"
    budget = store["chunk_bytes"]
    if chunk_index is not None and section_chunks and section_chunks[0]["oversized"]:
        budget = max(budget, section_chunks[0]["bytes"])
    rendered, _ = emit_bounded(store, section, section_chunks, budget, store_path, hint)
    sections = [selection_section(manifest, paths, len(manifest)), rendered]
    sections.append(chunks_section(chunks, (section,), paths))
    return sections


def section_of(output: str, name: str) -> str:
    """Return one Markdown section's body, fences and all."""
    marker = f"## {name}\n"
    if not output.startswith(marker):
        start = output.find(f"\n{marker}")
        if start < 0:
            return ""
        start += 1
    else:
        start = 0
    start += len(marker)
    end = output.find("\n## ", start)
    return output[start:] if end < 0 else output[start:end]


def fenced_body(section: str) -> Optional[str]:
    """Return the text inside a section's first fence, trailing newline kept."""
    lines = section.split("\n")
    fence: Optional[str] = None
    inner: list[str] = []
    for line in lines:
        if fence is None:
            if line.startswith("```"):
                fence = line[: len(line) - len(line.lstrip("`"))]
            continue
        if line == fence:
            return "\n".join(inner) + "\n"
        inner.append(line)
    return None


# --- Self-test ---------------------------------------------------------------


def self_test() -> int:
    """Drive the command line against a scratch repository. Exit 1 on mismatch."""
    base_file = "def f():\n    x = 1\n    return x\n\n\ndef g():\n    y = 2\n    return y\n"
    head_file = "def f():\n    x = 1\n    return x\n\n\ndef g():\n    y = 3\n    return y\n"
    third_file = "def f():\n    x = 1\n    return x\n\n\ndef g():\n    y = 3\n    return y + 1\n"
    odd_name = "-dash file [1]*?.txt"
    big_lines = 400

    def big_text(fill: str) -> str:
        """The chunking fixture, with a form-feed page break inside one line."""
        lines = [f"line {n:04d} " + fill * 50 + "\n" for n in range(big_lines)]
        lines[100] = "line 0100 \x0c" + fill * 50 + "\n"
        return "".join(lines)

    failures: list[str] = []
    passed: list[str] = []

    with tempfile.TemporaryDirectory() as repository:
        environment = dict(os.environ)
        environment.update(
            {
                "HOME": repository,
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_AUTHOR_NAME": "Review Context",
                "GIT_AUTHOR_EMAIL": "review-context@example.invalid",
                "GIT_COMMITTER_NAME": "Review Context",
                "GIT_COMMITTER_EMAIL": "review-context@example.invalid",
            }
        )

        def git(*arguments: str) -> str:
            completed = subprocess.run(
                ["git", *arguments],
                cwd=repository,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if completed.returncode != 0:
                raise GitError(" ".join(["git", *arguments]), completed.stderr.strip())
            return completed.stdout

        def write(name: str, text: str) -> None:
            with open(os.path.join(repository, name), "w", encoding="utf-8") as handle:
                handle.write(text)

        try:
            git("init", "-q", "--template=")
            git("config", "diff.python.xfuncname", "^def ")
            git("config", "diff.renames", "false")
            # A hostile prefix config the script must pin away: every assertion
            # below reads `a/` and `b/` headers, so the whole run tests the pin.
            git("config", "diff.srcPrefix", "src/")
            git("config", "diff.dstPrefix", "dst/")
            write(".gitattributes", "*.py diff=python\n")
            write("a.py", base_file)
            write("old.txt", "alpha\nbeta\ngamma\n")
            write("c.txt", "1\n2\n3\n")
            write("gone.txt", "to be deleted\n")
            write(odd_name, "odd one\nodd two\n")
            write("big.txt", big_text("x"))
            git("add", ".")
            git("commit", "-q", "-m", "Add the base files")
            git("branch", "-M", "trunk")
            git("checkout", "-q", "-b", "topic")
            merge_base = git("rev-parse", "HEAD").strip()
            write("a.py", head_file)
            write("b.py", "def h():\n    return 0\n")
            write("new.txt", "alpha\nbeta\ndelta\n")
            os.remove(os.path.join(repository, "old.txt"))
            os.remove(os.path.join(repository, "gone.txt"))
            write("c.txt", "1\n2\n4\n")
            write(odd_name, "odd one\nodd two changed\n")
            write("big.txt", big_text("y"))
            write("long.txt", "z" * 5000 + "\n")
            git("add", "-A", ".")
            git("commit", "-q", "-m", "Change g, add b.py, rename old.txt, edit c.txt")
            head = git("rev-parse", "HEAD").strip()
        except GitError as error:
            print(f"self-test setup failed: {error}")
            return 1

        def invoke(*arguments: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, os.path.abspath(__file__), *arguments],
                cwd=repository,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        def run(
            *extra: str, pinned_merge_base: Optional[str] = None
        ) -> Optional[str]:
            """Run the script; return its stdout, or None after recording the failure."""
            completed = invoke("--merge-base", pinned_merge_base or merge_base, *extra)
            if completed.returncode != 0:
                failures.append(
                    f"expected exit 0 from {' '.join(extra)}, got "
                    f"{completed.returncode}: {completed.stderr.strip()}"
                )
                return None
            return completed.stdout

        def expect_exit(case: str, code: int, fragment: str, *arguments: str) -> None:
            completed = invoke(*arguments)
            if completed.returncode != code:
                failures.append(
                    f"{case}: expected exit {code} from {' '.join(arguments)}, got "
                    f"{completed.returncode}: {completed.stderr.strip()}"
                )
            elif fragment not in completed.stderr:
                failures.append(f"{case}: stderr lacks `{fragment}`: {completed.stderr.strip()}")

        def expect_conditions(case: str, output: str, expected: dict[str, str]) -> None:
            conditions = section_of(output, "delta-conditions")
            for name, value in expected.items():
                if f"{name}: {value}\n" not in conditions:
                    failures.append(f"{case}: delta-conditions lacks `{name}: {value}`")

        output = run("--head", head)
        if output is None:
            print(failures[0])
            return 1

        manifest = section_of(output, "manifest")
        diff = section_of(output, "diff")
        ranges = section_of(output, "ranges")
        history = section_of(output, "history")

        if not re.search(r"^M a\.py .*new=no ", manifest, re.MULTILINE):
            failures.append("manifest is missing an `M a.py ... new=no` line")
        if not re.search(r"^A b\.py .*new=yes ", manifest, re.MULTILINE):
            failures.append("manifest is missing an `A b.py ... new=yes` line")
        if not re.search(r"^D gone\.txt .*lines=0$", manifest, re.MULTILINE):
            failures.append("manifest is missing a `D gone.txt ... lines=0` line")

        a_py_diff = diff.split("diff --git a/b.py")[0]
        if "a/a.py" not in a_py_diff or "def g():" not in a_py_diff:
            failures.append("the diff section's hunk for a.py does not contain `def g():`")

        if not re.search(r"^R new\.txt <- old\.txt ", manifest, re.MULTILINE):
            failures.append("manifest is missing an `R new.txt <- old.txt` line")
        if "rename from old.txt" not in diff:
            failures.append("the diff section does not detect the old.txt -> new.txt rename")

        if "note: no function context for b.py" in diff:
            failures.append("the diff section notes the added file b.py")
        if "note: no function context for c.txt; read enclosing ranges by hand" not in diff:
            failures.append("the diff section is missing the note for c.txt")

        if not re.search(r"^a\.py:\d+-\d+ @head$", ranges, re.MULTILINE):
            failures.append("ranges is missing an `a.py:<start>-<end> @head` line")
        if not re.search(r"^a\.py:\d+-\d+ @merge-base$", ranges, re.MULTILINE):
            failures.append("ranges is missing an `a.py:<start>-<end> @merge-base` line")
        if "## delta-conditions" in output:
            failures.append("the delta sections appear without --prior-head")
        for name in ("selection", "chunks"):
            if f"## {name}" in output:
                failures.append(f"the no-option output carries a `## {name}` section")
        if not output.startswith("## manifest\n"):
            failures.append("the no-option output does not start with `## manifest`")
        if [m.group(0) for m in re.finditer(r"^## .*$", output, re.MULTILINE)] != [
            "## manifest", "## diff", "## ranges", "## history"
        ]:
            failures.append("the no-option output does not carry exactly the four sections in order")

        a_py_history = [line for line in history.splitlines() if line.startswith("a.py: ")]
        if len(a_py_history) != 1:
            failures.append(f"expected one history line for a.py, got {len(a_py_history)}")
        odd_history = [line for line in history.splitlines() if line.startswith(f"{odd_name}: ")]
        if len(odd_history) != 1:
            failures.append(
                f"expected one history line for `{odd_name}` (literal pathspec), got {len(odd_history)}"
            )

        # Selection: --path is literal, keeps the full manifest, and filters the diff.
        case = "path selection (literal paths, full manifest, filtered diff)"
        before = len(failures)
        output = run("--head", head, "--path", "a.py", f"--path={odd_name}", "--path", "old.txt")
        if output is not None:
            headings = [m.group(0) for m in re.finditer(r"^## .*$", output, re.MULTILINE)]
            if headings != ["## manifest", "## selection", "## diff", "## ranges", "## history"]:
                failures.append(f"{case}: unexpected sections {headings}")
            selected_manifest = section_of(output, "manifest")
            for path in ("b.py", "c.txt", "gone.txt", "big.txt"):
                if f" {path} " not in selected_manifest:
                    failures.append(f"{case}: full manifest no longer lists {path}")
            selection = section_of(output, "selection")
            for fragment in ("M a.py ", f"M {odd_name} ", "R new.txt <- old.txt ", "unselected: 5 of 8"):
                if fragment not in selection:
                    failures.append(f"{case}: selection lacks `{fragment}`")
            selected_diff = section_of(output, "diff")
            for fragment in ("diff --git a/a.py b/a.py", f"a/{odd_name} b/{odd_name}", "rename from old.txt"):
                if fragment not in selected_diff:
                    failures.append(f"{case}: selected diff lacks `{fragment}`")
            for fragment in ("b/b.py", "b/c.txt", "gone.txt", "big.txt"):
                if fragment in selected_diff:
                    failures.append(f"{case}: selected diff still contains `{fragment}`")
            if "note: no function context for c.txt" in selected_diff:
                failures.append(f"{case}: selected diff carries the note for unselected c.txt")
            if "b.py:" not in section_of(output, "ranges"):
                failures.append(f"{case}: ranges dropped unselected b.py")
        expect_exit(case, 2, "unknown path `*.py`", "--merge-base", merge_base, "--head", head, "--path", "*.py")
        expect_exit(case, 2, "unknown path `nope.txt`", "--merge-base", merge_base, "--head", head, "--path", "nope.txt")
        expect_exit(case, 2, "unknown path `-dash file [1]*?.tx`", "--merge-base", merge_base, "--head", head, "--path=-dash file [1]*?.tx")
        if len(failures) == before:
            passed.append(case)

        # The reviewer's diff.srcPrefix / diff.dstPrefix cannot rename the blocks.
        case = "prefix config pinned (diff.srcPrefix / diff.dstPrefix)"
        before = len(failures)
        output = run("--head", head, "--path", "a.py")
        if output is not None:
            selected_diff = section_of(output, "diff")
            if "diff --git a/a.py b/a.py" not in selected_diff:
                failures.append(f"{case}: the block header is not `a/a.py b/a.py`")
            if "src/a.py" in output or "dst/a.py" in output:
                failures.append(f"{case}: the reviewer's prefixes reached the output")
            if "def g():" not in selected_diff:
                failures.append(f"{case}: --path a.py printed no diff under the prefix config")
        if len(failures) == before:
            passed.append(case)

        # Chunking splits on `\n` alone; other Unicode line breaks are diff text.
        case = "chunks split on newline only (form feed, U+2028)"
        before = len(failures)
        if chunk_lines("a\x0cb\nc\n", 4000) != [(1, 2, 6, False)]:
            failures.append(f"{case}: a form feed inside a line was treated as a break")
        if chunk_lines("x\u2028y\n", 4000) != [(1, 1, 6, False)]:
            failures.append(f"{case}: U+2028 inside a line was treated as a break")
        if chunk_lines("a\nb", 4000) != [(1, 2, 3, False)]:
            failures.append(f"{case}: an unterminated last line is miscounted")
        if chunk_lines("", 4000) != []:
            failures.append(f"{case}: empty text produced chunks")
        if len(failures) == before:
            passed.append(case)

        # Store: complete context persisted privately; bounded output; exact chunk recovery.
        case = "store round trip (persisted diff, bounded reads, byte-exact recovery)"
        before = len(failures)
        store_directory = tempfile.mkdtemp()
        store_path = os.path.join(store_directory, "review-context.json")
        output = run("--head", head, "--store", store_path, "--chunk-bytes", "4000")
        persisted: dict[str, Any] = {}
        try:
            with open(store_path, encoding="utf-8") as handle:
                persisted = json.load(handle)
            mode = stat.S_IMODE(os.stat(store_path).st_mode)
            if mode != 0o600:
                failures.append(f"{case}: store mode is {oct(mode)}, not 0o600")
        except (OSError, ValueError) as error:
            failures.append(f"{case}: cannot read the store: {error}")
        if output is not None and persisted:
            if persisted.get("format") != STORE_FORMAT:
                failures.append(f"{case}: store format is {persisted.get('format')!r}")
            if "withheld:" not in section_of(output, "diff"):
                failures.append(f"{case}: a diff over the bound was not withheld")
            if " b.py " not in section_of(output, "manifest"):
                failures.append(f"{case}: the bounded output lacks the full manifest")
            inventory = section_of(output, "chunks")
            if "diff coverage: incomplete (0/" not in inventory:
                failures.append(f"{case}: fresh store is not reported as 0 chunks consumed")
            if not re.search(r"^diff big\.txt#1/\d+ lines=1-\d+ bytes=\d+ missing$", inventory, re.MULTILINE):
                failures.append(f"{case}: inventory lacks a missing big.txt#1 line")
            if not re.search(r"^diff long\.txt#\d/\d lines=\d+-\d+ bytes=5002 missing oversized$", inventory, re.MULTILINE):
                failures.append(f"{case}: inventory does not flag long.txt's 5002-byte line as oversized")
            full_diff = persisted["context"]["diff"]
            if full_diff.rstrip("\n") not in diff:
                failures.append(f"{case}: the persisted diff differs from the no-option diff")
            chunks = persisted["chunks"]
            if sum(c["bytes"] for c in chunks) != len(full_diff.encode("utf-8")):
                failures.append(f"{case}: chunk byte counts do not sum to the persisted diff size")
            if any(c["bytes"] > 4000 and not c["oversized"] for c in chunks):
                failures.append(f"{case}: a non-oversized chunk exceeds the bound")
            # big.txt carries a form feed inside a line: labels count `\n` lines,
            # and no chunk boundary falls inside one.
            big_block = next((b for b in split_blocks(full_diff) if b["path"] == "big.txt"), None)
            big_chunks = [c for c in chunks if c["section"] == "diff" and c["path"] == "big.txt"]
            if big_block is None or len(big_chunks) < 2:
                failures.append(f"{case}: big.txt is not inventoried in several chunks")
            elif "\x0c" not in big_block["text"]:
                failures.append(f"{case}: the big.txt block carries no form feed to split on")
            else:
                text = big_block["text"]
                expected = text.count("\n") + (0 if text.endswith("\n") else 1)
                if big_chunks[-1]["end_line"] != expected:
                    failures.append(
                        f"{case}: big.txt's last chunk ends at line {big_chunks[-1]['end_line']}, "
                        f"the block has {expected} newline-terminated lines"
                    )
                if [c["start_line"] for c in big_chunks[1:]] != [
                    c["end_line"] + 1 for c in big_chunks[:-1]
                ]:
                    failures.append(f"{case}: big.txt's chunk line labels are not contiguous")
                encoded = full_diff.encode("utf-8")
                if not all(chunk_text(encoded, c).endswith("\n") for c in big_chunks[:-1]):
                    failures.append(f"{case}: a big.txt chunk boundary fell inside a diff line")
            # Overview from the store: no diff text, everything else present.
            overview = invoke("--from", store_path)
            if overview.returncode != 0:
                failures.append(f"{case}: --from overview exited {overview.returncode}: {overview.stderr}")
            else:
                headings = [m.group(0) for m in re.finditer(r"^## .*$", overview.stdout, re.MULTILINE)]
                if headings != ["## manifest", "## ranges", "## history", "## chunks"]:
                    failures.append(f"{case}: overview sections are {headings}")
                if "diff --git" in overview.stdout:
                    failures.append(f"{case}: the overview printed diff text")
            # Whole-path read that exceeds the bound is withheld and consumes nothing.
            big = invoke("--from", store_path, "--path", "big.txt")
            if big.returncode != 0 or "withheld:" not in section_of(big.stdout, "diff"):
                failures.append(f"{case}: reading big.txt without --chunk was not withheld")
            elif "consumed" in section_of(big.stdout, "chunks").replace("chunks consumed", ""):
                failures.append(f"{case}: a withheld read marked chunks consumed")
            expect_exit(case, 2, "out of range", "--from", store_path, "--path", "big.txt", "--chunk", "99")
            expect_exit(case, 2, "unknown path `*.txt`", "--from", store_path, "--path", "*.txt")
            expect_exit(case, 2, "no delta-diff section", "--from", store_path, "--section", "delta-diff", "--path", "a.py")
            # Consume every chunk exactly once, in inventory order, and recover the diff.
            recovered: list[str] = []
            emitted = 0
            for chunk in chunks:
                arguments = ["--from", store_path, "--path", chunk["path"]]
                if chunk["count"] > 1:
                    arguments += ["--chunk", str(chunk["index"])]
                read = invoke(*arguments)
                if read.returncode != 0:
                    failures.append(f"{case}: reading {chunk_label(chunk)} exited {read.returncode}: {read.stderr}")
                    break
                body = fenced_body(section_of(read.stdout, "diff"))
                if body is None:
                    failures.append(f"{case}: no fenced diff when reading {chunk_label(chunk)}")
                    break
                if len(body.encode("utf-8")) != chunk["bytes"]:
                    failures.append(
                        f"{case}: {chunk_label(chunk)} printed {len(body.encode('utf-8'))} bytes, "
                        f"inventory says {chunk['bytes']}"
                    )
                recovered.append(body)
                emitted += 1
                inventory = section_of(read.stdout, "chunks")
                if chunk["path"] == "big.txt" and chunk["index"] == 1:
                    if not re.search(r"^diff big\.txt#1/\d+ .* consumed$", inventory, re.MULTILINE):
                        failures.append(f"{case}: big.txt#1 is not consumed after its read")
                    if not re.search(r"^diff big\.txt#2/\d+ .* missing$", inventory, re.MULTILINE):
                        failures.append(f"{case}: big.txt#2 is not missing after reading #1")
                    if "diff coverage: incomplete" not in inventory:
                        failures.append(f"{case}: coverage not incomplete with big.txt chunks missing")
                    if "a.py" in inventory.split("diff coverage")[0]:
                        failures.append(f"{case}: a single-path read listed other paths' chunks")
            if emitted != len(chunks):
                failures.append(f"{case}: emitted {emitted} chunks, inventory has {len(chunks)}")
            if "".join(recovered) != full_diff:
                failures.append(f"{case}: concatenated chunks do not reproduce the persisted diff")
            final = invoke("--from", store_path)
            if final.returncode != 0 or f"diff coverage: complete ({len(chunks)}/{len(chunks)} chunks consumed)" not in final.stdout:
                failures.append(f"{case}: coverage is not complete after every chunk was read")
            # A store whose diff fits the bound prints it and marks everything consumed.
            small_store = store_path + ".small"
            output = run("--head", head, "--store", small_store, "--path", "a.py")
            if output is not None:
                if "diff --git a/a.py b/a.py" not in section_of(output, "diff"):
                    failures.append(f"{case}: a selection under the bound was not printed")
                inventory = section_of(output, "chunks")
                if not re.search(r"^diff a\.py#1/1 .* consumed$", inventory, re.MULTILINE):
                    failures.append(f"{case}: a printed selection was not marked consumed")
                if "diff coverage: incomplete" not in inventory:
                    failures.append(f"{case}: unselected chunks were not left missing")
        if len(failures) == before:
            passed.append(case)

        # The store is opened privately: no symlink, no other user's file, mode 0600.
        case = "store opened privately (symlink refused, pre-created file re-privatised)"
        before = len(failures)
        planted = tempfile.mkdtemp()
        target = os.path.join(planted, "target.json")
        link = os.path.join(planted, "link.json")
        with open(target, "w", encoding="utf-8"):
            pass
        os.symlink(target, link)
        expect_exit(
            case, 2, "cannot write store",
            "--merge-base", merge_base, "--head", head, "--path", "a.py", "--store", link,
        )
        if os.path.getsize(target) != 0:
            failures.append(f"{case}: the symlink's target received the diff")
        loose = os.path.join(planted, "loose.json")
        with open(loose, "w", encoding="utf-8") as handle:
            handle.write("pre-created\n")
        os.chmod(loose, 0o666)
        if run("--head", head, "--path", "a.py", "--store", loose) is not None:
            mode = stat.S_IMODE(os.stat(loose).st_mode)
            if mode != 0o600:
                failures.append(f"{case}: a pre-created store kept mode {oct(mode)}")
        shutil.rmtree(planted, ignore_errors=True)
        if len(failures) == before:
            passed.append(case)

        # The bound covers the whole build call, not the diff alone.
        case = "build call charges its other sections against the bound"
        before = len(failures)
        bounded_store = store_path + ".bounded"
        output = run("--head", head, "--path", "a.py", "--store", bounded_store, "--chunk-bytes", "500")
        if output is not None:
            selected: list[dict[str, Any]] = []
            try:
                with open(bounded_store, encoding="utf-8") as handle:
                    selected = [c for c in json.load(handle)["chunks"] if c["path"] == "a.py"]
            except (OSError, ValueError, KeyError) as error:
                failures.append(f"{case}: cannot read the bounded store: {error}")
            if not selected or sum(c["bytes"] for c in selected) >= 500:
                failures.append(f"{case}: a.py's diff is not under the 500-byte bound, so this proves nothing")
            if "withheld:" not in section_of(output, "diff"):
                failures.append(f"{case}: a diff under the bound was printed although the other sections exceed it")
            if "consumed" in section_of(output, "chunks").replace("chunks consumed", ""):
                failures.append(f"{case}: a chunk was consumed by a call whose whole output exceeds the bound")
        if len(failures) == before:
            passed.append(case)

        # Delta case 1: a third commit on top of the second, changing a line inside g.
        case = "delta ancestor case (third commit on top of the second)"
        before = len(failures)
        try:
            write("a.py", third_file)
            write("c.txt", "1\n2\n4\n5\n")
            git("commit", "-q", "-am", "Change g's return")
            third = git("rev-parse", "HEAD").strip()
        except GitError as error:
            print(f"self-test setup failed: {error}")
            return 1
        output = run("--head", third, "--prior-head", head, "--base-ref", "trunk")
        if output is not None:
            expect_conditions(
                case,
                output,
                {"ancestor": "yes", "merge-base-unchanged": "yes", "prior-head-reachable": "yes"},
            )
            delta_manifest = section_of(output, "delta-manifest")
            if not re.search(r"^M a\.py .*new=no ", delta_manifest, re.MULTILINE):
                failures.append(f"{case}: delta-manifest is missing an `M a.py` line")
            if "b.py" in delta_manifest:
                failures.append(f"{case}: delta-manifest lists b.py, which the delta leaves alone")
            delta_diff = section_of(output, "delta-diff")
            if "def g():" not in delta_diff or "+    return y + 1" not in delta_diff:
                failures.append(f"{case}: delta-diff does not show the change inside g")
            delta_overlap = section_of(output, "delta-overlap")
            if not re.search(
                r"^a\.py:\d+-\d+ overlaps a\.py:\d+-\d+$", delta_overlap, re.MULTILINE
            ):
                failures.append(f"{case}: delta-overlap does not pair the g hunk with the full diff")
            if re.search(r"^a\.py:\d+-\d+ overlaps none$", delta_overlap, re.MULTILINE):
                failures.append(f"{case}: delta-overlap reports the g hunk as overlapping none")
        output = run("--head", third, "--prior-head", head)
        if output is not None:
            expect_conditions(case, output, {"merge-base-unchanged": "unknown (no --base-ref)"})
        # Selection applies to the delta diff too, and the delta manifest stays complete.
        output = run("--head", third, "--prior-head", head, "--base-ref", "trunk", "--path", "a.py")
        if output is not None:
            delta_diff = section_of(output, "delta-diff")
            if "+    return y + 1" not in delta_diff:
                failures.append(f"{case}: selected delta-diff lacks the a.py change")
            if "c.txt" in delta_diff:
                failures.append(f"{case}: selected delta-diff still contains c.txt")
            if " c.txt " not in section_of(output, "delta-manifest"):
                failures.append(f"{case}: delta-manifest dropped unselected c.txt")
        expect_exit(
            case, 2, "unknown path `b.py`: not a path or old path in the delta-diff manifest",
            "--merge-base", merge_base, "--head", third, "--prior-head", head, "--path", "b.py",
        )
        # A stored re-review: the large full diff is withheld while the small delta fits.
        delta_store = store_path + ".delta"
        output = run("--head", third, "--prior-head", head, "--base-ref", "trunk", "--store", delta_store, "--chunk-bytes", "4000")
        if output is not None:
            inventory = section_of(output, "chunks")
            if "withheld:" not in section_of(output, "diff"):
                failures.append(f"{case}: the full diff over the bound was not withheld in the delta store")
            if "+    return y + 1" not in section_of(output, "delta-diff"):
                failures.append(f"{case}: the delta-diff under the bound was not printed")
            if not re.search(r"^delta-diff a\.py#1/1 .* consumed$", inventory, re.MULTILINE):
                failures.append(f"{case}: the printed delta-diff a.py chunk is not consumed")
            if "delta-diff coverage: complete (2/2 chunks consumed)" not in inventory:
                failures.append(f"{case}: delta-diff coverage after printing is not complete")
            if "\ndiff coverage: incomplete" not in inventory:
                failures.append(f"{case}: diff coverage is not incomplete while the full diff is withheld")
        # A tighter bound withholds the delta too; chunks are read back one at a time.
        tiny_store = store_path + ".tiny"
        output = run("--head", third, "--prior-head", head, "--base-ref", "trunk", "--store", tiny_store, "--chunk-bytes", "80")
        if output is not None:
            inventory = section_of(output, "chunks")
            first = re.search(r"^delta-diff a\.py#1/(\d+) .* missing$", inventory, re.MULTILINE)
            if first is None:
                failures.append(f"{case}: tiny delta store inventory lacks a missing delta-diff a.py#1 chunk")
            if "delta-diff coverage: incomplete (0/" not in inventory:
                failures.append(f"{case}: tiny delta store does not start at 0 delta chunks consumed")
            count = int(first.group(1)) if first else 0
            if count < 2:
                failures.append(f"{case}: expected a.py's delta to need at least 2 chunks at 80 bytes, got {count}")
            pieces: list[str] = []
            for index in range(1, count + 1):
                read = invoke("--from", tiny_store, "--section", "delta-diff", "--path", "a.py", "--chunk", str(index))
                if read.returncode != 0:
                    failures.append(f"{case}: delta chunk {index} read exited {read.returncode}: {read.stderr}")
                    break
                body = fenced_body(section_of(read.stdout, "delta-diff"))
                if body is None:
                    failures.append(f"{case}: delta chunk {index} read printed no fenced diff")
                    break
                pieces.append(body)
                inventory = section_of(read.stdout, "chunks")
                if "\ndiff coverage" in inventory or inventory.startswith("diff "):
                    failures.append(f"{case}: a delta-diff read reported the diff section")
                if re.search(r"^delta-diff c\.txt#", inventory, re.MULTILINE):
                    failures.append(f"{case}: a single-path delta read listed c.txt's chunks")
                if not re.search(rf"^delta-diff a\.py#{index}/{count} .* consumed$", inventory, re.MULTILINE):
                    failures.append(f"{case}: delta chunk {index} is not consumed after its read")
                if index < count and not re.search(rf"^delta-diff a\.py#{index + 1}/{count} .* missing$", inventory, re.MULTILINE):
                    failures.append(f"{case}: delta chunk {index + 1} is not missing after reading {index}")
            if "+    return y + 1" not in "".join(pieces):
                failures.append(f"{case}: the delta chunks of a.py do not contain the g change")
            if pieces and "delta-diff coverage: incomplete" not in inventory:
                failures.append(f"{case}: delta coverage is complete although c.txt's delta chunk is unread")
        if len(failures) == before:
            passed.append(case)

        # Delta case 2: the branch is rewritten with --amend, so the prior head is no ancestor.
        case = "delta amend case (branch rewritten with git commit --amend)"
        before = len(failures)
        try:
            git("commit", "-q", "--amend", "-m", "Change g's return (amended)")
            amended = git("rev-parse", "HEAD").strip()
        except GitError as error:
            print(f"self-test setup failed: {error}")
            return 1
        output = run("--head", amended, "--prior-head", third, "--base-ref", "trunk")
        if output is not None:
            expect_conditions(
                case,
                output,
                {"ancestor": "no", "merge-base-unchanged": "yes", "prior-head-reachable": "yes"},
            )
        if len(failures) == before:
            passed.append(case)

        # Delta case 3: the base ref moves by a commit on trunk, and topic merges it.
        case = "delta merge-base case (base ref moved by a commit on another branch)"
        before = len(failures)
        try:
            git("checkout", "-q", "trunk")
            write("d.txt", "trunk moved\n")
            git("add", "d.txt")
            git("commit", "-q", "-m", "Move trunk")
            git("checkout", "-q", "topic")
            git("merge", "-q", "--no-edit", "trunk")
            merged = git("rev-parse", "HEAD").strip()
            current_merge_base = git("merge-base", "trunk", merged).strip()
        except GitError as error:
            print(f"self-test setup failed: {error}")
            return 1
        if current_merge_base == merge_base:
            failures.append(f"{case}: moving trunk did not move the merge-base")
        output = run(
            "--head",
            merged,
            "--prior-head",
            amended,
            "--base-ref",
            "trunk",
            pinned_merge_base=current_merge_base,
        )
        if output is not None:
            expect_conditions(
                case,
                output,
                {"ancestor": "yes", "merge-base-unchanged": "no", "prior-head-reachable": "yes"},
            )
        if len(failures) == before:
            passed.append(case)

        # An unreachable prior head is reported, not a failure.
        output = run(
            "--head", merged, "--prior-head", "0" * 40, "--base-ref", "trunk"
        )
        if output is not None:
            expect_conditions(
                "unreachable prior head",
                output,
                {
                    "ancestor": "no",
                    "merge-base-unchanged": "no",
                    "prior-head-reachable": "no",
                },
            )
            if section_of(output, "delta-overlap").strip() != "```\n\n```":
                failures.append("unreachable prior head: delta-overlap is not empty")

        # --help documents the selection and recovery calls.
        case = "--help documents selection and recovery"
        before = len(failures)
        help_output = invoke("--help")
        if help_output.returncode != 0:
            failures.append(f"{case}: --help exited {help_output.returncode}")
        for option in ("--path", "--store", "--from", "--chunk", "--section", "--chunk-bytes"):
            if option not in help_output.stdout:
                failures.append(f"{case}: --help does not mention {option}")
        expect_exit(case, 2, "--chunk requires exactly one --path", "--from", store_path, "--chunk", "1")
        expect_exit(case, 2, "--from cannot be combined", "--from", store_path, "--head", head)
        if len(failures) == before:
            passed.append(case)

        # A bound a --from read cannot honour is refused rather than ignored:
        # the chunk offsets were fixed when the store was written, so a read
        # that quietly printed a whole chunk past the reviewer's limit would
        # mark it consumed anyway.
        case = "--chunk-bytes is only used with --store"
        before = len(failures)
        expect_exit(
            case, 2, "cannot be combined with --from",
            "--from", store_path, "--path", "big.txt", "--chunk", "1", "--chunk-bytes", "100",
        )
        expect_exit(case, 2, "--self-test takes no other arguments", "--self-test", "--chunk-bytes", "100")
        expect_exit(
            case, 2, "only used with --store",
            "--merge-base", merge_base, "--head", head, "--chunk-bytes", "100",
        )
        expect_exit(
            case, 2, "only used with --store",
            "--merge-base", merge_base, "--head", head, "--path", "a.py", "--chunk-bytes", "100",
        )
        default_store = store_path + ".default"
        if run("--head", head, "--path", "a.py", "--store", default_store) is not None:
            with open(default_store, encoding="utf-8") as handle:
                if json.load(handle)["chunk_bytes"] != DEFAULT_CHUNK_BYTES:
                    failures.append(f"{case}: a build without --chunk-bytes did not use the default")
        if len(failures) == before:
            passed.append(case)
        shutil.rmtree(store_directory, ignore_errors=True)

    for case in passed:
        print(f"self-test passed: {case}")
    for failure in failures:
        print(failure)
    return 1 if failures else 0


# --- Command line ------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the manifest, function-context diff, hunk ranges, and "
        "pre-merge-base history for one pull request's changes. With --store, "
        "persist the complete context privately and bound each call's diff output; "
        "with --from, read bounded chunks back from that store without touching git.",
        epilog="Selection and recovery: --path P (repeatable, literal, use --path=P for a "
        "leading dash) limits the diff and delta-diff output; --store FILE writes the "
        "complete context and prints at most --chunk-bytes of diff per call; "
        "--from FILE [--section diff|delta-diff] --path P [--chunk K] prints one path or "
        "one chunk from the store and marks it consumed in the `## chunks` inventory. "
        "Exit 2 names an unknown path, an out-of-range chunk, or an unreadable store.",
    )
    parser.add_argument("--merge-base", help="the pinned merge-base SHA")
    parser.add_argument("--head", help="the pinned head SHA")
    parser.add_argument(
        "--prior-head",
        help="the head the earlier review pinned; adds the delta sections",
    )
    parser.add_argument(
        "--base-ref",
        help="the base branch (e.g. origin/main) that decides merge-base-unchanged",
    )
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        metavar="PATH",
        help="repo-relative path to select, literally; repeatable; --path=PATH for a leading dash",
    )
    parser.add_argument(
        "--store",
        metavar="FILE",
        help="persist the complete context to this private file and bound the output",
    )
    parser.add_argument(
        "--chunk-bytes",
        type=int,
        default=None,
        metavar="N",
        help="the byte bound a stored call's diff text must fit; the build call charges "
        f"its other sections against it first (default {DEFAULT_CHUNK_BYTES}). "
        "Only used with --store: the bound is fixed when the store is written",
    )
    parser.add_argument(
        "--from",
        dest="store_from",
        metavar="FILE",
        help="read from a store written by --store instead of git; never rebuilds the diff",
    )
    parser.add_argument(
        "--section",
        choices=SECTIONS,
        default="diff",
        help="which diff a --from read comes from (default diff)",
    )
    parser.add_argument(
        "--chunk",
        type=int,
        metavar="K",
        help="with --from and one --path: print chunk K of that path (1-based)",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit one JSON object instead of Markdown"
    )
    parser.add_argument(
        "--self-test", action="store_true", help="check the command against a scratch repository"
    )
    arguments = parser.parse_args()

    if arguments.self_test:
        if (
            arguments.merge_base or arguments.head or arguments.prior_head or arguments.base_ref
            or arguments.path or arguments.store or arguments.store_from or arguments.chunk
            or arguments.chunk_bytes is not None
        ):
            parser.error("--self-test takes no other arguments")
        return self_test()
    if arguments.chunk_bytes is not None and arguments.chunk_bytes < 1:
        parser.error("--chunk-bytes must be at least 1")
    if arguments.chunk is not None and (len(arguments.path) != 1 or not arguments.store_from):
        parser.error("--chunk requires exactly one --path and --from")
    if arguments.store_from:
        if (
            arguments.merge_base or arguments.head or arguments.prior_head or arguments.base_ref
            or arguments.store
        ):
            parser.error("--from cannot be combined with --merge-base, --head, --prior-head, --base-ref, or --store")
        if arguments.chunk_bytes is not None:
            parser.error(
                "--chunk-bytes cannot be combined with --from: the bound and the chunk "
                "offsets were fixed when the store was written, so a smaller bound needs "
                "a rebuild with --store --chunk-bytes N"
            )
    else:
        if not arguments.merge_base or not arguments.head:
            parser.error("--merge-base and --head are both required")
        if arguments.base_ref and not arguments.prior_head:
            parser.error("--base-ref is only used with --prior-head")
        if arguments.section != "diff":
            parser.error("--section is only used with --from")
        if arguments.chunk_bytes is not None and not arguments.store:
            parser.error(
                "--chunk-bytes is only used with --store: the bound applies to the diff "
                "text a store build prints, so a build without --store prints its whole "
                "output unbounded"
            )

    try:
        if arguments.store_from:
            store = load_store(arguments.store_from)
            view = store_view(
                store, arguments.store_from, arguments.section, arguments.path, arguments.chunk
            )
            if arguments.path:
                write_store(arguments.store_from, store)
            sys.stdout.write(render_view(view, arguments.json))
            return 0
        context = build_context(
            arguments.merge_base,
            arguments.head,
            prior_head=arguments.prior_head,
            base_ref=arguments.base_ref,
        )
        if not arguments.path and not arguments.store:
            if arguments.json:
                print(json.dumps(context, ensure_ascii=False, indent=2))
            else:
                sys.stdout.write(render_markdown(context))
            return 0
        store = None
        if arguments.store:
            store = make_store(
                context,
                DEFAULT_CHUNK_BYTES if arguments.chunk_bytes is None else arguments.chunk_bytes,
            )
            write_store(arguments.store, store)
        view = live_view(context, arguments.path, store, arguments.store, arguments.json)
        if store is not None:
            write_store(arguments.store, store)
        sys.stdout.write(render_view(view, arguments.json))
    except GitError as error:
        print(f"review_context: {error.command} failed: {error.detail}", file=sys.stderr)
        return 2
    except InputError as error:
        print(f"review_context: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
