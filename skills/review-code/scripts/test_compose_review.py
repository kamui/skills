#!/usr/bin/env python3
"""Exercise compose_review.py through its CLI: composition, refusal, and batch agreement.

Usage: python3 scripts/test_compose_review.py
Inputs: local fixture compositions and a disposable Git repository; no forge access.
Exit 0: all checks pass; exit 1: a check fails; exit 2: the CLI cannot run.

Every fixture composes a payload, validates it with validate_review.py, and
projects it with --emit-batch, so the three scripts are checked in agreement.
Refusal fixtures assert the rule name and that no payload is printed.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import validate_review as vr

COMPOSER = Path(__file__).with_name("compose_review.py")
VALIDATOR = Path(__file__).with_name("validate_review.py")
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


def run(script: Path, stdin: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args], input=stdin, capture_output=True, encoding="utf-8", check=False
    )


def base_composition() -> dict:
    """The output contract's example review as a composition input."""
    return {
        "run": {
            "head": HEAD, "base_ref": "main", "base_sha": BASE, "merge_base": MERGE_BASE, "context": CONTEXT,
            "issues": ["acme/payments#123"], "coverage": "complete", "repository_url": REPO, "merged": False,
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
        value["run"].update(target_kind=kind, target="main..HEAD", tree="e" * 40,
                            change_description="Keep the key", specs=["spec/retries"])
        value["findings"][0]["source"] = 'commit-abcdef0/"Keep the key"'
        value["findings"][0]["anchor"]["side"] = "LEFT"
        result = run(COMPOSER, json.dumps(value))
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(result.stdout)
        body = payload["summary"]["body"]
        assert "repository_url" not in payload["summary"] and "](http" not in body, body
        assert "anchor `src/payments.ts:42`; fix `src/retry-policy.ts:18`" in body, body
        assert "anchor `src/queue.ts (file)`" in body, body
        assert '**Source:** commit-abcdef0/"Keep the key"' in payload["items"][0]["markdown"]
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
        value["run"].update(issues=[], specs=[], change_description="")
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
                         "context": CONTEXT, "issues": [], "coverage": "complete", "merged": False,
                         "change_description": ""},
                 "summary": {"status": "Approved", "intent": "Edit file.",
                             "issue_fit": "Issue alignment unavailable; no stated promises.",
                             "coverage": "Complete working-tree diff inspected."}}
        result = run(COMPOSER, json.dumps(value), "--store", str(store))
        assert result.returncode == 0, result.stdout + result.stderr
        value["run"]["tree"] = "0" * 40
        refused(value, "run-identity", "snapshot tree/store mismatch", "--store", str(store))
    print("ok local targets: identity, source kinds, code spans, and unchanged pull-request fixture")


def batch_paths(name: str) -> dict:
    return {"name": name, "bundle": f"/tmp/x/{name}", "raw_return": f"/tmp/x/{name}/raw-return.json",
            "accounting": f"/tmp/x/{name}/accounting.json", "operation": "Agent run_in_background=false"}


def gate_composition() -> dict:
    """The contract example as a committed local range with the private record's accounting."""
    value = base_composition()
    value["run"].pop("repository_url")
    value["run"].update(target_kind="range", target="main..HEAD", change_description="Keep the key", specs=["spec/retries"])
    value["record"] = {
        "repository": "/repo",
        "paths": {"private_dir": "/tmp/x", "store": f"/tmp/x/review-context-{HEAD}.json", "composition": "/tmp/x/composition.json",
                  "addenda": "/tmp/x/addenda", "evidence_packet": "/tmp/x/evidence.md"},
        "ledger": {
            "requirements": [{"source": "issue-123/acceptance-criterion-2", "class": "acceptance", "disposition": "partial",
                              "evidence": "src/payments.ts:42 creates a key per attempt"}],
            "candidates": [
                {"id": "payments/retry-idempotency", "kind": "requirement", "disposition": "survivor",
                 "verification": "independent-confirmed", "evidence": "src/payments.ts:42"},
                {"id": "queue/retry-order", "kind": "bug", "disposition": "question", "evidence": "src/queue.ts:5"},
                {"id": "payments/retry-budget", "kind": "maintainability", "disposition": "dropped", "evidence": "src/retry-policy.ts:20"},
            ],
        },
        "files": [{"path": "src/payments.ts", "state": "reviewed"}, {"path": "src/retry-policy.ts", "state": "reviewed"},
                  {"path": "src/queue.ts", "state": "reviewed"}, {"path": "docs/notes.md", "state": "ignored", "reason": "generated"}],
        "check_evidence": [
            {"check": "python3 scripts/test_retry.py", "head": HEAD, "outcome": "accepted", "reason": "same command, clean tree, output read"},
            {"check": "python3 scripts/test_queue.py", "head": PRIOR, "outcome": "historical", "reason": "the delta reaches none of its inputs"},
            {"check": "python3 scripts/test_payments.py", "head": HEAD, "outcome": "reviewer-executed", "reason": "the fixture changed since the supplied run"},
        ],
        "verification": {"batches": [batch_paths("initial")], "follow_up_spent": False, "clean_verdict": "not-required", "outstanding": []},
        "routed": {"unresolved": [], "disputed": [], "unrecoverable_inputs": []},
    }
    return value


