#!/usr/bin/env python3
"""Check the audit publication record's deleted-file CLI contract.

Usage: python3 scripts/test_link_coordinate.py
Inputs: pinned publication records; no repository or forge access.
Exit 0: all checks pass; exit 1: a check fails; exit 2: CLI cannot run.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).with_name("link_coordinate.py")
HEAD = "c0b089b5c39b2df6a0e26b319f026ede50938d7b"
MERGE_BASE = "2f06662c0f546404c2c72f449ea6e3cf4dd74d75"
PATH = ".claude/agents/v5b-primary-effort-medium.md"
REPO = "https://github.com/kamui/skills"


def invoke(command: str, record: dict, *extra: str) -> subprocess.CompletedProcess:
    args = [sys.executable, str(SCRIPT), command, "--repo-url", REPO,
            "--revision", HEAD, "--coordinate", record["coordinate"]]
    for field, option in [("side", "--side"), ("merge_base", "--merge-base"), ("old_path", "--old-path")]:
        if field in record:
            args += [option, record[field]]
    return subprocess.run(args + list(extra), capture_output=True, encoding="utf-8", check=False)


def main() -> int:
    manifest = {"status": "D", "path": PATH}
    record = {"coordinate": manifest["path"], "side": "LEFT", "merge_base": MERGE_BASE}
    deleted = f"[`{PATH}`]({REPO}/blob/{MERGE_BASE}/{PATH})"
    ordinary = f"[`{PATH}`]({REPO}/blob/{HEAD}/{PATH})"
    cases = [
        ("PR #118 deleted whole file", record, deleted),
        ("ordinary RIGHT file", dict(record, side="RIGHT"), ordinary),
        ("legacy file", {"coordinate": PATH}, ordinary),
        ("LEFT missing merge-base", {"coordinate": PATH, "side": "LEFT"}, f"`{PATH}`"),
        ("unavailable pre-image", dict(record, side="UNKNOWN"), f"`{PATH}`"),
        ("ambiguous pre-image", dict(record, side="UNKNOWN", coordinate="reported.md"), "`reported.md`"),
        ("rename remains unlinked", dict(record, old_path="other.md"), f"`{PATH}`"),
        ("LEFT line remains unlinked", dict(record, coordinate=PATH + ":1"), f"`{PATH}:1`"),
        ("RIGHT line unchanged", dict(record, side="RIGHT", coordinate=PATH + ":1"),
         f"[`{PATH}:1`]({REPO}/blob/{HEAD}/{PATH}?plain=1#L1)"),
    ]
    for name, value, fragment in cases:
        result = invoke("render", value)
        assert result.returncode == 0 and result.stdout == fragment + "\n", (name, result)
        result = invoke("check", value, "--fragment", fragment)
        assert result.returncode == 0 and not result.stdout, (name, result)
        print(f"ok {name}: render/check")
    for name, value in [
        ("malformed merge-base", dict(record, merge_base="main")),
        ("abbreviated merge-base", dict(record, merge_base=MERGE_BASE[:8])),
        ("UNKNOWN line", dict(record, side="UNKNOWN", coordinate=PATH + ":1")),
    ]:
        for command, extra in [("render", ()), ("check", ("--fragment", deleted))]:
            result = invoke(command, value, *extra)
            assert result.returncode == 1 and "/blob/" not in result.stdout, (name, result)
        print(f"ok {name}: refused")
    for fragment in [ordinary, deleted.replace(MERGE_BASE, "b" * 40)]:
        result = invoke("check", record, "--fragment", fragment)
        assert result.returncode == 1, result
    result = invoke("check", dict(record, side="UNKNOWN"), "--fragment", ordinary)
    assert result.returncode == 1, result
    print("ok head/arbitrary revision/unknown linked fragments: rejected")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"FAIL {error}")
        raise SystemExit(1)
    except OSError as error:
        print(f"test_link_coordinate: cannot run {SCRIPT}: {error}", file=sys.stderr)
        raise SystemExit(2)
