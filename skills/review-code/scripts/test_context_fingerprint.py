#!/usr/bin/env python3
"""Regression tests for the determinism of `context_fingerprint.py`.

`SKILL.md` step 2 skips an entire review when a prior review's recomputed
`context` digest matches its run trailer. That short-circuit is only sound if
two conforming runs over the same inputs compute byte-identical digests, so
these cases pin the normalizations the script promises: key order, array order,
comment-id type, the truncation and unavailability markers, the `--packet`
input path, and the sensitivity of the digest to every semantic field.

Run with ``python3 scripts/test_context_fingerprint.py``. Exit 0 when every
case passes; exit 1 after printing one line per failed case. Standard library
only; no network, git, or filesystem access beyond invoking the script under
test. The script is exercised through its real stdin interface with
``subprocess`` so that CLI-level behavior, including its error exits, is what
gets tested.
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve().parent / "context_fingerprint.py"
DIGEST_RE = re.compile(r"\A[0-9a-f]{64}\Z")

failures: list[str] = []


def fail(case: str, detail: str) -> None:
    failures.append(f"{case}: {detail}")


def run(payload: Any, *, dumps: Any = None) -> subprocess.CompletedProcess[str]:
    text = json.dumps(payload) if dumps is None else dumps
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def digest(case: str, payload: Any, *, dumps: Any = None) -> str | None:
    result = run(payload, dumps=dumps)
    if result.returncode != 0:
        fail(case, f"expected a digest, got exit {result.returncode}: {result.stderr.strip()}")
        return None
    value = result.stdout.strip()
    if not DIGEST_RE.match(value):
        fail(case, f"expected a 64-character lowercase hex digest, got `{value}`")
        return None
    return value


def expect_equal(case: str, left: Any, right: Any, *, left_dumps=None, right_dumps=None) -> None:
    a = digest(case, left, dumps=left_dumps)
    b = digest(case, right, dumps=right_dumps)
    if a is None or b is None:
        return
    if a != b:
        fail(case, f"digests differ but the inputs are logically identical ({a} != {b})")


def expect_different(case: str, left: Any, right: Any) -> None:
    a = digest(case, left)
    b = digest(case, right)
    if a is None or b is None:
        return
    if a == b:
        fail(case, f"digest {a} is unchanged after a semantic field changed")


def expect_error(case: str, payload: Any, fragment: str, *, dumps: Any = None) -> None:
    result = run(payload, dumps=dumps)
    if result.returncode == 0:
        fail(case, f"malformed payload was hashed instead of rejected (digest {result.stdout.strip()})")
        return
    if result.stdout.strip():
        fail(case, f"rejected payload still printed `{result.stdout.strip()}` on stdout")
    if fragment not in result.stderr:
        fail(case, f"error message `{result.stderr.strip()}` does not mention `{fragment}`")


# The reviewed inputs of one representative run. `guidance` here is a fixture of
# the F1.1 membership rule in `references/review-record.md`: root AGENTS.md and
# root CLAUDE.md, a path-scoped AGENTS.md in an ancestor directory of a changed
# path, and root CONTEXT.md. Membership is decided by the reviewer, not by this
# script — the script hashes exactly the entries it is given, which is why the
# membership rule has to be exhaustive for two runs to agree.
BASE: dict[str, Any] = {
    "pr": {
        "title": "Preserve the idempotency key across retries",
        "body": "Closes #123. Adds a retry policy for charge submission.",
    },
    "issues": [
        {
            "coordinate": "acme/payments#123",
            "title": "Retries must not double-charge",
            "body": "Acceptance criterion 2: one idempotency key per logical charge.",
            "comments": [
                {
                    "id": 42,
                    "author": "maintainer",
                    "created_at": "2026-08-30T10:00:00Z",
                    "updated_at": "2026-08-30T10:00:00Z",
                    "body": "The key must survive a timeout after commit.",
                },
                {
                    "id": 7,
                    "author": "author",
                    "created_at": "2026-08-29T09:00:00Z",
                    "updated_at": "2026-08-29T09:30:00Z",
                    "body": "Draft PR is up.",
                },
            ],
        },
        {
            "coordinate": "acme/payments#98",
            "title": "Retry policy epic",
            "body": "Umbrella issue.",
            "comments": [],
        },
    ],
    "specs": [
        {"identity": "https://example.test/specs/retries", "text": "Retries reuse one key."},
        {"text": "Inline spec text with no identity."},
    ],
    "guidance": [
        {"path": "AGENTS.md", "blob_sha": "1111111111111111111111111111111111111111"},
        {"path": "CLAUDE.md", "blob_sha": "2222222222222222222222222222222222222222"},
        {"path": "src/AGENTS.md", "blob_sha": "3333333333333333333333333333333333333333"},
        {"path": "CONTEXT.md", "blob_sha": "4444444444444444444444444444444444444444"},
    ],
}


def variant(mutate) -> dict[str, Any]:
    payload = copy.deepcopy(BASE)
    mutate(payload)
    return payload


def case_key_order_invariance() -> None:
    """Same logical content, different JSON key order, array order, and formatting."""
    reordered = copy.deepcopy(BASE)
    reordered["issues"].reverse()
    reordered["issues"][1]["comments"].reverse()
    reordered["specs"].reverse()
    reordered["guidance"].reverse()

    def reorder_keys(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: reorder_keys(value[key]) for key in reversed(list(value))}
        if isinstance(value, list):
            return [reorder_keys(item) for item in value]
        return value

    expect_equal(
        "key-order invariance",
        BASE,
        reorder_keys(reordered),
        right_dumps=json.dumps(reorder_keys(reordered), indent=4, sort_keys=False),
    )


def case_type_normalization() -> None:
    """A comment id given as "42" hashes the same as the integer 42."""

    def as_string(payload):
        payload["issues"][0]["comments"][0]["id"] = "42"

    expect_equal("comment-id type normalization", BASE, variant(as_string))


def case_absent_fields_normalize() -> None:
    """A null or omitted optional string is the same as the empty string."""

    def explicit_null(payload):
        payload["specs"][1]["identity"] = None

    expect_equal("null identity equals omitted identity", BASE, variant(explicit_null))


def case_repeated_invocation() -> None:
    """The same payload hashed in two separate processes gives the same digest."""
    expect_equal("digest stable across processes", BASE, copy.deepcopy(BASE))


def case_sensitivity() -> None:
    """Changing any single semantic field changes the digest."""

    def change_blob_sha(payload):
        payload["guidance"][0]["blob_sha"] = "9999999999999999999999999999999999999999"

    def change_issue_body(payload):
        payload["issues"][0]["body"] += " Also: never reorder."

    def change_pr_title(payload):
        payload["pr"]["title"] = "Preserve the idempotency key across retries."

    def change_comment_body(payload):
        payload["issues"][0]["comments"][1]["body"] = "Draft PR is up now."

    def change_comment_timestamp(payload):
        payload["issues"][0]["comments"][0]["updated_at"] = "2026-08-31T10:00:00Z"

    def change_spec_text(payload):
        payload["specs"][0]["text"] = "Retries reuse one key per logical charge."

    expect_different("sensitive to a guidance blob sha", BASE, variant(change_blob_sha))
    expect_different("sensitive to an issue body", BASE, variant(change_issue_body))
    expect_different("sensitive to the pr title", BASE, variant(change_pr_title))
    expect_different("sensitive to a comment body", BASE, variant(change_comment_body))
    expect_different("sensitive to a comment timestamp", BASE, variant(change_comment_timestamp))
    expect_different("sensitive to spec text", BASE, variant(change_spec_text))


def case_guidance_membership() -> None:
    """F1.1: membership is the reviewer's decision, and it changes the digest.

    The base fixture's `guidance` list is exactly what the review record's
    membership rule admits. Adding an entry the contract excludes — a non-root
    `CONTEXT.md`, or a head-branch variant of an included file — produces a
    different digest, which is why an under-specified membership rule would
    break the duplicate-review short-circuit even between two correct runs.
    """

    def add_non_root_context(payload):
        payload["guidance"].append(
            {"path": "docs/CONTEXT.md", "blob_sha": "5555555555555555555555555555555555555555"}
        )

    def add_out_of_scope_agents(payload):
        payload["guidance"].append(
            {"path": "tools/AGENTS.md", "blob_sha": "6666666666666666666666666666666666666666"}
        )

    def head_branch_variant(payload):
        payload["guidance"][0]["blob_sha"] = "7777777777777777777777777777777777777777"

    def drop_included_entry(payload):
        payload["guidance"] = [
            item for item in payload["guidance"] if item["path"] != "CONTEXT.md"
        ]

    expect_different("excluded non-root CONTEXT.md changes the digest", BASE, variant(add_non_root_context))
    expect_different("out-of-scope AGENTS.md changes the digest", BASE, variant(add_out_of_scope_agents))
    expect_different("head-branch blob variant changes the digest", BASE, variant(head_branch_variant))
    expect_different("dropping an included entry changes the digest", BASE, variant(drop_included_entry))


def case_comments_available() -> None:
    """Unavailable comments are hashed distinctly from zero comments.

    A run that could not obtain an issue's comments verbatim passes
    `comments_available: false` and no comments. Its digest must differ from a
    run over the same issue that genuinely has zero comments, or the
    duplicate-review short-circuit would treat the two as the same inputs.
    The explicit `true` is the default, so existing digests are unchanged.
    """

    def unavailable(payload):
        payload["issues"][1]["comments_available"] = False

    def unavailable_with_comments_absent(payload):
        del payload["issues"][1]["comments"]
        payload["issues"][1]["comments_available"] = False

    def unavailable_but_comments_present(payload):
        payload["issues"][0]["comments_available"] = False

    def explicit_true(payload):
        payload["issues"][0]["comments_available"] = True
        payload["issues"][1]["comments_available"] = True

    def non_boolean(payload):
        payload["issues"][1]["comments_available"] = "no"

    expect_different("unavailable comments differ from zero comments", BASE, variant(unavailable))
    expect_equal(
        "absent comments equal empty comments when unavailable",
        variant(unavailable),
        variant(unavailable_with_comments_absent),
    )
    expect_error(
        "unavailable comments with a non-empty list",
        variant(unavailable_but_comments_present),
        "must be absent or empty when comments_available is false",
    )
    expect_equal("explicit comments_available true equals omitted", BASE, variant(explicit_true))
    expect_error("non-boolean comments_available", variant(non_boolean), "comments_available must be a boolean")


def case_comments_complete() -> None:
    """A truncated comment connection is hashed distinctly from a complete one.

    Issue #132: when pagination of an issue's comments did not finish, the
    reviewer passes `comments_complete: false` beside the comments it did
    obtain. The digest must differ from a run that fetched every page and saw
    the same visible comments, or a truncated run could deduplicate against a
    complete one. `true` is the default, so existing digests are unchanged.
    """

    def truncated(payload):
        payload["issues"][0]["comments_complete"] = False

    def explicit_true(payload):
        payload["issues"][0]["comments_complete"] = True

    def truncated_and_unavailable(payload):
        payload["issues"][1]["comments_available"] = False
        payload["issues"][1]["comments_complete"] = False

    def non_boolean(payload):
        payload["issues"][0]["comments_complete"] = "no"

    expect_different("truncated comments differ from complete comments", BASE, variant(truncated))
    expect_equal("explicit comments_complete true equals omitted", BASE, variant(explicit_true))
    expect_error(
        "truncated and unavailable together",
        variant(truncated_and_unavailable),
        "comments_complete cannot be false when comments_available is false",
    )
    expect_error("non-boolean comments_complete", variant(non_boolean), "comments_complete must be a boolean")


def case_packet_input() -> None:
    """`--packet` hashes the packet's fingerprint section with stdin's specs and guidance.

    `forge_packet.py normalize` writes `pr` and `issues` under `fingerprint`;
    `--packet` takes them from there so the digest covers the same normalized
    records the review read. The result must equal the digest of the same
    fields supplied directly, and stdin must not carry its own `pr` or `issues`.
    """
    import tempfile

    packet = {
        "schema": "forge-packet/1",
        "fingerprint": {"pr": BASE["pr"], "issues": BASE["issues"]},
    }
    extra = {"specs": BASE["specs"], "guidance": BASE["guidance"]}
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "packet.json"
        path.write_text(json.dumps(packet), encoding="utf-8")

        def run_packet(stdin: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--packet", str(path)],
                input=stdin,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

        expected = digest("packet input baseline", BASE)
        result = run_packet(json.dumps(extra))
        if result.returncode != 0:
            fail("packet input", f"exit {result.returncode}: {result.stderr.strip()}")
        elif expected is not None and result.stdout.strip() != expected:
            fail("packet input", "--packet digest differs from the same fields supplied directly")

        result = run_packet("")
        bare = digest("packet input without extras", {"pr": BASE["pr"], "issues": BASE["issues"]})
        if result.returncode != 0 or (bare is not None and result.stdout.strip() != bare):
            fail("packet input without extras", f"empty stdin must mean no specs or guidance: exit {result.returncode}")

        result = run_packet(json.dumps({"pr": {"title": "x"}}))
        if result.returncode != 2 or "must not carry pr" not in result.stderr:
            fail("packet input conflict", f"stdin pr beside --packet must exit 2, got {result.returncode}")

        path.write_text(json.dumps({"fingerprint": {}}), encoding="utf-8")
        result = run_packet("")
        if result.returncode != 2 or "forge-packet/1" not in result.stderr:
            fail("packet input schema", f"unversioned packet must exit 2, got {result.returncode}")


def case_errors() -> None:
    """Malformed payloads are rejected, never silently hashed."""

    def non_integer_comment_id(payload):
        payload["issues"][0]["comments"][0]["id"] = "not-a-number"

    def float_comment_id(payload):
        payload["issues"][0]["comments"][0]["id"] = 42.5

    def negative_comment_id(payload):
        payload["issues"][0]["comments"][0]["id"] = -1

    def missing_comment_id(payload):
        del payload["issues"][0]["comments"][0]["id"]

    def issues_not_an_array(payload):
        payload["issues"] = {"acme/payments#123": {}}

    def pr_not_an_object(payload):
        payload["pr"] = ["title", "body"]

    def title_not_a_string(payload):
        payload["pr"]["title"] = 5

    def guidance_entry_not_an_object(payload):
        payload["guidance"].append("AGENTS.md")

    expect_error("non-integer comment id", variant(non_integer_comment_id), "must be a non-negative integer")
    expect_error("float comment id", variant(float_comment_id), "must be a non-negative integer")
    expect_error("negative comment id", variant(negative_comment_id), "must be a non-negative integer")
    expect_error("missing comment id", variant(missing_comment_id), "must be a non-negative integer")
    expect_error("issues is not an array", variant(issues_not_an_array), "issues must be an array")
    expect_error("pr is not an object", variant(pr_not_an_object), "pr must be an object")
    expect_error("pr title is not a string", variant(title_not_a_string), "must be a string or null")
    expect_error("guidance entry is not an object", variant(guidance_entry_not_an_object), "must be an object")
    expect_error("payload is not an object", None, "input must be an object", dumps='["not", "an", "object"]')
    expect_error("payload is not JSON", None, "", dumps="{not json")


def case_example() -> None:
    shown = subprocess.run([sys.executable, str(SCRIPT), "--example"], capture_output=True, text=True, encoding="utf-8", check=False)
    if shown.returncode != 0 or shown.stderr:
        fail("example", f"--example exited {shown.returncode}: {shown.stderr.strip()}")
        return
    value = digest("example digests", json.loads(shown.stdout))
    if value is not None and value != digest("example again", json.loads(shown.stdout)):
        fail("example", "the printed example does not digest deterministically")


CASES = (
    case_example,
    case_key_order_invariance,
    case_type_normalization,
    case_absent_fields_normalize,
    case_repeated_invocation,
    case_sensitivity,
    case_guidance_membership,
    case_comments_available,
    case_comments_complete,
    case_packet_input,
    case_errors,
)


def main() -> int:
    if not SCRIPT.exists():
        print(f"test_context_fingerprint: {SCRIPT} not found")
        return 1
    for case in CASES:
        case()
    for failure in failures:
        print(failure)
    if failures:
        print(f"test_context_fingerprint: {len(failures)} case(s) failed")
        return 1
    print(f"test_context_fingerprint: {len(CASES)} case group(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
