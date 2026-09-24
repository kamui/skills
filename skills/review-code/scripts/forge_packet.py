#!/usr/bin/env python3
"""Fetch a pull request's forge inputs and normalize them into one persisted review packet.

`references/targets.md`, read at `SKILL.md` step 1 for a pull request, runs
`fetch`, which fetches the pull request, its closing issues with their
comments, its reviews, review threads, and comments, and each explicitly
referenced non-closing issue with `gh api graphql`, saving every response to a
file. The saved responses become one logical collection of the reviewed forge
inputs -- the packet -- with stable numeric ids, edit timestamps, and
per-connection completeness. Only `fetch` calls `gh`; every other subcommand
reads the files it is given. No subcommand decides a review judgment.

Usage:
    python3 scripts/forge_packet.py fetch --repo OWNER/NAME --pr NUMBER
        --dir PRIVATE_DIR [--issue [OWNER/NAME]#NUMBER ...]
    python3 scripts/forge_packet.py normalize PAGE [PAGE ...] > packet.json
    python3 scripts/forge_packet.py later-state packet.json --review ID
        [--after ISO-8601]
    python3 scripts/forge_packet.py shortcut packet.json --review ID
        --merge-base SHA --supplied-inputs yes|no
    python3 scripts/forge_packet.py --self-test

`fetch` runs the root query, then one continuation query per bounded
connection whose `pageInfo.hasNextPage` is true, following each `endCursor`
until it is false, and one issue query per `--issue` not already among the
closing issues, with that issue's comment continuations. It runs in the
reviewed repository, targets `--repo` explicitly, and saves each response as
`gh` printed it to `forge-<n>.json` in `--dir`, a failed call included. It
records each call's file, role, connection, and exit in `fetch.json`, then
writes `packet.json`: exactly what `normalize` prints for those responses in
call order. A failed call is not followed further and names its gap in the
packet; its stderr line goes to stderr. A second `fetch` into the same
directory must name the same pull request and only `--issue` values: it
fetches the issues the saved responses lack and rewrites `packet.json` from
every saved response. Stdout is `packet <path>: complete|incomplete, <n>
responses`, then one `gap <text>` line per gap. `fetch` exits 0 when the packet
is written, gaps included; 2 when `gh` cannot run, the directory is unusable or
already holds another fetch, or the root response is missing or unrecognized.

`normalize` accepts the raw stdout of each `gh api graphql` call from the
documented root query and its continuation queries, in any order, and prints
the packet as one JSON object. Its exit is 0 even when a connection is
incomplete: the packet then reports `"complete": false` and names every gap,
because the reviewer still needs the pages that did arrive. A saved response
that carries GraphQL errors, or is empty or not JSON because the call failed,
is a named gap for the same reason, as is a page carrying the forge's HTTP
error body instead of a response. A file that cannot be opened, or a JSON page
that matches no documented query shape, is exit 2.

`later-state` answers the re-review reference's later-state question for the
candidate review `--review ID` (its `fullDatabaseId`): it prints one line per
pull-request, issue, review, comment, or reply created or edited after that
review's submission time (or after `--after`), one line per packet gap, and one
`thread-state` line per thread whose undated resolved state cannot be ruled
unchanged and that carries no later comment: every resolved thread, and every
thread predating the review, since one resolved when the review ran can have
been un-resolved since without leaving a timestamp. A thread the candidate
review created and left unresolved is the one silent case. Unedited candidate
reviews and their original comments are excluded, as are unedited replies with
this reviewer's prior-item trailer naming the candidate's commit, and empty,
unedited reviews holding only those replies. Edited records remain eligible.
Excluding publication replies leaves thread-state settling intact: a resolved
pre-existing thread still prints its thread-state line and exits 1.
Exit 0 means the packet is complete
and nothing later exists, so the deduplication rule may consider the candidate;
exit 1 means the lines on stdout stand between the run and that shortcut.

`shortcut` decides the duplicate-review identity for the same candidate. It
reads the candidate's `review-run` trailer from its body and prints one
`identity` line per mismatch: head, base ref and SHA against the packet,
merge-base against `--merge-base`, workflow against `render_review.WORKFLOW`,
`packet_context` against the digest this script computes from the packet, and
`supplied_inputs=no` required of both the trailer and `--supplied-inputs`. A
trailer without `packet_context` and `supplied_inputs`, such as an older one
carrying only `context=`, names the absent marker and never qualifies. The
`later-state` lines follow. Exit 0 permits the shortcut; exit 1 prints what
stands between the run and it.

The packet's `fingerprint` section holds the pull request's intent: its title
and body, and each linked issue's coordinate, title, body and comment records
with their availability and completeness. `packet_context` is the SHA-256 of
that section's canonical form, so any change to the pull request's text, a
linked issue's text or comments, a deleted comment, or the set of linked
issues changes it. The finalizer computes the same digest from the saved
packet; nothing accepts a model-supplied one.

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
page carried a GraphQL error or an HTTP failure. Anything else is a named gap.

Exit codes:
    0  the packet or an empty later-state report was written
    1  later-state or shortcut lines were written to stdout, or a --self-test
       assertion failed
    2  a page file cannot be opened or matches no documented shape, or `fetch`
       cannot run; the file or failing command is named on stderr
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
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


def packet_text(packet: dict[str, Any]) -> str:
    return json.dumps(packet, ensure_ascii=False, indent=2) + "\n"


# --- fetch ------------------------------------------------------------------

PAGE_INFO = "totalCount pageInfo{ hasNextPage endCursor }"
ISSUE_COMMENT_FIELDS = "fullDatabaseId author{login} createdAt updatedAt lastEditedAt body url"
ISSUE_FIELDS = f"number title body url updatedAt lastEditedAt comments(first:100){{ {PAGE_INFO} nodes{{ {ISSUE_COMMENT_FIELDS} }} }}"
THREAD_COMMENT_FIELDS = ("fullDatabaseId author{login} body createdAt updatedAt lastEditedAt "
                         "replyTo{ fullDatabaseId } pullRequestReview{ fullDatabaseId } url")
CONNECTION_FIELDS = {
    "closingIssuesReferences": (20, ISSUE_FIELDS),
    "reviews": (100, "fullDatabaseId author{login} state body submittedAt updatedAt lastEditedAt commit{oid} url"),
    "reviewThreads": (100, "id isResolved isOutdated path line originalLine diffSide "
                           f"comments(first:100){{ {PAGE_INFO} nodes{{ {THREAD_COMMENT_FIELDS} }} }}"),
    "comments": (100, "fullDatabaseId author{login} body createdAt updatedAt lastEditedAt url"),
}
REPOSITORY = "repository(owner:$owner,name:$name)"


def connection_query(name: str, after: bool) -> str:
    first, fields = CONNECTION_FIELDS[name]
    return f"{name}(first:{first}{',after:$after' if after else ''}){{ {PAGE_INFO} nodes{{ {fields} }} }}"


ROOT_QUERY = ("query($owner:String!,$name:String!,$number:Int!){ " + REPOSITORY + "{ url pullRequest(number:$number){ "
              "title body state merged isDraft baseRefName baseRefOid headRefOid updatedAt lastEditedAt baseRepository{ url } "
              + " ".join(connection_query(name, False) for name in PR_CONNECTIONS) + " } } }")
ISSUE_QUERY = "query($owner:String!,$name:String!,$issue:Int!){ " + REPOSITORY + "{ issue(number:$issue){ " + ISSUE_FIELDS + " } } }"
ISSUE_COMMENTS_QUERY = ("query($owner:String!,$name:String!,$issue:Int!,$after:String){ " + REPOSITORY + "{ issue(number:$issue){ "
                        f"number url comments(first:100,after:$after){{ {PAGE_INFO} nodes{{ {ISSUE_COMMENT_FIELDS} }} }} }} }} }}")
THREAD_COMMENTS_QUERY = ("query($thread:ID!,$after:String){ node(id:$thread){ ... on PullRequestReviewThread { "
                         f"id comments(first:100,after:$after){{ {PAGE_INFO} nodes{{ {THREAD_COMMENT_FIELDS} }} }} }} }} }}")


def pr_continuation_query(name: str) -> str:
    return ("query($owner:String!,$name:String!,$number:Int!,$after:String){ " + REPOSITORY
            + "{ pullRequest(number:$number){ " + connection_query(name, True) + " } } }")


FETCH_FORMAT = "forge-fetch/1"
MANIFEST = "fetch.json"
PACKET = "packet.json"
MAX_CALLS = 1000  # far beyond any real pull request; a forge that never ends a connection stops here


class FetchError(Exception):
    """`fetch` cannot run: `gh` is missing, the directory is unusable, or it holds another fetch."""


def repository_argument(value: str) -> tuple[str, str]:
    match = re.fullmatch(r"([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", value)
    if not match:
        raise argparse.ArgumentTypeError(f"expected OWNER/NAME, got {value!r}")
    return match.group(1), match.group(2)


def issue_argument(value: str) -> tuple[Optional[str], Optional[str], int]:
    match = re.fullmatch(r"(?:([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+))?#?([1-9][0-9]*)", value)
    if not match:
        raise argparse.ArgumentTypeError(f"expected NUMBER or OWNER/NAME#NUMBER, got {value!r}")
    return match.group(1), match.group(2), int(match.group(3))


def positive_int(value: str) -> int:
    if not value.isdigit() or int(value) < 1:
        raise argparse.ArgumentTypeError(f"expected a positive integer, got {value!r}")
    return int(value)


def next_cursor(connection: Any) -> Optional[str]:
    info = connection.get("pageInfo") if isinstance(connection, dict) else None
    if isinstance(info, dict) and info.get("hasNextPage") is True:
        cursor = info.get("endCursor")
        if isinstance(cursor, str) and cursor:
            return cursor
    return None


def nodes_of(connection: Any) -> list[dict[str, Any]]:
    nodes = connection.get("nodes") if isinstance(connection, dict) else None
    return [node for node in nodes if isinstance(node, dict)] if isinstance(nodes, list) else []


class Fetch:
    """One pull request's saved responses, in call order, and the continuations they still owe."""

    def __init__(self, directory: str, repository: tuple[str, str], number: int) -> None:
        self.directory = directory
        self.owner, self.name = repository
        self.number = number
        self.calls: list[dict[str, Any]] = []
        self.pages: list[tuple[str, Any]] = []
        self.queue: list[tuple[tuple[Any, ...], str]] = []
        self.seen: set[tuple[tuple[Any, ...], str]] = set()

    def open(self, issues: list[tuple[Optional[str], Optional[str], int]]) -> bool:
        """Check the directory; load an earlier fetch's responses. True when this call adds issues to one."""
        if not os.path.isdir(self.directory):
            raise FetchError(f"{self.directory}: not a directory; create the private directory first")
        manifest_path = os.path.join(self.directory, MANIFEST)
        if not os.path.exists(manifest_path):
            leftovers = sorted(name for name in os.listdir(self.directory)
                               if name == PACKET or re.fullmatch(r"forge-.*\.json", name))
            if leftovers:
                raise FetchError(f"{self.directory}: already holds {', '.join(leftovers)}; fetch into a fresh private directory")
            return False
        try:
            with open(manifest_path, encoding="utf-8") as handle:
                manifest = json.load(handle)
            if manifest.get("format") != FETCH_FORMAT:
                raise ValueError(f"format is not {FETCH_FORMAT}")
            repository, number, calls = manifest["repository"], manifest["pull_request"], manifest["responses"]
            files = [call["file"] for call in calls]
            if not all(isinstance(name, str) and re.fullmatch(r"forge-[0-9]+\.json", name) for name in files):
                raise ValueError("a response file name is not forge-<n>.json")
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            raise FetchError(f"{manifest_path}: cannot read the earlier fetch: {error}") from error
        if not isinstance(repository, str) or repository.lower() != f"{self.owner}/{self.name}".lower() or number != self.number:
            raise FetchError(f"{self.directory}: already holds the fetch of {repository}#{number}; fetch into a fresh private directory")
        if not issues:
            raise FetchError(f"{self.directory}: already fetched; a second fetch only adds --issue values")
        if not os.path.exists(os.path.join(self.directory, PACKET)):
            raise FetchError(f"{self.directory}: the earlier fetch wrote no {PACKET}; fetch into a fresh private directory")
        self.calls = list(calls)
        self.pages = [(os.path.join(self.directory, name), load_page(os.path.join(self.directory, name))) for name in files]
        return True

    def gh(self, role: str, connection: str, query: str, variables: list[tuple[str, str, Any]]) -> Optional[Any]:
        """Run one `gh api graphql` call and save its stdout; the parsed response, or None when the call failed."""
        if len(self.calls) >= MAX_CALLS:
            raise FetchError(f"more than {MAX_CALLS} calls; a connection never reported its last page")
        path = os.path.join(self.directory, f"forge-{len(self.calls) + 1}.json")
        command = ["gh", "api", "graphql"]
        for flag, key, value in variables:
            command += [flag, f"{key}={value}"]
        command += ["-f", f"query={query}"]
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        except OSError as error:
            raise FetchError(f"cannot run gh api graphql: {error}") from error
        try:
            with open(path, "x", encoding="utf-8") as handle:
                handle.write(result.stdout)
        except OSError as error:
            raise FetchError(f"cannot save {path}: {error}") from error
        self.calls.append({"file": os.path.basename(path), "role": role, "connection": connection, "exit": result.returncode})
        payload = load_page(path)
        self.pages.append((path, payload))
        if result.returncode != 0:
            detail = (result.stderr.strip().splitlines() or ["no stderr"])[-1]
            print(f"forge_packet: fetch: {role} {connection} ({path}): gh api graphql exited {result.returncode}: {detail}",
                  file=sys.stderr)
            return None
        return payload

    def owe(self, key: tuple[Any, ...], connection: Any) -> None:
        cursor = next_cursor(connection)
        if cursor is not None and (key, cursor) not in self.seen:
            self.seen.add((key, cursor))
            self.queue.append((key, cursor))

    def issue_key(self, issue: dict[str, Any]) -> Optional[tuple[Any, ...]]:
        coordinate = coordinate_from_url(text(issue.get("url")))
        if coordinate is not None:
            slug, _, number = coordinate.partition("#")
            owner, _, name = slug.partition("/")
            return ("issue", owner, name, int(number))
        number = issue.get("number")
        if isinstance(number, int) and not isinstance(number, bool):
            return ("issue", self.owner, self.name, number)
        return None

    def follow(self, payload: Any) -> None:
        """Queue every continuation a successful response reports: a connection with a further page."""
        data = payload.get("data", payload) if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            return
        repository, node = data.get("repository"), data.get("node")
        if isinstance(repository, dict) and isinstance(repository.get("pullRequest"), dict):
            pull_request = repository["pullRequest"]
            for name in PR_CONNECTIONS:
                connection = pull_request.get(name)
                self.owe(("pr", name), connection)
                for item in nodes_of(connection):
                    if name == "closingIssuesReferences":
                        key = self.issue_key(item)
                        if key is not None:
                            self.owe(key, item.get("comments"))
                    elif name == "reviewThreads" and isinstance(item.get("id"), str):
                        self.owe(("thread", item["id"]), item.get("comments"))
        if isinstance(repository, dict) and isinstance(repository.get("issue"), dict):
            key = self.issue_key(repository["issue"])
            if key is not None:
                self.owe(key, repository["issue"].get("comments"))
        if isinstance(node, dict) and isinstance(node.get("id"), str):
            self.owe(("thread", node["id"]), node.get("comments"))

    def drain(self) -> None:
        while self.queue:
            key, cursor = self.queue.pop(0)
            if key[0] == "pr":
                page = self.gh("continuation", key[1], pr_continuation_query(key[1]), [
                    ("-f", "owner", self.owner), ("-f", "name", self.name), ("-F", "number", self.number),
                    ("-f", "after", cursor)])
            elif key[0] == "issue":
                page = self.gh("continuation", "issue-comments", ISSUE_COMMENTS_QUERY, [
                    ("-f", "owner", key[1]), ("-f", "name", key[2]), ("-F", "issue", key[3]), ("-f", "after", cursor)])
            else:
                page = self.gh("continuation", "thread-comments", THREAD_COMMENTS_QUERY, [
                    ("-f", "thread", key[1]), ("-f", "after", cursor)])
            if page is not None:
                self.follow(page)

    def fetched_issues(self) -> set[str]:
        """Lower-cased coordinates of the closing and explicitly fetched issues the saved responses carry."""
        found: set[str] = set()
        for _, payload in self.pages:
            data = payload.get("data", payload) if isinstance(payload, dict) else None
            repository = data.get("repository") if isinstance(data, dict) else None
            if not isinstance(repository, dict):
                continue
            issues = nodes_of((repository.get("pullRequest") or {}).get("closingIssuesReferences")) \
                if isinstance(repository.get("pullRequest"), dict) else []
            if isinstance(repository.get("issue"), dict) and "title" in repository["issue"]:
                issues.append(repository["issue"])
            for issue in issues:
                key = self.issue_key(issue)
                if key is not None:
                    found.add(f"{key[1]}/{key[2]}#{key[3]}".lower())
        return found

    def run(self, issues: list[tuple[Optional[str], Optional[str], int]]) -> dict[str, Any]:
        if not self.open(issues):
            root = self.gh("root", "root", ROOT_QUERY, [
                ("-f", "owner", self.owner), ("-f", "name", self.name), ("-F", "number", self.number)])
            if root is None:
                issues = []  # without the root response there is no packet to add them to
            else:
                self.follow(root)
                self.drain()
        known = self.fetched_issues()
        for owner, name, number in issues:
            owner, name = owner or self.owner, name or self.name
            coordinate = f"{owner}/{name}#{number}"
            if coordinate.lower() in known:
                continue
            known.add(coordinate.lower())
            page = self.gh("issue", "issue", ISSUE_QUERY, [("-f", "owner", owner), ("-f", "name", name), ("-F", "issue", number)])
            if page is not None:
                self.follow(page)
                self.drain()
        manifest = {"format": FETCH_FORMAT, "repository": f"{self.owner}/{self.name}", "pull_request": self.number,
                    "responses": self.calls}
        try:
            with open(os.path.join(self.directory, MANIFEST), "w", encoding="utf-8") as handle:
                handle.write(json.dumps(manifest, indent=2) + "\n")
        except OSError as error:
            raise FetchError(f"cannot write {MANIFEST}: {error}") from error
        packet = normalize(self.pages)
        try:
            with open(os.path.join(self.directory, PACKET), "w", encoding="utf-8") as handle:
                handle.write(packet_text(packet))
        except OSError as error:
            raise FetchError(f"cannot write {PACKET}: {error}") from error
        return packet


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

    def same_author(record: dict[str, Any]) -> bool:
        author = (record.get("author") or "").removesuffix("[bot]")
        candidate_author = (candidate.get("author") or "").removesuffix("[bot]")
        return bool(author) and author == candidate_author

    def publication_reply(comment: dict[str, Any]) -> bool:
        marker = re.search(
            r"<!-- prior-item id=[^\s<>]+ classification=(?:fixed|accepted|obsolete|still-open) "
            r"head=([0-9a-f]{40}) -->\s*\Z", comment.get("body") or "",
        )
        return bool(
            comment.get("reply_to") and same_author(comment)
            and comment.get("last_edited_at") is None
            and marker and marker.group(1) == candidate.get("commit")
        )

    review_comments: dict[Optional[str], list[dict[str, Any]]] = {}
    for thread in packet["threads"]:
        for comment in thread["comments"]:
            review_comments.setdefault(comment.get("review_id"), []).append(comment)

    def publication_container(review: dict[str, Any]) -> bool:
        comments = review_comments.get(review["id"], [])
        return bool(
            same_author(review) and review.get("body") == ""
            and review.get("last_edited_at") is None
            and comments and all(publication_reply(comment) for comment in comments)
        )

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
        if (review["id"] == review_id and review.get("last_edited_at") is None) or publication_container(review):
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
            if (own and comment.get("last_edited_at") is None) or publication_reply(comment):
                continue
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


