#!/usr/bin/env python3
"""Resolve this experiment's pilot pair and cell order, and seal them.

Issue #149 must freeze the 24-cell order before dispatch, and #149 also requires
the six-cell pilot to cover one buggy target and the adjudicated clean one. Which
slot is clean is hidden truth (#148 sealed the registers), so a plainly committed
order would narrow the sealed status of the other slots for anyone who reads the
bundle — including a reviewer cell whose shell escapes its permitted roots. This
script therefore resolves the order from the sealed registers and writes it out
encrypted under the same key #148 used, printing only hashes and counts.

It reads each slot register's ``Verdict`` line (``adjudicated clean`` or
``N material defects``) and nothing else, so the operator running it never sees a
defect, a category or a leak SHA. The frozen selection rule is:

* pilot pair = the adjudicated clean slot and the lowest-numbered buggy slot;
* the pilot runs replicate 1 of both slots, arms in the order A, B, C per slot,
  clean slot first;
* the remaining eighteen cells follow, replicate 1 before replicate 2, slots in
  numeric order within a replicate, arms A, B, C within a slot;
* every cell of one slot-and-replicate is contiguous, so a budget stop always
  leaves whole A/B/C triples, which is the unit the matched cost ratio and the
  per-target recall need.

Usage::

    python3 scripts/seal_schedule.py --registers DIR --key FILE --sums FILE \\
        --out-plaintext FILE --out-ciphertext FILE [--slots slot-1,slot-2,...]
    python3 scripts/seal_schedule.py --self-test

``--sums`` is #148's ``targets/sealed/SHA256SUMS``; every register is checked
against it before it is read, so a substituted register cannot silently change
the schedule. The plaintext goes to evaluator-only storage (outside every
reviewer read surface) and the ciphertext into the committed bundle.

Output: the plaintext SHA-256, the ciphertext SHA-256, the cell count and the
arm counts. Never the pilot slots, never a verdict.

Exit: 0 success, 1 on a content violation (hash mismatch, unparsable verdict, no
clean slot or no buggy slot) with one line per violation on stdout, 2 when an
input cannot be read or ``openssl`` fails, naming the command on stderr.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ARMS = ("A", "B", "C")
REPLICATES = (1, 2)
VERDICT = re.compile(r"^\s*(?:#+\s*Verdict\s*|)(?P<line>.*)$")
CLEAN = re.compile(r"adjudicated\s+clean", re.I)
DEFECTS = re.compile(r"(?P<count>\d+)\s+material\s+defects?", re.I)


class Violation(ValueError):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verdict_of(text, name):
    """Return "clean" or "buggy" from the register's Verdict section only."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip().lower().lstrip("# ").startswith("verdict"):
            for candidate in lines[index:index + 4]:
                if CLEAN.search(candidate):
                    return "clean"
                match = DEFECTS.search(candidate)
                if match:
                    return "clean" if int(match.group("count")) == 0 else "buggy"
            break
    raise Violation("no parsable Verdict line in " + name)


def expected_sums(path):
    sums = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2:
            sums[parts[1]] = parts[0]
    return sums


def schedule(slots, status):
    clean = [slot for slot in slots if status[slot] == "clean"]
    buggy = [slot for slot in slots if status[slot] == "buggy"]
    violations = []
    if len(clean) != 1:
        violations.append("expected exactly one adjudicated clean slot, found %d" % len(clean))
    if not buggy:
        violations.append("expected at least one buggy slot, found none")
    if violations:
        raise Violation("\n".join(violations))
    pilot = [clean[0], buggy[0]]
    order = []
    for slot in pilot:
        for arm in ARMS:
            order.append({"cell_id": "%s-%s-replicate-1" % (slot, arm), "target_slot": slot,
                          "arm": arm, "replicate": 1, "block": "pilot", "ticket": 150})
    for replicate in REPLICATES:
        for slot in slots:
            if replicate == 1 and slot in pilot:
                continue
            for arm in ARMS:
                order.append({"cell_id": "%s-%s-replicate-%d" % (slot, arm, replicate),
                              "target_slot": slot, "arm": arm, "replicate": replicate,
                              "block": "grid", "ticket": 151})
    for position, cell in enumerate(order, start=1):
        cell["position"] = position
        cell["attempt_id"] = "issue-138-%s-attempt-1" % cell["cell_id"]
    return pilot, order


