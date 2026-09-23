#!/usr/bin/env python3
"""Compose, validate, and write review-code's step-5 artifacts and report in one call.

Usage:
    python3 scripts/finalize_review.py --store STORE [--packet PACKET] [--fingerprint-input FILE] [--compact] PRIVATE_DIR
    python3 scripts/finalize_review.py --profile implementation-gate --store STORE [--fingerprint-input FILE] [--compact] PRIVATE_DIR
    python3 scripts/finalize_review.py --check [--profile implementation-gate] PRIVATE_DIR

Reads PRIVATE_DIR/composition.json. Finalization requires its private
accounting for both profiles: a `record` section naming `repository`,
`requirements`, `files`, `check_evidence`, `verification` (`tasks`,
`batches`, `allowance`, `outstanding`) and `routed` (`unresolved`,
`disputed`, `unrecoverable_inputs`), each explicitly, empty lists included.
Nothing is defaulted, and the composer checks their content.

Mechanical fields an authoritative saved input already owns may be omitted,
and are filled before anything else runs; an explicit copy that disagrees is
refused, and an omitted field no input establishes is named:

    store              run.head, run.merge_base; with a working-tree snapshot,
                       run.target_kind (worktree) and run.tree
    --packet           run.target_kind (pull-request), run.base_ref,
                       run.base_sha, run.merged, run.repository_url,
                       run.issues; its pinned head must be the store's
    --fingerprint-input  the saved context_fingerprint.py input (`specs`
                       alone with --packet, which supplies `pr` and
                       `issues`). A range's run.target (`pr.title`), a local
                       target's run.change_description (`pr.body`, byte for
                       byte) and run.specs (spec identities), run.issues
                       without a packet, and run.context: its digest, with
                       guidance derived at run.base_sha exactly as
                       context_fingerprint.py --guidance-base does. An
                       explicit `context`, such as one computed early for the
                       duplicate-review shortcut, must equal it. A working
                       tree's `pr.title` must be `worktree tree=<run.tree>`.
    a local target     run.merged (false)
    this run           record.paths private_dir, store, composition,
                       skill_root, and addenda for the gate
    each batch         `name` and `phase` from its bundle's manifest.json,
                       `raw_return` from its accounting report, whose
                       manifest_sha256 must match that manifest

Without --fingerprint-input, `run.context` is required as before. Judgments
are never derived: coverage, status, requirement dispositions, file states,
task selection and rulings stay authored and checked.

Each prior item may add `reply` (drafted reply prose, or null), `thread_id` and
`comment_id`: both null for an item without a forge thread, otherwise the
thread's node id and its first comment's numeric id in the read-only
`--packet`. A reply needs a thread, a `disputed` item has none, and the
finalizer appends the prior-item trailer to `fixed`, `accepted`, `obsolete`
and `still-open` replies. These fields never reach the payload.

Stages, in order:

    derive      fill and check the mechanical fields above      -> nothing
    accounting  the checks above                                -> nothing
    compose     compose_review.py --store STORE - < the derived composition
                                                                  -> payload.json (publishable)
    record      compose_review.py --profile implementation-gate --store STORE
                - < the derived composition                       -> record.json  (implementation-gate)
    emit-batch  validate_review.py --emit-batch < payload.json    -> batch.json   (publishable)
    render      validate_review.py --render < payload.json        -> fragments.md (publishable)
    report      the summary body, the full body of each line-anchored finding and
                question it indexes, the private ledgers, routed state and
                drafted replies                                   -> report.md

Every output is staged as `<artifact>.part` and promoted only after every
stage passed, with `report.md` last: it is the success marker. A new gate
record, and the retained publishable composition (rewritten in place before
promotion), carry `finalization`: this protocol, the profile, the absolute
report path, the absolute store, packet and fingerprint input paths (null
when not given) that reproduce the digest, and each prior item's id,
classification, thread ids and rendered reply body (or null). Consumers
accept new-protocol output only with that report present; a record or
composition without `finalization` predates it. The gate creates
PRIVATE_DIR/addenda, where continuations append.

Before modifying anything, a run is refused when an addenda directory (this
directory's, or the one an existing record names) holds any entry, or when an
existing record cannot be read to name its addenda directory: replacing that
chain's record or composition would orphan it, so use a fresh private
directory. An empty addenda directory is not an active chain. Otherwise the
report and every earlier consumable output of either profile are removed
first, and a failed stage, write, or promotion removes what this run staged or
promoted, so no stale or partial output reads as success. Store, packet,
bundles and addenda are never touched.

A private directory has one writer at a time. A retry, rerun, or
continuation starts only after the earlier finalizer or reviewer has
exited, including one a host timed out. Overlapping writers are
unsupported, and neither the report marker nor the chain guard detects
them.

Default stdout is unchanged: `fragments.md` for publishable, `record
PRIVATE_DIR/record.json` for the gate. `--compact` prints `status`,
`coverage`, then one `<name> <absolute path>` line per output, report last.
`--check` modifies nothing: it prints the same lines for complete
new-protocol output, or `legacy <artifact path>` for valid pre-protocol
output, and otherwise one line per reason at exit 1.

A failing stage prints `<stage> failed with exit <status>; later stages did
not run:` followed by its output. Stages run as `python3 <script>`, the
interpreter the step itself names.

Exit codes:
    0  every stage passed, or --check found consumable output
    1  a content violation, a refused rerun, or unconsumable output under --check
    2  an input, store, or packet cannot be read, a stage cannot be started,
       or an output cannot be removed, written, or promoted
    *  otherwise, the failing stage's own status
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import compose_review as cr
import context_fingerprint as cf
import validate_review as vr

SCRIPTS = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS.parent
ARTIFACTS = {"publishable": ("payload.json", "batch.json", "fragments.md"), "implementation-gate": ("record.json",)}
REPORT = "report.md"
RECORD_SECTIONS = ("repository", "paths", "requirements", "files", "check_evidence", "verification", "routed")
VERIFICATION_SECTIONS = ("tasks", "batches", "allowance", "outstanding")
ROUTED_SECTIONS = ("unresolved", "disputed", "unrecoverable_inputs")
TRAILED = ("fixed", "accepted", "obsolete", "still-open")
LEGACY_SCHEMA = "implementation-gate-record/2"
LOCAL = ("range", "worktree")
# Where the finalizer fills a key, the keys take the order compositions have always written them in, so a derived
# record serializes as a transcribed one did; a fully written object keeps its own order.
PATH_ORDER = ("private_dir", "store", "composition", "addenda", "skill_root")
BATCH_ORDER = ("name", "phase", "bundle", "raw_return", "accounting", "operation")


class Stop(Exception):
    """A stage or write failed; its output is already printed."""

    def __init__(self, status: int) -> None:
        super().__init__(status)
        self.status = status


def fail(stage: str, status: int, output: str) -> Stop:
    sys.stdout.write(f"{stage} failed with exit {status}; later stages did not run:\n{output}")
    sys.stdout.flush()
    return Stop(status)


def read_json(path: Path, what: str, stage: str = "derive") -> Any:
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        raise fail(stage, 2, f"finalize_review: cannot read {what} {path}: {error}\n")


def run(stage: str, command: list[str], stdin: bytes | None = None) -> bytes:
    try:
        result = subprocess.run(["python3", *command], input=stdin, capture_output=True)
    except OSError as error:
        print(f"finalize_review: cannot start {stage}: {error}", file=sys.stderr)
        raise Stop(2)
    if result.returncode != 0:
        raise fail(stage, result.returncode, (result.stdout + result.stderr).decode("utf-8", "replace"))
    return result.stdout


# --- derive -------------------------------------------------------------------


def same_path(explicit: Any, owned: str) -> bool:
    return isinstance(explicit, str) and (os.path.abspath(explicit) == os.path.abspath(owned)
                                          or os.path.realpath(explicit) == os.path.realpath(owned))


def same_set(explicit: Any, owned: list[str]) -> bool:
    return isinstance(explicit, list) and all(isinstance(v, str) for v in explicit) and sorted(explicit) == sorted(owned)


def settle(report: vr.Report, holder: dict[str, Any], key: str, owned: Any, where: str, source: str, same: Any = None) -> None:
    """Fill an omitted mechanical field from the input that owns it; refuse an explicit copy that disagrees."""
    if owned is None:
        if key not in holder:
            report.add(where, "derived-field", f"`{key}` is omitted and {source} does not establish it")
    elif key not in holder:
        holder[key] = owned
    elif not (same(holder[key], owned) if same else holder[key] == owned):
        report.add(where, "derived-field", f"`{key}={json.dumps(holder[key], ensure_ascii=False)}` conflicts with "
                   f"{json.dumps(owned, ensure_ascii=False)} from {source}; omit it and the finalizer supplies it")


def ordered(value: dict[str, Any], written: set[str], order: tuple[str, ...]) -> dict[str, Any]:
    if set(value) == written:
        return value
    return {**{key: value[key] for key in order if key in value}, **{k: v for k, v in value.items() if k not in order}}


def text_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def derive_packet(report: vr.Report, run: dict[str, Any], packet: dict[str, Any], context: dict[str, Any]) -> None:
    pr = packet.get("pr")
    if not isinstance(pr, dict):
        report.add("packet", "schema", "the packet carries no `pr` section; normalize the saved pages with forge_packet.py")
        return
    settle(report, run, "target_kind", "pull-request", "run", "the packet")
    pinned = text_or_none(pr.get("head_sha"))
    if pinned is not None and isinstance(context.get("head"), str) and pinned != context["head"]:
        report.add("run.head", "derived-field", f"the packet pins head `{pinned}`, but the store was built for `{context['head']}`")
    settle(report, run, "base_ref", text_or_none(pr.get("base_ref")), "run", "the packet")
    settle(report, run, "base_sha", text_or_none(pr.get("base_sha")), "run", "the packet")
    settle(report, run, "merged", pr.get("merged") if isinstance(pr.get("merged"), bool) else None, "run", "the packet")
    settle(report, run, "repository_url", text_or_none(packet.get("repository_url")), "run", "the packet")
    fingerprint = packet.get("fingerprint")
    issues = fingerprint.get("issues") if isinstance(fingerprint, dict) else None
    coordinates = [issue.get("coordinate") for issue in issues if isinstance(issue, dict)] if isinstance(issues, list) else []
    coordinates = coordinates if isinstance(issues, list) and all(isinstance(c, str) for c in coordinates) else None
    settle(report, run, "issues", coordinates, "run", "the packet's fingerprint issues", same_set)


def derive_context(report: vr.Report, args: argparse.Namespace, run: dict[str, Any], packet: Any) -> None:
    """Fields the saved fingerprint input owns, and the digest over it computed by context_fingerprint.py's rules."""
    if args.fingerprint_input is None:
        if "context" not in run:
            report.add("run", "derived-field", "`context` is omitted; pass --fingerprint-input so the finalizer computes it from the saved inputs")
        return
    saved = read_json(Path(args.fingerprint_input), "fingerprint input")
    if not isinstance(saved, dict):
        report.add("fingerprint", "schema", "the fingerprint input must be a JSON object")
        return
    if "guidance" in saved:
        report.add("fingerprint.guidance", "schema", "the finalizer derives `guidance` at the base from the store; omit it")
        return
    if packet is None and "pr" not in saved:
        report.add("fingerprint.pr", "schema", "`pr` is required unless --packet supplies it")
        return
    try:
        inputs = cf.merge_packet(saved, args.packet) if packet is not None else dict(saved)
        normalized = cf.normalize(inputs)
    except (OSError, ValueError) as error:
        report.add("fingerprint", "schema", str(error))
        return
    source = "the fingerprint input"
    if packet is None:
        settle(report, run, "issues", [issue["coordinate"] for issue in normalized["issues"]], "run", f"{source}'s `issues`", same_set)
    kind = run.get("target_kind", "pull-request")
    if kind in LOCAL:
        title = normalized["pr"]["title"]
        if kind == "range":
            settle(report, run, "target", title or None, "run", f"{source}'s `pr.title`")
        elif isinstance(run.get("tree"), str) and title != f"worktree tree={run['tree']}":
            report.add("fingerprint.pr.title", "derived-field",
                       f"a working tree's `pr.title` is `worktree tree={run.get('tree')}`, not {json.dumps(title, ensure_ascii=False)}")
        settle(report, run, "change_description", normalized["pr"]["body"], "run", f"{source}'s `pr.body`")
        settle(report, run, "specs", [spec["identity"] for spec in normalized["specs"]], "run", f"{source}'s `specs`", same_set)
    base = run.get("base_sha")
    if report.lines or not (isinstance(base, str) and vr.COMMIT_SHA_RE.fullmatch(base)):
        return  # a refused field or an unusable base leaves no inputs to digest; the composer names the base
    try:
        inputs["guidance"] = cf.derive_guidance(base, args.store)
    except (OSError, ValueError) as error:
        raise fail("derive", 2, f"finalize_review: cannot derive guidance at `{base}` from `{args.store}`: {error}\n")
    digest = cf.digest(inputs)
    if run.setdefault("context", digest) != digest:
        report.add("run.context", "derived-field",
                   f"`context={run['context']}` is not the digest of the saved inputs, `{digest}`; a digest computed earlier, "
                   "such as for the duplicate-review shortcut, would bind this review to another context, so recompute "
                   "that decision from the saved inputs")


