#!/usr/bin/env python3
"""CLI regression tests for build_verifier_prompt.py."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "build_verifier_prompt.py"
SUPPORT_LABEL_RE = re.compile(
    r"^[ \t]*(?:-\s+)?(?:\*\*)?support(?:\*\*)?:",
    re.IGNORECASE | re.MULTILINE,
)

CODE_REPORT = """Finder prose is outside the machine-readable blocks.

````candidates
### Candidate
id: code/browser-context/remove-cookies-race
axis: Code
anchor: packages/browserContext.ts:291
fix: packages/browserContext.ts:291-292
title: removeCookies loses concurrent writes
claim: `removeCookies` on `BrowserContext` clears the context before restoring its snapshot.
  The write at `packages/browserContext.ts:291` is not atomic. The shipped policy reads
  priority: high
  and nothing downgrades it.
support: private finder process and uncertainty
trigger: A page writes a cookie between the clear and restore operations.
priority: P2
action: must-fix
````

```ledger
The reset branch also clears cookies | compare the live path | packages/browserContext.ts:540-544 | acquitted
The `removeCookies` reset premise holds elsewhere | trace the opposite branch | packages/other.ts:12 | acquitted
An unrelated generated file may drift | regenerate it | packages/types.d.ts:10 | acquitted
The `BrowserContext` constructor validates its options | inspect the constructor | packages/context/create.ts:8 | acquitted
A root-level helper of the same name drifts | diff the two files | browserContext.ts:14 | acquitted
```
"""

REQUIREMENTS_REPORT = """```candidates
### Candidate
id: requirements/release-notes/missing-flag
axis: Requirements
anchor: docs/Release Notes.md:3
fix: (same as anchor)
title: Release notes omit the new flag
claim: The issue asks for the flag to be documented and the notes do not mention it.
support: Searched the notes for the flag name.
trigger: A reader looks up the flag in the release notes.
priority: P3
action: must-fix
```