def encrypt(plaintext_path, ciphertext_path, key_path):
    command = ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-salt",
               "-pass", "file:" + str(key_path), "-in", str(plaintext_path), "-out", str(ciphertext_path)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        print(" ".join(command[:6]) + " ...", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(2)


def self_test():
    checks = []
    checks.append(("clean verdict", verdict_of("## Verdict\n\nadjudicated clean\n", "t") == "clean"))
    checks.append(("defect verdict", verdict_of("## Verdict\n2 material defects\n", "t") == "buggy"))
    checks.append(("zero defects is clean", verdict_of("Verdict\n0 material defects\n", "t") == "clean"))
    try:
        verdict_of("## Summary\nnothing here\n", "t")
        checks.append(("missing verdict rejected", False))
    except Violation:
        checks.append(("missing verdict rejected", True))
    slots = ["slot-1", "slot-2", "slot-3", "slot-4"]
    pilot, order = schedule(slots, {"slot-1": "buggy", "slot-2": "clean",
                                    "slot-3": "buggy", "slot-4": "buggy"})
    checks.append(("pilot is clean plus lowest buggy", pilot == ["slot-2", "slot-1"]))
    checks.append(("24 unique cells", len(order) == 24 and len({c["cell_id"] for c in order}) == 24))
    checks.append(("pilot owns six cells", sum(c["block"] == "pilot" for c in order) == 6))
    checks.append(("eight cells per arm", all(sum(c["arm"] == a for c in order) == 8 for a in ARMS)))
    checks.append(("triples contiguous", all(
        {order[i]["arm"], order[i + 1]["arm"], order[i + 2]["arm"]} == set(ARMS)
        for i in range(0, 24, 3))))
    checks.append(("positions are 1..24", [c["position"] for c in order] == list(range(1, 25))))
    try:
        schedule(slots, {s: "buggy" for s in slots})
        checks.append(("no clean slot rejected", False))
    except Violation:
        checks.append(("no clean slot rejected", True))
    for name, ok in checks:
        print(("ok   " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in checks) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registers", help="evaluator-only directory holding <slot>-register.md")
    parser.add_argument("--key")
    parser.add_argument("--sums", help="#148 targets/sealed/SHA256SUMS")
    parser.add_argument("--out-plaintext")
    parser.add_argument("--out-ciphertext")
    parser.add_argument("--slots", default="slot-1,slot-2,slot-3,slot-4")
    parser.add_argument("--experiment", default="issue-138")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    required = (args.registers, args.key, args.sums, args.out_plaintext, args.out_ciphertext)
    if not all(required):
        parser.error("--registers, --key, --sums, --out-plaintext and --out-ciphertext are required")
    slots = [slot.strip() for slot in args.slots.split(",") if slot.strip()]
    try:
        sums = expected_sums(args.sums)
        raw = {slot: Path(args.registers, slot + "-register.md").read_bytes() for slot in slots}
    except OSError as exc:
        print(exc, file=sys.stderr)
        return 2
    try:
        violations = [
            "register hash does not match the sealed sum: %s-register.md" % slot
            for slot in slots if sums.get(slot + "-register.md") != sha256(raw[slot])
        ]
        if violations:
            raise Violation("\n".join(violations))
        status = {slot: verdict_of(raw[slot].decode("utf-8"), slot + "-register.md") for slot in slots}
        pilot, order = schedule(slots, status)
    except Violation as exc:
        print(str(exc))
        return 1
    document = {"schema_version": "bounded-discovery-v1", "experiment_id": args.experiment,
                "written_at": datetime.now(timezone.utc).isoformat(),
                "rule": "pilot = the adjudicated clean slot and the lowest-numbered buggy slot, "
                        "replicate 1, arms A/B/C per slot, clean slot first; then replicate 1 of "
                        "the remaining slots and all of replicate 2, slots in numeric order, arms "
                        "A/B/C within each slot",
                "pilot_slots": pilot, "ordered_cells": order,
                "register_sums": {slot: sha256(raw[slot]) for slot in slots}}
    text = json.dumps(document, indent=2, sort_keys=True) + "\n"
    try:
        Path(args.out_plaintext).write_text(text, encoding="utf-8")
        Path(args.out_ciphertext).parent.mkdir(parents=True, exist_ok=True)
        encrypt(args.out_plaintext, args.out_ciphertext, args.key)
        ciphertext = Path(args.out_ciphertext).read_bytes()
    except OSError as exc:
        print(exc, file=sys.stderr)
        return 2
    print("cells %d  arms %s  pilot_cells %d" % (
        len(order), ",".join("%s=%d" % (a, sum(c["arm"] == a for c in order)) for a in ARMS),
        sum(c["block"] == "pilot" for c in order)))
    print("plaintext_sha256 %s" % sha256(text.encode("utf-8")))
    print("ciphertext_sha256 %s" % sha256(ciphertext))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