def derive_batch(report: vr.Report, where: str, batch: dict[str, Any]) -> None:
    """A batch's identity from its bundle manifest and its raw return from the accounting report reconciled."""
    bundle, accounting = batch.get("bundle"), batch.get("accounting")
    manifest_bytes, identity = None, {}
    if isinstance(bundle, str):
        try:
            manifest_bytes = (Path(bundle) / "manifest.json").read_bytes()
            manifest = json.loads(manifest_bytes)
            identity = manifest["batch"] if isinstance(manifest, dict) and isinstance(manifest.get("batch"), dict) else {}
        except (OSError, ValueError):
            manifest_bytes = None
    source = f"bundle manifest `{bundle}/manifest.json`"
    settle(report, batch, "name", text_or_none(identity.get("id")), where, source)
    settle(report, batch, "phase", text_or_none(identity.get("phase")), where, source)
    reconciled: Any = {}
    if isinstance(accounting, str):
        reconciled, _why = cr.load_object(accounting)
        reconciled = reconciled or {}
    settle(report, batch, "raw_return", text_or_none(reconciled.get("raw_return")), where, f"accounting report `{accounting}`", same_path)
    hashed = reconciled.get("manifest_sha256")
    if manifest_bytes is not None and isinstance(hashed, str) and hashed != hashlib.sha256(manifest_bytes).hexdigest():
        report.add(where, "derived-field", f"accounting report `{accounting}` accounts a return to another manifest than `{bundle}/manifest.json`")


