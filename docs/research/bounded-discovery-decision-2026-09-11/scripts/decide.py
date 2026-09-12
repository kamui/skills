#!/usr/bin/env python3
"""#153's decision: the mechanical half.

The decision itself is read off the frozen scorer; this script does everything
around it that must not depend on anyone's judgment:

* ``reveal``   - the per-member digests of #151's sealed packet archive, read
                 from the decrypted archive only after it hashes to the digest
                 #151 published, so that both packet files have a sealed digest
                 to be checked against without the key;
* ``verify``   - every revealed plaintext against the digest its stage sealed
                 (#148's registers and leak sets, #149's schedule, #151's
                 packets and redaction map through the reveal record, #152's
                 ruling tables, amendments and derived fields), both #152 freeze
                 records with their exact file sets, the packet set against the
                 public packet index (no packet missing, none duplicated, every
                 one hashing to its index entry), and the live ledger's chain and
                 totals;
* ``join``     - the redaction map, the sealed schedule, #151's cell manifest,
                 fidelity assessment and reconciliation, and #152's amended
                 derived fields into the grid the frozen scorer consumes, once
                 against truth ``v2`` and once against ``v1``, plus the fuller
                 per-attempt comparison record (roles, timing, packets);
* ``score``    - the pinned ``score_attempts.py`` over a grid, refusing a scorer
                 whose digest is not the frozen manifest's;
* ``compare``  - ``comparison-data.md`` from the comparison record, the two
                 scorecards and the loss-stage record;
* ``handoff``  - ``decision.json`` and the stage record that closes the epic's
                 measurement, carrying the scorer's verdicts and nothing it did
                 not say;
* ``scan``     - authored public files against local-path disclosure;
* ``--self-test`` - synthetic cases for the join, the truth parser, the
                 matched ratios, the exact-set freeze check, the loss-stage
                 vocabulary and the scan, plus CLI exit codes via subprocess.

Usage::

    decide.py reveal --archive grading-packets.tar.gz --sums F --out F
    decide.py verify --bundle D --targets-sums F --schedule-sums F \\
        --packets-dir D --reveal F --grading-dir D [--ledger F] --out F
    decide.py join --bundle D --closeout-dir D --frozen F [--evidence D] \\
        [--loss-stages F] --out-dir D
    decide.py score --scorer F --frozen F --grid F --out-json F --out-md F
    decide.py compare --comparison F --scorecard-v2 F --scorecard-v1 F \\
        --loss-stages F --out F
    decide.py handoff --comparison F --scorecard-v2 F --scorecard-v1 F \\
        --verification F --loss-stages F --out-decision F --out-handoff F
    decide.py scan FILE...
    decide.py --self-test

Input schema (UTF-8 JSON, every file an earlier stage wrote and this bundle
verifies before reading):

    revealed/schedule.json            #149: {"ordered_cells": [{"position", "cell_id",
                                      "target_slot", "arm", "replicate", ...}]}
    revealed/packets/redaction-map.json
                                      #151: {"target_masks": {slot: target_ref},
                                      "mapping": [{"attempt_ref", "packet_id", "arm",
                                      "position", "target_slot", "settled_usd", ...}]}
    revealed/amendment-1/derived-fields-amended-1.json
                                      #152: {"targets": {target_ref: {"register_status",
                                      "register_defect_ids", "defect_ids_after_grading",
                                      "truth_version_after_grading", "status_after_grading",
                                      "packets": [score_attempts.py's per-attempt fields
                                      keyed by "packet_id"]}}}
    revealed/targets/slot-N-register.md
                                      #148: a "# Verdict" section and "## GT-..." headings
                                      under "# Defect register"
    <closeout>/manifest.json, fidelity-assessment.json, reconciliation.json,
    packets/no-packet-manifest.json   #151's cell manifest (attempts with validity,
                                      completion, settled_usd, root_elapsed_seconds), the
                                      per-attempt assessment, the per-role cost split, and
                                      the attempts that published nothing
    loss-stages.json                  this bundle: {"rows": [{"attempt_ref", "defect_id",
                                      "outcome", "stage" | "origin", "evidence": [...]}],
                                      "verifier_exposure": [...], "scope_selector": {...}}

Exit: 0 on success, 1 on a content violation with one line per violation on
stdout, 2 when an input cannot be read or a subprocess fails.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

SCHEMA = "bounded-discovery-v1"
STATUSES = ("Approved", "Changes Requested", "Needs Information", "Incomplete")
ARMS = ("A", "B", "C")
STAGES = ("never-discovered", "raised-then-rejected-by-primary",
          "omitted-from-verification-by-policy", "verifier-refuted-or-unresolved",
          "publication-or-cap-loss", "unknown")
ORIGINS = ("primary", "finder", "verifier-added")
LOCAL_PATH = re.compile(r"(?:/Users|/home|/private|/tmp)/[^\s\"'`\\)]+")


class Failed(Exception):
    """A content violation: one line per problem on stdout, exit 1."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path):
    try:
        with open(os.path.expanduser(str(path)), encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, ValueError) as exc:
        sys.stderr.write("cannot read %s: %s\n" % (path, exc))
        raise SystemExit(2)


def read_text(path) -> str:
    try:
        with open(os.path.expanduser(str(path)), encoding="utf-8") as stream:
            return stream.read()
    except OSError as exc:
        sys.stderr.write("cannot read %s: %s\n" % (path, exc))
        raise SystemExit(2)


def write(path, payload) -> None:
    target = Path(os.path.expanduser(str(path)))
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, str):
        target.write_text(payload, encoding="utf-8")
    else:
        target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path) -> str:
    return hashlib.sha256(Path(os.path.expanduser(str(path))).read_bytes()).hexdigest()


def usd(value) -> Decimal:
    return Decimal(str(value))


def money(value) -> str:
    return format(usd(value).quantize(Decimal("0.0000001")), "f")


# --------------------------------------------------------------------------
# verify
# --------------------------------------------------------------------------

def parse_sums(text: str) -> dict:
    sums = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2:
            sums[parts[1]] = parts[0]
    return sums


def check_sums(directory, sums: dict, label: str, problems: list, checked: list) -> None:
    for name, digest in sorted(sums.items()):
        path = Path(directory) / name
        if not path.exists():
            problems.append("%s: %s is not among the revealed files" % (label, name))
            continue
        actual = sha256_file(path)
        checked.append({"source": label, "file": name, "sha256": actual, "matches": actual == digest})
        if actual != digest:
            problems.append("%s: %s hashes to %s..., sealed as %s..." % (label, name, actual[:12], digest[:12]))


def check_freeze_exact(record: dict, files: dict, label: str, problems: list) -> None:
    """The exact-set rule #152's review fixed: every recorded file, no extra, no duplicate."""
    recorded = set(record.get("files") or {})
    supplied = set(files)
    for name in sorted(recorded - supplied):
        problems.append("%s: frozen file %s was not supplied" % (label, name))
    for name in sorted(supplied - recorded):
        problems.append("%s: %s is not in the freeze record" % (label, name))
    for name in sorted(recorded & supplied):
        actual = sha256_file(files[name])
        if actual != record["files"][name]:
            problems.append("%s: %s hashes to %s..., frozen as %s..."
                            % (label, name, actual[:12], record["files"][name][:12]))


def ledger_summary(ledger: dict) -> dict:
    events = ledger.get("events") or []
    prior, intact = None, True
    for event in events:
        if event.get("previous_event_id") != prior:
            intact = False
            break
        prior = event["event_id"]
    last = events[-1] if events else {}
    return {
        "events": len(events),
        "chain_intact": intact,
        "actual_usd": ledger.get("actual_usd"),
        "reserved_usd": ledger.get("reserved_usd"),
        "uncertainty_usd": ledger.get("uncertainty_usd"),
        "frozen_total_cap_usd": ledger.get("frozen_total_cap_usd"),
        "grading_closeout_reserve_usd": ledger.get("grading_closeout_reserve_usd"),
        "last_event": {"ticket": last.get("ticket"), "phase": last.get("phase"),
                       "operation": last.get("operation"), "observed_at": last.get("observed_at")},
        "events_by_ticket": {str(t): sum(1 for e in events if e.get("ticket") == t)
                             for t in sorted({e.get("ticket") for e in events}, key=lambda x: (x is None, x))},
    }


PACKET_MEMBERS = ("grading-packets.json", "redaction-map.json")


def reveal_packets(archive, sums_text: str) -> dict:
    """Per-member digests of #151's packet archive, taken only from an archive that hashes to
    the digest #151 published. #151 sealed the two packet files as one archive and published the
    archive's plaintext digest, not the members', so this record is what gives each revealed file
    a sealed digest to be checked against later without the key."""
    recorded = parse_sums(sums_text).get("grading-packets.tar.gz")
    if not recorded:
        raise Failed("the sealed SHA256SUMS carries no entry for grading-packets.tar.gz")
    actual = sha256_file(archive)
    if actual != recorded:
        raise Failed("the archive hashes to %s..., #151 sealed %s...: not the sealed plaintext"
                     % (actual[:12], recorded[:12]))
    members = {}
    try:
        with tarfile.open(os.path.expanduser(str(archive)), "r:gz") as tar:
            for member in tar.getmembers():
                name = os.path.basename(member.name)
                if name in PACKET_MEMBERS and member.isfile():
                    members[name] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    except (OSError, tarfile.TarError) as exc:
        sys.stderr.write("cannot read %s: %s\n" % (archive, exc))
        raise SystemExit(2)
    missing = sorted(set(PACKET_MEMBERS) - set(members))
    if missing:
        raise Failed("the sealed archive lacks %s" % ", ".join(missing))
    return {"artifact_id": "issue-153-packet-reveal", "schema_version": SCHEMA, "revealed_at": now(),
            "source": "#151 packets/grading-packets.tar.gz.enc, decrypted under #148's key",
            "archive_sha256": actual, "archive_sha256_as_sealed": recorded, "members": members}


def check_reveal_record(reveal: dict, sums_text: str, problems: list) -> None:
    """The reveal record must name the archive #151 sealed and carry both member digests. The
    members themselves are trusted from the reveal step, which is the one place the key is needed:
    verify cannot re-derive them without the archive, and says so."""
    recorded = parse_sums(sums_text).get("grading-packets.tar.gz")
    if reveal.get("archive_sha256") != recorded or reveal.get("archive_sha256_as_sealed") != recorded:
        problems.append("#151 packets: the reveal record's archive digest is not the one #151 sealed")
    members = reveal.get("members") or {}
    for name in PACKET_MEMBERS:
        if not re.fullmatch(r"[0-9a-f]{64}", str(members.get(name, ""))):
            problems.append("#151 packets: the reveal record carries no digest for %s" % name)


