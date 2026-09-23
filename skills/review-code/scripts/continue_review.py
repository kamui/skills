#!/usr/bin/env python3
"""Load, validate and extend an implementation-gate record's version-2 continuation chain.

Usage:
    python3 scripts/continue_review.py state [--json] RECORD
    python3 scripts/continue_review.py compose --record RECORD --store STORE INPUT
    python3 scripts/continue_review.py --example

RECORD is the absolute path of the chain's `record.json` (the original record,
or a replacement record to continue from). The chain is that record, then
each addendum in its `addenda` directory whose `reviewed_head` is the current
head, in link order; an addendum whose `replaced_by_full_review` names a new
record moves the chain to that record and its own addenda directory. File
names and timestamps never order the chain.

`state` validates the chain and prints its current state: `status`,
`coverage`, `head`, `record`, the latest `addendum` when there is one, its
`report` (or `legacy <path>` for a chain file that predates the report), and
`continuation <this script>`. `--json` prints the whole state instead: open
findings and questions with their bodies, per-file coverage, requirement rows,
check evidence at its original heads, verification tasks and batches with the
chain file that holds each, confirmations with their accounting provenance,
cumulative allowance, outstanding work and routed items.

`compose` builds the next addendum from INPUT, the continuation's authored
decisions (`--example` prints the shape), and STORE, the continuation's
review_context.py store built with `--prior-head <current head>`. It derives
what a saved input owns and refuses an explicit copy that disagrees:

    format, workflow            implementation-gate-addendum/2, this workflow
    record, record_format       the chain's current record and its schema
    reviewed_head               the chain's current head
    final_head                  the store's head
    delta row order             the store's delta manifest (every delta path
                                needs an authored state; none defaults)
    batch name, phase,          each batch's bundle manifest and accounting
      raw_return                report, as finalize_review.py derives them
    verification.allowance      the chain's spent flags plus this addendum's
                                batches, cumulative; never reset
    verification.outstanding    when omitted, the chain's entries less those a
                                task here settled; when written, it keeps them
    routed                      when omitted, the chain's; when written, a
                                superset of it
    replaced_by_full_review     null when omitted

Every other field is a model decision and is required: each delta file's
state, each fixed finding's classification and evidence, new findings and
questions, changed requirement rows, check evidence, the tasks and batches
this continuation added, `status`, `coverage` and `coverage_gaps`.

Validation, for every chain file and for the new addendum: known schemas; a
record without `finalization` must pass validate_review.py, and one with it
must name an existing report; each addendum names the current record and its
schema and links `reviewed_head` to the current head; forks, cycles and
unlinked addenda are rejected; a fixed id must be open; new ids must not be;
file states, requirement rows and check evidence keep the record's rules at
the addendum's final head; each task's ruling must be the one its batch's
accounting report establishes; a mandatory finding needs its confirmed
candidate task within the remaining allowance; spent allowance, outstanding
work, routed items and untouched per-file coverage survive every addendum
(the base contract's allowance without `carried_from` reads as null);
`status` and `coverage` must agree with the cumulative open items, files,
outstanding work and unrecoverable inputs, except that a replacement's own
items govern the status and its own file accounting the files it settled. A
replacement record must head the addendum's final head, carry every open item
(an open must-fix still `must-fix`), routed item and outstanding task, keep
the spent flags with `carried_from` naming the chain file it replaced, and
carry the confirmation of each finding open before the addendum as
`carried:<original chain file>#<batch>` with its trigger.

A new addendum is written as `addendum-<final head>.json` in the current
record's addenda directory with `finalization` (review-code-finalization/1,
its report path and its inputs), then `addendum-<final head>.report.md`, the
complete current result, is promoted last as its success marker. Each is
staged as `.part` and linked into place without replacing any file; a failure
removes what this run wrote. An existing complete addendum for the final head
is refused; an interrupted one (its report missing) is replaced. The record,
its report and earlier addenda are never modified. A private directory has one
writer at a time.

Any version-1 record or addendum ends validation with
`legacy-chain-needs-mapping`: the chain files in link order and, as a floor,
the latest version-2 addendum's allowance, outstanding work and routed items.
Map it by hand under references/continuation-addendum.md; this is neither
approval nor a fresh chain or allowance, and `compose` refuses it.

Exit codes:
    0  the chain is valid (state), or the addendum and its report were saved
    1  `chain-invalid` or `legacy-chain-needs-mapping` followed by one line per
       reason or chain file, or a content violation in the new addendum, one
       `<location>: <rule>: <detail>` line each
    2  RECORD, INPUT or STORE cannot be read, or an output cannot be written,
       named on stderr
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import compose_review as cr
import finalize_review as fr
import review_context as rc
import validate_review as vr

SCRIPT = Path(__file__).resolve()
RECORD_V1, RECORD_V2 = "implementation-gate-record/1", cr.RECORD_SCHEMA
ADDENDUM_V1, ADDENDUM_V2 = "implementation-gate-addendum/1", "implementation-gate-addendum/2"
FIXED_CLASSIFICATIONS = ("fixed", "still-open", "not-verifiable")
ROUTED = ("unresolved", "disputed", "unrecoverable_inputs")
# The saved addendum's key order, as continuation-addendum.md has always listed it.
ADDENDUM_KEYS = ("format", "workflow", "record", "record_format", "reviewed_head", "final_head", "delta",
                 "replaced_by_full_review", "fixed_findings", "findings", "questions", "requirements", "check_evidence",
                 "verification", "status", "coverage", "coverage_gaps", "routed")
VERIFICATION_KEYS = ("tasks", "batches", "allowance", "outstanding")
AUTHORED = ("delta", "fixed_findings", "findings", "questions", "requirements", "check_evidence", "verification",
            "status", "coverage", "coverage_gaps")


class Invalid(Exception):
    """The chain cannot be read as current state; each line names why."""

    def __init__(self, lines: list[str]) -> None:
        super().__init__(lines)
        self.lines = lines


class Legacy(Exception):
    """A version-1 file is in the chain; the prose mapping owns it."""

    def __init__(self, files: list[tuple[str, str]], floor: dict[str, Any] | None) -> None:
        super().__init__(files)
        self.files, self.floor = files, floor


def sha(value: Any) -> bool:
    return isinstance(value, str) and bool(vr.COMMIT_SHA_RE.fullmatch(value))


def task_id(entry: str) -> str:
    return entry.split(":", 1)[0].strip()


def report_path(addendum: Path) -> Path:
    return addendum.with_name(addendum.name[: -len(".json")] + ".report.md")


# --- collect: read every chain file and order it by its links ------------------------------------------------------


def read_file(report: vr.Report, path: str, what: str) -> dict[str, Any] | None:
    doc, why = cr.load_object(path)
    if doc is None:
        report.add(what, "chain", f"`{path}` {why}")
    return doc


def collect(record_path: str, interrupted_final: str | None = None) -> tuple[list[tuple[str, Path, dict[str, Any]]], list[Path]]:
    """Every chain file in link order as ``(kind, path, doc)``, and an interrupted addendum for ``interrupted_final``.

    Raises Invalid for an unreadable, unknown or unlinked file, a fork or a cycle, and Legacy when any file is
    version 1 and the rest is readable and linked.
    """
    report = vr.Report()
    files: list[tuple[str, Path, dict[str, Any]]] = []
    interrupted: list[Path] = []
    legacy = False
    heads: set[str] = set()
    records: set[str] = set()
    path = Path(os.path.abspath(record_path))
    expected = None  # the head a replacement record must carry
    while True:
        doc = read_file(report, str(path), "record")
        if doc is None:
            break
        schema = doc.get("schema")
        if schema == RECORD_V1:
            legacy = True
        elif schema != RECORD_V2:
            report.add("record", "schema", f"`{path}` has unknown schema {json.dumps(schema)}")
            break
        if str(path) in records:
            report.add("record", "chain", f"`{path}` is reached twice; the chain has a cycle")
            break
        records.add(str(path))
        files.append(("record", path, doc))
        head = (doc.get("run") or {}).get("head") if isinstance(doc.get("run"), dict) else None
        addenda = ((doc.get("record") or {}).get("paths") or {}).get("addenda") if isinstance(doc.get("record"), dict) else None
        if not sha(head) or not (isinstance(addenda, str) and addenda.startswith("/")):
            report.add("record", "chain", f"`{path}` names no full `run.head` or absolute `record.paths.addenda`")
            break
        if expected is not None and head != expected:
            report.add("record", "chain", f"replacement `{path}` heads `{head}`, not the final head `{expected}` of the addendum naming it")
            break
        if expected is None and head in heads:
            report.add("record", "chain", f"`{path}` heads `{head}`, which the chain already reached; the chain has a cycle")
            break
        heads.add(head)
        try:
            names = sorted(os.listdir(addenda))
        except FileNotFoundError:
            names = []
        except OSError as error:
            report.add("addenda", "chain", f"cannot list `{addenda}`: {error}")
            break
        linked: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
        for name in names:
            if not (name.startswith("addendum-") and name.endswith(".json")):
                continue  # reports and staged .part files
            file = Path(addenda) / name
            addendum = read_file(report, str(file), "addendum")
            if addendum is None:
                continue
            fmt = addendum.get("format")
            if fmt == ADDENDUM_V1 or addendum.get("record_format") == RECORD_V1:
                legacy = True
            elif fmt != ADDENDUM_V2:
                report.add("addendum", "schema", f"`{file}` has unknown format {json.dumps(fmt)}")
                continue
            if not (sha(addendum.get("reviewed_head")) and sha(addendum.get("final_head"))):
                report.add("addendum", "chain", f"`{file}` names no full `reviewed_head` and `final_head`")
                continue
            why = cr.finalization_problem(addendum)
            if why and addendum["final_head"] == interrupted_final and interrupted_write(addendum, file):
                interrupted.append(file)  # this continuation's own interrupted write; compose replaces it
                continue
            if why:
                report.add("addendum", "finalization", f"`{file}` {why}")
                continue
            linked.setdefault(addendum["reviewed_head"], []).append((file, addendum))
        if report.lines:
            break
        used: set[Path] = set()
        current, replacement = head, None
        while current in linked:
            candidates = linked[current]
            if len(candidates) > 1:
                report.add("addenda", "chain", f"{', '.join(f'`{p}`' for p, _d in candidates)} all continue from `{current}`; "
                           "the chain forks, so no one current state exists")
                break
            file, addendum = candidates[0]
            used.add(file)
            final = addendum["final_head"]
            if final in heads:
                report.add("addendum", "chain", f"`{file}` returns to `{final}`, which the chain already reached; the chain has a cycle")
                break
            heads.add(final)
            files.append(("addendum", file, addendum))
            current = final
            replacement = addendum.get("replaced_by_full_review")
            if replacement not in (None, False):
                break
        forked = bool(report.lines)
        for group in linked.values():
            for file, addendum in group:
                if file not in used and not forked:
                    report.add("addendum", "chain", f"`{file}` continues from `{addendum['reviewed_head']}`, which no chain file "
                               "reaches; it is not linked to the record's head chain")
        if report.lines or replacement in (None, False):
            break
        if not (isinstance(replacement, str) and replacement.startswith("/")):
            if isinstance(replacement, str) or not legacy:
                report.add("addendum", "chain", f"`{files[-1][1]}` names replacement {json.dumps(replacement)}, not an absolute record path")
            break
        path, expected = Path(os.path.abspath(replacement)), current
    if report.lines:
        raise Invalid(report.lines)
    if legacy:
        raise Legacy([(doc.get("schema") or doc.get("format"), str(p)) for _k, p, doc in files], floor(files))
    return files, interrupted


def interrupted_write(addendum: dict[str, Any], file: Path) -> bool:
    """A new-protocol addendum whose own report was never promoted: the write stopped before its success marker."""
    meta = addendum.get("finalization")
    return (isinstance(meta, dict) and meta.get("protocol") == cr.FINALIZATION_PROTOCOL
            and meta.get("report") == str(report_path(file)) and not os.path.exists(meta["report"]))


def floor(files: list[tuple[str, Path, dict[str, Any]]]) -> dict[str, Any] | None:
    """What the latest version-2 addendum already recorded: the mapping may raise it, never lower it."""
    for kind, path, doc in reversed(files):
        if kind == "addendum" and doc.get("format") == ADDENDUM_V2 and isinstance(doc.get("verification"), dict):
            verification = doc["verification"]
            return {"from": str(path), "allowance": verification.get("allowance"),
                    "outstanding": verification.get("outstanding"), "routed": doc.get("routed")}
    return None


# --- reduce: validate each file against the state before it ---------------------------------------------------------


class State:
    """The chain's current state after the files reduced so far."""

    def __init__(self) -> None:
        self.repository: Any = None
        self.record: Path = Path("/")
        self.schema = RECORD_V2
        self.addenda: Path = Path("/")
        self.head = ""
        self.tip: Path = Path("/")
        self.tip_report: str | None = None
        self.addendum: Path | None = None  # the latest addendum, which a replacement it names does not displace
        self.chain: list[dict[str, Any]] = []
        self.open: dict[str, dict[str, Any]] = {}
        self.ids: set[str] = set()
        self.files: dict[str, dict[str, Any]] = {}
        self.requirements: dict[str, dict[str, Any]] = {}
        self.check_evidence: list[dict[str, Any]] = []
        self.tasks: list[dict[str, Any]] = []
        self.batches: list[dict[str, Any]] = []
        self.confirmations: dict[str, dict[str, Any]] = {}
        self.allowance = {"initial_spent": False, "follow_up_spent": False}
        self.outstanding: list[str] = []
        self.routed: dict[str, list[str]] = {key: [] for key in ROUTED}
        self.status = ""
        self.coverage = ""
        self.coverage_gaps: list[str] = []
        self.fixed: list[dict[str, Any]] = []

    def ledgers(self) -> dict[str, Any]:
        """The shape finalize_review.ledger_sections renders."""
        return {"requirements": list(self.requirements.values()), "files": list(self.files.values()),
                "check_evidence": self.check_evidence,
                "verification": {"allowance": dict(self.allowance, carried_from=None), "batches": self.batches,
                                 "tasks": self.tasks, "outstanding": self.outstanding},
                "routed": self.routed}