def derive_run(report: vr.Report, args: argparse.Namespace, run: dict[str, Any], packet: Any, store: Any) -> None:
    """Run identity from the store, the packet and the fingerprint input."""
    context = store.get("context") if isinstance(store, dict) and isinstance(store.get("context"), dict) else {}
    settle(report, run, "head", text_or_none(context.get("head")), "run", "the store")
    settle(report, run, "merge_base", text_or_none(context.get("merge_base")), "run", "the store")
    snapshot = context.get("snapshot") if isinstance(context.get("snapshot"), dict) else None
    if snapshot is not None:
        settle(report, run, "target_kind", "worktree", "run", "the store's working-tree snapshot")
    if run.get("target_kind") == "worktree":
        settle(report, run, "tree", text_or_none((snapshot or {}).get("tree")), "run", "the store's snapshot")
    if isinstance(packet, dict) and packet.get("schema") == "forge-packet/1":
        derive_packet(report, run, packet, context)
    if run.get("target_kind") in LOCAL:
        settle(report, run, "merged", False, "run", "a local target")
    derive_context(report, args, run, packet)


def derive(args: argparse.Namespace, private: Path, composition: Any, packet: Any, store: Any) -> tuple[Any, list[str]]:
    """The composition with omitted mechanical fields filled from the inputs that own them, and every conflict."""
    report = vr.Report()
    if not isinstance(composition, dict):
        return composition, []  # the accounting check names the malformed input
    composition = copy.deepcopy(composition)
    if isinstance(composition.get("run"), dict):
        derive_run(report, args, composition["run"], packet, store)
    record = composition.get("record")
    if isinstance(record, dict):
        paths = record.setdefault("paths", {})
        if isinstance(paths, dict):
            written = set(paths)
            owned = {"private_dir": str(private), "store": os.path.abspath(args.store),
                     "composition": str(private / "composition.json"), "skill_root": str(SKILL_ROOT)}
            if args.profile == "implementation-gate":
                owned["addenda"] = str(private / "addenda")
            for key, value in owned.items():
                settle(report, paths, key, value, "record.paths", "this finalizer run", same_path)
            record["paths"] = ordered(paths, written, PATH_ORDER)
        verification = record.get("verification")
        batches = verification.get("batches") if isinstance(verification, dict) else None
        for index, batch in enumerate(batches if isinstance(batches, list) else []):
            if isinstance(batch, dict):
                written = set(batch)
                derive_batch(report, f"record.verification.batches[{index}]", batch)
                batches[index] = ordered(batch, written, BATCH_ORDER)
    return composition, report.lines


