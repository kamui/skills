#!/usr/bin/env python3
"""Build the local review context for code-review-publish in one call.

Emits, for the pinned merge-base and head of one pull request, the changed-file
manifest, the complete merge-base diff with function context, the head and
merge-base line ranges of every hunk, and the last commits before the merge-base
that touched each changed path. It reads only the local git repository: it never
calls `gh`, never touches the network, and never prints a whole file.

Usage:
    python3 scripts/review_context.py --merge-base SHA --head SHA [--json]
    python3 scripts/review_context.py --self-test

Run it from inside the clone under review. Default output is Markdown with one
fenced block per section, in this order: `## manifest`, `## diff`, `## ranges`,
`## history`. `--json` emits the same content as one JSON object.

Manifest lines read `<status> <path> [<- <old path>] +<ins> -<del> new=<yes|no>
lines=<n>`, where `status` is `A`, `M`, `D`, or `R`; `new=yes` marks a path the
diff adds in full, so it is not read again; `lines` is the path's line count at
head, and `0` for a deletion. A binary path reports `+- --` for its counts.

Range lines read `<path>:<start>-<end> @head` and `<path>:<start>-<end>
@merge-base`, one pair per hunk, covering the lines the function-context hunk
spans on that side. A side a hunk covers no lines on -- the merge-base side of a
pure addition, the head side of a pure deletion -- has no line.

Exit codes:
    0  the context was written to stdout
    1  a --self-test assertion failed; unused in normal operation
    2  a git command failed, or the arguments are unusable; the failing command
       is named on stderr
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Any, Optional

HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")


class GitError(Exception):
    """A git subprocess failed, or could not be started."""

    def __init__(self, command: str, detail: str) -> None:
        super().__init__(f"{command}: {detail}")
        self.command = command
        self.detail = detail


def run_git(arguments: list[str], cwd: Optional[str] = None) -> str:
    command = ["git", "-c", "core.quotepath=false", *arguments]
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
    if completed.returncode != 0:
        raise GitError(printable, completed.stderr.strip() or "exited non-zero")
    return completed.stdout


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
    """Name each path whose every hunk header carries no enclosing context."""
    notes: list[str] = []
    for entry in files:
        if not entry["hunks"]:
            continue
        if any(hunk["section"] for hunk in entry["hunks"]):
            continue
        path = entry["new_path"] or entry["old_path"]
        notes.append(
            f"note: no function context for {path}; read enclosing ranges by hand"
        )
    return notes


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
                path,
            ],
            cwd,
        )
        history.append(
            {"path": path, "commits": [line for line in output.splitlines() if line]}
        )
    return history


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
    diff_text = context["diff"]
    diff_fence = fence_for(diff_text)

    sections = [
        f"## manifest\n\n```\n{manifest_body}\n```",
        f"## diff\n\n{diff_fence}diff\n{diff_text.rstrip(chr(10))}\n{diff_fence}",
    ]
    if context["notes"]:
        sections[-1] += "\n\n" + "\n".join(context["notes"])
    sections.append(f"## ranges\n\n```\n{range_body}\n```")
    sections.append(f"## history\n\n```\n{history_body}\n```")
    return "\n\n".join(sections) + "\n"


def build_context(merge_base: str, head: str, cwd: Optional[str] = None) -> dict[str, Any]:
    manifest = build_manifest(merge_base, head, cwd)
    diff_text = run_git(["diff", f"{merge_base}...{head}", "--function-context"], cwd)
    files = parse_diff(diff_text)
    return {
        "merge_base": merge_base,
        "head": head,
        "manifest": manifest,
        "diff": diff_text,
        "notes": build_notes(files),
        "ranges": build_ranges(files),
        "history": build_history(merge_base, manifest, cwd),
    }


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


def self_test() -> int:
    """Drive the command line against a scratch repository. Exit 1 on mismatch."""
    base_file = "def f():\n    x = 1\n    return x\n\n\ndef g():\n    y = 2\n    return y\n"
    head_file = "def f():\n    x = 1\n    return x\n\n\ndef g():\n    y = 3\n    return y\n"
    failures: list[str] = []

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
            write(".gitattributes", "*.py diff=python\n")
            write("a.py", base_file)
            git("add", ".")
            git("commit", "-q", "-m", "Add a.py")
            merge_base = git("rev-parse", "HEAD").strip()
            write("a.py", head_file)
            write("b.py", "def h():\n    return 0\n")
            git("add", ".")
            git("commit", "-q", "-m", "Change g and add b.py")
            head = git("rev-parse", "HEAD").strip()
        except GitError as error:
            print(f"self-test setup failed: {error}")
            return 1

        completed = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--merge-base", merge_base, "--head", head],
            cwd=repository,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    if completed.returncode != 0:
        print(f"expected exit 0, got {completed.returncode}: {completed.stderr.strip()}")
        return 1

    output = completed.stdout
    manifest = section_of(output, "manifest")
    diff = section_of(output, "diff")
    ranges = section_of(output, "ranges")
    history = section_of(output, "history")

    if not re.search(r"^M a\.py .*new=no ", manifest, re.MULTILINE):
        failures.append("manifest is missing an `M a.py ... new=no` line")
    if not re.search(r"^A b\.py .*new=yes ", manifest, re.MULTILINE):
        failures.append("manifest is missing an `A b.py ... new=yes` line")

    a_py_diff = diff.split("diff --git a/b.py")[0]
    if "a/a.py" not in a_py_diff or "def g():" not in a_py_diff:
        failures.append("the diff section's hunk for a.py does not contain `def g():`")

    if not re.search(r"^a\.py:\d+-\d+ @head$", ranges, re.MULTILINE):
        failures.append("ranges is missing an `a.py:<start>-<end> @head` line")
    if not re.search(r"^a\.py:\d+-\d+ @merge-base$", ranges, re.MULTILINE):
        failures.append("ranges is missing an `a.py:<start>-<end> @merge-base` line")

    a_py_history = [line for line in history.splitlines() if line.startswith("a.py: ")]
    if len(a_py_history) != 1:
        failures.append(f"expected one history line for a.py, got {len(a_py_history)}")

    for failure in failures:
        print(failure)
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the manifest, function-context diff, hunk ranges, and "
        "pre-merge-base history for one pull request's changes."
    )
    parser.add_argument("--merge-base", help="the pinned merge-base SHA")
    parser.add_argument("--head", help="the pinned head SHA")
    parser.add_argument(
        "--json", action="store_true", help="emit one JSON object instead of Markdown"
    )
    parser.add_argument(
        "--self-test", action="store_true", help="check the command against a scratch repository"
    )
    arguments = parser.parse_args()

    if arguments.self_test:
        if arguments.merge_base or arguments.head:
            parser.error("--self-test takes no other arguments")
        return self_test()
    if not arguments.merge_base or not arguments.head:
        parser.error("--merge-base and --head are both required")

    try:
        context = build_context(arguments.merge_base, arguments.head)
    except GitError as error:
        print(f"review_context: {error.command} failed: {error.detail}", file=sys.stderr)
        return 2

    if arguments.json:
        print(json.dumps(context, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(render_markdown(context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