def summary_gaps(body: str) -> list[str]:
    """The `Coverage gaps` lines the composer rendered into a record's summary body."""
    section = body.split("\n## Coverage gaps\n\n", 1)
    if len(section) < 2:
        return []
    return [line[2:] for line in section[1].split("\n\n", 1)[0].splitlines() if line.startswith("- ")]


def check_rulings(report: vr.Report, where: str, tasks: list[dict[str, Any]], batches: list[dict[str, Any]]) -> None:
    """Each task's claimed result must be the one its batch's accounting report, or a carried chain file's, establishes."""
    accounting = {b.get("name"): b.get("accounting") for b in batches if isinstance(b, dict)}
    for index, task in enumerate(tasks):
        if not isinstance(task, dict) or task.get("ruling") in ("pending", "withheld"):
            continue
        batch, identity = task.get("batch"), task.get("id")
        role = "candidates" if task.get("type") == "candidate" else "premises"
        if isinstance(batch, str) and batch.startswith("carried:"):
            chain_file, _, name = batch[len("carried:"):].partition("#")
            source, why = cr.chain_accounting(chain_file, name)
        else:
            source, why = accounting.get(batch), f"names batch {json.dumps(batch)}, which is not recorded"
        if source is not None:
            established, why = cr.accounted_ruling(source, role, identity)
            if established is not None and established != task.get("ruling"):
                why = f"accounting report `{source}` establishes `{established}`, not `{task.get('ruling')}`"
            elif established is not None:
                why = ""
        if why:
            report.add(f"{where}.verification.tasks[{index}]", "verification", f"task `{identity}`: {why}")


