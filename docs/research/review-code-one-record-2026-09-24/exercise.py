#!/usr/bin/env python3
"""Prepare, consume and observe the #357 reviewer-and-caller exercise on the four archived #341 tasks.

Usage:
    python3 exercise.py prepare --root ROOT --skill-root SKILL
    python3 exercise.py consume --root ROOT --task TASK
    python3 exercise.py observe EVENTS --skill-root SKILL

``prepare`` materializes the #341 archive under ROOT with SKILL as the installed review-code, reseeds
the continuation task as prior records, and writes each task's prompt from ``prompts/``. The archived
continuation seed is a version-2 record at 864eea8 and an addendum at 03ce7cd; the reseed finalizes the
same review decisions with SKILL's ``render_review.py`` as ``seed/r1`` (864eea8, the confirmed P1
must-fix and the P3 consider, initial batch spent) and ``seed/r2`` (03ce7cd, from ``--prior-record
seed/r1``: both items still open and rendered again, the must-fix's confirmation carried with
``confirmed_in`` seed/r1, follow-up unspent). The continuation prompt passes ``seed/r2`` as
``prior_record``, so the run exercises the prior-record route rather than a full review.

``consume`` runs the applicable caller's local artifact path on ``ROOT/TASK/work/review`` without forge
writes and prints one JSON object. implement-publish (``implementation-gate``, ``continuation``): the
documented ``render_review.py --check --head --lineage`` with every accepted record, then the record's
head, lineage, prior record, carried blockers, allowance and incomplete-result fields, and for the
continuation that the seed records are unchanged. review-code-publish (``publishable``,
``required-verification``): ``--check``, the batch's head, the ``writes.jsonl`` items its
``finalization.replies`` would produce, and a gating ``--emit-batch --event`` to a scratch file when the
status admits one.

``observe`` summarizes a ``codex exec --json`` event log: commands run with their exit codes, the skill
files read, each ``render_review.py`` finalization and its exit (repairs are the failures before the
last success), ``forge_packet.py`` and verifier dispatches, and token usage.

Exit codes: 0 success; 1 an unmet expectation, one line each on stderr (``consume`` still prints its
JSON); 2 an unreadable input or a failed subprocess.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parent / "review-code-artifact-savings-2026-09-22" / "archive"
ARCHIVER = HERE.parent / "tools" / "savings_archive.py"
TASKS = ("publishable", "implementation-gate", "required-verification", "continuation")
BASE = "2301c83ee0b2ba0248fe3d2d1f6cd481963545ab"
HEADS = {"publishable": "0eb283dfe715341548387bf65af857affedf5dfa",
         "implementation-gate": "2ba40465ef91f15b2963a4b12e80f46ee0e9efae",
         "required-verification": "a13922e76f42d9757608530348200affbf3bde2f",
         "continuation": "b96a362e99ce4f5b6b1fe26ad02fda66e8343723"}
R1_HEAD = "864eea86ab86bf5a3375898bc606933ea20696cc"
R2_HEAD = "03ce7cd85d34afda4ae47f06d7958ea906b3fcc1"
MUST_FIX = "accounts/frozen-transfer-bypass"
CONSIDER = "accounts/post-docstring-frozen"


def run(command: list[str], cwd: Path | None = None, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, input=stdin, capture_output=True, text=True, encoding="utf-8")
    return result


def must(command: list[str], cwd: Path | None = None) -> str:
    result = run(command, cwd)
    if result.returncode != 0:
        print(f"exercise: `{shlex.join(command)}` exited {result.returncode}:\n{result.stdout}{result.stderr}", file=sys.stderr)
        raise SystemExit(2)
    return result.stdout


def load(path: Path) -> Any:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --- prepare ---------------------------------------------------------------------------------------------------------


def reseed(task: Path, skill: Path) -> None:
    """Finalize the archived continuation state as seed/r1 and seed/r2 with SKILL's render_review.py."""
    render = str(skill / "scripts" / "render_review.py")
    repo, review = task / "repo", task / "review"
    archived = load(review / "composition.json")
    addendum = load(review / "addenda" / f"addendum-{R2_HEAD}.json")

    # R1: the archived initial review, with only what the current finalizer derives or retired left out.
    r1_dir = task / "seed" / "r1"
    r1_dir.mkdir(parents=True)
    r1 = json.loads(json.dumps(archived))
    for key in ("head", "merge_base", "merged", "context"):
        r1["run"].pop(key, None)
    r1["record"]["paths"] = {"spec": r1["record"]["paths"]["spec"]}
    verification = r1["record"]["verification"]
    verification.pop("allowance")
    verification["batches"] = [{key: batch[key] for key in ("bundle", "accounting", "operation")} for batch in verification["batches"]]
    dump(r1_dir / "composition.json", r1)
    must(["python3", render, "--store", str(review / f"review-context-{R1_HEAD}.json"), str(r1_dir)], repo)

    # R2: the addendum's decisions at 03ce7cd, as a re-review from R1 that carries both open items.
    r2_dir = task / "seed" / "r2"
    r2_dir.mkdir(parents=True)
    store = r2_dir / f"review-context-{R2_HEAD}.json"
    must(["python3", str(skill / "scripts" / "review_context.py"), "--merge-base", BASE, "--head", R2_HEAD, "--base-ref", "main",
          "--prior-head", R1_HEAD, "--store", str(store)], repo)
    messages = must(["git", "log", "--reverse", "--format=%H%n%B", f"{BASE}..{R2_HEAD}"], repo)
    findings = json.loads(json.dumps(archived["findings"]))
    blocker = next(f for f in findings if f["id"] == MUST_FIX)
    blocker.update(trigger="A transfer names a frozen account as its target.",
                   impact="`Ledger.transfer` refuses a frozen source but appends the credit to a frozen target, so that account is "
                          "credited despite the freeze that spec criterion 2 forbids.",
                   change="In `Ledger.transfer` (`ledger/accounts.py:85`), also raise `LedgerError` before appending either entry "
                          "when the target account is frozen.",
                   anchor={"type": "line", "path": "ledger/accounts.py", "start_line": 85, "end_line": 86, "side": "RIGHT"},
                   fix={"path": "ledger/accounts.py", "start_line": 85})
    evidence = {row["id"]: row["evidence"] for row in addendum["fixed_findings"]}
    r2 = {
        "run": dict(r1["run"], target=f"main...{R2_HEAD}", change_description=messages),
        "summary": dict(archived["summary"],
                        issue_fit="Partial — freezing, unfreezing, refused postings and refused transfers out of a frozen account "
                                  "are implemented; criterion 2's refusal of transfers into a frozen account is not.",
                        coverage="Complete merge-base diff reviewed (2 files), with the fix delta `864eea8..03ce7cd` read in full. "
                                 "Reviewer-executed `python3 -m unittest discover -s tests -v` at the head: 17 tests, pass."),
        "findings": findings, "questions": [], "observations": [],
        "prior_items": [
            {"id": MUST_FIX, "classification": "still-open", "action": "must-fix", "note": evidence[MUST_FIX]},
            {"id": CONSIDER, "classification": "still-open", "action": "consider",
             "note": "ledger/accounts.py:61 at 03ce7cd still lists no frozen-account error in the post docstring"},
        ],
        "record": {
            "repository": r1["record"]["repository"], "paths": r1["record"]["paths"],
            "requirements": [dict(row, evidence="ledger/accounts.py:85-86 refuses a frozen source; ledger/accounts.py:90 still credits a frozen target")
                             if row["source"].endswith("criterion-2") else row for row in r1["record"]["requirements"]],
            "files": r1["record"]["files"], "check_evidence": addendum["check_evidence"],
            "verification": {"tasks": [{"id": MUST_FIX, "type": "candidate", "trigger": "must-fix", "batch": "initial",
                                        "ruling": "confirmed", "confirmed_in": str(r1_dir / "record.json")}],
                             "batches": [], "outstanding": []},
            "routed": addendum["routed"],
        },
    }
    dump(r2_dir / "composition.json", r2)
    must(["python3", render, "--store", str(store), "--prior-record", str(r1_dir / "record.json"), str(r2_dir)], repo)


