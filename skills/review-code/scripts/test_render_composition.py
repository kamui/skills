#!/usr/bin/env python3
"""Exercise render_review.py's composition rules: composition, refusal, and batch agreement.

Usage: python3 scripts/test_render_composition.py
Inputs: local fixture compositions and a disposable Git repository; no forge access.
Exit 0: all checks pass; exit 1: a check fails; exit 2: the CLI cannot run.

Every fixture composes a payload with render_review.compose, validates it, and
projects it through the real `render_review.py --emit-batch` CLI, so composition,
validation and the batch are checked in agreement. Refusal fixtures assert the rule
name and that no payload is returned. Finalization, the record and prior-record runs
are exercised through the CLI by test_render_review.py.
"""
from __future__ import annotations

import atexit
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import render_review as vr

SCRIPT = Path(__file__).with_name("render_review.py")
COMPOSER, VALIDATOR = "compose", "validate"  # the composition and validation seams run() drives
CONTEXT_SCRIPT = Path(__file__).with_name("review_context.py")
HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
BASE = "b2c3d4e5f60718293a4b5c6d7e8f90123456789a"
MERGE_BASE = "d4e5f60718293a4b5c6d7e8f90123456789abcde"
PRIOR = "0123456789abcdef0123456789abcdef01234567"
CONTEXT = "91d34a2f4c869867167f0b31da7c207f4528e12e3d1ef4f107a5eabb4c18718e"
REPO = "https://github.com/acme/payments"
BLOB = f"{REPO}/blob/{HEAD}"
FINDING_FRAGMENT = (
    f"anchor [`src/payments.ts:42`]({BLOB}/src/payments.ts?plain=1#L42); "
    f"fix [`src/retry-policy.ts:18`]({BLOB}/src/retry-policy.ts?plain=1#L18)"
)
QUESTION_FRAGMENT = f"anchor [`src/queue.ts`]({BLOB}/src/queue.ts) (file)"


