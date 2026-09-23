#!/usr/bin/env python3
"""Compute the deterministic context digest used by review-code.

Usage:
    python3 scripts/context_fingerprint.py [INPUT | --json JSON]
    python3 scripts/context_fingerprint.py --packet packet.json [INPUT | --json JSON]
    python3 scripts/context_fingerprint.py --example    # print a minimal INPUT
    ... --guidance-base BASE --store STORE             # derive `guidance` too

INPUT is a JSON object with `pr`, `issues`, `specs`, and `guidance` as the
review record defines them (`-` or omitted reads stdin). With `--packet`, the
`pr` and `issues` objects come from the `fingerprint` section of the packet
that `forge_packet.py normalize` wrote, so the digest is computed over the same
normalized records the review read; the optional INPUT then supplies only
`specs` and `guidance`, and may not carry `pr` or `issues` of its own.

With `--guidance-base BASE --store STORE`, the script derives `guidance`
itself, and INPUT may not carry it: the sorted blobs, tracked at BASE, of root
`AGENTS.md`, `CLAUDE.md`, and `CONTEXT.md`, and of every `AGENTS.md` or
`CLAUDE.md` in an ancestor directory of a changed path. Changed paths are each
`path` and rename `old_path` in the store's merge-base manifest. The set is
exhaustive: linked files, `docs/agents/issue-tracker.md`, ADRs, design docs,
READMEs, skill files, and head-branch versions never enter it. This reads the
local git repository with `git ls-tree`.

On local targets, supply the same schema directly: `pr.title` is the range
as written or `worktree tree=<tree hash>`; `pr.body` holds only the real
commit messages since merge-base, never snapshot messages or uncommitted text.

`finalize_review.py --fingerprint-input INPUT` computes this same digest from
a saved INPUT file at finalization, with these functions.

Per issue, `comments_available: false` records that no comments could be
obtained and `comments_complete: false` records that a paginated comment
connection was left truncated. Each key is added to the normalized issue only
when false, so digests of inputs without them are unchanged.

Exit codes:
    0  the digest was printed
    2  the input cannot be read or violates the schema, or `git ls-tree` fails;
       the reason is on stderr
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from typing import Any


def string(value: Any, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string or null")
    return value


def mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def sequence(value: Any, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    return value


def utf8_key(value: str) -> bytes:
    return value.encode("utf-8")


def canonical_key(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def normalize(payload: Any) -> dict[str, Any]:
    root = mapping(payload, "input")
    pr = mapping(root.get("pr", {}), "pr")

    issues: list[dict[str, Any]] = []
    for issue_index, raw_issue in enumerate(sequence(root.get("issues"), "issues")):
        issue = mapping(raw_issue, f"issues[{issue_index}]")
        comments: list[dict[str, str]] = []
        for comment_index, raw_comment in enumerate(
            sequence(issue.get("comments"), f"issues[{issue_index}].comments")
        ):
            comment = mapping(
                raw_comment, f"issues[{issue_index}].comments[{comment_index}]"
            )
            comment_id = comment.get("id")
            if isinstance(comment_id, int):
                numeric_id = comment_id
            elif isinstance(comment_id, str) and comment_id.isascii() and comment_id.isdigit():
                numeric_id = int(comment_id)
            else:
                raise ValueError(
                    f"issues[{issue_index}].comments[{comment_index}].id "
                    "must be a non-negative integer"
                )
            if numeric_id < 0:
                raise ValueError(
                    f"issues[{issue_index}].comments[{comment_index}].id "
                    "must be a non-negative integer"
                )
            comments.append(
                {
                    "id": str(numeric_id),
                    "author": string(comment.get("author"), "comment.author"),
                    "created_at": string(comment.get("created_at"), "comment.created_at"),
                    "updated_at": string(comment.get("updated_at"), "comment.updated_at"),
                    "body": string(comment.get("body"), "comment.body"),
                }
            )
        comments.sort(key=lambda comment: (int(comment["id"]), canonical_key(comment)))
        comments_available = issue.get("comments_available", True)
        if not isinstance(comments_available, bool):
            raise ValueError(
                f"issues[{issue_index}].comments_available must be a boolean"
            )
        comments_complete = issue.get("comments_complete", True)
        if not isinstance(comments_complete, bool):
            raise ValueError(
                f"issues[{issue_index}].comments_complete must be a boolean"
            )
        normalized_issue: dict[str, Any] = {
            "coordinate": string(issue.get("coordinate"), "issue.coordinate"),
            "title": string(issue.get("title"), "issue.title"),
            "body": string(issue.get("body"), "issue.body"),
            "comments": comments,
        }
        if not comments_available:
            # Unavailable comments are a distinct input from zero comments:
            # two runs that differ here must not share a digest. The key is
            # only added when false so digests for existing inputs are unchanged.
            if comments:
                raise ValueError(
                    f"issues[{issue_index}].comments must be absent or empty "
                    "when comments_available is false"
                )
            normalized_issue["comments_available"] = False
        if not comments_complete:
            # A truncated comment connection is a distinct input from a complete
            # one with the same visible comments: the digest must not let a
            # run that missed a page match a run that fetched every page. The
            # key is only added when false, so existing digests are unchanged.
            if not comments_available:
                raise ValueError(
                    f"issues[{issue_index}].comments_complete cannot be false "
                    "when comments_available is false"
                )
            normalized_issue["comments_complete"] = False
        issues.append(normalized_issue)
    issues.sort(
        key=lambda issue: (utf8_key(issue["coordinate"]), canonical_key(issue))
    )

    specs: list[dict[str, str]] = []
    for spec_index, raw_spec in enumerate(sequence(root.get("specs"), "specs")):
        spec = mapping(raw_spec, f"specs[{spec_index}]")
        text = string(spec.get("text"), f"specs[{spec_index}].text")
        identity = string(spec.get("identity"), f"specs[{spec_index}].identity")
        if not identity:
            identity = "inline:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
        specs.append({"identity": identity, "text": text})
    specs.sort(
        key=lambda spec: (utf8_key(spec["identity"]), utf8_key(spec["text"]))
    )

    guidance: list[dict[str, str]] = []
    for item_index, raw_item in enumerate(sequence(root.get("guidance"), "guidance")):
        item = mapping(raw_item, f"guidance[{item_index}]")
        guidance.append(
            {
                "path": string(item.get("path"), f"guidance[{item_index}].path"),
                "blob_sha": string(
                    item.get("blob_sha"), f"guidance[{item_index}].blob_sha"
                ),
            }
        )
    guidance.sort(
        key=lambda item: (utf8_key(item["path"]), utf8_key(item["blob_sha"]))
    )

    return {
        "pr": {
            "title": string(pr.get("title"), "pr.title"),
            "body": string(pr.get("body"), "pr.body"),
        },
        "issues": issues,
        "specs": specs,
        "guidance": guidance,
    }


def digest(payload: Any) -> str:
    canonical = json.dumps(
        normalize(payload),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def merge_packet(payload: Any, packet_path: str) -> dict[str, Any]:
    """Take `pr` and `issues` from a forge packet, `specs` and `guidance` from payload."""
    with open(packet_path, encoding="utf-8") as packet_file:
        packet = json.load(packet_file)
    packet_root = mapping(packet, "packet")
    if packet_root.get("schema") != "forge-packet/1":
        raise ValueError("packet schema is not forge-packet/1; produce it with forge_packet.py normalize")
    fingerprint = mapping(packet_root.get("fingerprint"), "packet.fingerprint")
    root = mapping(payload, "input")
    for field in ("pr", "issues"):
        if field in root:
            raise ValueError(f"input must not carry {field} when --packet supplies it")
    merged = dict(root)
    merged["pr"] = fingerprint.get("pr", {})
    merged["issues"] = fingerprint.get("issues", [])
    return merged


def derive_guidance(base: str, store_path: str) -> list[dict[str, str]]:
    """The base-branch instruction files that apply to the store's changed paths."""
    with open(store_path, encoding="utf-8") as store_file:
        store = json.load(store_file)
    context = mapping(mapping(store, "store").get("context"), "store.context")
    wanted = {"AGENTS.md", "CLAUDE.md", "CONTEXT.md"}
    for index, raw_entry in enumerate(sequence(context.get("manifest"), "store.context.manifest")):
        entry = mapping(raw_entry, f"store.context.manifest[{index}]")
        for changed in (entry.get("path"), entry.get("old_path")):
            if not isinstance(changed, str) or not changed:
                continue
            parts = changed.split("/")[:-1]
            for depth in range(1, len(parts) + 1):
                directory = "/".join(parts[:depth])
                wanted.update({f"{directory}/AGENTS.md", f"{directory}/CLAUDE.md"})
    listing = subprocess.run(["git", "ls-tree", "-r", "-z", "--full-tree", base],
                             capture_output=True, text=True, encoding="utf-8")
    if listing.returncode != 0:
        raise ValueError(f"git ls-tree {base} failed: {listing.stderr.strip()}")
    guidance = []
    for record in listing.stdout.split("\0"):
        if not record:
            continue
        meta, path = record.split("\t", 1)
        _mode, kind, blob_sha = meta.split(" ")
        if kind == "blob" and path in wanted:
            guidance.append({"path": path, "blob_sha": blob_sha})
    return guidance


