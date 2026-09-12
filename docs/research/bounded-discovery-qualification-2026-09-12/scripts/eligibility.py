#!/usr/bin/env python3
"""Apply #148's mechanical target criteria E1-E3 and E5 to candidate pull requests.

#148's criteria are checked "mechanically by the curator" for E1-E10 and by the adjudicator
for E11. Four of them are decidable from the forge alone and are therefore the ones a script
should own, so that a hunt cannot quietly relax them:

- **E1 Unused** - the candidate is not on the reservation set, which ``reservations.py``
  derives by rule from the files that publish it.
- **E2 Settled** - ``mergedAt`` is on or before the freshness threshold, six months before the
  freeze's "today".
- **E3 Small** - at most 200 changed lines across at most 6 files.
- **E5 Trail readable through gh** - the pull request has GitHub-native reviews or review
  threads rather than an external review system.

E4 (packet-buildable), E6-E10 and E11 are not decidable from this data and stay where #148 put
them: the curator's own checks and the adjudicator's ruling. This script never selects a
target; it reports, per candidate, which of the four it passes.

Usage::

    python3 scripts/eligibility.py --reservations FILE --threshold YYYY-MM-DD
        --out FILE CANDIDATE [CANDIDATE ...]
    python3 scripts/eligibility.py --self-test

``CANDIDATE`` is ``owner/repo#number``. Forge data is read with ``gh api``; a candidate whose
data cannot be read is reported ``unknown`` and never silently passed.

Exit: 0 when every candidate was evaluated, 1 when a candidate could not be evaluated with one
line each on stdout, 2 when an input cannot be read or ``gh`` is unavailable.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CANDIDATE = re.compile(r"^([A-Za-z0-9][\w.-]*/[\w.-]+)#(\d+)$")
MAX_LINES = 200
MAX_FILES = 6


def fetch(repository, number):
    """The forge fields E1-E3 and E5 need, or None with the failure text."""
    query = ("repos/%s/pulls/%s" % (repository, number))
    result = subprocess.run(["gh", "api", query], text=True, capture_output=True)
    if result.returncode != 0:
        return None, result.stderr.strip().splitlines()[-1] if result.stderr else "gh failed"
    if not result.stdout.strip():
        return None, ("gh exited 0 with no output; the call did not leave the machine and the "
                      "emptiness is not an answer")
    pull = json.loads(result.stdout)
    reviews = subprocess.run(["gh", "api", query + "/reviews", "--jq", "length"],
                             text=True, capture_output=True)
    comments = subprocess.run(["gh", "api", query + "/comments", "--jq", "length"],
                              text=True, capture_output=True)
    return {
        "merged_at": pull.get("merged_at"),
        "merged": bool(pull.get("merged")),
        "changed_files": pull.get("changed_files"),
        "additions": pull.get("additions"),
        "deletions": pull.get("deletions"),
        "review_count": int(reviews.stdout.strip() or 0) if reviews.returncode == 0 else None,
        "review_comment_count": int(comments.stdout.strip() or 0)
        if comments.returncode == 0 else None,
        "title": pull.get("title"),
        "head_sha": (pull.get("head") or {}).get("sha"),
        "base_sha": (pull.get("base") or {}).get("sha"),
        "base_ref": (pull.get("base") or {}).get("ref"),
        "license": ((pull.get("base") or {}).get("repo") or {}).get("license") or None,
    }, None


def evaluate(candidate, data, reserved, threshold):
    """Each criterion is pass, fail or unknown. Unknown never counts as pass."""
    checks = {}
    checks["E1"] = {"passed": candidate not in reserved,
                    "detail": ("on the reservation set: " +
                               "; ".join(reserved[candidate]["reasons"])
                               if candidate in reserved else "not on the reservation set")}
    merged = data.get("merged_at")
    if not data.get("merged") or not merged:
        checks["E2"] = {"passed": False, "detail": "not merged"}
    else:
        checks["E2"] = {"passed": merged <= threshold,
                        "detail": "mergedAt " + merged + " against the threshold " + threshold}
    files, additions, deletions = (data.get("changed_files"), data.get("additions"),
                                   data.get("deletions"))
    if None in (files, additions, deletions):
        checks["E3"] = {"passed": None, "detail": "the forge did not report the size"}
    else:
        size = additions + deletions
        checks["E3"] = {"passed": size <= MAX_LINES and files <= MAX_FILES,
                        "detail": "%d files, +%d/-%d (%d) against at most %d files and %d lines"
                                  % (files, additions, deletions, size, MAX_FILES, MAX_LINES)}
    reviews, review_comments = data.get("review_count"), data.get("review_comment_count")
    if reviews is None or review_comments is None:
        checks["E5"] = {"passed": None, "detail": "the review trail could not be read"}
    else:
        checks["E5"] = {"passed": bool(reviews or review_comments),
                        "detail": "%d review submission(s), %d review comment(s)"
                                  % (reviews, review_comments)}
    return checks


def run(candidates, reservations_path: Path, threshold: str, out: Path):
    reserved = json.loads(reservations_path.read_text(encoding="utf-8"))["reserved"]
    rows, failures = [], []
    for candidate in candidates:
        match = CANDIDATE.match(candidate)
        if not match:
            failures.append(candidate + " is not owner/repo#number")
            continue
        data, error = fetch(match.group(1), match.group(2))
        if data is None:
            rows.append({"candidate": candidate, "error": error, "checks": None,
                         "mechanically_eligible": None})
            failures.append(candidate + " could not be read: " + str(error))
            continue
        checks = evaluate(candidate, data, reserved, threshold)
        decided = [check["passed"] for check in checks.values()]
        rows.append({
            "candidate": candidate,
            "title": data.get("title"),
            "head_sha": data.get("head_sha"),
            "base_ref": data.get("base_ref"),
            "checks": checks,
            "mechanically_eligible": (None if None in decided else all(decided)),
        })
    body = {
        "probe": "P24-machinery",
        "what_this_decides": ("E1, E2, E3 and E5 only. E4, E6-E10 stay with the curator and E11 "
                              "with the adjudicator; a candidate this script passes is not a "
                              "selected target and no selection is made here."),
        "freshness_threshold": threshold,
        "reservations": str(reservations_path),
        "reserved_count": len(reserved),
        "candidates": rows,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    out.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    for failure in failures:
        print(failure)
    for row in rows:
        if row["checks"]:
            verdict = {True: "eligible", False: "excluded", None: "unknown"}[
                row["mechanically_eligible"]]
            print("%-34s %-9s %s" % (row["candidate"], verdict,
                                     "; ".join(name + "=" +
                                               {True: "pass", False: "FAIL", None: "unknown"}[
                                                   check["passed"]]
                                               for name, check in row["checks"].items())))
    return 1 if failures else 0


def self_test():
    failures = []

    def check(name, condition):
        if not condition:
            failures.append(name)

    reserved = {"a/b#1": {"reasons": ["a revealed #138 target"]}}
    data = {"merged": True, "merged_at": "2025-01-01T00:00:00Z", "changed_files": 2,
            "additions": 10, "deletions": 5, "review_count": 1, "review_comment_count": 0}
    checks = evaluate("a/b#1", data, reserved, "2026-03-12T00:00:00Z")
    check("a reserved candidate fails E1", checks["E1"]["passed"] is False)
    checks = evaluate("c/d#2", data, reserved, "2026-03-12T00:00:00Z")
    check("an unreserved candidate passes E1", checks["E1"]["passed"] is True)
    check("a settled merge passes E2", checks["E2"]["passed"] is True)
    check("a small change passes E3", checks["E3"]["passed"] is True)
    check("a reviewed pull request passes E5", checks["E5"]["passed"] is True)

    late = dict(data, merged_at="2026-06-01T00:00:00Z")
    check("a recent merge fails E2",
          evaluate("c/d#2", late, reserved, "2026-03-12T00:00:00Z")["E2"]["passed"] is False)
    big = dict(data, additions=300)
    check("a large change fails E3",
          evaluate("c/d#2", big, reserved, "2026-03-12T00:00:00Z")["E3"]["passed"] is False)
    wide = dict(data, changed_files=9)
    check("a wide change fails E3",
          evaluate("c/d#2", wide, reserved, "2026-03-12T00:00:00Z")["E3"]["passed"] is False)
    unmerged = dict(data, merged=False, merged_at=None)
    check("an unmerged pull request fails E2",
          evaluate("c/d#2", unmerged, reserved, "2026-03-12T00:00:00Z")["E2"]["passed"] is False)
    unknown = dict(data, changed_files=None)
    check("an unreadable size is unknown, not a pass",
          evaluate("c/d#2", unknown, reserved, "2026-03-12T00:00:00Z")["E3"]["passed"] is None)
    untrailed = dict(data, review_count=0, review_comment_count=0)
    check("a pull request with no native trail fails E5",
          evaluate("c/d#2", untrailed, reserved, "2026-03-12T00:00:00Z")["E5"]["passed"] is False)

    for failure in failures:
        print("FAIL", failure)
    print(("FAILED " + str(len(failures))) if failures else "ok: 11 checks")
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidates", nargs="*")
    parser.add_argument("--reservations", type=Path)
    parser.add_argument("--threshold")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        if not args.candidates or not args.reservations or not args.threshold or not args.out:
            print("--reservations, --threshold, --out and at least one candidate are required")
            return 1
        threshold = args.threshold
        if len(threshold) == 10:
            threshold += "T00:00:00Z"
        return run(args.candidates, args.reservations, threshold, args.out)
    except (OSError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