def gate(composition: dict, name: str, *args: str) -> tuple[dict, str]:
    result = run(COMPOSER, json.dumps(composition), "--profile", "implementation-gate", *args)
    assert result.returncode == 0, (name, result.returncode, result.stdout, result.stderr)
    record = json.loads(result.stdout)
    assert record["schema"] == "implementation-gate-record/1" and record["profile"] == "implementation-gate", name
    assert record["workflow"] == vr.WORKFLOW and record["run"]["head"] == composition["run"]["head"], name
    assert record["run"]["target"] == composition["run"]["target"] and record["run"]["repository"] == composition["record"]["repository"], name
    assert run(VALIDATOR, result.stdout).returncode == 0, name  # the record is a superset of the validator payload
    return record, result.stdout


def implementation_gate() -> None:
    # The same authoritative fixture through both profiles: identical findings, questions, status, coverage, ids, and accounting.
    composition = gate_composition()
    plain = copy.deepcopy(composition)
    plain.pop("record")
    payload = json.loads(run(COMPOSER, json.dumps(plain)).stdout)
    assert run(COMPOSER, json.dumps(composition)).stdout == run(COMPOSER, json.dumps(plain)).stdout, "publishable output is unchanged by a record section"
    record, stdout = gate(composition, "gate fixture")
    assert record["summary"] == payload["summary"] and record["items"] == payload["items"], "profiles render the same review"
    assert record["status"] == "Changes Requested" and record["run"]["coverage"] == "complete"
    assert [item["id"] for item in record["items"] if item["type"] != "observation"] == ["payments/retry-idempotency", "queue/retry-order"]
    assert record["record"]["verification"] == composition["record"]["verification"], "verification accounting is carried as given"
    assert [e["outcome"] for e in record["record"]["check_evidence"]] == ["accepted", "historical", "reviewer-executed"], "reused evidence keeps its outcomes"
    assert record["record"]["paths"]["addenda"] == "/tmp/x/addenda" and record["run"]["issues"] == ["acme/payments#123"]
    assert run(COMPOSER, json.dumps(composition), "--profile", "implementation-gate").stdout == stdout, "record composition is deterministic"
    print("ok implementation-gate: same review as publishable, validator-readable record, accounting carried")

    # Both profiles reject equivalent semantic contradictions with the same lines.
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
        ("verification", mutate(**{"record.verification.follow_up_spent": True})),
        ("verification", mutate(**{"record.verification.batches": [batch_paths("a"), batch_paths("b"), batch_paths("c")]})),
        ("verification", mutate(**{"record.verification.batches": [], "record.verification.clean_verdict": "stands"})),
        ("verification", mutate(**{"record.verification.batches": []})),
        ("coverage-gaps", mutate(**{"record.verification.outstanding": ["clean-verdict attack over the complete ledger"]})),
        ("coverage-gaps", mutate(**{"record.files.0.state": "unreviewed"})),
        ("file-accounting", mutate(**{"record.files.1.path": "src/payments.ts"})),
        ("schema", mutate(**{"record.files.3.reason": None})),
        ("ledger", mutate(**{"record.ledger.candidates.0.id": "payments/other"})),
        ("ledger", mutate(**{"record.ledger.candidates.2.disposition": "survivor"})),
        ("ledger", mutate(**{"record.ledger.candidates.1.disposition": "survivor"})),
        ("ledger", mutate(**{"record.ledger.candidates.0.kind": "maintainability"})),
        ("ledger", mutate(**{"record.ledger.requirements.0.class": "wish"})),
        ("verification", mutate(**{"record.ledger.candidates.0.verification": "primary-confirmed"})),
        ("stable-id", mutate(**{"record.routed.unresolved": ["payments/unknown"]})),
        ("coverage-gaps", mutate(**{"record.routed.unrecoverable_inputs": ["the spec's benchmark artifact"]})),
        ("record-paths", mutate(**{"record.paths.addenda": None})),
        ("record-paths", mutate(**{"record.paths.store": "relative/store.json"})),
        ("schema", mutate(**{"record.verification": None})),
    ]
    for rule, bad in contradictions:
        publishable = refused(bad, rule, f"publishable rejects {rule}")
        gated = refused(bad, rule, f"implementation-gate rejects {rule}", "--profile", "implementation-gate")
        assert publishable == gated, (rule, publishable, gated)
    for name, bad in (("worktree", mutate(**{"run.target_kind": "worktree", "run.tree": "e" * 40})),
                      ("pull-request", mutate(**{"run.target_kind": "pull-request", "run.merged": False})),
                      ("prior head", mutate(**{"run.prior_head": PRIOR})),
                      ("missing record", plain)):
        refused(bad, "profile", f"implementation-gate refuses {name}", "--profile", "implementation-gate")
    print("ok implementation-gate: both profiles refuse the same contradictions; profile-only refusals named")

    # Outcomes: clean, material question, and incomplete with an exhausted follow-up allowance; blocking is the fixture above.
    clean = mutate(**{"findings": [], "questions": [], "observations": [], "summary.status": "Approved",
                      "record.verification.clean_verdict": "stands"})
    clean["record"]["ledger"]["candidates"] = [{"id": "payments/retry-budget", "kind": "maintainability", "disposition": "dropped", "evidence": "src/retry-policy.ts:20"}]
    record, _ = gate(clean, "clean outcome")
    assert record["status"] == "Approved" and record["summary"]["body"].startswith("**Approved (advisory)** — no findings.")
    refused(mutate(**{"findings": [], "questions": [], "observations": [], "summary.status": "Approved",
                      "record.ledger.candidates": clean["record"]["ledger"]["candidates"]}),
            "verification", "clean review without a clean-verdict attack", "--profile", "implementation-gate",
            needle="clean_verdict")
    hygiene = mutate(**{"findings": [consider()], "questions": [], "observations": [], "summary.status": "Approved"})
    hygiene["record"]["ledger"]["candidates"] = [{"id": "payments/retry-naming", "kind": "maintainability", "disposition": "survivor",
                                                  "verification": "primary-confirmed", "evidence": "src/payments.ts:50"}]
    refused(hygiene, "verification", "surviving hygiene switches nothing off", "--profile", "implementation-gate", needle="clean_verdict")
    hygiene["record"]["verification"]["clean_verdict"] = "stands"
    record, _ = gate(hygiene, "hygiene survivor with clean verdict")
    assert "1 consider finding" in record["summary"]["body"]
    # A surviving compatibility consider is material, and so is a survivor the reviewer marks material under another kind.
    compatibility = mutate(**{"findings": [consider(kind="compatibility")], "questions": [], "observations": [], "summary.status": "Approved"})
    compatibility["record"]["ledger"]["candidates"] = [{"id": "payments/retry-naming", "kind": "compatibility", "disposition": "survivor",
                                                        "verification": "independent-confirmed", "evidence": "src/payments.ts:50"}]
    gate(compatibility, "compatibility consider is material; not-required composes")
    marked = copy.deepcopy(hygiene)
    marked["record"]["verification"]["clean_verdict"] = "not-required"
    marked["record"]["ledger"]["candidates"][0]["material"] = True
    gate(marked, "reviewer-marked material survivor; not-required composes")
    marked["record"]["ledger"]["candidates"][0]["material"] = "yes"
    refused(marked, "schema", "material must be boolean", "--profile", "implementation-gate", needle="material")
    # A malformed row is reported and skipped, and a later row's violation still names its own input index.
    shifted = mutate(**{"record.ledger.requirements": [{"source": "issue-123/criterion-1"},
                                                       {"source": "issue-123/criterion-2", "class": "wish", "disposition": "met", "evidence": "x:1"}]})
    refused(shifted, "ledger", "violation at the input index", "--profile", "implementation-gate", needle="record.ledger.requirements[1]: ledger")
    question = mutate(**{"findings": [], "observations": [], "summary.status": "Needs Information", "record.verification.clean_verdict": "stands"})
    question["record"]["ledger"]["candidates"] = composition["record"]["ledger"]["candidates"][1:]
    record, _ = gate(question, "material question outcome")
    assert record["status"] == "Needs Information" and record["items"][0]["type"] == "question"
    incomplete = mutate(**{"findings": [], "questions": [], "observations": [], "summary.status": "Incomplete", "run.coverage": "incomplete",
                           "summary.coverage_gaps": ["clean-verdict attack over the complete ledger: follow-up batch spent"],
                           "record.verification.batches": [batch_paths("initial"), batch_paths("follow-up")],
                           "record.verification.follow_up_spent": True, "record.verification.clean_verdict": "outstanding",
                           "record.verification.outstanding": ["clean-verdict attack over the complete updated ledger"]})
    incomplete["record"]["ledger"]["candidates"] = clean["record"]["ledger"]["candidates"]
    record, _ = gate(incomplete, "incomplete after exhausted follow-up")
    assert record["status"] == "Incomplete" and record["record"]["verification"]["follow_up_spent"] is True
    refused(mutate(**{"record.verification.batches": [batch_paths("initial"), batch_paths("follow-up")]}),
            "verification", "two batches with follow-up unspent", "--profile", "implementation-gate", needle="follow_up_spent")
    print("ok implementation-gate: clean, blocking, material-question, and incomplete outcomes; exhausted follow-up")

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
        line = refused(value, "file-accounting", "manifest path without accounting", "--profile", "implementation-gate", "--store", str(store), needle="kept.txt")
        assert line == refused(value, "file-accounting", "publishable manifest accounting", "--store", str(store))
        value["record"]["files"].append({"path": "kept.txt", "state": "reviewed"})
        value["record"]["files"].append({"path": "old.txt", "state": "reviewed"})
        refused(value, "file-accounting", "pre-image path is not a manifest path", "--profile", "implementation-gate", "--store", str(store), needle="old.txt")
        value["record"]["files"].pop()
        value["findings"][0]["anchor"]["side"] = "RIGHT"
        refused(value, "anchor-provenance", "deleted file on the RIGHT", "--profile", "implementation-gate", "--store", str(store))
    print("ok implementation-gate: deleted and renamed evidence, file accounting against the pinned manifest")