def open_record(report: vr.Report, state: State, path: Path, doc: dict[str, Any]) -> None:
    """Start (or restart, after a replacement) the state at a version-2 record."""
    where = str(path)
    why = cr.finalization_problem(doc)
    if why:
        report.add(where, "finalization", why)
        return
    problems = vr.validate(doc)
    if problems:
        report.add(where, "schema", f"the record does not validate: {problems[0]}")
        return
    record, run = doc.get("record"), doc.get("run")
    if not isinstance(record, dict) or not isinstance(run, dict) or not isinstance(record.get("verification"), dict):
        report.add(where, "schema", "a version-2 record carries `run` and its `record` accounting")
        return
    verification = record["verification"]
    allowance = verification.get("allowance")
    if not isinstance(allowance, dict) or not all(isinstance(allowance.get(k), bool) for k in ("initial_spent", "follow_up_spent")):
        report.add(where, "schema", "`record.verification.allowance` carries boolean spent flags")
        return
    lists = {"files": record.get("files"), "requirements": record.get("requirements"), "check_evidence": record.get("check_evidence"),
             "tasks": verification.get("tasks"), "batches": verification.get("batches"), "outstanding": verification.get("outstanding")}
    routed = record.get("routed")
    if not all(isinstance(v, list) for v in lists.values()) or not isinstance(routed, dict) or \
            not all(isinstance(routed.get(k), list) for k in ROUTED):
        report.add(where, "schema", "the record's accounting sections are lists, and `routed` names its three lists")
        return
    check_rulings(report, where, lists["tasks"], lists["batches"])
    state.repository, state.record, state.schema = record.get("repository"), path, doc["schema"]
    state.addenda = Path(record["paths"]["addenda"])
    state.head, state.tip = run["head"], path
    final = doc.get("finalization")
    own_report = final.get("report") if isinstance(final, dict) else None
    if state.addendum is None:  # a replacement keeps the marker and fixes of the addendum that named it
        state.tip_report, state.fixed = own_report, []
    state.open = {}
    for item in doc.get("items", []):
        if item.get("type") in ("finding", "question"):
            state.open[item["id"]] = {"id": item["id"], "type": item["type"],
                                      "action": item.get("action", "question") if item["type"] == "finding" else "question",
                                      "priority": item.get("priority"), "kind": item.get("kind"), "markdown": item["markdown"],
                                      "trailer": item["trailer"], "head": run["head"], "source": str(path)}
    state.ids |= set(state.open)
    state.files = {row["path"]: dict(row) for row in lists["files"] if isinstance(row, dict) and "path" in row}
    state.requirements = {row["source"]: dict(row) for row in lists["requirements"] if isinstance(row, dict) and "source" in row}
    state.check_evidence = [dict(row, source=str(path)) for row in lists["check_evidence"] if isinstance(row, dict)]
    state.tasks = [dict(task, source=str(path)) for task in lists["tasks"] if isinstance(task, dict)]
    state.batches = [dict(batch, source=str(path)) for batch in lists["batches"] if isinstance(batch, dict)]
    state.confirmations = {}
    for task in state.tasks:
        if task.get("type") == "candidate" and task.get("ruling") == "confirmed":
            batch = task.get("batch")
            ref = batch if isinstance(batch, str) and batch.startswith("carried:") else f"carried:{path}#{batch}"
            state.confirmations[task["id"]] = {"batch": ref, "trigger": task.get("trigger")}
    state.allowance = {"initial_spent": allowance["initial_spent"], "follow_up_spent": allowance["follow_up_spent"]}
    state.outstanding = list(lists["outstanding"])
    state.routed = {key: list(routed[key]) for key in ROUTED}
    state.status, state.coverage = doc.get("status"), run.get("coverage")
    state.coverage_gaps = summary_gaps(doc["summary"]["body"])
    state.chain.append({"kind": "record", "path": str(path), "schema": doc["schema"], "head": run["head"],
                        "report": own_report})