# --- accounting ---------------------------------------------------------------


def packet_threads(packet: Any, report: vr.Report) -> dict[str, int | None]:
    """Each packet thread's node id and its first comment's numeric id."""
    if not isinstance(packet, dict) or packet.get("schema") != "forge-packet/1" or not isinstance(packet.get("threads"), list):
        report.add("packet", "schema", "expected a `forge-packet/1` packet from forge_packet.py normalize")
        return {}
    threads: dict[str, int | None] = {}
    for thread in packet["threads"]:
        if isinstance(thread, dict) and isinstance(thread.get("id"), str):
            comments = thread.get("comments")
            first = comments[0].get("id") if isinstance(comments, list) and comments and isinstance(comments[0], dict) else None
            threads[thread["id"]] = int(first) if isinstance(first, str) and first.isdigit() else None
    return threads


def check_replies(report: vr.Report, priors: Any, packet: Any) -> None:
    if not isinstance(priors, list):
        return  # the composer names a malformed list
    threads = None if packet is None else packet_threads(packet, report)
    for index, prior in enumerate(priors):
        where = f"prior_items[{index}]"
        if not isinstance(prior, dict):
            continue
        reply, thread, comment = prior.get("reply"), prior.get("thread_id"), prior.get("comment_id")
        if reply is not None and not (isinstance(reply, str) and reply.strip()):
            report.add(where, "prior-reply", "`reply` is the drafted reply prose, or null for none")
            reply = None
        if isinstance(reply, str) and "<!-- prior-item" in reply:
            report.add(where, "prior-reply", "`reply` carries a prior-item trailer; the finalizer appends it where required")
        if prior.get("classification") == "disputed" and reply is not None:
            report.add(where, "prior-reply", "a disputed item is not reposted, so it drafts no `reply`")
        if thread is None and comment is None:
            if reply is not None:
                report.add(where, "prior-reply", "a drafted `reply` needs the packet's `thread_id` and `comment_id` for its existing thread")
            continue
        if not (isinstance(thread, str) and thread) or not (isinstance(comment, int) and not isinstance(comment, bool)):
            report.add(where, "prior-reply", "`thread_id` (node id) and `comment_id` (integer) are both set, or both null for an item without a forge thread")
        elif threads is None:
            report.add(where, "prior-reply", "thread ids are checked against the forge packet; pass `--packet`")
        elif thread not in threads:
            report.add(where, "prior-reply", f"`thread_id={thread}` names no thread in the packet")
        elif threads[thread] != comment:
            report.add(where, "prior-reply", f"`comment_id={comment}` is not the first comment of thread `{thread}` in the packet ({threads[thread]})")


