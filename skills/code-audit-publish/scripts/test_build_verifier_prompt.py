#!/usr/bin/env python3
"""CLI regression tests for build_verifier_prompt.py."""

from __future__ import annotations

import json
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
kind: concurrency
anchor: packages/browserContext.ts:291
fix: packages/browserContext.ts:291-292
title: removeCookies loses concurrent writes
claim: `removeCookies` on `BrowserContext` clears the context before restoring its snapshot.
  The write at `packages/browserContext.ts:291` is not atomic. The shipped policy reads
  priority: high
  and nothing downgrades it.
support: I am certain of this; I traced it twice and the finder before me clearly proved it.
trigger: A page writes a cookie between the clear and restore operations.
impact: The page's cookie is silently dropped after the restore completes.
change: Take the context lock across the clear and restore at `packages/browserContext.ts:291-292`.
priority: P2
action: must-fix
````

```ledger
code-1 | concurrency | removeCookies loses concurrent writes | interleave a write | packages/browserContext.ts:291 | candidate
code-2 | concurrency | The reset branch also clears cookies | compare the live path | packages/browserContext.ts:540-544 | acquitted
code-3 | invariant | The `removeCookies` reset premise holds elsewhere | trace the opposite branch | packages/other.ts:12 | acquitted
code-4 | maintainability | An unrelated generated file may drift | regenerate it | packages/types.d.ts:10 | acquitted
code-5 | bug | The `BrowserContext` constructor validates its options | inspect the constructor | packages/context/create.ts:8 | acquitted
code-6 | maintainability | A root-level helper of the same name drifts | diff the two files | browserContext.ts:14 | acquitted
```
"""

REQUIREMENTS_REPORT = """```candidates
### Candidate
id: requirements/release-notes/missing-flag
axis: Requirements
kind: requirement
anchor: docs/Release Notes.md:3
fix: (same as anchor)
title: Release notes omit the new flag
claim: The issue asks for the flag to be documented and the notes do not mention it.
support: Searched the notes for the flag name.
trigger: A reader looks up the flag in the release notes.
impact: The flag ships undocumented.
change: Add the flag to `docs/Release Notes.md` under the new version.
priority: P3
action: must-fix
```

