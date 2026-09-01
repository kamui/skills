#!/usr/bin/env python3
"""Compute the deterministic context digest used by code-review-publish."""

from __future__ import annotations

import argparse
import hashlib
import json
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
        issues.append(
            {
                "coordinate": string(issue.get("coordinate"), "issue.coordinate"),
                "title": string(issue.get("title"), "issue.title"),
                "body": string(issue.get("body"), "issue.body"),
                "comments": comments,
            }
        )
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the code-review-publish context SHA-256 for structured JSON input."
    )
    parser.add_argument("input", nargs="?", default="-", help="JSON file, or - for stdin")
    parser.add_argument("--json", help="JSON value supplied directly instead of a file")
    args = parser.parse_args()

    try:
        if args.json is not None:
            if args.input != "-":
                parser.error("input and --json are mutually exclusive")
            payload = json.loads(args.json)
        elif args.input == "-":
            payload = json.load(sys.stdin)
        else:
            with open(args.input, encoding="utf-8") as input_file:
                payload = json.load(input_file)
        print(digest(payload))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"context_fingerprint: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
