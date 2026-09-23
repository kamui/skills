#!/usr/bin/env python3
"""Drive savings_archive.py through its command line against the committed and synthetic archives.

Usage: python3 docs/research/tools/test_savings_archive.py [-v]

The committed archive must verify, rebuild, materialize and check from a copy outside this
checkout, under a network namespace without interfaces when ``unshare -rn`` is available. Altered,
missing and unlisted archive files, tampered realizations and a changed helper must be refused.
A synthetic archive exercises the template declaration rules and carried-task relocation. The
baseline helper replay needs the baseline commit in this checkout and is skipped without it.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "savings_archive.py"
ARCHIVE = HERE.parent / "review-code-artifact-savings-2026-09-22" / "archive"
BASELINE = "d8c2dd93bbfff6ac85907159e7763508265f5442"
sys.path.insert(0, str(HERE))
import savings_archive as sa  # noqa: E402


def isolated() -> list[str]:
    """``unshare -rn`` when this host allows it: no network interface is up inside."""
    try:
        if subprocess.run(["unshare", "-rn", "true"], capture_output=True).returncode == 0:
            return ["unshare", "-rn"]
    except OSError:
        pass
    return []


def run(*args: str, cwd: Path = None, tool: Path = TOOL, prefix: list[str] = ()) -> subprocess.CompletedProcess:
    env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(Path(cwd or tempfile.gettempdir()).resolve()))
    return subprocess.run([*prefix, sys.executable, str(tool), *args], cwd=cwd, env=env,
                          capture_output=True, text=True, encoding="utf-8")


def fake_skill(root: Path) -> Path:
    skill = root / "skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# fake\n", encoding="utf-8")
    return skill


class Scratch(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="savings-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp)

    def copy_archive(self) -> Path:
        target = self.tmp / "archive"
        shutil.copytree(ARCHIVE, target)
        return target


class CommittedArchive(Scratch):
    def test_verifies(self):
        result = run("verify", str(ARCHIVE))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("archive verified", result.stdout)

    def test_fixture_rebuild_matches_the_manifest(self):
        result = run("fixture", str(ARCHIVE), "--out", str(self.tmp / "repo"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads((ARCHIVE / "manifest.json").read_text(encoding="utf-8"))
        rebuilt = dict(line.split() for line in result.stdout.splitlines())
        self.assertEqual(rebuilt, manifest["revisions"])

    def test_alterations_are_refused(self):
        archive = self.copy_archive()
        record = archive / "tasks/continuation/review/record.json"
        record.write_text(record.read_text(encoding="utf-8").replace('"P1"', '"P2"', 1), encoding="utf-8")
        (archive / "tasks/implementation-gate/inputs/spec.md").unlink()
        (archive / "tasks/publishable/stray.txt").write_text("x\n", encoding="utf-8")
        result = run("verify", str(archive))
        self.assertEqual(result.returncode, 1)
        self.assertIn("tasks/continuation/review/record.json: altered", result.stdout)
        self.assertIn("tasks/implementation-gate/inputs/spec.md: missing", result.stdout)
        self.assertIn("tasks/publishable/stray.txt: unlisted file", result.stdout)
        skill = fake_skill(self.tmp)
        refused = run("materialize", str(archive), "--root", str(self.tmp / "root"), "--skill-root", str(skill))
        self.assertEqual(refused.returncode, 1)
        self.assertFalse((self.tmp / "root").exists())

    def test_offline_copy_materializes_and_checks(self):
        work = self.tmp / "clean"
        work.mkdir()
        archive = work / "archive"
        shutil.copytree(ARCHIVE, archive)
        tool = work / "savings_archive.py"
        shutil.copy2(TOOL, tool)
        skill = fake_skill(work)
        root = work / "root"
        prefix = isolated()
        made = run("materialize", str(archive), "--root", str(root), "--skill-root", str(skill),
                   cwd=work, tool=tool, prefix=prefix)
        self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
        checked = run("check", str(archive), "--root", str(root), cwd=work, tool=tool, prefix=prefix)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        chain = root / "continuation/review/initial"
        digest = lambda path: sa.digest(path.read_bytes())
        manifest = json.loads((chain / "manifest.json").read_text(encoding="utf-8"))
        accounting = json.loads((chain / "accounting.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["input_sha256"], digest(chain / "input.json"))
        self.assertEqual(manifest["brief_sha256"], digest(chain / "brief.md"))
        self.assertEqual(json.loads((chain / "raw-return.json").read_text())["manifest_sha256"], digest(chain / "manifest.json"))
        self.assertEqual(accounting["raw_return"], str(chain / "raw-return.json"))
        self.assertEqual(accounting["raw_return_sha256"], digest(chain / "raw-return.json"))
        record = json.loads((root / "continuation/review/record.json").read_text(encoding="utf-8"))
        self.assertEqual(record["record"]["paths"]["skill_root"], str(skill))
        self.assertEqual(record["record"]["verification"]["batches"][0]["accounting"], str(chain / "accounting.json"))
        for path in root.rglob("*"):
            if path.is_file() and ".git" not in path.parts and path.name != "realization.json":
                self.assertNotIn("@TASK_ROOT@", path.read_text(encoding="utf-8", errors="replace"), path)
                self.assertNotIn("@SHA256:", path.read_text(encoding="utf-8", errors="replace"), path)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root / "continuation/repo", capture_output=True, text=True)
        self.assertEqual(head.stdout.strip(), json.loads((archive / "manifest.json").read_text())["revisions"]["D3"])

    def test_relocation_changes_only_declared_fields(self):
        skill = fake_skill(self.tmp)
        roots = [self.tmp / "one", self.tmp / "two" / "deeper"]
        for root in roots:
            result = run("materialize", str(ARCHIVE), "--root", str(root), "--skill-root", str(skill), "--task", "continuation")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        task = json.loads((ARCHIVE / "tasks/continuation/task.json").read_text(encoding="utf-8"))
        for rel, spec in task["files"].items():
            left, right = (roots[0] / "continuation" / rel).read_bytes(), (roots[1] / "continuation" / rel).read_bytes()
            if spec["kind"] == "copy":
                self.assertEqual(left, right, rel)
            if spec["kind"] != "json":
                continue
            declared = spec.get("paths", []) + spec.get("carried", []) + spec.get("hashes", [])
            a, b = list(sa.walk(json.loads(left))), list(sa.walk(json.loads(right)))
            self.assertEqual([p for p, _ in a], [p for p, _ in b], rel)
            changed = [p for (p, x), (_, y) in zip(a, b) if x != y]
            self.assertTrue(changed, rel)
            for pointer in changed:
                self.assertTrue(any(sa.matches(pattern, pointer) for pattern in declared), f"{rel}{pointer}")

    def test_check_refuses_tampered_realizations(self):
        skill = fake_skill(self.tmp)
        root = self.tmp / "root"
        self.assertEqual(run("materialize", str(ARCHIVE), "--root", str(root), "--skill-root", str(skill)).returncode, 0)
        record = root / "continuation/review/record.json"
        record.write_text(record.read_text(encoding="utf-8").replace('"P1"', '"P2"', 1), encoding="utf-8")
        (root / "publishable/repo/ledger/export.py").write_text("changed\n", encoding="utf-8")
        (root / "implementation-gate/inputs/evidence.md").unlink()
        result = run("check", str(ARCHIVE), "--root", str(root))
        self.assertEqual(result.returncode, 1)
        self.assertIn("continuation/review/record.json: differs from its canonical realization", result.stdout)
        self.assertIn("undeclared value changed", result.stdout)
        self.assertIn("publishable/repo: working tree is not clean", result.stdout)
        self.assertIn("implementation-gate/inputs/evidence.md: missing", result.stdout)

    def test_refuses_unsafe_and_existing_roots(self):
        skill = fake_skill(self.tmp)
        for root in (self.tmp / "has space", self.tmp / "quote\"d"):
            result = run("materialize", str(ARCHIVE), "--root", str(root), "--skill-root", str(skill))
            self.assertEqual(result.returncode, 2, result.stderr)
        (self.tmp / "exists").mkdir()
        result = run("materialize", str(ARCHIVE), "--root", str(self.tmp / "exists"), "--skill-root", str(skill))
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to overwrite", result.stderr)


def baseline_skill(target: Path) -> Path:
    repo = HERE.parents[2]
    archive = subprocess.run(["git", "archive", BASELINE, "skills/review-code"], cwd=repo, capture_output=True)
    if archive.returncode != 0:
        raise unittest.SkipTest(f"baseline commit {BASELINE} is not in this checkout")
    target.mkdir(parents=True)
    subprocess.run(["tar", "-x", "-C", str(target)], input=archive.stdout, check=True)
    return target / "skills/review-code"


class BaselineReplay(Scratch):
    def test_seeded_chain_replays_under_the_baseline_helpers(self):
        skill = baseline_skill(self.tmp / "baseline")
        root = self.tmp / "root"
        made = run("materialize", str(ARCHIVE), "--root", str(root), "--skill-root", str(skill), "--task", "continuation")
        self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
        result = run("check", str(ARCHIVE), "--root", str(root), "--skill-root", str(skill))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        compose = skill / "scripts/compose_review.py"
        compose.write_text(compose.read_text(encoding="utf-8").replace(
            'if __name__ == "__main__":', 'if __name__ == "__main__":\n    print(" ", end="")', 1), encoding="utf-8")
        changed = run("check", str(ARCHIVE), "--root", str(root), "--skill-root", str(skill))
        self.assertEqual(changed.returncode, 1)
        self.assertIn("compose_review: output differs from realized review/record.json", changed.stdout)


class Declarations(Scratch):
    """A one-commit synthetic archive whose continuation-like task carries a replacement record."""

    def build(self, record: dict, spec: dict, extra: dict = None) -> Path:
        archive = self.tmp / "synthetic"
        (archive / "fixture/files/M0").mkdir(parents=True)
        (archive / "fixture/files/M0/README.md").write_text("fixture\n", encoding="utf-8")
        (archive / "fixture/fixture.json").write_text(json.dumps({
            "format": "savings-fixture/1", "identity": {"name": "T", "email": "t@example.invalid"},
            "commits": [{"label": "M0", "parent": None, "date": "2026-09-01T00:00:00+00:00",
                         "message": "one\n", "files": ["README.md"]}],
            "refs": {"main": "M0"}}), encoding="utf-8")
        task = archive / "tasks/t"
        (task / "review").mkdir(parents=True, exist_ok=True)
        (task / "review/record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        files = {"review/record.json": spec, **(extra or {})}
        (archive / "manifest.json").write_text(json.dumps({
            "format": "savings-archive/1", "baseline": {"commit": "0" * 40}, "tasks": ["t"],
            "bundle": {"path": "ledger.bundle"}}), encoding="utf-8")
        sealed = run("seal", str(archive))
        self.assertEqual(sealed.returncode, 0, sealed.stdout + sealed.stderr)
        revisions = json.loads((archive / "manifest.json").read_text())["revisions"]
        (task / "task.json").write_text(json.dumps({
            "format": "savings-task/1", "name": "t", "repository": {"refs": {"main": revisions["M0"]}, "checkout": "main"},
            "files": files}), encoding="utf-8")
        sealed = run("seal", str(archive))
        self.assertEqual(sealed.returncode, 0, sealed.stdout + sealed.stderr)
        return archive

    RECORD = {"record": {"repository": "@TASK_ROOT@/repo",
                         "verification": {"tasks": [{"id": "a", "batch": "carried:@TASK_ROOT@/review/old.json#initial"},
                                                    {"id": "b", "batch": "follow-up"}],
                                          "allowance": {"carried_from": "@TASK_ROOT@/review/old.json"}},
                         "judgment": "@TASK_ROOT@ stays prose"}}
    SPEC = {"kind": "json", "paths": ["/record/repository", "/record/verification/allowance/carried_from"],
            "carried": ["/record/verification/tasks/*/batch"]}

    def test_undeclared_token_is_refused(self):
        archive = self.build(self.RECORD, self.SPEC)
        result = run("verify", str(archive))
        self.assertEqual(result.returncode, 1)
        self.assertIn("/record/judgment: token outside exactly one declared field group", result.stdout)

    def test_carried_references_relocate(self):
        record = json.loads(json.dumps(self.RECORD))
        record["record"]["judgment"] = "prose"
        archive = self.build(record, self.SPEC)
        self.assertEqual(run("verify", str(archive)).returncode, 0)
        skill = fake_skill(self.tmp)
        root = self.tmp / "root"
        made = run("materialize", str(archive), "--root", str(root), "--skill-root", str(skill))
        self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
        realized = json.loads((root / "t/review/record.json").read_text(encoding="utf-8"))["record"]
        self.assertEqual(realized["verification"]["tasks"][0]["batch"], f"carried:{root}/t/review/old.json#initial")
        self.assertEqual(realized["verification"]["tasks"][1]["batch"], "follow-up")
        self.assertEqual(realized["verification"]["allowance"]["carried_from"], f"{root}/t/review/old.json")
        self.assertEqual(run("check", str(archive), "--root", str(root)).returncode, 0)

    def test_misclassified_carried_field_is_refused(self):
        record = {"record": {"repository": "@TASK_ROOT@/repo", "carried": "@TASK_ROOT@/review/old.json#initial"}}
        spec = {"kind": "json", "paths": ["/record/repository"], "carried": ["/record/carried"]}
        result = run("verify", str(self.build(record, spec)))
        self.assertEqual(result.returncode, 1)
        self.assertIn("a carried field is carried:@TASK_ROOT@/<file>#<batch>", result.stdout)

    def test_stale_declaration_is_refused(self):
        spec = {"kind": "json", "paths": ["/record/repository", "/record/missing"]}
        result = run("verify", str(self.build({"record": {"repository": "@TASK_ROOT@/repo"}}, spec)))
        self.assertEqual(result.returncode, 1)
        self.assertIn("declared field /record/missing matches no token-bearing value", result.stdout)

    def test_brief_tokens_outside_its_records_are_refused(self):
        record = {"run": {"repository": "@TASK_ROOT@/repo"}}
        extra = {"review/brief.md": {"kind": "brief", "input": "review/record.json"}}
        brief = "# Brief @TASK_ROOT@\n\n" + sa.json_text(record)
        (self.tmp / "synthetic/tasks/t/review").mkdir(parents=True)
        (self.tmp / "synthetic/tasks/t/review/brief.md").write_text(brief, encoding="utf-8")
        result = run("verify", str(self.build(record, {"kind": "json", "paths": ["/run/repository"]}, extra)))
        self.assertEqual(result.returncode, 1)
        self.assertIn("token outside the brief's supplied-records JSON", result.stdout)


if __name__ == "__main__":
    unittest.main()