# --- packet identity --------------------------------------------------------

PACKET_CONTEXT_FORMAT = "packet-context/1"
RUN_TRAILER_RE = re.compile(r"<!--\s+review-run((?:\s+\S+=\S*)*)\s+-->")


def packet_context(packet: dict[str, Any]) -> str:
    """The SHA-256 of the packet's normalized intent: the pull request's title and body and each linked issue's
    coordinate, title, body, comment availability and completeness, and comment records, in canonical order."""
    if packet.get("schema") != SCHEMA or not isinstance(packet.get("fingerprint"), dict):
        raise PageError(f"packet schema is not {SCHEMA} with a `fingerprint` section; produce it with `normalize`")
    intent = packet["fingerprint"]
    pr = intent.get("pr") if isinstance(intent.get("pr"), dict) else {}
    issues = intent.get("issues") if isinstance(intent.get("issues"), list) else []

    def order(identity: str) -> tuple[int, str]:
        return (int(identity), "") if identity.isdigit() else (-1, identity)

    canonical = {
        "format": PACKET_CONTEXT_FORMAT,
        "pr": {"title": text(pr.get("title")), "body": text(pr.get("body"))},
        "issues": sorted(
            ({"coordinate": text(issue.get("coordinate")), "title": text(issue.get("title")),
              "body": text(issue.get("body")),
              "comments_available": issue.get("comments_available") is not False,
              "comments_complete": issue.get("comments_complete") is not False,
              "comments": sorted(
                  ({key: text(comment.get(key)) for key in ("id", "author", "created_at", "updated_at", "body")}
                   for comment in issue.get("comments") or [] if isinstance(comment, dict)),
                  key=lambda comment: order(comment["id"]))}
             for issue in issues if isinstance(issue, dict)),
            key=lambda issue: issue["coordinate"]),
    }
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def run_trailer(body: str) -> Optional[dict[str, str]]:
    """The key=value fields of the last `review-run` trailer in a review body, or None when it has none."""
    matches = list(RUN_TRAILER_RE.finditer(body or ""))
    if not matches:
        return None
    return dict(token.partition("=")[::2] for token in matches[-1].group(1).split())