def main() -> int:
    # Ordinary finding, whole-change question, observation: the contract example, byte for byte where the contract renders it.
    contract = base_composition()
    payload, batch, stdout = composed(contract, "contract example")
    body = payload["summary"]["body"]
    assert body.startswith("**Changes Requested (advisory)** — 1 must-fix finding, 1 open question.\n\n**Intent:**"), body
    assert f"## Findings\n\n- [P1] [must-fix] Preserve the idempotency key across retries — {FINDING_FRAGMENT}\n\n" in body
    assert f"## Open questions\n\n- [Question] Must retries preserve request order? — {QUESTION_FRAGMENT}\n\n**[Question]" in body
    assert "## Observations\n\n- The first configuration sentence" in body
    assert f"**Reviewed:** `{HEAD[:7]}` against merge-base `{MERGE_BASE[:7]}`." in body
    assert payload["items"][0]["markdown"] == vr.FINDING_MARKDOWN and payload["items"][1]["markdown"] == vr.QUESTION_MARKDOWN
    assert payload["items"][0]["trailer"] == vr.valid_payload()["items"][0]["trailer"]
    assert payload["summary"]["trailer"] == vr.RUN_TRAILER
    assert batch["comments"][0]["path"] == "src/payments.ts" and batch["comments"][0]["line"] == 42
    rendered = run(VALIDATOR, stdout, "--render")
    assert rendered.stdout == f"{FINDING_FRAGMENT}\n{QUESTION_FRAGMENT}\n", rendered.stdout
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
    assert item["markdown"].endswith(f"**Source:** Issue #123, acceptance criterion 2.\n\n{vr.PERMISSION_SENTENCE}"), item["markdown"]
    assert item["trailer"].endswith("blocking=false kind=maintainability -->") and len(batch["comments"]) == 2
    shared = base_composition()
    shared["findings"].append(consider(anchor=finding()["anchor"], fix=finding()["fix"], change=finding()["change"]))
    refused(shared, "summary-reference", "two findings sharing one anchor and fix", needle="findings[1]")
    assert "— 1 must-fix finding, 1 consider finding, 1 open question." in payload["summary"]["body"]
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
    assert suggestion["findings"][0]["change"] in payload["items"][0]["markdown"]
    assert suggestion["findings"][0]["change"] in batch["comments"][0]["body"]
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
    assert "— anchor `reported/path.ts` (file)\n" in payload["summary"]["body"] and f"{BLOB}/reported" not in payload["summary"]["body"]
    legacy = base_composition()
    legacy["questions"][0]["anchor"] = {"type": "file", "path": "src/queue.ts"}
    refused(legacy, "anchor-provenance", "file anchor without side", needle="questions[0].anchor")
    bad = base_composition()
    bad["findings"][0]["anchor"] = {"type": "line", "path": "src/payments.ts", "start_line": 44, "end_line": 42, "side": "RIGHT"}
    refused(bad, "anchor-shape", "reversed line anchor")
    bad = base_composition()
    bad["findings"][0]["anchor"] = {"type": "file", "path": "src/payments.ts", "side": "BOTH"}
    refused(bad, "anchor-provenance", "file anchor with a bad side")
    print("ok anchors: LEFT line, deleted file, UNKNOWN, missing or malformed provenance refused")

    # The pinned manifest checks anchor provenance without deciding it.
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
    assert "issues=none coverage=complete" in body and "workflow=v5b-21" in body
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
    assert payload["summary"]["body"].startswith("**Needs Information** — 1 consider finding, 1 open question.")
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
    assert payload["summary"]["body"].startswith("**Incomplete** — 1 consider finding.") and len(batch["comments"]) == 1
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
        "**Changes Requested (advisory)** — 1 consider finding, 1 open question, 2 prior items still open, 1 disputed prior finding. "
        f"Delta review of `{PRIOR[:7]}..{HEAD[:7]}`.\n"
    ), body
    assert "## Disputed\n\n- `payments/retry-idempotency` — disputed: declined twice" in body
    assert "## Prior findings\n\n- `payments/retry-logging` — fixed: implemented" in body
    assert "- `payments/retry-budget` — still-open:" in body and "- `queue/ordering` — not-verifiable:" in body
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
    assert vr_mode(payload) == "**Mode:** Retrospective review of merged pull request; publication disabled." and len(batch["comments"]) == 1
    merged["run"]["publication_authorized"] = True
    payload, _, _ = composed(merged, "retrospective authorized")
    assert vr_mode(payload) == "**Mode:** Retrospective review of merged pull request; publication separately authorized."
    absent = base_composition()
    del absent["run"]["merged"]
    refused(absent, "schema", "packet without merged", needle="run.merged")
    print("ok retrospective: Mode line follows merged and authorization, missing merged refused")

    # File fallback: re-anchoring a rejected line comment on its file moves the complete prose into the body.
    fallback = base_composition()
    fallback["findings"][0]["anchor"] = {"type": "file", "path": "src/payments.ts", "side": "RIGHT"}
    payload, batch, _ = composed(fallback, "file fallback")
    body = payload["summary"]["body"]
    file_fragment = f"anchor [`src/payments.ts`]({BLOB}/src/payments.ts) (file); fix [`src/retry-policy.ts:18`]({BLOB}/src/retry-policy.ts?plain=1#L18)"
    assert "## Findings" not in body and f"## Unanchored findings\n\n{vr_note()}\n\n- [P1] [must-fix] Preserve the idempotency key across retries — {file_fragment}\n\n**[P1] [must-fix]" in body
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
    assert unreadable.returncode == 2 and "compose_review" in unreadable.stderr, unreadable
    not_object = run(COMPOSER, "[]")
    assert not_object.returncode == 1 and "schema" in not_object.stdout, not_object
    print("ok input: unreadable input exits 2, non-object exits 1")
    local_targets()
    implementation_gate()
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
        print(f"test_compose_review: {error.cmd} failed: {error.stderr}", file=sys.stderr)
        raise SystemExit(2)
    except OSError as error:
        print(f"test_compose_review: cannot run {COMPOSER}: {error}", file=sys.stderr)
        raise SystemExit(2)