```ledger
The issue requires selective removal | inspect implementation | packages/browserContext.ts:279-292 | acquitted
A root-level notes file shares only the basename | diff the two files | Release Notes.md:9 | acquitted
The notes do describe the previous flag | read the section | `docs/Release Notes.md:40` | acquitted
```
"""


def invoke(
    code: Path, requirements: Path, repo: str = "/tmp/review-repo"
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--brief",
            str(code.parent / "verify.md"),
            "--repo",
            repo,
            "--base-sha",
            "a" * 40,
            "--head-sha",
            "b" * 40,
            "--merge-base",
            "c" * 40,
            "--code",
            str(code),
            "--requirements",
            str(requirements),
            "--suite-results",
            str(code.parent / "suite-results.txt"),
        ],
        capture_output=True,
        check=False,
        text=True,
    )


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        code = root / "code.md"
        requirements = root / "requirements.md"
        brief = root / "verify.md"
        suite_results = root / "suite-results.txt"
        code.write_text(CODE_REPORT, encoding="utf-8")
        requirements.write_text(REQUIREMENTS_REPORT, encoding="utf-8")
        brief.write_text("# Verifier brief\n", encoding="utf-8")
        suite_results.write_text(
            "python: 290 tests passed\nnode: 60 tests passed\n",
            encoding="utf-8",
        )

        before_related_acquittals = invoke(code, requirements)
        if "Related acquitted ledger rows" in before_related_acquittals.stdout:
            failures.append("acquitted rows were included before the verifier brief enabled them")

        brief.write_text("# Verifier brief\n\n## Related acquittals\n", encoding="utf-8")

        result = invoke(code, requirements)
        if result.returncode != 0:
            failures.append(f"normal invocation exited {result.returncode}: {result.stderr.strip()}")
        else:
            for fragment in (
                f"Verifier brief: `{brief}`",
                "Repository: `/tmp/review-repo`",
                f"- base SHA: `{'a' * 40}`",
                "## Test suite results",
                "python: 290 tests passed",
                "node: 60 tests passed",
                "id: code/browser-context/remove-cookies-race",
                "claim: `removeCookies` on `BrowserContext` clears the context before restoring its snapshot.\n"
                "  The write at `packages/browserContext.ts:291` is not atomic.",
                "trigger: A page writes a cookie between the clear and restore operations.",
                "The reset branch also clears cookies | compare the live path | "
                "packages/browserContext.ts:540-544 | acquitted",
                "The `removeCookies` reset premise holds elsewhere | trace the opposite branch | "
                "packages/other.ts:12 | acquitted",
                "The issue requires selective removal | inspect implementation | "
                "packages/browserContext.ts:279-292 | acquitted",
            ):
                if fragment not in result.stdout:
                    failures.append(f"normal output is missing {fragment!r}")
            if SUPPORT_LABEL_RE.search(result.stdout) or "private finder process" in result.stdout:
                failures.append("private finder material survived into stdout")
            if "unrelated generated file" in result.stdout:
                failures.append("unrelated acquitted row was sent to the verifier")
            if "constructor validates its options" in result.stdout:
                failures.append("a row sharing only a class name was treated as related")
            if "root-level helper of the same name" in result.stdout:
                failures.append("a row sharing only a path suffix was treated as related")
            if "shares only the basename" in result.stdout:
                failures.append(
                    "a row whose path shares only the basename after a space was treated as related"
                )
            if "notes do describe the previous flag" not in result.stdout:
                failures.append(
                    "a row citing the same file as a candidate, with a space in its path, was dropped"
                )
            if "  priority: high\n  and nothing downgrades it." not in result.stdout:
                failures.append("an indented field-like line inside the claim was not carried verbatim")
            if "priority: P2" not in result.stdout:
                failures.append("the candidate's own priority was lost to the claim's quoted line")

        column_zero_priority = CODE_REPORT.replace("  priority: high\n", "priority: high\n")
        assert column_zero_priority != CODE_REPORT
        code.write_text(column_zero_priority, encoding="utf-8")
        result = invoke(code, requirements)
        if result.returncode != 1 or "column-zero priority line inside claim" not in result.stdout:
            failures.append(
                "a column-zero field label quoted inside a claim was not refused with exit 1: "
                f"exit {result.returncode}, {result.stdout.strip()!r}"
            )

        column_zero_support = CODE_REPORT.replace(
            "  and nothing downgrades it.\n", "support: enabled\n  and nothing downgrades it.\n"
        )
        assert column_zero_support != CODE_REPORT
        code.write_text(column_zero_support, encoding="utf-8")
        result = invoke(code, requirements)
        if result.returncode != 1 or "second column-zero support line inside support" not in result.stdout:
            failures.append(
                "a claim line matching the next expected field was not refused with exit 1: "
                f"exit {result.returncode}, {result.stdout.strip()!r}"
            )

        missing_claim = CODE_REPORT.replace(
            "claim: `removeCookies` on `BrowserContext` clears the context before restoring its snapshot.\n"
            "  The write at `packages/browserContext.ts:291` is not atomic. The shipped policy reads\n"
            "  priority: high\n"
            "  and nothing downgrades it.\n",
            "",
        )
        code.write_text(missing_claim, encoding="utf-8")
        result = invoke(code, requirements)
        if result.returncode != 1 or "missing claim" not in result.stdout:
            failures.append("a candidate without claim was not refused with exit 1")

        missing_trigger = CODE_REPORT.replace(
            "trigger: A page writes a cookie between the clear and restore operations.\n",
            "",
        )
        code.write_text(missing_trigger, encoding="utf-8")
        result = invoke(code, requirements)
        if result.returncode != 1 or "missing trigger" not in result.stdout:
            failures.append("a candidate without trigger was not refused with exit 1")

        blank_values = {
            "id": "id: code/browser-context/remove-cookies-race\n",
            "axis": "axis: Code\n",
            "anchor": "anchor: packages/browserContext.ts:291\n",
            "fix": "fix: packages/browserContext.ts:291-292\n",
            "title": "title: removeCookies loses concurrent writes\n",
            "claim": "claim: `removeCookies` on `BrowserContext` clears the context before restoring its snapshot.\n"
            "  The write at `packages/browserContext.ts:291` is not atomic. The shipped policy reads\n"
            "  priority: high\n"
            "  and nothing downgrades it.\n",
            "trigger": "trigger: A page writes a cookie between the clear and restore operations.\n",
            "priority": "priority: P2\n",
            "action": "action: must-fix\n",
        }
        for field, original in blank_values.items():
            assert original in CODE_REPORT, field
            code.write_text(CODE_REPORT.replace(original, f"{field}:   \n"), encoding="utf-8")
            result = invoke(code, requirements)
            if result.returncode != 1 or f"empty {field}" not in result.stdout:
                failures.append(f"a candidate with a blank {field} was not refused with exit 1")

        leaked = CODE_REPORT.replace(
            "  and nothing downgrades it.\n",
            "  and nothing downgrades it.\n  support: leaked into the claim\n",
        )
        code.write_text(leaked, encoding="utf-8")
        result = invoke(code, requirements)
        if result.returncode != 1 or "private field text survived" not in result.stdout:
            failures.append("private-field text injected into a claim was not refused")

        wordy = CODE_REPORT.replace(
            "title: removeCookies loses concurrent writes\n",
            "title: removeCookies leaves unsupported writes that nothing supports\n",
        )
        code.write_text(wordy, encoding="utf-8")
        result = invoke(code, requirements, repo="/Users/x/Support/repo")
        if result.returncode != 0:
            failures.append(
                "a candidate whose prose contains the word support was refused: "
                f"exit {result.returncode}"
            )
        if "unsupported writes that nothing supports" not in result.stdout:
            failures.append("the prose containing the word support was dropped from the prompt")

        code.write_text(CODE_REPORT, encoding="utf-8")
        result = invoke(code, root / "missing.md")
        if result.returncode != 2 or "cannot read" not in result.stderr:
            failures.append(
                f"an unreadable report exited {result.returncode}, expected 2 naming the input"
            )

    for failure in failures:
        print(failure)
    if failures:
        print(f"test_build_verifier_prompt: {len(failures)} failure(s)")
        return 1
    print("test_build_verifier_prompt: all cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
