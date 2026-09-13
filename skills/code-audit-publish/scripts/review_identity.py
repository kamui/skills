#!/usr/bin/env python3
"""Check whether a prior audit can suppress a duplicate review.

Usage: python3 scripts/review_identity.py packet.json --review ID --author LOGIN
           --merge-base SHA --inputs context-inputs.json

Inputs: a forge-packet/1 from forge_packet.py and a JSON object carrying the
exact reviewed specs and guidance for context_fingerprint.py. The candidate
review must have one complete current-contract trailer and match the packet's
head/base/ref, supplied merge-base, issue set, posting identity and recomputed
digest. Later activity or an undated thread transition prevents the shortcut;
this conservative check never makes a relevance or finding judgment.

Exit 0: duplicate identity eligible (not publication authority).
Exit 1: one reason per line on stdout; perform the review.
Exit 2: unreadable or malformed input, with the reason on stderr; stop the step.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import quote

from context_fingerprint import digest, merge_packet
from forge_packet import PageError, later_state

WORKFLOW = "v2b-5"
SHA = re.compile(r"[0-9a-f]{40}\Z")


def check(packet: dict, review_id: str, author: str, merge_base: str, context: str) -> list[str]:
    if not SHA.fullmatch(merge_base):
        raise ValueError("merge-base must be a full lowercase 40-hex SHA")
    review = next((r for r in packet["reviews"] if r["id"] == review_id), None)
    if review is None:
        raise ValueError(f"review {review_id} is absent from the packet")
    reasons = []
    if review["author"] != author:
        reasons.append("candidate belongs to a different posting identity")
    if packet.get("complete") is not True:
        reasons.append("forge coverage incomplete")
    trailers = re.findall(r"<!-- review-run ([^\n]*?) -->", review["body"])
    if len(trailers) != 1:
        return reasons + ["candidate must have exactly one run trailer"]
    fields = {}
    for token in trailers[0].split():
        if token.count("=") != 1:
            return reasons + ["malformed run trailer"]
        key, value = token.split("=", 1)
        if key in fields or not value:
            return reasons + ["duplicate or empty run trailer field"]
        fields[key] = value
    pr = packet["pr"]
    issues = ",".join(sorted(i["coordinate"] for i in packet["fingerprint"]["issues"])) or "none"
    expected = {
        "workflow": WORKFLOW, "head": pr["head_sha"],
        "base-ref": quote(pr["base_ref"], safe="/-._~"), "base-sha": pr["base_sha"],
        "merge-base": merge_base, "context": context, "issues": issues,
        "coverage": "complete",
    }
    for key in ("head", "base-sha"):
        if not SHA.fullmatch(expected[key]):
            raise ValueError(f"packet {key} must be a full lowercase 40-hex SHA")
    for key, value in expected.items():
        if fields.get(key) != value:
            reasons.append(f"run identity differs: {key}")
    if review["commit"] != pr["head_sha"]:
        reasons.append("review commit differs from the pinned head")
    reasons.extend(later_state(packet, review_id, None))
    return reasons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("packet")
    parser.add_argument("--review", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--merge-base", required=True)
    parser.add_argument("--inputs", required=True)
    args = parser.parse_args()
    try:
        with open(args.packet, encoding="utf-8") as handle:
            packet = json.load(handle)
        with open(args.inputs, encoding="utf-8") as handle:
            inputs = json.load(handle)
        context = digest(merge_packet(inputs, args.packet))
        reasons = check(packet, args.review, args.author, args.merge_base, context)
    except (OSError, ValueError, KeyError, TypeError, PageError) as error:
        print(f"review_identity: {error}", file=sys.stderr)
        return 2
    for reason in reasons:
        print(reason)
    return 1 if reasons else 0


if __name__ == "__main__":
    raise SystemExit(main())
