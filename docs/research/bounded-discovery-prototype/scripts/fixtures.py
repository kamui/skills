#!/usr/bin/env python3
"""Build a disposable, unpaid synthetic config and scripted worker reports.

Usage: python3 scripts/fixtures.py --out NEW_DIR --case CASE [--arm A|B|C]
Input: named paper/routing scenario from DESIGN.md; no real target selection.
Output: config.json, scenario.json, synthetic ledger, permitted clone and canaries.
Exit: 0 success, 1 invalid content, 2 failed read/helper or existing destination.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from adapter import HERE, POLICY, REPO, SCHEMA, TREE, artifact, write
from budget import now


CASES = ("empty", "primary", "finder", "duplicate", "outside", "clean", "hygiene", "hygiene-required",
         "missing-dispatch", "missing-ruling", "generic", "concrete", "unavailable", "unknown", "not-inspected",
         "refuted", "unresolved", "late-row", "spent-follow-up", "scope-dispute", "missing-finder", "malformed", "timeout")


def response(report):
    return dict(report=deepcopy(report))


def no_batch(phase, claims, rows, reason="no-eligible-trigger"):
    return dict(dispatch=False, phase=phase, baseline_clause="#136 conditional verification",
                evidence="Explicit synthetic primary trigger decision", reason=reason,
                survivor_ids=[c["id"] for c in claims if c["admission"]["disposition"] == "survives"],
                affected_row_ids=[r["id"] for r in rows],
                triggers=dict(candidate=False, related=False, zero_survivor=False, high_risk=bool(rows)))


def batch(mode, candidates, rows):
    return dict(dispatch=True, mode=mode, candidate_ids=candidates, row_ids=rows,
                baseline_clause="#136 candidate / zero-survivor / late-related rule",
                trigger_evidence="Explicit synthetic primary eligibility decision")


def make(root, case, arm="C"):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    common = root / "inputs"
    clone = common / "clone"
    clone.mkdir(parents=True)
    write(clone / "queue.rs", b"fn idle() {}\nfn wake() {}\nfn outside() {}\n")
    write(clone / "concrete.ts", b"type A = {a: string};\ntype B = {b: number};\ntype Pair = A & B;\n")
    write(clone / "tests/unused.rs", b"// synthetic unused helper\n")
    write(clone / "docs/examples.md", b"Synthetic example text.\n")
    refs = {}
    for name in ("pr", "spec", "rules", "diff", "manifest", "ranges", "dependencies", "execution_policy"):
        refs[name + "_ref"] = write(common / (name + ".txt"), ("Legitimate synthetic common " + name + "\n").encode("utf-8"), "reviewer-common")
    source = dict(schema_version=SCHEMA, packet_id="toy-common", repository="fixture/queue", pr=1,
                  repository_url="https://github.com/fixture/queue", state="OPEN", merged=False,
                  posting_identity="fixture-owner", review_identity="fixture-owner", base_ref="main",
                  base_oid="1" * 40, head_oid="2" * 40, merge_base_oid="1" * 40,
                  cutoff=now(), permitted_history="offline fixture has no git history", content="Synthetic queue change",
                  provenance=dict(complete=True, origin="common-preparation", contains_arm_output=False), **refs)
    source_ref = write(common / "source.json", source, "reviewer-common")
    target = write(common / "target.json", {k: source[k] for k in ("repository", "pr", "base_oid", "head_oid", "merge_base_oid")}, "reviewer-common")
    scope = write(common / "scope.json", dict(scope_id="toy-scope", source_hash=source_ref["sha256"],
                  selection_mode="mechanical", selector_context="toy-selector", alternatives=["queue.rs:idle"],
                  rationale="First supported fixture progress surface", citations=["queue.rs:1"], max_hops=2,
                  roots=[dict(path="queue.rs", symbol="idle", start=1, end=1)], frontier=[], exclusions=["queue.rs:3"],
                  frozen_at=now()))
    helpers = {}
    command = ["git", "show", POLICY + ":skills/code-review-publish/scripts/validate_review.py"]
    result = subprocess.run(command, cwd=REPO, capture_output=True)
    if result.returncode:
        raise OSError("git show pinned validator failed: " + result.stderr.decode("utf-8"))
    helpers["validate_review"] = write(common / "helpers" / "validate_review.py", result.stdout)
    for name in ("transcript_usage", "agent_effort"):
        helpers[name] = artifact(HERE.parents[1] / "tools" / (name + ".py"))
    ledger = json.loads((HERE.parent / "ledger.json").read_text(encoding="utf-8"))
    ledger.update(synthetic=True, frozen_total_cap_usd="100", grading_closeout_reserve_usd="10")
    write(root / "ledger.json", ledger)
    task = write(common / "verifier-task.txt", b"Synthetic verifier task. Rule on supplied IDs from raw evidence.\n")
    primary = dict(model="fixture-primary", effort="high", permissions="finite-read-tools")
    stronger = dict(model="fixture-worker", effort="high", permissions="finite-read-tools")
    contexts = {role: "toy-" + role for role in ("primary", "initial-verifier", "follow-up-verifier")}
    if arm == "C":
        contexts["finder"] = "toy-finder"
    config = dict(schema_version=SCHEMA, experiment_id="issue-138-synthetic", arm=arm, replicate=1,
                  attempt_id="toy-attempt", predecessor=None, replacement_ordinal=0,
                  policy_commit=POLICY, skill_tree=TREE, source=source_ref, scope=scope, target=target,
                  method=artifact(HERE.parents[1] / "code-review-one-shot-method.md"),
                  design=artifact(HERE.parent / "DESIGN.md"), prototype=artifact(HERE / "adapter.py"),
                  prototype_files={name: artifact(HERE / name) for name in ("adapter.py", "budget.py", "fake_worker.py")},
                  primary_task=write(common / "primary-task.txt", b"Synthetic common primary policy task.\n"),
                  verifier_task=task, verifier_tasks={a: task for a in "ABC"},
                  primary_config=primary, workers={"A": primary, "B": stronger, "C": stronger},
                  finder_config=stronger if arm == "C" else None,
                  finder_task=write(common / "finder-task.txt", b"Synthetic bounded discovery task.\n") if arm == "C" else None,
                  contexts=contexts, clone_root=str(clone), permitted_input_roots=[
                      str(common), str(HERE.parents[1] / "tools"), str(HERE),
                      str(HERE.parent / "DESIGN.md"), str(HERE.parents[1] / "code-review-one-shot-method.md"),
                      str(HERE.parents[1] / "one-shot-qualification-2026-09-07/j-trpc-5017/j-bea6be14-seed2-att-12-run.md")],
                  helpers=helpers, ledger=str(root / "ledger.json"), isolation="finite-fake-tools",
                  session_shape="fresh workers, primary continuation", cache_policy="synthetic known tiers",
                  ordered_cells=[f"slot-{slot}-{a}-replicate-{rep}" for slot in range(1, 5) for a in "ABC" for rep in (1, 2)],
                  cell_id=f"slot-1-{arm}-replicate-1", completion_mode="render-only",
                  limits=dict(attempt_usd="8", request_usd="0.50", headroom_usd="0.05", requests=12,
                              tokens=12000, finder_tokens=2000, tokens_per_request=1000,
                              commands=30, wall_seconds=30, worker_seconds=5, finder_seconds=5),
                  rates=dict(input="2", output="10", cache_write_5m="1.25", cache_write_1h="2", cache_read="0.1",
                             observed_at=now(), evidence="Synthetic rates for arithmetic tests; not provider prices"))
    ev = dict(artifact=refs["diff_ref"], locator="fixture://queue.rs:1", observed_at=now(),
              availability="inspected", reason="Explicit synthetic tool read")

    def claim(cid, origin="primary", rejected=False, optional=False):
        roles = ["primary", "finder"] if origin == "both" else [origin]
        result = dict(id=cid, canonical_id=cid, origin=origin, sources=[dict(id=cid, role=r, freeze_id="toy-" + r + "-discovery") for r in roles],
                    dedup_decision="Fixture author explicitly identifies these source IDs", kind="bug",
                    claim="The idle worker can miss a wake", trigger="A wake arrives during the idle transition",
                    impact="The queued work remains idle", change="Check pending work under the queue lock",
                    anchor="queue.rs:1", fix="queue.rs:1", citations=["queue.rs:1"], requirements=["fixture requirement 1"],
                    support="PRIVATE SUPPORT MUST NOT ENTER VERIFIER PACKET", inspected_evidence=[deepcopy(ev)],
                    admission=dict(disposition="rejected" if rejected else "survives", original_text="Rejected after caller read" if rejected else "Admit this claim",
                                   evidence="fixture primary disposition", at_phase="admission"),
                    safety_premise="The idle worker cannot miss the wake", asserted_scope="Idle transition under queue lock",
                    disposition_evidence="fixture primary safety explanation",
                    verification=dict(required=not rejected and not optional, required_batches=[] if rejected or optional else ["initial"],
                                      trigger_evidence="Explicit pinned-policy fixture decision", supplied_batch_ids=[], rulings=[],
                                      disposition="not-required-policy" if rejected or optional else "pending"),
                    publication=dict(disposition="not-admitted" if rejected else "pending", payload_item_id=cid, evidence="fixture output decision"))
        if optional:
            result.update(kind="maintainability", claim="The fixture contains an unused helper",
                          trigger="A reader follows the declared test helper", impact="Dead setup obscures the exercised cases",
                          change="Remove the unused helper")
        return result

    def row(rid, required=None):
        return dict(id=rid, kind="concurrency", surface="queue.rs:1", safety_premise="Idle worker cannot miss wake",
                    asserted_scope="Idle transition under queue lock", inspected_evidence=[deepcopy(ev)],
                    disposition_evidence="Explicit fixture acquittal", triggers={"zero_survivor": bool(required)},
                    required_batches=required or [], received_batches=[], rulings=[],
                    fidelity="mandatory" if required else "policy-permitted-omission")

    claims, rows = [], []
    if case not in ("empty", "clean", "missing-finder", "malformed", "timeout"):
        claims = [claim("C1", "finder" if case == "finder" else "both" if case == "duplicate" else "primary")]
    if case == "outside":
        claims[0].update(anchor="queue.rs:3", fix="queue.rs:3", citations=["queue.rs:3"])
    if case.startswith("hygiene") or case in ("missing-dispatch", "missing-ruling"):
        claims = [claim("H1", optional=True), claim("H2", optional=True)]
        rows = [row("Q1")]
        for c in claims:
            c["kind"] = "maintainability"
        claims[0].update(anchor="tests/unused.rs:1", fix="tests/unused.rs:1", citations=["tests/unused.rs:1"])
        claims[1].update(anchor="docs/examples.md:1", fix="docs/examples.md:1", citations=["docs/examples.md:1"])
        claims[1].update(claim="The example repeats its introductory sentence", trigger="A reader follows the example",
                         impact="The duplicate sentence makes the example longer", change="Remove the repeated sentence")
        if case != "hygiene":
            claims[0]["verification"].update(required=True, required_batches=["initial"], disposition="pending")
            claims[0].update(kind="bug", claim="The active fixture assertion expects the wrong value",
                             trigger="CI executes the changed assertion", impact="The suite fails",
                             change="Correct the assertion's expected value")
            rows = [row("Q1", ["initial"])]
            rows[0]["surface"] = "tests/unused.rs:1"
    if case in ("generic", "concrete", "unavailable", "unknown", "not-inspected"):
        claims = [claim("H1", optional=True), claim("T1" if case != "concrete" else "T2", rejected=True)]
        claims[0].update(kind="maintainability", anchor="tests/unused.rs:1", fix="tests/unused.rs:1",
                         citations=["tests/unused.rs:1"])
        t = claims[1]
        t.update(kind="requirement", claim="Changed Overwrite may break router inference",
                 historical_local_id="internal/overwrite-compat-break", original_kind="requirement/compatibility",
                 safety_premise="Operands are already resolved object shapes due to _ctx_out: {} and UnsetMarker guards",
                 asserted_scope="All existing callers, including inferred router shapes",
                 disposition_evidence="Corrected #137 att-12 section 3 and section 10 note 3; rejected before formal admission")
        t["inspected_evidence"][0].update(locator="att-12 section 5 commands 8-10; middleware.ts:65,81,103,120,136; procedureBuilder.ts:38-44",
                                         reason="Caller searches and reads preceded rejection")
        history = HERE.parents[1] / "one-shot-qualification-2026-09-07/j-trpc-5017/j-bea6be14-seed2-att-12-run.md"
        t["inspected_evidence"][0]["artifact"] = artifact(history)
        if case == "concrete":
            t.pop("historical_local_id")
            t["original_kind"] = "bug"
            t.update(claim="Overwrite may fail on the specified concrete object pair",
                     safety_premise="This concrete A/B pair evaluates to the asserted merged object",
                     asserted_scope="Only this concrete A/B instantiation; generic operands unassessed",
                     disposition_evidence="Synthetic stipulated concrete-type assertion")
            t["inspected_evidence"] = [dict(ev, artifact=artifact(clone / "concrete.ts", "reviewer-common"), locator="fixture://concrete.ts:1-3")]
        elif case in ("unavailable", "unknown", "not-inspected"):
            t["inspected_evidence"][0].update(availability=case, reason="Synthetic failed read" if case == "unavailable" else "Synthetic access evidence state")
            t["admission"]["original_text"] = "Synthetic disposition with caller evidence " + case
            t.update(safety_premise="unknown", asserted_scope="unknown",
                     disposition_evidence="Synthetic caller-evidence gap, not a global safety conclusion")
            if case == "not-inspected":
                t["inspected_evidence"][0]["complete_access_trace"] = True
    if case in ("clean", "refuted", "unresolved", "late-row", "spent-follow-up", "scope-dispute"):
        rows = [row("Q1", ["initial"] if case == "clean" else [])]
    primary_claims = [deepcopy(c) for c in claims if c["origin"] in ("primary", "both")]
    finder_claims = [deepcopy(c) for c in claims if c["origin"] in ("finder", "both")]
    initial_candidates = [c["id"] for c in claims if c["verification"]["required"]]
    initial_rows = [r["id"] for r in rows if "initial" in r["required_batches"]]
    initial = batch("clean-verdict" if case == "clean" else "candidate", initial_candidates, initial_rows) if initial_candidates or initial_rows else no_batch(
        "initial", claims, rows, "policy-permitted-omission" if case == "hygiene" or case in ("generic", "concrete", "unavailable", "unknown", "not-inspected") else "no-eligible-trigger")
    if case == "missing-dispatch":
        initial = no_batch("initial", claims, rows, "required-unavailable")
    report = dict(complete=True, pass_complete=True, manifest_complete=True, first_falsification_complete=True,
                  claims=claims, rows=rows, initial=initial)
    discovery = dict(report, claims=primary_claims) if arm == "C" else report
    scenario = {"primary": {"discovery": response(discovery)}}
    if arm == "C":
        scenario["finder"] = {"discovery": response(dict(complete=True, pass_complete=True, claims=finder_claims))}
        scenario["primary"]["admission"] = response(report)
        calls = [dict(name="read", path=str(clone / "queue.rs"), start=1, end=1),
                 dict(name="read", path=str(clone / "queue.rs"), start=3, end=3)]
        for store in ("primary-private", "other-attempt", "hidden-truth"):
            secret = root / store / "canary.txt"
            write(secret, (store + " SECRET CANARY\n").encode("utf-8"))
            calls.append(dict(name="read", path=str(secret), start=1, end=1))
        (clone / "leak").symlink_to(root / "hidden-truth" / "canary.txt")
        calls += [dict(name="read", path=str(clone / "leak"), start=1, end=1), dict(name="shell", path="cat canary")]
        scenario["finder"]["discovery"]["tools"] = calls
    rulings = [dict(id=i, verdict="confirmed", evidence="fixture decisive raw check", scope="named transition") for i in initial_candidates]
    rulings += [dict(id=i, verdict="holds", evidence="fixture opposite branch check", scope="supplied bounded scope") for i in initial_rows]
    if case in ("refuted", "unresolved", "scope-dispute"):
        rulings[0].update(verdict="refuted", basis="unresolved" if case == "unresolved" else "contradicted", settling_fact="Need branch identity")
    if case == "missing-ruling":
        rulings = [r for r in rulings if r["id"] != "Q1"]
    scenario["initial-verifier"] = {"verification": response(dict(complete=True, rulings=rulings, conclusion="Scoped supplied ledger dispositions hold"))}
    reconciled = deepcopy(report)
    follow = no_batch("follow-up", reconciled["claims"], rows, "no-new-required-work")
    if case in ("refuted", "unresolved", "late-row", "spent-follow-up", "scope-dispute"):
        reconciled["rows"][0]["required_batches"] = ["follow-up"]
        if case in ("refuted", "unresolved"):
            reconciled["claims"][0]["admission"]["disposition"] = "rejected"
            refuted_row = row("R-C1", ["follow-up"])
            refuted_row["linked_claim_id"] = "C1"
            refuted_row["disposition_evidence"] = "Initial verifier refutation of C1"
            reconciled["rows"].append(refuted_row)
        follow = batch("clean-verdict" if case in ("refuted", "unresolved") else "related-acquittal", [],
                       [r["id"] for r in reconciled["rows"] if "follow-up" in r["required_batches"]])
    reconciled["follow-up"] = follow
    scenario["primary"]["reconcile"] = response(reconciled)
    follow_rulings = [dict(id=i, verdict="re-open" if case == "spent-follow-up" else "holds", evidence="fixture scoped check", scope="named transition") for i in follow.get("row_ids", [])]
    scenario["follow-up-verifier"] = {"verification": response(dict(complete=True, rulings=follow_rulings, conclusion="Scoped conclusion; no global safety claim"))}
    final = deepcopy(reconciled)
    final.update(pending_required_ids=["C1"] if case in ("spent-follow-up", "scope-dispute") else [],
                 completion="incomplete" if case in ("missing-dispatch", "missing-ruling", "spent-follow-up", "scope-dispute", "unresolved") else "complete")
    for c in final["claims"]:
        rejected = c["admission"]["disposition"] == "rejected"
        withheld = case in ("missing-dispatch", "spent-follow-up", "scope-dispute") and c["verification"]["required"]
        c["publication"]["disposition"] = "not-admitted" if rejected else "withheld" if withheld else "rendered"
        supplied = [] if not initial["dispatch"] or c["id"] not in initial["candidate_ids"] else ["batch-initial"]
        received = [r for r in rulings if r["id"] == c["id"]] if supplied else []
        disposition = ("not-required-policy" if not c["verification"]["required"] else
                       "missing-required-dispatch" if not supplied else
                       "missing-required-ruling" if not received else
                       "unresolved" if received[-1].get("basis") == "unresolved" else received[-1]["verdict"])
        c["verification"].update(supplied_batch_ids=supplied, rulings=received, disposition=disposition)
    for row_record in final["rows"]:
        supplied = (["batch-initial"] if initial["dispatch"] and row_record["id"] in initial["row_ids"] else [])
        supplied += ["batch-follow-up"] if follow["dispatch"] and row_record["id"] in follow["row_ids"] else []
        returned = [r for r in rulings + follow_rulings if r["id"] == row_record["id"]] if supplied else []
        row_record.update(received_batches=supplied, rulings=returned, fidelity=(
            "missing-required-dispatch" if row_record["required_batches"] and not supplied else
            "missing-required-ruling" if supplied and not returned else
            "faithful" if returned else "policy-permitted-omission"))
    final["payload"] = payload(final, helpers["validate_review"]["uri"], source)
    scenario["primary"]["final"] = response(final)
    if case == "missing-finder" and arm == "C":
        scenario["finder"]["discovery"]["missing"] = True
    if case == "malformed":
        scenario["primary"]["discovery"]["malformed"] = True
    if case == "timeout":
        scenario["primary"]["discovery"]["delay_seconds"] = 2
        config["limits"].update(worker_seconds=0.1, finder_seconds=0.1)
    write(root / "config.json", config)
    write(root / "scenario.json", scenario)
    return config, scenario


def payload(final, validator, source):
    trailer = (f"<!-- review-run head={source['head_oid']} base-ref=main base-sha={source['base_oid']} "
               f"merge-base={source['merge_base_oid']} workflow=v5b-10 context={'a' * 64} "
               f"issues=fixture/queue#1 coverage={'incomplete' if final['completion'] == 'incomplete' else 'complete'} -->")
    items = []
    for c in final["claims"]:
        if c["publication"]["disposition"] != "rendered":
            continue
        required = c["verification"]["required"]
        action, priority = ("must-fix", "P1") if required else ("consider", "P2")
        optional = "" if required else "\n\nClosing this without action is a correct response."
        items.append(dict(type="finding", priority=priority, action=action, blocking=required, kind=c["kind"],
                     markdown=f"**[{priority}] [{action}] {c['claim']}**\n\n**Triggers when:** {c['trigger']}.\n\n**Impact:** {c['impact']}.\n\n**Change:** {c['change']}.{optional}",
                     trailer=f"<!-- finding id={c['id']} head={source['head_oid']} priority={priority} action={action} blocking={'true' if required else 'false'} kind={c['kind']} fix={c['fix']} -->",
                     anchor=dict(type="line", path=c["anchor"].split(":")[0], start_line=int(c["anchor"].split(":")[1]), end_line=int(c["anchor"].split(":")[1]), side="RIGHT"), fix=c["fix"]))
    result = dict(summary=dict(body="Synthetic fixture\n\n" + trailer), items=items)
    rendered = subprocess.run([sys.executable, validator, "--render"], input=json.dumps(result), capture_output=True, text=True, encoding="utf-8")
    if rendered.returncode:
        raise ValueError("fixture payload rendering failed: " + rendered.stdout + rendered.stderr)
    status = "Incomplete" if final["completion"] == "incomplete" else "Changes Requested (advisory)" if any(i["blocking"] for i in items) else "Approved (advisory)"
    result["summary"]["body"] = status + "\n\nSynthetic fixture review.\n\n" + rendered.stdout + "\n" + trailer
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--case", choices=CASES, default="empty")
    parser.add_argument("--arm", choices=list("ABC"), default="C")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return subprocess.run([sys.executable, str(HERE / "test_adapter.py"),
            "AdapterTests.test_pinned_omission_and_evidence_states_across_arms"]).returncode
    if args.out is None:
        parser.error("--out is required")
    try:
        make(args.out, args.case, args.arm)
        return 0
    except ValueError as exc:
        print(str(exc))
        return 1
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
