#!/usr/bin/env python3
"""CLI regressions for brief construction and return accounting.

Usage: python3 scripts/test_verifier_handoff.py
Inputs: synthetic records in disposable directories; no forge or worker calls.
Exit 0: checks pass; 1: assertion failure; 2: a subprocess cannot run.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent
HEAD = "a" * 40
BASE = "b" * 40


def ev(coordinate="src/a.py:10", text="support: enabled\nconfidence = 1"):
    return {"coordinate": coordinate, "text": text, "support": "PRIVATE_NESTED"}


def candidate(key="a/bug", kind="bug"):
    return {"id": key, "kind": kind, "priority": "P2", "action": "must-fix",
            "title": "Retain a key", "claim": "Retries replace the key", "trigger": "A response is lost",
            "impact": "A duplicate charge is created", "change": "Keep the original key",
            "anchor": {"type": "line", "path": "src/a.py", "start_line": 10, "end_line": 12,
                       "side": "RIGHT", "support": "PRIVATE_ANCHOR"}, "fix": "src/b.py:20",
            "evidence": [ev()], "ranges": {"anchor": ev(text="src/a.py: +10,3"), "fix": ev("src/b.py:20", "src/b.py: +20,2")},
            "support": {"inspected": "PRIVATE_SUPPORT"}, "confidence": "PRIVATE_CONFIDENCE",
            "conclusion": "PRIVATE_CONCLUSION", "argument": "PRIVATE_ARGUMENT"}


def row(key="a/row", kind="bug"):
    return {"id": key, "kind": kind, "claim": "The empty queue is guarded", "disposition": "refuted",
            "falsification": "prevented only when queue is empty before dispatch",
            "evidence": ev(), "support": "PRIVATE_ROW"}


def input_data(mode="candidate-only", candidates=None, ids=None):
    return {"run": {"id": "run-1", "repository": "/tmp/checkout", "base": BASE, "head": HEAD,
                    "merge_base": BASE, "support": "PRIVATE_RUN"},
            "batch": {"id": "batch-1", "phase": "initial", "mode": mode},
            "run_policy": "No execution; bounded semantics traces only.",
            "sources": [ev("issue-219/criterion-1", "Keep the key")],
            "candidates": [candidate()] if candidates is None else candidates,
            "ledger_ids": [] if ids is None else ids, "support": "PRIVATE_ROOT"}


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.count = 0

    def tearDown(self):
        self.temp.cleanup()

    def path(self, suffix):
        self.count += 1
        return self.root / f"{self.count}-{suffix}"

    def write(self, value, suffix="input.json"):
        path = self.path(suffix)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def run_cli(self, script, *args, code=0, scripts=SCRIPTS):
        result = subprocess.run([sys.executable, str(scripts / script), *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def build(self, data=None, ledger=None, code=0, scripts=SCRIPTS):
        output = self.path("bundle")
        result = self.run_cli("build_verifier_prompt.py", self.write(input_data() if data is None else data),
                              "--ledger", self.write([] if ledger is None else ledger),
                              "--output", output, code=code, scripts=scripts)
        if code:
            self.assertFalse(output.exists(), result.stdout)
        return output

    def returned(self, bundle):
        manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
        result = {"manifest_sha256": hashlib.sha256((bundle / "manifest.json").read_bytes()).hexdigest(),
                  "candidates": [{"id": key, "verdict": "confirmed", "basis": "Changed line replaces the key",
                                  "evidence": [ev()]} for key in manifest["candidate_ids"]],
                  "ledger": [{"id": key, "ruling": "holds", "evidence": [ev("src/a.py:19")]} for key in manifest["ledger_ids"]],
                  "duplicate_groups": [], "observation": None}
        if manifest["batch"]["mode"] == "complete-ledger":
            result["conclusion"] = "clean verdict stands"
        return result

    def account(self, bundle, returned, code=0, scripts=SCRIPTS):
        raw = self.write(returned, "raw.json")
        before = raw.read_bytes()
        report = self.path("accounting.json")
        self.run_cli("account_verifier_return.py", "--bundle", bundle, "--output", report, raw, code=code, scripts=scripts)
        self.assertEqual(raw.read_bytes(), before)
        if report.exists():
            result = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(result["return"], returned)
            return result
        return None

    def test_batch_modes_initial_and_followup(self):
        for phase in ("initial", "follow-up"):
            for mode, candidates, rows in (
                ("candidate-only", [candidate()], []),
                ("complete-ledger", [], [row()]),
                ("complete-ledger", [], []),
                ("complete-ledger", [candidate()], [row("a/bug")]),
                ("related-acquittal", [candidate()], [row()]),
                ("related-acquittal", [], [row()]),
            ):
                with self.subTest(phase=phase, mode=mode, candidates=len(candidates), rows=len(rows)):
                    data = input_data(mode, candidates, [r["id"] for r in rows])
                    data["batch"]["phase"] = phase
                    bundle = self.build(data, rows)
                    report = self.account(bundle, self.returned(bundle))
                    self.assertTrue(report["structurally_complete"])
                    self.assertEqual(report["withheld"], {"candidates": [], "ledger": []})

    def test_projection_preserves_raw_evidence_and_excludes_private_fields(self):
        data = input_data("complete-ledger", [candidate()], ["a/bug"])
        data["candidates"][0]["test_evidence"] = [{"command": "python3 test_retry.py", "head": HEAD,
                                                  "exit_status": 1, "output": "support: bad key",
                                                  "support": "PRIVATE_TEST"}]
        bundle = self.build(data, [row("a/bug")])
        projected = json.loads((bundle / "input.json").read_text(encoding="utf-8"))
        brief = (bundle / "brief.md").read_text(encoding="utf-8")
        self.assertNotIn("PRIVATE_", brief)
        self.assertEqual(projected["candidates"][0]["evidence"][0]["text"], ev()["text"])
        self.assertEqual(projected["candidates"][0]["test_evidence"][0]["output"], "support: bad key")
        self.assertEqual(projected["ledger"][0]["falsification"], row()["falsification"])
        self.assertEqual(projected["candidates"][0]["ranges"]["fix"]["text"], "src/b.py: +20,2")

    def test_conditional_bundles_and_unavailable_evidence(self):
        data = input_data("complete-ledger", [candidate(kind="concurrency")], ["a/row"])
        c = data["candidates"][0]
        c["requirement_source"] = "artifact-sdk@2/api:send"
        c["rule_source"] = "base:AGENTS.md:5"
        c["conformance"] = {"coordinate": "artifact-sdk@2/api:send", "version": "sdk@2",
                             "artifact": [ev("sdk@2/api:10", "send(key)")],
                             "consumer_sites": [{"unavailable": "consumer artifact inaccessible", "coordinate": "consumer/aliases.py"}],
                             "support": "PRIVATE_ARTIFACT"}
        c["test_evidence"] = [{"unavailable": "offline dependencies"}]
        rows = [row()]
        rows[0]["released_compatibility"] = {"coordinate": "pr-body/change", "promise": "Change capacity", "scope": "released 1.6",
            **{key: [{"unavailable": "No " + key}] for key in ("documentation", "tests", "callers", "release_decision")}}
        bundle = self.build(data, rows)
        brief = (bundle / "brief.md").read_text(encoding="utf-8")
        self.assertIn("# Verifier bug-class check", brief)
        self.assertIn("## Conformance verifier procedure", brief)
        self.assertIn("Intent, approval, or a benchmark alone", brief)
        self.assertIn("consumer artifact inaccessible", brief)
        self.assertIn("base:AGENTS.md:5", brief)
        ordinary = (self.build() / "brief.md").read_text(encoding="utf-8")
        self.assertNotIn("# Verifier bug-class check", ordinary)
        self.assertNotIn("## Conformance verifier procedure", ordinary)
        self.assertNotIn("Intent, approval, or a benchmark alone", ordinary)

    def test_build_refusals(self):
        variants = []
        for repository in (".", "relative/checkout"):
            data = input_data()
            data["run"]["repository"] = repository
            variants.append((data, []))
        data = input_data("complete-ledger", [], [])
        variants.append((data, [row()]))
        variants.append((input_data("related-acquittal", [], ["missing"]), [row()]))
        variants.append((input_data("related-acquittal", [], ["a/row", "a/row"]), [row()]))
        variants.append((input_data(), [row(), row()]))
        variants.append((input_data(candidates=[candidate(), candidate()]), []))
        variants.append((input_data(candidates=[]), []))
        for field in ("trigger", "ranges", "anchor", "evidence"):
            data = input_data()
            del data["candidates"][0][field]
            variants.append((data, []))
        data = input_data()
        data["candidates"][0]["requirement_source"] = "artifact-a@1/file:name"
        variants.append((data, []))
        data = input_data()
        data["candidates"][0]["requirement_source"] = "pr-body/promise"
        variants.append((data, []))
        data = input_data()
        data["candidates"][0]["test_evidence"] = [{"command": "test", "head": BASE, "exit_status": 0, "output": "pass"}]
        variants.append((data, []))
        for i, (data, rows) in enumerate(variants):
            with self.subTest(case=i):
                self.build(data, rows, code=1)
        data["candidates"][0].pop("test_evidence")
        data["candidates"][0]["requirement_source"] = "pr-body/promise"
        data["sources"] = [ev("pr-title", "Change retries"), {"coordinate": "pr-body", "unavailable": "body fetch failed"}]
        self.build(data)

    def test_complete_ledger_uses_authoritative_rows_related_selection_is_model_owned(self):
        unrelated = row("other/lock", "maintainability")
        data = input_data("related-acquittal", [candidate()], [unrelated["id"]])
        bundle = self.build(data, [row(), unrelated])
        projected = json.loads((bundle / "input.json").read_text(encoding="utf-8"))
        self.assertEqual([r["id"] for r in projected["ledger"]], ["other/lock"])
        data["batch"]["mode"] = "complete-ledger"
        self.build(data, [row(), unrelated], code=1)

    def test_wrong_run_batch_and_tampered_bundle(self):
        first = self.build()
        for field, value in (("id", "run-2"), ("head", "c" * 40)):
            data = input_data()
            data["run"][field] = value
            second = self.build(data)
            report = self.account(second, self.returned(first), code=1)
            self.assertEqual(report["accounted"]["candidates"], [])
        data = input_data()
        data["batch"].update(id="batch-2", phase="follow-up")
        self.account(self.build(data), self.returned(first), code=1)
        returned = self.returned(first)
        (first / "brief.md").write_text("tampered", encoding="utf-8")
        self.assertIsNone(self.account(first, returned, code=1))

    def test_missing_duplicate_unknown_wrong_role_and_invalid_verdicts(self):
        bundle = self.build(input_data("complete-ledger", [candidate(), candidate("b/bug")], ["a/bug"]), [row("a/bug")])
        for mutation in (
            lambda r: r["candidates"].pop(0),
            lambda r: r["candidates"].append(copy.deepcopy(r["candidates"][0])),
            lambda r: r["candidates"][0].update(id="unknown"),
            lambda r: r["candidates"][0].update(verdict="plausible"),
            lambda r: r["candidates"][0].update(verdict="refuted", basis="contradiction"),
            lambda r: r["candidates"][0].update(verdict="refuted", basis="unresolved"),
            lambda r: r["candidates"][0].update(basis=""),
            lambda r: r["candidates"][0].update(evidence=[]),
            lambda r: r["candidates"].__setitem__(0, copy.deepcopy(r["ledger"][0])),
        ):
            returned = self.returned(bundle)
            mutation(returned)
            report = self.account(bundle, returned, code=1)
            self.assertIn("b/bug", report["accounted"]["candidates"])
            self.assertIn("a/bug", report["withheld"]["candidates"])
            self.assertIn("a/bug", report["accounted"]["ledger"])
        for mutation in (
            lambda r: r["ledger"].clear(),
            lambda r: r["ledger"].append(copy.deepcopy(r["ledger"][0])),
            lambda r: r["ledger"][0].update(id="b/bug"),
            lambda r: r["ledger"][0].update(ruling="confirmed"),
            lambda r: r["ledger"].append(123),
            lambda r: r["ledger"].__setitem__(0, copy.deepcopy(r["candidates"][0])),
        ):
            returned = self.returned(bundle)
            mutation(returned)
            report = self.account(bundle, returned, code=1)
            self.assertFalse(report["conclusion_accounted"])
            self.assertEqual(report["accounted"]["candidates"], ["a/bug", "b/bug"])

    def test_refutation_bases(self):
        bundle = self.build()
        for basis in ("contradicted", "prevented", "intentional", "pre-existing", "no-consequence", "unresolved"):
            returned = self.returned(bundle)
            returned["candidates"][0].update(verdict="refuted", basis=basis)
            if basis == "unresolved":
                returned["candidates"][0]["settling_fact"] = "Maintainer can supply the intended delivery guarantee."
                returned["candidates"][0]["evidence"] = [{"unavailable": "Product decision not recorded"}]
            self.account(bundle, returned)
        bundle = self.build(input_data(candidates=[candidate(kind="requirement")]))
        returned = self.returned(bundle)
        returned["candidates"][0].update(verdict="refuted", basis="pre-existing")
        self.account(bundle, returned, code=1)

    def test_conclusion_does_not_substitute_for_rows_or_candidates(self):
        bundle = self.build(input_data("complete-ledger", [candidate()], ["a/row"]), [row()])
        returned = self.returned(bundle)
        returned["ledger"][0].update(ruling="re-open", failed_step="Missing empty guard")
        self.account(bundle, returned, code=1)
        returned["conclusion"] = {"re_open": ["a/row"]}
        self.account(bundle, returned)
        returned["candidates"] = []
        report = self.account(bundle, returned, code=1)
        self.assertTrue(report["conclusion_accounted"])
        self.assertEqual(report["withheld"]["candidates"], ["a/bug"])
        for mode, rows in (("candidate-only", []), ("related-acquittal", [row()])):
            bundle = self.build(input_data(mode, [candidate()], [r["id"] for r in rows]), rows)
            returned = self.returned(bundle)
            returned["conclusion"] = "clean verdict stands"
            self.account(bundle, returned, code=1)

    def test_corrections_safety_duplicates_and_observation_preserved(self):
        bundle = self.build(input_data(candidates=[candidate(), candidate("b/bug")]))
        returned = self.returned(bundle)
        returned["candidates"][0]["corrections"] = {"priority": "P3", "action": "consider", "trigger": "Only on timeout",
            "impact": "One duplicate", "anchor": candidate()["anchor"], "fix": "src/b.py:22", "change": "Keep the key"}
        returned["candidates"][0]["safety_rulings"] = [{"path": "src/queue.py", "conditions": "steady state under lock",
            "premise": "queue nonempty", "ruling": "holds", "evidence": [ev("src/queue.py:22")]}]
        returned["duplicate_groups"] = [["a/bug", "b/bug"]]
        returned["observation"] = {"fact": "The timeout defaults to one second.", "evidence": [ev("config.py:2")]}
        self.account(bundle, returned)
        for mutation in (
            lambda r: r["candidates"][0]["corrections"].update(priority="P4"),
            lambda r: r["candidates"][0]["safety_rulings"][0].pop("conditions"),
            lambda r: r.update(observation=[r["observation"], r["observation"]]),
            lambda r: r.update(duplicate_groups=[["a/bug", "unknown"]]),
        ):
            invalid = copy.deepcopy(returned)
            mutation(invalid)
            self.account(bundle, invalid, code=1)

    def test_raw_parse_failures_and_no_overwrites(self):
        bundle = self.build()
        for raw_text in ('not JSON', '{"candidates": [], "candidates": []}', 'NaN'):
            raw = self.path("raw.json")
            raw.write_text(raw_text, encoding="utf-8")
            report = self.path("report.json")
            self.run_cli("account_verifier_return.py", "--bundle", bundle, "--output", report, raw, code=1)
            result = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(result["withheld"]["candidates"], ["a/bug"])
            self.assertEqual(raw.read_text(encoding="utf-8"), raw_text)
        raw = self.write(self.returned(bundle))
        self.run_cli("account_verifier_return.py", "--bundle", bundle, "--output", raw, raw, code=2)
        self.run_cli("build_verifier_prompt.py", self.write(input_data()), "--ledger", self.write([]), "--output", bundle, code=2)
        self.run_cli("build_verifier_prompt.py", self.root / "missing", "--ledger", self.write([]), "--output", self.path("bundle"), code=2)

    def test_standalone_install(self):
        skill = self.root / "installed" / "code-review-inspect"
        shutil.copytree(SCRIPTS.parent, skill, ignore=shutil.ignore_patterns("__pycache__"))
        bundle = self.build(scripts=skill / "scripts")
        self.account(bundle, self.returned(bundle), scripts=skill / "scripts")


if __name__ == "__main__":
    try:
        unittest.main()
    except OSError as error:
        print(f"test_verifier_handoff: cannot run CLI: {error}", file=sys.stderr)
        raise SystemExit(2)