def same_allowance(explicit: Any, derived: dict[str, Any]) -> bool:
    """The spent flags agree; an addendum carries nothing, so `carried_from` is null or, as the base contract wrote it, absent."""
    return (isinstance(explicit, dict) and set(explicit) <= {"initial_spent", "follow_up_spent", "carried_from"}
            and all(explicit.get(k) is derived[k] for k in ("initial_spent", "follow_up_spent"))
            and explicit.get("carried_from") is None)


def check_rows(report: vr.Report, doc: dict[str, Any], final: str) -> tuple[list, list, list, list]:
    """The addendum's delta, fixed-finding, requirement and check-evidence rows, under the record's row rules."""
    delta = cr.read_rows(report, "delta", doc.get("delta"), ("path", "state"))
    seen: set[str] = set()
    for where, row in delta:
        if row["state"] not in cr.FILE_STATES:
            report.add(where, "file-accounting", f"`state` must be one of {list(cr.FILE_STATES)}")
        if row["state"] == "ignored":
            cr.read_line(report, where, row, "reason")
        if row["path"] in seen:
            report.add(where, "file-accounting", f"`{row['path']}` is accounted for twice")
        seen.add(row["path"])
    fixed = cr.read_rows(report, "fixed_findings", doc.get("fixed_findings"), ("id", "classification", "evidence"))
    requirements = cr.read_rows(report, "requirements", doc.get("requirements"), ("source", "class", "disposition", "evidence"))
    for where, row in requirements:
        if row["class"] not in cr.REQUIREMENT_CLASSES:
            report.add(where, "requirements", f"`class` must be one of {list(cr.REQUIREMENT_CLASSES)}")
        if row["disposition"] not in cr.REQUIREMENT_DISPOSITIONS:
            report.add(where, "requirements", f"`disposition` must be one of {list(cr.REQUIREMENT_DISPOSITIONS)}")
    evidence = cr.read_rows(report, "check_evidence", doc.get("check_evidence"), ("check", "head", "outcome"))
    for where, row in evidence:
        if row["outcome"] not in cr.EVIDENCE_OUTCOMES:
            report.add(where, "check-evidence", f"`outcome` must be one of {list(cr.EVIDENCE_OUTCOMES)}")
        elif not sha(row["head"]):
            report.add(where, "trailer-sha", "`head` must be exactly 40 lowercase hexadecimal characters")
        elif row["outcome"] == "historical":
            if row["head"] == final:
                report.add(where, "check-evidence", "historical evidence keeps its original head, not the final head; evidence "
                           "for the final head is `accepted` or `reviewer-executed`")
            cr.read_line(report, where, row, "reason")
        else:
            if row["head"] != final:
                report.add(where, "check-evidence", f"`{row['outcome']}` evidence is attributed to the final head; a result from "
                           "another head is `historical` and is never relabelled")
            if row["outcome"] == "reviewer-executed":
                cr.read_line(report, where, row, "reason")
    return delta, fixed, requirements, evidence


