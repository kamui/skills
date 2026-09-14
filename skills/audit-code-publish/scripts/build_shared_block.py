#!/usr/bin/env python3
"""Build the shared, judgment-free input block for both review finders.

Purpose: assemble the pinned diff, changed-file manifest, ancestor guidance
files, test-suite result summaries, and finding-format pointer that both
finders receive verbatim, so no finder re-reads the repository to construct
its own inputs.

Usage:
    python3 scripts/build_shared_block.py --repo <path> --base-ref <ref>
        --base-sha <sha> --head-sha <sha> --merge-base <sha>
        --finding-format <absolute path> [--suite-results <path>]
        [--max-bytes <n>]

The block is written to stdout; an oversized-diff notice goes to stderr.

Exit codes:
    0  the block was written
    2  a git command failed, naming the command on stderr

Input schema: the pinned run identity (base ref, base SHA, head SHA,
merge-base) and a local git repository containing all three commits. The
finding-format path is an absolute path echoed into the block, not read.
When supplied, suite-results is a UTF-8 file containing one result-summary
line per suite.
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
import typing
from pathlib import Path, PurePosixPath

GUIDANCE_NAMES = (
    "CLAUDE.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "CODING_STANDARDS.md",
)


class GitFailure(Exception):
    """A git command could not produce the requested pinned input."""

    def __init__(self, command: list[str], detail: str) -> None:
        self.command = command
        self.detail = detail
        super().__init__(detail)


class InputError(OSError):
    """An argument named an input file the script could not read."""


def run_git(repo: Path, *arguments: str) -> str:
    command = ["git", "-C", str(repo), *arguments]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="surrogateescape",
        )
    except OSError as error:
        raise GitFailure(command, str(error)) from error
    if result.returncode != 0:
        raise GitFailure(command, result.stderr.strip())
    return result.stdout


def write_stream(stream: typing.TextIO, text: str) -> None:
    """Write text that may carry surrogates from `errors="surrogateescape"`.

    Git output is decoded with `surrogateescape`, so a byte the repository holds
    that is not valid UTF-8 survives as a lone surrogate. Encoding it back the
    same way round-trips the original byte; printing it to a strict stdout would
    raise `UnicodeEncodeError` and lose the whole block.
    """
    stream.flush()
    stream.buffer.write(text.encode("utf-8", errors="surrogateescape"))
    stream.buffer.flush()


def changed_paths(repo: Path, merge_base: str, head_sha: str) -> list[str]:
    output = run_git(
        repo,
        "diff",
        f"{merge_base}...{head_sha}",
        "--name-status",
        "-z",
    )
    fields = output.rstrip("\0").split("\0") if output else []
    paths: list[str] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        path_count = 2 if status[:1] in {"R", "C"} else 1
        if index + path_count > len(fields):
            command = [
                "git",
                "-C",
                str(repo),
                "diff",
                f"{merge_base}...{head_sha}",
                "--name-status",
                "-z",
            ]
            raise GitFailure(command, "git returned an incomplete name-status record")
        paths.extend(fields[index : index + path_count])
        index += path_count
    return paths


def guidance_candidates(paths: list[str]) -> set[str]:
    candidates: set[str] = set()
    for changed_path in paths:
        directory = PurePosixPath(changed_path).parent
        while True:
            prefix = "" if directory == PurePosixPath(".") else f"{directory}/"
            candidates.update(f"{prefix}{name}" for name in GUIDANCE_NAMES)
            if directory == PurePosixPath("."):
                break
            directory = directory.parent
    return candidates


def applicable_guidance(
    repo: Path, base_sha: str, paths: list[str]
) -> list[tuple[str, str, str]]:
    tree = set(
        filter(
            None,
            run_git(repo, "ls-tree", "-r", "--name-only", "-z", base_sha).split("\0"),
        )
    )
    applicable = guidance_candidates(paths) & tree
    ordered = sorted(applicable, key=lambda path: (path.count("/"), path))
    guidance: list[tuple[str, str, str]] = []
    for path in ordered:
        object_name = f"{base_sha}:{path}"
        blob_id = run_git(repo, "rev-parse", object_name).strip()
        content = run_git(repo, "show", object_name)
        guidance.append((path, blob_id, content))
    return guidance


def fenced(text: str, language: str = "text") -> str:
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", text)), default=0)
    marker = "`" * max(3, longest + 1)
    body = text.rstrip("\n")
    return f"{marker}{language}\n{body}\n{marker}" if body else f"{marker}{language}\n{marker}"


def build(args: argparse.Namespace) -> tuple[str, str | None]:
    repo = Path(args.repo).resolve()
    suite_results = None
    if args.suite_results:
        try:
            suite_results = Path(args.suite_results).read_text(encoding="utf-8")
        except OSError as error:
            raise InputError(
                f"cannot read suite results {args.suite_results}: {error}"
            ) from error
    manifest = run_git(repo, "diff", f"{args.merge_base}...{args.head_sha}", "--name-status")
    commits = run_git(
        repo,
        "log",
        f"{args.merge_base}..{args.head_sha}",
        "--format=%H %s",
    )
    diff = run_git(repo, "diff", f"{args.merge_base}...{args.head_sha}")
    paths = changed_paths(repo, args.merge_base, args.head_sha)
    guidance = applicable_guidance(repo, args.base_sha, paths)

    sections = [
        "## Pinned run identity\n\n"
        f"- base ref: `{args.base_ref}`\n"
        f"- base SHA: `{args.base_sha}`\n"
        f"- head SHA: `{args.head_sha}`\n"
        f"- merge-base: `{args.merge_base}`",
        "## Changed-file manifest\n\n" + fenced(manifest),
        "## Commit list\n\n" + fenced(commits),
    ]

    diff_bytes = len(diff.encode("utf-8", errors="surrogateescape"))
    notice = None
    if diff_bytes > args.max_bytes:
        command = f"git diff {args.merge_base}...{args.head_sha}"
        sections.append(
            "## Full diff\n\n"
            f"The diff is larger than the shared-input limit. In `{repo}`, run "
            f"`{command}` yourself before reviewing."
        )
        notice = (
            f"build_shared_block: diff is {diff_bytes} bytes, above --max-bytes "
            f"{args.max_bytes}; emitted the command-based fallback"
        )
    else:
        sections.append("## Full diff\n\n" + fenced(diff, "diff"))

    if guidance:
        rendered_guidance = ["## Applicable base-branch guidance"]
        for path, blob_id, content in guidance:
            rendered_guidance.append(
                f"### `{path}` (base blob `{blob_id}`)\n\n{content.rstrip()}"
            )
        sections.append("\n\n".join(rendered_guidance))
    else:
        sections.append("## Applicable base-branch guidance\n\nNone.")

    if suite_results is not None:
        sections.append("## Test suite results\n\n" + fenced(suite_results))

    sections.append(
        "## Finding format\n\n"
        f"Read `{args.finding_format}` before reviewing and follow its finding contract."
    )
    return "\n\n".join(sections) + "\n", notice


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write the shared audit-code-publish finder block to stdout."
    )
    parser.add_argument("--repo", required=True, help="path to the repository under review")
    parser.add_argument("--base-ref", required=True, help="pinned base branch name")
    parser.add_argument("--base-sha", required=True, help="pinned base branch commit")
    parser.add_argument("--head-sha", required=True, help="pinned pull-request head commit")
    parser.add_argument("--merge-base", required=True, help="pinned comparison merge-base")
    parser.add_argument(
        "--finding-format", required=True, help="absolute path to references/finding-format.md"
    )
    parser.add_argument(
        "--suite-results",
        help="UTF-8 file containing one result-summary line per test suite",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=200_000,
        help="replace a larger diff with a command-based fallback (default: 200000)",
    )
    args = parser.parse_args()

    if not Path(args.finding_format).is_absolute():
        parser.error("--finding-format must be an absolute path")
    if args.max_bytes < 0:
        parser.error("--max-bytes must be non-negative")

    try:
        output, notice = build(args)
    except InputError as error:
        write_stream(sys.stderr, f"build_shared_block: {error}\n")
        return 2
    except GitFailure as error:
        write_stream(
            sys.stderr,
            f"build_shared_block: git command failed: {shlex.join(error.command)}\n",
        )
        if error.detail:
            write_stream(sys.stderr, error.detail + "\n")
        return 2
    write_stream(sys.stdout, output)
    if notice:
        write_stream(sys.stderr, notice + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
