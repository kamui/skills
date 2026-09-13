#!/usr/bin/env python3
"""Normalize saved forge responses into one persisted review packet.

`SKILL.md` step 1 fetches the pull request, its closing issues with their
comments, and its reviews, review threads, and comments with `gh api graphql`,
saving every response page to a file. This script turns those saved pages into
one logical collection of the reviewed forge inputs -- the packet -- with
stable numeric ids, edit timestamps, and per-connection completeness. It reads
only the files it is given: it never calls `gh`, never touches the network, and
never decides a review judgment.

Usage:
    python3 scripts/forge_packet.py normalize PAGE [PAGE ...] > packet.json
    python3 scripts/forge_packet.py later-state packet.json --review ID
        [--after ISO-8601]
    python3 scripts/forge_packet.py --self-test

`normalize` accepts the raw stdout of each `gh api graphql` call from the
documented root query and its continuation queries, in any order, and prints
the packet as one JSON object. Its exit is 0 even when a connection is
incomplete: the packet then reports `"complete": false` and names every gap,
because the reviewer still needs the pages that did arrive. A saved response
that carries GraphQL errors, or is empty or not JSON because the call failed,
is a named gap for the same reason, as is a page carrying the forge's HTTP
error body instead of a response. A file that cannot be opened, or a JSON page
that matches no documented query shape, is exit 2.

`later-state` answers the output contract's later-state question for the
candidate review `--review ID` (its `fullDatabaseId`): it prints one line per
pull-request, issue, review, comment, or reply created or edited after that
review's submission time (or after `--after`), one line per packet gap, and one
`thread-state` line per thread whose undated resolved state cannot be ruled
unchanged and that carries no later comment: every resolved thread, and every
thread predating the review, since one resolved when the review ran can have
been un-resolved since without leaving a timestamp. A thread the candidate
review created and left unresolved is the one silent case. Only original output
is excluded: subsequent edits to the candidate review or its comments still count. Exit 0 means the packet is complete
and nothing later exists, so the deduplication rule may consider the candidate;
exit 1 means the lines on stdout stand between the run and that shortcut.

Recognized page shapes (each response's `data` wrapper is optional):

- root page: `repository.pullRequest` carrying `title`, exactly one per run;
- pull-request connection continuation: `repository.pullRequest` without
  `title`, carrying any of `closingIssuesReferences`, `reviews`,
  `reviewThreads`, or `comments`;
- issue page: `repository.issue` carrying `title` (an explicitly referenced
  issue outside the closing set) or without it (an issue-comment continuation
  for the issue named by `number`);
- thread continuation: `node` carrying the thread `id` and `comments`.

Every bounded connection carries `totalCount`, `pageInfo{hasNextPage
endCursor}`, and `nodes`. Nodes are merged across pages by stable id; a
connection is complete only when every page agrees on `totalCount`, the
distinct ids equal that count, some page reports `hasNextPage: false`, and no
page carried a GraphQL error or an HTTP failure. Anything else is a named gap. The packet's
`fingerprint` object is the `pr` and `issues` input of
`context_fingerprint.py`, so `context_fingerprint.py --packet packet.json`
hashes the same normalized records the review and the re-review read.

Exit codes:
    0  the packet or an empty later-state report was written to stdout
    1  later-state lines were written to stdout, or a --self-test assertion
       failed
    2  a page file cannot be opened or matches no documented shape; the file
       is named on stderr
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from typing import Any, Optional

SCHEMA = "forge-packet/1"
PR_CONNECTIONS = ("closingIssuesReferences", "reviews", "reviewThreads", "comments")


class PageError(Exception):
    """A page could not be read or recognized."""


# --- small value helpers ----------------------------------------------------


def text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def optional_text(value: Any) -> Optional[str]:
    return value if isinstance(value, str) else None


def login(value: Any) -> str:
    if isinstance(value, dict):
        return text(value.get("login"))
    return ""


def numeric_id(value: Any, where: str) -> str:
    """Return a stable numeric id as a decimal string.

    GitHub returns `fullDatabaseId` as a BigInt string and the deprecated
    `databaseId` as an integer; both normalize to the same text so the digest
    does not depend on which one a page carried.
    """
    if isinstance(value, bool):
        raise PageError(f"{where}: id must be numeric, got a boolean")
    if isinstance(value, int) and value >= 0:
        return str(value)
    if isinstance(value, str) and value.isascii() and value.isdigit():
        return str(int(value))
    raise PageError(f"{where}: missing stable numeric id (fullDatabaseId)")


def node_id(node: dict[str, Any], where: str) -> str:
    for key in ("fullDatabaseId", "databaseId"):
        if node.get(key) is not None:
            return numeric_id(node[key], where)
    raise PageError(f"{where}: missing stable numeric id (fullDatabaseId)")


def parse_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def coordinate_from_url(url: str) -> Optional[str]:
    """`https://github.com/o/r/issues/12` -> `o/r#12`."""
    parts = url.rstrip("/").split("/")
    if len(parts) >= 5 and parts[-2] in ("issues", "pull") and parts[-1].isdigit():
        return f"{parts[-4]}/{parts[-3]}#{parts[-1]}"
    return None


def repo_slug(url: str) -> Optional[str]:
    parts = url.rstrip("/").split("/")
    if len(parts) >= 2 and parts[-1] and parts[-2]:
        return f"{parts[-2]}/{parts[-1]}"
    return None


# --- connection merging -----------------------------------------------------


class Connection:
    """Pages of one bounded connection, merged by stable id."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pages = 0
        self.total_counts: list[Optional[int]] = []
        self.has_next: list[Optional[bool]] = []
        self.end_cursors: list[Optional[str]] = []
        self.errors: list[str] = []
        self.items: dict[str, dict[str, Any]] = {}
        self.order: list[str] = []
        self.conflicts: list[str] = []

    def add_page(self, connection: Any, key: Any, where: str) -> list[tuple[str, dict[str, Any]]]:
        """Merge one page; return (id, raw node) pairs for nested processing."""
        if connection is None:
            self.errors.append(f"{where}: connection missing from page")
            return []
        if not isinstance(connection, dict):
            raise PageError(f"{where}: connection must be an object")
        self.pages += 1
        total = connection.get("totalCount")
        self.total_counts.append(total if isinstance(total, int) and not isinstance(total, bool) else None)
        info = connection.get("pageInfo")
        has_next = info.get("hasNextPage") if isinstance(info, dict) else None
        self.has_next.append(has_next if isinstance(has_next, bool) else None)
        cursor = info.get("endCursor") if isinstance(info, dict) else None
        self.end_cursors.append(optional_text(cursor))
        if has_next is True and not text(cursor):
            self.errors.append(f"{where}: continuation has no endCursor")
        if not isinstance(has_next, bool):
            self.errors.append(f"{where}: page omitted boolean hasNextPage")
        nodes = connection.get("nodes")
        if nodes is None:
            nodes = []
        if not isinstance(nodes, list):
            raise PageError(f"{where}: nodes must be an array")
        pairs: list[tuple[str, dict[str, Any]]] = []
        for index, node in enumerate(nodes):
            if node is None:
                # GitHub returns null for a node the token cannot see.
                self.errors.append(f"{where}: nodes[{index}] is null (inaccessible item)")
                continue
            if not isinstance(node, dict):
                raise PageError(f"{where}: nodes[{index}] must be an object")
            item_id = key(node, f"{where}.nodes[{index}]")
            pairs.append((item_id, node))
        return pairs

    def put(self, item_id: str, record: dict[str, Any], comparable: dict[str, Any]) -> None:
        existing = self.items.get(item_id)
        if existing is None:
            self.items[item_id] = record
            self.order.append(item_id)
            return
        if existing.get("_comparable") != comparable:
            self.conflicts.append(item_id)
            # Keep the later edit so the packet reflects the latest state seen.
            if text(comparable.get("updated_at")) >= text(existing["_comparable"].get("updated_at")):
                record["_comparable"] = comparable
                self.items[item_id] = record
        # An identical duplicate at a page boundary is dropped silently.

    def gaps(self) -> list[str]:
        gaps: list[str] = []
        if self.pages == 0:
            gaps.append(f"{self.name}: no page fetched")
            return gaps
        gaps.extend(f"{self.name}: {error}" for error in self.errors)
        counts = {count for count in self.total_counts if count is not None}
        if None in self.total_counts:
            gaps.append(f"{self.name}: a page omitted totalCount")
        if len(counts) > 1:
            gaps.append(
                f"{self.name}: totalCount changed between pages "
                f"({', '.join(str(count) for count in sorted(counts))}); refetch"
            )
        distinct = len(self.items)
        no_last_page = False not in self.has_next
        if True not in self.has_next and no_last_page:
            gaps.append(f"{self.name}: no page reported pageInfo.hasNextPage")
        if len(counts) == 1:
            total = counts.pop()
            if distinct < total and no_last_page:
                gaps.append(
                    f"{self.name}: {distinct} of {total} items fetched; continuation missing or failed"
                )
            elif distinct < total:
                gaps.append(
                    f"{self.name}: {distinct} of {total} items fetched although a page reports "
                    "no further page; refetch"
                )
            elif distinct > total:
                gaps.append(
                    f"{self.name}: {distinct} distinct items exceed totalCount {total}; refetch"
                )
            elif no_last_page:
                gaps.append(
                    f"{self.name}: all {total} items fetched but no page reports hasNextPage: false; refetch"
                )
        elif no_last_page:
            gaps.append(f"{self.name}: last fetched page reports hasNextPage: true; continuation missing")
        for item_id in self.conflicts:
            gaps.append(
                f"{self.name}: item {item_id} differs between pages; the later edit was kept"
            )
        return gaps

    def records(self) -> list[dict[str, Any]]:
        """Records in forge order: by creation or submission time, then id."""
        out: list[dict[str, Any]] = []
        for item_id in self.order:
            record = dict(self.items[item_id])
            record.pop("_comparable", None)
            out.append(record)

        def sort_key(record: dict[str, Any]) -> tuple[str, int, str]:
            stamp = text(record.get("created_at") or record.get("submitted_at"))
            item_id = text(record.get("id"))
            numeric = int(item_id) if item_id.isdigit() else -1
            return (stamp, numeric, item_id)

        out.sort(key=sort_key)
        return out

    def coverage(self) -> dict[str, Any]:
        counts = {count for count in self.total_counts if count is not None}
        return {
            "pages": self.pages,
            "end_cursors": sorted(set(c for c in self.end_cursors if c is not None)),
            "total_count": counts.pop() if len(counts) == 1 else None,
            "fetched": len(self.items),
            "complete": not self.gaps(),
            "gaps": self.gaps(),
        }