# What --example prints: one local-range input with every field the review record names.
EXAMPLE = {
    "pr": {"title": "main...HEAD", "body": "Add retries for charge submission\n"},
    "issues": [{
        "coordinate": "acme/payments#123", "title": "Retries must reuse one idempotency key",
        "body": "Acceptance criterion 2: one key per logical charge.",
        "comments": [{"id": 1001, "author": "octocat", "created_at": "2026-09-01T12:00:00Z",
                      "updated_at": "2026-09-01T12:00:00Z", "body": "Confirmed on the payments service."}],
    }],
    "specs": [{"identity": "/abs/path/to/spec.md", "text": "Retries reuse one idempotency key per logical charge."}],
    "guidance": [{"path": "AGENTS.md", "blob_sha": "c" * 40}],
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the v5b review context SHA-256 for a structured JSON input."
    )
    parser.add_argument("input", nargs="?", default="-", help="JSON file, or - for stdin")
    parser.add_argument("--json", help="JSON value supplied directly instead of a file")
    parser.add_argument(
        "--packet",
        help="forge packet from forge_packet.py normalize; supplies pr and issues",
    )
    parser.add_argument("--guidance-base", help="base commit whose instruction files form `guidance`; needs --store")
    parser.add_argument("--store", help="review_context.py store whose manifest names the changed paths")
    parser.add_argument("--example", action="store_true", help="print a minimal input object, then exit")
    args = parser.parse_args()
    if (args.guidance_base is None) != (args.store is None):
        parser.error("--guidance-base and --store go together")
    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return 0

    try:
        if args.json is not None:
            if args.input != "-":
                parser.error("input and --json are mutually exclusive")
            payload = json.loads(args.json)
        elif args.input == "-":
            optional = args.packet is not None or args.store is not None
            raw = "" if sys.stdin.isatty() and optional else sys.stdin.read()
            if optional and not raw.strip():
                payload = {}  # no specs or guidance were supplied
            else:
                payload = json.loads(raw)
        else:
            with open(args.input, encoding="utf-8") as input_file:
                payload = json.load(input_file)
        if args.packet is not None:
            payload = merge_packet(payload, args.packet)
        if args.store is not None:
            payload = dict(mapping(payload, "input"))
            if "guidance" in payload:
                raise ValueError("input must not carry guidance when --store derives it")
            payload["guidance"] = derive_guidance(args.guidance_base, args.store)
        print(digest(payload))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"context_fingerprint: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