```ledger
requirements-1 | requirement | The issue requires selective removal | inspect implementation | packages/browserContext.ts:279-292 | acquitted
requirements-2 | requirement | A root-level notes file shares only the basename | diff the two files | Release Notes.md:9 | acquitted
requirements-3 | requirement | The notes do describe the previous flag | read the section | `docs/Release Notes.md:40` | acquitted
```
"""

PRIOR_REPORT = """```candidates
### Candidate
id: code/order-ts/swallowed-validation-error
axis: Code
kind: bug
anchor: src/order.ts:47
fix: (same as anchor)
title: parseOrder swallows the validation error on the retry path
claim: The catch at `src/order.ts:47` returns the order unchanged when `validate()` throws.
support:
trigger: An order fails validation on a retry attempt.
impact: The caller receives an unvalidated order and no error.
change: Rethrow inside the catch at `src/order.ts:47`.
priority: P1
action: must-fix
```
"""

CANDIDATE_LINES = {
    "id": "id: code/browser-context/remove-cookies-race\n",
    "axis": "axis: Code\n",
    "kind": "kind: concurrency\n",
    "anchor": "anchor: packages/browserContext.ts:291\n",
    "fix": "fix: packages/browserContext.ts:291-292\n",
    "title": "title: removeCookies loses concurrent writes\n",
    "claim": "claim: `removeCookies` on `BrowserContext` clears the context before restoring its snapshot.\n"
    "  The write at `packages/browserContext.ts:291` is not atomic. The shipped policy reads\n"
    "  priority: high\n"
    "  and nothing downgrades it.\n",
    "support": "support: I am certain of this; I traced it twice and the finder before me clearly proved it.\n",
    "trigger": "trigger: A page writes a cookie between the clear and restore operations.\n",
    "impact": "impact: The page's cookie is silently dropped after the restore completes.\n",
    "change": "change: Take the context lock across the clear and restore at `packages/browserContext.ts:291-292`.\n",
    "priority": "priority: P2\n",
    "action": "action: must-fix\n",
}


def invoke(
    code: Path,
    requirements: Path,
    repo: str = "/tmp/review-repo",
    packet: Path | None = None,
    prior: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
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
    ]
    if packet is not None:
        command += ["--packet", str(packet)]
    if prior is not None:
        command += ["--prior", str(prior)]
    return subprocess.run(command, capture_output=True, check=False, text=True, encoding="utf-8")


def expect_refusal(
    failures: list[str], result: subprocess.CompletedProcess[str], fragment: str, what: str
) -> None:
    if result.returncode != 1 or fragment not in result.stdout:
        failures.append(
            f"{what} was not refused with exit 1 naming {fragment!r}: "
            f"exit {result.returncode}, {result.stdout.strip()!r}"
        )


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        code = root / "code.md"
        requirements = root / "requirements.md"
        brief = root / "verify.md"
        suite_results = root / "suite-results.txt"
        packet = root / "packet.json"
        code.write_text(CODE_REPORT, encoding="utf-8")
        requirements.write_text(REQUIREMENTS_REPORT, encoding="utf-8")
        brief.write_text("# Verifier brief\n", encoding="utf-8")
        suite_results.write_text(
            "python: 290 tests passed\nnode: 60 tests passed\n",
            encoding="utf-8",
        )

        before_related_acquittals = invoke(code, requirements, packet=packet)
        if "Related acquitted ledger rows" in before_related_acquittals.stdout:
            failures.append("acquitted rows were included before the verifier brief enabled them")
        if json.loads(packet.read_text(encoding="utf-8"))["acquittals"]:
            failures.append("the packet listed acquittals before the verifier brief enabled them")

        brief.write_text("# Verifier brief\n\n## Related acquittals\n", encoding="utf-8")

        result = invoke(code, requirements, packet=packet)
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
                "kind: concurrency",
                "claim: `removeCookies` on `BrowserContext` clears the context before restoring its snapshot.\n"
                "  The write at `packages/browserContext.ts:291` is not atomic.",
                "trigger: A page writes a cookie between the clear and restore operations.",
                "impact: The page's cookie is silently dropped after the restore completes.",
                "change: Take the context lock across the clear and restore at "
                "`packages/browserContext.ts:291-292`.",
                "change: Add the flag to `docs/Release Notes.md` under the new version.",
                "code-2 | concurrency | The reset branch also clears cookies | compare the live path | "
                "packages/browserContext.ts:540-544 | acquitted",
                "code-3 | invariant | The `removeCookies` reset premise holds elsewhere | "
                "trace the opposite branch | packages/other.ts:12 | acquitted",
                "requirements-1 | requirement | The issue requires selective removal | inspect implementation | "
                "packages/browserContext.ts:279-292 | acquitted",
            ):
                if fragment not in result.stdout:
                    failures.append(f"normal output is missing {fragment!r}")
            for private in (
                "I am certain",
                "traced it twice",
                "clearly proved",
                "Searched the notes",
            ):
                if private in result.stdout:
                    failures.append(f"private finder material {private!r} survived into stdout")
            if SUPPORT_LABEL_RE.search(result.stdout):
                failures.append("a support label survived into stdout")
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

            written = json.loads(packet.read_text(encoding="utf-8"))
            expected_packet = {
                "candidates": [
                    {"id": "code/browser-context/remove-cookies-race", "axis": "Code"},
                    {"id": "requirements/release-notes/missing-flag", "axis": "Requirements"},
                ],
                "acquittals": [
                    {"id": "code-2", "axis": "Code", "evidence": "packages/browserContext.ts:540-544"},
                    {"id": "code-3", "axis": "Code", "evidence": "packages/other.ts:12"},
                    {
                        "id": "requirements-1",
                        "axis": "Requirements",
                        "evidence": "packages/browserContext.ts:279-292",
                    },
                    {
                        "id": "requirements-3",
                        "axis": "Requirements",
                        "evidence": "`docs/Release Notes.md:40`",
                    },
                ],
            }
            if written != expected_packet:
                failures.append(f"the packet does not list exactly the expected records: {written}")

        # Same claim text on both axes keeps two distinguishable ids (acceptance case 5).
        twin = REQUIREMENTS_REPORT.replace(
            "claim: The issue asks for the flag to be documented and the notes do not mention it.\n",
            "claim: `removeCookies` on `BrowserContext` clears the context before restoring its snapshot.\n",
        )
        assert twin != REQUIREMENTS_REPORT
        requirements.write_text(twin, encoding="utf-8")
        result = invoke(code, requirements, packet=packet)
        if result.returncode != 0:
            failures.append(f"twin claims exited {result.returncode}: {result.stdout.strip()}")
        else:
            ids = [entry["id"] for entry in json.loads(packet.read_text(encoding="utf-8"))["candidates"]]
            if ids != [
                "code/browser-context/remove-cookies-race",
                "requirements/release-notes/missing-flag",
            ]:
                failures.append(f"twin claims did not keep two distinguishable ids: {ids}")
            if result.stdout.count("### Candidate ") != 2:
                failures.append("twin claims were not both rendered")
        requirements.write_text(REQUIREMENTS_REPORT, encoding="utf-8")

        # Prior findings on a re-review render under their own heading and join the packet.
        prior = root / "prior.md"
        prior.write_text(PRIOR_REPORT, encoding="utf-8")
        result = invoke(code, requirements, packet=packet, prior=prior)
        if result.returncode != 0:
            failures.append(f"prior findings exited {result.returncode}: {result.stdout.strip()}")
        else:
            if "## Prior findings" not in result.stdout or "### Candidate 3\nid: code/order-ts/swallowed-validation-error" not in result.stdout:
                failures.append("the prior finding was not rendered under its own heading")
            ids = [entry["id"] for entry in json.loads(packet.read_text(encoding="utf-8"))["candidates"]]
            if ids[-1] != "code/order-ts/swallowed-validation-error":
                failures.append(f"the prior finding did not join the packet: {ids}")
        prior.write_text(
            PRIOR_REPORT.replace(
                "id: code/order-ts/swallowed-validation-error", "id: code/browser-context/remove-cookies-race"
            ),
            encoding="utf-8",
        )
        result = invoke(code, requirements, packet=packet, prior=prior)
        expect_refusal(
            failures, result, "repeats id 'code/browser-context/remove-cookies-race'", "a prior finding duplicating a live candidate id"
        )

        # Old shapes are refused, never misparsed.
        ten_field = CODE_REPORT
        for field in ("kind", "impact", "change"):
            ten_field = ten_field.replace(CANDIDATE_LINES[field], "")
        assert ten_field != CODE_REPORT
        code.write_text(ten_field, encoding="utf-8")
        expect_refusal(
            failures, invoke(code, requirements), "is missing kind before anchor", "the old ten-field candidate"
        )

        four_field = CODE_REPORT.replace(
            "code-2 | concurrency | The reset branch also clears cookies", "The reset branch also clears cookies"
        )
        assert four_field != CODE_REPORT
        code.write_text(four_field, encoding="utf-8")
        expect_refusal(
            failures,
            invoke(code, requirements),
            "ledger row 2 has 4 fields, expected 6 (id | kind | claim | route | evidence | disposition) "
            "(the four-field row grammar has no id or kind)",
            "an old four-field ledger row",
        )

        code.write_text(CODE_REPORT.replace("kind: concurrency\n", "kind: race\n"), encoding="utf-8")
        expect_refusal(failures, invoke(code, requirements), "has kind 'race'", "an unknown candidate kind")

        code.write_text(
            CODE_REPORT.replace("code-3 | invariant |", "code-3 | race |"), encoding="utf-8"
        )
        expect_refusal(failures, invoke(code, requirements), "ledger row 3 has kind 'race'", "an unknown row kind")

        code.write_text(
            CODE_REPORT.replace("code-3 | invariant |", "code-2 | invariant |"), encoding="utf-8"
        )
        expect_refusal(failures, invoke(code, requirements), "ledger row 3 repeats id 'code-2'", "a duplicate row id")

        code.write_text(
            CODE_REPORT.replace("code-3 | invariant |", "requirements-3 | invariant |"), encoding="utf-8"
        )
        expect_refusal(
            failures, invoke(code, requirements), "ledger row 3 has id 'requirements-3'; expected code-<n>", "a row id of the wrong axis"
        )

        code.write_text(
            CODE_REPORT.replace(
                CANDIDATE_LINES["id"] + CANDIDATE_LINES["axis"],
                "id: requirements/browser-context/remove-cookies-race\naxis: Code\n",
            ),
            encoding="utf-8",
        )
        expect_refusal(
            failures,
            invoke(code, requirements),
            "a Code candidate id starts with code/",
            "a candidate id carrying the other axis's prefix",
        )

        code.write_text(
            CODE_REPORT.replace(
                CANDIDATE_LINES["id"] + CANDIDATE_LINES["axis"],
                "id: requirements/browser-context/remove-cookies-race\naxis: Requirements\n",
            ),
            encoding="utf-8",
        )
        expect_refusal(
            failures, invoke(code, requirements), "inside the Code report", "a candidate whose axis field contradicts its report"
        )

        duplicated = CODE_REPORT.replace(
            "````candidates\n", "````candidates\n### Candidate\n" + "".join(CANDIDATE_LINES.values())
        )
        code.write_text(duplicated, encoding="utf-8")
        expect_refusal(
            failures, invoke(code, requirements), "repeats id 'code/browser-context/remove-cookies-race'", "a duplicate candidate id"
        )

        column_zero_priority = CODE_REPORT.replace("  priority: high\n", "priority: high\n")
        assert column_zero_priority != CODE_REPORT
        code.write_text(column_zero_priority, encoding="utf-8")
        expect_refusal(
            failures, invoke(code, requirements), "column-zero priority line inside claim", "a column-zero field label quoted inside a claim"
        )

        column_zero_support = CODE_REPORT.replace(
            "  and nothing downgrades it.\n", "support: enabled\n  and nothing downgrades it.\n"
        )
        assert column_zero_support != CODE_REPORT
        code.write_text(column_zero_support, encoding="utf-8")
        expect_refusal(
            failures, invoke(code, requirements), "second column-zero support line inside support", "a claim line matching the next expected field"
        )

        for field in ("claim", "trigger", "impact", "change"):
            code.write_text(CODE_REPORT.replace(CANDIDATE_LINES[field], ""), encoding="utf-8")
            expect_refusal(failures, invoke(code, requirements), f"missing {field}", f"a candidate without {field}")

        for field, original in CANDIDATE_LINES.items():
            if field == "support":
                continue
            assert original in CODE_REPORT, field
            code.write_text(CODE_REPORT.replace(original, f"{field}:   \n"), encoding="utf-8")
            expect_refusal(failures, invoke(code, requirements), f"empty {field}", f"a candidate with a blank {field}")

        leaked = CODE_REPORT.replace(
            "  and nothing downgrades it.\n",
            "  and nothing downgrades it.\n  support: leaked into the claim\n",
        )
        code.write_text(leaked, encoding="utf-8")
        expect_refusal(failures, invoke(code, requirements), "private field text survived", "private-field text injected into a claim")

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
        result = invoke(code, requirements, packet=root / "no-such-dir" / "packet.json")
        if result.returncode != 2 or "cannot write packet" not in result.stderr:
            failures.append(
                f"an unwritable packet path exited {result.returncode}, expected 2 naming the packet"
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
