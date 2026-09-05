#!/usr/bin/env python3
"""CLI fixtures for `forge_packet.py` and its hand-off to `context_fingerprint.py`.

`SKILL.md` step 1 keeps the forge inputs as one packet that the review, the
`context` digest, and the re-review all read. These cases drive the script
through `subprocess` on saved-response fixtures shaped like the documented
GraphQL queries and pin what issue #132 requires of it:

- a fixture shaped like the root query with a real non-empty issue-comment
  list normalizes and fingerprints without synthesized identities;
- two-page outer (reviews) and nested (issue comments, thread replies)
  connections merge to a complete packet;
- duplicate items at a page boundary collapse by stable id, and a duplicate
  whose content differs is reported;
- a missing or failed continuation is a named gap, never complete coverage,
  and the truncated packet cannot pass the later-state check or share a digest
  with the complete one;
- a reply edited after a review without a code change is later state, while the
  candidate review's own original comments are not;
- a resolved thread with no resolution timestamp is never silently unchanged.

Run with ``python3 scripts/test_forge_packet.py``. Exit 0 when every case
passes; exit 1 after printing one line per failed case. Standard library only;
no network or git access beyond invoking the scripts under test.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "forge_packet.py"
FINGERPRINT = HERE / "context_fingerprint.py"

failures: list[str] = []


def fail(case: str, detail: str) -> None:
    failures.append(f"{case}: {detail}")


def run(*args: str, stdin: Optional[str] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def write(directory: Path, name: str, payload: Any) -> str:
    path = directory / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def normalize(case: str, directory: Path, pages: dict[str, Any]) -> Optional[dict[str, Any]]:
    paths = [write(directory, name, payload) for name, payload in pages.items()]
    result = run("normalize", *paths)
    if result.returncode != 0:
        fail(case, f"normalize exited {result.returncode}: {result.stderr.strip()}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        fail(case, f"normalize printed invalid JSON: {error}")
        return None


def digest(case: str, directory: Path, packet: dict[str, Any], extra: Optional[dict[str, Any]] = None) -> Optional[str]:
    path = write(directory, f"{case}-packet.json", packet)
    result = subprocess.run(
        [sys.executable, str(FINGERPRINT), "--packet", path],
        input=json.dumps(extra) if extra is not None else "",
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        fail(case, f"context_fingerprint exited {result.returncode}: {result.stderr.strip()}")
        return None
    return result.stdout.strip()


# --- fixtures ---------------------------------------------------------------

T0 = "2026-09-01T09:00:00Z"  # the candidate review's submission time
BEFORE = "2026-08-30T10:00:00Z"
AFTER = "2026-09-02T12:00:00Z"


def connection(nodes: list[Any], total: int, has_next: bool, cursor: Optional[str] = "cur") -> dict[str, Any]:
    return {"totalCount": total, "pageInfo": {"hasNextPage": has_next, "endCursor": cursor}, "nodes": nodes}


def issue_comment(number: int, created: str = BEFORE, edited: Optional[str] = None, body: str = "comment") -> dict[str, Any]:
    return {
        "fullDatabaseId": str(number),
        "author": {"login": "maintainer"},
        "createdAt": created,
        "updatedAt": edited or created,
        "lastEditedAt": edited,
        "body": body,
        "url": f"https://github.com/acme/payments/issues/123#issuecomment-{number}",
    }


def review(number: int, submitted: str, author: str = "reviewer") -> dict[str, Any]:
    return {
        "fullDatabaseId": str(number),
        "author": {"login": author},
        "state": "COMMENTED",
        "body": f"review {number}",
        "submittedAt": submitted,
        "updatedAt": submitted,
        "lastEditedAt": None,
        "commit": {"oid": "a" * 40},
        "url": f"https://github.com/acme/payments/pull/7#pullrequestreview-{number}",
    }


def thread_comment(
    number: int,
    created: str,
    review_id: str,
    reply_to: Optional[str] = None,
    edited: Optional[str] = None,
    author: str = "reviewer",
) -> dict[str, Any]:
    return {
        "fullDatabaseId": str(number),
        "author": {"login": author},
        "body": f"thread comment {number}",
        "createdAt": created,
        "updatedAt": edited or created,
        "lastEditedAt": edited,
        "replyTo": {"fullDatabaseId": reply_to} if reply_to else None,
        "pullRequestReview": {"fullDatabaseId": review_id},
        "url": f"https://github.com/acme/payments/pull/7#discussion_r{number}",
    }


def thread(thread_id: str, comments: dict[str, Any], resolved: bool = False, path: str = "src/retry.ts") -> dict[str, Any]:
    return {
        "id": thread_id,
        "isResolved": resolved,
        "isOutdated": False,
        "path": path,
        "line": 18,
        "originalLine": 18,
        "diffSide": "RIGHT",
        "comments": comments,
    }


def issue(number: int, comments: dict[str, Any], edited: Optional[str] = None) -> dict[str, Any]:
    return {
        "number": number,
        "title": f"Issue {number}",
        "body": "Acceptance criterion 2: one idempotency key per logical charge.",
        "url": f"https://github.com/acme/payments/issues/{number}",
        "updatedAt": edited or BEFORE,
        "lastEditedAt": edited,
        "comments": comments,
    }


def root(
    *,
    closing: dict[str, Any],
    reviews: dict[str, Any],
    threads: dict[str, Any],
    comments: Optional[dict[str, Any]] = None,
    pr_edited: Optional[str] = None,
) -> dict[str, Any]:
    """A response shaped exactly like SKILL.md's documented root query."""
    return {
        "data": {
            "repository": {
                "url": "https://github.com/acme/payments",
                "pullRequest": {
                    "title": "Preserve the idempotency key across retries",
                    "body": "Closes #123. Adds a retry policy for charge submission.",
                    "state": "OPEN",
                    "merged": False,
                    "isDraft": False,
                    "baseRefName": "main",
                    "baseRefOid": "b" * 40,
                    "headRefOid": "a" * 40,
                    "updatedAt": pr_edited or BEFORE,
                    "lastEditedAt": pr_edited,
                    "baseRepository": {"url": "https://github.com/acme/payments"},
                    "closingIssuesReferences": closing,
                    "reviews": reviews,
                    "reviewThreads": threads,
                    "comments": comments if comments is not None else connection([], 0, False, None),
                },
            }
        }
    }


