#!/usr/bin/env python3
"""Render and check commit-pinned coordinate link fragments for published reviews.

Purpose: the published review body, and the caller report on a retrospective
run, name files by coordinate. Every coordinate the URL rule can express
renders as a Markdown link whose visible text is the unchanged coordinate and
whose target is a commit-pinned blob URL under the base repository's canonical
web URL; everything the rule cannot express stays the code span it already
was. This script owns that rule so no review composes a URL by hand.

The rule:
    - the link resolves at the reviewed full head SHA, never a branch name or
      an abbreviated SHA;
    - a line coordinate renders `?plain=1#L<line>`, a range renders
      `?plain=1#L<start>-L<end>`, and a file anchor (a bare path) carries
      neither;
    - the path is decoded of its percent escapes once, then encoded once with
      `urllib.parse.quote(path, safe="/")`, so spaces, `%`, and path-borne
      `?`/`#` cannot forge a query or fragment;
    - a `LEFT` anchor, and any coordinate carrying an old path, renders as a
      code span: merge-base and rename links are deferred to issue #84.

Usage:
    python3 scripts/link_coordinate.py --self-test
    python3 scripts/link_coordinate.py render --repo-url <url> --revision <sha>
        --coordinate <path|path:line|path:start-end> [--side RIGHT|LEFT]
        [--old-path <path>]
    python3 scripts/link_coordinate.py check --repo-url <url> --revision <sha>
        --coordinate <...> [--side RIGHT|LEFT] [--old-path <path>]
        --fragment <fragment|->

`render` writes one fragment to stdout, followed by a newline. `check`
re-renders the fragment from the same inputs and exits 0 only when `--fragment`
is exactly that fragment; `-` reads the fragment from stdin, stripping one
trailing newline. `render` with `--old-path` notes on stderr that renames are
deferred to issue #84 and emits the code-span form.

Exit codes:
    0  fragment rendered, fragment matched, or the self-test passed
    1  content violation: one line per violation on stdout
    2  input cannot be read: named on stderr

Input schema: `--repo-url` is the base repository's canonical http(s) web URL;
`--revision` is the reviewed head as a full 40-hex commit SHA; `--side` is the
diff side the coordinate was read at (`RIGHT`, the default, links; `LEFT`
never does); `--coordinate` is a whole repository-relative path optionally
followed by `:<line>` or `:<start>-<end>`; `--old-path` records the pre-rename
path, if any; `--fragment` (check only) is the published fragment under test.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import sys
import urllib.parse

SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
RANGE_PATTERN = re.compile(r"^[0-9]+-[0-9]+$")


class CoordinateError(Exception):
    """An input violates the URL rule; one line on stdout, exit 1."""


def parse_coordinate(coordinate: str) -> tuple[str, int | None, int | None]:
    """Split a coordinate into its path and optional inclusive line range."""
    if not coordinate or coordinate != coordinate.strip():
        raise CoordinateError(
            f"coordinate {coordinate!r} must be a non-empty coordinate"
            " without leading or trailing whitespace"
        )
    if "`" in coordinate:
        raise CoordinateError(
            f"coordinate {coordinate!r} contains a backtick, which the URL rule"
            " cannot render safely; paths with backticks are deferred to issue #84"
        )
    if "\n" in coordinate or "\r" in coordinate:
        raise CoordinateError(f"coordinate {coordinate!r} spans multiple lines")
    path, start, end = coordinate, None, None
    head, separator, tail = coordinate.rpartition(":")
    if head and separator and tail:
        if RANGE_PATTERN.match(tail):
            first, last = tail.split("-", 1)
            start, end = int(first), int(last)
            path = head
        elif tail.isdigit():
            start, end = int(tail), None
            path = head
    if start is not None and start < 1:
        raise CoordinateError(f"coordinate {coordinate!r} has a non-positive start line")
    if end is not None and end < 1:
        raise CoordinateError(f"coordinate {coordinate!r} has a non-positive end line")
    if start is not None and end is not None and start > end:
        raise CoordinateError(f"coordinate {coordinate!r} has a reversed range: {start} > {end}")
    return path, start, end


def validate_identity(repo_url: str, revision: str) -> str:
    """Return the canonical repository URL, refusing a non-commit revision."""
    repo = repo_url.rstrip("/")
    if not (repo.startswith("http://") or repo.startswith("https://")):
        raise CoordinateError(
            f"repository URL {repo_url!r} must be the canonical http(s) web URL"
            " of the base repository"
        )
    if not SHA_PATTERN.match(revision):
        raise CoordinateError(
            f"revision {revision!r} must be the reviewed head as a full 40-hex"
            " commit SHA, never a branch name or abbreviated SHA"
        )
    return repo


def blob_url(repo_url: str, revision: str, coordinate: str) -> str:
    """Build the commit-pinned blob URL for one coordinate."""
    path, start, end = parse_coordinate(coordinate)
    repo = validate_identity(repo_url, revision)
    quoted = urllib.parse.quote(urllib.parse.unquote(path), safe="/")
    url = f"{repo}/blob/{revision}/{quoted}"
    if start is None:
        return url
    if end is None:
        return f"{url}?plain=1#L{start}"
    return f"{url}?plain=1#L{start}-L{end}"


def render_fragment(
    repo_url: str,
    revision: str,
    side: str,
    coordinate: str,
    old_path: str | None = None,
) -> str:
    """Render the exact fragment the URL rule produces for one coordinate."""
    parse_coordinate(coordinate)
    validate_identity(repo_url, revision)
    if side == "LEFT" or old_path is not None:
        return f"`{coordinate}`"
    return f"[`{coordinate}`]({blob_url(repo_url, revision, coordinate)})"


def check_fragment(
    repo_url: str,
    revision: str,
    side: str,
    coordinate: str,
    old_path: str | None,
    fragment: str,
) -> str | None:
    """Return one violation line when the fragment is not exactly the rule's."""
    expected = render_fragment(repo_url, revision, side, coordinate, old_path)
    if fragment == expected:
        return None
    return (
        "link_coordinate: fragment does not match the rule for coordinate"
        f" {coordinate!r}: expected {expected}, got {fragment}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render or check a commit-pinned coordinate link fragment."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in fixtures and exit",
    )
    commands = parser.add_subparsers(dest="command", metavar="command")
    for name, help_text in (
        ("render", "write the fragment for one coordinate to stdout"),
        ("check", "exit 0 only when --fragment is exactly the rule's fragment"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument(
            "--repo-url",
            required=True,
            help="base repository's canonical http(s) web URL",
        )
        command.add_argument(
            "--revision",
            required=True,
            help="reviewed head as a full 40-hex commit SHA",
        )
        command.add_argument(
            "--coordinate",
            required=True,
            help="path, path:line, or path:start-end",
        )
        command.add_argument(
            "--side",
            choices=("RIGHT", "LEFT"),
            default="RIGHT",
            help="diff side the coordinate was read at (default: RIGHT)",
        )
        command.add_argument(
            "--old-path",
            help="pre-rename path when the file was renamed; renders the code-span form",
        )
        if name == "check":
            command.add_argument(
                "--fragment",
                required=True,
                help="the fragment under test; '-' reads it from stdin",
            )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.command is None:
        parser.error("one of --self-test or a command (render, check) is required")
    fragment = None
    if args.command == "check" and args.fragment == "-":
        try:
            fragment = sys.stdin.read()
        except OSError as error:
            sys.stderr.write(f"link_coordinate: cannot read stdin: {error}\n")
            return 2
        if fragment.endswith("\r\n"):
            fragment = fragment[:-2]
        elif fragment.endswith("\n"):
            fragment = fragment[:-1]
    elif args.command == "check":
        fragment = args.fragment
    try:
        if args.command == "render":
            output = render_fragment(
                args.repo_url, args.revision, args.side, args.coordinate, args.old_path
            )
            if args.old_path is not None and args.side != "LEFT":
                sys.stderr.write(
                    "link_coordinate: --old-path supplied; rename links are deferred"
                    " to issue #84, so the coordinate renders as a code span\n"
                )
            sys.stdout.write(output + "\n")
        else:
            violation = check_fragment(
                args.repo_url,
                args.revision,
                args.side,
                args.coordinate,
                args.old_path,
                fragment,
            )
            if violation is not None:
                sys.stdout.write(violation + "\n")
                return 1
    except CoordinateError as error:
        sys.stdout.write(f"link_coordinate: {error}\n")
        return 1
    return 0


def self_test() -> int:
    repo = "https://github.com/acme/payments"
    head = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
    merge_base = "9e8d7c6a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e"
    other_sha = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    base = f"{repo}/blob/{head}"
    failures: list[str] = []
    cases = 0

    def run(argv: list[str]) -> tuple[int, str, str]:
        nonlocal cases
        cases += 1
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def expect_render(name: str, argv: list[str], expected: str) -> None:
        code, out, _ = run(argv)
        if code != 0:
            failures.append(f"{name}: exit {code}, stdout {out!r}")
        elif out != expected + "\n":
            failures.append(f"{name}: got {out!r}, want {expected + chr(10)!r}")
        else:
            print(f"ok {name}")

    def expect_check(name: str, argv: list[str]) -> None:
        code, out, _ = run(argv)
        if code != 0:
            failures.append(f"{name}: exit {code}, stdout {out!r}")
        elif out:
            failures.append(f"{name}: expected silent success, got {out!r}")
        else:
            print(f"ok {name}")

    def expect_violation(name: str, argv: list[str]) -> None:
        code, out, _ = run(argv)
        if code != 1:
            failures.append(f"{name}: exit {code}, want 1")
        elif not out.strip() or len(out.strip().splitlines()) != 1:
            failures.append(f"{name}: want exactly one violation line, got {out!r}")
        else:
            print(f"ok {name}")

    anchor_fragment = f"[`src/payments.ts:42`]({base}/src/payments.ts?plain=1#L42)"
    fix_fragment = f"[`src/retry-policy.ts:18`]({base}/src/retry-policy.ts?plain=1#L18)"

    def check_argv(coordinate: str, fragment: str, **overrides: str) -> list[str]:
        argv = [
            "check",
            "--repo-url",
            overrides.get("repo_url", repo),
            "--revision",
            overrides.get("revision", head),
            "--coordinate",
            coordinate,
            "--fragment",
            fragment,
        ]
        if "side" in overrides:
            argv += ["--side", overrides["side"]]
        return argv

    expect_render(
        "code file, single line, RIGHT",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "src/payments.ts:42", "--side", "RIGHT"],
        anchor_fragment,
    )
    expect_render(
        "side defaults to RIGHT",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "src/payments.ts:42"],
        anchor_fragment,
    )
    expect_render(
        "Markdown file line carries ?plain=1",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "README.md:14"],
        f"[`README.md:14`]({base}/README.md?plain=1#L14)",
    )
    expect_render(
        "range uses L<start>-L<end>",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "src/order.ts:47-52"],
        f"[`src/order.ts:47-52`]({base}/src/order.ts?plain=1#L47-L52)",
    )
    expect_render(
        "LEFT renders a code span",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "src/payments.ts:42", "--side", "LEFT"],
        "`src/payments.ts:42`",
    )
    expect_render(
        "file anchor carries no fragment",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "docs/ops.md"],
        f"[`docs/ops.md`]({base}/docs/ops.md)",
    )
    expect_render(
        "distinct fix renders its own fragment",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "src/retry-policy.ts:18"],
        fix_fragment,
    )
    if anchor_fragment == fix_fragment:
        failures.append("distinct fix: fix fragment equals the anchor fragment")
    expect_render(
        "spaces are percent-encoded once",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "docs/my file.md:3"],
        f"[`docs/my file.md:3`]({base}/docs/my%20file.md?plain=1#L3)",
    )
    expect_render(
        "literal percent is encoded once",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "docs/100%.md:7"],
        f"[`docs/100%.md:7`]({base}/docs/100%25.md?plain=1#L7)",
    )
    expect_render(
        "parentheses and brackets are encoded",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "src/a(1)[2].ts:5"],
        f"[`src/a(1)[2].ts:5`]({base}/src/a%281%29%5B2%5D.ts?plain=1#L5)",
    )
    expect_render(
        "path-borne query and fragment are encoded",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "src/a#b?c.ts:4"],
        f"[`src/a#b?c.ts:4`]({base}/src/a%23b%3Fc.ts?plain=1#L4)",
    )
    expect_render(
        "old path renders a code span",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "src/new-name.ts:9", "--old-path", "src/old-name.ts"],
        "`src/new-name.ts:9`",
    )
    expect_check(
        "check accepts the exact fragment",
        check_argv("src/payments.ts:42", anchor_fragment),
    )
    stdin_fragment = io.StringIO(anchor_fragment + "\n")
    saved_stdin, sys.stdin = sys.stdin, stdin_fragment
    try:
        expect_check(
            "check reads the fragment from stdin",
            check_argv("src/payments.ts:42", "-"),
        )
    finally:
        sys.stdin = saved_stdin

    expect_violation(
        "wrong repository fails the check",
        check_argv(
            "src/payments.ts:42",
            "[`src/payments.ts:42`](https://github.com/other/repo/blob/"
            + head
            + "/src/payments.ts?plain=1#L42)",
        ),
    )
    expect_violation(
        "wrong path fails the check",
        check_argv("src/payments.ts:42", f"[`src/payments.ts:42`]({base}/src/other.ts?plain=1#L42)"),
    )
    expect_violation(
        "wrong revision fails the check",
        check_argv(
            "src/payments.ts:42",
            f"[`src/payments.ts:42`]({repo}/blob/{other_sha}/src/payments.ts?plain=1#L42)",
        ),
    )
    expect_violation(
        "wrong visible text fails the check",
        check_argv("src/payments.ts:42", f"[`src/payments.ts:43`]({base}/src/payments.ts?plain=1#L42)"),
    )
    expect_violation(
        "missing ?plain=1 fails the check",
        check_argv("src/payments.ts:42", f"[`src/payments.ts:42`]({base}/src/payments.ts#L42)"),
    )
    expect_violation(
        "branch name in the revision slot fails render",
        ["render", "--repo-url", repo, "--revision", "main", "--coordinate", "src/payments.ts:42"],
    )
    expect_violation(
        "branch name in the revision slot fails the check",
        check_argv(
            "src/payments.ts:42",
            f"[`src/payments.ts:42`]({repo}/blob/main/src/payments.ts?plain=1#L42)",
        ),
    )
    expect_violation(
        "merge-base SHA in the revision slot fails the check",
        check_argv(
            "src/payments.ts:42",
            f"[`src/payments.ts:42`]({repo}/blob/{merge_base}/src/payments.ts?plain=1#L42)",
        ),
    )
    expect_violation(
        "double encoding fails the check",
        check_argv("docs/100%.md:7", f"[`docs/100%.md:7`]({base}/docs/100%2525.md?plain=1#L7)"),
    )
    expect_violation(
        "linked LEFT anchor fails the check",
        check_argv(
            "src/payments.ts:42",
            anchor_fragment,
            side="LEFT",
        ),
    )
    expect_violation(
        "unencoded path injection fails the check",
        check_argv("a.md?x=1:9", f"[`a.md?x=1:9`]({base}/a.md?x=1?plain=1#L9)"),
    )
    expect_violation(
        "Markdown-link injection through a path fails the check",
        check_argv(
            "src/a](https://evil.example)b.ts:5",
            "[`src/a](https://evil.example)b.ts:5`]"
            f"({base}/src/a](https://evil.example)b.ts?plain=1#L5)",
        ),
    )
    expect_violation(
        "backtick in the coordinate fails render",
        ["render", "--repo-url", repo, "--revision", head, "--coordinate", "src/a`b.ts:1"],
    )

    for failure in failures:
        print(f"FAIL {failure}")
    print(f"self-test: {cases - len(failures)}/{cases} cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