def check_packets(packets_dir, index: dict, reveal: dict, problems: list, checked: list) -> None:
    """Both revealed packet files against the reveal record's sealed member digests, then the
    packet set against the public index: nothing missing, nothing duplicated, everything hashing
    to its entry, and the redaction map naming exactly that set."""
    folder = Path(packets_dir)
    for name in PACKET_MEMBERS:
        path = folder / name
        if not path.exists():
            problems.append("#151 packets: %s is not among the revealed files" % name)
            continue
        actual = sha256_file(path)
        sealed = (reveal.get("members") or {}).get(name)
        checked.append({"source": "#151 sealed packet archive", "file": name, "sha256": actual, "matches": actual == sealed})
        if actual != sealed:
            problems.append("#151 packets: %s hashes to %s..., the sealed archive member is %s..."
                            % (name, actual[:12], (sealed or "")[:12]))
    if problems:
        return
    packets = load(folder / "grading-packets.json")
    mapping = load(folder / "redaction-map.json")
    indexed = {p["packet_id"]: p["masked_packet_sha256"] for p in index["packets"]}
    seen = []
    for packet in packets["packets"]:
        pid = packet["packet_id"]
        if pid in seen:
            problems.append("#151 packets: packet %s appears twice" % pid[:8])
        seen.append(pid)
        digest = hashlib.sha256(json.dumps(packet, sort_keys=True).encode("utf-8")).hexdigest()
        checked.append({"source": "#151 packet index", "file": pid, "sha256": digest, "matches": digest == indexed.get(pid)})
        if digest != indexed.get(pid):
            problems.append("#151 packets: packet %s does not hash to the public index" % pid[:8])
    for pid in sorted(set(indexed) - set(seen)):
        problems.append("#151 packets: packet %s is in the public index and not in the revealed file" % pid[:8])
    for pid in sorted(set(seen) - set(indexed)):
        problems.append("#151 packets: packet %s is not in the public index" % pid[:8])
    rows = mapping["mapping"]
    mapped = [row["packet_id"] for row in rows]
    if len(mapped) != len(set(mapped)) or len({row["attempt_ref"] for row in rows}) != len(rows):
        problems.append("#151 redaction map: a packet or attempt is mapped twice")
    if set(mapped) != set(indexed):
        problems.append("#151 redaction map: packet ids differ from the public index")
    for row in rows:
        if row["masked_packet_sha256"] != indexed.get(row["packet_id"]):
            problems.append("#151 redaction map: packet %s carries a digest the index does not" % row["packet_id"][:8])


def verify(args) -> dict:
    bundle = Path(args.bundle)
    problems, checked = [], []
    check_sums(bundle / "revealed" / "targets", parse_sums(read_text(args.targets_sums)),
               "#148 sealed registers", problems, checked)
    check_sums(bundle / "revealed", parse_sums(read_text(args.schedule_sums)),
               "#149 sealed schedule", problems, checked)
    # #151: both packet files against the sealed archive's member digests, then the public index.
    reveal = load(args.reveal)
    check_reveal_record(reveal, read_text(Path(args.packets_dir) / "SHA256SUMS"), problems)
    check_packets(bundle / "revealed" / "packets", load(Path(args.packets_dir) / "packet-index.json"), reveal,
                  problems, checked)
    seal = load(Path(args.packets_dir) / "seal.json")
    if sorted(seal.get("files_sealed") or []) != sorted(PACKET_MEMBERS):
        problems.append("#151 seal record names a different file set")
    # #152: two freeze records with exact file sets, and the seal's per-file digests.
    grading = Path(args.grading_dir)
    tables = bundle / "revealed" / "rulings"
    amend = bundle / "revealed" / "amendment-1"
    check_freeze_exact(load(grading / "rulings-freeze.json"), {
        "rulings-target-A.json": tables / "rulings-target-A.json",
        "rulings-target-B.json": tables / "rulings-target-B.json",
        "derived-fields.json": tables / "derived-fields.json"}, "#152 rulings-freeze.json", problems)
    check_freeze_exact(load(grading / "rulings-freeze-2.json"), {
        "rulings-target-A.json": tables / "rulings-target-A.json",
        "rulings-target-B.json": tables / "rulings-target-B.json",
        "amendment-1-target-A.json": amend / "amendment-1-target-A.json",
        "amendment-1-target-B.json": amend / "amendment-1-target-B.json",
        "derived-fields-amended-1.json": amend / "derived-fields-amended-1.json"},
        "#152 rulings-freeze-2.json", problems)
    for seal_path, folder in ((grading / "sealed" / "seal.json", tables),
                              (grading / "sealed" / "amendment-1" / "seal.json", amend)):
        record = load(seal_path)
        for name, digest in sorted(record["files_sealed"].items()):
            path = folder / name
            if not path.exists():
                continue  # prompts, launch records and transcripts stay in the seal
            actual = sha256_file(path)
            checked.append({"source": str(seal_path.relative_to(grading.parent.parent)), "file": name,
                            "sha256": actual, "matches": actual == digest})
            if actual != digest:
                problems.append("#152 seal: %s hashes to %s..., sealed as %s..." % (name, actual[:12], digest[:12]))
    ledger = ledger_summary(load(args.ledger)) if args.ledger else None
    if ledger and not ledger["chain_intact"]:
        problems.append("ledger: the event chain is broken")
    if ledger and usd(ledger["reserved_usd"] or 0) != 0:
        problems.append("ledger: a reservation is outstanding")
    record = {
        "artifact_id": "issue-153-verification",
        "schema_version": SCHEMA,
        "verified_at": now(),
        "rulings_froze_before_unblinding": {
            "freeze_1_frozen_at": load(grading / "rulings-freeze.json").get("frozen_at"),
            "freeze_2_frozen_at": load(grading / "rulings-freeze-2.json").get("frozen_at"),
            "redaction_map_opened_by": "#153, after both freezes verified against the revealed tables",
            "grading_handoff_redaction_map_opened": load(grading / "handoff.json")["rulings"]["redaction_map_opened"],
        },
        "checked": checked,
        "problems": problems,
        "ledger": ledger,
        "verified": not problems,
    }
    return record


# --------------------------------------------------------------------------
# join
# --------------------------------------------------------------------------

def parse_register(text: str) -> dict:
    """Status and defect IDs from a sealed register: the Verdict section and the GT headings."""
    verdict = ""
    section = None
    defects = []
    for line in text.splitlines():
        if line.startswith("# "):
            section = line[2:].strip().lower()
            continue
        if section == "verdict" and line.strip():
            verdict += line.strip() + " "
        if section == "defect register":
            match = re.match(r"^## (GT-[A-Za-z0-9]+)", line)
            if match:
                defects.append(match.group(1))
    lowered = verdict.lower()
    if "adjudicated clean" in lowered or "0 material" in lowered:
        status = "clean"
    elif "material defect" in lowered:
        status = "buggy"
    else:
        raise Failed("register verdict is neither clean nor a defect count: %r" % verdict.strip())
    if (status == "clean") != (not defects):
        raise Failed("register verdict %r disagrees with its %d defect heading(s)" % (verdict.strip(), len(defects)))
    return {"status": status, "defect_ids": defects, "verdict": verdict.strip()}


def amended_items(rulings: dict, amendments: list) -> dict:
    """Every ruled item per packet, with each versioned amendment laid over the frozen table by
    item_ref exactly as the grading stage's derive step does: an amendment replaces the whole item."""
    replacements = {}
    for amendment in amendments:
        for item in amendment.get("items") or []:
            replacements[item["item_ref"]] = item
    out = {}
    for packet in rulings.get("packets") or []:
        out[packet["packet_id"]] = [replacements.get(item["item_ref"], item) for item in packet.get("items") or []]
    return out


def concept_counts(items: list) -> dict:
    """Duplicate-concept counts for one attempt, from its item-to-concept mapping (method section
    4): a second item on a concept already claimed is a duplicate, counted once per extra item;
    one item that names several concepts is bundled, not duplicated. Both are reported, and a zero
    is a count over the ruled items, never an omission."""
    per_concept = {}
    per_concept_false = {}
    per_concept_false_findings = {}
    bundled = bundled_material_findings = 0
    for item in items:
        concepts = [item.get("concept")] + [extra.get("concept") for extra in item.get("additional_concepts") or []]
        concepts = [c for c in concepts if c]
        finding = item.get("kind") == "finding"
        material = finding and item.get("ruling") == "supported" and item.get("materiality") == "material"
        if len(concepts) > 1:
            bundled += 1
            bundled_material_findings += 1 if material else 0
        for concept in concepts:
            per_concept[concept] = per_concept.get(concept, 0) + 1
            if item.get("ruling") == "false":
                per_concept_false[concept] = per_concept_false.get(concept, 0) + 1
                if finding:
                    per_concept_false_findings[concept] = per_concept_false_findings.get(concept, 0) + 1
    return {
        "items_ruled": len(items),
        "concepts_claimed": len(per_concept),
        "duplicate_items_on_a_concept": sum(n - 1 for n in per_concept.values()),
        "duplicate_false_items": sum(n - 1 for n in per_concept_false.values()),
        "bundled_concept_items": bundled,
        # The grading stage's derived fields count bundling over supported material findings and
        # false claims over findings only; these two are what the join cross-checks against them.
        "bundled_material_findings": bundled_material_findings,
        "duplicate_false_finding_items": sum(n - 1 for n in per_concept_false_findings.values()),
        "items_per_concept": dict(sorted(per_concept.items())),
    }


def claims_clean(status: str, clean_claim: bool) -> bool:
    return bool(clean_claim) or status == "Approved"


