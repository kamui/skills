#!/usr/bin/env python3
"""Exercise audit duplicate eligibility through the CLI.

Usage: python3 scripts/test_review_identity.py
Input: self-contained forge fixtures; no network or sibling skill imports.
Exit 0: all cases pass; 1: assertions fail; 2: fixture/subprocess I/O failure.
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from context_fingerprint import digest
from forge_packet import normalize, output_digest, sample_root

HERE = Path(__file__).resolve().parent
BASE = "b" * 40
MERGE = "c" * 40
INPUTS = {"specs": [], "guidance": [{"path": "AGENTS.md", "blob_sha": "d" * 40}]}


def fixture() -> dict:
    packet = normalize([("root", sample_root())])
    context = digest(dict(packet["fingerprint"], **INPUTS))
    packet["reviews"][0]["body"] = (
        "Changes Requested (advisory)\n"
        f"<!-- review-run workflow=v2b-7 head={'a' * 40} base-ref=main state=OPEN merged=false "
        f"base-sha={BASE} merge-base={MERGE} context={context} "
        "issues=acme/payments#123 coverage=complete -->"
    )
    seal_output(packet)
    return packet


def seal_output(packet: dict) -> None:
    review = packet["reviews"][0]
    comments = [c for t in packet["threads"] for c in t["comments"]
                if c.get("review_id") == review["id"] and c.get("reply_to") is None]
    review["body"] = re.sub(r" output=[0-9a-f]{64}", "", review["body"])
    value = output_digest({"body": review["body"], "comments": comments})
    review["body"] = review["body"].replace(" -->", f" output={value} -->")


def main() -> int:
    failures = []
    checks = 0
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)

        def check(name: str, packet: dict, expected: int, *, inputs: dict = INPUTS,
                  merge: str = MERGE, author: str = "reviewer", contains: str = "") -> None:
            nonlocal checks
            checks += 1
            (tmp / "packet.json").write_text(json.dumps(packet), encoding="utf-8")
            (tmp / "inputs.json").write_text(json.dumps(inputs), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(HERE / "review_identity.py"), str(tmp / "packet.json"),
                 "--review", "900", "--author", author, "--merge-base", merge,
                 "--inputs", str(tmp / "inputs.json")], capture_output=True, text=True, encoding="utf-8",
            )
            if result.returncode != expected or contains not in result.stdout + result.stderr:
                failures.append(f"{name}: exit {result.returncode}: {result.stdout} {result.stderr}")

        original = fixture()
        payload = {"body": original["reviews"][0]["body"],
                   "comments": original["threads"][0]["comments"]}
        (tmp / "output.json").write_text(json.dumps(payload), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(HERE / "forge_packet.py"), "output-digest", str(tmp / "output.json")],
            capture_output=True, text=True, encoding="utf-8",
        )
        if result.returncode != 0 or f"output={result.stdout.strip()} " not in payload["body"]:
            failures.append(f"publication digest CLI roundtrip: {result.stdout} {result.stderr}")
        check("exact current inputs", original, 0)
        changed = fixture()
        changed["pr"].update(state="MERGED", merged=True)
        check("open review cannot suppress merged retrospective", changed, 1, contains="merged")
        changed["reviews"][0]["body"] = changed["reviews"][0]["body"].replace(
            "state=OPEN merged=false", "state=MERGED merged=true")
        check("matching merged identity is eligible but grants no authority", changed, 0)
        changed = fixture()
        changed["pr"]["state"] = "CLOSED"
        check("closed lifecycle differs at same head", changed, 1, contains="state")
        check("different identity", fixture(), 1, author="another", contains="reviewer identity")
        check("changed merge-base", fixture(), 1, merge="e" * 40, contains="merge-base")
        check("abbreviated SHA", fixture(), 2, merge="abc", contains="40-hex")
        changed = fixture()
        changed["pr"]["base_sha"] = "e" * 40
        check("changed base same head", changed, 1, contains="base-sha")
        changed = fixture()
        changed["fingerprint"]["issues"][0]["body"] = "Also guarantee refunds."
        check("changed issue same status", changed, 1, contains="context")
        check("changed guidance", fixture(), 1,
              inputs={"specs": [], "guidance": [{"path": "AGENTS.md", "blob_sha": "e" * 40}]},
              contains="context")
        check("additional supplied spec", fixture(), 1,
              inputs=dict(INPUTS, specs=[{"identity": "doc:1", "text": "Refunds required"}]),
              contains="context")
        changed = fixture()
        changed["reviews"][0]["body"] = changed["reviews"][0]["body"].replace("v2b-7", "v2b-6")
        check("old workflow", changed, 1, contains="workflow")
        changed = fixture()
        body = changed["reviews"][0]["body"].split()
        changed["reviews"][0]["body"] = " ".join(t for t in body if not t.startswith("context="))
        check("no digest trailer", changed, 1, contains="context")
        changed = fixture()
        changed["reviews"][0]["body"] += "\n" + changed["reviews"][0]["body"]
        check("multiple trailers", changed, 1, contains="exactly one")
        changed = fixture()
        reply = copy.deepcopy(changed["threads"][0]["comments"][0])
        reply.update(id="5001", author="human", body="The requirement also applies to refunds.",
                     reply_to="5000", created_at="2026-09-01T11:00:00Z",
                     updated_at="2026-09-01T11:00:00Z")
        changed["threads"][0]["comments"].append(reply)
        check("human reply without trailer and same review id", changed, 1, contains="reply ")
        changed = fixture()
        changed["reviews"][0]["last_edited_at"] = "2026-09-01T11:00:00Z"
        changed["reviews"][0]["body"] = "New evidence.\n" + changed["reviews"][0]["body"]
        check("edited candidate review", changed, 1, contains="own-output")
        changed = fixture()
        changed["reviews"][0]["updated_at"] = "2026-09-01T09:00:01Z"
        for comment in changed["threads"][0]["comments"]:
            comment.update(created_at="2026-09-01T09:00:01Z", updated_at="2026-09-01T09:00:01Z")
        check("original timestamps drift one second without edits", changed, 0)
        changed["reviews"][0]["body"] = "[Finding](https://example.test/comment/1)\n" + changed["reviews"][0]["body"]
        changed["reviews"][0]["last_edited_at"] = "2026-09-01T09:00:10Z"
        seal_output(changed)  # the same final payload sent by the phase-2 update
        check("phase-2 linked index is original output", changed, 0)
        changed["threads"][0]["comments"][0]["body"] += " Later correction."
        check("later edit to an original comment", changed, 1, contains="own-output")
        changed = fixture()
        changed["threads"][0]["comments"] = []
        check("deleted original comment", changed, 1, contains="own-output")
        changed = fixture()
        changed["reviews"][0]["body"] = re.sub(r" output=[0-9a-f]{64}", "", changed["reviews"][0]["body"])
        check("missing output baseline", changed, 1, contains="output digest unavailable")
        changed = fixture()
        changed["threads"][0]["is_resolved"] = True
        check("undated resolution", changed, 1, contains="thread-state")
        changed = fixture()
        changed["complete"] = False
        changed["gaps"] = ["reviews: page after cursor-2 failed"]
        check("failed later page", changed, 1, contains="cursor-2")
        changed = fixture()
        changed["reviews"][0]["body"] = changed["reviews"][0]["body"].replace("coverage=complete", "coverage=incomplete")
        check("prior incomplete", changed, 1, contains="coverage")
        # Raw omitted state must survive normalization as a coverage failure.
        for field in ("state", "merged"):
            raw = sample_root()
            del raw["data"]["repository"]["pullRequest"][field]
            packet = normalize([("root", raw)])
            packet["reviews"][0]["body"] = fixture()["reviews"][0]["body"]
            check(f"missing {field}", packet, 1, contains="state unavailable")
        for field in ("createdAt", "updatedAt"):
            raw = sample_root()
            del raw["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"][0]["comments"]["nodes"][0][field]
            packet = normalize([("root", raw)])
            packet["reviews"][0]["body"] = fixture()["reviews"][0]["body"]
            check(f"missing comment {field}", packet, 1, contains="unavailable")
        for field in ("hasNextPage", "endCursor"):
            raw = sample_root()
            connection = raw["data"]["repository"]["pullRequest"]["reviews"]
            connection["pageInfo"]["hasNextPage"] = True
            del connection["pageInfo"][field]
            packet = normalize([("root", raw)])
            packet["reviews"][0]["body"] = fixture()["reviews"][0]["body"]
            check(f"missing pagination {field}", packet, 1, contains="incomplete")
        # Types/order normalize independently from review eligibility.
        raw = sample_root()
        comment = raw["data"]["repository"]["pullRequest"]["closingIssuesReferences"]["nodes"][0]["comments"]["nodes"][0]
        comment["fullDatabaseId"] = 42
        packet = normalize([("root", raw)])
        packet["reviews"][0]["body"] = fixture()["reviews"][0]["body"]
        check("numeric type normalization", packet, 0)
    for failure in failures:
        print(failure)
    if failures:
        return 1
    print(f"test_review_identity: {checks} CLI cases passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OSError as error:
        print(f"test_review_identity: {error}", file=sys.stderr)
        raise SystemExit(2)
