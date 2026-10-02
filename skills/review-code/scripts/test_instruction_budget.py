#!/usr/bin/env python3
"""Measure runtime instructions, primary paths, and generated verifier briefs.

Usage: python3 scripts/test_instruction_budget.py
Counts UTF-8 bytes, including expanded help/examples on representative paths: a
first review of a pull request or local target (one record shape serves both), a
review with one required verifier batch, and a re-review, which covers both a pull
request's prior review and a local prior record. Evidence and code are excluded;
the example brief also reports its supplied records.
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
ALWAYS_LOADED = ("SKILL.md", "references/rubric.md", "references/output.md")
# DESIGN.md records the 2026-10-02 synthesis and the evidence required to raise these limits.
BUDGET = 21_000
LIMITS = {"runtime total": 56_000, "always loaded": BUDGET, "review": 40_000,
          "required verifier": 47_000, "re-review": 49_000,
          "verifier instructions": 10_000, "verifier example brief": 13_000}


def output(script, *args):
    return subprocess.run([sys.executable, str(SKILL / "scripts" / script), *args],
                          check=True, capture_output=True).stdout


def measurements():
    files = {"SKILL.md": (SKILL / "SKILL.md").read_bytes()}
    files.update({str(p.relative_to(SKILL)): p.read_bytes()
                  for p in sorted((SKILL / "references").glob("*.md"))})
    always = b"".join(files[name] for name in ALWAYS_LOADED)

    def refs(*names):
        return b"".join(files["references/" + name] for name in names)
    # Every path builds context once; the rubric carries changed tests and supplied checks.
    common = always + output("review_context.py", "--help")
    review = common + refs("targets.md") + output("render_review.py", "--example")
    values = {"runtime total": b"".join(files.values()), "always loaded": always, "review": review,
              "required verifier": review + refs("verification.md") + output("build_verifier_prompt.py", "--example"),
              "re-review": review + refs("prior-state.md")}
    data = copy.deepcopy(builder.EXAMPLE)
    c = data["candidates"][0]
    c["kind"] = "concurrency"
    raw = [{"coordinate": "release:1", "text": "Public contract"}]
    c["conformance"] = {"coordinate": "artifact-package@1/api:method", "version": "1",
                        "artifact": raw, "consumer_sites": raw}
    c["released_compatibility"] = {"coordinate": "pr-body/change", "promise": "Change method",
                                   "scope": "released version 1",
                                   **{key: raw for key in ("documentation", "tests", "callers", "release_decision")}}
    brief = builder.render(builder.project(data), builder.new_bundle_id(), "/abs/path/to/initial/" + builder.RETURN_NAME)
    marker = builder.RECORDS.encode("utf-8")
    values["verifier instructions"] = brief.split(marker, 1)[0]
    values["verifier example brief"] = brief
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
