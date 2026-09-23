#!/usr/bin/env python3
"""Compare review-code's measured load paths between two skill roots.

Usage: python3 measure.py --before <skill root> --after <skill root> [--output FILE]

Each root is a `skills/review-code` directory, such as one extracted with
`git archive <commit> skills/review-code`. Both roots are measured with this
checkout's `test_instruction_budget.py`, so the paths are defined identically.
For every path it reports UTF-8 bytes, words and documented command mentions;
it also reports whether each authored-input example and four representative
verifier briefs are byte-identical between the roots. Exit 0 on success, 2 when
a root or helper cannot be read.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

BUDGET = Path(__file__).resolve().parents[3] / "skills" / "review-code" / "scripts" / "test_instruction_budget.py"
COMMAND = re.compile(rb"python3 (?:scripts/|<)")
EXAMPLES = (("compose_review.py", "--example", "--profile", "publishable"),
            ("compose_review.py", "--example", "--profile", "implementation-gate"),
            ("context_fingerprint.py", "--example"), ("build_verifier_prompt.py", "--example"),
            ("continue_review.py", "--example"))


def budget(root):
    """Load the measurement module against ROOT's references and helpers."""
    sys.modules.pop("build_verifier_prompt", None)
    sys.path.insert(0, str(root / "scripts"))
    try:
        spec = importlib.util.spec_from_file_location("budget", BUDGET)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    module.SKILL = root
    return module


def leaves(value):
    if isinstance(value, dict):
        return sum(leaves(item) for item in value.values()) or 1
    if isinstance(value, list):
        return sum(leaves(item) for item in value) or 1
    return 1


def briefs(builder):
    data = copy.deepcopy(builder.EXAMPLE)
    out = [builder.render(builder.project(data)), builder.render(builder.project(data), "/private/r/raw-return.json")]
    c = data["candidates"][0]
    c["kind"] = "concurrency"
    raw = [{"coordinate": "release:1", "text": "Public contract"}]
    c["conformance"] = {"coordinate": "artifact-package@1/api:method", "version": "1", "artifact": raw, "consumer_sites": raw}
    c["released_compatibility"] = {"coordinate": "pr-body/change", "promise": "Change method", "scope": "released version 1",
                                   **{key: raw for key in ("documentation", "tests", "callers", "release_decision")}}
    out += [builder.render(builder.project(data)), builder.render(builder.project(data), "/private/r/raw-return.json")]
    return [hashlib.sha256(brief).hexdigest() for brief in out]


def measure(root):
    module = budget(root)
    values = module.measurements()
    paths = {name: {"bytes": len(content), "words": len(content.split()),
                    "commands": len(COMMAND.findall(content))} for name, content in values.items()}
    examples = {}
    for args in EXAMPLES:
        text = subprocess.run([sys.executable, str(root / "scripts" / args[0]), *args[1:]],
                              check=True, capture_output=True).stdout
        examples[" ".join(args)] = {"sha256": hashlib.sha256(text).hexdigest(), "leaves": leaves(json.loads(text))}
    return {"paths": paths, "examples": examples, "briefs": briefs(module.builder)}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        before, after = measure(args.before.resolve()), measure(args.after.resolve())
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"measure: {error}", file=sys.stderr)
        return 2
    rows = [{"path": name, "before": before["paths"][name], "after": after["paths"][name],
             "delta_bytes": after["paths"][name]["bytes"] - before["paths"][name]["bytes"]}
            for name in after["paths"] if name in before["paths"]]
    result = {"paths": rows,
              "examples_identical": {name: before["examples"][name] == after["examples"][name] for name in after["examples"]},
              "example_leaves": {name: after["examples"][name]["leaves"] for name in after["examples"]},
              "briefs_identical": before["briefs"] == after["briefs"]}
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
