#!/usr/bin/env python3
"""Select, bind, and run one documented shell block.

Usage: python3 scripts/run_block.py <reference> --marker <string> -- name=value...
Input: a UTF-8 Markdown reference with one matching ``sh`` fence and one
placeholder-assignment line in that fence.
Exit 0-255: the selected block's status; 2: a launcher argument, input, or
execution failure, reported on stderr with a ``run_block:`` prefix.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys
import tempfile


FENCE = re.compile(r"```sh\n(.*?)```", re.DOTALL)
ASSIGNMENT = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")
PLACEHOLDER = re.compile(r"<([^<>]+)>")


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        fail(message)


def fail(message: str) -> None:
    print(f"run_block: {message}", file=sys.stderr)
    raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = Parser(add_help=True)
    parser.add_argument("reference")
    parser.add_argument("--marker", required=True)
    raw = sys.argv[1:]
    try:
        separator = raw.index("--")
    except ValueError:
        if "-h" in raw or "--help" in raw:
            return parser.parse_args(raw)
        fail("bindings must follow --")
    args = parser.parse_args(raw[:separator])
    args.bindings = raw[separator + 1 :]
    return args


def select(reference: Path, marker: str) -> str:
    try:
        text = reference.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        fail(f"cannot read {reference}: {error}")
    matches = [body for body in FENCE.findall(text) if marker in body]
    if len(matches) != 1:
        fail(f"{reference}: marker {marker!r} matched {len(matches)} sh fences")
    return matches[0]


def binding_values(raw: list[str]) -> tuple[list[str], list[str]]:
    names, values = [], []
    for item in raw:
        if "=" not in item:
            fail(f"binding {item!r} is not name=value")
        name, value = item.split("=", 1)
        if not name:
            fail(f"binding {item!r} has an empty name")
        if name in names:
            fail(f"binding name {name!r} was given more than once")
        names.append(name)
        values.append(value)
    return names, values


def bind(block: str, names: list[str]) -> str:
    candidates: list[tuple[int, list[tuple[str, str]], str]] = []
    lines = block.splitlines(keepends=True)
    for index, line in enumerate(lines):
        content = line.rstrip("\r\n")
        tokens = content.split()
        assignments = [ASSIGNMENT.fullmatch(token) for token in tokens]
        if tokens and all(assignments):
            pairs = [(match.group(1), match.group(2)) for match in assignments if match is not None]
            if any(PLACEHOLDER.fullmatch(value) for _, value in pairs):
                candidates.append((index, pairs, line[len(content) :]))
    if len(candidates) != 1:
        fail(f"selected block has {len(candidates)} placeholder assignment lines")

    index, pairs, ending = candidates[0]
    placeholders = [PLACEHOLDER.fullmatch(value).group(1) for _, value in pairs if PLACEHOLDER.fullmatch(value)]
    if len(set(placeholders)) != len(placeholders):
        fail("placeholder names on the assignment line are not unique")
    missing = sorted(set(placeholders) - set(names))
    extra = sorted(set(names) - set(placeholders))
    if missing or extra:
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("extra " + ", ".join(extra))
        fail("binding names do not match placeholders: " + "; ".join(details))

    positions = {name: position for position, name in enumerate(names, 1)}
    bound = []
    for variable, value in pairs:
        placeholder = PLACEHOLDER.fullmatch(value)
        bound.append(f"{variable}=${positions[placeholder.group(1)]}" if placeholder else f"{variable}={value}")
    lines[index] = " ".join(bound) + ending
    return "".join(lines)


def main() -> int:
    args = parse_args()
    reference = Path(args.reference)
    names, values = binding_values(args.bindings)
    program = bind(select(reference, args.marker), names)
    try:
        with tempfile.TemporaryDirectory(prefix="run-block-") as directory:
            script = Path(directory) / "block.sh"
            script.write_text(program, encoding="utf-8")
            return subprocess.run(["sh", str(script), *values]).returncode
    except OSError as error:
        fail(f"cannot execute selected block: {error}")


if __name__ == "__main__":
    raise SystemExit(main())