def new_items(report: vr.Report, state: State, doc: dict[str, Any], final: str,
              store: dict[str, Any] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """New findings and questions composed at the final head exactly as the composer renders a record's items."""
    findings, questions = [], []
    for key, compose, out in (("findings", cr.compose_finding, findings), ("questions", cr.compose_question, questions)):
        raw = doc.get(key)
        if not isinstance(raw, list):
            report.add(key, "schema", f"`{key}` must be a list (empty for none)")
            continue
        for index, value in enumerate(raw):
            item = compose(report, f"{key}[{index}]", value, final)
            if item is not None:
                out.append((f"{key}[{index}]", item, value))
    cr.check_identities(report, [(w, i) for w, i, _v in findings], [(w, i) for w, i, _v in questions], [])
    located = [(w, i) for w, i, _v in findings + questions]
    if store is None:
        cr.require_file_sides(report, located)
    else:
        context = store["context"]
        cr.check_store(report, store, {"target_kind": "range", "head": context.get("head"), "merge_base": context.get("merge_base")},
                       located)
        for _w, item, value in findings + questions:
            value["anchor"] = item["anchor"]  # a side the pinned manifest established is saved with the item
    for where, item, _value in findings + questions:
        if item["id"] in state.open:
            report.add(where, "stable-id", f"`{item['id']}` is already open in the chain; a stable id names one open item, "
                       "classified under `fixed_findings`")
    return [i for _w, i, _v in findings], [i for _w, i, _v in questions]


def apply_addendum(report: vr.Report, state: State, path: Path, doc: dict[str, Any], store: dict[str, Any] | None = None,
                   compose: bool = False) -> None:
    """Validate one addendum against the state before it and advance the state; ``compose`` fills derived fields."""
    where = str(path)
    if not compose:
        missing = [key for key in ADDENDUM_KEYS if key not in doc]
        missing += [f"verification.{k}" for k in VERIFICATION_KEYS if isinstance(doc.get("verification"), dict) and k not in doc["verification"]]
        if missing:
            report.add(where, "schema", f"missing {', '.join(f'`{k}`' for k in missing)}")
            return
        if not (isinstance(doc.get("workflow"), str) and doc["workflow"]):
            report.add(where, "schema", "`workflow` names the continuing reviewer's identifier")
    else:
        fr.settle(report, doc, "format", ADDENDUM_V2, "addendum", "this helper")
        fr.settle(report, doc, "workflow", vr.WORKFLOW, "addendum", "this review-code installation")
    fr.settle(report, doc, "record", str(state.record), "addendum", "the chain's current record", fr.same_path)
    fr.settle(report, doc, "record_format", state.schema, "addendum", "the chain's current record")
    fr.settle(report, doc, "reviewed_head", state.head, "addendum", "the chain's current head")
    if doc.get("format") != ADDENDUM_V2:
        report.add(where, "schema", f"`format` is `{ADDENDUM_V2}`")
    final = doc.get("final_head")
    if not sha(final):
        report.add("final_head", "trailer-sha", "`final_head` must be exactly 40 lowercase hexadecimal characters")
        return
    if final == state.head or any(entry["head"] == final for entry in state.chain):
        report.add("final_head", "chain", f"`{final}` is a head the chain already reviewed; a continuation reviews a new head")
    if "finalization" in doc and path.name != f"addendum-{final}.json":
        report.add(where, "chain", f"a finalized addendum is named `addendum-{final}.json`")
    final_meta = doc.get("finalization")
    if isinstance(final_meta, dict) and final_meta.get("report") != str(report_path(path)):
        report.add(where, "finalization", f"the report is `{report_path(path)}`, distinct from the record's; "
                   f"not {json.dumps(final_meta.get('report'))}")
    if compose and doc.get("replaced_by_full_review", None) is None:
        doc["replaced_by_full_review"] = None

    delta, fixed, requirements, evidence = check_rows(report, doc, final)
    if store is not None:
        order = [e["path"] for e in store["context"]["delta"]["manifest"] if isinstance(e, dict) and isinstance(e.get("path"), str)]
        authored = {row["path"] for _w, row in delta}
        for missing_path in [p for p in order if p not in authored]:
            report.add("delta", "file-accounting", f"`{missing_path}` is in the delta manifest and has no state; every delta "
                       "file needs a decision: `reviewed`, `ignored` with a reason, or `unreviewed`")
        for extra in sorted(authored - set(order)):
            report.add("delta", "file-accounting", f"`{extra}` is not in the delta manifest `{state.head}...{final}`")
        if isinstance(doc.get("delta"), list) and not report.lines:
            rows = {row["path"]: row for _w, row in delta}
            doc["delta"] = [rows[p] for p in dict.fromkeys(order)]

    before = set(state.open)
    closing: set[str] = set()
    for location, row in fixed:
        if row["classification"] not in FIXED_CLASSIFICATIONS:
            report.add(location, "fixed-findings", f"`classification` must be one of {list(FIXED_CLASSIFICATIONS)}")
        if row["id"] not in before:
            report.add(location, "fixed-findings", f"`{row['id']}` is not an open item in the chain; report an unknown id as a "
                       "coverage gap instead")
        elif row["classification"] == "fixed":
            closing.add(row["id"])
    if len({row["id"] for _l, row in fixed}) != len(fixed):
        report.add("fixed_findings", "stable-id", "an id is classified twice")
    findings, questions = new_items(report, state, doc, final, store)

    verification = doc.get("verification")
    if not isinstance(verification, dict):
        report.add("verification", "schema", "`verification` is an object with the `tasks` and `batches` this continuation added")
        return
    for key in ("tasks", "batches"):
        if key not in verification:
            report.add("verification", "schema", f"`{key}` is required; write an empty list when there is none")
    batches = verification.get("batches")
    for index, batch in enumerate(batches if isinstance(batches, list) else []):
        if isinstance(batch, dict):
            written = set(batch)
            fr.derive_batch(report, f"verification.batches[{index}]", batch)
            batches[index] = fr.ordered(batch, written, fr.BATCH_ORDER)
    phases = [b.get("phase") for b in batches if isinstance(b, dict)] if isinstance(batches, list) else []
    prior = state.allowance
    if "initial" in phases and prior["initial_spent"]:
        report.add("verification.batches", "verification", "the chain already spent its initial batch; a continuation "
                   "dispatches at most the follow-up")
    if "follow-up" in phases and prior["follow_up_spent"]:
        report.add("verification.batches", "verification", "the chain already spent its follow-up; a continuation or worker "
                   "change grants no further batch")
    if "follow-up" in phases and not prior["initial_spent"] and "initial" not in phases:
        report.add("verification.batches", "verification", "a follow-up batch needs the initial batch spent first")
    allowance = {"initial_spent": prior["initial_spent"] or "initial" in phases,
                 "follow_up_spent": prior["follow_up_spent"] or "follow-up" in phases, "carried_from": None}
    fr.settle(report, verification, "allowance", allowance, "verification", "the chain's spent flags and this addendum's batches",
              same_allowance)

    settled = {t.get("id") for t in verification.get("tasks", []) if isinstance(t, dict) and t.get("ruling") not in ("pending", "withheld")} \
        if isinstance(verification.get("tasks"), list) else set()
    carried = [entry for entry in state.outstanding if task_id(entry) not in settled]
    if compose and "outstanding" not in verification:
        verification["outstanding"] = carried
    written = verification.get("outstanding")
    if isinstance(written, list):
        kept = {task_id(e) for e in written if isinstance(e, str)}
        for entry in carried:
            if task_id(entry) not in kept:
                report.add("verification.outstanding", "carried-state", f"drops `{entry}`; outstanding work survives every addendum "
                           "until a task here settles it")
    for key in ("tasks", "batches", "allowance", "outstanding"):
        if key in verification:
            verification[key] = verification.pop(key)  # the saved key order
    if compose and "routed" not in doc:
        doc["routed"] = {key: list(state.routed[key]) for key in ROUTED}
    routed = doc.get("routed")
    if not isinstance(routed, dict):
        report.add("routed", "schema", "`routed` names `unresolved`, `disputed` and `unrecoverable_inputs`")
        routed = {}
    known = state.ids | {i["id"] for i in findings + questions}
    for key in ROUTED:
        entries = cr.read_lines(report, f"routed.{key}", routed.get(key, []))
        for entry in state.routed[key]:
            if entry not in entries:
                report.add(f"routed.{key}", "carried-state", f"drops `{entry}`; routed items survive every addendum")
        if key != "unrecoverable_inputs":
            for identity in entries:
                if identity not in known:
                    report.add(f"routed.{key}", "stable-id", f"`{identity}` is not an item id in the chain")

    coverage, status, gaps = doc.get("coverage"), doc.get("status"), doc.get("coverage_gaps")
    if coverage not in vr.COVERAGE:
        report.add("coverage", "trailer-grammar", f"`coverage` must be one of {list(vr.COVERAGE)}, not `{coverage!r}`")
    gaps = cr.read_lines(report, "coverage_gaps", gaps if gaps is not None else "missing")
    if coverage == "incomplete" and not gaps:
        report.add("coverage_gaps", "coverage-gaps", "`coverage` is `incomplete`, so `coverage_gaps` names each gap")
    if coverage == "complete" and gaps:
        report.add("coverage_gaps", "coverage-gaps", "`coverage_gaps` is non-empty, which contradicts `coverage=complete`")
    if status not in cr.STATUSES:
        report.add("status", "status-consistency", f"`status` must be one of {list(cr.STATUSES)}, not `{status!r}`")
    files = dict(state.files)
    files.update({row["path"]: dict(row) for _w, row in delta})
    unreviewed = sorted(p for p, row in files.items() if row.get("state") == "unreviewed")
    replacement = doc.get("replaced_by_full_review")
    if unreviewed and coverage == "complete" and replacement is None:  # a replacement's own file accounting governs it
        report.add("coverage", "coverage-gaps", f"{', '.join(f'`{p}`' for p in unreviewed)} stays `unreviewed`, which contradicts "
                   "`coverage=complete`; per-file coverage the delta did not reach stays as the chain left it")
    if routed.get("unrecoverable_inputs") and coverage == "complete":
        report.add("routed.unrecoverable_inputs", "coverage-gaps", "an unrecoverable input contradicts `coverage=complete`")
    if not report.lines:
        check = dict(verification, allowance=dict(verification["allowance"], carried_from=str(state.tip)))
        cr.read_verification(report, check, coverage, findings, questions)
    if replacement is None:  # a replacement's own items govern its status, checked in replace()
        after = {i: item for i, item in state.open.items() if i not in closing}
        for item in findings + questions:
            after[item["id"]] = item
        check_status(report, status, coverage, list(after.values()))
    if replacement is not None and not (isinstance(replacement, str) and replacement.startswith("/")):
        report.add("replaced_by_full_review", "record-paths", "is null or the replacement record's absolute path")
    if report.lines:
        return

    previous = state.tip
    for item in findings + questions:
        state.open[item["id"]] = {"id": item["id"], "type": item["type"], "action": item.get("action", "question"),
                                  "priority": item.get("priority"), "kind": item.get("kind"), "markdown": item["markdown"],
                                  "trailer": item["trailer"], "head": final, "source": where}
    for identity in closing:
        state.open.pop(identity, None)
    state.ids |= {i["id"] for i in findings + questions}
    state.files = files
    state.requirements.update({row["source"]: dict(row) for _w, row in requirements})
    state.check_evidence += [dict(row, source=where) for _w, row in evidence]
    state.tasks += [dict(task, source=where) for task in verification["tasks"]]
    state.batches += [dict(batch, source=where) for batch in verification["batches"]]
    for task in verification["tasks"]:
        if task.get("type") == "candidate" and task.get("ruling") == "confirmed":
            state.confirmations[task["id"]] = {"batch": f"carried:{path}#{task.get('batch')}", "trigger": task.get("trigger")}
    state.allowance = {k: verification["allowance"][k] for k in ("initial_spent", "follow_up_spent")}
    state.outstanding = list(verification["outstanding"])
    state.routed = {key: list(routed[key]) for key in ROUTED}
    state.status, state.coverage, state.coverage_gaps = status, coverage, list(gaps)
    state.fixed = [dict(row, source=where) for _l, row in fixed]
    state.head, state.tip, state.addendum = final, path, path
    meta = doc.get("finalization")
    state.tip_report = meta.get("report") if isinstance(meta, dict) else None
    state.chain.append({"kind": "addendum", "path": where, "format": ADDENDUM_V2, "reviewed_head": doc["reviewed_head"],
                        "head": final, "report": state.tip_report})
    if replacement is not None:
        replace(report, state, previous, path, doc, Path(os.path.abspath(replacement)), before)


def check_status(report: vr.Report, status: Any, coverage: Any, items: list[dict[str, Any]]) -> None:
    """`status` against the open items it summarizes, under the composer's status rules."""
    found = vr.Report()
    cr.check_status(found, status, coverage, [{"id": i.get("id"), "action": i.get("action")} for i in items if i.get("type") == "finding"],
                    [i for i in items if i.get("type") == "question"], [])
    for line in found.lines:
        report.add("status", *line.split(": ", 2)[1:])


def replace(report: vr.Report, state: State, previous: Path, addendum: Path, doc: dict[str, Any], path: Path,
            carried: set[str]) -> None:
    """Check that a replacement record carries the chain's state, then continue from it.

    ``carried`` names the items open before the addendum; only their confirmations have a chain file to carry from.
    """
    record = read_file(report, str(path), "replaced_by_full_review")
    if record is None:
        return
    where = f"replaced_by_full_review `{path}`"
    run = record.get("run") if isinstance(record.get("run"), dict) else {}
    accounting = record.get("record") if isinstance(record.get("record"), dict) else {}
    verification = accounting.get("verification") if isinstance(accounting.get("verification"), dict) else {}
    allowance = verification.get("allowance") if isinstance(verification.get("allowance"), dict) else {}
    if run.get("head") != doc["final_head"]:
        report.add(where, "chain", f"heads `{run.get('head')}`, not the addendum's final head `{doc['final_head']}`")
    if accounting.get("repository") != state.repository:
        report.add(where, "chain", f"reviews repository {json.dumps(accounting.get('repository'))}, not {json.dumps(state.repository)}")
    if (record.get("status"), run.get("coverage")) != (doc["status"], doc["coverage"]):
        report.add(where, "chain", "the addendum that names a replacement carries its status and coverage")
    carried_from = allowance.get("carried_from")
    if not any(fr.same_path(carried_from, str(p)) for p in (previous, addendum)):
        report.add(where, "carried-state", f"`allowance.carried_from` is {json.dumps(carried_from)}, not the chain file it "
                   f"replaced, `{previous}`")
    for flag in ("initial_spent", "follow_up_spent"):
        if state.allowance[flag] and allowance.get(flag) is not True:
            report.add(where, "carried-state", f"resets `{flag}`; spent allowance survives a replacement")
    own = [item for item in record.get("items", []) if isinstance(item, dict)]
    check_status(report, doc["status"], doc["coverage"], own)
    items = {item.get("id"): item for item in own}
    for identity, item in state.open.items():
        if identity not in items:
            report.add(where, "carried-state", f"drops open item `{identity}`")
        elif item["action"] == "must-fix" and items[identity].get("action") != "must-fix":
            report.add(where, "carried-state", f"carries open must-fix `{identity}` as {json.dumps(items[identity].get('action'))}; "
                       "an unsettled blocker survives a replacement until `fixed_findings` settles it")
    routed = accounting.get("routed") if isinstance(accounting.get("routed"), dict) else {}
    for key in ROUTED:
        for entry in state.routed[key]:
            if entry not in (routed.get(key) or []):
                report.add(where, "carried-state", f"drops routed `{key}` entry `{entry}`")
    outstanding = {task_id(e) for e in verification.get("outstanding") or [] if isinstance(e, str)}
    for entry in state.outstanding:
        if task_id(entry) not in outstanding:
            report.add(where, "carried-state", f"drops outstanding `{entry}`")
    tasks = {t.get("id"): t for t in verification.get("tasks") or [] if isinstance(t, dict)}
    for identity, confirmation in state.confirmations.items():
        if identity not in carried or identity not in state.open or state.open[identity]["type"] != "finding":
            continue
        task = tasks.get(identity, {})
        if (task.get("type"), task.get("ruling"), task.get("batch"), task.get("trigger")) != \
                ("candidate", "confirmed", confirmation["batch"], confirmation["trigger"]):
            report.add(where, "carried-state", f"open finding `{identity}` needs its confirmation carried as a `confirmed` candidate "
                       f"task with `batch: {confirmation['batch']}` and `trigger: {confirmation['trigger']}`, its original "
                       "accounting provenance")
    if report.lines:
        return
    open_record(report, state, path, record)


def load(record_path: str, interrupted_final: str | None = None) -> tuple[State, list[Path]]:
    files, interrupted = collect(record_path, interrupted_final)
    report, state = vr.Report(), State()
    for kind, path, doc in files:
        if kind == "record":
            if state.chain:
                continue  # a replacement: apply_addendum already opened it
            open_record(report, state, path, doc)
        else:
            apply_addendum(report, state, path, doc)
        if report.lines:
            raise Invalid(report.lines)
    return state, interrupted


# --- output ---------------------------------------------------------------------------------------------------------


def summary_lines(state: State) -> str:
    lines = [f"status {state.status}", f"coverage {state.coverage}", f"head {state.head}", f"record {state.record}"]
    if state.addendum is not None:
        lines.append(f"addendum {state.addendum}")
    lines.append(f"report {state.tip_report}" if state.tip_report else f"legacy {state.addendum or state.record}")
    lines.append(f"continuation {SCRIPT}")
    return "".join(line + "\n" for line in lines)


def state_json(state: State) -> dict[str, Any]:
    return {"status": state.status, "coverage": state.coverage, "coverage_gaps": state.coverage_gaps, "head": state.head,
            "repository": state.repository, "record": str(state.record), "record_schema": state.schema,
            "addenda": str(state.addenda), "tip": str(state.tip), "addendum": str(state.addendum) if state.addendum else None,
            "report": state.tip_report, "chain": state.chain,
            "open": list(state.open.values()), "fixed": state.fixed, "files": list(state.files.values()),
            "requirements": list(state.requirements.values()), "check_evidence": state.check_evidence,
            "verification": {"tasks": state.tasks, "batches": state.batches, "allowance": state.allowance,
                             "outstanding": state.outstanding},
            "confirmations": state.confirmations, "routed": state.routed, "continuation": str(SCRIPT)}


def legacy_lines(error: Legacy) -> str:
    lines = ["legacy-chain-needs-mapping"] + [f"chain {fmt} {path}" for fmt, path in error.files]
    if error.floor:
        lines.append(f"floor {error.floor['from']}")
        lines.append(f"floor allowance {json.dumps(error.floor['allowance'])}")
        lines.append(f"floor outstanding {json.dumps(error.floor['outstanding'])}")
        lines.append(f"floor routed {json.dumps(error.floor['routed'])}")
    lines.append("map these files under references/continuation-addendum.md's Version 1 chains; this is neither approval "
                 "nor a fresh chain or allowance")
    return "".join(line + "\n" for line in lines)


def render(state: State, reviewed: str, doc: dict[str, Any], inputs: dict[str, str]) -> str:
    """The complete current result after this addendum, through the finalizer's shared ledger sections."""
    code = fr.code
    parts = [f"# Continuation report\n\nProfile `implementation-gate`; status **{state.status}**; coverage `{state.coverage}`. "
             "`continue_review.py` generated this report from the validated chain; it replaces no earlier report.",
             f"## Chain\n\nDelta `{reviewed}...{state.head}` continues the record at {code(state.record)}.\n\n"
             + "\n".join(f"- {entry['kind'].capitalize()} {code(entry['path'])}: head `{entry['head']}`." for entry in state.chain)]
    counts = {"must-fix": 0, "consider": 0, "question": 0}
    for item in state.open.values():
        counts[item["action"] if item["type"] == "finding" else "question"] += 1
    parts.append(f"## Open items\n\n{counts['must-fix']} must-fix, {counts['consider']} consider, {counts['question']} "
                 "question(s) open at the final head." + "".join(
                     f"\n\n### {code(item['id'])} (from {code(item['source'])})\n\n{item['markdown']}\n\n{item['trailer']}"
                     for item in state.open.values()))
    rows = [f"- {code(row['id'])}: {row['classification']}. {row['evidence']}" for row in state.fixed]
    parts.append("## Reported fixes\n\n" + ("\n".join(rows) or "None reported."))
    rows = [f"- {code(row['path'])}: {row['state']}" + (f", {row['reason']}" if row.get("reason") else "") for row in doc["delta"]]
    parts.append("## Delta coverage\n\n" + ("\n".join(rows) or "The delta changes no file."))
    parts.append("## Coverage gaps\n\n" + ("\n".join(f"- {gap}" for gap in state.coverage_gaps) or "None."))
    parts.extend(fr.ledger_sections(state.ledgers()))
    paths = [("addendum", str(state.addendum)), ("record", str(state.record)), *inputs.items(), ("continuation", str(SCRIPT))]
    parts.append("## Artifacts\n\n" + "\n".join(f"- {name}: {code(path)}" for name, path in paths))
    return "\n\n".join(parts) + "\n"


def link(data: bytes, target: Path) -> None:
    """Write ``data`` beside ``target`` and link it into place, never replacing a file."""
    part = target.with_name(target.name + ".part")
    try:
        part.unlink()
    except FileNotFoundError:
        pass
    part.write_bytes(data)
    try:
        os.link(part, target)
    finally:
        part.unlink()


def compose(args: argparse.Namespace) -> int:
    try:
        with open(args.store, encoding="utf-8") as handle:
            store = json.load(handle)
    except (OSError, ValueError) as error:
        print(f"continue_review: cannot read store {args.store}: {error}", file=sys.stderr)
        return 2
    try:
        with open(args.input, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, ValueError) as error:
        print(f"continue_review: cannot read input {args.input}: {error}", file=sys.stderr)
        return 2
    report = vr.Report()
    context = store.get("context") if isinstance(store, dict) and store.get("format") == rc.STORE_FORMAT else None
    delta = context.get("delta") if isinstance(context, dict) else None
    if not isinstance(context, dict) or not sha(context.get("head")):
        report.add("store", "schema", f"expected a `{rc.STORE_FORMAT}` store from review_context.py --store")
    elif not isinstance(delta, dict) or not isinstance(delta.get("manifest"), list):
        report.add("store", "schema", "the store carries no delta; build it with --prior-head <the chain's current head>")
    elif (delta.get("conditions") or {}).get("prior-head-reachable") != "yes":
        report.add("store", "schema", "the store could not reach its prior head, so it establishes no delta")
    if not isinstance(doc, dict):
        report.add("input", "schema", "the continuation input must be a JSON object")
    if report.lines:
        print("".join(line + "\n" for line in report.lines), end="")
        return 1
    final = context["head"]
    try:
        state, interrupted = load(args.record, final)
    except Legacy as error:
        sys.stdout.write(legacy_lines(error))
        return 1
    except Invalid as error:
        sys.stdout.write("chain-invalid\n" + "".join(line + "\n" for line in error.lines))
        return 1
    if delta.get("prior_head") != state.head:
        report.add("store", "chain", f"the store's delta starts at `{delta.get('prior_head')}`, not the chain's current head `{state.head}`")
    unknown = sorted(set(doc) - set(ADDENDUM_KEYS))
    if unknown:
        report.add("input", "schema", f"unknown keys {unknown}")
    for key in AUTHORED:
        if key not in doc:
            report.add("input", "schema", f"`{key}` is a continuation decision and is required; write an empty list when there is none")
    fr.settle(report, doc, "final_head", final, "input", "the store")
    if report.lines:
        print("".join(line + "\n" for line in report.lines), end="")
        return 1
    target = state.addenda / f"addendum-{final}.json"
    marker = report_path(target)
    doc["finalization"] = {"protocol": cr.FINALIZATION_PROTOCOL, "profile": "implementation-gate", "report": str(marker),
                           "inputs": {"store": os.path.abspath(args.store), "input": os.path.abspath(args.input)}}
    reviewed = state.head
    apply_addendum(report, state, target, doc, store, compose=True)
    if report.lines:
        print("".join(line + "\n" for line in report.lines), end="")
        return 1
    if target.exists() and target not in interrupted:
        print(f"{target}: chain: exists and is never overwritten; a continuation writes a new final head's addendum")
        return 1
    if marker.exists():
        print(f"{marker}: chain: exists without its addendum; remove it only after confirming no continuation wrote it")
        return 1
    saved = {key: doc[key] for key in ADDENDUM_KEYS}
    saved["finalization"] = doc["finalization"]
    written: list[Path] = []
    try:
        state.addenda.mkdir(parents=True, exist_ok=True)
        for stale in interrupted:
            stale.unlink()
        text = render(state, reviewed, saved, {"store": os.path.abspath(args.store), "input": os.path.abspath(args.input)})
        link((json.dumps(saved, indent=2) + "\n").encode("utf-8"), target)
        written.append(target)
        link(text.encode("utf-8"), marker)  # the success marker, promoted last
    except BaseException as error:
        for path in written:
            try:
                path.unlink()
            except OSError:
                pass
        if not isinstance(error, OSError):
            raise
        print(f"continue_review: cannot write the addendum: {error}; nothing this run wrote is left consumable", file=sys.stderr)
        return 2
    sys.stdout.write(summary_lines(state))
    return 0


def example() -> dict[str, Any]:
    """What a continuation writes; the helper derives the rest from the chain and the store."""
    final = "c3d4e5f60718293a4b5c6d7e8f90123456789abc"
    return {
        "delta": [{"path": "src/retry-policy.ts", "state": "reviewed"},
                  {"path": "docs/notes.md", "state": "ignored", "reason": "generated changelog"}],
        "fixed_findings": [{"id": "payments/retry-idempotency", "classification": "fixed",
                            "evidence": "src/retry-policy.ts:18 now reuses one key per logical charge; test_retry passes at the final head"}],
        "findings": [], "questions": [],
        "requirements": [{"source": "issue-123/acceptance-criterion-2", "class": "acceptance", "disposition": "met",
                          "evidence": "src/retry-policy.ts:18 reuses the key; tests/test_retry.ts:40"}],
        "check_evidence": [{"check": "pnpm test payments", "head": final, "outcome": "reviewer-executed",
                            "reason": "the fix changes the retry policy the suite covers"}],
        "verification": {
            "tasks": [{"id": "premise-2", "type": "safety-premise", "area": "data-integrity",
                       "premise": "Every retry of one charge reads the key stored before the first attempt.",
                       "evidence": "src/retry-policy.ts:12-18", "batch": "follow-up", "ruling": "holds"}],
            "batches": [{"bundle": "/tmp/continuation-XXXXXX/follow-up",
                         "accounting": "/tmp/continuation-XXXXXX/follow-up/accounting.json", "operation": "Agent run_in_background=false"}]},
        "status": "Approved", "coverage": "complete", "coverage_gaps": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--example", action="store_true", help="print the continuation input a reviewer writes, then exit")
    commands = parser.add_subparsers(dest="command")
    state_parser = commands.add_parser("state", help="validate the chain and print its current state")
    state_parser.add_argument("--json", action="store_true", help="print the whole current state as JSON")
    state_parser.add_argument("record", help="absolute path of the chain's record.json")
    compose_parser = commands.add_parser("compose", help="validate and save the next addendum")
    compose_parser.add_argument("--record", required=True, help="absolute path of the chain's record.json")
    compose_parser.add_argument("--store", required=True, help="the continuation's review_context.py store, built with --prior-head")
    compose_parser.add_argument("input", help="the continuation's authored decisions")
    args = parser.parse_args()
    if args.example:
        print(json.dumps(example(), indent=2))
        return 0
    if args.command == "compose":
        return compose(args)
    if args.command != "state":
        parser.error("choose `state`, `compose` or --example")
    if not os.path.isfile(args.record):
        print(f"continue_review: cannot read record {args.record}", file=sys.stderr)
        return 2
    try:
        state, _interrupted = load(args.record)
    except Legacy as error:
        sys.stdout.write(legacy_lines(error))
        return 1
    except Invalid as error:
        sys.stdout.write("chain-invalid\n" + "".join(line + "\n" for line in error.lines))
        return 1
    sys.stdout.write(json.dumps(state_json(state), indent=2) + "\n" if args.json else summary_lines(state))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