def prepare(args: argparse.Namespace) -> int:
    root, skill = Path(os.path.abspath(args.root)), Path(os.path.abspath(args.skill_root))
    must(["python3", str(ARCHIVER), "materialize", str(ARCHIVE), "--root", str(root), "--skill-root", str(skill)])
    reseed(root / "continuation", skill)
    bounds = (HERE / "prompts" / "_bounds.txt").read_text(encoding="utf-8").rstrip("\n")
    for task in TASKS:
        text = (HERE / "prompts" / f"{task}.md").read_text(encoding="utf-8").replace("@BOUNDS@", bounds)
        text = text.replace("@TASK_ROOT@", str(root / task)).replace("@SKILL_ROOT@", str(skill))
        (root / task / "prompt.md").write_text(text, encoding="utf-8")
    hashes = {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted((root / "continuation" / "seed").rglob("*")) if path.is_file()}
    dump(root / "seed-hashes.json", hashes)
    print(json.dumps({"root": str(root), "skill_root": str(skill), "seed_files": len(hashes)}))
    return 0


# --- consume ---------------------------------------------------------------------------------------------------------


def consume(args: argparse.Namespace) -> int:
    root = Path(os.path.abspath(args.root))
    task, private = root / args.task, root / args.task / "work" / "review"
    unmet: list[str] = []
    out: dict[str, Any] = {"task": args.task, "private_dir": str(private)}
    try:
        record = load(private / "record.json")
    except (OSError, ValueError) as error:
        out["record"] = f"unreadable: {error}"
        print(json.dumps(out, indent=2))
        print(f"no readable record in {private}", file=sys.stderr)
        return 1
    render = str(Path(record["record"]["paths"]["skill_root"]) / "scripts" / "render_review.py")
    run_fields, accounting = record["run"], record["record"]
    verification = accounting["verification"]
    out.update(status=record["status"], coverage=run_fields["coverage"], head=run_fields["head"],
               packet_context=run_fields["packet_context"], supplied_inputs=run_fields["supplied_inputs"],
               findings=[{"id": i["id"], "priority": i["priority"], "action": i["action"], "kind": i["kind"]}
                         for i in record["items"] if i["type"] == "finding"],
               questions=[i["id"] for i in record["items"] if i["type"] == "question"],
               observations=sum(1 for i in record["items"] if i["type"] == "observation"),
               allowance=verification["allowance"], batches=[b["name"] + "/" + b["phase"] for b in verification["batches"]],
               tasks=[{k: t.get(k) for k in ("id", "type", "trigger", "batch", "ruling", "confirmed_in")} for t in verification["tasks"]],
               outstanding=verification["outstanding"], lineage=record["lineage"], prior_record=record["prior_record"],
               prior_items=[{k: p[k] for k in ("id", "classification", "action")} for p in record["prior_items"]])
    if run_fields["head"] != HEADS[args.task]:
        unmet.append(f"the record reviews {run_fields['head']}, not {HEADS[args.task]}")
    if (run_fields["coverage"] == "complete") == bool(verification["outstanding"]):
        unmet.append("coverage and outstanding verification disagree")

    if args.task in ("implementation-gate", "continuation"):
        accepted = ([task / "seed" / "r1" / "record.json", task / "seed" / "r2" / "record.json"]
                    if args.task == "continuation" else [])
        command = ["python3", render, "--check", "--head", HEADS[args.task]]
        for path in [*accepted, private / "record.json"]:
            command += ["--lineage", str(path)]
        checked = run([*command, str(private)])
        out["caller_check"] = {"command": shlex.join([*command, str(private)]), "exit": checked.returncode,
                               "stdout": checked.stdout}
        if checked.returncode != 0:
            unmet.append("the caller's lineage check refused the record")
        if args.task == "continuation":
            if record["prior_record"] != str(accepted[1]) or record["lineage"] != [str(p) for p in accepted]:
                unmet.append("the record does not continue seed/r2 with lineage [r1, r2]")
            classified = {p["id"]: p["classification"] for p in record["prior_items"]}
            if set(classified) != {MUST_FIX, CONSIDER}:
                unmet.append(f"prior items classified: {classified}")
            if not verification["allowance"]["initial_spent"]:
                unmet.append("the initial batch the prior spent reads as unspent")
            open_blockers = [i["id"] for i in record["items"] if i["type"] == "finding" and i["action"] == "must-fix"]
            out["open_blockers"] = open_blockers
            before = load(root / "seed-hashes.json")
            after = {key: hashlib.sha256((root / key).read_bytes()).hexdigest() for key in before if (root / key).is_file()}
            out["seed_unchanged"] = before == after
            if before != after:
                unmet.append("the prior record's directory changed")
    else:
        checked = run(["python3", render, "--check", str(private)])
        out["caller_check"] = {"exit": checked.returncode, "stdout": checked.stdout}
        if checked.returncode != 0:
            unmet.append("--check refused the record")
        batch = load(private / "batch.json")
        out["batch"] = {"commit_id": batch["commit_id"], "event": batch["event"], "comments": len(batch["comments"])}
        if batch["commit_id"] != HEADS[args.task]:
            unmet.append("the batch names another head")
        out["writes_jsonl_items"] = len(record["finalization"]["replies"])
        event = {"Approved": "APPROVE", "Changes Requested": "REQUEST_CHANGES"}.get(record["status"])
        if event is not None:
            payload = (private / "payload.json").read_text(encoding="utf-8")
            gated = run(["python3", render, "--emit-batch", "--event", event], stdin=payload)
            out["gating"] = {"event": event, "exit": gated.returncode,
                             "advisory_suffix_removed": gated.returncode == 0 and "(advisory)**" not in json.loads(gated.stdout)["body"].split("\n", 1)[0]}
            if gated.returncode != 0:
                unmet.append(f"gating emission failed: {gated.stdout}")
    report = private / "report.md"
    out["report_bytes"] = report.stat().st_size if report.is_file() else None
    out["unmet"] = unmet
    print(json.dumps(out, indent=2, ensure_ascii=False))
    for line in unmet:
        print(line, file=sys.stderr)
    return 1 if unmet else 0


