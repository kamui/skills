#!/usr/bin/env python3
"""Derive this run's planned cells and sealed order, or check the manifest against them.

Usage: python3 -B order.py [--check]

The target order is random.Random(seed).shuffle over the id-sorted cohort, with seed the first 16
hex digits of the SHA-256 of the cohort's packet_sha256 values concatenated in id order, as in
run 2026-09-24-builtin-baseline. Every built-in cell precedes every review-code cell, because the
maintainer funded the built-in first. Within an arm, replicate 1 runs across all targets before
replicate 2, and replicate 2 before replicate 3. Exit 0 printed or matching, 1 on a mismatch.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys

RUN = os.path.dirname(os.path.abspath(__file__))
ARMS = ("claude-builtin-sonnet-5-5-high", "review-code-sonnet-5-5-high-enforced")
REPLICATES = 3


def derive(cohort):
    ids = sorted(entry["target"] for entry in cohort)
    packets = {entry["target"]: entry["packet_sha256"] for entry in cohort}
    seed = int(hashlib.sha256("".join(packets[t] for t in ids).encode("utf-8")).hexdigest()[:16], 16)
    order = list(ids)
    random.Random(seed).shuffle(order)
    planned = [{"target": t, "arm": a, "replicate": r} for t in ids for a in ARMS for r in range(1, REPLICATES + 1)]
    sealed = [f"{t}/{a}/{r}" for a in ARMS for r in range(1, REPLICATES + 1) for t in order]
    return seed, order, planned, sealed


def main():
    with open(os.path.join(RUN, "manifest.json"), encoding="utf-8") as handle:
        manifest = json.load(handle)
    seed, order, planned, sealed = derive(manifest["cohort"])
    if "--check" not in sys.argv:
        print(json.dumps({"seed": seed, "target_order": order, "planned_cells": planned, "sealed_order": sealed}, indent=2))
        return 0
    problems = [name for name, value in (("planned_cells", planned), ("sealed_order", sealed)) if manifest.get(name) != value]
    for name in problems:
        print(f"manifest {name} differs from the derivation")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
