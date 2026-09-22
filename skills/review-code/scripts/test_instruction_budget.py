#!/usr/bin/env python3
"""Hold review-code's always-loaded instructions to a byte budget.

Usage: python3 scripts/test_instruction_budget.py

Every review reads `SKILL.md`, `references/review-rubric.md`, and
`references/review-record.md` at the start and `references/rendering.md` at
step 5, and the model resends them on every later call of the run. This check
sums their `wc -c` sizes and fails when the total exceeds BUDGET. A new rule
belongs in a script, in a reference its branch loads, or in place of text it
supersedes; raise BUDGET only with a dated DESIGN.md entry saying why.

Exit 0: within budget; 1: over budget, with one line per file and the total.
"""
from __future__ import annotations

import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ALWAYS_LOADED = ("SKILL.md", "references/review-rubric.md", "references/review-record.md", "references/rendering.md")
BUDGET = 73_000


def main() -> int:
    sizes = {name: (SKILL / name).stat().st_size for name in ALWAYS_LOADED}
    total = sum(sizes.values())
    if total <= BUDGET:
        print(f"test_instruction_budget: {total:,} of {BUDGET:,} bytes")
        return 0
    for name, size in sizes.items():
        print(f"{name}: {size:,}")
    print(f"test_instruction_budget: always-loaded set is {total:,} bytes, over the {BUDGET:,}-byte budget")
    return 1


if __name__ == "__main__":
    sys.exit(main())