def check_accounting(composition: Any, packet: Any) -> list[str]:
    """Presence of every accounting section, never defaulted, and packet-bound reply ids; the composer checks content."""
    report = vr.Report()
    if not isinstance(composition, dict):
        report.add("input", "schema", "the composition input must be a JSON object")
        return report.lines
    record = composition.get("record")
    if not isinstance(record, dict):
        report.add("record", "accounting", "finalization requires the private `record` accounting for either profile; nothing is defaulted")
    else:
        for key in RECORD_SECTIONS:
            if key not in record:
                report.add("record", "accounting", f"`{key}` is required; write an empty list when there is none")
        for key, keys in (("verification", VERIFICATION_SECTIONS), ("routed", ROUTED_SECTIONS)):
            if isinstance(record.get(key), dict):
                for inner in keys:
                    if inner not in record[key]:
                        report.add(f"record.{key}", "accounting", f"`{inner}` is required; nothing is defaulted")
    check_replies(report, composition.get("prior_items", []), packet)
    return report.lines


def rendered_replies(composition: dict[str, Any]) -> list[dict[str, Any]]:
    """Each prior item's thread ids and drafted reply, with the prior-item trailer appended where required."""
    head = composition["run"]["head"]
    replies = []
    for prior in composition.get("prior_items", []):
        body = prior.get("reply")
        if body is not None and prior["classification"] in TRAILED:
            body = (f"{body.rstrip()}\n\n<!-- prior-item id={prior['id']} "
                    f"classification={prior['classification']} head={head} -->")
        replies.append({"id": prior["id"], "classification": prior["classification"],
                        "thread_id": prior.get("thread_id"), "comment_id": prior.get("comment_id"), "body": body})
    return replies


# --- report -------------------------------------------------------------------


def code(value: Any) -> str:
    text = str(value)
    ticks = "`" * (max((len(run) for run in re.findall(r"`+", text)), default=0) + 1)
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{ticks}{pad}{text}{pad}{ticks}"


def fenced(text: str) -> str:
    ticks = "`" * max(3, max((len(run) for run in re.findall(r"`+", text)), default=0) + 1)
    return f"{ticks}markdown\n{text.rstrip(chr(10))}\n{ticks}"


def ids(values: list[str]) -> str:
    return ", ".join(code(value) for value in values) if values else "none"