def run(script: str, stdin: str, *args: str) -> subprocess.CompletedProcess:
    """Compose or validate in process with the old CLI's result shape; `--emit-batch` runs the real CLI."""
    if script == VALIDATOR and "--emit-batch" in args:
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin, capture_output=True, encoding="utf-8", check=False)

    def result(code: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess([script, *args], code, stdout, stderr)

    try:
        value = json.loads(stdin)
    except ValueError as error:
        return result(2, stderr=f"render_review: cannot read composition input: {error}")
    if script == VALIDATOR:
        lines = vr.validate(value)
        return result(1 if lines else 0, "".join(f"{line}\n" for line in lines))
    store = None
    if "--store" in args:
        try:
            store = json.loads(Path(args[args.index("--store") + 1]).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            return result(2, stderr=f"render_review: cannot read store: {error}")
    payload, violations = vr.compose(value, store)
    if violations:
        return result(1, "".join(f"{line}\n" for line in violations))
    return result(0, json.dumps(payload, indent=2) + "\n")


def base_composition() -> dict:
    """The output contract's example review as a composition input."""
    return {
        "run": {
            "head": HEAD, "base_ref": "main", "base_sha": BASE, "merge_base": MERGE_BASE, "packet_context": CONTEXT,
            "supplied_inputs": "no", "issues": ["acme/payments#123"], "coverage": "complete", "repository_url": REPO, "merged": False,
        },
        "summary": {
            "status": "Changes Requested",
            "intent": "Add retries for charge submission without changing payment semantics.",
            "issue_fit": "Partial — retry availability is implemented, but acceptance criterion 2's idempotency guarantee remains open.",
            "coverage": "Complete merge-base diff reviewed; payment callers inspected; focused `retry-policy` test run once at the head: pass.",
        },
        "findings": [
            {
                "id": "payments/retry-idempotency", "title": "Preserve the idempotency key across retries",
                "priority": "P1", "action": "must-fix", "kind": "requirement",
                "trigger": "The server commits a charge but its response times out and the\nclient retries.",
                "impact": "The retry uses a new idempotency key and can submit a second charge.",
                "change": "In `src/retry-policy.ts`, reuse one idempotency key across every attempt\nfor the same logical charge.",
                "source": "Issue #123, acceptance criterion 2.",
                "anchor": {"type": "line", "path": "src/payments.ts", "start_line": 42, "end_line": 42, "side": "RIGHT"},
                "fix": {"path": "src/retry-policy.ts", "start_line": 18},
            }
        ],
        "questions": [
            {
                "id": "queue/retry-order", "title": "Must retries preserve request order?",
                "evidence": "The new queue retries at the tail, while existing callers consume it\nas FIFO. The issue, tests, and history do not establish whether reordering is allowed.",
                "why_it_matters": "The answer determines whether this is a merge-blocking regression.",
                "answer": "Confirm whether retry order is part of the contract;\nthe maintainer answer settles whether the candidate should re-open as a finding.",
                "anchor": {"type": "file", "path": "src/queue.ts", "side": "RIGHT"},
            }
        ],
        "observations": [
            {
                "fact": "The first configuration sentence covers same-shard re-points more broadly than the implementation does.",
                "evidence": "`redis.conf:1903`, `src/replication.c:2701`.",
            }
        ],
    }


def composed(composition: dict, name: str, *args: str) -> tuple[dict, dict, str]:
    """Compose, then validate and project the printed payload; return (payload, batch, raw stdout)."""
    result = run(COMPOSER, json.dumps(composition), *args)
    assert result.returncode == 0, (name, result.returncode, result.stdout, result.stderr)
    assert result.stderr == "", (name, result.stderr)
    payload = json.loads(result.stdout)
    checked = run(VALIDATOR, result.stdout)
    assert checked.returncode == 0, (name, checked.stdout)
    emitted = run(VALIDATOR, result.stdout, "--emit-batch")
    assert emitted.returncode == 0, (name, emitted.stdout)
    batch = json.loads(emitted.stdout)
    assert batch["commit_id"] == composition["run"]["head"] and batch["body"] == payload["summary"]["body"], name
    inline = [item for item in payload["items"] if item["type"] != "observation" and item["anchor"]["type"] == "line"]
    assert len(batch["comments"]) == len(inline), (name, batch["comments"])
    for item in payload["items"]:
        if item["type"] == "observation":
            assert item["markdown"] in payload["summary"]["body"], (name, item)
            continue
        fragment = vr.render_reference(item, {"head": composition["run"]["head"], "merge_base": composition["run"]["merge_base"], "repository_url": REPO})
        assert payload["summary"]["body"].count(fragment) == 1, (name, fragment)
        if item["anchor"]["type"] != "line":
            # A body-carried item keeps its complete prose and trailer in the body, once.
            assert payload["summary"]["body"].count(item["markdown"]) == 1, (name, item["id"])
            assert payload["summary"]["body"].count(item["trailer"]) == 1, (name, item["id"])
        else:
            assert item["markdown"] not in payload["summary"]["body"], (name, item["id"])
            assert any(comment["body"] == f"{item['markdown']}\n\n{item['trailer']}" for comment in batch["comments"]), name
    return payload, batch, result.stdout


def refused(composition: dict, rule: str, name: str, *args: str, needle: str | None = None) -> str:
    result = run(COMPOSER, json.dumps(composition), *args)
    assert result.returncode == 1, (name, result.returncode, result.stdout, result.stderr)
    rules = {line.split(": ", 2)[1] for line in result.stdout.splitlines() if line.count(": ") >= 2}
    assert rule in rules, (name, rule, result.stdout)
    assert '"summary"' not in result.stdout and "commit_id" not in result.stdout, (name, result.stdout)
    if needle is not None:
        assert needle in result.stdout, (name, needle, result.stdout)
    return result.stdout


def finding(**overrides) -> dict:
    value = base_composition()["findings"][0]
    value.update(overrides)
    return value


def consider(**overrides) -> dict:
    value = finding(id="payments/retry-naming", title="Name the retry budget constant", priority="P3", action="consider",
                    kind="maintainability", change="Name the budget constant in `src/payments.ts` after the policy it bounds.",
                    anchor={"type": "line", "path": "src/payments.ts", "start_line": 50, "end_line": 50, "side": "RIGHT"})
    del value["fix"]
    value.update(overrides)
    return value


def local_targets() -> None:
    for kind in ("range", "worktree"):
        value = base_composition()
        value["run"].pop("repository_url")
        value["run"].pop("packet_context")
        value["run"].update(target_kind=kind, target="main..HEAD", tree="e" * 40,
                            change_description="Keep the key", specs=["spec/retries"], supplied_inputs="yes")
        value["findings"][0]["source"] = 'commit-abcdef0/"Keep the key"'
        value["findings"][0]["anchor"]["side"] = "LEFT"
        result = run(COMPOSER, json.dumps(value))
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(result.stdout)
        body = payload["summary"]["body"]
        assert "repository_url" not in payload["summary"] and "](http" not in body, body
        assert "anchor `src/payments.ts:42`; fix `src/retry-policy.ts:18`" in body, body
        assert "anchor `src/queue.ts (file)`" in body, body
        assert 'commit-abcdef0/"Keep the key"' in payload["items"][0]["markdown"]
        assert "Source: originating issues; user-supplied spec; commit messages in the range." in body, body
        assert "**Mode:**" not in body, body
        if kind == "worktree":
            assert f"Working tree snapshot `{HEAD}` (tree `{'e' * 40}`)" in body, body
            bad_tree = copy.deepcopy(value)
            bad_tree["run"].pop("tree")
            refused(bad_tree, "schema", "snapshot tree required", needle="run.tree")
        else:
            assert "**Reviewed:** Range `main..HEAD`: `a1b2c3d` against merge-base" in body, body
        assert run(VALIDATOR, result.stdout).returncode == 0
        assert run(VALIDATOR, result.stdout, "--emit-batch").returncode == 0
        assert "packet_context=none supplied_inputs=yes " in payload["summary"]["trailer"], payload["summary"]["trailer"]
        refused(dict(value, run=dict(value["run"], packet_context=CONTEXT)), "trailer-grammar", "a local target has no packet digest")
        refused(dict(value, run=dict(value["run"], supplied_inputs="no")), "trailer-grammar", "supplied_inputs contradicts specs")
        value["run"].update(issues=[], specs=[], change_description="", supplied_inputs="no")
        result = run(COMPOSER, json.dumps(value))
        assert result.returncode == 0, result.stdout
        assert "Source: no source (no issue, spec, or commit messages)." in json.loads(result.stdout)["summary"]["body"]
        value["run"]["repository_url"] = REPO
        refused(value, "schema", "local links refused")
        value["run"].pop("repository_url")
        value["run"]["merged"] = True
        refused(value, "schema", "local retrospective refused")

    # Explicit pull-request identity preserves the existing fixture byte for byte.
    implicit = run(COMPOSER, json.dumps(base_composition()))
    explicit = base_composition()
    explicit["run"]["target_kind"] = "pull-request"
    assert run(COMPOSER, json.dumps(explicit)).stdout == implicit.stdout

    # Real producer metadata is required when composing a stored snapshot.
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        def git(*args):
            return subprocess.run(["git", *args], cwd=root, capture_output=True,
                                  text=True, encoding="utf-8", check=True).stdout.strip()
        git("init", "-q")
        git("config", "user.name", "Test")
        git("config", "user.email", "test@example.invalid")
        (root / "file").write_text("base\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-qm", "Initial")
        base = git("rev-parse", "HEAD")
        (root / "file").write_text("working\n", encoding="utf-8")
        store = Path(directory) / "context.json"
        subprocess.run([sys.executable, str(CONTEXT_SCRIPT), "--worktree", "--store", str(store)],
                       cwd=root, capture_output=True, text=True, encoding="utf-8", check=True)
        snapshot = json.loads(store.read_text(encoding="utf-8"))["context"]["snapshot"]
        value = {"run": {"head": snapshot["head"], "base_sha": base, "merge_base": base,
                         "base_ref": "HEAD", "target_kind": "worktree", "tree": snapshot["tree"],
                         "supplied_inputs": "no", "issues": [], "coverage": "complete", "merged": False,
                         "change_description": ""},
                 "summary": {"status": "Approved", "intent": "Edit file.",
                             "issue_fit": "Issue alignment unavailable; no stated promises.",
                             "coverage": "Complete working-tree diff inspected."}}
        result = run(COMPOSER, json.dumps(value), "--store", str(store))
        assert result.returncode == 0, result.stdout + result.stderr
        value["run"]["tree"] = "0" * 40
        refused(value, "run-identity", "snapshot tree/store mismatch", "--store", str(store))
    print("ok local targets: identity, source kinds, code spans, and unchanged pull-request fixture")


# Verifier artifacts the record's tasks name; the composer reads each batch's accounting report.
ARTIFACTS = tempfile.mkdtemp(prefix="compose-review-test-")
atexit.register(shutil.rmtree, ARTIFACTS, True)


def batch_paths(name: str, phase: str | None = None) -> dict:
    return {"name": name, "phase": phase or name, "bundle": f"{ARTIFACTS}/{name}", "raw_return": f"{ARTIFACTS}/{name}/raw-return.json",
            "accounting": f"{ARTIFACTS}/{name}/accounting.json", "operation": "Agent run_in_background=false"}


def write_accounting(path: str, tasks: list) -> None:
    """An accounting report, in the shape account_verifier_return.py writes, that establishes each task's ruling."""
    report = {"format": "verifier-accounting/3", "accounted": {"candidates": [], "premises": []},
              "withheld": {"candidates": [], "premises": []}, "return": {"candidates": [], "premises": []}}
    for task in tasks:
        role = "candidates" if task["type"] == "candidate" else "premises"
        if task["ruling"] == "withheld":
            report["withheld"][role].append(task["id"])
            continue
        report["accounted"][role].append(task["id"])
        if role == "premises":
            record = {"id": task["id"], "ruling": task["ruling"]}
        elif task["ruling"] == "confirmed":
            record = {"id": task["id"], "verdict": "confirmed", "basis": "decisive"}
        else:
            record = {"id": task["id"], "verdict": "refuted", "basis": "unresolved" if task["ruling"] == "unresolved" else "contradicted"}
        report["return"][role].append(record)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(report), encoding="utf-8")


def candidate_task(identity: str = "payments/retry-idempotency", trigger: str = "must-fix", batch: str | None = "initial",
                   ruling: str = "confirmed") -> dict:
    return {"id": identity, "type": "candidate", "trigger": trigger, "batch": batch, "ruling": ruling}


def premise_task(identity: str = "premise-1", ruling: str = "holds", batch: str | None = "initial", **extra) -> dict:
    return {"id": identity, "type": "safety-premise", "area": "data-integrity",
            "premise": "The charge lookup always succeeds before `submitCharge()` records the charge.",
            "evidence": "src/charges.ts:31", "batch": batch, "ruling": ruling, **extra}


def verification(tasks: list, batches: list, initial: bool | None = None, follow_up: bool | None = None,
                 outstanding: list | None = None) -> dict:
    phases = {b["phase"] for b in batches}
    for batch in batches:
        write_accounting(batch["accounting"], [t for t in tasks if t.get("batch") == batch["name"]])
    return {"tasks": tasks, "batches": batches,
            "allowance": {"initial_spent": bool(phases) if initial is None else initial,
                          "follow_up_spent": "follow-up" in phases if follow_up is None else follow_up},
            "outstanding": outstanding or []}


def gate_composition() -> dict:
    """The contract example as a committed local range with the private record's accounting."""
    value = base_composition()
    value["run"].pop("repository_url")
    value["run"].pop("packet_context")
    value["run"].update(target_kind="range", target="main..HEAD", change_description="Keep the key", specs=["spec/retries"],
                        supplied_inputs="yes")
    value["record"] = {
        "repository": "/repo",
        "paths": {"private_dir": "/tmp/x", "store": f"/tmp/x/review-context-{HEAD}.json", "composition": "/tmp/x/composition.json",
                  "skill_root": "/skills/review-code", "evidence_packet": "/tmp/x/evidence.md"},
        "requirements": [{"source": "issue-123/acceptance-criterion-2", "class": "acceptance", "disposition": "partial",
                          "evidence": "src/payments.ts:42 creates a key per attempt"}],
        "files": [{"path": "src/payments.ts", "state": "reviewed"}, {"path": "src/retry-policy.ts", "state": "reviewed"},
                  {"path": "src/queue.ts", "state": "reviewed"}, {"path": "docs/notes.md", "state": "ignored", "reason": "generated"}],
        "check_evidence": [
            {"check": "python3 scripts/test_retry.py", "head": HEAD, "outcome": "accepted", "reason": "same command, clean tree, output read"},
            {"check": "python3 scripts/test_queue.py", "head": PRIOR, "outcome": "historical", "reason": "the delta reaches none of its inputs"},
            {"check": "python3 scripts/test_payments.py", "head": HEAD, "outcome": "reviewer-executed", "reason": "the fixture changed since the supplied run"},
        ],
        "verification": verification([candidate_task()], [batch_paths("initial")]),
        "routed": {"unresolved": [], "disputed": [], "unrecoverable_inputs": []},
    }
    return value


def gate(composition: dict, name: str, *args: str) -> tuple[dict, str]:
    """Compose the record fields render_review.py writes into record.json; the payload they carry must validate."""
    store = json.loads(Path(args[args.index("--store") + 1]).read_text(encoding="utf-8")) if "--store" in args else None
    payload, fields, violations = vr.compose_record(composition, store)
    assert not violations, (name, violations)
    record = {"workflow": vr.WORKFLOW, "run": dict(fields["run"], issues=sorted(composition["run"]["issues"])),
              "status": fields["status"], "summary": payload["summary"], "items": payload["items"], "record": fields["record"]}
    assert "ledger" not in record["record"] and "clean_verdict" not in record["record"]["verification"], name
    assert record["run"]["head"] == composition["run"]["head"], name
    assert record["run"]["target"] == composition["run"].get("target") and record["record"]["repository"] == composition["record"]["repository"], name
    assert run(VALIDATOR, json.dumps(payload)).returncode == 0, name
    return record, json.dumps(record, indent=2)


def record_accounting() -> None:
    # The record section adds accounting without changing the review it carries.
    composition = gate_composition()
    plain = copy.deepcopy(composition)
    plain.pop("record")
    payload = json.loads(run(COMPOSER, json.dumps(plain)).stdout)
    assert run(COMPOSER, json.dumps(composition)).stdout == run(COMPOSER, json.dumps(plain)).stdout, "the payload is unchanged by a record section"
    record, stdout = gate(composition, "record fixture")
    assert record["summary"] == payload["summary"] and record["items"] == payload["items"], "the record carries the payload's review"
    assert record["status"] == "Changes Requested" and record["run"]["coverage"] == "complete"
    assert [item["id"] for item in record["items"] if item["type"] != "observation"] == ["payments/retry-idempotency", "queue/retry-order"]
    assert record["record"]["verification"] == composition["record"]["verification"], "verification accounting is carried as given"
    assert [e["outcome"] for e in record["record"]["check_evidence"]] == ["accepted", "historical", "reviewer-executed"], "reused evidence keeps its outcomes"
    assert record["run"]["issues"] == ["acme/payments#123"]
    assert gate(composition, "again")[1] == stdout, "record composition is deterministic"
    print("ok record: the payload's review, validator-readable, accounting carried")

    # Semantic contradictions in the record's accounting are refused by rule.
    def mutate(**changes):
        value = copy.deepcopy(composition)
        for path, new in changes.items():
            target = value
            keys = path.split(".")
            for key in keys[:-1]:
                target = target[int(key)] if key.isdigit() else target[key]
            if new is None:
                del target[keys[-1]]
            else:
                target[keys[-1]] = new
        return value

    contradictions = [
        ("priority-action", mutate(**{"findings.0.blocking": False})),
        ("stable-id", mutate(**{"questions.0.id": "payments/retry-idempotency"})),
        ("status-consistency", mutate(**{"summary.status": "Approved"})),
        ("check-evidence", mutate(**{"record.check_evidence.1.head": HEAD})),
        ("check-evidence", mutate(**{"record.check_evidence.0.head": PRIOR})),
        ("schema", mutate(**{"record.check_evidence.2.reason": None})),
        ("verification", mutate(**{"record.verification.allowance.follow_up_spent": True})),
        ("verification", mutate(**{"record.verification.allowance.initial_spent": False})),
        ("verification", mutate(**{"record.verification.batches": [batch_paths("a", "initial"), batch_paths("b", "follow-up"), batch_paths("c", "follow-up")]})),
        ("verification", mutate(**{"record.verification.batches": [], "record.verification.allowance.initial_spent": False})),
        ("verification", mutate(**{"record.verification.tasks.0.ruling": "refuted"})),
        ("verification", mutate(**{"record.verification.tasks.0.trigger": "optional"})),
        ("verification", mutate(**{"record.verification.tasks": []})),
        ("verification", mutate(**{"record.verification.tasks.0.batch": "follow-up"})),
        ("stable-id", mutate(**{"record.verification.tasks": [candidate_task(), candidate_task()]})),
        ("coverage-gaps", mutate(**{"record.verification.outstanding": ["premise-2: follow-up spent"]})),
        ("coverage-gaps", mutate(**{"record.files.0.state": "unreviewed"})),
        ("file-accounting", mutate(**{"record.files.1.path": "src/payments.ts"})),
        ("schema", mutate(**{"record.files.3.reason": None})),
        ("requirements", mutate(**{"record.requirements.0.class": "wish"})),
        ("stable-id", mutate(**{"record.routed.unresolved": ["payments/unknown"]})),
        ("coverage-gaps", mutate(**{"record.routed.unrecoverable_inputs": ["the spec's benchmark artifact"]})),
        ("record-paths", mutate(**{"record.paths.store": "relative/store.json"})),
        ("schema", mutate(**{"record.verification": None})),
        ("schema", mutate(**{"record.verification.allowance": None})),
    ]
    for rule, bad in contradictions:
        refused(bad, rule, f"record rejects {rule}")
    # Every target kind shares the record shape; the record names the skill root its readers run scripts from.
    gate(mutate(**{"run.target_kind": "worktree", "run.tree": "e" * 40, "run.target": None}), "worktree record")
    gate(mutate(**{"run.prior_head": PRIOR}), "delta review record")
    refused(mutate(**{"record.paths.skill_root": None}), "record-paths", "record requires skill_root", needle="`skill_root`")
    refused(mutate(**{"record.verification.allowance.carried_from": "/tmp/x/record.json"}), "verification", "retired carried_from",
            needle="retired")
    refused(mutate(**{"record.verification.tasks.0.batch": "carried:/tmp/x/record.json#initial"}),
            "verification", "retired carried batch reference", needle="retired")
    print("ok record: contradictions refused by rule; retired carried references named")

    # Outcomes. Blocking with a confirmed candidate is the fixture above.
    def outcome(status: str, tasks: list, batches: list, findings: list | None = None, questions: list | None = None, **extra) -> dict:
        value = mutate(**{"findings": findings or [], "questions": questions or [], "observations": [], "summary.status": status})
        value["record"]["verification"] = verification(tasks, batches, **extra)
        if value["record"]["verification"]["outstanding"]:
            value["run"]["coverage"] = "incomplete"
            value["summary"]["coverage_gaps"] = ["required verification did not finish: " + "; ".join(value["record"]["verification"]["outstanding"])]
        return value

    # No blocker and no high-risk area: no task, no batch, nothing spent.
    record, _ = gate(outcome("Approved", [], []), "clean outcome with no verification")
    assert record["status"] == "Approved" and record["summary"]["body"].startswith("**Approved (advisory)** — no findings.")
    assert record["record"]["verification"]["allowance"] == {"initial_spent": False, "follow_up_spent": False}
    # A refuted candidate is dropped; an unresolved one is dropped only when optional.
    gate(outcome("Approved", [candidate_task(ruling="refuted"), candidate_task("queue/empty-pop", "optional", ruling="unresolved")],
                 [batch_paths("initial")]), "refuted and optional unresolved candidates publish nothing")
    # A required unresolved candidate becomes a question with its id or stays outstanding, never an Approved drop.
    refused(outcome("Approved", [candidate_task(ruling="unresolved")], [batch_paths("initial")]), "verification",
            "unresolved must-fix candidate dropped from an Approved record", needle="required candidate")
    gate(outcome("Needs Information", [candidate_task("queue/retry-order", "data-integrity", ruling="unresolved")], [batch_paths("initial")],
                 questions=copy.deepcopy(composition["questions"])), "unresolved required candidate routed to its question")
    gate(outcome("Incomplete", [candidate_task(ruling="unresolved")], [batch_paths("initial")],
                 outstanding=["payments/retry-idempotency: settling fact unavailable"]), "unresolved required candidate left outstanding")
    # A ruling stands only on the accounting report of the batch it names.
    mismatched = copy.deepcopy(composition)
    write_accounting(mismatched["record"]["verification"]["batches"][0]["accounting"], [candidate_task(ruling="refuted")])
    refused(mismatched, "verification", "confirmed task over an accounting that refuted it",
            needle="establishes `refuted`, not `confirmed`")
    missing = copy.deepcopy(composition)
    missing["record"]["verification"]["batches"][0]["accounting"] = f"{ARTIFACTS}/absent/accounting.json"
    refused(missing, "verification", "confirmed task over a missing accounting report", needle="cannot be read")
    unaccounted = copy.deepcopy(composition)
    write_accounting(unaccounted["record"]["verification"]["batches"][0]["accounting"], [candidate_task(ruling="withheld")])
    refused(unaccounted, "verification", "confirmed task the accounting withheld",
            needle="establishes `withheld`, not `confirmed`")
    write_accounting(composition["record"]["verification"]["batches"][0]["accounting"], composition["record"]["verification"]["tasks"])
    gate(composition, "fixture composes again once its accounting is rewritten")
    # A premise ruling is checked the same way, and a malformed report is refused rather than crashing.
    premise_mismatch = outcome("Approved", [premise_task()], [batch_paths("initial")])
    write_accounting(premise_mismatch["record"]["verification"]["batches"][0]["accounting"], [premise_task(ruling="fails")])
    refused(premise_mismatch, "verification", "premise ruling its accounting does not establish",
            needle="establishes `fails`, not `holds`")
    Path(premise_mismatch["record"]["verification"]["batches"][0]["accounting"]).write_text(
        json.dumps({"withheld": ["premise-1"], "accounted": "x", "return": None}), encoding="utf-8")
    refused(premise_mismatch, "verification", "malformed accounting report", needle="does not account")
    # A batch whose accounting produced no report still records its withheld tasks as outstanding work.
    no_report = outcome("Incomplete", [candidate_task(ruling="withheld"), candidate_task("payments/retry-naming", "optional", ruling="withheld")],
                        [batch_paths("initial")], outstanding=["payments/retry-idempotency: accounting produced no report"])
    Path(no_report["record"]["verification"]["batches"][0]["accounting"]).unlink()
    gate(no_report, "withheld tasks over a batch with no accounting report")
    # High-risk no-blocker conclusion: a premise that holds approves, and a question can carry an unresolved one.
    record, _ = gate(outcome("Approved", [premise_task()], [batch_paths("initial")]), "safety premise holds")
    assert record["record"]["verification"]["tasks"][0]["type"] == "safety-premise"
    gate(outcome("Needs Information", [premise_task(ruling="unresolved", reopened_as="queue/retry-order")], [batch_paths("initial")],
                 questions=copy.deepcopy(composition["questions"])), "unresolved premise routed to a material question")
    refused(outcome("Approved", [premise_task(ruling="unresolved")], [batch_paths("initial")]), "verification",
            "unresolved premise with neither a question nor outstanding work", needle="premise-1")
    gate(outcome("Incomplete", [premise_task(ruling="unresolved")], [batch_paths("initial")], outstanding=["premise-1: settling fact unavailable"]),
         "unresolved premise left outstanding")
    # A premise that fails reopens as a candidate; the follow-up confirms the new blocker it became.
    reopened = [premise_task(ruling="fails", reopened_as="payments/retry-idempotency"),
                candidate_task(batch="follow-up")]
    record, _ = gate(outcome("Changes Requested", reopened, [batch_paths("initial"), batch_paths("follow-up")],
                             findings=copy.deepcopy(composition["findings"])), "failed premise reopened and confirmed in the follow-up")
    assert record["record"]["verification"]["allowance"]["follow_up_spent"] is True
    refused(outcome("Approved", [premise_task(ruling="fails")], [batch_paths("initial")]), "verification",
            "failed premise with nothing reopened", needle="reopened_as")
    # A new blocker found after feedback needs a follow-up confirmation; with the follow-up spent it stays unpublished and outstanding.
    new_blocker = [candidate_task(), candidate_task("queue/lost-ack", batch="follow-up")]
    two_findings = copy.deepcopy(composition["findings"]) + [finding(id="queue/lost-ack", title="Acknowledge only after the write",
                                                                     anchor={"type": "line", "path": "src/queue.ts", "start_line": 9, "end_line": 9, "side": "RIGHT"})]
    gate(outcome("Changes Requested", new_blocker, [batch_paths("initial"), batch_paths("follow-up")], findings=two_findings),
         "new blocker after feedback confirmed in the follow-up")
    refused(outcome("Changes Requested", [candidate_task(), candidate_task("queue/lost-ack", batch=None, ruling="pending")],
                    [batch_paths("initial"), batch_paths("follow-up")], findings=two_findings), "verification",
            "unconfirmed new blocker rendered after the allowance is spent", needle="queue/lost-ack")
    exhausted = outcome("Changes Requested", [candidate_task(), candidate_task("queue/lost-ack", batch=None, ruling="pending")],
                        [batch_paths("initial"), batch_paths("follow-up")], findings=copy.deepcopy(composition["findings"]),
                        outstanding=["queue/lost-ack: must-fix candidate arrived after the follow-up was spent"])
    record, _ = gate(exhausted, "exhausted allowance leaves the new blocker outstanding")
    assert record["run"]["coverage"] == "incomplete" and record["status"] == "Changes Requested"
    refused(outcome("Changes Requested", [candidate_task(), candidate_task("queue/lost-ack", batch=None, ruling="pending")],
                    [batch_paths("initial"), batch_paths("follow-up")], findings=copy.deepcopy(composition["findings"])), "verification",
            "pending required work missing from outstanding", needle="queue/lost-ack")
    # Missing evidence: a withheld required result is outstanding work, never completed verification.
    withheld = outcome("Incomplete", [candidate_task(ruling="withheld")], [batch_paths("initial")],
                       outstanding=["payments/retry-idempotency: return cited no raw location"])
    gate(withheld, "withheld candidate outstanding")
    refused(outcome("Approved", [candidate_task(ruling="withheld")], [batch_paths("initial")]), "verification",
            "withheld candidate without outstanding work", needle="withheld")
    gate(outcome("Approved", [candidate_task("payments/retry-naming", "optional", ruling="withheld")], [batch_paths("initial")]),
         "withheld optional scrutiny stays optional")
    for ruling in ("withheld", "unresolved"):
        gate(outcome("Approved", [premise_task(ruling=ruling, trigger="optional")], [batch_paths("initial")]),
             f"{ruling} optional premise stays optional")
    refused(outcome("Approved", [premise_task(trigger="must-fix")], [batch_paths("initial")]), "verification",
            "a premise trigger other than optional", needle="only as `optional`")
    # No awaited route: required work is pending with no batch, and nothing is spent.
    gate(outcome("Incomplete", [premise_task(ruling="pending", batch=None)], [], outstanding=["premise-1: review-wait-unavailable"]),
         "pending premise with no route")
    print("ok record: confirmed, refuted, unresolved, premise, new-blocker, missing-evidence, and exhausted outcomes")

    # Carried confirmations and a prior record's allowance are checked against real records in test_render_review.py.
    refused(outcome("Changes Requested", [dict(candidate_task(), confirmed_in="/tmp/x/record.json")], [],
                    findings=copy.deepcopy(composition["findings"])), "verification", "carried confirmation without a prior record",
            needle="only a prior_record run")
    refused(outcome("Approved", [], [], initial=True), "verification", "spent flag with nothing recorded or carried",
            needle="no `initial` batch recorded here")
    print("ok record: a carried confirmation or spent flag needs a prior record")

    # Deleted and renamed evidence against a real store: file accounting is exactly the pinned manifest.
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        def git(*args):
            return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
        git("init", "-q")
        git("config", "user.name", "Test")
        git("config", "user.email", "test@example.invalid")
        for name in ("gone.txt", "old.txt", "kept.txt"):
            (root / name).write_text("\n".join(f"{name} line {i}" for i in range(1, 21)) + "\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-qm", "base")
        base = git("rev-parse", "HEAD")
        git("rm", "-q", "gone.txt")
        git("mv", "old.txt", "new.txt")
        (root / "kept.txt").write_text("changed\n" + "\n".join(f"kept.txt line {i}" for i in range(2, 21)) + "\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-qm", "Delete, rename, edit")
        head = git("rev-parse", "HEAD")
        store = Path(directory) / f"review-context-{head}.json"
        subprocess.run([sys.executable, str(CONTEXT_SCRIPT), "--merge-base", base, "--head", head, "--store", str(store)],
                       cwd=root, capture_output=True, check=True)
        manifest = {e["path"]: e["status"] for e in json.loads(store.read_text(encoding="utf-8"))["context"]["manifest"]}
        assert manifest["gone.txt"] == "D" and manifest["new.txt"].startswith("R") and manifest["kept.txt"] == "M", manifest
        value = gate_composition()
        value["run"].update(head=head, base_sha=base, merge_base=base, target="main..HEAD", change_description="Delete, rename, edit")
        value["findings"][0].update(anchor={"type": "file", "path": "gone.txt", "side": "LEFT"},
                                    fix={"path": "kept.txt", "start_line": 1}, change="In `kept.txt`, restore the guard the deleted file carried.")
        value["questions"][0]["anchor"] = {"type": "line", "path": "new.txt", "start_line": 1, "end_line": 1, "side": "RIGHT"}
        value["record"]["paths"]["store"] = str(store)
        value["record"]["files"] = [{"path": "gone.txt", "state": "reviewed"}, {"path": "new.txt", "state": "reviewed"}, {"path": "kept.txt", "state": "reviewed"}]
        for item in value["record"]["check_evidence"]:
            if item["outcome"] != "historical":
                item["head"] = head
        record, _ = gate(value, "deleted and renamed evidence", "--store", str(store))
        assert "anchor `gone.txt (file)`; fix `kept.txt:1`" in record["summary"]["body"], record["summary"]["body"]
        assert run(COMPOSER, json.dumps(value), "--store", str(store)).returncode == 0
        value["record"]["files"].pop()
        line = refused(value, "file-accounting", "manifest path without accounting", "--store", str(store), needle="kept.txt")
        assert line == refused(value, "file-accounting", "publishable manifest accounting", "--store", str(store))
        value["record"]["files"].append({"path": "kept.txt", "state": "reviewed"})
        value["record"]["files"].append({"path": "old.txt", "state": "reviewed"})
        refused(value, "file-accounting", "pre-image path is not a manifest path", "--store", str(store), needle="old.txt")
        value["record"]["files"].pop()
        value["findings"][0]["anchor"]["side"] = "RIGHT"
        refused(value, "anchor-provenance", "deleted file on the RIGHT", "--store", str(store))
    print("ok record: deleted and renamed evidence, file accounting against the pinned manifest")


def compact_reviews() -> None:
    for optional in (False, True):
        value = base_composition()
        value.update(findings=[consider()] if optional else [], questions=[], observations=[])
        value["summary"].update(status="Approved", issue_fit="Issue #123: requirements met.",
                                coverage="Full diff covered; focused retry-policy test passed.",
                                check_details=["Reviewer ran retry-policy at the reviewed head; output: saved-check.log"])
        payload, batch, raw = composed(value, "compact approval")
        body = payload["summary"]["body"]
        visible, opening, detail = body.partition("<details>\n<summary>Review details</summary>\n")
        assert opening and "<details open" not in body and body.count("</details>") == 1, body
        assert f"Reviewed `{HEAD[:7]}`. Full diff covered; focused retry-policy test passed." in visible
        assert value["summary"]["intent"] in detail and value["summary"]["intent"] not in visible
        assert value["summary"]["issue_fit"] in detail and "saved-check.log" in detail
        assert "saved-check.log" not in visible and payload["summary"]["trailer"] in detail.split("</details>")[1]
        if optional:
            assert visible.startswith("**Approved (advisory)** — no must-fix findings; 1 optional improvement."), visible
            assert "[P3] [consider] Name the retry budget constant" in visible
            comment = batch["comments"][0]["body"]
            assert vr.PERMISSION_SENTENCE in comment and "blocking=false" in comment
        else:
            assert visible.startswith("**Approved (advisory)** — no findings."), visible
            assert "## Findings" not in visible and not batch["comments"]
        gated = run(VALIDATOR, raw, "--emit-batch", "--event", "APPROVE")
        assert gated.returncode == 0, gated.stdout
        published = json.loads(gated.stdout)
        assert published["event"] == "APPROVE" and published["body"].startswith("**Approved** — ")
        assert published["comments"] == batch["comments"]

    for key in ("trigger", "impact", "change"):
        for empty in (None, "", " "):
            value = base_composition()
            if empty is None:
                del value["findings"][0][key]
            else:
                value["findings"][0][key] = empty
            refused(value, "schema", f"missing structured {key}", needle=key)
    value = base_composition()
    value["run"]["coverage"] = "incomplete"
    value["summary"]["coverage_gaps"] = ["src/queue.ts: execution unavailable; supply the queue fixture."]
    payload, _, _ = composed(value, "visible question and coverage gap")
    visible = payload["summary"]["body"].split("<details>", 1)[0]
    assert "## Open questions" in visible and "## Coverage gaps" in visible
    assert value["questions"][0]["why_it_matters"] in visible
    assert value["summary"]["coverage_gaps"][0] in visible

    value = base_composition()
    value["summary"]["check_details"] = "not a list"
    refused(value, "schema", "malformed check details", needle="check_details")

    value = base_composition()
    value["findings"][0]["change"] += "\n\n~~~~suggestion\n  const key = attempt.idempotencyKey;\n\n~~~~"
    payload, _, _ = composed(value, "fenced suggestion with blank line")
    markdown = payload["items"][0]["markdown"]
    explanation, block = markdown.split("\n\n", 2)[1:]
    for key in ("trigger", "impact", "source"):
        assert " ".join(value["findings"][0][key].splitlines()) in explanation
    assert block == "~~~~suggestion\n  const key = attempt.idempotencyKey;\n\n~~~~", block
    assert "**Triggers when:**" not in markdown and "**Impact:**" not in markdown and "**Change:**" not in markdown
    print("ok compact reviews: approvals, optional findings, disclosures, structured evidence and suggestion bytes")


def main() -> int:
    compact_reviews()
    # Ordinary finding, whole-change question, observation: the contract example, byte for byte where the contract renders it.
    contract = base_composition()
    payload, batch, stdout = composed(contract, "contract example")
    body = payload["summary"]["body"]
    assert body.startswith("**Changes Requested (advisory)** — 1 must-fix finding, 1 open question.\n\n## Findings"), body
    assert f"## Findings\n\n- [P1] [must-fix] Preserve the idempotency key across retries — {FINDING_FRAGMENT}\n\n" in body
    assert "## Open questions\n\n**[Question] Must retries preserve request order?**" in body
    assert f"\n\n{QUESTION_FRAGMENT}\n\n" in body
    assert "## Observations\n\n- The first configuration sentence" in body
    assert f"**Reviewed:** `{HEAD[:7]}` against merge-base `{MERGE_BASE[:7]}`." in body
    assert payload["items"][0]["markdown"] == vr.FINDING_MARKDOWN and payload["items"][1]["markdown"] == vr.QUESTION_MARKDOWN
    assert payload["items"][0]["trailer"] == vr.valid_payload()["items"][0]["trailer"]
    assert payload["summary"]["trailer"] == vr.RUN_TRAILER
    assert batch["comments"][0]["path"] == "src/payments.ts" and batch["comments"][0]["line"] == 42
    identity = {"head": HEAD, "merge_base": MERGE_BASE, "repository_url": REPO}
    assert [vr.render_reference(item, identity) for item in payload["items"][:2]] == [FINDING_FRAGMENT, QUESTION_FRAGMENT]
    assert run(COMPOSER, json.dumps(contract)).stdout == stdout, "composition is deterministic"
    for section in ("## Unanchored findings", "## Disputed", "## Prior findings", "## Coverage gaps", "## Ambiguities", "**Mode:**"):
        assert section not in body, section
    assert vr.validate(vr.valid_payload()) == [] and vr.validate(vr.unanchored_payload()) == [], "historical validator inputs remain readable"
    print("ok contract example: compose/validate/emit-batch agree, deterministic")

    # Optional finding: the permission sentence is rendered last, blocking derives from action, conflicts are refused.
    optional = base_composition()
    optional["findings"].append(consider())
    payload, batch, _ = composed(optional, "consider finding")
    item = payload["items"][1]
    assert item["markdown"].startswith("**[P3] [consider] Name the retry budget constant**") and item["blocking"] is False
    assert item["markdown"].endswith(f"Issue #123, acceptance criterion 2.\n\n{vr.PERMISSION_SENTENCE}"), item["markdown"]
    assert item["trailer"].endswith("blocking=false kind=maintainability -->") and len(batch["comments"]) == 2
    shared = base_composition()
    shared["findings"].append(consider(anchor=finding()["anchor"], fix=finding()["fix"], change=finding()["change"]))
    refused(shared, "summary-reference", "two findings sharing one anchor and fix", needle="findings[1]")
    assert "— 1 must-fix finding, 1 optional improvement, 1 open question." in payload["summary"]["body"]
    assert "- [P3] [consider] Name the retry budget constant — " in payload["summary"]["body"]
    refused({**optional, "findings": [finding(), consider(blocking=True)]}, "priority-action", "consider marked blocking")
    refused({**optional, "findings": [finding(blocking=False)]}, "priority-action", "must-fix marked non-blocking")
    refused({**optional, "findings": [finding(), consider(priority="P0")]}, "priority-action", "P0 consider")
    refused({**optional, "findings": [finding(kind="style")]}, "priority-action", "unknown kind")
    refused({**optional, "findings": [finding(change=f"Do it.\n\n{vr.PERMISSION_SENTENCE}")]}, "field-label", "authored permission sentence")
    print("ok consider finding: permission sentence, derived blocking, conflicting metadata refused")

    # Clean review, gating, and the advisory marker.
    clean = base_composition()
    clean.update({"findings": [], "questions": [], "observations": []})
    clean["summary"]["status"] = "Approved"
    payload, batch, _ = composed(clean, "clean review")
    assert payload["summary"]["body"].startswith("**Approved (advisory)** — no findings.\n") and batch["comments"] == []
    for gating in (True, False, "true", None):
        bad = copy.deepcopy(clean)
        bad["summary"]["gating"] = gating
        refused(bad, "publication-boundary", "gating belongs to publisher", needle="summary.gating")
    print("ok clean review: always advisory, composition gating input refused")

    # Questions: a line-anchored question is a comment; a whole-change question lives in the body with its prose.
    questions = base_composition()
    line_question = copy.deepcopy(questions["questions"][0])
    line_question.update({"id": "queue/retry-window", "title": "Is the retry window bounded?",
                          "anchor": {"type": "line", "path": "src/queue.ts", "start_line": 7, "end_line": 9, "side": "RIGHT"}})
    questions["questions"].append(line_question)
    payload, batch, _ = composed(questions, "line and whole-change questions")
    assert len(batch["comments"]) == 2 and batch["comments"][1]["start_line"] == 7 and batch["comments"][1]["line"] == 9
    assert "— 1 must-fix finding, 2 open questions." in payload["summary"]["body"]
    assert f"- [Question] Is the retry window bounded? — anchor [`src/queue.ts:7-9`]({BLOB}/src/queue.ts?plain=1#L7-L9)" in payload["summary"]["body"]
    bad = base_composition()
    bad["questions"][0]["answer"] = "**Change:** reorder the queue."
    refused(bad, "question-form", "question requesting code")
    bad = base_composition()
    bad["questions"][0]["evidence"] = f"{vr.QUESTION_FRAMING}. Already framed."
    refused(bad, "question-form", "question with authored framing")
    bad = base_composition()
    bad["questions"][0]["priority"] = "P2"
    refused(bad, "question-form", "question with priority")
    print("ok questions: line anchor is a comment, whole-change question is body-carried, malformed forms refused")

    # Observations: three publish; a fourth is refused with the private-record disposition named, never dropped.
    observations = base_composition()
    observations["observations"] = [
        {"fact": f"Fact number {n} stands on its own.", "evidence": f"`src/file{n}.ts:{n}`."} for n in range(1, 4)
    ]
    payload, _, _ = composed(observations, "three observations")
    assert payload["summary"]["body"].count("\n- Fact number ") == 3
    observations["observations"].append({"fact": "A fourth fact.", "evidence": "`src/file4.ts:4`."})
    refused(observations, "observation-cap", "four observations", needle="observation (unpublished, cap)")
    bad = base_composition()
    bad["observations"][0]["fact"] = "The configuration covers same-shard re-points. The implementation narrows it."
    refused(bad, "observation-form", "two-sentence observation", needle="observations[0]")
    bad = base_composition()
    bad["observations"][0]["fact"] = "The configuration should cover same-shard re-points."
    refused(bad, "observation-form", "observation using should", needle="observations[0]")
    print("ok observations: cap refused with the disposition named, validator locations translated")

    # Code and suggestion blocks are preserved verbatim; a literal label counts only outside code.
    suggestion = base_composition()
    suggestion["findings"][0]["change"] = (
        "Reuse one key across every attempt in `src/retry-policy.ts`:\n\n```suggestion\n"
        "const key = attempt.idempotencyKey; // **Impact:** and **Change:** here are code, not fields\n```"
    )
    payload, batch, _ = composed(suggestion, "suggestion block")
    patch = suggestion["findings"][0]["change"].split("\n\n", 1)[1]
    assert payload["items"][0]["markdown"].endswith(patch)
    assert patch in batch["comments"][0]["body"]
    span = base_composition()
    span["findings"][0]["change"] = "Keep the `**Impact:**` label in `src/retry-policy.ts`. Reuse one key."
    composed(span, "label inside a code span")
    bare = base_composition()
    bare["findings"][0]["change"] = "Reuse one key in `src/retry-policy.ts`.\n\n**Impact:** restated here."
    refused(bare, "field-label", "literal label outside code", needle="findings[0]")
    print("ok code blocks: suggestion and code-span labels preserved, bare label refused")

    # Every question/observation prose field owns its labels outside code only.
    for key in ("evidence", "why_it_matters", "answer"):
        for label in ("**Evidence:**", "**Why it matters:**", "**Change:**", vr.QUESTION_FRAMING):
            for code in (f"`{label}`", f"\n\n```text\n{label}\n```\n"):
                sample = base_composition()
                sample["questions"][0][key] += f" {code}"
                payload, _, _ = composed(sample, f"question {key} code label")
                assert sample["questions"][0][key] in payload["items"][1]["markdown"]
            sample = base_composition()
            sample["questions"][0][key] += f" {label} Duplicate."
            refused(sample, "question-form" if label == vr.QUESTION_FRAMING else "field-label", f"question {key} bare label", needle=key)
    for key in ("fact", "evidence"):
        for label in ("Evidence:", "**Evidence:**", "**Why it matters:**"):
            for code in (f"`{label}`", f"\n\n```text\n{label}\n```\n"):
                sample = base_composition()
                sample["observations"][0][key] = f"The literal {code} is present."
                payload, batch, _ = composed(sample, f"observation {key} code label")
                assert sample["observations"][0][key] in payload["items"][-1]["markdown"]
                assert sample["observations"][0][key] in batch["body"]
            sample = base_composition()
            sample["observations"][0][key] = f"The literal {label} is present."
            refused(sample, "field-label", f"observation {key} bare label", needle=key)
    whitespace = base_composition()
    whitespace["observations"][0] = {"fact": "  The configuration records the limit.  ", "evidence": "  `redis.conf:1903`. \n"}
    payload, batch, _ = composed(whitespace, "observation exact whitespace")
    authored = whitespace["observations"][0]
    expected = authored["fact"] + " Evidence: " + authored["evidence"]
    assert payload["items"][-1]["markdown"] == expected and expected in batch["body"]
    print("ok prose: all question and observation fields mask code labels and preserve authored bytes")

    # The composed advisory record feeds #226's authorized gating emitter unchanged.
    for composition, event, status in ((base_composition(), "REQUEST_CHANGES", "Changes Requested"),
                                        (clean, "APPROVE", "Approved")):
        payload, _, raw = composed(composition, "advisory before gating")
        emitted = run(VALIDATOR, raw, "--emit-batch", "--event", event)
        assert emitted.returncode == 0, emitted.stdout
        batch = json.loads(emitted.stdout)
        assert batch["event"] == event and batch["body"].startswith(f"**{status}** — ")
        assert "(advisory)" in payload["summary"]["body"].splitlines()[0]
    print("ok gating: composed advisory payloads project to both authorized events")

    for key in ("intent", "issue_fit", "coverage"):
        for label in ("Intent", "Issue fit", "Coverage", "Reviewed", "Mode"):
            token = f"**{label}:**"
            for literal in (f"`{token}`", f"\n\n```text\n{token}\n```\n"):
                sample = base_composition()
                sample["summary"][key] += literal
                payload, _, _ = composed(sample, "summary code label")
                assert sample["summary"][key] in payload["summary"]["body"]
            sample = base_composition()
            sample["summary"][key] += f"\n\n{token} Duplicate."
            refused(sample, "field-label", "summary bare label", needle=f"summary.{key}")
    print("ok summary labels: all authored summary fields accept code literals and refuse duplicate labels")

    # Fix sites: omitted, distinct and named, distinct and unnamed, ranged, and a path needing percent-encoding.
    no_fix = base_composition()
    del no_fix["findings"][0]["fix"]
    payload, _, _ = composed(no_fix, "fix omitted")
    assert "fix=" not in payload["items"][0]["trailer"] and "fix" not in payload["items"][0]
    assert f"— anchor [`src/payments.ts:42`]({BLOB}/src/payments.ts?plain=1#L42)\n" in payload["summary"]["body"]
    unnamed = base_composition()
    unnamed["findings"][0]["change"] = "Reuse one idempotency key across every attempt."
    refused(unnamed, "fix-site", "fix site not named in change", needle="src/retry-policy.ts")
    same_file = base_composition()
    same_file["findings"][0]["change"] = "Reuse one idempotency key across every attempt."
    same_file["findings"][0]["fix"] = {"path": "src/payments.ts", "start_line": 40, "end_line": 41}
    payload, _, _ = composed(same_file, "ranged fix in the anchor's file")
    assert payload["items"][0]["fix"] == "src/payments.ts:40-41" and "fix=src/payments.ts:40-41 -->" in payload["items"][0]["trailer"]
    encoded = base_composition()
    encoded["findings"][0]["change"] = "Document the key in docs/my 100% file.md."
    encoded["findings"][0]["fix"] = {"path": "docs/my 100% file.md", "start_line": 3}
    payload, _, _ = composed(encoded, "fix path percent-encoded")
    assert payload["items"][0]["fix"] == "docs/my%20100%25%20file.md:3"
    assert f"; fix [`docs/my%20100%25%20file.md:3`]({BLOB}/docs/my%20100%25%20file.md?plain=1#L3)" in payload["summary"]["body"]
    bad = base_composition()
    bad["findings"][0]["fix"] = {"path": "src/retry-policy.ts", "start_line": 20, "end_line": 18}
    refused(bad, "fix-coordinate", "reversed fix range")
    print("ok fix sites: omitted, ranged, encoded, unnamed refused")

    # Anchors: LEFT line, deleted file, unknown provenance, missing provenance.
    left_line = base_composition()
    left_line["findings"][0]["anchor"] = {"type": "line", "path": "src/payments.ts", "start_line": 40, "end_line": 40, "side": "LEFT"}
    payload, batch, _ = composed(left_line, "LEFT line anchor")
    assert batch["comments"][0]["side"] == "LEFT"
    assert f"— anchor `src/payments.ts:40`; fix [`src/retry-policy.ts:18`]({BLOB}/src/retry-policy.ts?plain=1#L18)" in payload["summary"]["body"]
    deleted = base_composition()
    deleted["questions"][0]["anchor"] = {"type": "file", "path": "src/legacy-queue.ts", "side": "LEFT"}
    payload, batch, _ = composed(deleted, "deleted file question")
    assert f"anchor [`src/legacy-queue.ts`]({REPO}/blob/{MERGE_BASE}/src/legacy-queue.ts) (file)" in payload["summary"]["body"]
    unknown = base_composition()
    unknown["questions"][0]["anchor"] = {"type": "file", "path": "reported/path.ts", "side": "UNKNOWN"}
    payload, _, _ = composed(unknown, "UNKNOWN provenance")
    assert "\nanchor `reported/path.ts` (file)\n" in payload["summary"]["body"] and f"{BLOB}/reported" not in payload["summary"]["body"]
    legacy = base_composition()
    legacy["questions"][0]["anchor"] = {"type": "file", "path": "src/queue.ts"}
    refused(legacy, "anchor-provenance", "file anchor without side or store", needle="questions[0].anchor")
    bad = base_composition()
    bad["findings"][0]["anchor"] = {"type": "line", "path": "src/payments.ts", "start_line": 44, "end_line": 42, "side": "RIGHT"}
    refused(bad, "anchor-shape", "reversed line anchor")
    bad = base_composition()
    bad["findings"][0]["anchor"] = {"type": "file", "path": "src/payments.ts", "side": "BOTH"}
    refused(bad, "anchor-provenance", "file anchor with a bad side")
    print("ok anchors: LEFT line, deleted file, UNKNOWN, missing or malformed provenance refused")

    # The pinned manifest checks supplied anchor provenance and derives an omitted file side.
    with tempfile.TemporaryDirectory() as directory:
        store_path = Path(directory) / f"review-context-{HEAD}.json"
        repo = Path(directory) / "repo"
        repo.mkdir()

        def git(*args: str) -> str:
            result = subprocess.run(["git", "-C", str(repo), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", *args],
                                    capture_output=True, encoding="utf-8", check=True)
            return result.stdout.strip()

        git("init", "-q")
        (repo / "src").mkdir()
        for name, count in (("payments.ts", 50), ("old-queue.ts", 10), ("legacy-queue.ts", 8)):
            (repo / "src" / name).write_text("".join(f"{name} line {n}\n" for n in range(count)), encoding="utf-8")
        git("add", ".")
        git("commit", "-qm", "Add base fixtures")
        base = git("rev-parse", "HEAD")
        git("mv", "src/old-queue.ts", "src/queue.ts")
        git("rm", "src/legacy-queue.ts")
        (repo / "src/payments.ts").write_text("changed\n" * 50, encoding="utf-8")
        (repo / "src/retry-policy.ts").write_text("retry\n" * 20, encoding="utf-8")
        git("add", ".")
        git("commit", "-qm", "Modify rename delete and add fixtures")
        head = git("rev-parse", "HEAD")
        produced = subprocess.run([sys.executable, str(CONTEXT_SCRIPT), "--head", head, "--merge-base", base, "--store", str(store_path)],
                                  cwd=repo, capture_output=True, encoding="utf-8", check=False)
        assert produced.returncode == 0, (produced.stdout, produced.stderr)
        store = json.loads(store_path.read_text(encoding="utf-8"))
        assert store["context"]["head"] == head and store["context"]["merge_base"] == base
        assert {entry["status"][0] for entry in store["context"]["manifest"]} == {"A", "D", "M", "R"}

        def pinned(composition: dict) -> dict:
            value = copy.deepcopy(composition)
            for key, original, actual in (("head", HEAD, head), ("merge_base", MERGE_BASE, base), ("base_sha", BASE, base)):
                if value["run"][key] == original:
                    value["run"][key] = actual
            return value

        composed(pinned(base_composition()), "manifest agrees", "--store", str(store_path))
        composed(pinned(deleted), "manifest D entry with LEFT", "--store", str(store_path))
        renamed = base_composition()
        renamed["questions"][0]["anchor"] = {"type": "line", "path": "src/old-queue.ts", "start_line": 3, "end_line": 3, "side": "LEFT"}
        for side in ("LEFT", "RIGHT"):
            renamed["questions"][0]["anchor"]["side"] = side
            refused(pinned(renamed), "anchor-provenance", "rename pre-image path", "--store", str(store_path))
            renamed["questions"][0]["anchor"]["path"] = "src/queue.ts"
            _, batch, _ = composed(pinned(renamed), "rename manifest path", "--store", str(store_path))
            assert batch["comments"][1]["path"] == "src/queue.ts" and batch["comments"][1]["side"] == side
            renamed["questions"][0]["anchor"]["path"] = "src/old-queue.ts"
        composed(pinned(left_line), "modified LEFT line", "--store", str(store_path))
        for path, valid_side in (("src/legacy-queue.ts", "LEFT"), ("src/retry-policy.ts", "RIGHT")):
            line = base_composition()
            line["questions"][0]["anchor"] = {"type": "line", "path": path, "start_line": 3, "end_line": 3, "side": valid_side}
            composed(pinned(line), "line manifest compatible", "--store", str(store_path))
            line["questions"][0]["anchor"]["side"] = "LEFT" if valid_side == "RIGHT" else "RIGHT"
            refused(pinned(line), "anchor-provenance", "line manifest incompatible", "--store", str(store_path))
        at_head = copy.deepcopy(deleted)
        at_head["questions"][0]["anchor"]["side"] = "RIGHT"
        refused(pinned(at_head), "anchor-provenance", "deleted file marked RIGHT", "--store", str(store_path), needle="`D` entry")
        as_unknown = copy.deepcopy(deleted)
        as_unknown["questions"][0]["anchor"]["side"] = "UNKNOWN"
        composed(pinned(as_unknown), "deleted file marked UNKNOWN is the reviewer's call", "--store", str(store_path))
        undeleted = base_composition()
        undeleted["questions"][0]["anchor"]["side"] = "LEFT"
        refused(pinned(undeleted), "anchor-provenance", "present file marked LEFT", "--store", str(store_path))
        refused(pinned(unknown), "anchor-provenance", "path outside the manifest", "--store", str(store_path), needle="reported/path.ts")

        # An omitted file side is derived from the pinned manifest into the same payload an explicit side composes.
        for path, side, revision in (("src/legacy-queue.ts", "LEFT", base), ("src/payments.ts", "RIGHT", head),
                                     ("src/queue.ts", "RIGHT", head), ("src/retry-policy.ts", "RIGHT", head)):
            explicit = base_composition()
            explicit["questions"][0]["anchor"] = {"type": "file", "path": path, "side": side}
            omitted = copy.deepcopy(explicit)
            del omitted["questions"][0]["anchor"]["side"]
            expected, _, raw = composed(pinned(explicit), f"explicit {side} {path}", "--store", str(store_path))
            derived, _, derived_raw = composed(pinned(omitted), f"derived {side} {path}", "--store", str(store_path))
            assert derived_raw == raw, (path, "an omitted side composes the explicit side's bytes")
            assert derived["items"][1]["anchor"] == {"type": "file", "path": path, "side": side}, derived["items"][1]
            assert f"anchor [`{path}`]({REPO}/blob/{revision}/{path}) (file)" in derived["summary"]["body"], path
        repeated = base_composition()
        repeated["findings"][0]["anchor"] = {"type": "file", "path": "src/payments.ts"}
        repeated["findings"].append(consider(anchor={"type": "file", "path": "src/payments.ts"}, fix={"path": "src/payments.ts", "start_line": 5}))
        payload, _, _ = composed(pinned(repeated), "two omitted sides on one path", "--store", str(store_path))
        assert [item["anchor"] for item in payload["items"][:2]] == [{"type": "file", "path": "src/payments.ts", "side": "RIGHT"}] * 2
        pre_image = base_composition()
        pre_image["questions"][0]["anchor"] = {"type": "file", "path": "src/old-queue.ts"}
        refused(pinned(pre_image), "anchor-provenance", "omitted side on a rename pre-image", "--store", str(store_path),
                needle="not in the pinned merge-base manifest")
        ambiguous_store = Path(directory) / "ambiguous.json"
        ambiguous = copy.deepcopy(store)
        ambiguous["context"]["manifest"] += [{**entry, "status": "X"} for entry in store["context"]["manifest"] if entry["path"] == "src/payments.ts"]
        ambiguous["context"]["manifest"].append({"status": "U", "path": "src/conflicted.ts", "old_path": None, "insertions": "0",
                                                 "deletions": "0", "new": False, "lines": 1})
        ambiguous_store.write_text(json.dumps(ambiguous), encoding="utf-8")
        for path in ("src/payments.ts", "src/conflicted.ts"):
            unestablished = base_composition()
            unestablished["questions"][0]["anchor"] = {"type": "file", "path": path}
            refused(pinned(unestablished), "anchor-provenance", f"unestablished revision for {path}", "--store", str(ambiguous_store),
                    needle="does not establish one revision")
            unestablished["questions"][0]["anchor"]["side"] = "UNKNOWN"
            payload, _, _ = composed(pinned(unestablished), f"explicit UNKNOWN for {path}", "--store", str(ambiguous_store))
            assert f"\nanchor `{path}` (file)\n" in payload["summary"]["body"], path
        print("ok manifest derivation: deleted, present, renamed, and added file sides; unestablished revisions need an explicit side")
        stale = base_composition()
        stale["run"]["head"] = PRIOR
        refused(pinned(stale), "run-identity", "store built for another head", "--store", str(store_path))
        missing = run(COMPOSER, json.dumps(base_composition()), "--store", str(Path(directory) / "absent.json"))
        assert missing.returncode == 2 and "absent.json" in missing.stderr, missing
        for invalid in (store["context"], {**store, "format": "unknown"}, {**store, "context": []}, {**store, "context": {}}):
            store_path.write_text(json.dumps(invalid), encoding="utf-8")
            refused(pinned(base_composition()), "schema", "malformed store envelope/context", "--store", str(store_path))
    print("ok manifest: real producer store, path/side agreement, stale and malformed stores refused")

    # Stable ids: duplicates and malformed ids are refused.
    duplicate = base_composition()
    duplicate["questions"][0]["id"] = "payments/retry-idempotency"
    refused(duplicate, "stable-id", "duplicate id across finding and question")
    spaced = base_composition()
    spaced["findings"][0]["id"] = "payments/retry idempotency"
    refused(spaced, "stable-id", "id with a space")
    print("ok stable ids: duplicates and malformed ids refused")

    # Missing workflow-required issue: a complete review still emits its material question.
    required_issue = base_composition()
    required_issue["run"]["issues"] = []
    required_issue["findings"] = []
    required_issue["observations"] = []
    required_issue["summary"]["status"] = "Needs Information"
    required_issue["summary"]["issue_fit"] = "Issue alignment unavailable; the ledger came from the pull-request title and body. The repository workflow requires an originating issue."
    required_issue["questions"] = [{
        "id": "workflow/required-issue", "title": "Which originating issue applies?",
        "anchor": {"type": "file", "path": "src/queue.ts", "side": "RIGHT"},
        "evidence": "The repository workflow requires an originating issue, but none resolves from the pull-request text, supplied inputs, branch, or commits.",
        "why_it_matters": "The merge decision requires the originating issue so its acceptance criteria can be checked.",
        "answer": "The pull-request author can supply the issue; its acceptance criteria settle the required issue-alignment decision.",
    }]
    payload, batch, _ = composed(required_issue, "missing required issue")
    body = batch["body"]
    assert body.startswith("**Needs Information** — 1 open question.")
    assert "**[Question] Which originating issue applies?**" in body
    assert required_issue["summary"]["issue_fit"] in body
    assert "issues=none coverage=complete" in body and f"workflow={vr.WORKFLOW} " in body
    assert "## Coverage gaps" not in body and batch["comments"] == [] and batch["event"] == "COMMENT"
    assert payload["items"][0]["id"] == "workflow/required-issue"
    wrong = copy.deepcopy(required_issue)
    wrong["summary"]["status"] = "Incomplete"
    refused(wrong, "status-consistency", "missing required issue alone cannot be Incomplete")
    blocked = copy.deepcopy(required_issue)
    blocked["findings"] = [finding()]
    blocked["summary"]["status"] = "Changes Requested"
    _, batch, _ = composed(blocked, "required issue beside a blocker")
    assert batch["body"].startswith("**Changes Requested (advisory)** — 1 must-fix finding, 1 open question.")
    gap = copy.deepcopy(required_issue)
    gap["run"]["coverage"] = "incomplete"
    gap["summary"]["status"] = "Incomplete"
    gap["summary"]["coverage_gaps"] = ["The reviewThreads continuation failed; a missing reply could settle a prior finding."]
    _, batch, _ = composed(gap, "required issue beside a genuine coverage gap")
    assert batch["body"].startswith("**Incomplete** — 1 open question.") and "## Coverage gaps" in batch["body"]
    print("ok required issue: body question, current workflow, no-issue identity, status precedence")

    # Statuses: each of the four, with the contradictions the contract's precedence makes decidable.
    approved_with_blocker = base_composition()
    approved_with_blocker["summary"]["status"] = "Approved"
    refused(approved_with_blocker, "status-consistency", "Approved with a must-fix", needle="payments/retry-idempotency")
    changes_without_blocker = base_composition()
    changes_without_blocker["findings"] = [consider()]
    refused(changes_without_blocker, "status-consistency", "Changes Requested without a blocker")
    needs_info = base_composition()
    needs_info["findings"] = [consider()]
    needs_info["summary"]["status"] = "Needs Information"
    payload, _, _ = composed(needs_info, "Needs Information")
    assert payload["summary"]["body"].startswith("**Needs Information** — 1 optional improvement, 1 open question.")
    needs_info["questions"] = []
    refused(needs_info, "status-consistency", "Needs Information without a question")
    incomplete_marked_complete = base_composition()
    incomplete_marked_complete["findings"] = [consider()]
    incomplete_marked_complete["summary"]["status"] = "Incomplete"
    refused(incomplete_marked_complete, "status-consistency", "Incomplete with complete coverage")
    incomplete = base_composition()
    incomplete["findings"] = [consider()]
    incomplete["questions"] = []
    incomplete["run"]["coverage"] = "incomplete"
    incomplete["summary"]["status"] = "Incomplete"
    incomplete["summary"]["coverage_gaps"] = [
        "`reviewThreads` continuation 2 failed; a reply there could change `payments/retry-naming`.",
        "Verification of `payments/retry-budget` did not finish; it stays unpublished.",
    ]
    payload, batch, _ = composed(incomplete, "incomplete coverage with a verified unrelated finding")
    assert payload["summary"]["body"].startswith("**Incomplete** — 1 optional improvement.") and len(batch["comments"]) == 1
    assert "## Coverage gaps\n\n- `reviewThreads` continuation 2 failed" in payload["summary"]["body"]
    assert "coverage=incomplete -->" in payload["summary"]["trailer"]
    approved_incomplete = copy.deepcopy(incomplete)
    approved_incomplete["summary"]["status"] = "Approved"
    refused(approved_incomplete, "status-consistency", "Approved with incomplete coverage")
    del incomplete["summary"]["coverage_gaps"]
    refused(incomplete, "coverage-gaps", "incomplete coverage without a named gap")
    gaps_but_complete = base_composition()
    gaps_but_complete["summary"]["coverage_gaps"] = ["a gap"]
    refused(gaps_but_complete, "coverage-gaps", "coverage gaps with complete coverage")
    blocker_incomplete = base_composition()
    blocker_incomplete["run"]["coverage"] = "incomplete"
    blocker_incomplete["summary"]["coverage_gaps"] = ["Verification of `payments/retry-budget` did not finish."]
    payload, _, _ = composed(blocker_incomplete, "blocker takes precedence over incomplete coverage")
    assert payload["summary"]["body"].startswith("**Changes Requested (advisory)**") and "## Coverage gaps" in payload["summary"]["body"]
    print("ok statuses: all four composed, contradictions with blockers, coverage, and questions refused")

    # Re-review: prior items are accounted for in the summary only and never enter the batch; disputed blockers hold status.
    rereview = base_composition()
    rereview["run"]["prior_head"] = PRIOR
    rereview["findings"] = [consider()]
    rereview["prior_items"] = [
        {"id": "payments/retry-idempotency", "classification": "disputed", "action": "must-fix",
         "note": "declined twice; the timeout-after-commit trace still holds at `src/payments.ts:42`."},
        {"id": "payments/retry-logging", "classification": "fixed", "action": "consider",
         "note": "implemented in `9f1e0aa`; the focused test passes at the head."},
        {"id": "payments/retry-budget", "classification": "still-open", "action": "must-fix",
         "note": "the reply states intent; the head still creates a key per attempt."},
        {"id": "queue/ordering", "classification": "not-verifiable", "action": "question", "note": "no maintainer answer yet."},
    ]
    payload, batch, _ = composed(rereview, "re-review with prior items")
    body = payload["summary"]["body"]
    assert body.startswith(
        "**Changes Requested (advisory)** — 1 optional improvement, 1 open question, 2 prior items still open, 1 disputed prior finding. "
        f"Delta review of `{PRIOR[:7]}..{HEAD[:7]}`.\n"
    ), body
    assert "## Disputed\n\n- `payments/retry-idempotency` — disputed: declined twice" in body
    assert "## Settled findings\n\n- `payments/retry-logging` — fixed: implemented" in body
    assert "- `payments/retry-budget` — still-open:" in body and "- `queue/ordering` — not-verifiable:" in body
    visible, _, details = body.partition("<details>")
    assert "## Disputed" in visible and "## Prior findings" in visible
    assert "payments/retry-logging" not in visible and "payments/retry-logging" in details
    for prior in rereview["prior_items"]:
        assert body.count(f"`{prior['id']}`") == 1, prior["id"]
        assert not any(prior["id"] in comment["body"] for comment in batch["comments"]), prior["id"]
    assert len(batch["comments"]) == 1 and "payments/retry-naming" in batch["comments"][0]["body"]
    approved = copy.deepcopy(rereview)
    approved["summary"]["status"] = "Approved"
    refused(approved, "status-consistency", "Approved over a disputed prior must-fix", needle="payments/retry-budget")
    reposted = copy.deepcopy(rereview)
    reposted["findings"].append(finding(id="payments/retry-budget"))
    refused(reposted, "stable-id", "still-open prior finding re-posted as a new finding", needle="duplicate comment")
    converted = copy.deepcopy(rereview)
    converted["questions"][0]["id"] = "payments/retry-budget"
    composed(converted, "prior finding carried as a question keeps its id")
    requestion = copy.deepcopy(rereview)
    requestion["questions"][0]["id"] = "queue/ordering"
    refused(requestion, "stable-id", "open prior question re-posted as a new question")
    bad = copy.deepcopy(rereview)
    bad["prior_items"][0]["classification"] = "declined"
    refused(bad, "prior-item", "unknown prior classification")
    print("ok re-review: prior accounting in the summary only, disputed blocker holds status, duplicates refused")

    # Retrospective review of a merged target: the Mode line is mandatory and the would-be batch still emits.
    merged = base_composition()
    merged["run"]["merged"] = True
    payload, batch, _ = composed(merged, "retrospective default")
    assert vr_mode(payload) == "**Mode:** Retrospective review of merged pull request." and len(batch["comments"]) == 1
    merged["run"]["publication_authorized"] = True
    refused(merged, "schema", "publication authorization is review-code-publish's", needle="run.publication_authorized")
    absent = base_composition()
    del absent["run"]["merged"]
    refused(absent, "schema", "packet without merged", needle="run.merged")
    retired = base_composition()
    retired["run"]["context"] = CONTEXT
    refused(retired, "schema", "model-authored context digest", needle="run.context")
    for bad in ("abc", None):
        wrong = base_composition()
        wrong["run"]["packet_context"] = bad
        refused(wrong, "trailer-grammar", "pull request without a packet digest", needle="run.packet_context")
    supplied = base_composition()
    supplied["run"]["specs"] = ["https://example.com/spec"]
    refused(supplied, "trailer-grammar", "supplied spec with supplied_inputs=no", needle="run.supplied_inputs")
    supplied["run"]["supplied_inputs"] = "yes"
    payload, _, _ = composed(supplied, "supplied spec on a pull request")
    assert f"packet_context={CONTEXT} supplied_inputs=yes " in payload["summary"]["trailer"]
    print("ok retrospective and identity: plain Mode line, retired inputs refused, packet identity in the trailer")

    # File fallback: re-anchoring a rejected line comment on its file moves the complete prose into the body.
    fallback = base_composition()
    fallback["findings"][0]["anchor"] = {"type": "file", "path": "src/payments.ts", "side": "RIGHT"}
    payload, batch, _ = composed(fallback, "file fallback")
    body = payload["summary"]["body"]
    file_fragment = f"anchor [`src/payments.ts`]({BLOB}/src/payments.ts) (file); fix [`src/retry-policy.ts:18`]({BLOB}/src/retry-policy.ts?plain=1#L18)"
    assert body.count("Preserve the idempotency key across retries") == 1
    assert "## Findings" not in body and f"## Unanchored findings\n\n{vr_note()}\n\n**[P1] [must-fix]" in body
    assert body.count(file_fragment) == 1 and batch["comments"] == []
    assert "— 1 must-fix finding, 1 open question." in body
    print("ok file fallback: body-carried finding with prose, trailer, and fragment once")

    # Ambiguities and issue coordinates render mechanically.
    ambiguous = base_composition()
    ambiguous["run"]["issues"] = ["acme/payments#9", "acme/payments#123"]
    ambiguous["summary"]["ambiguities"] = [
        {"term": "released contract", "readings": ["the tagged release", "the default branch"], "applied": "reading (a), the safer one."}
    ]
    payload, _, _ = composed(ambiguous, "ambiguities and issues")
    assert "## Ambiguities\n\n- **released contract** — (a) the tagged release; (b) the default branch. Applied: reading (a), the safer one." in payload["summary"]["body"]
    assert "issues=acme/payments#123,acme/payments#9 " in payload["summary"]["trailer"]
    none = base_composition()
    none["run"]["issues"] = []
    payload, _, _ = composed(none, "no issues")
    assert "issues=none " in payload["summary"]["trailer"]
    plain = base_composition()
    del plain["run"]["repository_url"]
    result = run(COMPOSER, json.dumps(plain))
    assert result.returncode == 0, result.stdout
    plain_payload = json.loads(result.stdout)
    assert "repository_url" not in plain_payload["summary"] and "anchor `src/payments.ts:42`; fix `src/retry-policy.ts:18`" in plain_payload["summary"]["body"]
    assert run(VALIDATOR, result.stdout).returncode == 0
    print("ok summary: ambiguities, sorted issues, none, code-span fallback without repository_url")

    unreadable = run(COMPOSER, "{not json")
    assert unreadable.returncode == 2 and "render_review" in unreadable.stderr, unreadable
    not_object = run(COMPOSER, "[]")
    assert not_object.returncode == 1 and "schema" in not_object.stdout, not_object
    print("ok input: unreadable input exits 2, non-object exits 1")
    local_targets()
    record_accounting()
    shown = subprocess.run([sys.executable, str(SCRIPT), "--example"], capture_output=True, encoding="utf-8", check=False)
    assert shown.returncode == 0 and shown.stderr == "", ("example", shown.stderr)
    value = json.loads(shown.stdout)
    # The example is what the reviewer writes; the finalizer fills the rest, and test_render_review.py finalizes it.
    assert not {"head", "context", "packet_context", "supplied_inputs"} & set(value["run"]), "derived run fields are omitted"
    assert all(set(b) == {"bundle", "accounting", "operation"} for b in value["record"]["verification"]["batches"])
    assert "allowance" not in value["record"]["verification"], "the finalizer derives the spent allowance"
    assert run(COMPOSER, shown.stdout).returncode == 1, "run alone, the composer requires every field"
    print("ok example: --example prints the authored composition, which the composer alone refuses")
    return 0


def vr_mode(payload: dict) -> str:
    return payload["summary"]["body"].split("\n\n")[1]


def vr_note() -> str:
    return "The forge's review batch cannot carry a file subject, so each finding below carries its complete prose here."


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"FAIL {error}")
        raise SystemExit(1)
    except subprocess.CalledProcessError as error:
        print(f"test_render_composition: {error.cmd} failed: {error.stderr}", file=sys.stderr)
        raise SystemExit(2)
    except OSError as error:
        print(f"test_render_composition: cannot run {SCRIPT}: {error}", file=sys.stderr)
        raise SystemExit(2)