# --- observe ---------------------------------------------------------------------------------------------------------


READERS = re.compile(r"\b(cat|sed|head|tail|less|batcat|bat|nl|awk|rg|grep|python3 -c)\b")


def observe(args: argparse.Namespace) -> int:
    skill = os.path.abspath(args.skill_root)
    commands: list[dict[str, Any]] = []
    usage: dict[str, int] = {}
    messages = 0
    try:
        lines = Path(args.events).read_text(encoding="utf-8").splitlines()
    except OSError as error:
        print(f"exercise: cannot read {args.events}: {error}", file=sys.stderr)
        return 2
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        item = event.get("item") if isinstance(event.get("item"), dict) else {}
        if event.get("type") == "item.completed" and item.get("type") == "command_execution":
            commands.append({"command": item.get("command", ""), "exit": item.get("exit_code")})
        elif event.get("type") == "item.completed" and item.get("type") == "agent_message":
            messages += 1
        elif event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            for key, value in event["usage"].items():
                if isinstance(value, int):
                    usage[key] = usage.get(key, 0) + value
    reads: dict[str, int] = {}
    for entry in commands:
        text = entry["command"]
        if not READERS.search(text):
            continue
        for match in re.finditer(re.escape(skill) + r"/((?:references/)?[A-Za-z0-9_.-]+\.(?:md|py))", text):
            reads[match.group(1)] = reads.get(match.group(1), 0) + 1
    finalizations = [e for e in commands if "render_review.py" in e["command"] and "--store" in e["command"]]
    last_success = max((i for i, e in enumerate(finalizations) if e["exit"] == 0), default=None)
    summary = {
        "commands": len(commands), "failed_commands": sum(1 for e in commands if e["exit"] not in (0, None)),
        "agent_messages": messages, "skill_files_read": dict(sorted(reads.items())),
        "finalizations": [e["exit"] for e in finalizations],
        "repair_loops": sum(1 for i, e in enumerate(finalizations) if e["exit"] != 0 and (last_success is None or i < last_success)),
        "checks": [e["exit"] for e in commands if "render_review.py" in e["command"] and "--check" in e["command"]],
        "forge_packet": [e["command"].split("forge_packet.py", 1)[1].split()[0] for e in commands if "forge_packet.py" in e["command"]],
        "verifier_builds": sum(1 for e in commands if "build_verifier_prompt.py" in e["command"] and "--example" not in e["command"]),
        "verifier_dispatches": sum(1 for e in commands if re.search(r"\bcodex exec\b", e["command"])),
        "accountings": [e["exit"] for e in commands if "account_verifier_return.py" in e["command"]],
        "usage": usage,
    }
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("prepare")
    one.add_argument("--root", required=True)
    one.add_argument("--skill-root", required=True)
    two = sub.add_parser("consume")
    two.add_argument("--root", required=True)
    two.add_argument("--task", required=True, choices=TASKS)
    three = sub.add_parser("observe")
    three.add_argument("events")
    three.add_argument("--skill-root", required=True)
    args = parser.parse_args()
    return {"prepare": prepare, "consume": consume, "observe": observe}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