def build_join(schedule: dict, manifest: dict, fidelity: dict, reconciliation: dict, mapping: dict,
               derived: dict, registers: dict, no_packet: dict, frozen: dict,
               timing: dict = None, exposure: dict = None, items_by_packet: dict = None) -> dict:
    """Join every operational record to the frozen rulings, keyed by attempt_ref."""
    problems = []
    items_by_packet = items_by_packet or {}
    by_position = {c["position"]: c for c in schedule["ordered_cells"]}
    slot_of_ref = {v: k for k, v in mapping["target_masks"].items()}
    packets_by_id = {}
    for target_ref, entry in derived["targets"].items():
        for packet in entry["packets"]:
            packets_by_id[packet["packet_id"]] = dict(packet, target_ref=target_ref)
    map_by_attempt = {row["attempt_ref"]: row for row in mapping["mapping"]}
    fidelity_by_attempt = {a["attempt_ref"]: a for a in fidelity["attempts"]}
    recon_by_attempt = {a["attempt_ref"]: a for a in reconciliation["attempts"]}
    no_packet_refs = {a["attempt_ref"] for a in no_packet["attempts"]}
    # Truth per slot: the register's own verdict for v1, the derived fields for the graded revision.
    truth = {}
    for slot, register in sorted(registers.items()):
        v1 = parse_register(register)
        truth[slot] = {"status": v1["status"], "defect_ids_v1": list(v1["defect_ids"]),
                       "defect_ids_v2": list(v1["defect_ids"]), "truth_version_after_grading": "v1",
                       "attempted": False, "confirmed_truth_revisions": [], "verdict": v1["verdict"]}
    for target_ref, entry in derived["targets"].items():
        slot = slot_of_ref[target_ref]
        record = truth[slot]
        record["attempted"] = True
        if entry["register_status"] != record["status"]:
            problems.append("%s: derived register status %s differs from the register's %s"
                            % (slot, entry["register_status"], record["status"]))
        if sorted(entry["register_defect_ids"]) != sorted(record["defect_ids_v1"]):
            problems.append("%s: derived v1 defect ids differ from the register's" % slot)
        record["defect_ids_v2"] = sorted(entry["defect_ids_after_grading"])
        record["truth_version_after_grading"] = entry["truth_version_after_grading"]
        record["confirmed_truth_revisions"] = list(entry["confirmed_truth_revisions"])
        record["status_after_grading"] = entry["status_after_grading"]
        record["amendments_applied"] = len(entry.get("amendments_applied") or [])
        if entry["status_after_grading"] != record["status"]:
            problems.append("%s: the clean/buggy classification changed in grading" % slot)
    attempts = []
    for cell in manifest["cells"]:
        if cell["status"] != "attempted":
            continue
        sched = by_position[cell["position"]]
        if cell["arm"] != sched["arm"]:
            problems.append("position %d: manifest arm %s, schedule arm %s" % (cell["position"], cell["arm"], sched["arm"]))
        for attempt in cell["attempts"]:
            ref = attempt["attempt_ref"]
            fid = fidelity_by_attempt.get(ref) or {}
            rec = recon_by_attempt.get(ref) or {}
            row = map_by_attempt.get(ref)
            slot = sched["target_slot"]
            if fid.get("operational_validity") != attempt["operational_validity"]:
                problems.append("%s: manifest validity %s, assessment %s"
                                % (ref, attempt["operational_validity"], fid.get("operational_validity")))
            if row:
                if row["arm"] != cell["arm"] or row["position"] != cell["position"] or row["target_slot"] != slot:
                    problems.append("%s: redaction map disagrees with the schedule or manifest" % ref)
                if usd(row["settled_usd"]) != usd(attempt["settled_usd"]):
                    problems.append("%s: redaction map cost differs from the manifest" % ref)
                packet = packets_by_id.get(row["packet_id"])
                if packet is None:
                    problems.append("%s: packet %s has no ruling" % (ref, row["packet_id"][:8]))
                    continue
                if slot_of_ref[packet["target_ref"]] != slot:
                    problems.append("%s: packet ruled under %s, attempt on %s" % (ref, packet["target_ref"], slot))
            elif ref not in no_packet_refs:
                problems.append("%s: neither a packet nor a no-packet entry" % ref)
            else:
                packet = None
            if usd(rec.get("ledger_settled_usd", attempt["settled_usd"])) != usd(attempt["settled_usd"]):
                problems.append("%s: reconciliation cost differs from the manifest" % ref)
            valid = attempt["operational_validity"] == "valid"
            completed = attempt["completion"] == "complete"
            t = truth[slot]
            if packet:
                status, clean_claim = packet["status"], packet["clean_claim"]
                recovered = sorted(packet["recovered_defect_ids"])
                sufficient = sorted(packet["sufficient_fix_defect_ids"])
                partial = sorted(packet.get("partial_fix_defect_ids") or [])
            else:
                status, clean_claim, recovered, sufficient, partial = "Incomplete", False, [], [], []
            buggy = t["status"] == "buggy"
            if packet:
                if row["packet_id"] not in items_by_packet:
                    problems.append("%s: packet %s has no ruled items to count concepts over" % (ref, row["packet_id"][:8]))
                counts = concept_counts(items_by_packet.get(row["packet_id"], []))
                if counts["items_ruled"] != packet["raw_items"]:
                    problems.append("%s: %d ruled items against %d raw items in the derived fields"
                                    % (ref, counts["items_ruled"], packet["raw_items"]))
                if counts["bundled_material_findings"] != packet.get("bundled_concept_items", 0):
                    problems.append("%s: bundled material findings %d against the derived fields' %d"
                                    % (ref, counts["bundled_material_findings"], packet.get("bundled_concept_items", 0)))
                if packet["raw_false_finding_items"] - packet["unique_false_claims"] != counts["duplicate_false_finding_items"]:
                    problems.append("%s: duplicate false findings %d against the derived fields' raw-minus-unique %d"
                                    % (ref, counts["duplicate_false_finding_items"],
                                       packet["raw_false_finding_items"] - packet["unique_false_claims"]))
            else:
                counts = concept_counts([])
            entry = {
                "position": cell["position"], "attempt_ref": ref, "ordinal": attempt["ordinal"],
                "attempt_id": "issue-138-%s-attempt-%d" % (sched["cell_id"], attempt["ordinal"]),
                "cell_id": sched["cell_id"], "target_slot": slot, "arm": cell["arm"], "replicate": sched["replicate"],
                "is_replacement": attempt["is_replacement"], "predecessor_ref": attempt["predecessor_ref"],
                "operational_validity": attempt["operational_validity"], "invalidated_by": attempt["invalidated_by"],
                "validity_basis": attempt["validity_basis"], "replacement_eligible": attempt["replacement_eligible"],
                "valid": valid, "completion": attempt["completion"], "completed": completed,
                "valid_completed": valid and completed, "produced_claims": attempt["produced_claims"],
                "packet_id": row["packet_id"] if row else None, "status": status, "clean_claim": clean_claim,
                "honest_incomplete": packet["honest_incomplete"] if packet else None,
                "target_status": t["status"],
                "defects_v2": t["defect_ids_v2"], "defects_v1": t["defect_ids_v1"],
                "recovered_defect_ids": recovered, "sufficient_fix_defect_ids": sufficient,
                "partial_fix_defect_ids": partial,
                "recovered_v1": sorted(set(recovered) & set(t["defect_ids_v1"])),
                "sufficient_v1": sorted(set(sufficient) & set(t["defect_ids_v1"])),
                "recall_v2": (len(set(recovered) & set(t["defect_ids_v2"])) / len(t["defect_ids_v2"])) if buggy else None,
                "recall_v1": (len(set(recovered) & set(t["defect_ids_v1"])) / len(t["defect_ids_v1"])) if buggy else None,
                "sufficient_outcome_recall_v2": (len(sufficient) / len(t["defect_ids_v2"])) if buggy else None,
                "fix_sufficiency": (len(sufficient) / len(recovered)) if recovered else None,
                "false_clean": buggy and claims_clean(status, clean_claim),
                "concepts_claimed": counts["concepts_claimed"],
                "duplicate_items_on_a_concept": counts["duplicate_items_on_a_concept"],
                "duplicate_false_items": counts["duplicate_false_items"],
                "bundled_concept_items": counts["bundled_concept_items"],
                "items_per_concept": counts["items_per_concept"],
                "raw_items": packet["raw_items"] if packet else 0,
                "raw_finding_items": packet["raw_finding_items"] if packet else 0,
                "raw_false_finding_items": packet["raw_false_finding_items"] if packet else 0,
                "raw_false_non_finding_items": packet.get("raw_false_non_finding_items", 0) if packet else 0,
                "unique_false_claims": packet["unique_false_claims"] if packet else 0,
                "action_errors": packet["action_errors"] if packet else 0,
                "priority_errors": packet["priority_errors"] if packet else 0,
                "unresolved_adjudications": packet["unresolved_adjudications"] if packet else 0,
                "unsupported_safety_claims": packet.get("unsupported_safety_claims", 0) if packet else 0,
                "safety_claims": packet.get("safety_claims", 0) if packet else 0,
                "settled_usd": money(attempt["settled_usd"]),
                "per_role_usd": rec.get("per_role_recovered_usd") or {},
                "unassigned_residual_usd": rec.get("unassigned_residual_usd"),
                "self_report_usd": rec.get("self_report_usd"),
                "recomputed_usage_usd": rec.get("recomputed_usage_usd"),
                "root_elapsed_seconds": attempt["root_elapsed_seconds"],
                "duration_censored": attempt["completion"] != "complete",
                "timing_availability": attempt["timing_availability"],
                "timing": (timing or {}).get(ref),
                "verifier": (exposure or {}).get(ref),
            }
            attempts.append(entry)
    attempts.sort(key=lambda a: (a["position"], a["ordinal"]))
    planned = list(frozen["cells"]["cell_ids"])
    attempted_cells = {a["cell_id"] for a in attempts}
    cells = {}
    for a in attempts:
        cell = cells.setdefault(a["cell_id"], {"cell_id": a["cell_id"], "target_slot": a["target_slot"], "arm": a["arm"],
                                               "replicate": a["replicate"], "attempts": [], "charges_usd": Decimal(0),
                                               "valid_completed": False})
        cell["attempts"].append(a["attempt_ref"])
        cell["charges_usd"] += usd(a["settled_usd"])
        cell["valid_completed"] = cell["valid_completed"] or a["valid_completed"]
    for cell in cells.values():
        cell["charges_usd"] = money(cell["charges_usd"])
    pairs = matched_pairs(cells)
    if problems:
        raise Failed("\n".join(problems))
    return {
        "artifact_id": "issue-153-comparison",
        "schema_version": SCHEMA,
        "joined_at": now(),
        "truth": truth,
        "expected_clean_targets": sorted(s for s, t in truth.items() if t["status"] == "clean"),
        "planned_cells": planned,
        "attempted_cells": sorted(attempted_cells),
        "unattempted_cells": sorted(set(planned) - attempted_cells),
        "attempts": attempts,
        "cells": [cells[k] for k in sorted(cells)],
        "matched_pairs": pairs,
        "arm_role_spend": arm_role_spend(attempts),
    }


def matched_pairs(cells: dict) -> dict:
    by_key = {}
    for cell in cells.values():
        by_key.setdefault((cell["target_slot"], cell["replicate"]), {})[cell["arm"]] = usd(cell["charges_usd"])
    rows, ratios = [], {"B/A": [], "C/A": [], "C/B": []}
    for key in sorted(by_key):
        arms = by_key[key]
        row = {"target_slot": key[0], "replicate": key[1],
               "cost_usd": {arm: money(arms[arm]) for arm in sorted(arms)}}
        for name, (num, den) in (("B/A", ("B", "A")), ("C/A", ("C", "A")), ("C/B", ("C", "B"))):
            if num in arms and den in arms and arms[den] != 0:
                ratio = float(arms[num] / arms[den])
                row[name] = ratio
                ratios[name].append(ratio)
            else:
                row[name] = None
        rows.append(row)
    return {"pairs": rows,
            "medians": {name: (statistics.median(v) if v else None) for name, v in ratios.items()},
            "pair_counts": {name: len(v) for name, v in ratios.items()}}


def arm_role_spend(attempts: list) -> dict:
    out = {}
    for arm in ARMS:
        rows = [a for a in attempts if a["arm"] == arm]
        roles = {}
        residual = Decimal(0)
        for a in rows:
            for role, amount in (a["per_role_usd"] or {}).items():
                roles[role] = roles.get(role, Decimal(0)) + usd(amount)
            residual += usd(a["unassigned_residual_usd"] or 0)
        out[arm] = {"attempts": len(rows), "settled_usd": money(sum((usd(a["settled_usd"]) for a in rows), Decimal(0))),
                    "by_role_usd": {r: money(v) for r, v in sorted(roles.items())},
                    "unassigned_residual_usd": money(residual)}
    return out


def grid_from(comparison: dict, version: str, frozen: dict) -> dict:
    """The frozen scorer's input, against truth v2 (graded) or v1 (as registered)."""
    key = "defect_ids_v2" if version == "v2" else "defect_ids_v1"
    targets = {}
    for slot, t in comparison["truth"].items():
        targets[slot] = {"status": t["status"], "defect_ids": list(t[key]),
                         "truth_version": t["truth_version_after_grading"] if version == "v2" else "v1"}
    attempts = []
    for a in comparison["attempts"]:
        known = set(targets[a["target_slot"]]["defect_ids"])
        attempts.append({
            "attempt_id": a["attempt_id"], "cell_id": a["cell_id"], "target_slot": a["target_slot"],
            "arm": a["arm"], "replicate": a["replicate"], "valid": a["valid"], "completed": a["completed"],
            "status": a["status"], "clean_claim": a["clean_claim"],
            "recovered_defect_ids": sorted(set(a["recovered_defect_ids"]) & known),
            "sufficient_fix_defect_ids": sorted(set(a["sufficient_fix_defect_ids"]) & known),
            "raw_false_finding_items": a["raw_false_finding_items"],
            "unique_false_claims": a["unique_false_claims"],
            "action_errors": a["action_errors"], "priority_errors": a["priority_errors"],
            "unresolved_adjudications": a["unresolved_adjudications"],
            "billed_cost_usd": a["settled_usd"],
            "attempt_ref": a["attempt_ref"], "operational_validity": a["operational_validity"],
            "completion": a["completion"],
        })
    thresholds = {"relative_recall_gain": 0.20, "zero_baseline_absolute_gain": 0.10, "matched_cost_ratio": 1.25}
    return {"experiment_id": frozen["experiment_id"], "truth_version": version,
            "control_arm": "A", "candidate_arms": ["B", "C"], "thresholds": thresholds,
            "targets": targets, "attempts": attempts, "planned_cells": list(comparison["planned_cells"]),
            "expected_clean_targets": list(comparison["expected_clean_targets"])}


