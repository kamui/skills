#!/usr/bin/env python3
"""CLI fixtures for `forge_packet.py`: the packet, its `packet_context` identity, and the shortcut.

`SKILL.md` step 1 keeps the forge inputs as one packet that the review, the
`packet_context` digest, and the re-review all read. These cases drive the script
through `subprocess` on saved-response fixtures shaped like the documented
GraphQL queries and pin what issues #132 and #357 require of it:

- a fixture shaped like the root query with a real non-empty issue-comment
  list normalizes and hashes without synthesized identities;
- the digest covers the pull request's text and each linked issue's text,
  comments, availability and completeness, and the set of linked issues, in
  canonical order;
- the duplicate-review shortcut refuses a deleted issue comment, an added or
  removed older linked issue, supplied specs in either run, a trailer without the
  new markers or with only the older `context=`, and accepts equal complete inputs;
- two-page outer (reviews) and nested (issue comments, thread replies)
  connections merge to a complete packet;
- duplicate items at a page boundary collapse by stable id, and a duplicate
  whose content differs is reported;
- a missing or failed continuation is a named gap, never complete coverage,
  and the truncated packet cannot pass the later-state check or share a digest
  with the complete one;
- edited candidate reviews, original comments, and marked replies are later
  state; unedited publication replies and their empty containers are excluded;
- an undated thread resolution is never silently unchanged, whether the thread
  is resolved now or predates the review and may have been un-resolved since;
- a page carrying the forge's HTTP error body is a named gap, not exit 2.

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
sys.path.insert(0, str(HERE))
import forge_packet  # noqa: E402  the digest the shortcut and the finalizer both derive
import render_review  # noqa: E402

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


def digest(case: str, directory: Path, packet: dict[str, Any]) -> Optional[str]:
    try:
        return forge_packet.packet_context(packet)
    except forge_packet.PageError as error:
        fail(case, f"packet_context refused the packet: {error}")
        return None


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
    first = digest(case, directory, packet)
    reordered = copy.deepcopy(packet)
    reordered["fingerprint"]["issues"][0]["comments"].reverse()
    reordered["fingerprint"] = dict(reversed(list(reordered["fingerprint"].items())))
    if first is None or first != digest(case, directory, reordered) or len(first) != 64:
        fail(case, "the digest depends on key or comment order")


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
    # `gh api` writes the forge's HTTP error body on a rate limit or a 5xx: a
    # named gap for the pages that did arrive, not a shape error that stops step 1.
    http = {"message": "You have exceeded a secondary rate limit", "documentation_url": "https://docs.github.com"}
    packet = normalize(case, directory, {"root.json": first, "http-error.json": http})
    if packet is not None and not any(
        "HTTP error: You have exceeded a secondary rate limit" in gap and "http-error.json" in gap
        for gap in packet["gaps"]
    ):
        fail(case, f"HTTP error body not named as a gap: {packet['gaps'] if packet else None}")
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
    """Edits to replies and original comments are later state; undated thread state is never silent."""
    case = "later-state"
    threads = connection(
        [
            thread(
                "PRRT_1",
                connection(
                    [
                        thread_comment(5000, T0, "900", edited=AFTER),
                        thread_comment(5001, BEFORE, "900", reply_to="5000", author="author", edited=AFTER),
                    ],
                    2,
                    False,
                ),
            ),
            thread("PRRT_2", connection([thread_comment(6000, T0, "900")], 1, False), resolved=True),
            thread("PRRT_3", connection([thread_comment(7000, BEFORE, "800")], 1, False), resolved=False),
            thread("PRRT_4", connection([thread_comment(8000, T0, "900")], 1, False), resolved=False),
        ],
        4,
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
    if not any(line.startswith("thread-comment thread=PRRT_1 id=5000") for line in lines):
        fail(case, f"the candidate's edited original comment was not reported: {lines}")
    if any("id=6000" in line or "id=8000" in line for line in lines):
        fail(case, f"the candidate's unedited original comment was reported: {lines}")
    if any(line.startswith("review id=800") for line in lines):
        fail(case, f"an earlier review was reported as later state: {lines}")
    if not any(line.startswith("thread-state thread=PRRT_2") and "resolved:" in line for line in lines):
        fail(case, f"a resolved thread without a timestamp was silently treated as unchanged: {lines}")
    if not any(line.startswith("thread-state thread=PRRT_3") and "unresolved:" in line for line in lines):
        fail(case, f"a pre-existing thread that may have been un-resolved was silent: {lines}")
    if any(line.startswith("thread-state thread=PRRT_4") for line in lines):
        fail(case, f"a thread the candidate review created and left unresolved drew a line: {lines}")
    # With the edits undone, the resolved thread unresolved, and no thread left
    # from an earlier review, nothing is later: exit 0.
    clean = copy.deepcopy(page)
    pr = clean["data"]["repository"]["pullRequest"]
    original = pr["reviewThreads"]["nodes"][0]["comments"]["nodes"][0]
    original["lastEditedAt"] = None
    original["updatedAt"] = T0
    reply = pr["reviewThreads"]["nodes"][0]["comments"]["nodes"][1]
    reply["lastEditedAt"] = None
    reply["updatedAt"] = BEFORE
    pr["reviewThreads"]["nodes"][1]["isResolved"] = False
    threads = pr["reviewThreads"]
    threads["nodes"] = [node for node in threads["nodes"] if node["id"] != "PRRT_3"]
    threads["totalCount"] = 3
    clean_packet = normalize(case, directory, {"clean.json": clean})
    if clean_packet is not None:
        clean_path = write(directory, "clean-packet.json", clean_packet)
        result = run("later-state", clean_path, "--review", "900")
        if result.returncode != 0 or result.stdout.strip():
            fail(case, f"clean packet should exit 0 silently, got {result.returncode}: {result.stdout!r}")
        # Issue and pull-request body edits are later state as well.
        edited = copy.deepcopy(clean)
        edited["data"]["repository"]["pullRequest"]["lastEditedAt"] = AFTER
        edited["data"]["repository"]["pullRequest"]["closingIssuesReferences"]["nodes"][0]["lastEditedAt"] = AFTER
        edited_packet = normalize(case, directory, {"edited.json": edited})
        if edited_packet is not None:
            result = run("later-state", write(directory, "edited-packet.json", edited_packet), "--review", "900")
            out = result.stdout
            if result.returncode != 1 or "pr edited" not in out or "issue acme/payments#123 edited" not in out:
                fail(case, f"pr and issue body edits not reported: {out!r}")
        # --after overrides the review's own submission time: the clean packet is
        # silent at the review's own cutoff, so an earlier cutoff is the only
        # thing that can make this exit 1.
        result = run("later-state", clean_path, "--review", "900", "--after", "2026-01-01T00:00:00Z")
        if result.returncode != 1:
            fail(case, "--after cutoff was ignored")
    result = run("later-state", path, "--review", "999")
    if result.returncode != 2 or "not in the packet" not in result.stderr:
        fail(case, f"unknown review id must exit 2: {result.returncode} {result.stderr!r}")


def case_publication_artifacts(directory: Path) -> None:
    """Only unedited marked publication artifacts are silent, never author dispositions."""
    marker = "<!-- prior-item id=bug/retry classification=fixed head=" + "a" * 40 + " -->"
    reply = thread_comment(5002, AFTER, "901", reply_to="5000")
    reply["body"] = "Fixed.\n\n" + marker
    container = review(901, AFTER)
    container["body"] = ""
    page = root(
        closing=connection([], 0, False),
        reviews=connection([review(800, BEFORE), review(900, T0), container], 3, False),
        threads=connection([thread("PRRT_1", connection([
            thread_comment(5000, BEFORE, "800"), reply,
        ], 2, False), resolved=True)], 1, False),
    )
    state_line = (
        "thread-state thread=PRRT_1 path=src/retry.ts resolved: no timestamp; "
        "settle against the candidate review's recorded prior-item classification or treat as later state"
    )

    def check(name: str, fixture: dict[str, Any], expected: list[str]) -> None:
        packet = normalize(name, directory, {name + ".json": fixture})
        if packet is None:
            return
        result = run("later-state", write(directory, name + "-packet.json", packet), "--review", "900")
        if result.returncode != 1 or result.stdout.splitlines() != expected:
            fail(name, f"expected exit 1 and {expected!r}, got {result.returncode}: {result.stdout!r} {result.stderr!r}")

    check("publication shape", page, [state_line])
    for classification in ("accepted", "obsolete", "still-open"):
        variant = copy.deepcopy(page)
        variant["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"][0]["comments"]["nodes"][1]["body"] = marker.replace("fixed", classification)
        check(classification, variant, [state_line])

    for name in ("edited reply", "nonempty container", "edited container", "mixed container",
                 "author disposition", "wrong head", "wrong author", "malformed marker",
                 "nontrailer marker", "edited candidate", "bot suffix", "empty container"):
        variant = copy.deepcopy(page)
        pr = variant["data"]["repository"]["pullRequest"]
        comments = pr["reviewThreads"]["nodes"][0]["comments"]
        marked = comments["nodes"][1]
        box = pr["reviews"]["nodes"][2]
        review_line = f"review id=901 by reviewer at {AFTER}"
        reply_line = f"reply thread=PRRT_1 id=5002 at {AFTER}"
        expected = [review_line, reply_line]
        if name == "edited reply":
            marked["lastEditedAt"] = AFTER
        elif name == "nonempty container":
            box["body"] = "Independent review text"
            expected = [review_line, state_line]
        elif name == "edited container":
            box["lastEditedAt"] = AFTER
            expected = [review_line, state_line]
        elif name == "mixed container":
            comments["nodes"].append(thread_comment(5003, AFTER, "901", reply_to="5000"))
            comments["totalCount"] = 3
            expected = [review_line, f"reply thread=PRRT_1 id=5003 at {AFTER}"]
        elif name == "author disposition":
            marked["body"] = "Declined.\n<!-- reply to=bug/retry disposition=declined head=" + "a" * 40 + " -->"
        elif name == "wrong head":
            marked["body"] = marker.replace("a" * 40, "b" * 40)
        elif name == "wrong author":
            marked["author"] = {"login": "someone-else"}
        elif name == "malformed marker":
            marked["body"] = marker.replace("classification=fixed", "classification=implemented")
        elif name == "nontrailer marker":
            marked["body"] = marker + "\nAdditional text"
        elif name == "edited candidate":
            pr["reviews"]["nodes"][1]["lastEditedAt"] = AFTER
            expected = [f"review id=900 by reviewer at {AFTER}", state_line]
        elif name == "bot suffix":
            marked["author"] = {"login": "reviewer[bot]"}
            box["author"] = {"login": "reviewer[bot]"}
            expected = [state_line]
        elif name == "empty container":
            comments["nodes"].pop()
            comments["totalCount"] = 1
            expected = [review_line, state_line]
        check(name, variant, expected)


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


def case_packet_context_sensitivity(directory: Path) -> None:
    """Every intent field moves the digest; ordering and fields outside the intent do not."""
    case = "packet context sensitivity"
    packet = normalize(case, directory, {"root.json": simple_root()})
    if packet is None:
        return
    base = digest(case, directory, packet)

    def changed(mutate) -> Optional[str]:
        value = copy.deepcopy(packet)
        mutate(value)
        return digest(case, directory, value)

    intent = packet["fingerprint"]
    for name, mutate in (
        ("pr title", lambda p: p["fingerprint"]["pr"].update(title="Other title")),
        ("pr body", lambda p: p["fingerprint"]["pr"].update(body="Closes #124.")),
        ("issue title", lambda p: p["fingerprint"]["issues"][0].update(title="Other")),
        ("issue body", lambda p: p["fingerprint"]["issues"][0].update(body="Other criterion.")),
        ("issue coordinate", lambda p: p["fingerprint"]["issues"][0].update(coordinate="acme/payments#999")),
        ("comment body", lambda p: p["fingerprint"]["issues"][0]["comments"][0].update(body="edited")),
        ("comment edit time", lambda p: p["fingerprint"]["issues"][0]["comments"][0].update(updated_at=AFTER)),
        ("comment author", lambda p: p["fingerprint"]["issues"][0]["comments"][0].update(author="someone")),
        ("deleted comment", lambda p: p["fingerprint"]["issues"][0]["comments"].pop()),
        ("comments unavailable", lambda p: p["fingerprint"]["issues"][0].update(comments=[], comments_available=False)),
        ("comments truncated", lambda p: p["fingerprint"]["issues"][0].update(comments_complete=False)),
        ("added linked issue", lambda p: p["fingerprint"]["issues"].append(dict(intent["issues"][0], coordinate="acme/payments#124"))),
        ("removed linked issue", lambda p: p["fingerprint"]["issues"].clear()),
    ):
        if changed(mutate) == base:
            fail(case, f"{name} did not change the digest")
    empty = copy.deepcopy(packet)
    empty["fingerprint"]["issues"][0]["comments"] = []
    unavailable = copy.deepcopy(empty)
    unavailable["fingerprint"]["issues"][0]["comments_available"] = False
    if digest(case, directory, empty) == digest(case, directory, unavailable):
        fail(case, "an empty comment list and unavailable comments share a digest")
    two = copy.deepcopy(packet)
    two["fingerprint"]["issues"].append(dict(intent["issues"][0], coordinate="acme/payments#124"))
    swapped = copy.deepcopy(two)
    swapped["fingerprint"]["issues"].reverse()
    if digest(case, directory, two) != digest(case, directory, swapped):
        fail(case, "linked-issue order changed the digest")
    for name, mutate in (
        ("review body", lambda p: p["reviews"][0].update(body="edited review")),
        ("pr edit time", lambda p: p["pr"].update(last_edited_at=AFTER)),
    ):
        if changed(mutate) != base:
            fail(case, f"{name} is outside the intent but changed the digest")
    result = run("shortcut", write(directory, "bad-packet.json", {"schema": "forge-packet/0"}), "--review", "900",
                 "--merge-base", "c" * 40, "--supplied-inputs", "no")
    if result.returncode != 2:
        fail(case, f"a packet of another schema must exit 2, got {result.returncode}: {result.stdout!r}")


def trailer(digest_value: Optional[str], supplied: Optional[str] = "no", *, workflow: Optional[str] = None,
            context: Optional[str] = None, head: str = "a" * 40, merge_base: str = "c" * 40) -> str:
    fields = [f"head={head}", "base-ref=main", f"base-sha={'b' * 40}", f"merge-base={merge_base}",
              f"workflow={workflow or render_review.WORKFLOW}"]
    if context is not None:
        fields.append(f"context={context}")
    if digest_value is not None:
        fields.append(f"packet_context={digest_value}")
    if supplied is not None:
        fields.append(f"supplied_inputs={supplied}")
    return "**Approved (advisory)** — no findings.\n\n<!-- review-run " + " ".join(fields + ["issues=acme/payments#123", "coverage=complete"]) + " -->"


def case_shortcut(directory: Path) -> None:
    """The scripted identity decides duplicates later-state cannot see; equal complete inputs qualify."""
    case = "duplicate-review shortcut"

    def pages(comments: list[int], extra_issues: tuple[int, ...] = (), body: str = "") -> dict[str, Any]:
        issues = [issue(123, connection([issue_comment(n) for n in comments], len(comments), False))]
        issues += [issue(n, connection([], 0, False, None)) for n in extra_issues]
        candidate = review(900, T0)
        candidate["body"] = body
        return root(closing=connection(issues, len(issues), False), reviews=connection([candidate], 1, False),
                    threads=connection([thread("PRRT_1", connection([thread_comment(5000, T0, "900")], 1, False))], 1, False))

    def packet_digest(comments: list[int], extra_issues: tuple[int, ...] = ()) -> Optional[str]:
        packet = normalize(case, directory, {f"prior-{len(comments)}-{len(extra_issues)}.json": pages(comments, extra_issues)})
        return None if packet is None else digest(case, directory, packet)

    prior = packet_digest([42, 7])
    prior_two = packet_digest([42, 7], (124,))
    count = 0

    def shortcut(body: str, comments: list[int] = (42, 7), extra_issues: tuple[int, ...] = (), supplied: str = "no",
                 merge_base: str = "c" * 40) -> subprocess.CompletedProcess[str]:
        nonlocal count
        count += 1
        path = write(directory, f"shortcut-{count}.json", normalize(case, directory, {f"now-{count}.json": pages(list(comments), extra_issues, body)}))
        return run("shortcut", path, "--review", "900", "--merge-base", merge_base, "--supplied-inputs", supplied)

    same = shortcut(trailer(prior))
    if same.returncode != 0 or same.stdout:
        fail(case, f"equal complete inputs must qualify, got {same.returncode}: {same.stdout!r}")
    expectations = [
        ("deleted older issue comment", shortcut(trailer(prior), comments=[42]), "identity packet_context:"),
        ("added older linked issue", shortcut(trailer(prior), extra_issues=(124,)), "identity packet_context:"),
        ("removed older linked issue", shortcut(trailer(prior_two)), "identity packet_context:"),
        ("current-only supplied spec", shortcut(trailer(prior), supplied="yes"), "this run has caller-supplied issues or specs"),
        ("prior-only supplied spec", shortcut(trailer(prior, "yes")), "review 900 used caller-supplied issues or specs"),
        ("absent markers", shortcut(trailer(None, None)), "carries no packet_context and supplied_inputs markers;"),
        ("older context= trailer", shortcut(trailer(None, None, context=prior)), "(an older `context=` trailer)"),
        ("digest without its supplied-inputs marker", shortcut(trailer(prior, None)), "carries no packet_context and supplied_inputs"),
        ("no trailer", shortcut("Looks fine."), "carries no review-run trailer"),
        ("other workflow", shortcut(trailer(prior, workflow="v5b-24")), "identity workflow:"),
        ("other merge-base", shortcut(trailer(prior), merge_base="d" * 40), "identity merge-base:"),
        ("other head", shortcut(trailer(prior, head="e" * 40)), "identity head:"),
    ]
    for name, result, needle in expectations:
        if result.returncode != 1 or needle not in result.stdout:
            fail(case, f"{name}: expected exit 1 naming {needle!r}, got {result.returncode}: {result.stdout!r}")
        elif any(not line.startswith("identity ") for line in result.stdout.splitlines()):
            fail(case, f"{name}: later-state saw what only the digest or markers can: {result.stdout!r}")
    # The digest does not waive later state: an edited issue after the review still stands in the way.
    edited = pages([42, 7], body=trailer(prior))
    edited["data"]["repository"]["pullRequest"]["closingIssuesReferences"]["nodes"][0]["lastEditedAt"] = AFTER
    path = write(directory, "edited.json", normalize(case, directory, {"edited-page.json": edited}))
    result = run("shortcut", path, "--review", "900", "--merge-base", "c" * 40, "--supplied-inputs", "no")
    if result.returncode != 1 or "issue acme/payments#123 edited" not in result.stdout:
        fail(case, f"a later issue edit must still defeat the shortcut, got {result.returncode}: {result.stdout!r}")


CASES = (
    case_root_fixture_fingerprints,
    case_two_page_connections,
    case_duplicate_page_items,
    case_missing_or_failed_continuation,
    case_later_state,
    case_publication_artifacts,
    case_explicit_issue_page,
    case_shape_errors,
    case_packet_context_sensitivity,
    case_shortcut,
)


def main() -> int:
    for script in (SCRIPT,):
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
