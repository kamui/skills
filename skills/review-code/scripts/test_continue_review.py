#!/usr/bin/env python3
"""Exercise continue_review.py through its CLI: chain loading, validation, composition, reports and legacy routing.

Usage: python3 scripts/test_continue_review.py
Inputs: implementation-gate records composed by compose_review.py from the composer's fixture composition,
synthetic continuation stores (and one built by review_context.py in a scratch repository), and verifier
accounting reports in the shape account_verifier_return.py writes; no forge access.
Exit 0: all checks pass; 1: a check fails; 2: a subprocess cannot run.

Every successful compose must leave the record, its report and earlier addenda byte for byte unchanged and
write `addendum-<final head>.json` plus its distinct `.report.md`. Every refusal must leave no new consumable
addendum, and an invalid, interrupted or legacy chain must never read as a valid state.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import compose_review as cr
import review_context as rc
import test_compose_review as fixtures

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
HELPER = SCRIPTS / "continue_review.py"
HEAD, MERGE_BASE = fixtures.HEAD, fixtures.MERGE_BASE
F1, F2, F3 = "c3d4e5f60718293a4b5c6d7e8f90123456789abc", "2" * 40, "3" * 40
FINDING, QUESTION = "payments/retry-idempotency", "queue/retry-order"
MANIFEST = ["src/payments.ts", "src/retry-policy.ts", "src/queue.ts", "docs/notes.md"]

# Runs the helper with one injected fault while it links the addendum's report: `kill` exits without cleanup,
# `fail` raises an OSError.
INJECT = r"""
import os, sys
sys.path.insert(0, sys.argv[1])
import continue_review
fault, sys.argv = sys.argv[2], ["continue_review.py", *sys.argv[3:]]
real_link = os.link
def link(src, dst, *args, **kwargs):
    if str(dst).endswith(".report.md"):
        if fault == "kill":
            os._exit(137)
        raise OSError(28, "injected link failure", str(dst))
    return real_link(src, dst, *args, **kwargs)
