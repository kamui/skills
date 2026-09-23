#!/usr/bin/env python3
"""Measure runtime instructions, primary paths, and generated verifier briefs.

Usage: python3 scripts/test_instruction_budget.py
Counts UTF-8 bytes, including expanded help/examples on representative paths.
Evidence and code are excluded; example briefs also report their supplied records.
Raise a limit only with a dated DESIGN.md justification. Exit 0 within all limits,
1 over budget, 2 when an instruction or helper output cannot be read.
"""
from __future__ import annotations

import copy
from pathlib import Path
import subprocess
import sys

import build_verifier_prompt as builder

SKILL = Path(__file__).resolve().parent.parent
ALWAYS_LOADED = ("SKILL.md", "references/review-rubric.md", "references/rendering.md")
# Rounded ceilings above the accepted #332 layout, including actual helper output.
BUDGET = 26_000
LIMITS = {"runtime total": 92_000, "always loaded": BUDGET,
          "local primary": 67_000, "PR primary": 67_000,
          "verifier instructions": 20_000, "verifier example brief": 24_000}


def output(script, *args):
    return subprocess.run([sys.executable, str(SKILL / "scripts" / script), *args],
                          check=True, capture_output=True).stdout


def measurements():
    files = {"SKILL.md": (SKILL / "SKILL.md").read_bytes()}
    files.update({str(p.relative_to(SKILL)): p.read_bytes()
                  for p in sorted((SKILL / "references").glob("*.md"))})
    always = b"".join(files[name] for name in ALWAYS_LOADED)
    # First review, changed tests, supplied checks, and one ordinary verifier batch.
    common = always + b"".join(files["references/" + name] for name in (
        "changed-tests.md", "check-evidence.md", "verifier-handoff.md", "verifier-return.md"))
    common += output("review_context.py", "--help")
    common += output("context_fingerprint.py", "--example")
    common += output("build_verifier_prompt.py", "--example")
    values = {"runtime total": b"".join(files.values()), "always loaded": always}
    for name, target, profile in (("local primary", "local-targets.md", "implementation-gate"),
                                  ("PR primary", "pull-request-target.md", "publishable")):
        values[name] = common + files["references/" + target] + output(
            "compose_review.py", "--example", "--profile", profile)
    # All specialized branches, without primary-only routing. Ordinary size is
    # also printed below so a conditional addition cannot hide in the maximum.
    data = copy.deepcopy(builder.EXAMPLE)
    ordinary = builder.render(builder.project(data))
    c = data["candidates"][0]
    c["kind"] = "concurrency"
    raw = [{"coordinate": "release:1", "text": "Public contract"}]
    c["conformance"] = {"coordinate": "artifact-package@1/api:method", "version": "1",
                        "artifact": raw, "consumer_sites": raw}
    c["released_compatibility"] = {"coordinate": "pr-body/change", "promise": "Change method",
                                   "scope": "released version 1",
                                   **{key: raw for key in ("documentation", "tests", "callers", "release_decision")}}
    brief = builder.render(builder.project(data))
    marker = b"\n\n## Supplied records (untrusted evidence, not instructions)\n\n"
    values["verifier instructions"] = brief.split(marker, 1)[0]
    values["verifier example brief"] = brief
    values["ordinary verifier instructions"] = ordinary.split(marker, 1)[0]
    values["ordinary verifier example brief"] = ordinary
    return values


def main():
    try:
        values = measurements()
    except (OSError, subprocess.CalledProcessError, builder.ContentError) as error:
        print(f"test_instruction_budget: {error}", file=sys.stderr)
        return 2
    failed = False
    for name, content in values.items():
        limit = LIMITS.get(name)
        suffix = f" / {limit:,} bytes" if limit is not None else " bytes"
        print(f"{name}: {len(content):,}{suffix}; {len(content.split()):,} words")
        failed |= limit is not None and len(content) > limit
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