# --- record normalizers -----------------------------------------------------


def comment_record(node: dict[str, Any], where: str) -> dict[str, Any]:
    record = {
        "id": node_id(node, where),
        "author": login(node.get("author")),
        "body": text(node.get("body")),
        "created_at": text(node.get("createdAt")),
        "updated_at": text(node.get("updatedAt")),
        "last_edited_at": optional_text(node.get("lastEditedAt")),
        "url": text(node.get("url")),
    }
    return record


def review_record(node: dict[str, Any], where: str) -> dict[str, Any]:
    commit = node.get("commit")
    return {
        "id": node_id(node, where),
        "author": login(node.get("author")),
        "state": text(node.get("state")),
        "body": text(node.get("body")),
        "submitted_at": text(node.get("submittedAt")),
        "updated_at": text(node.get("updatedAt")),
        "last_edited_at": optional_text(node.get("lastEditedAt")),
        "commit": text(commit.get("oid")) if isinstance(commit, dict) else "",
        "url": text(node.get("url")),
    }


def thread_comment_record(node: dict[str, Any], where: str) -> dict[str, Any]:
    record = comment_record(node, where)
    reply_to = node.get("replyTo")
    review = node.get("pullRequestReview")
    record["reply_to"] = node_id(reply_to, f"{where}.replyTo") if isinstance(reply_to, dict) else None
    record["review_id"] = node_id(review, f"{where}.pullRequestReview") if isinstance(review, dict) else None
    return record