def shortcut(packet: dict[str, Any], review_id: str, merge_base: str, supplied_inputs: str) -> list[str]:
    """Why the candidate review cannot stand in for this run, one line each; empty when the shortcut applies."""
    import render_review  # the workflow constant; imported late because render_review imports this module

    lines = later_state(packet, review_id, None)  # also refuses a packet or review it cannot read
    candidate = next(review for review in packet["reviews"] if review["id"] == review_id)
    fields = run_trailer(candidate.get("body") or "")
    identity: list[str] = []
    if fields is None:
        identity.append(f"identity review {review_id} carries no review-run trailer")
        return identity + lines
    if "packet_context" not in fields or "supplied_inputs" not in fields:
        older = " (an older `context=` trailer)" if "context" in fields else ""
        identity.append(f"identity review {review_id} carries no packet_context and supplied_inputs markers{older}; "
                        "its packet identity cannot be established")
    pr = packet["pr"]
    expected = {"head": pr.get("head_sha"), "base-ref": pr.get("base_ref"), "base-sha": pr.get("base_sha"),
                "merge-base": merge_base, "workflow": render_review.WORKFLOW}
    if "packet_context" in fields:
        expected["packet_context"] = packet_context(packet)
    for key, value in expected.items():
        if fields.get(key) != value:
            identity.append(f"identity {key}: review {review_id} has {fields.get(key) or 'none'}, this run has {value}")
    if fields.get("supplied_inputs", "no") != "no":
        identity.append(f"identity supplied_inputs: review {review_id} used caller-supplied issues or specs")
    if supplied_inputs != "no":
        identity.append("identity supplied_inputs: this run has caller-supplied issues or specs")
    return identity + lines


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

    published = copy.deepcopy(reopened)
    pr = published["data"]["repository"]["pullRequest"]
    thread = pr["reviewThreads"]["nodes"][0]
    thread["isResolved"] = True
    reply = copy.deepcopy(thread["comments"]["nodes"][0])
    reply.update({
        "fullDatabaseId": "5001", "replyTo": {"fullDatabaseId": "5000"},
        "pullRequestReview": {"fullDatabaseId": "901"},
        "createdAt": "2026-09-01T09:01:00Z", "updatedAt": "2026-09-01T09:01:00Z",
        "body": "Fixed.\n<!-- prior-item id=bug/retry classification=fixed head=" + "a" * 40 + " -->",
    })
    thread["comments"] = connection([thread["comments"]["nodes"][0], reply], 2, False)
    container = copy.deepcopy(pr["reviews"]["nodes"][0])
    container.update({"fullDatabaseId": "901", "body": "", "submittedAt": reply["createdAt"], "updatedAt": reply["createdAt"]})
    pr["reviews"] = connection([pr["reviews"]["nodes"][0], container], 2, False)
    lines = later_state(normalize([("root", published)]), "900", None)
    check("publication leaves thread-state", lines == [
        "thread-state thread=PRRT_1 path=src/retry.ts resolved: no timestamp; "
        "settle against the candidate review's recorded prior-item classification or treat as later state"
    ], str(lines))

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
    fetch_parser = subparsers.add_parser("fetch", help="fetch a pull request's forge inputs with gh and write packet.json")
    fetch_parser.add_argument("--repo", required=True, type=repository_argument, help="the base repository, OWNER/NAME")
    fetch_parser.add_argument("--pr", required=True, type=positive_int, help="the pull request number")
    fetch_parser.add_argument("--dir", required=True, help="the run's private directory")
    fetch_parser.add_argument("--issue", action="append", default=[], type=issue_argument,
                              help="an explicitly referenced non-closing issue, NUMBER or OWNER/NAME#NUMBER; repeatable")
    normalize_parser = subparsers.add_parser("normalize", help="merge saved response pages into one packet")
    normalize_parser.add_argument("pages", nargs="+", help="saved `gh api graphql` responses, or - for stdin")
    later_parser = subparsers.add_parser("later-state", help="list state created or edited after a review")
    later_parser.add_argument("packet", help="packet written by `normalize`")
    later_parser.add_argument("--review", required=True, help="fullDatabaseId of the candidate review")
    later_parser.add_argument("--after", help="ISO-8601 cutoff overriding the review's submission time")
    shortcut_parser = subparsers.add_parser("shortcut", help="decide the duplicate-review identity for a candidate review")
    shortcut_parser.add_argument("packet", help="packet written by `normalize`")
    shortcut_parser.add_argument("--review", required=True, help="fullDatabaseId of the candidate review")
    shortcut_parser.add_argument("--merge-base", required=True, help="this run's full merge-base SHA")
    shortcut_parser.add_argument("--supplied-inputs", required=True, choices=("yes", "no"),
                                 help="whether this run has caller-supplied issues or specs")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.command is None:
        parser.print_usage(sys.stderr)
        return 2
    if args.command == "fetch":
        fetch = Fetch(args.dir, args.repo, args.pr)
        try:
            packet = fetch.run(args.issue)
        except (FetchError, PageError) as error:
            print(f"forge_packet: {error}", file=sys.stderr)
            return 2
        state = "complete" if packet["complete"] else "incomplete"
        print(f"packet {os.path.join(args.dir, PACKET)}: {state}, {len(fetch.calls)} responses")
        for gap in packet["gaps"]:
            print(f"gap {gap}")
        return 0
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
        if args.command == "shortcut":
            lines = shortcut(packet, args.review, args.merge_base, args.supplied_inputs)
        else:
            lines = later_state(packet, args.review, args.after)
        for line in lines:
            print(line)
        return 1 if lines else 0
    except PageError as error:
        print(f"forge_packet: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
