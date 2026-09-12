#!/usr/bin/env python3
"""Drive the uniform payload contract through its CLI, passing and refusing.

Usage: python3 scripts/test_payload.py
Input: synthetic payloads in temporary directories only; no study, provider
session or container is launched. Exit: 0 pass, 1 test failures.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import payload

SCRIPT = str(Path(payload.__file__).resolve())

# A validator stand-in for a study's pinned output-contract program: it refuses a
# body that does not carry the run trailer the contract requires.
FIXTURE_VALIDATOR = '''#!/usr/bin/env python3
import json, sys
review = json.load(sys.stdin)
body = (review.get("summary") or {}).get("body", "")
if "<!-- review-run" not in body:
    print("summary.body: the run trailer is missing")
    sys.exit(1)
sys.exit(0)
'''


def finding(fix=None):
    item = {"type": "finding", "markdown": "The retry loop never resets its counter.",
            "trailer": "<!-- finding id=code/retry head=abc priority=P1 action=must-fix -->",
            "anchor": {"type": "line", "path": "src/retry.ts", "start_line": 42,
                       "end_line": 44, "side": "RIGHT"},
            "priority": "P1", "action": "must-fix", "blocking": True, "kind": "bug"}
    if fix:
        item["fix"] = fix
    return item


def question():
    return {"type": "question", "markdown": "Is the queue drained before shutdown?",
            "trailer": "<!-- question id=code/queue head=abc action=question -->",
            "anchor": {"type": "file", "path": "src/queue.ts"}}


def observation():
    return {"type": "observation", "markdown": "One sentence. Evidence: `redis.conf:19`."}


def envelope(arm="A", attempt="attempt-1", outcome="findings", items=None, body=None,
             stop=None):
    if items is None:
        items = [finding(), question(), observation()] if outcome == "findings" else []
    if body is None:
        body = "" if outcome in payload.EMPTY_OUTCOMES else \
            "## Review\n\nMode: retrospective.\n\n<!-- review-run head=abc -->"
    return {"schema_version": payload.SCHEMA_VERSION, "attempt_id": attempt, "arm": arm,
            "outcome": outcome, "summary": {"body": body}, "items": items, "stop": stop}


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.work = self.base / "work"
        self.work.mkdir()
        self.receipt = self.base / "payload-receipt.json"

    def call(self, *args, expected=0):
        result = subprocess.run([sys.executable, SCRIPT, *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(result.returncode, expected,
                         "argv=%s\n%s%s" % (args, result.stdout, result.stderr))
        return result

    def write_payload(self, document, name=payload.PAYLOAD_NAME):
        path = self.work / name
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        return path

    def validator(self):
        path = self.base / "pinned_contract.py"
        path.write_text(FIXTURE_VALIDATOR, encoding="utf-8")
        return path

    # -- validate ---------------------------------------------------------

    def test_every_outcome_validates_under_one_key_set(self):
        shapes = []
        for arm, outcome, stop in (("A", "findings", None), ("B", "clean", None),
                                   ("C", "stopped", {"reason": "budget", "detail": "ceiling"}),
                                   ("A", "unavailable",
                                    {"reason": "provider-error", "detail": "502 at turn 43"})):
            document = envelope(arm=arm, outcome=outcome, stop=stop)
            path = self.write_payload(document, "payload-%s-%s.json" % (arm, outcome))
            self.call("validate", "--payload", path, "--arm", arm,
                      "--expect-outcome", outcome)
            shapes.append(tuple(sorted(document)))
        self.assertEqual(len(set(shapes)), 1, "every outcome carries the same envelope keys")

    def test_a_stopped_payload_keeps_findings_out_and_a_clean_one_keeps_items_empty(self):
        cases = {
            "outcome stopped": envelope(outcome="stopped", items=[finding()],
                                        stop={"reason": "budget", "detail": "d"}),
            "outcome clean": envelope(outcome="clean", items=[observation()]),
            "outcome findings": envelope(outcome="findings", items=[]),
            "stop: a stopped payload": envelope(outcome="stopped"),
        }
        for expected, document in cases.items():
            path = self.write_payload(document, "case-%s.json" % abs(hash(expected)))
            result = self.call("validate", "--payload", path, expected=1)
            self.assertIn(expected, result.stdout, result.stdout)

    def test_a_stopped_payload_may_not_carry_a_review_body(self):
        document = envelope(outcome="stopped", body="I did not finish, but probably fine.",
                            stop={"reason": "budget", "detail": "d"})
        path = self.write_payload(document, "bodied-stop.json")
        result = self.call("validate", "--payload", path, expected=1)
        self.assertIn("the review body must be empty", result.stdout)

    def test_arm_specific_structure_is_refused(self):
        document = envelope()
        document["finder_claims"] = ["arm C only"]
        path = self.write_payload(document, "extra-envelope.json")
        self.assertIn("finder_claims is not part of the frozen contract",
                      self.call("validate", "--payload", path, expected=1).stdout)

        document = envelope()
        document["items"][0]["confidence"] = 0.9
        path = self.write_payload(document, "extra-item.json")
        self.assertIn("items[0]: confidence is not part of the frozen contract",
                      self.call("validate", "--payload", path, expected=1).stdout)

        document = envelope()
        del document["items"]
        path = self.write_payload(document, "no-items.json")
        self.assertIn("items is required in every arm's payload",
                      self.call("validate", "--payload", path, expected=1).stdout)

    def test_item_and_anchor_rules(self):
        for mutate, expected in (
                (lambda d: d["items"][0].update(priority="urgent"), "items[0].priority"),
                (lambda d: d["items"][0].update(action="question"), "items[0].action"),
                (lambda d: d["items"][0].update(blocking="yes"), "items[0].blocking"),
                (lambda d: d["items"][0].update(markdown="  "), "items[0].markdown"),
                (lambda d: d["items"][0]["anchor"].update(side="MIDDLE"),
                 "items[0].anchor.side"),
                (lambda d: d["items"][0]["anchor"].update(end_line=1),
                 "items[0].anchor: end_line precedes start_line"),
                (lambda d: d["items"][0]["anchor"].pop("side"),
                 "items[0].anchor: side is required"),
                (lambda d: d["items"][2].update(anchor={"type": "file", "path": "a"}),
                 "items[2]: anchor is not part of the frozen contract"),
                (lambda d: d["items"][1].update(type="insight"), "items[1]: type must be one of"),
        ):
            document = envelope()
            mutate(document)
            path = self.write_payload(document, "item-%d.json" % abs(hash(expected)))
            result = self.call("validate", "--payload", path, expected=1)
            self.assertIn(expected, result.stdout, result.stdout)

    def test_identity_and_unreadable_input(self):
        path = self.write_payload(envelope(arm="A", attempt="attempt-1"), "identity.json")
        result = self.call("validate", "--payload", path, "--arm", "B",
                           "--attempt", "attempt-9", expected=1)
        self.assertIn("payload says 'A', the attempt is arm 'B'", result.stdout)
        self.assertIn("payload says 'attempt-1', the attempt is 'attempt-9'", result.stdout)
        markdown = self.work / "not-json.json"
        markdown.write_text("## Review\n\nA markdown payload.\n", encoding="utf-8")
        self.call("validate", "--payload", markdown, expected=1)
        self.call("validate", "--payload", self.work / "absent.json", expected=2)

    # -- emit -------------------------------------------------------------

    def test_emit_writes_a_stopped_payload_once_and_never_a_review(self):
        out = self.base / "stopped.json"
        self.call("emit", "--out", out, "--arm", "B", "--attempt", "attempt-2",
                  "--outcome", "unavailable", "--reason", "provider-error",
                  "--detail", "502 at turn 43")
        document = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(document["items"], [])
        self.assertEqual(document["summary"]["body"], "")
        self.assertEqual(document["stop"]["reason"], "provider-error")
        self.call("validate", "--payload", out, "--arm", "B", "--expect-outcome", "unavailable")
        self.call("emit", "--out", out, "--arm", "B", "--attempt", "attempt-2",
                  "--outcome", "unavailable", "--reason", "provider-error", expected=2)
        result = self.call("emit", "--out", self.base / "other.json", "--arm", "B",
                           "--attempt", "attempt-2", "--outcome", "findings",
                           "--reason", "budget", expected=1)
        self.assertIn("the arm's own output", result.stdout)
        self.assertFalse((self.base / "other.json").exists())

    # -- accept -----------------------------------------------------------

    def accept(self, completion, expected=0, **extra):
        args = ["accept", "--work", self.work, "--receipt", self.receipt, "--arm", "A",
                "--attempt", "attempt-1", "--completion", completion]
        for key, value in extra.items():
            args += ["--" + key.replace("_", "-"), value]
        return self.call(*args, expected=expected)

    def test_accept_retains_what_the_arm_produced(self):
        self.write_payload(envelope(items=[finding("src/retry.ts:18"), observation()]))
        self.accept("complete")
        receipt = json.loads(self.receipt.read_text(encoding="utf-8"))
        self.assertEqual(receipt["produced_by"], "arm")
        self.assertEqual(receipt["outcome"], "findings")
        self.assertEqual(receipt["item_count"], 2)
        self.assertTrue(receipt["items_present"])
        self.assertEqual(receipt["source_form"], payload.PAYLOAD_NAME)
        self.assertIn("items[].fix", receipt["key_paths"])

    def test_accept_is_rerunnable_but_a_changed_payload_is_refused(self):
        self.write_payload(envelope())
        self.accept("complete")
        first = json.loads(self.receipt.read_text(encoding="utf-8"))
        self.accept("complete")
        self.assertEqual(json.loads(self.receipt.read_text(encoding="utf-8"))["accepted_at"],
                         first["accepted_at"])
        self.write_payload(envelope(items=[finding(), finding(), observation()]))
        result = self.accept("complete", expected=1)
        self.assertIn("the payload changed after acceptance", result.stdout)
        self.assertEqual(json.loads(self.receipt.read_text(encoding="utf-8")), first)

    def test_a_stopped_attempt_gets_a_stopped_payload_with_no_invented_items(self):
        self.accept("stopped-budget", stop_detail="the frozen ceiling stopped phase 2")
        written = json.loads((self.work / payload.PAYLOAD_NAME).read_text(encoding="utf-8"))
        self.assertEqual(written["outcome"], "stopped")
        self.assertEqual(written["items"], [])
        self.assertEqual(written["summary"]["body"], "")
        receipt = json.loads(self.receipt.read_text(encoding="utf-8"))
        self.assertEqual(receipt["produced_by"], "coordinator")
        self.assertEqual(receipt["item_count"], 0)
        self.assertEqual(receipt["stop"]["reason"], "budget")

    def test_a_coordinator_payload_stays_coordinator_produced_on_re_acceptance(self):
        self.accept("stopped-budget")
        first = json.loads(self.receipt.read_text(encoding="utf-8"))
        self.assertEqual(first["produced_by"], "coordinator")
        # Settlement is re-runnable: the payload now exists either way, and the
        # origin record is what keeps "the arm wrote this" from becoming true.
        self.accept("stopped-budget")
        again = json.loads(self.receipt.read_text(encoding="utf-8"))
        self.assertEqual(again["produced_by"], "coordinator")
        self.assertEqual(again["payload_sha256"], first["payload_sha256"])
        # The origin record is kept beside the receipt, never in the work
        # directory the arm writes to, so the arm cannot plant one.
        self.assertTrue(payload.origin_for(self.receipt).is_file())
        self.assertFalse(any(self.work.glob("*" + payload.ORIGIN_SUFFIX)))
        forged = self.base / "forged-work"
        forged.mkdir()
        receipt_name = "forged-receipt.json"
        receipt = self.base / receipt_name
        (forged / payload.PAYLOAD_NAME).write_text(
            json.dumps(envelope(outcome="stopped",
                                stop={"reason": "budget", "detail": "I gave up"})),
            encoding="utf-8")
        (forged / (Path(receipt_name).stem + payload.ORIGIN_SUFFIX)).write_text(json.dumps(
            {"produced_by": "coordinator",
             "payload_sha256": payload.sha256_file(forged / payload.PAYLOAD_NAME)}),
            encoding="utf-8")
        self.call("accept", "--work", forged, "--receipt", receipt, "--arm", "A",
                  "--attempt", "attempt-1", "--completion", "stopped-budget")
        self.assertEqual(json.loads(receipt.read_text(encoding="utf-8"))["produced_by"], "arm")

    def test_emit_records_its_origin_where_the_coordinator_keeps_it(self):
        out = self.work / payload.PAYLOAD_NAME
        origin_path = payload.origin_for(self.receipt)
        self.call("emit", "--out", out, "--arm", "A", "--attempt", "attempt-1",
                  "--outcome", "unavailable", "--reason", "launch-failed",
                  "--origin", origin_path)
        origin = json.loads(origin_path.read_text(encoding="utf-8"))
        self.assertEqual(origin["payload_sha256"], payload.sha256_file(out))
        self.accept("stopped-runtime")
        self.assertEqual(json.loads(self.receipt.read_text(encoding="utf-8"))["produced_by"],
                         "coordinator")

    def test_a_provider_error_is_unavailable_and_a_complete_attempt_must_produce(self):
        self.accept("stopped-runtime")
        self.assertEqual(json.loads(self.receipt.read_text(encoding="utf-8"))["outcome"],
                         "unavailable")
        empty = tempfile.TemporaryDirectory()
        self.addCleanup(empty.cleanup)
        result = self.call("accept", "--work", empty.name, "--receipt",
                           self.base / "second.json", "--arm", "A", "--attempt", "a",
                           "--completion", "complete", expected=1)
        self.assertIn("a complete attempt produced no", result.stdout)
        self.assertFalse((Path(empty.name) / payload.PAYLOAD_NAME).exists())
        self.assertFalse((self.base / "second.json").exists())

    def test_an_unclassified_completion_is_refused_rather_than_guessed(self):
        result = self.accept("stopped-mystery", expected=1)
        self.assertIn("has no frozen outcome", result.stdout)
        self.assertFalse((self.work / payload.PAYLOAD_NAME).exists())

    def test_a_second_payload_form_is_refused_and_its_content_is_left_alone(self):
        markdown = self.work / "review-payload.md"
        markdown.write_text("## Review\n\nA real finding lives here.\n", encoding="utf-8")
        result = self.accept("stopped-budget", expected=1)
        self.assertIn("carries a second payload form", result.stdout)
        self.assertFalse((self.work / payload.PAYLOAD_NAME).exists())
        self.assertIn("A real finding lives here", markdown.read_text(encoding="utf-8"))
        self.assertFalse(self.receipt.exists())

    def test_completion_and_outcome_must_agree(self):
        self.write_payload(envelope(outcome="stopped",
                                    stop={"reason": "budget", "detail": "d"}))
        self.assertIn("cannot be masked as stopped", self.accept("complete", expected=1).stdout)
        self.write_payload(envelope())
        self.assertIn("must record the stop that ended it",
                      self.accept("stopped-budget", expected=1).stdout)
        self.write_payload(envelope(stop={"reason": "budget",
                                          "detail": "stopped after the payload was written"}))
        self.accept("stopped-budget")
        receipt = json.loads(self.receipt.read_text(encoding="utf-8"))
        self.assertEqual(receipt["outcome"], "findings")
        self.assertEqual(receipt["item_count"], 3)

    def test_the_pinned_contract_validator_gates_a_review_and_skips_a_stop(self):
        validator = self.validator()
        self.write_payload(envelope(body="## Review\n\nNo trailer here."))
        result = self.accept("complete", contract_validator=str(validator), expected=1)
        self.assertIn("pinned contract validator exited 1", result.stdout)
        self.assertFalse(self.receipt.exists())
        (self.work / payload.PAYLOAD_NAME).unlink()
        self.write_payload(envelope())
        self.accept("complete", contract_validator=str(validator))
        self.assertEqual(json.loads(self.receipt.read_text(encoding="utf-8"))
                         ["contract_validator"]["sha256"], payload.sha256_file(validator))
        # A stopped payload holds no review, so the review validator is not run
        # against it and its refusal cannot invent one.
        other = self.base / "stopped-work"
        other.mkdir()
        self.call("accept", "--work", other, "--receipt", self.base / "stop-receipt.json",
                  "--arm", "C", "--attempt", "attempt-3", "--completion", "stopped-budget",
                  "--contract-validator", validator)


class UniformityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def call(self, *args, expected=0):
        result = subprocess.run([sys.executable, SCRIPT, *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(result.returncode, expected,
                         "argv=%s\n%s%s" % (args, result.stdout, result.stderr))
        return result

    def receipts(self, arms=("A", "B", "C"), outcomes=("findings", "clean", "stopped"),
                 fix_arm=None):
        paths = []
        for arm in arms:
            for outcome in outcomes:
                work = self.base / ("work-%s-%s" % (arm, outcome))
                work.mkdir()
                attempt = "attempt-%s-%s" % (arm, outcome)
                completion = "complete" if outcome in ("findings", "clean") else "stopped-budget"
                if outcome != "stopped":
                    items = [finding("src/a.ts:1" if arm == fix_arm else None)] \
                        if outcome == "findings" else []
                    document = envelope(arm=arm, attempt=attempt, outcome=outcome, items=items)
                    (work / payload.PAYLOAD_NAME).write_text(
                        json.dumps(document, indent=2), encoding="utf-8")
                receipt = self.base / ("receipt-%s-%s.json" % (arm, outcome))
                self.call("accept", "--work", work, "--receipt", receipt, "--arm", arm,
                          "--attempt", attempt, "--completion", completion)
                paths.append(receipt)
        return paths

    def uniformity(self, paths, *extra, expected=0):
        args = ["uniformity"]
        for path in paths:
            args += ["--receipt", str(path)]
        return self.call(*args, *extra, expected=expected)

    def test_three_arms_under_one_contract_pass_with_full_outcome_coverage(self):
        paths = self.receipts()
        out = self.base / "uniformity.json"
        self.uniformity(paths, "--require-arm", "A", "--require-arm", "B", "--require-arm", "C",
                        "--require-outcome", "findings", "--require-outcome", "clean",
                        "--require-outcome", "stopped", "--out", out)
        report = json.loads(out.read_text(encoding="utf-8"))
        self.assertTrue(report["passed"])
        self.assertEqual(sorted(report["arms"]), ["A", "B", "C"])
        self.assertEqual(report["shape_correlations"], [])

    def test_a_missing_arm_or_outcome_blocks_masking(self):
        paths = self.receipts(arms=("A", "B"))
        result = self.uniformity(paths, "--require-arm", "A", "--require-arm", "B",
                                 "--require-arm", "C", expected=1)
        self.assertIn("arm C produced no accepted payload", result.stdout)
        paths = self.receipts(arms=("C",), outcomes=("findings",))
        result = self.uniformity(paths, "--require-outcome", "stopped", expected=1)
        self.assertIn("arm C never produced a stopped payload", result.stdout)

    def test_the_pilot_tell_is_refused(self):
        paths = self.receipts(arms=("A",), outcomes=("findings",))
        for field, value, expected in (
                ("source_form", "review-payload.md", "records source form 'review-payload.md'"),
                ("items_present", False, "records no items array")):
            stale = json.loads(paths[0].read_text(encoding="utf-8"))
            stale.update(arm="B", **{field: value})
            tell = self.base / ("tell-%s.json" % field)
            tell.write_text(json.dumps(stale), encoding="utf-8")
            result = self.uniformity(paths + [tell], expected=1)
            self.assertIn(expected, result.stdout)

    def test_a_second_validator_or_contract_is_refused(self):
        paths = self.receipts(arms=("A",), outcomes=("findings",))
        forked = json.loads(paths[0].read_text(encoding="utf-8"))
        forked.update(arm="B", validator_sha256="0" * 64,
                      contract_validator={"path": "/other.py", "sha256": "1" * 64})
        other = self.base / "forked.json"
        other.write_text(json.dumps(forked), encoding="utf-8")
        result = self.uniformity(paths + [other], expected=1)
        self.assertIn("receipts disagree on validator_sha256", result.stdout)
        self.assertIn("different pinned contract validators", result.stdout)

    def test_a_field_only_one_arm_carries_blocks_until_it_is_ruled_on(self):
        paths = self.receipts(arms=("A", "B"), outcomes=("findings",), fix_arm="A")
        result = self.uniformity(paths, expected=1)
        self.assertIn("items[].fix appears only in arm A", result.stdout)
        out = self.base / "shape.json"
        self.uniformity(paths, "--allow-shape-correlation", "items[].fix", "--out", out)
        report = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(report["shape_correlations"],
                         [{"key_path": "items[].fix", "only_arm": "A",
                           "ruled_acceptable": True}])
        self.assertEqual(report["allowed_shape_correlations"], ["items[].fix"])
        # The ruling is per field: one on another field leaves this one blocking.
        self.assertIn("items[].fix appears only in arm A",
                      self.uniformity(paths, "--allow-shape-correlation",
                                      "items[].anchor.side", expected=1).stdout)

    def test_a_non_receipt_and_a_missing_receipt_are_refused(self):
        stray = self.base / "stray.json"
        stray.write_text(json.dumps({"arm": "A", "outcome": "findings"}), encoding="utf-8")
        self.assertIn("is not a payload receipt", self.uniformity([stray], expected=1).stdout)
        self.uniformity([self.base / "absent.json"], expected=2)
        self.call("uniformity", expected=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
