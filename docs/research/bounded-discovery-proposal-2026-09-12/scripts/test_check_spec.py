#!/usr/bin/env python3
"""Drive check_spec.py through its command line over synthetic readiness records.

Usage: python3 scripts/test_check_spec.py
Input: disposable synthetic bundles, plus the committed record for one case.
Exit: 0 pass, 1 test failures.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
CHECK = HERE / "check_spec.py"


def run(*args):
    return subprocess.run([sys.executable, str(CHECK), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8", timeout=60)


def row(identifier, **overrides):
    base = {"id": identifier, "source": "#199", "title": identifier, "status": "tooling-delivered",
            "controls": ["controls/thing.py"], "tests": ["controls/test_thing.py::test_alpha"],
            "probes": [], "evidence_required": "runtime evidence", "open_questions": []}
    base.update(overrides)
    return base


class CheckSpecTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        controls = self.root / "controls"
        controls.mkdir()
        (controls / "thing.py").write_text("# a control\n", encoding="utf-8")
        (controls / "test_thing.py").write_text(
            "class T:\n    def test_alpha(self):\n        pass\n", encoding="utf-8")
        self.bundle = self.root / "bundle"
        self.bundle.mkdir()
        (self.bundle / "probes.md").write_text(
            "| # | Control |\n| --- | --- |\n| P01 | one |\n| P02 | two |\n", encoding="utf-8")
        self.document = {
            "schema_version": "v1", "document_status": "proposed", "written_at": "2026-09-12",
            "specification": "spec.md", "probe_catalogue": "probes.md",
            "produced_for": {"freeze_gate_issue": 207},
            "requirements": [row("gap-%d" % n) for n in range(1, 11)]}
        self.document["requirements"][0]["probes"] = ["P01"]
        self.document["requirements"][1]["probes"] = ["P02"]
        (self.bundle / "spec.md").write_text(
            "\n".join("### %s" % r["id"] for r in self.document["requirements"]) + "\n",
            encoding="utf-8")

    def write(self, document=None):
        path = self.bundle / "readiness.json"
        path.write_text(json.dumps(document or self.document), encoding="utf-8")
        return path

    def check(self, document=None, expected=1):
        result = run("--spec", self.write(document), "--repo-root", self.root)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def mutated(self, index=0, **overrides):
        document = copy.deepcopy(self.document)
        document["requirements"][index].update(overrides)
        return document

    def test_the_committed_record_passes_as_written(self):
        result = run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")

    def test_a_well_formed_synthetic_record_passes(self):
        self.assertEqual(self.check(expected=0), "")

    def test_a_status_that_claims_establishment_is_refused_by_name(self):
        for status, word in (("established", "established"), ("frozen", "frozen"),
                             ("qualified", "qualified"), ("authorized", "authorized"),
                             ("evidence-approved", "approved")):
            output = self.check(self.mutated(status=status))
            self.assertIn("claims the requirement is %s" % word, output)

    def test_an_unrecognised_status_is_refused(self):
        self.assertIn("is not one of", self.check(self.mutated(status="mostly-there")))

    def test_delivered_tooling_must_name_a_control_and_a_test(self):
        self.assertIn("delivered tooling is named", self.check(self.mutated(tests=[])))
        self.assertIn("delivered tooling is named", self.check(self.mutated(controls=[])))

    def test_a_specified_only_row_may_not_name_tests(self):
        self.assertIn("is specified-only but names tests",
                      self.check(self.mutated(status="specified-only")))

    def test_an_unresolved_row_must_say_what_is_unresolved(self):
        for status in ("unknown", "budget-dependent"):
            output = self.check(self.mutated(status=status, controls=[], tests=[]))
            self.assertIn("records no open question", output)
            self.assertNotIn("delivered tooling", output)
        self.assertEqual(self.check(self.mutated(status="unknown", controls=[], tests=[],
                                                 open_questions=["which runtime"]),
                                    expected=0), "")

    def test_a_renamed_or_missing_test_is_caught(self):
        self.assertIn("which controls/test_thing.py does not define",
                      self.check(self.mutated(tests=["controls/test_thing.py::test_gone"])))
        self.assertIn("names test file controls/absent.py",
                      self.check(self.mutated(tests=["controls/absent.py::test_alpha"])))
        self.assertIn("is not <path>::<test name>",
                      self.check(self.mutated(tests=["controls/test_thing.py"])))

    def test_a_missing_control_is_caught(self):
        self.assertIn("names control controls/absent.py",
                      self.check(self.mutated(controls=["controls/absent.py"])))

    def test_a_path_that_leaves_the_repository_is_refused_rather_than_resolved(self):
        outside = self.root.parent / ("outside-%s.py" % self.root.name)
        outside.write_text("def test_alpha(self):\n    pass\n", encoding="utf-8")
        self.addCleanup(outside.unlink)
        for entry in (str(outside), "../%s" % outside.name):
            self.assertIn("is not a repository-relative path",
                          self.check(self.mutated(controls=[entry])))
            self.assertIn("is not a repository-relative path",
                          self.check(self.mutated(tests=["%s::test_alpha" % entry])))

    def test_a_test_name_that_is_only_text_does_not_count_as_defined(self):
        quote = '"' * 3
        (self.root / "controls" / "test_thing.py").write_text("\n".join([
            "NOTE = " + quote,
            "def test_ghost(self):",
            "    pass",
            quote,
            "",
            "class T:",
            "    def test_alpha(self):",
            "        pass",
            ""]), encoding="utf-8")
        self.assertIn("names test_ghost, which controls/test_thing.py does not define",
                      self.check(self.mutated(tests=["controls/test_thing.py::test_ghost"])))
        self.assertEqual(self.check(expected=0), "")

    def test_a_test_file_that_does_not_parse_is_refused(self):
        (self.root / "controls" / "broken.py").write_text("def test_alpha(\n", encoding="utf-8")
        self.assertIn("which does not parse",
                      self.check(self.mutated(tests=["controls/broken.py::test_alpha"])))

    def test_every_gap_is_carried_exactly_once(self):
        document = copy.deepcopy(self.document)
        document["requirements"] = document["requirements"][:-1]
        self.assertIn("gap-10 appears 0 time(s)", self.check(document))
        document = copy.deepcopy(self.document)
        document["requirements"].append(row("gap-3", probes=[]))
        output = self.check(document)
        self.assertIn("gap-3 appears 2 time(s)", output)
        self.assertIn("requirement id gap-3 is used more than once", output)

    def test_the_probe_lists_must_agree_in_both_directions(self):
        self.assertIn("claims probe P99, which the catalogue does not define",
                      self.check(self.mutated(probes=["P99"])))
        self.assertIn("probe P02 is defined in the catalogue and claimed by no requirement",
                      self.check(self.mutated(index=1, probes=[])))

    def test_a_row_absent_from_the_specification_is_caught(self):
        (self.bundle / "spec.md").write_text("### gap-1\n", encoding="utf-8")
        self.assertIn("requirement gap-2 is not discussed in the specification", self.check())

    def test_requirement_ids_are_matched_as_complete_identifiers(self):
        path = self.bundle / "spec.md"
        missing = path.read_text(encoding="utf-8").replace("### gap-1\n", "")
        for decoy in ("gap-10", "gap-1-extra", "prefix-gap-1", "gap-1_suffix"):
            with self.subTest(decoy=decoy):
                path.write_text(missing + decoy + "\n", encoding="utf-8")
                self.assertIn("requirement gap-1 is not discussed in the specification",
                              self.check())

    def test_unknown_and_missing_keys_are_refused_at_both_levels(self):
        document = copy.deepcopy(self.document)
        document["dispatch_authorized"] = False
        self.assertIn("document has unknown key dispatch_authorized", self.check(document))
        self.assertIn("requirement gap-1 has unknown key verdict",
                      self.check(self.mutated(verdict="pass")))
        document = copy.deepcopy(self.document)
        del document["requirements"][0]["evidence_required"]
        self.assertIn("is missing evidence_required", self.check(document))

    def test_the_document_must_describe_a_proposed_specification(self):
        document = copy.deepcopy(self.document)
        document["document_status"] = "frozen"
        self.assertIn("this record describes a proposed specification", self.check(document))

    def test_the_named_documents_must_sit_beside_the_record(self):
        document = copy.deepcopy(self.document)
        document["specification"] = "../elsewhere.md"
        self.assertIn("specification must name a file beside this record", self.check(document))
        document = copy.deepcopy(self.document)
        document["probe_catalogue"] = "absent.md"
        self.assertIn("probe_catalogue must name a file beside this record", self.check(document))

    def test_an_unreadable_or_malformed_record_exits_two(self):
        path = self.bundle / "readiness.json"
        path.write_text("{not json", encoding="utf-8")
        self.assertEqual(run("--spec", path, "--repo-root", self.root).returncode, 2)
        self.assertEqual(run("--spec", self.bundle / "absent.json",
                             "--repo-root", self.root).returncode, 2)


if __name__ == "__main__":
    sys.exit(0 if unittest.main(exit=False, verbosity=2).result.wasSuccessful() else 1)