def render_report(profile: str, composition: dict[str, Any], payload: dict[str, Any],
                  replies: list[dict[str, Any]], outputs: list[tuple[str, Path]]) -> str:
    record, run_fields = composition["record"], composition["run"]
    parts = [f"# Review report\n\nProfile `{profile}`; status **{composition['summary']['status']}**; coverage "
             f"`{run_fields['coverage']}`. `finalize_review.py` generated this report from the validated composition. "
             "The summary body below is the one the payload carries.",
             payload["summary"]["body"].rstrip("\n")]

    target = run_fields.get("target_kind", "pull-request")
    lines = [f"- Repository: {code(record['repository'])}", f"- Target: {target}"
             + (f" {code(run_fields['target'])}" if run_fields.get("target") else "")
             + (f", tree `{run_fields['tree']}`" if run_fields.get("tree") else ""),
             f"- Merged: {'yes' if run_fields.get('merged') else 'no'}"
             + (", publication separately authorized" if run_fields.get("publication_authorized") else "")]
    if run_fields.get("prior_head"):
        lines.append(f"- Prior head: `{run_fields['prior_head']}`")
    if run_fields.get("specs"):
        lines.append(f"- Specs: {ids(run_fields['specs'])}")
    parts.append("## Run\n\nHead, base, merge-base, workflow, context digest, issues and coverage are in the run trailer above.\n\n"
                 + "\n".join(lines))

    inline = [item for item in payload["items"] if item["type"] != "observation" and item["anchor"].get("type") == "line"]
    if inline:
        parts.append("## Line comments\n\nThe full body of each line-anchored item the summary indexes.\n\n"
                     + "\n\n".join(f"### {code(item['id'])}\n\n{item['markdown']}\n\n{item['trailer']}" for item in inline))

    rows = [f"- {code(r['source'])} ({r['class']}): {r['disposition']}. {r['evidence']}" for r in record["requirements"]]
    parts.append("## Requirements\n\n" + ("\n".join(rows) or "None recorded."))
    rows = [f"- {code(f['path'])}: {f['state']}" + (f", {f['reason']}" if f.get("reason") else "") for f in record["files"]]
    parts.append("## File coverage\n\n" + ("\n".join(rows) or "No changed file."))
    rows = [f"- {code(e['check'])} at `{e['head']}`: {e['outcome']}" + (f", {e['reason']}" if e.get("reason") else "")
            for e in record["check_evidence"]]
    parts.append("## Check evidence\n\n" + ("\n".join(rows) or "None used."))

    verification = record["verification"]
    allowance = verification["allowance"]
    lines = [f"- Allowance: initial batch {'spent' if allowance['initial_spent'] else 'unspent'}, follow-up "
             f"{'spent' if allowance['follow_up_spent'] else 'unspent'}"
             + (f", carried from {code(allowance['carried_from'])}." if allowance.get("carried_from") else ".")]
    for batch in verification["batches"]:
        lines.append(f"- Batch {code(batch['name'])} ({batch['phase']}), {code(batch['operation'])}: bundle "
                     f"{code(batch['bundle'])}, raw return {code(batch['raw_return'])}, accounting {code(batch['accounting'])}.")
    for task in verification["tasks"]:
        batch = code(task["batch"]) if task.get("batch") else "none"
        if task["type"] == "candidate":
            lines.append(f"- Candidate {code(task['id'])}, trigger `{task['trigger']}`, batch {batch}: {task['ruling']}.")
        else:
            line = (f"- Safety premise {code(task['id'])}, area `{task['area']}`"
                    + (", optional" if task.get("trigger") == "optional" else "")
                    + f", batch {batch}: {task['ruling']}. {task['premise']} Evidence: {task['evidence']}")
            if task.get("reopened_as"):
                line += f" Reopened as {code(task['reopened_as'])}."
            lines.append(line)
    lines.extend(f"- Outstanding: {entry}" for entry in verification["outstanding"])
    parts.append("## Verification\n\n" + "\n".join(lines))

    routed = record["routed"]
    parts.append("## Routed\n\n" + "\n".join([f"- Unresolved: {ids(routed['unresolved'])}.",
                                                f"- Disputed: {ids(routed['disputed'])}."]
                                               + [f"- Unrecoverable input: {entry}" for entry in routed["unrecoverable_inputs"]]))

    if replies:
        entries = []
        for reply in replies:
            where = (f"Thread {code(reply['thread_id'])}, first comment `{reply['comment_id']}`." if reply["thread_id"]
                     else "No forge thread.")
            body = f"Drafted reply:\n\n{fenced(reply['body'])}" if reply["body"] is not None else "No drafted reply."
            entries.append(f"### {code(reply['id'])}: {reply['classification']}\n\n{where} {body}")
        parts.append("## Prior-item replies\n\n" + "\n\n".join(entries))

    paths = [f"- {name}: {code(path)}" for name, path in outputs]
    paths += [f"- {key}: {code(value)}" for key, value in record["paths"].items() if value not in {str(p) for _n, p in outputs}]
    parts.append("## Artifacts\n\n" + "\n".join(paths))
    return "\n\n".join(parts) + "\n"