def read_timing(evidence, attempts_refs) -> dict:
    """The #130 sidecar per attempt, from the sealed evidence when it is present.

    A position directory holds the cell's surviving attempt; a discarded
    predecessor is under ``invalid/<attempt_ref>`` or nowhere at all, and never
    inherits its successor's sidecar.
    """
    out = {}
    root = Path(os.path.expanduser(str(evidence)))
    last_ordinal = {}
    for ref in attempts_refs:
        position, ordinal = ref.split("-attempt-")
        last_ordinal[position] = max(last_ordinal.get(position, 0), int(ordinal))
    for ref in attempts_refs:
        position, ordinal = ref.split("-attempt-")
        if int(ordinal) == last_ordinal[position]:
            path = root / position / "work" / "timing.json"
        else:
            path = root / "invalid" / ref / "work" / "timing.json"
        if not path.exists():
            continue
        try:
            sidecar = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        record = dict(sidecar)
        dispatched = sidecar.get("root_dispatched_at")
        for name, key in (("elapsed_to_payload_seconds", "payload_validated_at"),
                          ("elapsed_to_completion_seconds", "completed_at")):
            record[name] = None
            if dispatched and sidecar.get(key):
                record[name] = round((datetime.fromisoformat(sidecar[key]) - datetime.fromisoformat(dispatched)).total_seconds(), 3)
        out[ref] = record
    return out


def join(args) -> None:
    bundle = Path(args.bundle)
    closeout = Path(args.closeout_dir)
    schedule = load(bundle / "revealed" / "schedule.json")
    mapping = load(bundle / "revealed" / "packets" / "redaction-map.json")
    derived = load(bundle / "revealed" / "amendment-1" / "derived-fields-amended-1.json")
    items_by_packet = {}
    for target in ("A", "B"):
        items_by_packet.update(amended_items(
            load(bundle / "revealed" / "rulings" / ("rulings-target-%s.json" % target)),
            [load(bundle / "revealed" / "amendment-1" / ("amendment-1-target-%s.json" % target))]))
    registers = {}
    for path in sorted((bundle / "revealed" / "targets").glob("slot-*-register.md")):
        registers[path.name.split("-register")[0]] = read_text(path)
    manifest = load(closeout / "manifest.json")
    fidelity = load(closeout / "fidelity-assessment.json")
    reconciliation = load(closeout / "reconciliation.json")
    no_packet = load(closeout / "packets" / "no-packet-manifest.json")
    frozen = load(args.frozen)
    refs = [a["attempt_ref"] for c in manifest["cells"] for a in c["attempts"]]
    timing = read_timing(args.evidence, refs) if args.evidence else {}
    exposure = {}
    if args.loss_stages:
        for row in load(args.loss_stages).get("verifier_exposure") or []:
            exposure[row["attempt_ref"]] = row
    comparison = build_join(schedule, manifest, fidelity, reconciliation, mapping, derived, registers,
                            no_packet, frozen, timing, exposure, items_by_packet)
    comparison["derived_fields"] = "revealed/amendment-1/derived-fields-amended-1.json"
    comparison["closeout"] = {"manifest": str(closeout / "manifest.json"),
                              "fidelity_assessment": str(closeout / "fidelity-assessment.json"),
                              "reconciliation": str(closeout / "reconciliation.json")}
    comparison["spend_columns"] = {
        "pre_freeze_usd": reconciliation["columns"]["pre_freeze_usd"],
        "setup_and_selection_usd": reconciliation["columns"]["setup_and_selection_usd"],
        "review_attempts_usd": reconciliation["columns"]["review_attempts_usd"],
        "grading_usd": args.grading_usd,
        "decision_usd": "0",
        "retained_uncertainty_usd": reconciliation["totals"]["retained_uncertainty_usd"],
        "conservative_bounds": reconciliation["conservative_bounds"],
        "note": "review consumption, one-off setup and selection, charged grading and this decision stay in separate columns; shared setup is charged once to the epic",
    }
    out = Path(args.out_dir)
    write(out / "comparison.json", comparison)
    write(out / "grid-v2.json", grid_from(comparison, "v2", frozen))
    write(out / "grid-v1.json", grid_from(comparison, "v1", frozen))
    print("wrote comparison.json, grid-v2.json and grid-v1.json under %s" % out)


# --------------------------------------------------------------------------
# score
# --------------------------------------------------------------------------

def score(args) -> None:
    frozen = load(args.frozen)
    pinned = frozen["pins"]["freeze_tools"]["score_attempts.py"]["sha256"]
    actual = sha256_file(args.scorer)
    if actual != pinned:
        raise Failed("scorer %s hashes to %s..., the freeze pinned %s..." % (args.scorer, actual[:12], pinned[:12]))
    for flag, out in (("--json", args.out_json), (None, args.out_md)):
        cmd = [sys.executable, args.scorer, "--input", args.grid, "--out", out] + ([flag] if flag else [])
        run = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if run.returncode == 1:
            raise Failed(run.stdout.strip())
        if run.returncode:
            sys.stderr.write("%s failed: %s\n" % (" ".join(cmd), run.stderr[:400]))
            raise SystemExit(2)
    report = load(args.out_json)
    print("scored %s: %s" % (args.grid, ", ".join("%s against %s %s" % (s["candidate_arm"], s["control_arm"], s["verdict"])
                                                    for s in report["screens"])))


# --------------------------------------------------------------------------
# compare: comparison-data.md
# --------------------------------------------------------------------------

def fmt(value, digits=3):
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return "%.*f" % (digits, value)
    return str(value)


def pct(value):
    return "n/a" if value is None else "%.0f%%" % (100 * value)


def minutes(seconds):
    return "n/a" if seconds is None else "%.1f min" % (seconds / 60)


def validate_loss_stages(record: dict) -> list:
    problems = []
    for row in record.get("rows") or []:
        if row.get("outcome") == "missed" and row.get("stage") not in STAGES:
            problems.append("%s/%s: stage %r is not in the vocabulary" % (row.get("attempt_ref"), row.get("defect_id"), row.get("stage")))
        for extra in row.get("also") or []:
            if extra not in STAGES:
                problems.append("%s/%s: stage %r is not in the vocabulary" % (row.get("attempt_ref"), row.get("defect_id"), extra))
        if row.get("outcome") == "recovered" and row.get("origin") not in ORIGINS:
            problems.append("%s/%s: origin %r is not in the vocabulary" % (row.get("attempt_ref"), row.get("defect_id"), row.get("origin")))
        if row.get("stage") is not None and row.get("stage") not in STAGES:
            problems.append("%s: stage %r is not in the vocabulary" % (row.get("attempt_ref"), row.get("stage")))
        if not row.get("evidence"):
            problems.append("%s/%s: no evidence cited" % (row.get("attempt_ref"), row.get("defect_id")))
    return problems


def compare(args) -> None:
    comparison = load(args.comparison)
    v2, v1 = load(args.scorecard_v2), load(args.scorecard_v1)
    losses = load(args.loss_stages)
    problems = validate_loss_stages(losses)
    if problems:
        raise Failed("\n".join(problems))
    write(args.out, render_comparison(comparison, v2, v1, losses))
    print("wrote " + args.out)