def pr_continuation(**connections: dict[str, Any]) -> dict[str, Any]:
    return {"data": {"repository": {"pullRequest": connections}}}


def issue_continuation(number: int, comments: dict[str, Any]) -> dict[str, Any]:
    return {
        "data": {
            "repository": {
                "url": "https://github.com/acme/payments",
                "issue": {"number": number, "url": f"https://github.com/acme/payments/issues/{number}", "comments": comments},
            }
        }
    }


def thread_continuation(thread_id: str, comments: dict[str, Any]) -> dict[str, Any]:
    return {"data": {"node": {"id": thread_id, "comments": comments}}}


def simple_root() -> dict[str, Any]:
    """One page, complete everywhere, with two real issue comments."""
    return root(
        closing=connection([issue(123, connection([issue_comment(42), issue_comment(7)], 2, False))], 1, False),
        reviews=connection([review(900, T0)], 1, False),
        threads=connection(
            [thread("PRRT_1", connection([thread_comment(5000, T0, "900")], 1, False))], 1, False
        ),
    )


# --- cases ------------------------------------------------------------------


def case_root_fixture_fingerprints(directory: Path) -> None:
    """A documented-query fixture with real comments normalizes and hashes as is."""
    case = "root fixture fingerprints"
    packet = normalize(case, directory, {"root.json": simple_root()})
    if packet is None:
        return
    if not packet["complete"] or packet["gaps"]:
        fail(case, f"expected a complete packet, got gaps {packet['gaps']}")
    ids = sorted(comment["id"] for comment in packet["issues"][0]["comments"])
    if ids != ["42", "7"]:
        fail(case, f"expected the forge ids 42 and 7 verbatim, got {ids}")
    fingerprint_issue = packet["fingerprint"]["issues"][0]
    if fingerprint_issue["coordinate"] != "acme/payments#123":
        fail(case, f"coordinate derived wrongly: {fingerprint_issue['coordinate']}")
    if sorted(comment["id"] for comment in fingerprint_issue["comments"]) != ["42", "7"]:
        fail(case, "fingerprint comments do not carry the forge ids")
    if "comments_complete" in fingerprint_issue or "comments_available" in fingerprint_issue:
        fail(case, "a complete issue must not carry a truncation marker")
    if packet["pr"]["head_sha"] != "a" * 40 or packet["pr"]["merged"] is not False:
        fail(case, "run identity fields were not carried")
    via_packet = digest(case, directory, packet, {"specs": [], "guidance": []})
    direct_payload = dict(packet["fingerprint"], specs=[], guidance=[])
    direct = subprocess.run(
        [sys.executable, str(FINGERPRINT)],
        input=json.dumps(direct_payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if via_packet is None or direct.returncode != 0:
        fail(case, f"direct digest exited {direct.returncode}: {direct.stderr.strip()}")
    elif via_packet != direct.stdout.strip():
        fail(case, "--packet digest differs from the digest of the same fields supplied directly")
    without_extra = digest(case, directory, packet)
    if without_extra != via_packet:
        fail(case, "empty stdin with --packet must equal empty specs and guidance")


def case_two_page_connections(directory: Path) -> None:
    """Outer reviews and nested issue comments and thread replies span two pages."""
    case = "two-page connections"
    first = root(
        closing=connection([issue(123, connection([issue_comment(42)], 2, True))], 1, False),
        reviews=connection([review(900, T0)], 2, True),
        threads=connection(
            [thread("PRRT_1", connection([thread_comment(5000, T0, "900")], 2, True))], 1, False
        ),
    )
    pages = {
        "root.json": first,
        "issue-p2.json": issue_continuation(123, connection([issue_comment(7)], 2, False)),
        "reviews-p2.json": pr_continuation(reviews=connection([review(901, BEFORE, "other")], 2, False)),
        "thread-p2.json": thread_continuation(
            "PRRT_1", connection([thread_comment(5001, AFTER, "901", reply_to="5000", author="author")], 2, False)
        ),
    }
    packet = normalize(case, directory, pages)
    if packet is None:
        return
    if not packet["complete"]:
        fail(case, f"expected complete, got gaps {packet['gaps']}")
    if sorted(comment["id"] for comment in packet["issues"][0]["comments"]) != ["42", "7"]:
        fail(case, "nested issue comments did not merge across pages")
    if sorted(review["id"] for review in packet["reviews"]) != ["900", "901"]:
        fail(case, "outer reviews did not merge across pages")
    replies = packet["threads"][0]["comments"]
    if [comment["id"] for comment in replies] != ["5000", "5001"] or replies[1]["reply_to"] != "5000":
        fail(case, f"thread replies did not merge across pages: {replies}")
    coverage = packet["coverage"]
    if coverage["reviews"]["pages"] != 2 or coverage["issue acme/payments#123 comments"]["pages"] != 2:
        fail(case, f"page counts not tracked: {coverage}")
    # The same pages in another order give the same packet content.
    reordered = normalize(case, directory, dict(reversed(list(pages.items()))))
    if reordered is not None:
        for key in ("issues", "reviews", "threads", "fingerprint", "complete"):
            left = json.dumps(packet[key], sort_keys=True)
            right = json.dumps(reordered[key], sort_keys=True)
            if key == "reviews":
                left = json.dumps(sorted(packet[key], key=lambda r: r["id"]), sort_keys=True)
                right = json.dumps(sorted(reordered[key], key=lambda r: r["id"]), sort_keys=True)
            if left != right:
                fail(case, f"page order changed the packet's {key}")


def case_duplicate_page_items(directory: Path) -> None:
    """An item repeated at a page boundary counts once; a differing repeat is reported."""
    case = "duplicate page items"
    first = root(
        closing=connection([issue(123, connection([issue_comment(42), issue_comment(7)], 3, True))], 1, False),
        reviews=connection([review(900, T0)], 1, False),
        threads=connection([], 0, False, None),
    )
    same = issue_continuation(123, connection([issue_comment(7), issue_comment(8)], 3, False))
    packet = normalize(case, directory, {"root.json": first, "p2.json": same})
    if packet is not None:
        ids = sorted(comment["id"] for comment in packet["issues"][0]["comments"])
        if ids != ["42", "7", "8"] or not packet["complete"]:
            fail(case, f"identical boundary duplicate not collapsed: ids {ids}, gaps {packet['gaps']}")
    differing = issue_continuation(
        123, connection([issue_comment(7, edited=AFTER, body="comment, edited"), issue_comment(8)], 3, False)
    )
    packet = normalize(case, directory, {"root.json": first, "p2-diff.json": differing})
    if packet is not None:
        ids = sorted(comment["id"] for comment in packet["issues"][0]["comments"])
        kept = next(comment for comment in packet["issues"][0]["comments"] if comment["id"] == "7")
        if ids != ["42", "7", "8"]:
            fail(case, f"differing duplicate produced wrong ids {ids}")
        if kept["body"] != "comment, edited" or kept["last_edited_at"] != AFTER:
            fail(case, "the later edit of a differing duplicate was not kept")
        if packet["complete"] or not any("item 7 differs between pages" in gap for gap in packet["gaps"]):
            fail(case, f"differing duplicate was not reported: {packet['gaps']}")


def case_missing_or_failed_continuation(directory: Path) -> None:
    """A missing page, a failed page, and a null node are named gaps, never complete."""
    case = "missing or failed continuation"
    first = root(
        closing=connection([issue(123, connection([issue_comment(42)], 2, True))], 1, False),
        reviews=connection([review(900, T0)], 3, True),
        threads=connection(
            [thread("PRRT_1", connection([thread_comment(5000, T0, "900")], 1, False))], 3, True
        ),
    )
    packet = normalize(case, directory, {"root.json": first})
    if packet is None:
        return
    if packet["complete"]:
        fail(case, "truncated packet reported complete")
    expected = (
        "issue acme/payments#123 comments: 1 of 2 items fetched; continuation missing or failed",
        "reviews: 1 of 3 items fetched; continuation missing or failed",
        "reviewThreads: 1 of 3 items fetched; continuation missing or failed",
    )
    for fragment in expected:
        if not any(fragment in gap for gap in packet["gaps"]):
            fail(case, f"no gap mentions `{fragment}`: {packet['gaps']}")
    # A null node (an item the token cannot see) is a permanent named gap.
    with_null = copy.deepcopy(first)
    with_null["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"].append(None)
    packet_null = normalize(case, directory, {"null.json": with_null})
    if packet_null is not None and not any("nodes[1] is null" in gap for gap in packet_null["gaps"]):
        fail(case, f"null node not named as a gap: {packet_null['gaps']}")
    if packet["fingerprint"]["issues"][0].get("comments_complete") is not False:
        fail(case, "truncated issue comments must carry comments_complete: false into the digest input")
    if packet["issues"][0]["comments_complete"] is not False or packet["coverage"]["reviews"]["complete"]:
        fail(case, "per-connection completeness not recorded")
    # A failed continuation (GraphQL error, null data) is a named gap too.
    failed = {"data": None, "errors": [{"message": "Something went wrong while executing your query."}]}
    packet = normalize(case, directory, {"root.json": first, "failed.json": failed})
    if packet is not None and not any("GraphQL errors" in gap and "failed.json" in gap for gap in packet["gaps"]):
        fail(case, f"failed page not named as a gap: {packet['gaps'] if packet else None}")
    # A truncated packet can neither pass later-state nor share the complete digest.
    truncated = normalize(case, directory, {"root.json": first})
    complete = normalize(
        case,
        directory,
        {
            "root.json": first,
            "issue-p2.json": issue_continuation(123, connection([issue_comment(7)], 2, False)),
            "reviews-p2.json": pr_continuation(
                reviews=connection([review(901, BEFORE), review(902, BEFORE)], 3, False)
            ),
            "threads-p2.json": pr_continuation(
                reviewThreads=connection(
                    [
                        thread("PRRT_2", connection([thread_comment(6000, BEFORE, "901")], 1, False)),
                        thread("PRRT_3", connection([thread_comment(7000, BEFORE, "902")], 1, False)),
                    ],
                    3,
                    False,
                )
            ),
        },
    )
    if truncated is None or complete is None:
        return
    if not complete["complete"]:
        fail(case, f"completed packet still has gaps: {complete['gaps']}")
    path = write(directory, "truncated-packet.json", truncated)
    result = run("later-state", path, "--review", "900")
    if result.returncode != 1 or not any(line.startswith("incomplete ") for line in result.stdout.splitlines()):
        fail(case, f"later-state on a truncated packet must exit 1 with incomplete lines, got {result.returncode}: {result.stdout!r}")
    left = digest(case, directory, truncated)
    right = digest(case, directory, complete)
    if left is not None and right is not None and left == right:
        fail(case, "truncated and complete packets share a digest")
    # The truncation marker alone changes the digest even with equal visible comments.
    marker = copy.deepcopy(complete)
    marker["fingerprint"]["issues"][0]["comments_complete"] = False
    if digest(case, directory, marker) == right:
        fail(case, "comments_complete: false did not change the digest")


def case_later_state(directory: Path) -> None:
    """Edited replies are later state; the review's own comments are not; threads never silent."""
    case = "later-state"
    threads = connection(
        [
            thread(
                "PRRT_1",
                connection(
                    [
                        thread_comment(5000, T0, "900"),
                        thread_comment(5001, BEFORE, "900", reply_to="5000", author="author", edited=AFTER),
                    ],
                    2,
                    False,
                ),
            ),
            thread("PRRT_2", connection([thread_comment(6000, T0, "900")], 1, False), resolved=True),
            thread("PRRT_3", connection([thread_comment(7000, BEFORE, "800")], 1, False), resolved=False),
        ],
        3,
        False,
    )
    page = root(
        closing=connection([issue(123, connection([issue_comment(42)], 1, False))], 1, False),
        reviews=connection([review(800, BEFORE, "other"), review(900, T0)], 2, False),
        threads=threads,
    )
    packet = normalize(case, directory, {"root.json": page})
    if packet is None:
        return
    path = write(directory, "later-packet.json", packet)
    result = run("later-state", path, "--review", "900")
    lines = result.stdout.splitlines()
    if result.returncode != 1:
        fail(case, f"expected exit 1 with later state, got {result.returncode}: {result.stdout!r} {result.stderr!r}")
    if not any(line.startswith("reply thread=PRRT_1 id=5001") and AFTER in line for line in lines):
        fail(case, f"a reply edited after the review was not reported: {lines}")
    if any("id=5000" in line or "id=6000" in line for line in lines):
        fail(case, f"the candidate review's own comments were reported as later state: {lines}")
    if any(line.startswith("review id=800") for line in lines):
        fail(case, f"an earlier review was reported as later state: {lines}")
    if not any(line.startswith("thread-state thread=PRRT_2") for line in lines):
        fail(case, f"a resolved thread without a timestamp was silently treated as unchanged: {lines}")
    if any(line.startswith("thread-state thread=PRRT_3") for line in lines):
        fail(case, f"an unresolved thread drew a thread-state line: {lines}")
    # With the edit undone and the resolved thread unresolved, nothing is later: exit 0.
    clean = copy.deepcopy(page)
    pr = clean["data"]["repository"]["pullRequest"]
    reply = pr["reviewThreads"]["nodes"][0]["comments"]["nodes"][1]
    reply["lastEditedAt"] = None
    reply["updatedAt"] = BEFORE
    pr["reviewThreads"]["nodes"][1]["isResolved"] = False
    packet = normalize(case, directory, {"clean.json": clean})
    if packet is not None:
        result = run("later-state", write(directory, "clean-packet.json", packet), "--review", "900")
        if result.returncode != 0 or result.stdout.strip():
            fail(case, f"clean packet should exit 0 silently, got {result.returncode}: {result.stdout!r}")
        # Issue and pull-request body edits are later state as well.
        edited = copy.deepcopy(clean)
        edited["data"]["repository"]["pullRequest"]["lastEditedAt"] = AFTER
        edited["data"]["repository"]["pullRequest"]["closingIssuesReferences"]["nodes"][0]["lastEditedAt"] = AFTER
        packet = normalize(case, directory, {"edited.json": edited})
        if packet is not None:
            result = run("later-state", write(directory, "edited-packet.json", packet), "--review", "900")
            out = result.stdout
            if result.returncode != 1 or "pr edited" not in out or "issue acme/payments#123 edited" not in out:
                fail(case, f"pr and issue body edits not reported: {out!r}")
        # --after overrides the review's own submission time.
        result = run("later-state", write(directory, "clean-packet.json", packet or {}), "--review", "900", "--after", "2026-01-01T00:00:00Z")
        if result.returncode != 1:
            fail(case, "--after cutoff was ignored")
    result = run("later-state", path, "--review", "999")
    if result.returncode != 2 or "not in the packet" not in result.stderr:
        fail(case, f"unknown review id must exit 2: {result.returncode} {result.stderr!r}")


def case_explicit_issue_page(directory: Path) -> None:
    """An explicitly referenced issue joins the packet and the digest as a non-closing issue."""
    case = "explicit issue page"
    explicit = {
        "data": {
            "repository": {
                "url": "https://github.com/acme/payments",
                "issue": issue(98, connection([issue_comment(300)], 1, False)),
            }
        }
    }
    packet = normalize(case, directory, {"root.json": simple_root(), "issue98.json": explicit})
    if packet is None:
        return
    coordinates = [entry["coordinate"] for entry in packet["issues"]]
    if coordinates != ["acme/payments#123", "acme/payments#98"]:
        fail(case, f"explicit issue missing or misordered: {coordinates}")
    if packet["explicit_issues"] != ["acme/payments#98"] or packet["issues"][1]["closing"] is not False:
        fail(case, "explicit issue not distinguished from closing issues")
    if [entry["coordinate"] for entry in packet["fingerprint"]["issues"]] != coordinates:
        fail(case, "explicit issue absent from the digest input")
    if not packet["complete"]:
        fail(case, f"unexpected gaps: {packet['gaps']}")


def case_shape_errors(directory: Path) -> None:
    """Unrecognized pages, two roots, and missing ids are exit 2 with the file named."""
    case = "shape errors"
    checks = {
        "no root": ({"only.json": pr_continuation(reviews=connection([], 0, False, None))}, "no root page"),
        "two roots": ({"a.json": simple_root(), "b.json": simple_root()}, "second root page"),
        "unknown shape": ({"root.json": simple_root(), "odd.json": {"data": {"viewer": {"login": "x"}}}}, "matches no documented query shape"),
        "not json": ({"root.json": simple_root()}, None),
        "missing file": ({"root.json": simple_root()}, "cannot read page"),
        "continuation for unfetched thread": (
            {"root.json": simple_root(), "t.json": thread_continuation("PRRT_9", connection([], 0, False, None))},
            None,
        ),
    }
    for name, (pages, fragment) in checks.items():
        paths = [write(directory, f"{name}-{file}", payload) for file, payload in pages.items()]
        if name == "not json":
            bad = directory / "bad.json"
            bad.write_text("", encoding="utf-8")  # a failed `gh` call saved nothing
            paths.append(str(bad))
        if name == "missing file":
            paths.append(str(directory / "never-written.json"))
        result = run("normalize", *paths)
        if fragment is None:
            # An unmatched continuation or an unreadable saved response is a
            # named gap (the fetch failed), not a shape error that stops the step.
            expected_gap = "the fetch failed" if name == "not json" else "matches no fetched thread"
            if result.returncode != 0 or expected_gap not in result.stderr:
                fail(case, f"{name}: expected a gap, got exit {result.returncode}: {result.stderr!r}")
            elif json.loads(result.stdout)["complete"]:
                fail(case, f"{name}: packet with a gap reported complete")
            continue
        if result.returncode != 2 or fragment not in result.stderr or result.stdout.strip():
            fail(case, f"{name}: expected exit 2 mentioning `{fragment}`, got {result.returncode}: {result.stderr!r}")
    missing_id = simple_root()
    del missing_id["data"]["repository"]["pullRequest"]["closingIssuesReferences"]["nodes"][0]["comments"]["nodes"][0]["fullDatabaseId"]
    result = run("normalize", write(directory, "missing-id.json", missing_id))
    if result.returncode != 2 or "missing stable numeric id" not in result.stderr:
        fail(case, f"missing comment id must exit 2, got {result.returncode}: {result.stderr!r}")
    # The deprecated integer databaseId still normalizes to the same id text.
    legacy = simple_root()
    comment = legacy["data"]["repository"]["pullRequest"]["closingIssuesReferences"]["nodes"][0]["comments"]["nodes"][0]
    del comment["fullDatabaseId"]
    comment["databaseId"] = 42
    packet = normalize(case, directory, {"legacy.json": legacy})
    if packet is not None and sorted(c["id"] for c in packet["issues"][0]["comments"]) != ["42", "7"]:
        fail(case, "integer databaseId did not normalize to the same id text")
    result = run("--self-test")
    if result.returncode != 0:
        fail(case, f"--self-test exited {result.returncode}: {result.stdout} {result.stderr}")


CASES = (
    case_root_fixture_fingerprints,
    case_two_page_connections,
    case_duplicate_page_items,
    case_missing_or_failed_continuation,
    case_later_state,
    case_explicit_issue_page,
    case_shape_errors,
)


def main() -> int:
    for script in (SCRIPT, FINGERPRINT):
        if not script.exists():
            print(f"test_forge_packet: {script} not found")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        for case in CASES:
            (directory / case.__name__).mkdir()
            case(directory / case.__name__)
    for failure in failures:
        print(failure)
    if failures:
        print(f"test_forge_packet: {len(failures)} case(s) failed")
        return 1
    print(f"test_forge_packet: {len(CASES)} case group(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