# --- outputs ------------------------------------------------------------------


def active_chain(private: Path) -> str:
    """Why finalizing here would orphan an active record/addendum chain, or ``""``."""
    directories = [private / "addenda"]
    record = private / "record.json"
    try:
        with open(record, encoding="utf-8") as handle:
            named = json.load(handle)["record"]["paths"]["addenda"]
        if not isinstance(named, str):
            raise TypeError("`record.paths.addenda` is not a path")
        if os.path.abspath(named) != str(directories[0]):
            directories.append(Path(named))
    except FileNotFoundError:
        pass
    except (OSError, ValueError, KeyError, TypeError) as error:
        return (f"cannot establish which addenda directory `{record}` heads ({error.__class__.__name__}: {error}), "
                "so replacing it could orphan its chain; finalize in a fresh private directory")
    for directory in directories:
        try:
            entries = sorted(os.listdir(directory))
        except FileNotFoundError:
            continue
        except OSError as error:
            return f"cannot establish that `{directory}` holds no addendum: {error}"
        if entries:
            return (f"`{directory}` holds {', '.join(entries)}, so its record heads an active chain that this run "
                    "would orphan; finalize in a fresh private directory")
    return ""


def compact(profile: str, status: str, coverage: str, outputs: list[tuple[str, Path]]) -> str:
    return "".join([f"status {status}\n", f"coverage {coverage}\n"] + [f"{name} {path}\n" for name, path in outputs])


def output_paths(profile: str, private: Path) -> list[tuple[str, Path]]:
    names = [(name.split(".")[0], private / name) for name in ARTIFACTS[profile]]
    if profile == "implementation-gate":
        names.append(("addenda", private / "addenda"))
    return names + [("composition", private / "composition.json"), ("report", private / REPORT)]