def comparable(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "url"}


# --- packet assembly --------------------------------------------------------


class Packet:
    def __init__(self) -> None:
        self.root: Optional[dict[str, Any]] = None
        self.root_file = ""
        self.repository_url = ""
        self.closing = Connection("closingIssuesReferences")
        self.reviews = Connection("reviews")
        self.threads = Connection("reviewThreads")
        self.pr_comments = Connection("comments")
        self.issue_comments: dict[str, Connection] = {}
        self.issue_meta: dict[str, dict[str, Any]] = {}
        self.issue_order: list[str] = []
        self.explicit_issues: list[str] = []
        self.thread_comments: dict[str, Connection] = {}
        self.thread_meta: dict[str, dict[str, Any]] = {}
        self.page_errors: list[str] = []
        self.unmatched: list[str] = []

    # -- page dispatch --

    def add_page(self, payload: Any, where: str) -> None:
        if isinstance(payload, UnreadablePage):
            self.page_errors.append(f"{where}: {payload.reason}; the fetch failed")
            return
        if not isinstance(payload, dict):
            raise PageError(f"{where}: response must be a JSON object")
        errors = payload.get("errors")
        if isinstance(errors, list) and errors:
            messages = "; ".join(
                text(error.get("message")) if isinstance(error, dict) else str(error) for error in errors
            )
            self.page_errors.append(f"{where}: GraphQL errors: {messages}")
        elif "message" in payload and not any(key in payload for key in ("data", "repository", "node")):
            # `gh api` writes the forge's JSON error body on an HTTP failure --
            # a secondary rate limit or a 5xx -- so the page is a failed fetch,
            # not an unrecognized shape.
            self.page_errors.append(f"{where}: HTTP error: {text(payload.get('message'))}; the fetch failed")
            return
        data = payload.get("data", payload)
        if not isinstance(data, dict):
            if self.page_errors and self.page_errors[-1].startswith(where):
                return
            raise PageError(f"{where}: response has no data object")
        repository = data.get("repository")
        node = data.get("node")
        if isinstance(repository, dict) and isinstance(repository.get("pullRequest"), dict):
            pull_request = repository["pullRequest"]
            if "title" in pull_request:
                self.add_root(repository, pull_request, where)
            else:
                self.add_pr_continuation(pull_request, where)
            return
        if isinstance(repository, dict) and isinstance(repository.get("issue"), dict):
            self.add_issue_page(repository, repository["issue"], where)
            return
        if isinstance(node, dict) and "comments" in node:
            self.add_thread_continuation(node, where)
            return
        if self.page_errors and self.page_errors[-1].startswith(where):
            return  # a failed page with null data is a recorded gap, not a shape error
        raise PageError(f"{where}: matches no documented query shape")

    def add_root(self, repository: dict[str, Any], pull_request: dict[str, Any], where: str) -> None:
        if self.root is not None:
            raise PageError(f"{where}: second root page (the first was {self.root_file})")
        self.root_file = where
        self.repository_url = text(repository.get("url"))
        base_repository = pull_request.get("baseRepository")
        self.root = {
            "title": text(pull_request.get("title")),
            "body": text(pull_request.get("body")),
            "state": text(pull_request.get("state")),
            "merged": pull_request.get("merged") if isinstance(pull_request.get("merged"), bool) else None,
            "is_draft": pull_request.get("isDraft") if isinstance(pull_request.get("isDraft"), bool) else None,
            "base_ref": text(pull_request.get("baseRefName")),
            "base_sha": text(pull_request.get("baseRefOid")),
            "head_sha": text(pull_request.get("headRefOid")),
            "updated_at": text(pull_request.get("updatedAt")),
            "last_edited_at": optional_text(pull_request.get("lastEditedAt")),
            "repository_url": text(base_repository.get("url")) if isinstance(base_repository, dict) else "",
        }
        self.add_pr_continuation(pull_request, where, root=True)

    def add_pr_continuation(self, pull_request: dict[str, Any], where: str, *, root: bool = False) -> None:
        present = [name for name in PR_CONNECTIONS if name in pull_request]
        if not present:
            raise PageError(f"{where}: pullRequest page carries no documented connection")
        for name in PR_CONNECTIONS:
            if name not in pull_request and not root:
                continue
            connection = pull_request.get(name)
            spot = f"{where}.pullRequest.{name}"
            if name == "closingIssuesReferences":
                for coordinate, node in self.closing.add_page(connection, self.issue_key, spot):
                    entry = {"coordinate": coordinate, "_comparable": {"coordinate": coordinate}}
                    self.closing.put(coordinate, entry, entry["_comparable"])
                    self.add_issue(node, spot, explicit=False)
            elif name == "reviews":
                for _, node in self.reviews.add_page(connection, node_id, spot):
                    record = review_record(node, spot)
                    record["_comparable"] = comparable(record)
                    self.reviews.put(record["id"], record, record["_comparable"])
            elif name == "reviewThreads":
                for thread_id, node in self.threads.add_page(connection, self.thread_key, spot):
                    self.add_thread(thread_id, node, spot)
            elif name == "comments":
                for _, node in self.pr_comments.add_page(connection, node_id, spot):
                    record = comment_record(node, spot)
                    record["_comparable"] = comparable(record)
                    self.pr_comments.put(record["id"], record, record["_comparable"])

    # -- issues --

    def issue_key(self, node: dict[str, Any], where: str) -> str:
        return self.issue_coordinate(node, where)

    def issue_coordinate(self, node: dict[str, Any], where: str) -> str:
        number = node.get("number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise PageError(f"{where}: issue lacks a number")
        coordinate = coordinate_from_url(text(node.get("url")))
        if coordinate is None:
            slug = repo_slug(self.repository_url) if self.repository_url else None
            if slug is None:
                raise PageError(f"{where}: issue lacks a url and the repository url is unknown")
            coordinate = f"{slug}#{number}"
        return coordinate

    def add_issue(self, node: dict[str, Any], where: str, *, explicit: bool) -> None:
        coordinate = self.issue_coordinate(node, where)
        meta = {
            "coordinate": coordinate,
            "number": node.get("number"),
            "title": text(node.get("title")),
            "body": text(node.get("body")),
            "updated_at": text(node.get("updatedAt")),
            "last_edited_at": optional_text(node.get("lastEditedAt")),
            "url": text(node.get("url")),
            "closing": not explicit,
        }
        existing = self.issue_meta.get(coordinate)
        if existing is None:
            self.issue_meta[coordinate] = meta
            self.issue_order.append(coordinate)
        else:
            if not explicit:
                existing["closing"] = True
            for key in ("title", "body", "updated_at", "last_edited_at", "url"):
                if meta[key] and not existing.get(key):
                    existing[key] = meta[key]
        if explicit and coordinate not in self.explicit_issues:
            self.explicit_issues.append(coordinate)
        self.add_issue_comments(coordinate, node.get("comments"), f"{where}.comments")

    def add_issue_comments(self, coordinate: str, connection: Any, where: str) -> None:
        conn = self.issue_comments.setdefault(coordinate, Connection(f"issue {coordinate} comments"))
        for _, node in conn.add_page(connection, node_id, where):
            record = comment_record(node, where)
            record["_comparable"] = comparable(record)
            conn.put(record["id"], record, record["_comparable"])

    def add_issue_page(self, repository: dict[str, Any], issue: dict[str, Any], where: str) -> None:
        if "title" in issue:
            self.add_issue(issue, f"{where}.issue", explicit=True)
            return
        number = issue.get("number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise PageError(f"{where}: issue continuation lacks a number")
        coordinate = coordinate_from_url(text(issue.get("url")))
        if coordinate is None:
            # Match the continuation to a known issue by number within the
            # pull request's repository; a continuation for an unknown issue
            # is a shape error, since its title and body were never fetched.
            slug = repo_slug(text(repository.get("url")) or self.repository_url)
            coordinate = f"{slug}#{number}" if slug else None
            if coordinate not in self.issue_meta:
                candidates = [
                    known for known in self.issue_order if self.issue_meta[known]["number"] == number
                ]
                if len(candidates) == 1:
                    coordinate = candidates[0]
        if coordinate is None or coordinate not in self.issue_meta:
            self.unmatched.append(
                f"{where}: issue-comment continuation for #{number} matches no fetched issue"
            )
            return
        self.add_issue_comments(coordinate, issue.get("comments"), f"{where}.issue.comments")

    # -- threads --

    def thread_key(self, node: dict[str, Any], where: str) -> str:
        thread_id = node.get("id")
        if not isinstance(thread_id, str) or not thread_id:
            raise PageError(f"{where}: thread lacks a node id")
        return thread_id

    def add_thread(self, thread_id: str, node: dict[str, Any], where: str) -> None:
        line = node.get("line")
        original_line = node.get("originalLine")
        meta = {
            "id": thread_id,
            "is_resolved": node.get("isResolved") if isinstance(node.get("isResolved"), bool) else None,
            "is_outdated": node.get("isOutdated") if isinstance(node.get("isOutdated"), bool) else None,
            "path": text(node.get("path")),
            "line": line if isinstance(line, int) and not isinstance(line, bool) else None,
            "original_line": original_line
            if isinstance(original_line, int) and not isinstance(original_line, bool)
            else None,
            "diff_side": optional_text(node.get("diffSide")),
        }
        record = dict(meta)
        record["_comparable"] = meta
        self.threads.put(thread_id, record, meta)
        self.thread_meta[thread_id] = self.threads.items[thread_id]
        self.add_thread_comments(thread_id, node.get("comments"), f"{where}.comments")

    def add_thread_comments(self, thread_id: str, connection: Any, where: str) -> None:
        conn = self.thread_comments.setdefault(thread_id, Connection(f"thread {thread_id} comments"))
        for _, node in conn.add_page(connection, node_id, where):
            record = thread_comment_record(node, where)
            record["_comparable"] = comparable(record)
            conn.put(record["id"], record, record["_comparable"])

    def add_thread_continuation(self, node: dict[str, Any], where: str) -> None:
        thread_id = node.get("id")
        if not isinstance(thread_id, str) or not thread_id:
            raise PageError(f"{where}: thread continuation lacks a node id")
        if thread_id not in self.thread_meta:
            self.unmatched.append(
                f"{where}: thread-comment continuation for {thread_id} matches no fetched thread"
            )
            return
        self.add_thread_comments(thread_id, node.get("comments"), f"{where}.node.comments")

    # -- output --

    def build(self) -> dict[str, Any]:
        if self.root is None:
            raise PageError("no root page: one page must carry repository.pullRequest with title")
        gaps: list[str] = list(self.page_errors) + list(self.unmatched)
        if self.root["state"] not in ("OPEN", "CLOSED", "MERGED"):
            gaps.append("pr: explicit state unavailable")
        if self.root["merged"] is None:
            gaps.append("pr: explicit merged state unavailable")
        coverage: dict[str, Any] = {}
        for conn in (self.closing, self.reviews, self.threads, self.pr_comments):
            coverage[conn.name] = conn.coverage()
            gaps.extend(conn.gaps())

        issues: list[dict[str, Any]] = []
        fingerprint_issues: list[dict[str, Any]] = []
        for coordinate in self.issue_order:
            meta = self.issue_meta[coordinate]
            conn = self.issue_comments.get(coordinate) or Connection(f"issue {coordinate} comments")
            conn_coverage = conn.coverage()
            coverage[conn.name] = conn_coverage
            gaps.extend(conn.gaps())
            comments = conn.records()
            issue = dict(meta)
            issue["comments"] = comments
            issue["comments_complete"] = conn_coverage["complete"]
            issues.append(issue)
            fingerprint_issue: dict[str, Any] = {
                "coordinate": coordinate,
                "title": meta["title"],
                "body": meta["body"],
                "comments": [
                    {
                        "id": comment["id"],
                        "author": comment["author"],
                        "created_at": comment["created_at"],
                        "updated_at": comment["updated_at"],
                        "body": comment["body"],
                    }
                    for comment in comments
                ],
            }
            if conn.pages == 0:
                fingerprint_issue["comments"] = []
                fingerprint_issue["comments_available"] = False
            elif not conn_coverage["complete"]:
                fingerprint_issue["comments_complete"] = False
            fingerprint_issues.append(fingerprint_issue)

        threads: list[dict[str, Any]] = []
        for thread in self.threads.records():
            conn = self.thread_comments.get(thread["id"]) or Connection(f"thread {thread['id']} comments")
            conn_coverage = conn.coverage()
            coverage[conn.name] = conn_coverage
            gaps.extend(conn.gaps())
            thread["comments"] = conn.records()
            thread["comments_complete"] = conn_coverage["complete"]
            threads.append(thread)

        # A connection count does not establish that its evidence fields arrived.
        for issue in issues:
            for comment in issue["comments"]:
                for field in ("created_at", "updated_at"):
                    if parse_time(comment.get(field)) is None:
                        gaps.append(f"issue {issue['coordinate']} comment {comment['id']}: {field} unavailable")
        for record in self.reviews.records() + self.pr_comments.records() + [
            comment for thread in threads for comment in thread["comments"]
        ]:
            for field in (("submitted_at", "updated_at") if "submitted_at" in record else ("created_at", "updated_at")):
                if parse_time(record.get(field)) is None:
                    gaps.append(f"record {record['id']}: {field} unavailable")
        for thread in threads:
            if thread["is_resolved"] is None:
                gaps.append(f"thread {thread['id']}: resolution state unavailable")

        return {
            "schema": SCHEMA,
            "repository_url": self.root["repository_url"] or self.repository_url,
            "pr": self.root,
            "issues": issues,
            "explicit_issues": self.explicit_issues,
            "reviews": self.reviews.records(),
            "threads": threads,
            "pr_comments": self.pr_comments.records(),
            "coverage": coverage,
            "gaps": gaps,
            "complete": not gaps,
            "fingerprint": {
                "pr": {"title": self.root["title"], "body": self.root["body"]},
                "issues": fingerprint_issues,
            },
        }


class UnreadablePage:
    """A saved response that is not JSON: the fetch failed, so it is a gap."""

    def __init__(self, reason: str) -> None:
        self.reason = reason


def load_page(path: str) -> Any:
    try:
        if path == "-":
            raw = sys.stdin.read()
        else:
            with open(path, encoding="utf-8") as handle:
                raw = handle.read()
    except OSError as error:
        raise PageError(f"{path}: cannot read page: {error}") from error
    try:
        return json.loads(raw)
    except json.JSONDecodeError as error:
        return UnreadablePage(f"empty or non-JSON response ({error})")


def page_rank(payload: Any) -> int:
    """Order pages so the records a continuation extends are defined first."""
    if not isinstance(payload, dict):
        return 4
    data = payload.get("data", payload)
    if not isinstance(data, dict):
        return 4
    repository = data.get("repository")
    if isinstance(repository, dict):
        pull_request = repository.get("pullRequest")
        if isinstance(pull_request, dict):
            return 0 if "title" in pull_request else 1
        issue = repository.get("issue")
        if isinstance(issue, dict):
            return 2 if "title" in issue else 3
    return 3


def normalize(pages: list[tuple[str, Any]]) -> dict[str, Any]:
    packet = Packet()
    for where, payload in sorted(pages, key=lambda page: page_rank(page[1])):
        packet.add_page(payload, where)
    return packet.build()


# --- later-state ------------------------------------------------------------


def later_state(packet: dict[str, Any], review_id: str, after: Optional[str]) -> list[str]:
    if packet.get("schema") != SCHEMA:
        raise PageError(f"packet schema is not {SCHEMA}; produce it with `normalize`")
    lines: list[str] = []
    candidate = next((review for review in packet["reviews"] if review["id"] == review_id), None)
    if candidate is None:
        raise PageError(f"review {review_id} is not in the packet's reviews")
    cutoff_text = after or candidate.get("submitted_at") or ""
    cutoff = parse_time(cutoff_text)
    if cutoff is None:
        raise PageError(f"cannot parse the cutoff time `{cutoff_text}`")

    for gap in packet.get("gaps", []):
        lines.append(f"incomplete {gap}")

    def later(*stamps: Optional[str]) -> Optional[str]:
        for stamp in stamps:
            parsed = parse_time(stamp)
            if parsed is not None and parsed > cutoff:
                return stamp
        return None

    pr = packet["pr"]
    stamp = later(pr.get("last_edited_at"))
    if stamp:
        lines.append(f"pr edited {stamp}")
    for issue in packet["issues"]:
        stamp = later(issue.get("last_edited_at"))
        if stamp:
            lines.append(f"issue {issue['coordinate']} edited {stamp}")
        for comment in issue["comments"]:
            stamp = later(comment.get("created_at"), comment.get("last_edited_at"), comment.get("updated_at"))
            if stamp:
                lines.append(f"issue-comment {issue['coordinate']} id={comment['id']} at {stamp}")
    for review in packet["reviews"]:
        if review["id"] == review_id:
            stamp = later(review.get("last_edited_at"), review.get("updated_at"))
            if stamp:
                lines.append(f"review id={review_id} edited {stamp}")
            continue
        stamp = later(review.get("submitted_at"), review.get("last_edited_at"), review.get("updated_at"))
        if stamp:
            lines.append(f"review id={review['id']} by {review['author'] or '?'} at {stamp}")
    for thread in packet["threads"]:
        thread_later = False
        # A thread the candidate review created starts unresolved and carries
        # only its own comments, so silence about its state is correct. Any
        # other thread predates the review, and `is_resolved` carries no
        # timestamp either way, so its current state has to be settled.
        pre_existing = any(comment.get("review_id") != review_id for comment in thread["comments"])
        for comment in thread["comments"]:
            own = comment.get("review_id") == review_id and comment.get("reply_to") is None
            if own:
                stamp = later(comment.get("last_edited_at"), comment.get("updated_at"))
                if stamp:
                    lines.append(f"thread-comment thread={thread['id']} id={comment['id']} edited {stamp}")
                    thread_later = True
                continue  # exclude original output, retain subsequent edits
            stamp = later(comment.get("created_at"), comment.get("last_edited_at"), comment.get("updated_at"))
            if stamp:
                kind = "reply" if comment.get("reply_to") else "thread-comment"
                lines.append(f"{kind} thread={thread['id']} id={comment['id']} at {stamp}")
                thread_later = True
        if not thread_later and (thread.get("is_resolved") or pre_existing):
            state = "resolved" if thread.get("is_resolved") else "unresolved"
            lines.append(
                f"thread-state thread={thread['id']} path={thread['path'] or '?'} {state}: "
                "no timestamp; settle against the candidate review's recorded prior-item "
                "classification or treat as later state"
            )
    for comment in packet["pr_comments"]:
        stamp = later(comment.get("created_at"), comment.get("last_edited_at"), comment.get("updated_at"))
        if stamp:
            lines.append(f"pr-comment id={comment['id']} at {stamp}")
    return lines


# --- self-test --------------------------------------------------------------


def connection(nodes: list[dict[str, Any]], total: int, has_next: bool, cursor: Optional[str] = "c") -> dict[str, Any]:
    return {"totalCount": total, "pageInfo": {"hasNextPage": has_next, "endCursor": cursor}, "nodes": nodes}


def sample_root() -> dict[str, Any]:
    return {
        "data": {
            "repository": {
                "url": "https://github.com/acme/payments",
                "pullRequest": {
                    "title": "Retry charges",
                    "body": "Closes #123.",
                    "state": "OPEN",
                    "merged": False,
                    "isDraft": False,
                    "baseRefName": "main",
                    "baseRefOid": "b" * 40,
                    "headRefOid": "a" * 40,
                    "updatedAt": "2026-09-01T10:00:00Z",
                    "lastEditedAt": None,
                    "baseRepository": {"url": "https://github.com/acme/payments"},
                    "closingIssuesReferences": connection(
                        [
                            {
                                "number": 123,
                                "title": "No double charge",
                                "body": "Criterion 2.",
                                "url": "https://github.com/acme/payments/issues/123",
                                "updatedAt": "2026-08-30T10:00:00Z",
                                "lastEditedAt": None,
                                "comments": connection(
                                    [
                                        {
                                            "fullDatabaseId": "42",
                                            "author": {"login": "maintainer"},
                                            "createdAt": "2026-08-30T10:00:00Z",
                                            "updatedAt": "2026-08-30T10:00:00Z",
                                            "lastEditedAt": None,
                                            "body": "Survive a timeout.",
                                            "url": "https://github.com/acme/payments/issues/123#issuecomment-42",
                                        }
                                    ],
                                    1,
                                    False,
                                ),
                            }
                        ],
                        1,
                        False,
                    ),
                    "reviews": connection(
                        [
                            {
                                "fullDatabaseId": "900",
                                "author": {"login": "reviewer"},
                                "state": "COMMENTED",
                                "body": "summary",
                                "submittedAt": "2026-09-01T09:00:00Z",
                                "updatedAt": "2026-09-01T09:00:00Z",
                                "lastEditedAt": None,
                                "commit": {"oid": "a" * 40},
                                "url": "https://github.com/acme/payments/pull/7#pullrequestreview-900",
                            }
                        ],
                        1,
                        False,
                    ),
                    "reviewThreads": connection(
                        [
                            {
                                "id": "PRRT_1",
                                "isResolved": False,
                                "isOutdated": False,
                                "path": "src/retry.ts",
                                "line": 18,
                                "originalLine": 18,
                                "diffSide": "RIGHT",
                                "comments": connection(
                                    [
                                        {
                                            "fullDatabaseId": "5000",
                                            "author": {"login": "reviewer"},
                                            "body": "finding",
                                            "createdAt": "2026-09-01T09:00:00Z",
                                            "updatedAt": "2026-09-01T09:00:00Z",
                                            "lastEditedAt": None,
                                            "replyTo": None,
                                            "pullRequestReview": {"fullDatabaseId": "900"},
                                            "url": "u",
                                        }
                                    ],
                                    1,
                                    False,
                                ),
                            }
                        ],
                        1,
                        False,
                    ),
                    "comments": connection([], 0, False, None),
                },
            }
        }
    }


def self_test() -> int:
    failures: list[str] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        if not condition:
            failures.append(f"{name}: {detail}".rstrip(": "))

    packet = normalize([("root", sample_root())])
    check("complete packet", packet["complete"], str(packet["gaps"]))
    check("issue id normalized", packet["issues"][0]["comments"][0]["id"] == "42")
    check("fingerprint issue", packet["fingerprint"]["issues"][0]["coordinate"] == "acme/payments#123")
    check("no truncation marker", "comments_complete" not in packet["fingerprint"]["issues"][0])

    truncated = copy.deepcopy(sample_root())
    truncated["data"]["repository"]["pullRequest"]["reviews"]["pageInfo"]["hasNextPage"] = True
    truncated["data"]["repository"]["pullRequest"]["reviews"]["totalCount"] = 3
    packet = normalize([("root", truncated)])
    check("truncated is incomplete", not packet["complete"])
    check("gap names reviews", any(gap.startswith("reviews: 1 of 3") for gap in packet["gaps"]), str(packet["gaps"]))

    lines = later_state(normalize([("root", sample_root())]), "900", None)
    check("clean later-state", lines == [], str(lines))

    reopened = copy.deepcopy(sample_root())
    thread = reopened["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"][0]
    thread["comments"]["nodes"][0]["pullRequestReview"]["fullDatabaseId"] = "800"
    lines = later_state(normalize([("root", reopened)]), "900", None)
    check(
        "pre-existing unresolved thread",
        any(line.startswith("thread-state thread=PRRT_1") and "unresolved" in line for line in lines),
        str(lines),
    )

    http_error = normalize([("root", sample_root()), ("page2", {"message": "rate limited"})])
    check("http error body is a gap", not http_error["complete"], str(http_error["gaps"]))
    check(
        "http error body is named",
        any("HTTP error: rate limited" in gap for gap in http_error["gaps"]),
        str(http_error["gaps"]),
    )
    try:
        normalize([("root", {"data": {"repository": {}}})])
        check("unknown shape rejected", False)
    except PageError:
        pass
    for failure in failures:
        print(failure)
    if failures:
        print(f"forge_packet --self-test: {len(failures)} assertion(s) failed")
        return 1
    print("forge_packet --self-test: passed")
    return 0


# --- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true", help="run the built-in assertions")
    subparsers = parser.add_subparsers(dest="command")
    normalize_parser = subparsers.add_parser("normalize", help="merge saved response pages into one packet")
    normalize_parser.add_argument("pages", nargs="+", help="saved `gh api graphql` responses, or - for stdin")
    later_parser = subparsers.add_parser("later-state", help="list state created or edited after a review")
    later_parser.add_argument("packet", help="packet written by `normalize`")
    later_parser.add_argument("--review", required=True, help="fullDatabaseId of the candidate review")
    later_parser.add_argument("--after", help="ISO-8601 cutoff overriding the review's submission time")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.command is None:
        parser.print_usage(sys.stderr)
        return 2
    try:
        if args.command == "normalize":
            pages = [(path, load_page(path)) for path in args.pages]
            packet = normalize(pages)
            json.dump(packet, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
            for gap in packet["gaps"]:
                print(f"forge_packet: gap: {gap}", file=sys.stderr)
            return 0
        packet = load_page(args.packet)
        if not isinstance(packet, dict):
            raise PageError(f"{args.packet}: packet must be a JSON object")
        lines = later_state(packet, args.review, args.after)
        for line in lines:
            print(line)
        return 1 if lines else 0
    except PageError as error:
        print(f"forge_packet: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
