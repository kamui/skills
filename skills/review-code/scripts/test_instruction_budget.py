#!/usr/bin/env python3
"""Measure runtime instructions, primary paths, and generated verifier briefs.

Usage: python3 scripts/test_instruction_budget.py
Counts UTF-8 bytes, including expanded help/examples on representative paths:
local and pull-request publishable reviews, the implementation gate, a pull-request
review with one required verifier batch, a pull-request re-review, and a gate
continuation. Evidence and code are excluded; example briefs also report their
supplied records.
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
# Rounded ceilings above the #356 layout, including actual helper output. The always-loaded
# set now carries the rubric and stays below #346's 32,567-byte common set (always loaded
# plus changed tests and check evidence); DESIGN.md dates why the target paths rose.
BUDGET = 32_000
LIMITS = {"runtime total": 84_000, "always loaded": BUDGET,
          "local publishable": 55_000, "PR publishable": 55_000, "implementation-gate": 55_000,
          "required verifier": 68_000, "re-review": 62_000, "continuation": 43_000,
          "verifier instructions": 18_000, "verifier example brief": 22_000,
          "file-transport verifier example brief": 22_000}


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
    first = common + output("context_fingerprint.py", "--example")
    publishable = output("compose_review.py", "--example", "--profile", "publishable")
    pr = first + refs("targets.md") + publishable
    values = {"runtime total": b"".join(files.values()), "always loaded": always,
              "local publishable": first + refs("targets.md") + publishable,
              "PR publishable": pr,
              "implementation-gate": first + refs("targets.md") + output(
                  "compose_review.py", "--example", "--profile", "implementation-gate"),
              # One ordinary batch; the worker-only references stay out of the primary.
              "required verifier": pr + refs("verification.md") + output("build_verifier_prompt.py", "--example"),
              "re-review": pr + refs("prior-state.md"),
              "continuation": common + refs("continuation-addendum.md") + output("continue_review.py", "--example")}
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
    # The same batch with a worker-saved return; the assignment line is the only per-run text.
    values["file-transport verifier example brief"] = builder.render(builder.project(data), "/private/initial-return/raw-return.json")
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
