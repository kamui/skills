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

import build_verifier_prompt as builder

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


def premise(key="premise-1", area="concurrency"):
    return {"id": key, "area": area, "premise": "The lookup always succeeds before `updateShardId()` runs",
            "evidence": [ev("src/c.py:40", "sender = lookup(id)")], "support": "PRIVATE_PREMISE"}


def input_data(candidates=None, premises=None):
    return {"run": {"id": "run-1", "repository": "/tmp/checkout", "base": BASE, "head": HEAD,
                    "merge_base": BASE, "support": "PRIVATE_RUN"},
            "batch": {"id": "batch-1", "phase": "initial"},
            "run_policy": "No execution; bounded semantics traces only.",
            "sources": [ev("issue-219/criterion-1", "Keep the key")],
            "candidates": [candidate()] if candidates is None else candidates,
            "premises": [] if premises is None else premises, "support": "PRIVATE_ROOT"}


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

    def build(self, data=None, code=0, scripts=SCRIPTS):
        output = self.path("bundle")
        result = self.run_cli("build_verifier_prompt.py", self.write(input_data() if data is None else data),
                              "--output", output, code=code, scripts=scripts)
        if code:
            self.assertFalse(output.exists(), result.stdout)
        return output

    def returned(self, bundle):
        manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
        return {"manifest_sha256": hashlib.sha256((bundle / "manifest.json").read_bytes()).hexdigest(),
                "candidates": [{"id": key, "verdict": "confirmed", "basis": "Changed line replaces the key",
                                "evidence": [ev()]} for key in manifest["candidate_ids"]],
                "premises": [{"id": key, "ruling": "holds", "evidence": [ev("src/c.py:38", "if id in table:")]}
                             for key in manifest["premise_ids"]],
                "duplicate_groups": [], "observation": None}

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

    def test_task_mixes_initial_and_followup(self):
        for phase in ("initial", "follow-up"):
            for candidates, premises in (([candidate()], []), ([], [premise()]), ([candidate()], [premise()])):
                with self.subTest(phase=phase, candidates=len(candidates), premises=len(premises)):
                    data = input_data(candidates, premises)
                    data["batch"]["phase"] = phase
                    bundle = self.build(data)
                    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
                    self.assertEqual(manifest["format"], "verifier-manifest/2")
                    self.assertEqual(manifest["premise_ids"], [p["id"] for p in premises])
                    report = self.account(bundle, self.returned(bundle))
                    self.assertTrue(report["structurally_complete"])
                    self.assertEqual(report["withheld"], {"candidates": [], "premises": []})
                    self.assertEqual(report["accounted"]["premises"], [p["id"] for p in premises])

    def test_retired_ledger_modes_are_not_projected(self):
        data = input_data()
        data["batch"]["mode"] = "complete-ledger"
        data["ledger_ids"] = ["a/row"]
        bundle = self.build(data)
        projected = json.loads((bundle / "input.json").read_text(encoding="utf-8"))
        self.assertEqual(projected["batch"], {"id": "batch-1", "phase": "initial"})
        self.assertNotIn("ledger", projected)
        brief = (bundle / "brief.md").read_text(encoding="utf-8").lower()
        for retired in ("clean verdict", "complete-ledger", "related-acquittal", "ledger row", "attackable"):
            self.assertNotIn(retired, brief)
        self.run_cli("build_verifier_prompt.py", self.write(input_data()), "--ledger", self.write([]),
                     "--output", self.path("bundle"), code=2)

    def test_brief_carries_the_safety_premise_task(self):
        brief = (self.build(input_data([], [premise()])) / "brief.md").read_text(encoding="utf-8")
        self.assertIn("## Safety premises and scoped safety rulings", brief)
        self.assertIn("Trace the opposite branch", brief)
        self.assertIn("updateShardId()", brief)
        self.assertNotIn("PRIVATE_", brief)

    def test_commit_requirement_sources(self):
        for role in ("candidate", "premise"):
            item = candidate() if role == "candidate" else premise(area="compatibility")
            item["requirement_source"] = 'commit-abcdef0/"Keep the key"'
            data = input_data([item], []) if role == "candidate" else input_data([], [item])
            data["sources"] = [ev("commit-abcdef0", "Keep the key\n\nAcross retries.")]
            bundle = self.build(data)
            self.assertIn('Keep the key', (bundle / 'brief.md').read_text(encoding='utf-8'))
            self.account(bundle, self.returned(bundle))
            data["sources"] = [ev("commit-1234567", "A different commit")]
            self.build(data, code=1)
            item["requirement_source"] = 'commit-notasha/"Keep the key"'
            self.build(data, code=1)

    def test_projection_preserves_raw_evidence_and_excludes_private_fields(self):
        data = input_data([candidate()], [premise()])
        data["candidates"][0]["test_evidence"] = [{"command": "python3 test_retry.py", "head": HEAD,
                                                  "exit_status": 1, "output": "support: bad key",
                                                  "support": "PRIVATE_TEST"}]
        bundle = self.build(data)
        projected = json.loads((bundle / "input.json").read_text(encoding="utf-8"))
        brief = (bundle / "brief.md").read_text(encoding="utf-8")
        self.assertNotIn("PRIVATE_", brief)
        self.assertEqual(projected["candidates"][0]["evidence"][0]["text"], ev()["text"])
        self.assertEqual(projected["candidates"][0]["test_evidence"][0]["output"], "support: bad key")
        self.assertEqual(projected["premises"][0]["premise"], premise()["premise"])
        self.assertEqual(projected["candidates"][0]["ranges"]["fix"]["text"], "src/b.py: +20,2")

    def test_conditional_bundles_and_unavailable_evidence(self):
        data = input_data([candidate(kind="concurrency")], [premise(area="compatibility")])
        c = data["candidates"][0]
        c["requirement_source"] = "artifact-sdk@2/api:send"
        c["rule_source"] = "base:AGENTS.md:5"
        c["conformance"] = {"coordinate": "artifact-sdk@2/api:send", "version": "sdk@2",
                             "artifact": [ev("sdk@2/api:10", "send(key)")],
                             "consumer_sites": [{"unavailable": "consumer artifact inaccessible", "coordinate": "consumer/aliases.py"}],
                             "support": "PRIVATE_ARTIFACT"}
        c["test_evidence"] = [{"unavailable": "offline dependencies"}]
        data["premises"][0]["released_compatibility"] = {"coordinate": "pr-body/change", "promise": "Change capacity", "scope": "released 1.6",
            **{key: [{"unavailable": "No " + key}] for key in ("documentation", "tests", "callers", "release_decision")}}
        bundle = self.build(data)
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

    def test_brief_embeds_focused_test_rules_without_primary_wrapper(self):
        brief = (self.build() / "brief.md").read_text(encoding="utf-8")
        self.assertIn("## Focused-test safety and execution", brief)
        self.assertIn("run the changed test or the smallest affected group once", brief)
        self.assertNotIn("run_events.py", brief)
        self.assertNotIn("wrap --private-dir", brief)
        self.assertNotIn("Primary focused-test recording", brief)

    def test_brief_is_self_contained_for_the_worker(self):
        brief = (self.build() / "brief.md").read_text(encoding="utf-8")
        self.assertIn("Read nothing outside this brief", brief)
        self.assertNotIn("SKILL.md", brief)
        self.assertNotIn("What the primary does with the return", brief)
        self.assertNotIn("## Supplied check evidence", brief)
        data = input_data()
        data["candidates"][0]["test_evidence"] = [{"command": "pytest tests/test_a.py", "head": HEAD,
                                                   "exit_status": 0, "output": "1 passed"}]
        with_evidence = (self.build(data) / "brief.md").read_text(encoding="utf-8")
        self.assertIn("## Supplied check evidence", with_evidence)
        self.assertIn("A new head is an invalidation boundary", with_evidence)
        self.assertNotIn("SKILL.md", with_evidence)
        self.assertNotIn("## Primary accounting", with_evidence)
        self.assertNotIn("Account for supplied checks", with_evidence)

    def test_instruction_sections_reject_missing_duplicate_or_reversed_boundaries(self):
        source = self.root / "instruction.md"
        for content in ("start\nbody", "end\nstart\nbody", "start\nstart\nend\n"):
            source.write_text(content, encoding="utf-8")
            with self.assertRaises(builder.ContentError):
                builder.section(self.root, source.name, "start\n", "end\n")
        source.write_text("preface\nstart\nworker\nend\nprimary\n", encoding="utf-8")
        self.assertEqual(builder.section(self.root, source.name, "start\n", "end\n"), "worker\n")

    def test_example_input_builds(self):
        result = self.run_cli("build_verifier_prompt.py", "--example")
        example = json.loads(result.stdout)
        example["run"]["repository"] = str(self.root)
        bundle = self.build(example)
        self.assertTrue((bundle / "brief.md").exists())
        self.account(bundle, self.returned(bundle))

    def test_build_refusals(self):
        variants = []
        for repository in (".", "relative/checkout"):
            data = input_data()
            data["run"]["repository"] = repository
            variants.append(data)
        variants.append(input_data([], []))
        variants.append(input_data([candidate(), candidate()]))
        variants.append(input_data([candidate("same")], [premise("same")]))
        variants.append(input_data([], [premise(), premise()]))
        for field in ("area", "premise", "evidence"):
            data = input_data([], [premise()])
            del data["premises"][0][field]
            variants.append(data)
        variants.append(input_data([], [premise(area="performance")]))
        data = input_data([], [premise()])
        data["premises"][0]["premise"] = "First line\nsecond line"
        variants.append(data)
        for field in ("trigger", "ranges", "anchor", "evidence"):
            data = input_data()
            del data["candidates"][0][field]
            variants.append(data)
        data = input_data()
        data["candidates"][0]["requirement_source"] = "artifact-a@1/file:name"
        variants.append(data)
        data = input_data()
        data["candidates"][0]["requirement_source"] = "pr-body/promise"
        variants.append(data)
        data = input_data()
        data["candidates"][0]["test_evidence"] = [{"command": "test", "head": BASE, "exit_status": 0, "output": "pass"}]
        variants.append(data)
        for i, data in enumerate(variants):
            with self.subTest(case=i):
                self.build(data, code=1)
        data["candidates"][0].pop("test_evidence")
        data["candidates"][0]["requirement_source"] = "pr-body/promise"
        data["sources"] = [ev("pr-title", "Change retries"), {"coordinate": "pr-body", "unavailable": "body fetch failed"}]
        self.build(data)

    def test_wrong_run_batch_and_tampered_bundle(self):
        first = self.build(input_data([candidate()], [premise()]))
        for field, value in (("id", "run-2"), ("head", "c" * 40)):
            data = input_data([candidate()], [premise()])
            data["run"][field] = value
            second = self.build(data)
            report = self.account(second, self.returned(first), code=1)
            self.assertEqual(report["accounted"], {"candidates": [], "premises": []})
            self.assertEqual(report["withheld"], {"candidates": ["a/bug"], "premises": ["premise-1"]})
        data = input_data([candidate()], [premise()])
        data["batch"].update(id="batch-2", phase="follow-up")
        self.account(self.build(data), self.returned(first), code=1)
        returned = self.returned(first)
        (first / "brief.md").write_text("tampered", encoding="utf-8")
        self.assertIsNone(self.account(first, returned, code=1))

    def test_missing_duplicate_unknown_wrong_role_and_invalid_verdicts(self):
        bundle = self.build(input_data([candidate(), candidate("b/bug")], [premise()]))
        for mutation in (
            lambda r: r["candidates"].pop(0),
            lambda r: r["candidates"].append(copy.deepcopy(r["candidates"][0])),
            lambda r: r["candidates"][0].update(id="unknown"),
            lambda r: r["candidates"][0].update(verdict="plausible"),
            lambda r: r["candidates"][0].update(verdict="refuted", basis="contradiction"),
            lambda r: r["candidates"][0].update(verdict="refuted", basis="unresolved"),
            lambda r: r["candidates"][0].update(basis=""),
            lambda r: r["candidates"][0].update(evidence=[]),
            lambda r: r["candidates"][0].update(evidence=[{"unavailable": "could not read the anchor"}]),
            lambda r: r["candidates"][0].update(verdict="refuted", basis="prevented", evidence=[{"unavailable": "guard not found"}]),
            lambda r: r["candidates"].__setitem__(0, copy.deepcopy(r["premises"][0])),
        ):
            returned = self.returned(bundle)
            mutation(returned)
            report = self.account(bundle, returned, code=1)
            self.assertIn("b/bug", report["accounted"]["candidates"])
            self.assertIn("a/bug", report["withheld"]["candidates"])
            self.assertIn("premise-1", report["accounted"]["premises"])
        for mutation in (
            lambda r: r["premises"].clear(),
            lambda r: r["premises"].append(copy.deepcopy(r["premises"][0])),
            lambda r: r["premises"][0].update(id="a/bug"),
            lambda r: r["premises"][0].update(ruling="re-open"),
            lambda r: r["premises"][0].update(ruling="fails"),
            lambda r: r["premises"][0].update(ruling="unresolved"),
            lambda r: r["premises"][0].update(evidence=[{"unavailable": "table not inspected"}]),
            lambda r: r["premises"].__setitem__(0, copy.deepcopy(r["candidates"][0])),
        ):
            returned = self.returned(bundle)
            mutation(returned)
            report = self.account(bundle, returned, code=1)
            self.assertEqual(report["withheld"]["premises"], ["premise-1"])
            self.assertEqual(report["accounted"]["candidates"], ["a/bug", "b/bug"])
        for retired in (lambda r: r.update(ledger=[]), lambda r: r.update(conclusion="clean verdict stands"),
                        lambda r: r.pop("premises"), lambda r: r["premises"].append(123)):
            returned = self.returned(bundle)
            retired(returned)
            self.assertFalse(self.account(bundle, returned, code=1)["structurally_complete"])

    def test_premise_rulings(self):
        bundle = self.build(input_data([], [premise()]))
        for ruling, extra in (("holds", {}), ("fails", {"failed_step": "A missed lookup leaves `sender` NULL at src/c.py:41"}),
                              ("unresolved", {"settling_fact": "The operator can say whether failover runs concurrently",
                                              "evidence": [{"unavailable": "failover scheduling is configured outside the repository"}]})):
            with self.subTest(ruling=ruling):
                returned = self.returned(bundle)
                returned["premises"][0].update(ruling=ruling, **extra)
                report = self.account(bundle, returned)
                self.assertEqual(report["accounted"]["premises"], ["premise-1"])

    def test_refutation_bases(self):
        bundle = self.build()
        for basis in ("contradicted", "prevented", "intentional", "pre-existing", "no-consequence", "unresolved"):
            returned = self.returned(bundle)
            returned["candidates"][0].update(verdict="refuted", basis=basis)
            if basis == "unresolved":
                returned["candidates"][0]["settling_fact"] = "Maintainer can supply the intended delivery guarantee."
                returned["candidates"][0]["evidence"] = [{"unavailable": "Product decision not recorded"}]
            self.account(bundle, returned)
        bundle = self.build(input_data([candidate(kind="requirement")]))
        returned = self.returned(bundle)
        returned["candidates"][0].update(verdict="refuted", basis="pre-existing")
        self.account(bundle, returned, code=1)

    def test_corrections_safety_duplicates_and_observation_preserved(self):
        bundle = self.build(input_data([candidate(), candidate("b/bug")]))
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
        bundle = self.build(input_data([candidate()], [premise()]))
        for raw_text in ('not JSON', '{"candidates": [], "candidates": []}', 'NaN'):
            raw = self.path("raw.json")
            raw.write_text(raw_text, encoding="utf-8")
            report = self.path("report.json")
            self.run_cli("account_verifier_return.py", "--bundle", bundle, "--output", report, raw, code=1)
            result = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(result["withheld"], {"candidates": ["a/bug"], "premises": ["premise-1"]})
            self.assertEqual(raw.read_text(encoding="utf-8"), raw_text)
        raw = self.write(self.returned(bundle))
        self.run_cli("account_verifier_return.py", "--bundle", bundle, "--output", raw, raw, code=2)
        self.run_cli("build_verifier_prompt.py", self.write(input_data()), "--output", bundle, code=2)
        self.run_cli("build_verifier_prompt.py", self.root / "missing", "--output", self.path("bundle"), code=2)

    def test_standalone_install(self):
        skill = self.root / "installed" / "review-code"
        shutil.copytree(SCRIPTS.parent, skill, ignore=shutil.ignore_patterns("__pycache__"))
        bundle = self.build(input_data([candidate()], [premise()]), scripts=skill / "scripts")
        self.account(bundle, self.returned(bundle), scripts=skill / "scripts")


if __name__ == "__main__":
    try:
        unittest.main()
    except OSError as error:
        print(f"test_verifier_handoff: cannot run CLI: {error}", file=sys.stderr)
        raise SystemExit(2)