def remove(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def finalize(args: argparse.Namespace, private: Path) -> int:
    active = active_chain(private)
    if active:
        print(f"finalize refused: {active}")
        return 1
    stale = [REPORT] + [name for names in ARTIFACTS.values() for name in names]
    try:
        for name in stale:  # the report first: it is the success marker
            remove(private / name)
            remove(private / f"{name}.part")
        remove(private / "composition.json.part")
    except OSError as error:
        print(f"finalize_review: cannot remove stale output: {error}", file=sys.stderr)
        return 2

    composition_path = private / "composition.json"
    composition = read_json(composition_path, "composition")
    packet = read_json(Path(args.packet), "packet") if args.packet else None
    composition, violations = derive(args, private, composition, packet, read_json(Path(args.store), "store"))
    if violations:
        raise fail("derive", 1, "".join(line + "\n" for line in violations))
    violations = check_accounting(composition, packet)
    if violations:
        raise fail("accounting", 1, "".join(line + "\n" for line in violations))

    compose = [str(SCRIPTS / "compose_review.py"), "--store", args.store, "-"]
    if args.profile == "implementation-gate":
        compose[1:1] = ["--profile", "implementation-gate"]
    # ASCII-escaped JSON reads the same under any stdin encoding the composer's locale selects.
    composed = run("record" if args.profile == "implementation-gate" else "compose", compose,
                   json.dumps(composition).encode("ascii"))
    staged: dict[str, bytes] = {}
    if args.profile == "publishable":
        validate = str(SCRIPTS / "validate_review.py")
        staged["payload.json"] = composed
        staged["batch.json"] = run("emit-batch", [validate, "--emit-batch"], composed)
        staged["fragments.md"] = run("render", [validate, "--render"], composed)
    payload = json.loads(composed)

    outputs = output_paths(args.profile, private)
    replies = rendered_replies(composition)
    given = {"store": args.store, "packet": args.packet, "fingerprint_input": args.fingerprint_input}
    given = {name: os.path.abspath(path) if path else None for name, path in given.items()}
    finalization = {"protocol": cr.FINALIZATION_PROTOCOL, "profile": args.profile,
                    "report": str(private / REPORT), "inputs": given, "replies": replies}
    try:
        inputs = [(name, Path(path)) for name, path in given.items() if path and name != "store"]
        report = render_report(args.profile, composition, payload, replies, outputs[:-1] + inputs)
    except (KeyError, TypeError, AttributeError) as error:  # the composer validated these shapes
        raise fail("report", 1, f"finalize_review: cannot render the report from the validated input: {error!r}\n")
    if args.profile == "implementation-gate":
        staged["record.json"] = (json.dumps({**payload, "finalization": finalization}, indent=2) + "\n").encode("utf-8")
    retained = None
    if args.profile == "publishable":
        retained = (json.dumps({**composition, "finalization": finalization}, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    staged[REPORT] = report.encode("utf-8")

    parts: list[Path] = []
    promoted: list[Path] = []
    try:
        for name, data in staged.items():
            part = private / f"{name}.part"
            parts.append(part)
            part.write_bytes(data)
        if retained is not None:
            part = private / "composition.json.part"
            parts.append(part)
            part.write_bytes(retained)
            os.replace(part, composition_path)
        if args.profile == "implementation-gate":
            (private / "addenda").mkdir(exist_ok=True)
        for name in staged:  # insertion order ends with the report
            os.replace(private / f"{name}.part", private / name)
            promoted.append(private / name)
    except BaseException as error:
        for path in parts + promoted[::-1]:
            try:
                remove(path)
            except OSError:
                pass
        if not isinstance(error, OSError):
            raise
        print(f"finalize_review: cannot write output: {error}; nothing this run wrote is left consumable", file=sys.stderr)
        return 2

    if args.compact:
        sys.stdout.write(compact(args.profile, composition["summary"]["status"], composition["run"]["coverage"], outputs))
    elif args.profile == "publishable":
        sys.stdout.buffer.write(staged["fragments.md"])
    else:
        print(f"record {private / 'record.json'}")
    return 0


def check(args: argparse.Namespace, private: Path) -> int:
    """Read-only: whether PRIVATE_DIR holds consumable output of the profile."""
    if args.profile == "implementation-gate":
        source = private / "record.json"
    else:
        source = private / "composition.json"
    try:
        with open(source, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, ValueError) as error:
        print(f"unconsumable: cannot read {source}: {error}")
        return 1
    if not isinstance(doc, dict):
        print(f"unconsumable: {source} is not a JSON object")
        return 1
    outputs = output_paths(args.profile, private)
    if "finalization" not in doc:
        artifact = private / ARTIFACTS[args.profile][0]
        if args.profile == "implementation-gate":
            if doc.get("schema") != LEGACY_SCHEMA or vr.validate(doc):
                print(f"unconsumable: {source} has no finalization and is not a valid {LEGACY_SCHEMA} record")
                return 1
        else:
            try:
                with open(artifact, encoding="utf-8") as handle:
                    valid = not vr.validate(json.load(handle))
            except (OSError, ValueError):
                valid = False
            if not valid or not (private / "batch.json").is_file():
                print(f"unconsumable: {source} has no finalization and {private} holds no valid legacy payload and batch")
                return 1
        print(f"legacy {artifact}")
        return 0
    problems = []
    why = cr.finalization_problem(doc)
    if why:
        problems.append(f"{source} {why}")
    elif doc["finalization"].get("profile") != args.profile:
        problems.append(f"{source} was finalized under `{doc['finalization'].get('profile')}`, not `{args.profile}`")
    problems += [f"{path} is missing" for name, path in outputs[:-1] if name != "addenda" and not path.exists()]
    if problems:
        for problem in problems:
            print(f"unconsumable: {problem}")
        return 1
    summary = doc.get("summary", {}) if args.profile == "publishable" else {"status": doc.get("status")}
    coverage = (doc.get("run") or {}).get("coverage")
    sys.stdout.write(compact(args.profile, summary.get("status"), coverage, outputs))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--profile", choices=cr.PROFILES, default="publishable")
    parser.add_argument("--store", help="the step-2 review-context store")
    parser.add_argument("--packet", help="the run's forge packet, read-only; supplies pull-request identity and checks prior-item thread ids")
    parser.add_argument("--fingerprint-input", help="the saved context_fingerprint.py input, read-only; supplies local target fields and the digest")
    parser.add_argument("--compact", action="store_true", help="print status, coverage, and output paths instead of the default")
    parser.add_argument("--check", action="store_true", help="read-only: report whether PRIVATE_DIR holds consumable output")
    parser.add_argument("private_dir", help="directory holding composition.json")
    args = parser.parse_args()
    private = Path(os.path.abspath(args.private_dir))
    if args.check:
        return check(args, private)
    if args.store is None:
        parser.error("--store is required unless --check")
    try:
        return finalize(args, private)
    except Stop as stop:
        return stop.status


if __name__ == "__main__":
    raise SystemExit(main())
