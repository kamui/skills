#!/usr/bin/env python3
"""One payload contract every arm produces and is validated against before masking.

#199 gap 6: in the pilot only one arm wrote structured ``items`` beside its review
body, so a populated array correlated with that arm and the masked packets carried
a structural tell. This is the prospective fix: one frozen envelope, one validator,
one file name, for every arm. A finding payload, a clean payload and a
stopped/unavailable payload have the same key set and differ only in the values a
grader is meant to read.

Usage::

    python3 scripts/payload.py validate --payload FILE [--arm ARM] [--attempt ID]
        [--expect-outcome findings|clean|stopped|unavailable]
        [--contract-validator PATH]
    python3 scripts/payload.py emit --out FILE --arm ARM --attempt ID
        --outcome stopped|unavailable --reason REASON [--detail TEXT]
    python3 scripts/payload.py accept --work DIR --receipt FILE --arm ARM
        --attempt ID --completion STATE [--stop-detail TEXT]
        [--contract-validator PATH]
    python3 scripts/payload.py uniformity --receipt FILE [--receipt FILE ...]
        [--require-arm ARM ...] [--require-outcome OUTCOME ...] [--strict-shape]
        [--out FILE]
    python3 scripts/payload.py --self-test

``validate`` checks one payload against the frozen envelope. ``emit`` writes the
stopped/unavailable payload for an attempt that produced none; it invents no
items and no body. ``accept`` is the coordinator's production gate for one
attempt: it refuses a second payload form, validates the payload the arm wrote or
emits the stopped one, refuses a payload that changed after a previous
acceptance, and retains a receipt. ``uniformity`` checks a set of receipts before
masking: one schema, one validator, one file form across every arm, and the
outcome coverage a freeze probe requires.

Input schema (UTF-8 JSON payload)::

    {"schema_version": "bounded-discovery-payload-v1",
     "attempt_id": "<attempt>", "arm": "<arm>",
     "outcome": "findings" | "clean" | "stopped" | "unavailable",
     "summary": {"body": "<published review body, empty for stopped>"},
     "items": [ {"type": "finding", "markdown": ..., "trailer": ...,
                 "anchor": {...}, "priority": "P1", "action": "must-fix",
                 "blocking": true, "kind": "bug", "fix": "path:line"},
                {"type": "question", "markdown": ..., "trailer": ...,
                 "anchor": {...}},
                {"type": "observation", "markdown": ...} ],
     "stop": null | {"reason": "<reason>", "detail": "<free text>"}}

Every key above is required in every payload of every arm; ``fix`` and an
anchor's optional members are the only omissible fields. Unknown keys are
violations, so an arm cannot carry a structure the other arms do not.

Exit: 0 success, 1 one or more contract violations, one line each on stdout,
2 an input cannot be read or an output cannot be written, named on stderr.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

SCHEMA_VERSION = "bounded-discovery-payload-v1"

# The one file every arm writes. A second form is what produced the pilot's tell.
PAYLOAD_NAME = "review-payload.json"
REJECTED_FORMS = ("review-payload.md", "review-payload.markdown", "review-payload.txt",
                  "review-payload.yaml", "review-payload.yml")

ENVELOPE_KEYS = ("schema_version", "attempt_id", "arm", "outcome", "summary",
                 "items", "stop")
OUTCOMES = ("findings", "clean", "stopped", "unavailable")
PRODUCED_OUTCOMES = ("findings", "clean")
EMPTY_OUTCOMES = ("stopped", "unavailable")

STOPPED_REASONS = ("budget", "wall-clock", "invalid", "cancelled")
UNAVAILABLE_REASONS = ("launch-refused", "launch-failed", "provider-error",
                       "runtime-error", "no-payload-retained")
REASONS = {"stopped": STOPPED_REASONS, "unavailable": UNAVAILABLE_REASONS}

# Required and optional members, per item type. Nothing else is accepted.
ITEM_KEYS = {
    "finding": (("type", "markdown", "trailer", "anchor", "priority", "action",
                 "blocking", "kind"), ("fix",)),
    "question": (("type", "markdown", "trailer", "anchor"), ()),
    "observation": (("type", "markdown"), ()),
}
PRIORITIES = ("P0", "P1", "P2", "P3")
FINDING_ACTIONS = ("must-fix", "consider")
SIDES = ("LEFT", "RIGHT")

# How a coordinator's completion state becomes an outcome when the attempt wrote
# no payload at all. A completion this table does not name is refused rather than
# guessed, because the outcome decides what a grader is later shown.
COMPLETION_OUTCOME = {
    "stopped-budget": ("stopped", "budget"),
    "stopped-wall-clock": ("stopped", "wall-clock"),
    "stopped-invalid": ("stopped", "invalid"),
    "stopped-isolation": ("stopped", "invalid"),
    "stopped-cancelled": ("stopped", "cancelled"),
    "stopped-runtime": ("unavailable", "runtime-error"),
    "stopped-finder": ("unavailable", "runtime-error"),
    "stopped-launch": ("unavailable", "launch-failed"),
    "reservation-refused": ("unavailable", "launch-refused"),
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def write_exclusive(path, document) -> None:
    """Create a record that no retry may overwrite, flushed to disk."""
    with open(path, "x", encoding="utf-8") as stream:
        json.dump(document, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def write_record(path, document) -> None:
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(document, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def key_problems(where, mapping, required, optional=()) -> list:
    """Exact membership: a missing key and an extra key are both violations."""
    problems = []
    present = set(mapping)
    for key in required:
        if key not in present:
            problems.append("%s: %s is required in every arm's payload" % (where, key))
    for key in sorted(present - set(required) - set(optional)):
        problems.append("%s: %s is not part of the frozen contract" % (where, key))
    return problems


def text_problems(where, value, allow_empty=False) -> list:
    if not isinstance(value, str):
        return ["%s: must be a string" % where]
    if not allow_empty and not value.strip():
        return ["%s: must not be empty" % where]
    return []


def anchor_problems(where, anchor) -> list:
    if not isinstance(anchor, dict):
        return ["%s: anchor must be an object" % where]
    kind = anchor.get("type")
    if kind == "file":
        problems = key_problems(where, anchor, ("type", "path"), ("side",))
    elif kind == "line":
        problems = key_problems(where, anchor,
                                ("type", "path", "start_line", "end_line", "side"))
    else:
        return ["%s: anchor type must be file or line" % where]
    problems += text_problems(where + ".path", anchor.get("path"))
    if "side" in anchor and anchor.get("side") not in SIDES:
        problems.append("%s.side: must be one of %s" % (where, ", ".join(SIDES)))
    if kind == "line":
        start, end = anchor.get("start_line"), anchor.get("end_line")
        for name, value in (("start_line", start), ("end_line", end)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                problems.append("%s.%s: must be a line number" % (where, name))
        if isinstance(start, int) and isinstance(end, int) and not isinstance(start, bool) \
                and not isinstance(end, bool) and end < start:
            problems.append("%s: end_line precedes start_line" % where)
    return problems


def item_problems(index, item) -> list:
    where = "items[%d]" % index
    if not isinstance(item, dict):
        return ["%s: must be an object" % where]
    kind = item.get("type")
    if kind not in ITEM_KEYS:
        return ["%s: type must be one of %s" % (where, ", ".join(sorted(ITEM_KEYS)))]
    required, optional = ITEM_KEYS[kind]
    problems = key_problems(where, item, required, optional)
    problems += text_problems(where + ".markdown", item.get("markdown"))
    if "trailer" in required:
        problems += text_problems(where + ".trailer", item.get("trailer"))
    if "anchor" in required:
        problems += anchor_problems(where + ".anchor", item.get("anchor"))
    if "fix" in item:
        problems += text_problems(where + ".fix", item.get("fix"))
    if kind == "finding":
        if item.get("priority") not in PRIORITIES:
            problems.append("%s.priority: must be one of %s" % (where, ", ".join(PRIORITIES)))
        if item.get("action") not in FINDING_ACTIONS:
            problems.append("%s.action: must be one of %s"
                            % (where, ", ".join(FINDING_ACTIONS)))
        if not isinstance(item.get("blocking"), bool):
            problems.append("%s.blocking: must be true or false" % where)
        problems += text_problems(where + ".kind", item.get("kind"))
    return problems


def stop_problems(stop, outcome) -> list:
    """``stop`` is present in every payload and null only for an attempt that ran
    to its own end. A stopped or unavailable outcome must name why."""
    if stop is None:
        if outcome in EMPTY_OUTCOMES:
            return ["stop: a %s payload must record its reason" % outcome]
        return []
    if not isinstance(stop, dict):
        return ["stop: must be null or an object"]
    problems = key_problems("stop", stop, ("reason", "detail"))
    problems += text_problems("stop.detail", stop.get("detail"))
    allowed = REASONS.get(outcome, STOPPED_REASONS + UNAVAILABLE_REASONS)
    if stop.get("reason") not in allowed:
        problems.append("stop.reason: a %s payload's reason must be one of %s"
                        % (outcome, ", ".join(allowed)))
    return problems


def validate_document(document, arm=None, attempt=None, expect_outcome=None) -> list:
    """Every violation of the frozen contract, one line each."""
    if not isinstance(document, dict):
        return ["payload: must be a JSON object"]
    problems = key_problems("payload", document, ENVELOPE_KEYS)
    if document.get("schema_version") != SCHEMA_VERSION:
        problems.append("schema_version: must be %s" % SCHEMA_VERSION)
    problems += text_problems("attempt_id", document.get("attempt_id"))
    problems += text_problems("arm", document.get("arm"))
    outcome = document.get("outcome")
    if outcome not in OUTCOMES:
        problems.append("outcome: must be one of %s" % ", ".join(OUTCOMES))

    summary = document.get("summary")
    body = None
    if not isinstance(summary, dict):
        problems.append("summary: must be an object carrying the review body")
    else:
        problems += key_problems("summary", summary, ("body",))
        body = summary.get("body")
        problems += text_problems("summary.body", body, allow_empty=True)

    items = document.get("items")
    if not isinstance(items, list):
        problems.append("items: every arm's payload carries an items array, empty or not")
        items = []
    else:
        for index, item in enumerate(items):
            problems += item_problems(index, item)

    problems += stop_problems(document.get("stop"), outcome)

    # Outcome and content have to agree, so a clean result and a stopped attempt
    # are never told apart by shape alone and neither can carry invented items.
    if outcome == "findings":
        if not items:
            problems.append("outcome findings: the items array is empty; a clean result "
                            "is the outcome for a review that raised nothing")
        if isinstance(body, str) and not body.strip():
            problems.append("outcome findings: the review body is empty")
    elif outcome == "clean":
        if items:
            problems.append("outcome clean: a clean result carries the empty items array")
        if isinstance(body, str) and not body.strip():
            problems.append("outcome clean: the review body is empty")
    elif outcome in EMPTY_OUTCOMES:
        if items:
            problems.append("outcome %s: no item may be invented for an attempt that "
                            "produced none" % outcome)
        if isinstance(body, str) and body != "":
            problems.append("outcome %s: the review body must be empty; retain the "
                            "attempt's own output as findings or clean instead" % outcome)

    if arm and document.get("arm") != arm:
        problems.append("arm: payload says %r, the attempt is arm %r"
                        % (document.get("arm"), arm))
    if attempt and document.get("attempt_id") != attempt:
        problems.append("attempt_id: payload says %r, the attempt is %r"
                        % (document.get("attempt_id"), attempt))
    if expect_outcome and outcome != expect_outcome:
        problems.append("outcome: expected %s, payload says %r" % (expect_outcome, outcome))
    return problems


def key_paths(document) -> list:
    """Every field path the payload actually carries, for the shape comparison."""
    paths = set()

    def walk(prefix, value):
        if isinstance(value, dict):
            for key, child in value.items():
                walk("%s.%s" % (prefix, key) if prefix else key, child)
        elif isinstance(value, list):
            for child in value:
                walk(prefix + "[]", child)
        else:
            paths.add(prefix)

    walk("", document)
    return sorted(paths)


def load_payload(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def contract_validator_problems(validator, document) -> list:
    """Run the study's pinned output-contract validator over the review itself.

    The envelope is arm-uniform by construction; this is where a freeze binds the
    deeper contract, and it is the identical program for every arm. The review is
    fed on stdin as ``{"summary": ..., "items": ...}``, which is what the skill's
    own ``validate_review.py`` reads. A stopped or unavailable payload holds no
    review, so there is nothing for it to validate and it is not run.
    """
    if document["outcome"] not in PRODUCED_OUTCOMES:
        return []
    review = json.dumps({"summary": document["summary"], "items": document["items"]})
    try:
        done = subprocess.run([sys.executable, str(validator)], input=review,
                              capture_output=True, text=True, encoding="utf-8", timeout=600)
    except subprocess.SubprocessError as exc:
        return ["pinned contract validator did not complete: %s" % exc]
    if done.returncode == 0:
        return []
    lines = [line for line in (done.stdout or "").splitlines() if line.strip()]
    if not lines:
        lines = [(done.stderr or "").strip() or "no output"]
    return ["pinned contract validator exited %d: %s" % (done.returncode, line)
            for line in lines]


def build_stop_payload(arm, attempt, outcome, reason, detail) -> dict:
    return {"schema_version": SCHEMA_VERSION, "attempt_id": attempt, "arm": arm,
            "outcome": outcome, "summary": {"body": ""}, "items": [],
            "stop": {"reason": reason, "detail": detail}}


def command_validate(args) -> int:
    document = load_payload(args.payload)
    problems = validate_document(document, args.arm, args.attempt, args.expect_outcome)
    if not problems and args.contract_validator:
        problems = contract_validator_problems(args.contract_validator, document)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def command_emit(args) -> int:
    if args.outcome not in EMPTY_OUTCOMES:
        print("emit writes only a %s payload; a review payload is the arm's own output"
              % " or ".join(EMPTY_OUTCOMES))
        return 1
    document = build_stop_payload(args.arm, args.attempt, args.outcome, args.reason,
                                  args.detail or "no payload was retained for this attempt")
    problems = validate_document(document, args.arm, args.attempt, args.outcome)
    if problems:
        for problem in problems:
            print(problem)
        return 1
    write_exclusive(args.out, document)
    return 0


def accept(work, receipt_path, arm, attempt, completion, stop_detail=None,
           contract_validator=None) -> tuple:
    """Validate or produce this attempt's payload and retain its receipt.

    Returns ``(receipt or None, problems)``. Nothing is written when the payload
    violates the contract, so masking never sees an unvalidated payload.
    """
    work = Path(work)
    payload_path = work / PAYLOAD_NAME
    problems = []

    # A second payload form is the tell itself, and it may hold real findings, so
    # it is refused rather than ignored or overwritten.
    for name in REJECTED_FORMS:
        other = work / name
        if other.exists():
            problems.append("%s carries a second payload form; the contract is one %s, and "
                            "its findings must be carried into that file before masking"
                            % (other, PAYLOAD_NAME))
    if problems:
        return None, problems

    produced_by = "arm"
    if not payload_path.exists():
        if completion == "complete":
            return None, ["a complete attempt produced no %s; the contract payload is "
                          "required in every arm" % PAYLOAD_NAME]
        if completion not in COMPLETION_OUTCOME:
            return None, ["completion %r has no frozen outcome; classify the attempt "
                          "before masking it" % completion]
        outcome, reason = COMPLETION_OUTCOME[completion]
        document = build_stop_payload(arm, attempt, outcome, reason,
                                      stop_detail or "the attempt ended as %s and retained "
                                                     "no payload" % completion)
        write_exclusive(payload_path, document)
        produced_by = "coordinator"

    document = load_payload(payload_path)
    problems = validate_document(document, arm, attempt)
    if not problems and completion == "complete" and document["outcome"] in EMPTY_OUTCOMES:
        problems.append("a complete attempt cannot be masked as %s" % document["outcome"])
    if not problems and completion != "complete" and document["outcome"] in PRODUCED_OUTCOMES \
            and document.get("stop") is None:
        problems.append("the attempt ended as %s, so its payload must record the stop that "
                        "ended it beside the output it kept" % completion)
    if not problems and contract_validator:
        problems += contract_validator_problems(contract_validator, document)
    if problems:
        return None, problems

    payload_sha = sha256_file(payload_path)
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": "bounded-discovery-payload-receipt",
        "accepted_at": now(),
        "attempt_id": attempt, "arm": arm, "completion": completion,
        "outcome": document["outcome"],
        "produced_by": produced_by,
        "source_form": PAYLOAD_NAME,
        "items_present": True,
        "item_count": len(document["items"]),
        "item_types": sorted({item["type"] for item in document["items"]}),
        "body_sha256": sha256_bytes(document["summary"]["body"].encode("utf-8")),
        "payload_sha256": payload_sha,
        "validator_sha256": sha256_file(Path(__file__).resolve()),
        "contract_validator": ({"path": str(Path(contract_validator).resolve()),
                                "sha256": sha256_file(contract_validator)}
                               if contract_validator else None),
        "key_paths": key_paths(document),
        "stop": document["stop"],
    }
    receipt_path = Path(receipt_path)
    if receipt_path.exists():
        previous = json.loads(receipt_path.read_text(encoding="utf-8"))
        if previous.get("payload_sha256") != payload_sha:
            return None, ["the payload changed after acceptance %s; an accepted payload is "
                          "what gets masked and it is not rewritten"
                          % previous.get("accepted_at")]
        receipt["accepted_at"] = previous.get("accepted_at", receipt["accepted_at"])
    write_record(receipt_path, receipt)
    return receipt, []


def command_accept(args) -> int:
    receipt, problems = accept(args.work, args.receipt, args.arm, args.attempt,
                               args.completion, args.stop_detail, args.contract_validator)
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print(json.dumps({"outcome": receipt["outcome"], "item_count": receipt["item_count"],
                      "produced_by": receipt["produced_by"],
                      "payload_sha256": receipt["payload_sha256"]}))
    return 0


def uniformity(receipts, require_arms=(), require_outcomes=(), strict_shape=False) -> dict:
    """Compare accepted payloads across arms before anything is masked."""
    problems = []
    documents = []
    for path in receipts:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        document["_path"] = str(path)
        documents.append(document)
    if not documents:
        return {"passed": False, "problems": ["no receipt was supplied; masking needs one "
                                              "accepted payload per attempt"], "arms": {}}

    for document in documents:
        where = document["_path"]
        if document.get("artifact_id") != "bounded-discovery-payload-receipt":
            problems.append("%s is not a payload receipt; every arm's payload passes the "
                            "same acceptance gate" % where)
        if document.get("source_form") != PAYLOAD_NAME:
            problems.append("%s records source form %r; the contract is one %s in every arm"
                            % (where, document.get("source_form"), PAYLOAD_NAME))
        if not document.get("items_present"):
            problems.append("%s records no items array; a payload without one is the "
                            "structural tell this contract removes" % where)

    for field in ("schema_version", "validator_sha256"):
        values = sorted({str(document.get(field)) for document in documents})
        if len(values) > 1:
            problems.append("receipts disagree on %s (%s); one frozen contract and one "
                            "pinned validator govern every arm" % (field, ", ".join(values)))
    contracts = sorted({json.dumps(document.get("contract_validator"), sort_keys=True)
                        for document in documents})
    if len(contracts) > 1:
        problems.append("receipts name different pinned contract validators; A, B and C "
                        "are validated by the same program or the comparison is not blind")

    arms = {}
    for document in documents:
        entry = arms.setdefault(str(document.get("arm")),
                                {"receipts": 0, "outcomes": {}, "key_paths": set(),
                                 "item_counts": []})
        entry["receipts"] += 1
        outcome = str(document.get("outcome"))
        entry["outcomes"][outcome] = entry["outcomes"].get(outcome, 0) + 1
        entry["key_paths"].update(document.get("key_paths") or [])
        entry["item_counts"].append(document.get("item_count"))

    for arm in require_arms:
        if arm not in arms:
            problems.append("arm %s produced no accepted payload; every arm is masked under "
                            "the same contract or none is" % arm)
    for arm in sorted(arms) if not require_arms else require_arms:
        for outcome in require_outcomes:
            if arm in arms and outcome not in arms[arm]["outcomes"]:
                problems.append("arm %s never produced a %s payload; the freeze probes every "
                                "outcome in every arm" % (arm, outcome))

    # A field only one arm ever carries is a shape correlation. Under the closed
    # schema it can only be an omissible field, so it is reported as evidence a
    # freeze must rule on, and fails the check when the caller asked it to.
    correlations = []
    if len(arms) > 1:
        for path in sorted(set().union(*(entry["key_paths"] for entry in arms.values()))):
            carrying = sorted(arm for arm, entry in arms.items() if path in entry["key_paths"])
            if len(carrying) == 1:
                correlations.append({"key_path": path, "only_arm": carrying[0]})
    if strict_shape and correlations:
        for correlation in correlations:
            problems.append("%s appears only in arm %s; a masked packet's shape would "
                            "correlate with its arm"
                            % (correlation["key_path"], correlation["only_arm"]))

    return {"schema_version": SCHEMA_VERSION,
            "artifact_id": "bounded-discovery-payload-uniformity",
            "checked_at": now(), "receipts": len(documents),
            "arms": {arm: {"receipts": entry["receipts"], "outcomes": entry["outcomes"],
                           "item_counts": entry["item_counts"],
                           "key_paths": sorted(entry["key_paths"])}
                     for arm, entry in sorted(arms.items())},
            "shape_correlations": correlations,
            "strict_shape": bool(strict_shape),
            "problems": problems, "passed": not problems}


def command_uniformity(args) -> int:
    report = uniformity(args.receipt, args.require_arm, args.require_outcome,
                        args.strict_shape)
    if args.out:
        write_record(args.out, report)
    for problem in report["problems"]:
        print(problem)
    return 0 if report["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("operation", nargs="?",
                        choices=("validate", "emit", "accept", "uniformity"))
    parser.add_argument("--payload")
    parser.add_argument("--work", help="the cell's work directory, for accept")
    parser.add_argument("--receipt", action="append", default=[],
                        help="acceptance receipt; repeatable for uniformity")
    parser.add_argument("--out")
    parser.add_argument("--arm")
    parser.add_argument("--attempt")
    parser.add_argument("--completion", help="the coordinator's completion state")
    parser.add_argument("--outcome", choices=OUTCOMES)
    parser.add_argument("--expect-outcome", choices=OUTCOMES)
    parser.add_argument("--reason", choices=sorted(set(STOPPED_REASONS + UNAVAILABLE_REASONS)))
    parser.add_argument("--detail")
    parser.add_argument("--stop-detail")
    parser.add_argument("--contract-validator",
                        help="the study's pinned output-contract validator, run over the "
                             "same payload in every arm")
    parser.add_argument("--require-arm", action="append", default=[])
    parser.add_argument("--require-outcome", action="append", default=[], choices=OUTCOMES)
    parser.add_argument("--strict-shape", action="store_true",
                        help="fail when a field appears in only one arm")
    parser.add_argument("--self-test", action="store_true")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return subprocess.run([sys.executable,
                               str(Path(__file__).with_name("test_payload.py"))]).returncode
    if not args.operation:
        parser.error("an operation is required")
    if args.operation == "validate" and not args.payload:
        parser.error("validate requires --payload")
    if args.operation == "emit" and not (args.out and args.arm and args.attempt
                                         and args.outcome and args.reason):
        parser.error("emit requires --out, --arm, --attempt, --outcome and --reason")
    if args.operation == "accept" and not (args.work and args.receipt and args.arm
                                           and args.attempt and args.completion):
        parser.error("accept requires --work, --receipt, --arm, --attempt and --completion")
    if args.operation == "accept" and len(args.receipt) != 1:
        parser.error("accept writes exactly one receipt")
    if args.operation == "uniformity" and not args.receipt:
        parser.error("uniformity requires at least one --receipt")
    try:
        if args.operation == "validate":
            return command_validate(args)
        if args.operation == "emit":
            return command_emit(args)
        if args.operation == "accept":
            args.receipt = args.receipt[0]
            return command_accept(args)
        return command_uniformity(args)
    except ValueError as exc:
        print("payload: %s" % exc)
        return 1
    except OSError as exc:
        sys.stderr.write("%s\n" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
