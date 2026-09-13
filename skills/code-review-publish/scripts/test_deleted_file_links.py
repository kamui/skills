#!/usr/bin/env python3
"""Exercise deleted-file payload rendering, validation and batch transport.

Usage: python3 scripts/test_deleted_file_links.py
Inputs: local fixture payloads; no repository or forge access.
Exit 0: all checks pass; exit 1: a check fails; exit 2: CLI cannot run.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

from validate_review import WORKFLOW

SCRIPT = Path(__file__).with_name("validate_review.py")
HEAD = "c0b089b5c39b2df6a0e26b319f026ede50938d7b"
MERGE_BASE = "2f06662c0f546404c2c72f449ea6e3cf4dd74d75"
PATH = ".claude/agents/v5b-primary-effort-medium.md"
REPO = "https://github.com/kamui/skills"


def invoke(payload: dict, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], input=json.dumps(payload),
        capture_output=True, encoding="utf-8", check=False,
    )


def payload(anchor: dict, fragment: str) -> dict:
    trailer = (
        f"<!-- review-run head={HEAD} base-ref=main base-sha={MERGE_BASE} "
        f"merge-base={MERGE_BASE} workflow={WORKFLOW} context={'a' * 64} "
        "issues=kamui/skills#84 coverage=complete -->"
    )
    question = {
        "type": "question", "id": "effort-profile/deletion",
        "anchor": anchor,
        "markdown": (
            "**[Question] Must existing users retain the effort profile?**\n\n"
            "**Evidence:** PR #118 removes the effort profile. The available evidence "
            "does not establish whether users still depend on this profile.\n\n"
            "**Why it matters:** The answer determines whether this deletion breaks "
            "the supported setup at release.\n\n"
            "**Change no code for this.** The maintainer can confirm whether this "
            "profile remains part of the supported setup."
        ),
        "trailer": f"<!-- question id=effort-profile/deletion head={HEAD} action=question -->",
    }
    body = (
        "**Needs Information** — 1 open question.\n\n"
        "**Intent:** Remove obsolete effort profiles.\n\n"
        "**Issue fit:** The linked issue requests a working deleted-file reference.\n\n"
        "**Coverage:** Complete fixture inspection.\n\n"
        f"**Reviewed:** `{HEAD}` against merge-base `{MERGE_BASE}`.\n\n"
        f"## Open questions\n\n{question['markdown']}\n\n{fragment}\n\n"
        f"{question['trailer']}\n\n{trailer}"
    )
    return {"summary": {"body": body, "trailer": trailer, "repository_url": REPO},
            "items": [question]}


def main() -> int:
    # This D record is the pinned merge-base manifest entry for PR #118.
    manifest = {"status": "D", "path": PATH, "old_path": None}
    anchor = {"type": "file", "path": manifest["path"],
              "side": "LEFT" if manifest["status"] == "D" else "RIGHT"}
    deleted = f"anchor [`{PATH}`]({REPO}/blob/{MERGE_BASE}/{PATH}) (file)"
    ordinary = f"anchor [`{PATH}`]({REPO}/blob/{HEAD}/{PATH}) (file)"
    unknown = f"anchor `{PATH}` (file)"
    cases = [
        ("PR #118 deleted file", anchor, deleted),
        ("legacy file anchor", {"type": "file", "path": PATH}, ordinary),
        ("ordinary RIGHT file", dict(anchor, side="RIGHT"), ordinary),
        ("unavailable pre-image", dict(anchor, side="UNKNOWN"), unknown),
        ("ambiguous pre-image", {"type": "file", "path": "reported/path.md", "side": "UNKNOWN"},
         "anchor `reported/path.md` (file)"),
    ]
    for name, coordinate, fragment in cases:
        value = payload(coordinate, fragment)
        result = invoke(value, "--render")
        assert result.returncode == 0 and result.stdout == fragment + "\n", (name, result)
        result = invoke(value)
        assert result.returncode == 0, (name, result.stdout)
        result = invoke(value, "--emit-batch")
        assert result.returncode == 0, (name, result.stdout)
        batch = json.loads(result.stdout)
        assert batch["commit_id"] == HEAD and batch["comments"] == [], (name, batch)
        assert batch["body"] == value["summary"]["body"], name
        print(f"ok {name}: render/validate/emit-batch")

    for name, coordinate in [
        ("malformed side", dict(anchor, side="BOTH")),
        ("null side", dict(anchor, side=None)),
        ("arbitrary revision", dict(anchor, revision="b" * 40)),
        ("ambiguous path array", dict(anchor, path=[PATH, "other.md"])),
    ]:
        for mode in ((), ("--render",), ("--emit-batch",)):
            result = invoke(payload(coordinate, deleted), *mode)
            assert result.returncode == 1 and "anchor-shape" in result.stdout, (name, mode, result)
            assert f"{REPO}/blob/" not in result.stdout, (name, mode, result.stdout)
        print(f"ok {name}: refused in all modes")

    for name, value in [
        ("deleted linked at head", payload(anchor, ordinary)),
        ("unknown linked at head", payload(dict(anchor, side="UNKNOWN"), ordinary)),
        ("arbitrary linked revision", payload(anchor, deleted.replace(MERGE_BASE, "b" * 40))),
    ]:
        for mode in ((), ("--emit-batch",)):
            result = invoke(value, *mode)
            assert result.returncode == 1 and "summary-reference" in result.stdout, (name, result)
        print(f"ok {name}: body rejected")

    missing = copy.deepcopy(payload(anchor, deleted))
    for field in ("body", "trailer"):
        missing["summary"][field] = missing["summary"][field].replace(f"merge-base={MERGE_BASE} ", "")
    result = invoke(missing, "--render")
    assert result.returncode == 1 and "trailer-sha" in result.stdout, result
    # A run still needs its pinned identity; a missing per-file path uses UNKNOWN instead.
    print("ok missing pinned merge-base: render refused")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"FAIL {error}")
        raise SystemExit(1)
    except OSError as error:
        print(f"test_deleted_file_links: cannot run {SCRIPT}: {error}", file=sys.stderr)
        raise SystemExit(2)