os.link = link
sys.exit(continue_review.main())
"""


def run(*args, cwd=SKILL):
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True, encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Chain(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.count = 0

    def tearDown(self):
        self.temp.cleanup()

    # --- fixtures -------------------------------------------------------------

    def fresh(self, name):
        self.count += 1
        path = self.root / f"{name}-{self.count}"
        path.mkdir()
        return path

    def batch(self, where: Path, name: str, phase: str, tasks: list) -> dict:
        """A bundle manifest and an accounting report that establishes each task's ruling."""
        bundle = where / name
        bundle.mkdir(parents=True, exist_ok=True)
        manifest = json.dumps({"format": "verifier-manifest/2", "batch": {"id": name, "phase": phase}}).encode("utf-8")
        (bundle / "manifest.json").write_bytes(manifest)
        accounting = bundle / "accounting.json"
        fixtures.write_accounting(str(accounting), tasks)
        report = json.loads(accounting.read_text(encoding="utf-8"))
        report.update(raw_return=str(bundle / "raw-return.json"), manifest_sha256=hashlib.sha256(manifest).hexdigest())
        accounting.write_text(json.dumps(report), encoding="utf-8")
        return {"name": name, "phase": phase, "bundle": str(bundle), "raw_return": str(bundle / "raw-return.json"),
                "accounting": str(accounting), "operation": "Agent run_in_background=false"}

    def record(self, *, legacy=False, mutate=None, head=HEAD, name="review") -> Path:
        """A record composed by compose_review.py; new-protocol unless ``legacy``, with its report written."""
        private = self.fresh(name)
        composition = fixtures.gate_composition()
        composition["run"]["head"] = head
        composition["record"]["repository"] = str(self.root / "repo")
        composition["record"]["paths"] = {"private_dir": str(private), "store": str(private / "store.json"),
                                          "composition": str(private / "composition.json"),
                                          "addenda": str(private / "addenda"), "skill_root": str(SKILL)}
        composition["record"]["check_evidence"] = [
            {"check": "python3 scripts/test_retry.py", "head": head, "outcome": "reviewer-executed", "reason": "the suite covers retries"}]
        tasks = [fixtures.candidate_task()]
        composition["record"]["verification"] = {"tasks": tasks, "batches": [self.batch(private, "initial", "initial", tasks)],
                                                 "allowance": {"initial_spent": True, "follow_up_spent": False, "carried_from": None},
                                                 "outstanding": []}
        if mutate:
            mutate(composition, private)
        result = subprocess.run([sys.executable, str(SCRIPTS / "compose_review.py"), "--profile", "implementation-gate", "-"],
                                input=json.dumps(composition), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record = json.loads(result.stdout)
        if not legacy:
            (private / "report.md").write_text("# Review report\n", encoding="utf-8")
            record["finalization"] = {"protocol": cr.FINALIZATION_PROTOCOL, "profile": "implementation-gate",
                                      "report": str(private / "report.md"), "inputs": {}, "replies": []}
        (private / "addenda").mkdir()
        (private / "composition.json").write_text(json.dumps(composition), encoding="utf-8")
        path = private / "record.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return path

    def store(self, prior: str, final: str, delta=("src/retry-policy.ts",), reachable=True) -> Path:
        path = self.fresh("store") / "store.json"
        entry = lambda p: {"path": p, "status": "M"}  # noqa: E731
        context = {"head": final, "merge_base": MERGE_BASE, "manifest": [entry(p) for p in MANIFEST],
                   "delta": {"prior_head": prior, "conditions": {"ancestor": "yes", "merge-base-unchanged": "yes",
                                                                 "prior-head-reachable": "yes" if reachable else "no"},
                             "manifest": [entry(p) for p in delta]}}
        path.write_text(json.dumps({"format": rc.STORE_FORMAT, "context": context}), encoding="utf-8")
        return path

    def continuation(self, **overrides) -> dict:
        value = {"delta": [{"path": "src/retry-policy.ts", "state": "reviewed"}],
                 "fixed_findings": [{"id": FINDING, "classification": "fixed", "evidence": "src/retry-policy.ts:18 reuses the key"}],
                 "findings": [], "questions": [], "requirements": [], "check_evidence": [],
                 "verification": {"tasks": [], "batches": []},
                 "status": "Needs Information", "coverage": "complete", "coverage_gaps": []}
        value.update(overrides)
        return value

    def compose(self, record: Path, store: Path, value: dict, inject: str | None = None):
        path = self.fresh("input") / "continuation.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        args = ["compose", "--record", record, "--store", store, path]
        if inject:
            return run("-c", INJECT, SCRIPTS, inject, *args)
        return run(HELPER, *args)

    def state(self, record: Path, *flags):
        return run(HELPER, "state", *flags, record)

    def snapshot(self, record: Path) -> dict:
        directory = record.parent
        files = [record, *sorted(p for p in (directory / "addenda").glob("*") if p.suffix != ".part")]
        if (directory / "report.md").exists():
            files.append(directory / "report.md")
        return {str(p): digest(p) for p in files}

    def composed(self, record: Path, store: Path, value: dict) -> dict:
        """Compose; assert the earlier artifacts are unchanged and the addendum and its distinct report exist."""
        final = json.loads(Path(store).read_text(encoding="utf-8"))["context"]["head"]
        before = {path: value_hash for path, value_hash in self.snapshot(record).items()
                  if not path.endswith(f"addendum-{final}.json")}  # only an interrupted write of this final head is replaced
        result = self.compose(record, store, value)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        lines = dict(line.split(" ", 1) for line in result.stdout.splitlines())
        addendum, report = Path(lines["addendum"]), Path(lines["report"])
        self.assertEqual((addendum.name, report.name), (f"addendum-{final}.json", f"addendum-{final}.report.md"))
        self.assertNotEqual(report, record.parent / "report.md")
        after = self.snapshot(record)
        for path, value_hash in before.items():
            self.assertEqual(after[path], value_hash, f"{path} changed")
        saved = json.loads(addendum.read_text(encoding="utf-8"))
        self.assertEqual(saved["finalization"]["report"], str(report))
        self.assertEqual(sorted(p.name for p in addendum.parent.glob("*.part")), [])
        checked = self.state(record)
        self.assertEqual((checked.returncode, checked.stdout), (0, result.stdout))
        return saved

    def invalid(self, result, needle: str):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(result.stdout.startswith("chain-invalid\n"), result.stdout)
        self.assertIn(needle, result.stdout)

    def refused(self, result, rule: str, needle: str | None = None):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f": {rule}: ", result.stdout)
        if needle:
            self.assertIn(needle, result.stdout)

    def no_new_addendum(self, record: Path, final: str):
        addenda = record.parent / "addenda"
        self.assertFalse((addenda / f"addendum-{final}.json").exists())
        self.assertFalse((addenda / f"addendum-{final}.report.md").exists())

    # --- valid chains -----------------------------------------------------------

    def test_valid_chain_derives_mechanical_fields_and_renders_the_current_result(self):
        record = self.record()
        state = self.state(record)
        self.assertEqual(state.returncode, 0, state.stdout)
        self.assertEqual(state.stdout.splitlines()[:4], ["status Changes Requested", "coverage complete", f"head {HEAD}", f"record {record}"])
        self.assertIn(f"report {record.parent / 'report.md'}", state.stdout)
        self.assertTrue(state.stdout.endswith(f"continuation {HELPER}\n"))
        saved = self.composed(record, self.store(HEAD, F1), self.continuation())
        self.assertEqual(list(saved)[:8], ["format", "workflow", "record", "record_format", "reviewed_head", "final_head", "delta",
                                           "replaced_by_full_review"])
        self.assertEqual((saved["format"], saved["record"], saved["record_format"], saved["reviewed_head"], saved["final_head"]),
                         ("implementation-gate-addendum/2", str(record), "implementation-gate-record/2", HEAD, F1))
        self.assertEqual(saved["verification"]["allowance"], {"initial_spent": True, "follow_up_spent": False, "carried_from": None})
        self.assertEqual((saved["verification"]["outstanding"], saved["routed"], saved["replaced_by_full_review"]),
                         ([], {"unresolved": [], "disputed": [], "unrecoverable_inputs": []}, None))
        current = json.loads(self.state(record, "--json").stdout)
        self.assertEqual([item["id"] for item in current["open"]], [QUESTION], "the open question survives the fix")
        report = Path(saved["finalization"]["report"]).read_text(encoding="utf-8")
        question = json.loads(record.read_text(encoding="utf-8"))["items"][1]
        self.assertEqual(report.count(question["markdown"]), 1)
        for section in ("## Open items", "## Reported fixes", "## Delta coverage", "## Requirements", "## File coverage",
                        "## Check evidence", "## Verification", "## Routed", "## Artifacts"):
            self.assertIn(section, report)

    def test_multi_step_fixes_and_new_items(self):
        record = self.record()
        still = self.continuation(fixed_findings=[{"id": FINDING, "classification": "still-open", "evidence": "a frozen target still posts"}],
                                  status="Changes Requested")
        self.composed(record, self.store(HEAD, F1), still)
        # A new consider finding and a new question on the second step; the first finding is fixed at last.
        consider = fixtures.consider(id="docs/notes-scope", anchor={"type": "file", "path": "docs/notes.md"})
        question = dict(fixtures.base_composition()["questions"][0], id="queue/retry-cap", title="Must retries stop after three attempts?")
        second = self.continuation(findings=[consider], questions=[question])
        saved = self.composed(record, self.store(F1, F2), second)
        self.assertEqual(saved["findings"][0]["anchor"]["side"], "RIGHT", "the store's manifest establishes a file anchor's side")
        current = json.loads(self.state(record, "--json").stdout)
        self.assertEqual(sorted(item["id"] for item in current["open"]), ["docs/notes-scope", "queue/retry-cap", QUESTION])
        self.assertEqual([entry["head"] for entry in current["chain"]], [HEAD, F1, F2])
        # A fixed id must be open, and a new id must not already be.
        again = self.continuation(fixed_findings=[{"id": FINDING, "classification": "fixed", "evidence": "x"}])
        self.refused(self.compose(record, self.store(F2, F3), again), "fixed-findings", "not an open item")
        duplicate = self.continuation(fixed_findings=[], questions=[dict(question, title="Again?")])
        self.refused(self.compose(record, self.store(F2, F3), duplicate), "stable-id", "already open")
        self.no_new_addendum(record, F3)

    def test_delta_needs_a_decision_for_every_file(self):
        record = self.record()
        store = self.store(HEAD, F1, delta=("src/retry-policy.ts", "src/queue.ts"))
        self.refused(self.compose(record, store, self.continuation()), "file-accounting", "`src/queue.ts` is in the delta manifest")
        extra = self.continuation(delta=[{"path": "src/retry-policy.ts", "state": "reviewed"}, {"path": "src/queue.ts", "state": "reviewed"},
                                         {"path": "docs/notes.md", "state": "reviewed"}])
        self.refused(self.compose(record, store, extra), "file-accounting", "not in the delta manifest")
        unknown = self.continuation(delta=[{"path": "src/queue.ts", "state": "reviewed"}, {"path": "src/retry-policy.ts", "state": "reviewed"}],
                                    summary="not a key")
        self.refused(self.compose(record, store, unknown), "schema", "unknown keys ['summary']")
        missing = self.continuation(delta=[{"path": "src/queue.ts", "state": "reviewed"}, {"path": "src/retry-policy.ts", "state": "reviewed"}])
        del missing["status"]
        self.refused(self.compose(record, store, missing), "schema", "`status` is a continuation decision")
        # Rows are saved in the manifest's order, whatever order they were written in.
        del missing["coverage_gaps"]
        missing.update(status="Needs Information", coverage_gaps=[])
        saved = self.composed(record, store, missing)
        self.assertEqual([row["path"] for row in saved["delta"]], ["src/retry-policy.ts", "src/queue.ts"])

    def test_store_must_carry_the_chain_delta(self):
        record = self.record()
        self.refused(self.compose(record, self.store(F2, F1), self.continuation()), "chain", "not the chain's current head")
        self.refused(self.compose(record, self.store(HEAD, F1, reachable=False), self.continuation()), "schema", "could not reach")
        self.refused(self.compose(record, self.store(HEAD, F1), self.continuation(final_head=F2)), "derived-field", "conflicts")
        self.refused(self.compose(record, self.store(HEAD, HEAD), self.continuation()), "chain", "already reviewed")
        self.no_new_addendum(record, F1)

    def test_untouched_unreviewed_file_keeps_coverage_incomplete(self):
        def unreviewed(composition, _private):
            composition["record"]["files"][3] = {"path": "docs/notes.md", "state": "unreviewed"}
            composition["run"]["coverage"] = "incomplete"
            composition["summary"]["coverage_gaps"] = ["docs/notes.md: generated file not read"]
        record = self.record(mutate=unreviewed)
        self.refused(self.compose(record, self.store(HEAD, F1), self.continuation()), "coverage-gaps", "`docs/notes.md` stays `unreviewed`")
        self.assertIn("docs/notes.md: generated file not read", json.loads(self.state(record, "--json").stdout)["coverage_gaps"])
        kept = self.continuation(status="Incomplete", coverage="incomplete", coverage_gaps=["docs/notes.md: still unread"])
        self.composed(record, self.store(HEAD, F1), kept)
        files = {row["path"]: row["state"] for row in json.loads(self.state(record, "--json").stdout)["files"]}
        self.assertEqual((files["docs/notes.md"], files["src/retry-policy.ts"]), ("unreviewed", "reviewed"))

    def test_historical_checks_keep_their_heads(self):
        record = self.record()
        historical = {"check": "python3 scripts/test_retry.py", "head": HEAD, "outcome": "historical", "reason": "the delta reaches none of its inputs"}
        executed = {"check": "python3 scripts/test_queue.py", "head": F1, "outcome": "reviewer-executed", "reason": "the fix touches it"}
        saved = self.composed(record, self.store(HEAD, F1), self.continuation(check_evidence=[historical, executed]))
        self.assertEqual(saved["check_evidence"], [historical, executed])
        relabelled = dict(historical, head=F2)
        self.refused(self.compose(record, self.store(F1, F2), self.continuation(fixed_findings=[], check_evidence=[relabelled])),
                     "check-evidence", "keeps its original head")
        stale = dict(executed, head=F1)
        self.refused(self.compose(record, self.store(F1, F2), self.continuation(fixed_findings=[], check_evidence=[stale])),
                     "check-evidence", "never relabelled")
        current = json.loads(self.state(record, "--json").stdout)
        self.assertEqual([(row["check"], row["head"]) for row in current["check_evidence"]],
                         [("python3 scripts/test_retry.py", HEAD), ("python3 scripts/test_retry.py", HEAD), ("python3 scripts/test_queue.py", F1)])

    def test_allowance_is_cumulative_and_exhausts(self):
        record = self.record()
        premise = fixtures.premise_task(identity="premise-2", batch="follow-up")
        where = self.fresh("continuation")
        batch = self.batch(where, "follow-up", "follow-up", [premise])
        written = {key: batch[key] for key in ("bundle", "accounting", "operation")}
        first = self.continuation(verification={"tasks": [premise], "batches": [written]})
        saved = self.composed(record, self.store(HEAD, F1), first)
        self.assertEqual(saved["verification"]["batches"][0], batch, "name, phase and raw_return come from the bundle and accounting")
        self.assertEqual(saved["verification"]["allowance"], {"initial_spent": True, "follow_up_spent": True, "carried_from": None})
        # A further batch has no allowance left, and an explicit reset of the spent flags is refused.
        again = self.batch(self.fresh("continuation"), "follow-up-2", "follow-up", [dict(premise, id="premise-3", batch="follow-up-2")])
        extra = self.continuation(fixed_findings=[], verification={"tasks": [dict(premise, id="premise-3", batch="follow-up-2")],
                                                                     "batches": [{k: again[k] for k in ("bundle", "accounting", "operation")}]})
        self.refused(self.compose(record, self.store(F1, F2), extra), "verification", "already spent its follow-up")
        reset = self.continuation(fixed_findings=[], verification={"tasks": [], "batches": [],
                                                                     "allowance": {"initial_spent": True, "follow_up_spent": False, "carried_from": None}})
        self.refused(self.compose(record, self.store(F1, F2), reset), "derived-field", "`allowance=")
        # A new must-fix finding cannot publish without a confirmed candidate task, and there is no batch left for one.
        blocker = fixtures.finding(id="queue/drop-on-full", title="Block when the queue is full",
                                   anchor={"type": "line", "path": "src/queue.ts", "start_line": 3, "end_line": 3, "side": "RIGHT"}, fix=None)
        unconfirmed = self.continuation(fixed_findings=[], findings=[blocker], status="Changes Requested")
        self.refused(self.compose(record, self.store(F1, F2), unconfirmed), "verification", "requires a candidate task")
        self.no_new_addendum(record, F2)

    def test_explicit_dropping_of_carried_state_fails(self):
        def routed(composition, _private):
            composition["record"]["routed"]["unresolved"] = [QUESTION]
            composition["record"]["verification"]["outstanding"] = ["premise-9: the host timed out"]
            composition["run"]["coverage"] = "incomplete"
            composition["summary"]["coverage_gaps"] = ["premise-9 did not finish"]
        record = self.record(mutate=routed)
        base = dict(status="Incomplete", coverage="incomplete", coverage_gaps=["premise-9 did not finish"])
        dropped = self.continuation(routed={"unresolved": [], "disputed": [], "unrecoverable_inputs": []}, **base)
        self.refused(self.compose(record, self.store(HEAD, F1), dropped), "carried-state", f"drops `{QUESTION}`")
        cleared = self.continuation(verification={"tasks": [], "batches": [], "outstanding": []}, **base)
        self.refused(self.compose(record, self.store(HEAD, F1), cleared), "carried-state", "drops `premise-9: the host timed out`")
        complete = self.continuation()
        self.refused(self.compose(record, self.store(HEAD, F1), complete), "coverage-gaps", "outstanding verification contradicts")
        self.no_new_addendum(record, F1)
        saved = self.composed(record, self.store(HEAD, F1), self.continuation(**base))
        self.assertEqual((saved["routed"]["unresolved"], saved["verification"]["outstanding"]), ([QUESTION], ["premise-9: the host timed out"]))

    def test_example_input_composes(self):
        record = self.record()
        example = json.loads(run(HELPER, "--example").stdout)
        tasks = example["verification"]["tasks"]
        batch = self.batch(self.fresh("continuation"), "follow-up", "follow-up", tasks)
        example["verification"]["batches"] = [{k: batch[k] for k in ("bundle", "accounting", "operation")}]
        saved = self.composed(record, self.store(HEAD, F1, delta=("src/retry-policy.ts", "docs/notes.md")), example)
        self.assertEqual(saved["status"], "Approved")

    def test_real_store_from_review_context(self):
        repo = self.fresh("repo")

        def git(*args):
            return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()

        git("init", "-q", "-b", "main")
        git("config", "user.email", "t@example.com")
        git("config", "user.name", "T")
        (repo / "a.txt").write_text("one\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-qm", "base")
        base = git("rev-parse", "HEAD")
        (repo / "a.txt").write_text("two\n", encoding="utf-8")
        git("commit", "-qam", "change")
        head = git("rev-parse", "HEAD")
        (repo / "b.txt").write_text("fix\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-qm", "fix")
        final = git("rev-parse", "HEAD")

        def pinned(composition, _private):
            composition["run"]["merge_base"] = base
            composition["findings"] = []
            composition["questions"] = []
            composition["summary"]["status"] = "Approved"
            composition["record"]["files"] = [{"path": "a.txt", "state": "reviewed"}]
            composition["record"]["verification"]["tasks"] = []
            composition["record"]["verification"]["batches"] = []
            composition["record"]["verification"]["allowance"]["initial_spent"] = False
        record = self.record(mutate=pinned, head=head)
        store = self.fresh("store") / "store.json"
        built = run(SCRIPTS / "review_context.py", "--merge-base", base, "--head", final, "--prior-head", head, "--base-ref", "main",
                    "--store", store, cwd=repo)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        value = self.continuation(delta=[{"path": "b.txt", "state": "reviewed"}], fixed_findings=[], status="Approved")
        saved = self.composed(record, store, value)
        self.assertEqual((saved["reviewed_head"], saved["final_head"]), (head, final))

    # --- replacements -------------------------------------------------------------

    def replacement(self, predecessor: Path, *, carried_from: str | None = None, batch: str | None = None,
                    drop_question=False) -> Path:
        def carry(composition, _private):
            composition["run"]["head"] = F1
            ref = batch or f"carried:{predecessor}#initial"
            composition["record"]["verification"] = {
                "tasks": [fixtures.candidate_task(batch=ref)], "batches": [],
                "allowance": {"initial_spent": True, "follow_up_spent": False, "carried_from": carried_from or str(predecessor)},
                "outstanding": []}
            if drop_question:
                composition["questions"] = []
                composition["record"]["routed"]["unresolved"] = []
        return self.record(mutate=carry, head=F1, name="replacement")

    def test_source_confirmed_replacement_continues_the_chain(self):
        record = self.record()
        replacement = self.replacement(record)
        value = self.continuation(fixed_findings=[], status="Changes Requested", replaced_by_full_review=str(replacement),
                                  delta=[{"path": "src/retry-policy.ts", "state": "reviewed"}])
        before = self.snapshot(replacement)
        result = self.compose(record, self.store(HEAD, F1), value)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        named = record.parent / "addenda" / f"addendum-{F1}.json"
        self.assertIn(f"record {replacement}\naddendum {named}\nreport {named.with_name(f'addendum-{F1}.report.md')}\n", result.stdout)
        self.assertEqual(self.snapshot(replacement), before)
        current = json.loads(self.state(record, "--json").stdout)
        self.assertEqual((current["record"], current["head"]), (str(replacement), F1))
        self.assertEqual(current["confirmations"][FINDING]["batch"], f"carried:{record}#initial", "the original accounting provenance")
        # The next continuation writes into the replacement's addenda and still carries the original provenance.
        saved = self.composed(record, self.store(F1, F2), self.continuation())
        self.assertEqual(saved["record"], str(replacement))
        self.assertTrue((replacement.parent / "addenda" / f"addendum-{F2}.json").exists())
        from_replacement = self.state(replacement)
        self.assertEqual(from_replacement.returncode, 0, from_replacement.stdout)

    def test_replacement_settles_coverage_the_chain_left_open(self):
        def unreviewed(composition, _private):
            composition["record"]["files"][3] = {"path": "docs/notes.md", "state": "unreviewed"}
            composition["run"]["coverage"] = "incomplete"
            composition["summary"]["coverage_gaps"] = ["docs/notes.md: generated file not read"]
        record = self.record(mutate=unreviewed)
        replacement = self.replacement(record)  # a full review that accounts for every file, coverage complete
        value = self.continuation(fixed_findings=[], status="Changes Requested", replaced_by_full_review=str(replacement))
        self.composed(record, self.store(HEAD, F1), value)
        current = json.loads(self.state(record, "--json").stdout)
        self.assertEqual((current["coverage"], {row["path"]: row["state"] for row in current["files"]}["docs/notes.md"]),
                         ("complete", "ignored"), "the replacement's own accounting settles the file")
        # Without a replacement, the untouched unreviewed file still keeps coverage incomplete.
        again = self.record(mutate=unreviewed)
        self.refused(self.compose(again, self.store(HEAD, F1), self.continuation(fixed_findings=[], status="Changes Requested")),
                     "coverage-gaps", "stays `unreviewed`")

    def full_review(self, predecessor: Path, findings: list, questions: list) -> Path:
        """A replacement whose own follow-up batch confirms each finding it raises."""
        def own(composition, private):
            composition["findings"], composition["questions"] = findings, questions
            if not findings:
                composition["summary"]["status"] = "Needs Information"
            tasks = [fixtures.candidate_task(identity=f["id"], batch="follow-up") for f in findings]
            composition["record"]["verification"] = {
                "tasks": tasks, "batches": [self.batch(private, "follow-up", "follow-up", tasks)] if tasks else [],
                "allowance": {"initial_spent": True, "follow_up_spent": bool(tasks), "carried_from": str(predecessor)},
                "outstanding": []}
        return self.record(mutate=own, head=F1, name="replacement")

    def test_replacement_records_its_own_confirmed_blocker(self):
        record = self.record()
        question = fixtures.base_composition()["questions"][0]
        blocker = fixtures.finding(id="queue/drop-on-full", title="Block when the queue is full",
                                   anchor={"type": "line", "path": "src/queue.ts", "start_line": 3, "end_line": 3, "side": "RIGHT"}, fix=None)
        # The addendum fixes the chain's blocker; the full review raises and confirms a new one, so its status governs.
        replacement = self.full_review(record, [blocker], [question])
        self.composed(record, self.store(HEAD, F1), self.continuation(status="Changes Requested", replaced_by_full_review=str(replacement)))
        current = json.loads(self.state(record, "--json").stdout)
        self.assertEqual((current["status"], sorted(item["id"] for item in current["open"])), ("Changes Requested", [blocker["id"], QUESTION]))
        self.assertEqual(current["confirmations"][blocker["id"]]["batch"], f"carried:{replacement}#follow-up")
        # The replacement's own items, not the chain's, must support the status the addendum carries.
        other = self.record()
        settled = self.full_review(other, [], [question])
        result = self.compose(other, self.store(HEAD, F1), self.continuation(status="Changes Requested", replaced_by_full_review=str(settled)))
        self.refused(result, "status-consistency", "needs an unsettled must-fix")

    def test_replacement_confirms_a_blocker_the_addendum_raised(self):
        def approved(composition, _private):
            composition["findings"], composition["questions"] = [], []
            composition["summary"]["status"] = "Approved"
            composition["record"]["verification"] = {"tasks": [], "batches": [], "outstanding": [],
                                                     "allowance": {"initial_spent": False, "follow_up_spent": False, "carried_from": None}}
        record = self.record(mutate=approved)
        blocker = fixtures.finding(id="queue/drop-on-full", title="Block when the queue is full",
                                   anchor={"type": "line", "path": "src/queue.ts", "start_line": 3, "end_line": 3, "side": "RIGHT"}, fix=None)
        task = fixtures.candidate_task(identity=blocker["id"], batch="initial")
        batch = self.batch(self.fresh("continuation"), "initial", "initial", [task])
        # The addendum's own confirmation has no chain file yet, so the replacement confirms the blocker in its own batch.
        replacement = self.full_review(record, [blocker], [])
        value = self.continuation(fixed_findings=[], findings=[blocker], status="Changes Requested", replaced_by_full_review=str(replacement),
                                  verification={"tasks": [task], "batches": [{k: batch[k] for k in ("bundle", "accounting", "operation")}]})
        self.composed(record, self.store(HEAD, F1), value)
        current = json.loads(self.state(record, "--json").stdout)
        self.assertEqual(current["confirmations"][blocker["id"]]["batch"], f"carried:{replacement}#follow-up")

    def test_replacement_that_drops_state_is_invalid(self):
        record = self.record()
        base = dict(fixed_findings=[], status="Changes Requested")
        other = self.record(name="other")
        reset = self.replacement(record)
        value = json.loads(reset.read_text(encoding="utf-8"))
        value["record"]["verification"]["allowance"]["initial_spent"] = False
        reset.write_text(json.dumps(value), encoding="utf-8")
        cases = {
            "resets `initial_spent`": reset,
            "drops open item `queue/retry-order`": self.replacement(record, drop_question=True),
            "original accounting provenance": self.replacement(record, batch=f"carried:{other}#initial"),
            "not the chain file it replaced": self.replacement(record, carried_from=str(other)),
        }
        for needle, replacement in cases.items():
            with self.subTest(needle):
                result = self.compose(record, self.store(HEAD, F1), self.continuation(replaced_by_full_review=str(replacement), **base))
                self.refused(result, "carried-state", needle)
                self.no_new_addendum(record, F1)
        missing = self.compose(record, self.store(HEAD, F1), self.continuation(replaced_by_full_review=str(self.root / "absent.json"), **base))
        self.refused(missing, "chain", "cannot be read")

    # --- invalid chains --------------------------------------------------------------

    def addendum(self, owner: Path, reviewed: str, final: str, **overrides) -> Path:
        """A hand-written version-2 addendum without finalization, as continuations wrote before this helper."""
        value = {"format": "implementation-gate-addendum/2", "workflow": "v5b-24", "record": str(owner),
                 "record_format": "implementation-gate-record/2", "reviewed_head": reviewed, "final_head": final,
                 "delta": [{"path": "src/retry-policy.ts", "state": "reviewed"}], "replaced_by_full_review": None,
                 "fixed_findings": [], "findings": [], "questions": [], "requirements": [], "check_evidence": [],
                 "verification": {"tasks": [], "batches": [], "allowance": {"initial_spent": True, "follow_up_spent": False, "carried_from": None},
                                  "outstanding": []},
                 "status": "Changes Requested", "coverage": "complete", "coverage_gaps": [],
                 "routed": {"unresolved": [], "disputed": [], "unrecoverable_inputs": []}}
        value.update(overrides)
        path = owner.parent / "addenda" / f"addendum-{final}.json"
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def test_old_chain_without_markers_stays_readable(self):
        record = self.record(legacy=True)
        # The base contract listed only the two spent flags, so an addendum written then may omit `carried_from`.
        tip = self.addendum(record, HEAD, F1, verification={"tasks": [], "batches": [], "outstanding": [],
                                                            "allowance": {"initial_spent": True, "follow_up_spent": False}})
        state = self.state(record)
        self.assertEqual(state.returncode, 0, state.stdout)
        self.assertIn(f"legacy {tip}\n", state.stdout)
        saved = self.composed(record, self.store(F1, F2), self.continuation())
        self.assertEqual(saved["reviewed_head"], F1)

    def test_malformed_missing_forked_cyclic_and_mismatched_chains(self):
        cases = {
            "cannot be read": lambda r: (r.parent / "addenda" / f"addendum-{F1}.json").write_text("{", encoding="utf-8"),
            "the chain forks": lambda r: (self.addendum(r, HEAD, F1), self.addendum(r, HEAD, F2)),
            "the chain has a cycle": lambda r: (self.addendum(r, HEAD, F1), self.addendum(r, F1, HEAD)),
            "not linked to the record's head chain": lambda r: self.addendum(r, F3, F1),
            "`record=": lambda r: self.addendum(r, HEAD, F1, record=str(self.root / "elsewhere.json")),
            "`record_format=": lambda r: self.addendum(r, HEAD, F1, record_format="implementation-gate-record/3"),
            "unknown format": lambda r: self.addendum(r, HEAD, F1, format="implementation-gate-addendum/3"),
            "missing `routed`": lambda r: self.addendum(r, HEAD, F1, **{"routed": None}) and _drop(r, F1, "routed"),
            "is not an open item": lambda r: self.addendum(r, HEAD, F1, fixed_findings=[{"id": "x/unknown", "classification": "fixed", "evidence": "e"}]),
            "resets": lambda r: self.addendum(r, HEAD, F1, verification={"tasks": [], "batches": [], "allowance": {
                "initial_spent": False, "follow_up_spent": False, "carried_from": None}, "outstanding": []}),
            "carries": lambda r: self.addendum(r, HEAD, F1, verification={"tasks": [], "batches": [], "allowance": {
                "initial_spent": True, "follow_up_spent": False, "carried_from": str(r)}, "outstanding": []}),
            "contradicts the unsettled must-fix": lambda r: self.addendum(r, HEAD, F1, status="Approved"),
            "does not account": lambda r: Path(json.loads(r.read_text(encoding="utf-8"))["record"]["verification"]["batches"][0]["accounting"])
            .write_text(json.dumps({"format": "verifier-accounting/2"}), encoding="utf-8"),
        }
        for needle, damage in cases.items():
            with self.subTest(needle):
                record = self.record()
                damage(record)
                self.invalid(self.state(record), "`allowance=" if needle in ("resets", "carries") else needle)
                result = self.compose(record, self.store(HEAD, F1), self.continuation())
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertTrue(result.stdout.startswith("chain-invalid\n"), result.stdout)
        self.assertEqual(run(HELPER, "state", self.root / "absent" / "record.json").returncode, 2)

    def test_unknown_protocols_and_missing_reports(self):
        record = self.record()
        doc = json.loads(record.read_text(encoding="utf-8"))
        record.write_text(json.dumps(dict(doc, finalization=dict(doc["finalization"], protocol="review-code-finalization/9"))), encoding="utf-8")
        self.invalid(self.state(record), "unknown finalization protocol")
        record = self.record()
        (record.parent / "report.md").unlink()
        self.invalid(self.state(record), "does not exist")
        record = self.record()
        self.addendum(record, HEAD, F1, finalization={"protocol": "other/1", "report": "/x"})
        self.invalid(self.state(record), "unknown finalization protocol")

    def test_interrupted_addendum_is_incomplete_and_a_retry_replaces_it(self):
        record = self.record()
        killed = self.compose(record, self.store(HEAD, F1), self.continuation(), inject="kill")
        self.assertEqual(killed.returncode, 137, killed.stdout + killed.stderr)
        interrupted = record.parent / "addenda" / f"addendum-{F1}.json"
        self.assertTrue(interrupted.exists() and not (record.parent / "addenda" / f"addendum-{F1}.report.md").exists())
        self.invalid(self.state(record), "does not exist, so its finalization did not complete")
        # Another continuation from the same state cannot build on an interrupted write it did not make.
        self.assertTrue(self.compose(record, self.store(HEAD, F2), self.continuation()).stdout.startswith("chain-invalid\n"))
        self.composed(record, self.store(HEAD, F1), self.continuation())
        # A write that fails before its report leaves nothing consumable.
        failed = self.compose(record, self.store(F1, F2), self.continuation(fixed_findings=[]), inject="fail")
        self.assertEqual(failed.returncode, 2, failed.stdout + failed.stderr)
        self.no_new_addendum(record, F2)
        self.assertEqual(self.state(record).returncode, 0)
        # A complete addendum is never overwritten.
        self.refused(self.compose(record, self.store(HEAD, F1), self.continuation()), "chain")

    # --- legacy routing -----------------------------------------------------------------

    def test_version_one_and_mixed_chains_route_to_the_manual_mapping(self):
        record = self.record()
        doc = json.loads(record.read_text(encoding="utf-8"))
        doc.pop("finalization")
        record.write_text(json.dumps(dict(doc, schema="implementation-gate-record/1")), encoding="utf-8")
        mixed = self.addendum(record, HEAD, F1, record_format="implementation-gate-record/1", coverage="incomplete",
                              coverage_gaps=["v1-clean-verdict needs discharge"],
                              verification={"tasks": [], "batches": [], "allowance": {"initial_spent": True, "follow_up_spent": True,
                                                                                      "carried_from": None},
                                            "outstanding": ["v1-clean-verdict"]})
        result = self.state(record)
        self.assertEqual(result.returncode, 1, result.stdout)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[:3], ["legacy-chain-needs-mapping", f"chain implementation-gate-record/1 {record}",
                                     f"chain implementation-gate-addendum/2 {mixed}"])
        self.assertIn('floor allowance {"initial_spent": true, "follow_up_spent": true, "carried_from": null}', lines)
        self.assertIn('floor outstanding ["v1-clean-verdict"]', lines)
        self.assertNotIn("Approved", result.stdout)
        refused = self.compose(record, self.store(F1, F2), self.continuation())
        self.assertEqual((refused.returncode, refused.stdout), (1, result.stdout), "compose routes the same way and writes nothing")
        self.no_new_addendum(record, F2)
        # A version-1 addendum on a version-2 record routes too; unreadable legacy state stays incomplete instead.
        record = self.record()
        self.addendum(record, HEAD, F1, format="implementation-gate-addendum/1")
        self.assertTrue(self.state(record).stdout.startswith("legacy-chain-needs-mapping\n"))
        (record.parent / "addenda" / f"addendum-{F2}.json").write_text("not json", encoding="utf-8")
        self.invalid(self.state(record), "cannot be read")

    # --- installed callers ----------------------------------------------------------------

    def test_installed_caller_reads_the_helper_path_and_cannot_publish_from_an_invalid_chain(self):
        record = self.record()
        checked = run(SCRIPTS / "finalize_review.py", "--check", "--profile", "implementation-gate", record.parent)
        self.assertEqual(checked.returncode, 0, checked.stdout)
        helper = dict(line.split(" ", 1) for line in checked.stdout.splitlines())["continuation"]
        self.assertEqual(helper, str(HELPER))
        self.assertTrue(checked.stdout.endswith(f"report {record.parent / 'report.md'}\n"))
        self.addendum(record, HEAD, F1)
        self.addendum(record, HEAD, F2)
        forked = run(helper, "state", record)
        self.assertEqual(forked.returncode, 1)
        self.assertTrue(forked.stdout.startswith("chain-invalid\n"))
        text = (SKILL.parent / "implement-publish" / "references" / "continuation.md").read_text(encoding="utf-8")
        for needle in ("`continuation`", "state", "compose", "chain-invalid", "legacy-chain-needs-mapping"):
            self.assertIn(needle, text)
        gate = (SKILL.parent / "implement-publish" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("exit 0", gate)


def _drop(record: Path, final: str, key: str) -> None:
    path = record.parent / "addenda" / f"addendum-{final}.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value.pop(key)
    path.write_text(json.dumps(value), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