def render_comparison(comparison: dict, v2: dict, v1: dict, losses: dict) -> str:
    truth = comparison["truth"]
    attempts = comparison["attempts"]
    lines = ["# Comparison data — issue #153, the #138 pilot after grading", "",
             "Every attempt the epic dispatched, joined after #152's rulings froze: the arm and target from the",
             "sealed schedule and redaction map, operational validity from #151's fidelity assessment, completion",
             "and cost from its manifest and reconciliation, and the per-attempt scoring fields from #152's",
             "amended derived fields. Eighteen of the twenty-four planned cells were never attempted and appear",
             "here as missing. The screening verdicts are in [`evaluation.md`](evaluation.md); the scorer's own",
             "output is [`scorecard-v2.md`](scorecard-v2.md) (graded truth) and [`scorecard-v1.md`](scorecard-v1.md)",
             "(truth as registered before grading).", ""]
    lines += ["## 1. Truth after grading", "",
              "| Slot | Target | Status | Defects as registered (v1) | Defects after grading | Attempted |",
              "| --- | --- | --- | --- | --- | --- |"]
    labels = {"slot-1": "clap-rs/clap#6212", "slot-2": "grpc/grpc-go#7417", "slot-3": "nats-io/nats-server#6593",
              "slot-4": "nats-io/nats-server#7395"}
    for slot in sorted(truth):
        t = truth[slot]
        lines.append("| %s | %s | %s | %s | %s (%s) | %s |" % (
            slot, labels.get(slot, ""), t["status"], ", ".join(t["defect_ids_v1"]) or "none",
            ", ".join(t["defect_ids_v2"]) or "none", t["truth_version_after_grading"],
            "yes" if t["attempted"] else "no"))
    lines += ["", "The clean/buggy mix is unchanged by grading: the one clean slot stays clean, and the buggy slot the",
              "pilot ran on gained a second, adjudicator-confirmed defect, which moves its recall denominator from one",
              "to two for every attempt on it. Two buggy slots were never attempted, so every macro over buggy targets",
              "is unavailable rather than zero.", ""]
    lines += ["## 2. Per-attempt rows", "",
              "`D_t` and `R_i` are against the graded truth (v2); the v1 column shows recovery against the register as",
              "frozen. `Valid` is #151's operational validity: no attempt is `valid`, because the launch argv was never",
              "retained (five `unresolved`) or a protocol rule was broken (three `invalid`). False clean is a property of",
              "the published status on a buggy target. `V` is whether a verifier batch ran and what it received.", "",
              "Duplicates are items beyond the first on a concept the attempt already claimed (supported or",
              "false alike); bundled is one item naming more than one concept, which is not a duplicate. Both are",
              "counted over the ruled items, so a zero is established, not omitted.", "",
              "| Pos | Attempt | Cell | Arm | Validity | Completion | Status | `D_t` | `R_i` (v2) | Recall v2 | Recall v1 | Sufficient / partial | Raw items | Concepts | Duplicates | Bundled | False findings | False clean | V | Settled |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for a in attempts:
        buggy = a["target_status"] == "buggy"
        ver = a.get("verifier") or {}
        vtext = {"clean-verdict": "clean-verdict batch", "candidate": "candidate batch (%d, %d finder-origin)"
                 % (ver.get("candidates_received", 0), ver.get("finder_origin_received", 0)),
                 "none": "none (policy)"}.get(ver.get("batch"), "n/a")
        lines.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %d | %d | %d | %d | %d | %s | %s | $%s |" % (
            a["position"], a["attempt_ref"], a["cell_id"], a["arm"], a["operational_validity"], a["completion"],
            a["status"], len(a["defects_v2"]) if buggy else "0 (clean)",
            ", ".join(a["recovered_defect_ids"]) or "—",
            fmt(a["recall_v2"]) if buggy else "N/A", fmt(a["recall_v1"]) if buggy else "N/A",
            ("%s / %s" % (", ".join(a["sufficient_fix_defect_ids"]) or "—", ", ".join(a["partial_fix_defect_ids"]) or "—")) if a["recovered_defect_ids"] else "—",
            a["raw_items"], a["concepts_claimed"], a["duplicate_items_on_a_concept"], a["bundled_concept_items"],
            a["raw_false_finding_items"], ("**yes**" if a["false_clean"] else "no") if buggy else "N/A",
            vtext, a["settled_usd"]))
    lines += ["", "Raw items across the six packets: %d, of which %d findings, %d false findings, %d false non-finding items, %d unresolved rulings, %d action errors, %d priority errors, %d unsupported explicit safety claims. Concepts claimed: %d over %d items; duplicate items on a concept: %d (of them false: %d); bundled items: %d."
              % (sum(a["raw_items"] for a in attempts), sum(a["raw_finding_items"] for a in attempts),
                 sum(a["raw_false_finding_items"] for a in attempts), sum(a["raw_false_non_finding_items"] for a in attempts),
                 sum(a["unresolved_adjudications"] for a in attempts), sum(a["action_errors"] for a in attempts),
                 sum(a["priority_errors"] for a in attempts), sum(a["unsupported_safety_claims"] for a in attempts),
                 sum(a["concepts_claimed"] for a in attempts), sum(a["raw_items"] for a in attempts),
                 sum(a["duplicate_items_on_a_concept"] for a in attempts), sum(a["duplicate_false_items"] for a in attempts),
                 sum(a["bundled_concept_items"] for a in attempts)), ""]
    lines += ["## 3. Arm scorecards (frozen scorer, graded truth)", "",
              "| Arm | Attempts | Valid completed | Completion | Macro recall (all) | Macro recall (completed) | False clean | Raw false findings | Sufficient-outcome recall | Fix sufficiency | Billed |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for arm, card in v2["arms"].items():
        lines.append("| %s | %d | %d | %s | %s | %s | %d (%s) | %d | %s | %s | $%s |" % (
            arm, card["attempts"], card["valid_completed"], fmt(card["completion_rate"]),
            fmt(card["macro_material_recall_all_attempts"]), fmt(card["macro_material_recall_completed_only"]),
            card["false_clean_count"], fmt(card["false_clean_rate"]), card["raw_false_finding_items"],
            fmt(card["sufficient_outcome_recall"]), fmt(card["aggregate_fix_sufficiency"]), card["billed_cost_total"]))
    lines += ["", "Both macros are unavailable in every arm: two of the three buggy targets have no attempt, and no",
              "attempt is a valid completed outcome. The per-target figures below are what was measured.", ""]
    lines += ["### Per-target recall on the one buggy target attempted", "",
              "| Arm | Attempts on slot-1 | Recall v2 (all attempts) | Recall v1 (all attempts) | Valid completed | Recovered | Sufficient fixes | Note |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for arm in ARMS:
        rows = [a for a in attempts if a["arm"] == arm and a["target_slot"] == "slot-1"]
        if not rows:
            continue
        note = "; ".join("%s: %s, %s" % (a["attempt_ref"], a["operational_validity"], a["completion"]) for a in rows)
        lines.append("| %s | %d | %s | %s | %d | %s | %s | %s |" % (
            arm, len(rows), fmt(statistics.mean(a["recall_v2"] for a in rows)), fmt(statistics.mean(a["recall_v1"] for a in rows)),
            sum(1 for a in rows if a["valid_completed"]), ", ".join(", ".join(a["recovered_defect_ids"]) or "—" for a in rows),
            ", ".join(", ".join(a["sufficient_fix_defect_ids"]) or "—" for a in rows), note))
    lines += ["", "Against v1 the two recovering attempts hold one recovery each and no sufficient fix, because the one",
              "fix ruled sufficient restores the defect that grading added (GT-p2), not the registered one (GT-p1).", ""]
    lines += ["## 4. Screens", ""]
    for report, label in ((v2, "graded truth (v2)"), (v1, "truth as registered (v1)")):
        lines.append("### Against %s" % label)
        lines.append("")
        for s in report["screens"]:
            lines.append("**%s against %s — %s.**" % (s["candidate_arm"], s["control_arm"], s["verdict"]))
            lines.append("")
            for c in s["criteria"]:
                lines.append("- %s — %s: %s" % (c["criterion"], c["verdict"], c["detail"]))
            for b in s["blockers"]:
                lines.append("- blocked — %s" % b)
            lines.append("")
    lines += ["## 5. Matched cost", "",
              "Cells matched by target and replicate, each charged every attempt including its discarded predecessor.",
              "Two pairs exist; the other six planned pairs per contrast have no member.", "",
              "| Target | Replicate | A | B | C | B/A | C/A | C/B |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in comparison["matched_pairs"]["pairs"]:
        c = row["cost_usd"]
        lines.append("| %s | %d | $%s | $%s | $%s | %s | %s | %s |" % (
            row["target_slot"], row["replicate"], c.get("A", "—"), c.get("B", "—"), c.get("C", "—"),
            fmt(row["B/A"]), fmt(row["C/A"]), fmt(row["C/B"])))
    med = comparison["matched_pairs"]["medians"]
    lines += ["", "Medians over the two pairs: B/A %s, C/A %s, C/B %s (gate ≤ 1.25 for the two screens; C/B is reported, not gated)."
              % (fmt(med["B/A"]), fmt(med["C/A"]), fmt(med["C/B"])), ""]
    lines += ["### Spend by arm and role", "",
              "Per-role figures are #151's recovered split from the retained per-transcript costs; the residual is the",
              "settled charge no transcript accounts for, carried as unassigned.", "",
              "| Arm | Attempts | Primary | Verifier | Finder | Unassigned residual | Settled |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for arm, spend in comparison["arm_role_spend"].items():
        roles = spend["by_role_usd"]
        lines.append("| %s | %d | $%s | $%s | $%s | $%s | $%s |" % (
            arm, spend["attempts"], roles.get("primary", "0"), roles.get("worker", "0"), roles.get("finder", "0"),
            spend["unassigned_residual_usd"], spend["settled_usd"]))
    cols = comparison["spend_columns"]
    lines += ["", "### Spend columns for the epic", "",
              "| Column | USD |", "| --- | --- |",
              "| Pre-freeze (targets, probes) | %s |" % cols["pre_freeze_usd"],
              "| Shared setup and selection, charged once | %s |" % cols["setup_and_selection_usd"],
              "| Review attempts, all eight, discards included | %s |" % cols["review_attempts_usd"],
              "| Charged grading (#152) | %s |" % cols["grading_usd"],
              "| This decision (#153) | %s |" % cols["decision_usd"],
              "| Retained uncertainty | %s |" % cols["retained_uncertainty_usd"], ""]
    lines += ["## 6. Elapsed time", "",
              "Root elapsed is the whole attempt from dispatch to exit; the sidecar events come from #130's timing",
              "record inside the sealed evidence. A stopped attempt's duration is censored at the stop and is not a",
              "completion. Every arm ran its verifier in the foreground by the frozen rule, so these are this harness's",
              "timings, not the policy's production timing.", "",
              "| Attempt | Arm | Completion | Root elapsed | To validated payload | To completion | Censored |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for a in attempts:
        t = a.get("timing") or {}
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            a["attempt_ref"], a["arm"], a["completion"], minutes(a["root_elapsed_seconds"]),
            minutes(t.get("elapsed_to_payload_seconds")), minutes(t.get("elapsed_to_completion_seconds")),
            "yes" if a["duration_censored"] else "no"))
    lines += ["", "## 7. Where each defect was found or lost", "",
              "Coordinator judgments from each attempt's own stage records, made after the rulings froze",
              "([`loss-stages.json`](loss-stages.json) carries the evidence pointers). `Admissible` is the screen's view",
              "once operational validity is joined.", "",
              "| Attempt | Arm | Defect | Outcome | Stage or origin | Verified | Fix | Admissible |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in losses["rows"]:
        if row.get("defect_id") is None:
            continue
        stage = row.get("stage") if row["outcome"] == "missed" else "origin: " + row.get("origin", "")
        if row.get("also"):
            stage += "; also " + ", ".join(row["also"])
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            row["attempt_ref"], row["arm"], row["defect_id"], row["outcome"], stage,
            row.get("verified", "—"), row.get("fix", "—"),
            "—" if row["outcome"] == "missed" else ("yes" if row.get("admissible") else "no: " + row.get("why_inadmissible", ""))))
    lines += ["", "On the clean target, arm C's finder raised two concurrency claims and the primary rejected both",
              "before verification; both rejections were correct, and the clean-verdict batch upheld them.", ""]
    lines += ["### Scope selector", "", "| Slot | Selected scope | Defect sites | Miss |", "| --- | --- | --- | --- |"]
    for slot, rec in sorted(losses["scope_selector"].items()):
        lines.append("| %s | `%s` | %s | %s |" % (slot, rec["selected_scope"], "; ".join(rec["defect_sites"]) or "none",
                                                   "yes" if rec["miss"] else "no"))
    lines += ["", "## 8. Unattempted cells", "",
              "%d of %d planned cells were never dispatched and stay unavailable: %s."
              % (len(comparison["unattempted_cells"]), len(comparison["planned_cells"]),
                 ", ".join("`%s`" % c for c in comparison["unattempted_cells"])), ""]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# handoff
# --------------------------------------------------------------------------

def handoff(args) -> None:
    comparison = load(args.comparison)
    v2, v1 = load(args.scorecard_v2), load(args.scorecard_v1)
    verification = load(args.verification)
    losses = load(args.loss_stages)
    if not verification.get("verified"):
        raise Failed("the verification record carries problems; no decision is recorded over unverified inputs")
    screens = {s["candidate_arm"]: s for s in v2["screens"]}
    verdicts = {arm: s["verdict"] for arm, s in screens.items()}
    if any(v == "pass" for v in verdicts.values()):
        outcome = "proceed-to-fresh-confirmation"
    elif any(v == "fail" for v in verdicts.values()):
        outcome = "reject"
    else:
        outcome = "inconclusive"
    false_findings = sum(a["raw_false_finding_items"] for a in comparison["attempts"])
    decision = {
        "artifact_id": "issue-153-decision",
        "schema_version": SCHEMA,
        "decided_at": now(),
        "experiment_id": v2["experiment_id"],
        "truth_version_scored": v2["truth_version"],
        "outcome": outcome,
        "screens": {arm: {"verdict": s["verdict"],
                          "criteria": {c["criterion"]: c["verdict"] for c in s["criteria"]},
                          "blockers": s["blockers"]} for arm, s in screens.items()},
        "screens_v1": {s["candidate_arm"]: s["verdict"] for s in v1["screens"]},
        "supported_raw_false_findings": false_findings,
        "reject_available": false_findings > 0,
        "positive_screen_available": False,
        "why_positive_screen_unavailable": [
            "%d of %d planned cells were never attempted" % (len(comparison["unattempted_cells"]), len(comparison["planned_cells"])),
            "no attempt is a valid completed outcome: five are operationally unresolved and three invalid",
            "two of the three buggy targets have no attempt, so every macro recall is unavailable",
        ],
        "measured_but_not_gating": {
            "matched_cost_ratio_medians": comparison["matched_pairs"]["medians"],
            "matched_pairs": comparison["matched_pairs"]["pair_counts"],
            "false_clean_by_arm": {arm: card["false_clean_count"] for arm, card in v2["arms"].items()},
            "slot_1_recall_v2_by_arm": {arm: card["per_target_recall_all_attempts"].get("slot-1")
                                        for arm, card in v2["arms"].items()},
            "finder_origin_material_recoveries": [r["defect_id"] for r in losses["rows"]
                                                  if r.get("outcome") == "recovered" and r.get("origin") == "finder"],
        },
        "what_would_change_it": {
            "reject": "a supported raw false finding in a candidate arm; none was ruled in any of the six packets, so no arm can be rejected on this evidence",
            "proceed": "a complete grid of valid completed cells on all four targets with the frozen mix, which the frozen limits cannot fund (one replacement remains against six cells to re-run) and which the retained evidence cannot certify (no launch argv); it needs a new preregistration whose freeze closes #199's gaps first",
            "inconclusive_stands_if": "nothing further is run; the eighteen unattempted cells stay unattempted",
        },
        "confirmation_study": {"recommended": False, "authorized": False,
                               "why": "a confirmation study follows a complete positive screen; none exists. What was observed on one buggy target (both stronger-verifier arms recovering what the control returned Approved on, one recovery finder-origin) is a hypothesis for a future freeze, not evidence for one."},
        "dispatch_authorized": False,
    }
    ledger = verification.get("ledger") or {}
    reserve = ledger.get("grading_closeout_reserve_usd")
    grading = (comparison.get("spend_columns") or {}).get("grading_usd")
    if reserve is not None and grading is not None:
        unused = money(usd(reserve) - usd(grading))
        if args.reserve_unused is None:
            args.reserve_unused = unused
        elif money(args.reserve_unused) != unused:
            raise Failed("reserve unused %s does not equal the reserve %s less charged grading %s = %s"
                         % (args.reserve_unused, reserve, grading, unused))
    stage = {
        "artifact_id": "issue-153-decision-handoff",
        "schema_version": SCHEMA,
        "stage": "decision",
        "created_at": now(),
        "disposition": "decision-delivered",
        "experiment_disposition": "stopped-incomplete",
        "decision": outcome,
        "decision_record": "decision.json",
        "dispatch_authorized": False,
        "dispatch_hold": "held. The epic's measurement is closed; nothing runs from this handoff.",
        "rulings_froze_before_unblinding": verification["rulings_froze_before_unblinding"],
        "revealed": "revealed/: every sealed plaintext this decision reads, byte-identical to its sealed digest (verification.json)",
        "cells": {"planned": len(comparison["planned_cells"]), "attempted": len(comparison["attempted_cells"]),
                  "unattempted": len(comparison["unattempted_cells"]), "attempts_recorded": len(comparison["attempts"]),
                  "valid_completed": sum(1 for a in comparison["attempts"] if a["valid_completed"])},
        "truth": {slot: {"status": t["status"], "defects_v1": t["defect_ids_v1"], "defects_after_grading": t["defect_ids_v2"],
                         "truth_version_after_grading": t["truth_version_after_grading"]} for slot, t in comparison["truth"].items()},
        "accounting": {
            "decision_charged_usd": "0",
            "grading_closeout_reserve_usd": ledger.get("grading_closeout_reserve_usd"),
            "reserve_unused_usd": args.reserve_unused,
            "ledger_actual_usd": ledger.get("actual_usd"),
            "ledger_uncertainty_usd": ledger.get("uncertainty_usd"),
            "ledger_reserved_usd": ledger.get("reserved_usd"),
            "ledger_events": ledger.get("events"),
            "ledger_chain_intact": ledger.get("chain_intact"),
            "frozen_total_cap_usd": ledger.get("frozen_total_cap_usd"),
            "note": "no model session was charged to this ticket; the ledger is left as #152 settled it, and no stop event is appended because budget.py implements none",
        },
        "next_stage": {
            "tickets": [138, 129, 199],
            "work": "#138 closes on this decision as a capped, inconclusive result; #129 records it under its known limits; #199 stays unscheduled and becomes the precondition of any future freeze.",
            "must_not": ["dispatch any cell from this handoff", "read the per-target figures as a comparison between arms",
                         "treat the inconclusive outcome as evidence for or against the stronger-verifier hypothesis"],
        },
    }
    write(args.out_decision, decision)
    write(args.out_handoff, stage)
    print("decision: %s (%s)" % (outcome, ", ".join("%s %s" % (a, v) for a, v in sorted(verdicts.items()))))


# --------------------------------------------------------------------------
# scan
# --------------------------------------------------------------------------

def scan_text(text: str) -> list:
    return sorted({"refusing to publish: the file contains the local path %r" % m for m in LOCAL_PATH.findall(text)})


def scan(paths: list) -> list:
    problems = []
    for path in paths:
        for problem in scan_text(read_text(path)):
            problems.append("%s: %s" % (path, problem))
    return problems


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------

def synthetic() -> dict:
    schedule = {"ordered_cells": [
        {"position": 1, "cell_id": "slot-2-A-replicate-1", "target_slot": "slot-2", "arm": "A", "replicate": 1},
        {"position": 2, "cell_id": "slot-2-B-replicate-1", "target_slot": "slot-2", "arm": "B", "replicate": 1},
        {"position": 3, "cell_id": "slot-1-A-replicate-1", "target_slot": "slot-1", "arm": "A", "replicate": 1},
        {"position": 4, "cell_id": "slot-1-B-replicate-1", "target_slot": "slot-1", "arm": "B", "replicate": 1},
        {"position": 5, "cell_id": "slot-1-C-replicate-1", "target_slot": "slot-1", "arm": "C", "replicate": 1}]}
    def attempt(ref, ordinal, completion, validity, cost, claims, pred=None):
        return {"attempt_ref": ref, "ordinal": ordinal, "completion": completion, "operational_validity": validity,
                "settled_usd": cost, "root_elapsed_seconds": 100.0, "is_replacement": pred is not None,
                "predecessor_ref": pred, "produced_claims": claims, "replacement_eligible": False,
                "invalidated_by": None if validity != "invalid" else "recorded basis", "validity_basis": "synthetic",
                "timing_availability": "synthetic"}
    manifest = {"cells": [
        {"position": 1, "arm": "A", "status": "attempted", "attempts": [attempt("position-01-attempt-1", 1, "stopped-runtime", "invalid", "0", False),
                                                                        attempt("position-01-attempt-2", 2, "complete", "unresolved", "3.0", True, "position-01-attempt-1")]},
        {"position": 2, "arm": "B", "status": "attempted", "attempts": [attempt("position-02-attempt-1", 1, "complete", "unresolved", "3.6", True)]},
        {"position": 3, "arm": "A", "status": "attempted", "attempts": [attempt("position-03-attempt-1", 1, "complete", "unresolved", "4.0", True)]},
        {"position": 4, "arm": "B", "status": "attempted", "attempts": [attempt("position-04-attempt-1", 1, "complete", "invalid", "6.0", True)]},
        {"position": 5, "arm": "C", "status": "attempted", "attempts": [attempt("position-05-attempt-1", 1, "stopped-budget", "unresolved", "9.0", True)]},
        {"position": 6, "arm": None, "status": "unattempted", "attempts": []}]}
    fidelity = {"attempts": [dict(attempt_ref=a["attempt_ref"], operational_validity=a["operational_validity"])
                             for c in manifest["cells"] for a in c["attempts"]]}
    reconciliation = {"attempts": [{"attempt_ref": a["attempt_ref"], "ledger_settled_usd": a["settled_usd"],
                                    "per_role_recovered_usd": {"primary": a["settled_usd"]}, "unassigned_residual_usd": "0",
                                    "self_report_usd": a["settled_usd"], "recomputed_usage_usd": a["settled_usd"]}
                                   for c in manifest["cells"] for a in c["attempts"]],
                      "columns": {"pre_freeze_usd": "1", "setup_and_selection_usd": "0", "review_attempts_usd": "25.6"},
                      "totals": {"retained_uncertainty_usd": "0"}, "conservative_bounds": []}
    def packet(pid, status, clean, recovered, sufficient, false=0):
        return {"packet_id": pid, "status": status, "clean_claim": clean, "honest_incomplete": False,
                "recovered_defect_ids": recovered, "sufficient_fix_defect_ids": sufficient, "partial_fix_defect_ids": [],
                "raw_items": len(recovered) + false, "raw_finding_items": len(recovered) + false,
                "raw_false_finding_items": false, "unique_false_claims": false, "action_errors": 0, "priority_errors": 0,
                "unresolved_adjudications": 0}
    derived = {"targets": {
        "<target-A>": {"register_status": "clean", "register_defect_ids": [], "defect_ids_after_grading": [],
                       "truth_version_after_grading": "v1", "confirmed_truth_revisions": [], "status_after_grading": "clean",
                       "packets": [packet("p1", "Approved", True, [], []), packet("p2", "Approved", True, [], [])]},
        "<target-B>": {"register_status": "buggy", "register_defect_ids": ["GT-x1"], "defect_ids_after_grading": ["GT-x1", "GT-x2"],
                       "truth_version_after_grading": "v2", "confirmed_truth_revisions": ["GT-x2"], "status_after_grading": "buggy",
                       "packets": [packet("p3", "Approved", True, [], []),
                                   packet("p4", "Changes Requested", False, ["GT-x1", "GT-x2"], ["GT-x2"]),
                                   packet("p5", "Changes Requested", False, ["GT-x1", "GT-x2"], ["GT-x2"])]}}}
    mapping = {"target_masks": {"slot-1": "<target-B>", "slot-2": "<target-A>"}, "mapping": [
        {"attempt_ref": "position-01-attempt-2", "packet_id": "p1", "arm": "A", "position": 1, "target_slot": "slot-2", "settled_usd": "3.0"},
        {"attempt_ref": "position-02-attempt-1", "packet_id": "p2", "arm": "B", "position": 2, "target_slot": "slot-2", "settled_usd": "3.6"},
        {"attempt_ref": "position-03-attempt-1", "packet_id": "p3", "arm": "A", "position": 3, "target_slot": "slot-1", "settled_usd": "4.0"},
        {"attempt_ref": "position-04-attempt-1", "packet_id": "p4", "arm": "B", "position": 4, "target_slot": "slot-1", "settled_usd": "6.0"},
        {"attempt_ref": "position-05-attempt-1", "packet_id": "p5", "arm": "C", "position": 5, "target_slot": "slot-1", "settled_usd": "9.0"}]}
    registers = {
        "slot-1": "# Target\n\n# Verdict\n\n1 material defect.\n\n# Defect register\n\n## GT-x1: something\n\ntext\n\n# Not ground truth\n",
        "slot-2": "# Target\n\n# Verdict\n\nadjudicated clean (D_u = 0)\n\n# Defect register\n\nNone.\n",
        "slot-3": "# Target\n\n# Verdict\n\n1 material defect.\n\n# Defect register\n\n## GT-y1: something\n"}
    no_packet = {"attempts": [{"attempt_ref": "position-01-attempt-1"}]}
    frozen = {"experiment_id": "synthetic", "cells": {"cell_ids": [c["cell_id"] for c in schedule["ordered_cells"]] + ["slot-3-A-replicate-1"]}}
    def item(ref, concept, ruling="supported", extra=None, kind="finding"):
        record = {"item_ref": ref, "kind": kind, "ruling": ruling, "concept": concept,
                  "materiality": "material" if ruling == "supported" and kind == "finding" else "not-applicable"}
        if extra:
            record["additional_concepts"] = [{"concept": e} for e in extra]
        return record
    items_by_packet = {"p1": [], "p2": [], "p3": [],
                       "p4": [item("p4/r1", "GT-x1"), item("p4/r2", "GT-x2")],
                       "p5": [item("p5/r1", "GT-x1", extra=["GT-x2"]), item("p5/r2", "GT-x1")]}
    derived["targets"]["<target-B>"]["packets"][2]["bundled_concept_items"] = 1
    derived["targets"]["<target-B>"]["packets"][2]["raw_items"] = 2
    derived["targets"]["<target-B>"]["packets"][2]["raw_finding_items"] = 2
    return dict(schedule=schedule, manifest=manifest, fidelity=fidelity, reconciliation=reconciliation,
                mapping=mapping, derived=derived, registers=registers, no_packet=no_packet, frozen=frozen,
                items_by_packet=items_by_packet)


def self_test() -> int:
    checks = []
    def check(name, ok):
        checks.append((name, bool(ok)))

    # 1. The register parser.
    clean = parse_register("# Verdict\n\nadjudicated clean (D_u = 0)\n\n# Defect register\n\nNone.\n")
    buggy = parse_register("# Verdict\n\n1 material defect (confirmed) — plus one excluded.\n\n# Defect register\n\n## GT-r1 — x\n\n# Reproduction\n\n## not a defect heading\n")
    check("1a clean register parses clean with no ids", clean["status"] == "clean" and clean["defect_ids"] == [])
    check("1b buggy register parses its GT headings only inside the register section", buggy == dict(buggy, status="buggy", defect_ids=["GT-r1"]))
    try:
        parse_register("# Verdict\n\n1 material defect.\n\n# Defect register\n\nNone.\n")
        check("1c a verdict that disagrees with its headings is refused", False)
    except Failed:
        check("1c a verdict that disagrees with its headings is refused", True)

    # 2. The join on a synthetic pilot.
    fx = synthetic()
    comparison = build_join(**fx)
    rows = {a["attempt_ref"]: a for a in comparison["attempts"]}
    check("2a every attempt joins, no-packet attempt included", len(rows) == 6)
    check("2b a no-packet attempt scores Incomplete with no claim", rows["position-01-attempt-1"]["status"] == "Incomplete"
          and rows["position-01-attempt-1"]["clean_claim"] is False and rows["position-01-attempt-1"]["recovered_defect_ids"] == [])
    check("2c an unresolved attempt is not valid, and not valid-completed", rows["position-02-attempt-1"]["valid"] is False
          and rows["position-02-attempt-1"]["valid_completed"] is False and rows["position-02-attempt-1"]["completed"] is True)
    check("2d Approved on the buggy target is false clean; on the clean target it is not",
          rows["position-03-attempt-1"]["false_clean"] is True and rows["position-01-attempt-2"]["false_clean"] is False)
    check("2e recall against v2 and v1 use their own denominators",
          rows["position-04-attempt-1"]["recall_v2"] == 1.0 and rows["position-04-attempt-1"]["recall_v1"] == 1.0
          and rows["position-03-attempt-1"]["recall_v2"] == 0.0)
    check("2f the v1 view drops the sufficient fix that only the added defect earned",
          rows["position-04-attempt-1"]["sufficient_v1"] == [] and rows["position-04-attempt-1"]["sufficient_fix_defect_ids"] == ["GT-x2"])
    check("2g the unattempted slot's truth comes from its register", comparison["truth"]["slot-3"]["defect_ids_v2"] == ["GT-y1"]
          and comparison["truth"]["slot-3"]["attempted"] is False)
    check("2h a cell is charged every attempt including its discarded predecessor",
          [c for c in comparison["cells"] if c["cell_id"] == "slot-2-A-replicate-1"][0]["charges_usd"] == "3.0000000")
    check("2i unattempted planned cells are listed", comparison["unattempted_cells"] == ["slot-3-A-replicate-1"])
    grid = grid_from(comparison, "v2", fx["frozen"])
    check("2j the grid carries the scorer's schema fields", all(k in grid["attempts"][0] for k in
          ("attempt_id", "cell_id", "target_slot", "arm", "replicate", "valid", "completed", "status", "clean_claim",
           "recovered_defect_ids", "sufficient_fix_defect_ids", "raw_false_finding_items", "unique_false_claims",
           "billed_cost_usd")) and grid["targets"]["slot-1"]["defect_ids"] == ["GT-x1", "GT-x2"])
    grid1 = grid_from(comparison, "v1", fx["frozen"])
    check("2k the v1 grid intersects recovered and sufficient ids with the v1 register",
          [a for a in grid1["attempts"] if a["attempt_ref"] == "position-04-attempt-1"][0]["sufficient_fix_defect_ids"] == []
          and grid1["targets"]["slot-1"]["defect_ids"] == ["GT-x1"])

    check("2l duplicate and bundled concept counts come from the ruled items",
          rows["position-04-attempt-1"]["duplicate_items_on_a_concept"] == 0 and rows["position-04-attempt-1"]["concepts_claimed"] == 2
          and rows["position-05-attempt-1"]["duplicate_items_on_a_concept"] == 1 and rows["position-05-attempt-1"]["bundled_concept_items"] == 1
          and rows["position-05-attempt-1"]["concepts_claimed"] == 2 and rows["position-01-attempt-1"]["concepts_claimed"] == 0)
    # 2m. concept_counts on the method's own cases
    two_supported = [{"item_ref": "a/r1", "ruling": "supported", "concept": "GT-1"}, {"item_ref": "a/r2", "ruling": "supported", "concept": "GT-1"}]
    two_false = [{"item_ref": "a/r1", "ruling": "false", "concept": "F1"}, {"item_ref": "a/r2", "ruling": "false", "concept": "F1"}]
    bundled = [{"item_ref": "a/r1", "ruling": "supported", "concept": "GT-1", "additional_concepts": [{"concept": "GT-2"}]}]
    c1, c2, c3 = concept_counts(two_supported), concept_counts(two_false), concept_counts(bundled)
    check("2m a supported duplicate pair is one concept and one duplicate; a false pair likewise and a false duplicate; a bundled item is neither",
          (c1["concepts_claimed"], c1["duplicate_items_on_a_concept"], c1["duplicate_false_items"]) == (1, 1, 0)
          and (c2["concepts_claimed"], c2["duplicate_items_on_a_concept"], c2["duplicate_false_items"]) == (1, 1, 1)
          and (c3["concepts_claimed"], c3["duplicate_items_on_a_concept"], c3["bundled_concept_items"]) == (2, 0, 1))
    amended = amended_items({"packets": [{"packet_id": "p", "items": [{"item_ref": "p/r1", "ruling": "false", "concept": "F1"}]}]},
                            [{"items": [{"item_ref": "p/r1", "ruling": "supported", "concept": "N2"}]}])
    check("2n an amendment replaces the item by item_ref before counting", amended["p"][0]["concept"] == "N2" and amended["p"][0]["ruling"] == "supported")
    # 2p. A false observation naming two concepts is bundled in the published count and not in the
    # cross-checked one, which is scoped like the grading stage's: the join must not trip on it.
    scoped = synthetic()
    scoped["items_by_packet"]["p3"] = [
        {"item_ref": "p3/r1", "kind": "observation", "ruling": "false", "concept": "N1", "materiality": "not-applicable",
         "additional_concepts": [{"concept": "N2"}]},
        {"item_ref": "p3/r2", "kind": "observation", "ruling": "false", "concept": "N1", "materiality": "not-applicable"}]
    scoped["derived"]["targets"]["<target-B>"]["packets"][0]["raw_items"] = 2
    row = {a["attempt_ref"]: a for a in build_join(**scoped)["attempts"]}["position-03-attempt-1"]
    check("2p bundled and duplicate counts over non-findings are published and not cross-checked against finding-scoped fields",
          row["bundled_concept_items"] == 1 and row["duplicate_items_on_a_concept"] == 1 and row["duplicate_false_items"] == 1
          and row["raw_false_finding_items"] == 0)
    bad = synthetic()
    bad["items_by_packet"]["p4"].append(item_dup := {"item_ref": "p4/r3", "kind": "finding", "ruling": "supported", "concept": "GT-x1"})
    try:
        build_join(**bad)
        check("2o ruled items that disagree with the derived raw count are refused", False)
    except Failed as exc:
        check("2o ruled items that disagree with the derived raw count are refused", "ruled items against" in str(exc))

    # 3. A join that disagrees with itself is refused.
    bad = synthetic()
    bad["mapping"]["mapping"][2]["arm"] = "C"
    try:
        build_join(**bad)
        check("3a a redaction-map arm that contradicts the schedule is refused", False)
    except Failed as exc:
        check("3a a redaction-map arm that contradicts the schedule is refused", "disagrees" in str(exc))
    bad = synthetic()
    bad["derived"]["targets"]["<target-A>"]["status_after_grading"] = "buggy"
    try:
        build_join(**bad)
        check("3b a changed clean/buggy classification is refused", False)
    except Failed as exc:
        check("3b a changed clean/buggy classification is refused", "classification changed" in str(exc))

    # 4. Matched ratios.
    pairs = matched_pairs({"a": {"target_slot": "s", "replicate": 1, "arm": "A", "charges_usd": "4"},
                           "b": {"target_slot": "s", "replicate": 1, "arm": "B", "charges_usd": "6"},
                           "c": {"target_slot": "s", "replicate": 1, "arm": "C", "charges_usd": "9"},
                           "a2": {"target_slot": "t", "replicate": 1, "arm": "A", "charges_usd": "2"},
                           "b2": {"target_slot": "t", "replicate": 1, "arm": "B", "charges_usd": "2"}})
    check("4a ratios per pair and medians over available pairs", abs(pairs["medians"]["B/A"] - 1.25) < 1e-9
          and abs(pairs["medians"]["C/A"] - 2.25) < 1e-9 and abs(pairs["medians"]["C/B"] - 1.5) < 1e-9
          and pairs["pair_counts"] == {"B/A": 2, "C/A": 1, "C/B": 1})
    check("4b a pair with no member is unavailable, not zero", pairs["pairs"][1]["C/A"] is None)

    # 5. The exact-set freeze check.
    with tempfile.TemporaryDirectory() as scratch:
        one = Path(scratch) / "one.json"; one.write_text("1", encoding="utf-8")
        two = Path(scratch) / "two.json"; two.write_text("2", encoding="utf-8")
        record = {"files": {"one.json": sha256_file(one), "two.json": sha256_file(two)}}
        problems = []
        check_freeze_exact(record, {"one.json": one, "two.json": two}, "t", problems)
        check("5a the exact set verifies", problems == [])
        problems = []
        check_freeze_exact(record, {"one.json": one}, "t", problems)
        check("5b an omitted frozen file is refused", any("was not supplied" in p for p in problems))
        problems = []
        check_freeze_exact(record, {"one.json": one, "two.json": two, "three.json": one}, "t", problems)
        check("5c an extra file is refused", any("not in the freeze record" in p for p in problems))
        two.write_text("changed", encoding="utf-8")
        problems = []
        check_freeze_exact(record, {"one.json": one, "two.json": two}, "t", problems)
        check("5d a changed file is refused", any("hashes to" in p for p in problems))

    # 5e. The packet reveal and its altered-input cases.
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        packet_a = {"packet_id": "aaaa", "status": "Approved", "body_markdown": "x", "items": []}
        packet_b = {"packet_id": "bbbb", "status": "Approved", "body_markdown": "y", "items": []}
        digest = lambda p: hashlib.sha256(json.dumps(p, sort_keys=True).encode("utf-8")).hexdigest()
        index = {"packets": [{"packet_id": "aaaa", "masked_packet_sha256": digest(packet_a)},
                             {"packet_id": "bbbb", "masked_packet_sha256": digest(packet_b)}]}
        packets_text = json.dumps({"packets": [packet_a, packet_b]}, indent=1)
        mapping = {"mapping": [{"packet_id": "aaaa", "attempt_ref": "position-01-attempt-1", "masked_packet_sha256": digest(packet_a), "worker_model": None},
                               {"packet_id": "bbbb", "attempt_ref": "position-02-attempt-1", "masked_packet_sha256": digest(packet_b), "worker_model": None}]}
        mapping_text = json.dumps(mapping, indent=1)
        revealed = root / "revealed"; revealed.mkdir()
        (revealed / "grading-packets.json").write_text(packets_text, encoding="utf-8")
        (revealed / "redaction-map.json").write_text(mapping_text, encoding="utf-8")
        archive = root / "grading-packets.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(revealed / "grading-packets.json", arcname="grading-packets.json")
            tar.add(revealed / "redaction-map.json", arcname="redaction-map.json")
        sums = "%s  grading-packets.tar.gz\n" % sha256_file(archive)
        record = reveal_packets(archive, sums)
        check("5e the reveal records both members from an archive that hashes as sealed",
              sorted(record["members"]) == ["grading-packets.json", "redaction-map.json"]
              and record["members"]["grading-packets.json"] == sha256_file(revealed / "grading-packets.json"))
        try:
            reveal_packets(archive, "%s  grading-packets.tar.gz\n" % ("0" * 64))
            check("5f an archive that does not hash as sealed is refused", False)
        except Failed as exc:
            check("5f an archive that does not hash as sealed is refused", "not the sealed plaintext" in str(exc))
        short = root / "short.tar.gz"
        with tarfile.open(short, "w:gz") as tar:
            tar.add(revealed / "grading-packets.json", arcname="grading-packets.json")
        try:
            reveal_packets(short, "%s  grading-packets.tar.gz\n" % sha256_file(short))
            check("5g an archive lacking a member is refused", False)
        except Failed as exc:
            check("5g an archive lacking a member is refused", "lacks redaction-map.json" in str(exc))
        problems, checked = [], []
        check_packets(revealed, index, record, problems, checked)
        check("5h the intact reveal verifies", problems == [])
        # emptied packets: refused by the sealed digest, and by the index completeness check
        (revealed / "grading-packets.json").write_text(json.dumps({"packets": []}), encoding="utf-8")
        problems = []
        check_packets(revealed, index, record, problems, [])
        check("5i an emptied packet file is refused", any("sealed archive member" in p for p in problems))
        problems = []
        check_packets(revealed, index, {"members": {"grading-packets.json": sha256_file(revealed / "grading-packets.json"),
                                                    "redaction-map.json": record["members"]["redaction-map.json"]}}, problems, [])
        check("5j a packet missing from the file is refused against the index even with a matching digest",
              any("in the public index and not in the revealed file" in p for p in problems))
        # duplicated packet
        (revealed / "grading-packets.json").write_text(json.dumps({"packets": [packet_a, packet_a, packet_b]}), encoding="utf-8")
        problems = []
        check_packets(revealed, index, {"members": {"grading-packets.json": sha256_file(revealed / "grading-packets.json"),
                                                    "redaction-map.json": record["members"]["redaction-map.json"]}}, problems, [])
        check("5k a duplicated packet is refused", any("appears twice" in p for p in problems))
        (revealed / "grading-packets.json").write_text(packets_text, encoding="utf-8")
        # a changed worker_model in the map: refused by the sealed digest
        changed = json.loads(mapping_text); changed["mapping"][0]["worker_model"] = "claude-opus-5"
        (revealed / "redaction-map.json").write_text(json.dumps(changed, indent=1), encoding="utf-8")
        problems = []
        check_packets(revealed, index, record, problems, [])
        check("5l a changed redaction-map row is refused by the sealed digest", any("redaction-map.json hashes to" in p for p in problems))
        (revealed / "redaction-map.json").write_text(mapping_text, encoding="utf-8")
        run = subprocess.run([sys.executable, __file__, "reveal", "--archive", str(archive), "--sums", str(root / "missing-sums"),
                              "--out", str(root / "r.json")], capture_output=True, text=True, encoding="utf-8")
        check("5m reveal exits 2 on an unreadable SHA256SUMS", run.returncode == 2)
        problems = []
        check_reveal_record(record, sums, problems)
        check("5o the reveal record verifies against the sealed sums", problems == [])
        problems = []
        check_reveal_record(record, "%s  grading-packets.tar.gz\n" % ("1" * 64), problems)
        check("5p a reveal record naming another archive is refused", any("not the one #151 sealed" in p for p in problems))
        problems = []
        check_reveal_record({"archive_sha256": record["archive_sha256"], "archive_sha256_as_sealed": record["archive_sha256"],
                             "members": {"grading-packets.json": record["members"]["grading-packets.json"]}}, sums, problems)
        check("5q a reveal record missing a member digest is refused", any("no digest for redaction-map.json" in p for p in problems))
        (root / "sums").write_text(sums, encoding="utf-8")
        run = subprocess.run([sys.executable, __file__, "reveal", "--archive", str(archive), "--sums", str(root / "sums"),
                              "--out", str(root / "r.json")], capture_output=True, text=True, encoding="utf-8")
        check("5n reveal exits 0 and writes the record", run.returncode == 0 and (root / "r.json").exists())

    # 6. The loss-stage vocabulary.
    check("6a a known stage and origin pass", validate_loss_stages({"rows": [
        {"attempt_ref": "x", "defect_id": "d", "outcome": "missed", "stage": "never-discovered", "evidence": ["e"]},
        {"attempt_ref": "x", "defect_id": "d", "outcome": "recovered", "origin": "finder", "evidence": ["e"]}]}) == [])
    check("6b an unknown stage is refused", validate_loss_stages({"rows": [
        {"attempt_ref": "x", "defect_id": "d", "outcome": "missed", "stage": "lost-somehow", "evidence": ["e"]}]}) != [])
    check("6c a row without evidence is refused", validate_loss_stages({"rows": [
        {"attempt_ref": "x", "defect_id": "d", "outcome": "recovered", "origin": "primary", "evidence": []}]}) != [])

    # 7. The scan.
    check("7a a home or temporary path is refused", scan_text("see /Users/someone/x and /tmp/y/z") != [])
    check("7b a repository path and a ~ path pass", scan_text("docs/research/x.md and ~/.config/bounded-discovery/issue-153") == [])

    # 7b. Money renders as fixed decimals, zero included.
    check("7c zero money renders as a fixed decimal", money("0") == "0.0000000" and money("3.85953300") == "3.8595330")

    # 7d. A discarded predecessor never inherits its successor's timing sidecar.
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        (root / "position-01" / "work").mkdir(parents=True)
        (root / "position-01" / "work" / "timing.json").write_text(json.dumps({
            "root_dispatched_at": "2026-09-09T05:00:00+00:00", "payload_validated_at": "2026-09-09T05:10:00+00:00",
            "completed_at": "2026-09-09T05:20:00+00:00"}), encoding="utf-8")
        timing = read_timing(root, ["position-01-attempt-1", "position-01-attempt-2"])
        check("7d the surviving attempt gets the sidecar and its predecessor gets none",
              "position-01-attempt-1" not in timing and timing["position-01-attempt-2"]["elapsed_to_payload_seconds"] == 600.0
              and timing["position-01-attempt-2"]["elapsed_to_completion_seconds"] == 1200.0)

    # 8. The ledger summary.
    summary = ledger_summary({"actual_usd": "1", "reserved_usd": "0", "events": [
        {"event_id": "a", "previous_event_id": None, "ticket": 1}, {"event_id": "b", "previous_event_id": "a", "ticket": 2}]})
    check("8a an intact chain is reported intact", summary["chain_intact"] is True and summary["events"] == 2)
    summary = ledger_summary({"events": [{"event_id": "a", "previous_event_id": None}, {"event_id": "b", "previous_event_id": "zz"}]})
    check("8b a broken chain is reported broken", summary["chain_intact"] is False)

    # 9. CLI exit codes through subprocess.
    with tempfile.TemporaryDirectory() as scratch:
        leaky = Path(scratch) / "leaky.md"; leaky.write_text("path /private/tmp/secret\n", encoding="utf-8")
        clean_file = Path(scratch) / "clean.md"; clean_file.write_text("nothing here\n", encoding="utf-8")
        run = subprocess.run([sys.executable, __file__, "scan", str(leaky)], capture_output=True, text=True, encoding="utf-8")
        check("9a scan exits 1 with one line per violation", run.returncode == 1 and "local path" in run.stdout)
        run = subprocess.run([sys.executable, __file__, "scan", str(clean_file)], capture_output=True, text=True, encoding="utf-8")
        check("9b scan exits 0 on a clean file", run.returncode == 0)
        run = subprocess.run([sys.executable, __file__, "scan", str(Path(scratch) / "missing.md")], capture_output=True, text=True, encoding="utf-8")
        check("9c an unreadable input exits 2", run.returncode == 2)
        # score refuses a scorer whose digest is not the pinned one
        fake_scorer = Path(scratch) / "score_attempts.py"; fake_scorer.write_text("print('no')\n", encoding="utf-8")
        frozen = Path(scratch) / "manifest.json"
        frozen.write_text(json.dumps({"pins": {"freeze_tools": {"score_attempts.py": {"sha256": "0" * 64}}}}), encoding="utf-8")
        gridfile = Path(scratch) / "grid.json"; gridfile.write_text("{}", encoding="utf-8")
        run = subprocess.run([sys.executable, __file__, "score", "--scorer", str(fake_scorer), "--frozen", str(frozen),
                              "--grid", str(gridfile), "--out-json", str(Path(scratch) / "o.json"),
                              "--out-md", str(Path(scratch) / "o.md")], capture_output=True, text=True, encoding="utf-8")
        check("9d score refuses an unpinned scorer with exit 1", run.returncode == 1 and "pinned" in run.stdout)

    failures = 0
    for name, ok in checks:
        print(("ok   " if ok else "FAIL ") + name)
        failures += 0 if ok else 1
    print("self-test: %d checks, %d failures" % (len(checks), failures))
    return 1 if failures else 0


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("reveal")
    p.add_argument("--archive", required=True)
    p.add_argument("--sums", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("verify")
    p.add_argument("--bundle", required=True)
    p.add_argument("--targets-sums", required=True)
    p.add_argument("--schedule-sums", required=True)
    p.add_argument("--packets-dir", required=True)
    p.add_argument("--reveal", required=True)
    p.add_argument("--grading-dir", required=True)
    p.add_argument("--ledger")
    p.add_argument("--out", required=True)
    p = sub.add_parser("join")
    p.add_argument("--bundle", required=True)
    p.add_argument("--closeout-dir", required=True)
    p.add_argument("--frozen", required=True)
    p.add_argument("--evidence")
    p.add_argument("--loss-stages")
    p.add_argument("--grading-usd", default="0")
    p.add_argument("--out-dir", required=True)
    p = sub.add_parser("score")
    p.add_argument("--scorer", required=True)
    p.add_argument("--frozen", required=True)
    p.add_argument("--grid", required=True)
    p.add_argument("--out-json", required=True)
    p.add_argument("--out-md", required=True)
    p = sub.add_parser("compare")
    p.add_argument("--comparison", required=True)
    p.add_argument("--scorecard-v2", required=True)
    p.add_argument("--scorecard-v1", required=True)
    p.add_argument("--loss-stages", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("handoff")
    p.add_argument("--comparison", required=True)
    p.add_argument("--scorecard-v2", required=True)
    p.add_argument("--scorecard-v1", required=True)
    p.add_argument("--verification", required=True)
    p.add_argument("--loss-stages", required=True)
    p.add_argument("--reserve-unused", default=None)
    p.add_argument("--out-decision", required=True)
    p.add_argument("--out-handoff", required=True)
    p = sub.add_parser("scan")
    p.add_argument("files", nargs="+")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.command:
        parser.error("a command or --self-test is required")
    try:
        if args.command == "reveal":
            record = reveal_packets(args.archive, read_text(args.sums))
            write(args.out, record)
            print("wrote %s: archive %s..., %d member digest(s)" % (args.out, record["archive_sha256"][:12], len(record["members"])))
            return 0
        if args.command == "verify":
            record = verify(args)
            write(args.out, record)
            for problem in record["problems"]:
                print(problem)
            print("%s: %d digests checked, %d problem(s)" % (args.out, len(record["checked"]), len(record["problems"])))
            return 1 if record["problems"] else 0
        if args.command == "join":
            join(args)
        elif args.command == "score":
            score(args)
        elif args.command == "compare":
            compare(args)
        elif args.command == "handoff":
            handoff(args)
        elif args.command == "scan":
            problems = scan(args.files)
            for problem in problems:
                print(problem)
            if problems:
                return 1
            print("scan: %d file(s) carry no local path" % len(args.files))
    except Failed as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
