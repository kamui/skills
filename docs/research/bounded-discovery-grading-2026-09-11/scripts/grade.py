#!/usr/bin/env python3
"""#152's independent grading: the mechanical half.

The adjudicator, a fresh headless session per masked target, makes every
judgment: whether a claim is supported, material, which concept it belongs
to, whether its fix suffices, whether its priority or action is wrong. This
script does everything around those judgments that must not depend on them:

* ``split``     - one packet file per masked target, from #151's sealed
                  ``grading-packets.json``; nothing operational reaches it;
* ``render``    - the adjudicator prompt from the public template, refusing
                  an unfilled placeholder;
* ``validate``  - the ruling table's shape: every packet covered, every axis
                  in its vocabulary, every concept described, every ruling
                  consistent with its two supporting axes;
* ``derive``    - the per-attempt scoring fields the frozen scorer consumes
                  (``score_attempts.py``), mapped from the rulings and shown
                  beside the raw item counts they collapse - the only place
                  the raw-versus-concept arithmetic happens;
* ``freeze``    - the digest of every ruling file and of the derived fields,
                  recorded before the arm mapping is opened, and ``--check``
                  to prove a later copy is byte-identical;
* ``publish``   - the anonymous public summary: counts per packet and masked
                  target, no path, no symbol, no slot, scanned against #149's
                  frozen manifest before it is written;
* ``seal``      - the full ruling tables under #148's key, with the plaintext
                  digests recorded beside the ciphertext;
* ``audit``     - one adjudicator transcript: the model and effort on every
                  assistant line, whether the context was fresh, and every
                  path a tool call named, classified against the permitted
                  roots - a read outside them is reported, never smoothed;
* ``meter``     - one session's cost from its transcript at the frozen rates
                  and from the runtime's own envelope, charging the larger
                  and recording the difference;
* ``scan``      - every public file of this bundle against the same forbidden
                  set, before it is committed;
* ``handoff``   - the stage record #153 reads, assembled from the records
                  above and refusing to carry anything operational;
* ``--self-test`` - the scoring mapping on five synthetic cases: a supported
                  duplicate pair, a false duplicate pair, a true fact with an
                  invented impact, an insufficient fix and an unresolved claim.

Usage::

    grade.py split --packets F --out-dir D
    grade.py render --template T --target-ref R --packets F --register F \\
        --clone D --base-branch B --work D --out F --exec-note S --budget S \\
        --out-prompt F
    grade.py validate --rulings F --packets F
    grade.py derive --rulings F... --out F
    grade.py freeze --rulings F... --derived F --out F [--check]
    grade.py publish --derived F --rulings F... --frozen manifest.json \\
        --known-cue S --out F
    grade.py seal --key K --out-dir D FILE...
    grade.py audit --transcript F --root D... --out F
    grade.py meter --transcript F --envelope F --rates F --tools D --out F
    grade.py scan --frozen manifest.json FILE...
    grade.py handoff --public F --freeze F --seal F --derived F \
        --metering F... --audit F... --frozen manifest.json --out F
    grade.py --self-test

Exit: 0 on success, 1 on a content violation with one line per violation on
stdout, 2 when an input cannot be read or a subprocess fails.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RULINGS = ("supported", "false", "unresolved", "not-applicable")
SUPPORT = ("supported", "false", "unresolved", "none")
MATERIALITY = ("material", "sub-threshold", "not-applicable")
FIXES = ("sufficient", "partial", "absent", "unresolved", "not-applicable")
KINDS = ("finding", "question", "observation", "hygiene")
SAFETY = ("supported", "unsupported", "unresolved")
STATUSES = ("Approved", "Changes Requested", "Needs Information", "Incomplete")
SOURCE_EXTENSIONS = ("go", "rs", "toml", "mod", "lock")
PUBLIC_PATH_ROOTS = ("docs/", "scripts/", "metering/", "sealed/", "prompts/", "packets/",
                     "WORK/", "BUNDLE/", ".config/bounded-discovery/", "config/bounded-discovery/")


class Failed(Exception):
    """A content violation: reported on stdout, exit 1."""


def load(path):
    try:
        return json.loads(Path(os.path.expanduser(str(path))).read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.stderr.write("missing %s\n" % path)
        raise SystemExit(2)
    except (OSError, ValueError) as exc:
        sys.stderr.write("cannot read %s: %s\n" % (path, exc))
        raise SystemExit(2)


def write(path, payload) -> None:
    target = Path(os.path.expanduser(str(path)))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path) -> str:
    return hashlib.sha256(Path(os.path.expanduser(str(path))).read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------
# split: one packet file per masked target
# --------------------------------------------------------------------------

def split(packets, out_dir) -> dict:
    """Group the sealed packets by masked target.

    Only the grader-facing fields travel: packet id, status, body, items and
    the masked target token. The document-level instructions and blinding
    note travel with every file, because the grader reads one file."""
    by_target = {}
    for packet in packets["packets"]:
        for key in ("packet_id", "status", "body_markdown", "items", "target_ref"):
            if key not in packet:
                raise Failed("packet %s lacks %s" % (packet.get("packet_id"), key))
        by_target.setdefault(packet["target_ref"], []).append(packet)
    written = {}
    for target_ref, group in sorted(by_target.items()):
        name = "packets-%s.json" % re.sub(r"[^A-Za-z0-9]+", "-", target_ref).strip("-")
        payload = {
            "artifact_id": "issue-152-packets-" + target_ref,
            "blinding_limit": packets.get("blinding_limit"),
            "instructions": packets.get("instructions"),
            "packet_count": len(group),
            "packets": sorted(group, key=lambda p: p["packet_id"]),
            "schema_version": packets.get("schema_version"),
            "source_packets_sha256": None,
            "target_ref": target_ref,
        }
        write(Path(out_dir) / name, payload)
        written[target_ref] = str(Path(out_dir) / name)
    return written


# --------------------------------------------------------------------------
# render: the prompt from the public template
# --------------------------------------------------------------------------

def render(template: str, values: dict) -> str:
    text = template
    for key, value in values.items():
        text = text.replace("{%s}" % key, str(value))
    left = sorted(set(re.findall(r"\{[A-Z_]+\}", text)))
    if left:
        raise Failed("unfilled placeholder(s): " + ", ".join(left))
    return text


# --------------------------------------------------------------------------
# validate: the ruling table's shape
# --------------------------------------------------------------------------

def expected_ruling(defect: str, consequence: str) -> str:
    if defect == "none" and consequence == "none":
        return "not-applicable"
    if "false" in (defect, consequence):
        return "false"
    if "unresolved" in (defect, consequence):
        return "unresolved"
    return "supported"


def target_token(value) -> str:
    """The masked target token in its canonical ``<target-X>`` form.

    An adjudicator wrote the token without its angle brackets once; the label
    is not a judgment, so it is normalised rather than sent back."""
    return "<%s>" % str(value or "").strip("<>")


def confirmed_revisions(rulings: dict) -> set:
    """Proposed truth revisions that count as truth for the rescoring.

    The template records a revision only when the adjudicator confirmed it
    with independent evidence, so a revision without a status is confirmed;
    one that carries any other status is excluded."""
    return {r["proposed_id"] for r in rulings.get("proposed_truth_revisions") or []
            if r.get("proposed_id") and r.get("status", "confirmed") == "confirmed"}


def item_concepts(item: dict) -> list:
    """The item's primary concept and its bundled additional concepts, each
    with the fix ruling that applies to that concept alone."""
    pairs = [(item.get("concept"), item.get("requested_fix"))]
    for extra in item.get("additional_concepts") or []:
        pairs.append((extra.get("concept"), extra.get("requested_fix")))
    return pairs


def validate(rulings: dict, packets: dict) -> list:
    problems = []
    expected_ids = {p["packet_id"] for p in packets["packets"]}
    if target_token(rulings.get("target_ref")) != target_token(packets.get("target_ref")):
        problems.append("target_ref %r does not match the packets' %r"
                        % (rulings.get("target_ref"), packets.get("target_ref")))
    if rulings.get("register_status") not in ("buggy", "clean"):
        problems.append("register_status must be buggy or clean")
    register_ids = set(rulings.get("register_defect_ids") or [])
    if (rulings.get("register_status") == "clean") != (not register_ids):
        problems.append("register_status disagrees with register_defect_ids")
    concepts = rulings.get("concepts") or {}
    for cid in register_ids:
        if cid not in concepts:
            problems.append("register defect %s is not described under concepts" % cid)
    proposed = confirmed_revisions(rulings)
    seen_packets = set()
    status_by_packet = {p["packet_id"]: p["status"] for p in packets["packets"]}
    for packet in rulings.get("packets") or []:
        pid = packet.get("packet_id")
        if pid not in expected_ids:
            problems.append("packet %s is not in the packet file" % pid)
            continue
        if pid in seen_packets:
            problems.append("packet %s ruled twice" % pid)
        seen_packets.add(pid)
        if packet.get("status") != status_by_packet[pid]:
            problems.append("packet %s status %r differs from the packet's %r"
                            % (pid, packet.get("status"), status_by_packet[pid]))
        if not isinstance(packet.get("explicit_clean_claim"), bool):
            problems.append("packet %s explicit_clean_claim must be a boolean" % pid)
        if packet.get("status") == "Approved" and packet.get("explicit_clean_claim") is False:
            problems.append("packet %s is Approved, which is an explicit clean return, but "
                            "explicit_clean_claim is false" % pid)
        refs = set()
        for item in packet.get("items") or []:
            ref = item.get("item_ref", "")
            if not ref.startswith(pid + "/r"):
                problems.append("item %r is not keyed under packet %s" % (ref, pid))
            if ref in refs:
                problems.append("item %s appears twice" % ref)
            refs.add(ref)
            for field, vocab in (("kind", KINDS), ("defect_supported", SUPPORT),
                                 ("consequence_supported", SUPPORT), ("ruling", RULINGS),
                                 ("materiality", MATERIALITY), ("requested_fix", FIXES)):
                if item.get(field) not in vocab:
                    problems.append("item %s %s=%r is not one of %s"
                                    % (ref, field, item.get(field), ", ".join(vocab)))
                    break
            else:
                want = expected_ruling(item["defect_supported"], item["consequence_supported"])
                if item["ruling"] != want:
                    problems.append("item %s ruling %s does not follow from defect=%s and "
                                    "consequence=%s (expected %s)"
                                    % (ref, item["ruling"], item["defect_supported"],
                                       item["consequence_supported"], want))
                if item["ruling"] != "supported" and item["materiality"] != "not-applicable":
                    problems.append("item %s is %s yet carries materiality %s"
                                    % (ref, item["ruling"], item["materiality"]))
                if item["ruling"] == "supported" and item["materiality"] == "not-applicable":
                    problems.append("item %s is supported but has no materiality" % ref)
                material = item["ruling"] == "supported" and item["materiality"] == "material"
                if not material and item["requested_fix"] != "not-applicable":
                    problems.append("item %s is not a supported material item yet has a "
                                    "requested_fix ruling" % ref)
                if material and item["requested_fix"] == "not-applicable":
                    problems.append("item %s is supported and material but has no fix ruling" % ref)
                if material and item["concept"] not in register_ids | proposed:
                    problems.append("item %s is supported and material but its concept %r is "
                                    "neither a register defect nor a proposed revision"
                                    % (ref, item.get("concept")))
            if item.get("concept") not in concepts:
                problems.append("item %s names concept %r, which is not described"
                                % (ref, item.get("concept")))
            for extra in item.get("additional_concepts") or []:
                if extra.get("concept") not in register_ids | proposed:
                    problems.append("item %s bundles concept %r, which is neither a register "
                                    "defect nor a confirmed revision" % (ref, extra.get("concept")))
                if extra.get("concept") == item.get("concept"):
                    problems.append("item %s bundles its own primary concept" % ref)
                if extra.get("requested_fix") not in FIXES[:-1]:
                    problems.append("item %s bundled concept %r has fix ruling %r"
                                    % (ref, extra.get("concept"), extra.get("requested_fix")))
                if not (item.get("ruling") == "supported" and item.get("materiality") == "material"):
                    problems.append("item %s bundles a concept but is not a supported material item"
                                    % ref)
            for field in ("priority_error", "action_error"):
                if not isinstance(item.get(field), bool):
                    problems.append("item %s %s must be a boolean" % (ref, field))
            if not item.get("citations"):
                problems.append("item %s has no citations" % ref)
        for claim in packet.get("safety_claims") or []:
            if claim.get("ruling") not in SAFETY:
                problems.append("packet %s safety claim %r has ruling %r"
                                % (pid, (claim.get("quote") or "")[:40], claim.get("ruling")))
    missing = expected_ids - seen_packets
    outstanding = set()
    for entry in rulings.get("outstanding") or []:
        outstanding.add(entry if isinstance(entry, str) else str(entry.get("packet_id", entry)))
    for pid in sorted(missing):
        if not any(pid in o for o in outstanding):
            problems.append("packet %s has no rulings and is not listed as outstanding" % pid)
    return sorted(set(problems))


# --------------------------------------------------------------------------
# derive: rulings -> the frozen scorer's per-attempt fields
# --------------------------------------------------------------------------

def derive_packet(packet: dict, register_ids: set, proposed_ids: set) -> dict:
    """Collapse one packet's raw items into the fields score_attempts.py reads.

    Raw counts count every item; concept counts count each concept once per
    attempt. Both are reported so the collapse is visible."""
    items = packet.get("items") or []
    findings = [i for i in items if i["kind"] == "finding"]
    truth = register_ids | proposed_ids
    material = [i for i in items if i["ruling"] == "supported" and i["materiality"] == "material"]
    pairs = [(c, f) for i in material for c, f in item_concepts(i) if c in truth]
    recovered = sorted({c for c, _ in pairs})
    # A concept is sufficiently fixed when at least one item recovering it
    # requests a sufficient fix; a partial or absent request never credits.
    sufficient = sorted({c for c, f in pairs if f == "sufficient"})
    false_findings = [i for i in findings if i["ruling"] == "false"]
    false_non_findings = [i for i in items if i["kind"] != "finding" and i["ruling"] == "false"]
    unresolved = [i for i in items if i["ruling"] == "unresolved"]
    kinds = {k: sum(1 for i in items if i["kind"] == k) for k in KINDS}
    return {
        "packet_id": packet["packet_id"],
        "status": packet["status"],
        "clean_claim": bool(packet.get("explicit_clean_claim")) or packet["status"] == "Approved",
        "honest_incomplete": bool(packet.get("honest_incomplete")),
        "raw_items": len(items),
        "raw_items_by_kind": kinds,
        "raw_finding_items": len(findings),
        "raw_supported_material_items": len(material),
        "raw_supported_material_items_on_truth": len([i for i in material if i["concept"] in truth]),
        "recovered_defect_ids": recovered,
        "sufficient_fix_defect_ids": sufficient,
        "partial_fix_defect_ids": sorted({c for c, f in pairs if f == "partial"} - set(sufficient)),
        "bundled_concept_items": sum(1 for i in material if i.get("additional_concepts")),
        "raw_false_finding_items": len(false_findings),
        "unique_false_claims": len({i["concept"] for i in false_findings}),
        "raw_false_non_finding_items": len(false_non_findings),
        "unique_false_non_finding_claims": len({i["concept"] for i in false_non_findings}),
        "raw_sub_threshold_items": len([i for i in items if i["ruling"] == "supported"
                                        and i["materiality"] == "sub-threshold"]),
        "unresolved_adjudications": len(unresolved),
        "unique_unresolved_concepts": len({i["concept"] for i in unresolved}),
        "action_errors": sum(1 for i in items if i.get("action_error")),
        "priority_errors": sum(1 for i in items if i.get("priority_error")),
        "unsupported_safety_claims": sum(1 for c in packet.get("safety_claims") or []
                                         if c.get("ruling") == "unsupported"),
        "unresolved_safety_claims": sum(1 for c in packet.get("safety_claims") or []
                                        if c.get("ruling") == "unresolved"),
        "safety_claims": len(packet.get("safety_claims") or []),
        "unmasking_cues": len(packet.get("unmasking_cues") or []),
    }


def derive(ruling_files: list) -> dict:
    targets = {}
    for path in ruling_files:
        rulings = load(path)
        register_ids = set(rulings.get("register_defect_ids") or [])
        proposed_ids = confirmed_revisions(rulings)
        target_ref = target_token(rulings["target_ref"])
        entry = targets.setdefault(target_ref, {
            "truth_version_graded": rulings.get("truth_version"),
            "register_status": rulings.get("register_status"),
            "register_defect_ids": sorted(register_ids),
            "confirmed_truth_revisions": sorted(proposed_ids),
            "truth_version_after_grading": "v2" if proposed_ids else rulings.get("truth_version"),
            "defect_ids_after_grading": sorted(register_ids | proposed_ids),
            "status_after_grading": "buggy" if register_ids | proposed_ids else "clean",
            "packets": [],
            "outstanding": rulings.get("outstanding") or [],
            "rulings_file": os.path.basename(str(path)),
        })
        for packet in rulings.get("packets") or []:
            entry["packets"].append(derive_packet(packet, register_ids, proposed_ids))
        entry["packets"].sort(key=lambda p: p["packet_id"])
    return {"artifact_id": "issue-152-derived-fields", "derived_at": now(),
            "schema_version": "bounded-discovery-v1", "targets": targets,
            "note": "Per-packet fields in the shape score_attempts.py consumes, without arm, "
                    "validity or cost: #153 joins those after the freeze. Raw counts count every "
                    "published item; recovered and false-claim counts count each concept once "
                    "per attempt."}


# --------------------------------------------------------------------------
# freeze: digests recorded before the mapping is opened
# --------------------------------------------------------------------------

def freeze(ruling_files: list, derived_file) -> dict:
    files = {}
    for path in list(ruling_files) + [derived_file]:
        files[os.path.basename(str(path))] = sha256_file(path)
    combined = hashlib.sha256("\n".join("%s  %s" % (d, n) for n, d in sorted(files.items()))
                              .encode("utf-8")).hexdigest()
    return {"artifact_id": "issue-152-rulings-freeze", "frozen_at": now(),
            "files": files, "combined_sha256": combined,
            "schema_version": "bounded-discovery-v1",
            "note": "Recorded before the redaction map was opened. A later copy of any file "
                    "listed here that does not hash to the value recorded is not the frozen "
                    "ruling; grade.py freeze --check verifies."}


def check_freeze(record: dict, ruling_files: list, derived_file) -> list:
    problems = []
    for path in list(ruling_files) + [derived_file]:
        name = os.path.basename(str(path))
        if name not in record["files"]:
            problems.append("%s is not in the freeze record" % name)
        elif sha256_file(path) != record["files"][name]:
            problems.append("%s does not hash to its frozen digest" % name)
    return problems


# --------------------------------------------------------------------------
# publish: the anonymous public summary, scanned before it is written
# --------------------------------------------------------------------------

def disclosive_values(frozen) -> tuple:
    """What must never appear in a public artifact, from #149's manifest.

    The same derivation the closeout uses: every slot name, repository (and
    each of its path components), url, pinned object id and pull-request
    reference; allowed are this repository's own public pins."""
    forbidden, allowed = set(), set()
    pins = (frozen or {}).get("pins") or {}
    for key in ("policy_commit", "skill_tree"):
        if pins.get(key):
            allowed.add(pins[key])
    if (frozen or {}).get("repository_commit_read"):
        allowed.add(frozen["repository_commit_read"])
    for slot, entry in sorted(((frozen or {}).get("targets") or {}).items()):
        forbidden.add(slot)
        target = (entry or {}).get("target") or {}
        for key in ("repository", "url", "head_oid", "base_oid_recorded", "merge_base_oid"):
            if target.get(key):
                forbidden.add(str(target[key]))
        if target.get("repository"):
            forbidden.update(part for part in str(target["repository"]).split("/") if part)
        if target.get("pr"):
            forbidden.add("%s#%s" % (target.get("repository", ""), target["pr"]))
            forbidden.add("#%s" % target["pr"])
    return sorted(forbidden), sorted(allowed)


def leak_scan(payload, forbidden, allowed=()) -> list:
    text = json.dumps(payload)
    found = []
    for name in forbidden:
        if name and name in text:
            found.append("refusing to write: the payload contains %r, which identifies a target"
                         % name)
    for match in set(re.findall(r"\b[0-9a-f]{40}\b", text)):
        if match not in set(allowed):
            found.append("refusing to write: the payload contains the object id %s..., which is "
                         "not one of this repository's public pins" % match[:8])
    # A source path names the project as surely as its name does. Source
    # extensions are refused outright; a slash path is refused unless it is
    # rooted in this repository or the evaluator's own working tree.
    for match in set(re.findall(r"[A-Za-z0-9_.~$/-]+\.(?:go|rs|py|md|toml|mod|lock|json|txt|sh)\b",
                                text)):
        extension = match.rsplit(".", 1)[-1]
        if extension in SOURCE_EXTENSIONS:
            found.append("refusing to write: the payload contains the source path %r" % match)
        elif "/" in match and not match.lstrip("$~/").startswith(PUBLIC_PATH_ROOTS):
            found.append("refusing to write: the payload contains the path-shaped value %r" % match)
    return sorted(set(found))


def public_defect_ids(entry: dict) -> dict:
    """Register IDs are renamed positionally so their letters name nothing."""
    ids = sorted(entry["defect_ids_after_grading"])
    return {real: "D%d" % (n + 1) for n, real in enumerate(ids)}


def publish(derived: dict, ruling_docs: list, frozen: dict, known_cues: list) -> dict:
    targets = {}
    cues = []
    for target_ref, entry in sorted(derived["targets"].items()):
        mask = public_defect_ids(entry)
        packets = []
        for packet in entry["packets"]:
            public = dict(packet)
            public["recovered_defect_ids"] = sorted(mask[d] for d in packet["recovered_defect_ids"])
            public["sufficient_fix_defect_ids"] = sorted(mask[d] for d in
                                                         packet["sufficient_fix_defect_ids"])
            public["partial_fix_defect_ids"] = sorted(mask[d] for d in packet["partial_fix_defect_ids"])
            packets.append(public)
        targets[target_ref] = {
            "register_status": entry["register_status"],
            "defect_count_v1": len(entry["register_defect_ids"]),
            "confirmed_truth_revisions": len(entry["confirmed_truth_revisions"]),
            "truth_version_after_grading": entry["truth_version_after_grading"],
            "defect_count_after_grading": len(entry["defect_ids_after_grading"]),
            "status_after_grading": entry["status_after_grading"],
            "public_defect_ids": sorted(mask.values()),
            "packets": packets,
            "outstanding_count": len(entry["outstanding"]),
            "raw_items_total": sum(p["raw_items"] for p in packets),
            "raw_finding_items_total": sum(p["raw_finding_items"] for p in packets),
            "raw_false_finding_items_total": sum(p["raw_false_finding_items"] for p in packets),
            "unique_false_claims_total": sum(p["unique_false_claims"] for p in packets),
        }
    for doc in ruling_docs:
        for packet in doc.get("packets") or []:
            for cue in packet.get("unmasking_cues") or []:
                cues.append({"packet_id": packet["packet_id"], "source": "adjudicator",
                             "cue": "recorded in the sealed ruling table"})
    for cue in known_cues:
        cues.append({"packet_id": None, "source": "coordinator", "cue": cue})
    payload = {
        "artifact_id": "issue-152-rulings-public",
        "published_at": now(),
        "schema_version": "bounded-discovery-v1",
        "blinding": "label masking, not guaranteed blinding; every cue is listed, none is "
                    "resolved, and the arm mapping stays sealed until #153 opens it",
        "targets": targets,
        "unmasking_cues": cues,
        "note": "Counts only. Paths, symbols, quotes and citations are in the sealed ruling "
                "tables. Defect IDs are renumbered per target so that a register's own "
                "lettering names nothing.",
    }
    forbidden, allowed = disclosive_values(frozen)
    leaked = leak_scan(payload, forbidden, allowed)
    if leaked:
        raise Failed("\n".join(leaked))
    return payload


# --------------------------------------------------------------------------
# seal: the full tables under #148's key
# --------------------------------------------------------------------------

def seal(files: list, key, out_dir) -> dict:
    out = Path(os.path.expanduser(str(out_dir)))
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as scratch:
        archive = Path(scratch) / "rulings.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            for path in files:
                tar.add(os.path.expanduser(str(path)), arcname=os.path.basename(str(path)))
        plaintext_sha = sha256_file(archive)
        cipher = out / "rulings.tar.gz.enc"
        run = subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "200000",
                              "-salt", "-pass", "file:" + os.path.expanduser(str(key)),
                              "-in", str(archive), "-out", str(cipher)],
                             capture_output=True, text=True, encoding="utf-8")
        if run.returncode:
            sys.stderr.write("openssl enc failed: %s\n" % run.stderr[:400])
            raise SystemExit(2)
    record = {
        "artifact_id": "issue-152-rulings-seal",
        "cipher": "openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt, under #148's key",
        "ciphertext_bytes": cipher.stat().st_size,
        "ciphertext_sha256": sha256_file(cipher),
        "files_sealed": {os.path.basename(str(p)): sha256_file(p) for p in files},
        "plaintext_sha256": plaintext_sha,
        "schema_version": "bounded-discovery-v1",
        "sealed_at": now(),
        "why_sealed": "the ruling tables quote the packets' paths, symbols and citations, which "
                      "name the targets; the public summary carries counts only",
    }
    (out / "SHA256SUMS").write_text("%s  rulings.tar.gz\n" % plaintext_sha, encoding="utf-8")
    write(out / "seal.json", record)
    return record


# --------------------------------------------------------------------------
# audit: what one adjudicator session ran at, and what it read
# --------------------------------------------------------------------------

SYNTHETIC_MODEL = "<synthetic>"
PATH_TOKEN = re.compile(r"(?<![\w.-])(/[\w.@+-]+(?:/[\w.@+-]+)*)")


def paths_in_tool_use(block: dict) -> list:
    """Every path a tool call names: file tools by argument, shell by token."""
    name = block.get("name")
    args = block.get("input") or {}
    found = []
    if name in ("Read", "Write", "Edit", "Glob", "Grep"):
        for key in ("file_path", "path"):
            if args.get(key):
                found.append(str(args[key]))
    elif name == "Bash":
        found.extend(PATH_TOKEN.findall(str(args.get("command", ""))))
    return found


def audit(transcript, roots: list, labels: list = ()) -> dict:
    labels = list(labels) or ["root-%d" % (n + 1) for n in range(len(roots))]
    if len(labels) != len(roots):
        raise Failed("one label per root is required")
    roots = [os.path.realpath(os.path.expanduser(r)) for r in roots]
    models, efforts = {}, {}
    assistant = root_user = summaries = synthetic = 0
    tool_calls = {}
    inside, outside = set(), set()
    with open(os.path.expanduser(str(transcript)), encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            kind = record.get("type")
            if kind == "user" and record.get("parentUuid") in (None, "None"):
                root_user += 1
            elif kind in ("summary", "compact-boundary"):
                summaries += 1
            elif kind == "assistant":
                message = record.get("message") or {}
                if message.get("model") == SYNTHETIC_MODEL or record.get("isApiErrorMessage"):
                    synthetic += 1
                    continue
                assistant += 1
                models[message.get("model")] = models.get(message.get("model"), 0) + 1
                effort = message.get("effort") or record.get("effort")
                efforts[effort] = efforts.get(effort, 0) + 1
                for block in message.get("content") or []:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_calls[block.get("name")] = tool_calls.get(block.get("name"), 0) + 1
                        for path in paths_in_tool_use(block):
                            if path.startswith("/dev/"):
                                # A redirect to the null device reads nothing.
                                continue
                            real = os.path.realpath(os.path.expanduser(path))
                            if any(real == r or real.startswith(r + os.sep) for r in roots):
                                inside.add(path)
                            elif os.path.exists(real):
                                outside.add(path)
                            else:
                                # A path that does not exist on this machine
                                # (a clone-relative citation, a placeholder in a
                                # quoted command) reads nothing.
                                inside.add(path)
    return {"transcript": os.path.basename(str(transcript)), "assistant_lines": assistant,
            "synthetic_error_lines": synthetic, "models": models, "efforts": efforts,
            "fresh_context": root_user == 1 and summaries == 0,
            "root_user_messages": root_user, "summary_records": summaries,
            "tool_calls": tool_calls, "permitted_roots": labels,
            "permitted_roots_note": "labels, not paths: a clone directory is named after its "
                                    "target and this record is public",
            "paths_named": len(inside | outside),
            "paths_outside_permitted_roots": sorted(outside),
            "read_outside_permitted_roots": bool(outside)}


# --------------------------------------------------------------------------
# meter: the transcript at frozen rates against the runtime's self-report
# --------------------------------------------------------------------------

def meter(transcript, envelopes: list, rates: dict, tools_dir) -> dict:
    scan = audit(transcript, [])
    models = [m for m in scan["models"] if m]
    if len(models) != 1:
        raise Failed("the transcript carries %d model(s); one is expected" % len(models))
    model = models[0]
    card = (rates.get("models") or {}).get(model)
    if not card:
        raise Failed("no frozen rate for %s" % model)
    helper = Path(os.path.expanduser(str(tools_dir))) / "transcript_usage.py"
    command = [sys.executable, str(helper), os.path.expanduser(str(transcript)),
               "--prices", "%s,%s" % (card["input_usd_per_mtok"], card["output_usd_per_mtok"]),
               "--cache-write-mult", card.get("cache_write_5m_mult", "1.25"),
               "--cache-write-1h-mult", card.get("cache_write_1h_mult", "2.0"),
               "--cache-read-mult", card.get("cache_read_mult", "0.1"), "--json"]
    run = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if run.returncode:
        sys.stderr.write("transcript_usage.py failed: %s\n" % run.stderr[:400])
        raise SystemExit(2)
    usage = json.loads(run.stdout)
    total = usage.get("total") or usage
    from decimal import Decimal
    transcript_usd = Decimal(str(total["cost"]))
    envs = [load(e) for e in envelopes]
    # The runtime reports a binary float; the ledger settles to seven places.
    cent7 = Decimal("0.0000001")
    self_report = sum((Decimal(str(e.get("total_cost_usd", "0"))).quantize(cent7) for e in envs),
                      Decimal("0"))
    charged = max(transcript_usd, self_report)
    return {"model": model, "rates": card, "transcript_usd": str(transcript_usd),
            "self_report_usd": str(self_report), "charged_usd": str(charged),
            "difference_usd": str(self_report - transcript_usd),
            "charged_from": "self-report" if self_report >= transcript_usd else "transcript",
            "segments": len(envs),
            "envelopes": [{k: e.get(k) for k in ("subtype", "is_error", "duration_ms",
                                                  "num_turns", "total_cost_usd", "modelUsage")}
                          for e in envs],
            "transcript_usage": usage,
            "helper": os.path.basename(str(helper)), "helper_prices": command[3:]}


# --------------------------------------------------------------------------
# handoff: the stage record #153 reads
# --------------------------------------------------------------------------

def handoff(public: dict, freeze_record: dict, seal_record: dict, derived: dict,
            metering: list, audits: list, frozen: dict) -> dict:
    from decimal import Decimal
    charged = sum((Decimal(m["charged_usd"]) for m in metering), Decimal("0"))
    targets = {}
    outstanding = 0
    for target_ref, entry in sorted(derived["targets"].items()):
        outstanding += len(entry["outstanding"])
        targets[target_ref] = {
            "packets_ruled": len(entry["packets"]),
            "packets_outstanding": len(entry["outstanding"]),
            "raw_items": sum(p["raw_items"] for p in entry["packets"]),
            "truth_version_graded": entry["truth_version_graded"],
            "truth_version_after_grading": entry["truth_version_after_grading"],
            "confirmed_truth_revisions": len(entry["confirmed_truth_revisions"]),
            "status_after_grading": entry["status_after_grading"],
        }
    fidelity = [{"transcript": a["transcript"], "models": a["models"], "efforts": a["efforts"],
                 "fresh_context": a["fresh_context"],
                 "read_outside_permitted_roots": a["read_outside_permitted_roots"]}
                for a in audits]
    complete = outstanding == 0
    record = {
        "artifact_id": "issue-152-grading-handoff",
        "schema_version": "bounded-discovery-v1",
        "stage": "grading",
        "created_at": now(),
        "disposition": "grading-delivered" if complete else "grading-delivered-partial",
        "experiment_disposition": "stopped-incomplete",
        "dispatch_authorized": False,
        "dispatch_hold": "held. Grading launched no reviewer run and authorises none; the "
                         "eighteen unattempted cells stay unattempted.",
        "rulings": {
            "frozen_at": freeze_record["frozen_at"],
            "combined_sha256": freeze_record["combined_sha256"],
            "files": freeze_record["files"],
            "sealed": True,
            "ciphertext_sha256": seal_record["ciphertext_sha256"],
            "plaintext_sha256": seal_record["plaintext_sha256"],
            "public_summary": "rulings-public.json",
            "redaction_map_opened": False,
            "arm_mapping_seen_by_adjudicator": False,
        },
        "targets": targets,
        "packets_ruled": sum(t["packets_ruled"] for t in targets.values()),
        "packets_outstanding": outstanding,
        "no_packet_attempts": 2,
        "adjudicator_fidelity": fidelity,
        "grading_cost": {
            "sessions": len(metering),
            "charged_usd": str(charged),
            "per_session": [{"target_ref": m.get("target_ref"), "charged_usd": m["charged_usd"],
                             "charged_from": m["charged_from"],
                             "self_report_usd": m["self_report_usd"],
                             "transcript_usd": m["transcript_usd"]} for m in metering],
        },
        "unmasking_cues": public.get("unmasking_cues"),
        "blinding": public.get("blinding"),
        "claims_note": "No quality, recall or cost comparison appears here. No arm is named, "
                       "no arm is described as better or worse, and no validity, completion or "
                       "cost label was joined to any ruling. The scorer's per-attempt fields are "
                       "derived without arm, validity or cost; #153 joins those.",
        "next_stage": {
            "tickets": [153],
            "work": "#153 verifies the freeze against the sealed tables, opens the redaction map, "
                    "joins arm, replicate, completion and cost from it and operational validity "
                    "from the closeout's fidelity assessment to the derived per-attempt fields, "
                    "runs the frozen scorer, and records reject or inconclusive.",
            "must_not": [
                "dispatch any reviewer run from this handoff",
                "alter a frozen ruling; a disagreement is recorded beside the table, not inside it",
                "treat an unresolved attempt as a valid completed outcome",
                "treat a sub-threshold or unresolved item as a recovery",
                "read the count of packets that recovered a defect as a comparison before the "
                "arm mapping is joined",
            ],
        },
    }
    forbidden, allowed = disclosive_values(frozen)
    leaked = leak_scan(record, forbidden, allowed)
    if leaked:
        raise Failed("\n".join(leaked))
    return record


# --------------------------------------------------------------------------
# self-test: the scoring mapping on synthetic cases
# --------------------------------------------------------------------------

def item(ref, kind="finding", defect="supported", consequence="supported", materiality="material",
         concept="GT-x1", fix="sufficient", action=False, priority=False):
    ruling = expected_ruling(defect, consequence)
    if ruling != "supported":
        materiality = "not-applicable"
    if not (ruling == "supported" and materiality == "material"):
        fix = "not-applicable"
    return {"item_ref": ref, "structured_item_id": None, "kind": kind, "anchor": "a:1",
            "quote": ref, "asserted_defect": "x", "asserted_consequence": "y",
            "defect_supported": defect, "consequence_supported": consequence, "ruling": ruling,
            "materiality": materiality, "concept": concept, "requested_fix": fix,
            "priority_error": priority, "priority_note": "", "action_error": action,
            "action_note": "", "citations": ["a:1"], "basis": "synthetic"}


def self_test() -> int:
    failures = []

    def check(name, condition):
        if not condition:
            failures.append(name)

    register = {"GT-x1"}
    base = {"packet_id": "p", "status": "Changes Requested", "explicit_clean_claim": False,
            "honest_incomplete": False, "safety_claims": [], "unmasking_cues": []}

    # 1. A supported duplicate pair: two raw items, one recovered concept.
    dup = dict(base, items=[item("p/r1"), item("p/r2")])
    d = derive_packet(dup, register, set())
    check("supported duplicate pair counts two raw items", d["raw_supported_material_items"] == 2)
    check("supported duplicate pair recovers one concept", d["recovered_defect_ids"] == ["GT-x1"])
    check("supported duplicate pair credits one sufficient fix",
          d["sufficient_fix_defect_ids"] == ["GT-x1"])
    check("supported duplicate pair has no false items", d["raw_false_finding_items"] == 0)

    # 2. A false duplicate pair: two raw false items, one false concept.
    fdup = dict(base, items=[item("p/r1", defect="false", concept="F1", action=True),
                             item("p/r2", defect="false", concept="F1", action=True)])
    d = derive_packet(fdup, register, set())
    check("false duplicate pair counts two raw false items", d["raw_false_finding_items"] == 2)
    check("false duplicate pair counts one false concept", d["unique_false_claims"] == 1)
    check("false duplicate pair recovers nothing", d["recovered_defect_ids"] == [])
    check("false duplicate pair carries its action errors", d["action_errors"] == 2)

    # 3. A true fact with an invented impact is false, and recovers nothing.
    invented = dict(base, items=[item("p/r1", defect="supported", consequence="false",
                                      concept="F2")])
    d = derive_packet(invented, register, set())
    check("true fact plus invented impact is a false finding", d["raw_false_finding_items"] == 1)
    check("true fact plus invented impact recovers nothing", d["recovered_defect_ids"] == [])
    check("the ruling follows from the consequence axis",
          expected_ruling("supported", "false") == "false")

    # 4. An insufficient fix recovers the concept and earns no sufficiency credit.
    partial = dict(base, items=[item("p/r1", fix="partial")])
    d = derive_packet(partial, register, set())
    check("partial fix recovers the concept", d["recovered_defect_ids"] == ["GT-x1"])
    check("partial fix earns no sufficiency credit", d["sufficient_fix_defect_ids"] == [])
    check("partial fix is reported as partial", d["partial_fix_defect_ids"] == ["GT-x1"])

    # 5. An unresolved claim is neither recovered nor false.
    unresolved = dict(base, items=[item("p/r1", defect="unresolved", concept="U1")])
    d = derive_packet(unresolved, register, set())
    check("unresolved claim is counted as unresolved", d["unresolved_adjudications"] == 1)
    check("unresolved claim is not false", d["raw_false_finding_items"] == 0)
    check("unresolved claim recovers nothing", d["recovered_defect_ids"] == [])

    # 5b. One item bundling two concepts recovers both, each fix judged alone.
    bundled_item = item("p/r1", fix="partial")
    bundled_item["additional_concepts"] = [{"concept": "GT-x2", "requested_fix": "sufficient",
                                            "basis": "synthetic"}]
    bundled = dict(base, items=[bundled_item])
    d = derive_packet(bundled, {"GT-x1", "GT-x2"}, set())
    check("bundled item recovers both concepts", d["recovered_defect_ids"] == ["GT-x1", "GT-x2"])
    check("bundled item credits only the sufficient fix", d["sufficient_fix_defect_ids"] == ["GT-x2"])
    check("bundled item reports the partial one", d["partial_fix_defect_ids"] == ["GT-x1"])
    check("bundled item is counted once as raw", d["raw_supported_material_items"] == 1)

    # 5c. A confirmed revision is truth; a revision marked unresolved is not.
    doc_rev = {"proposed_truth_revisions": [{"proposed_id": "GT-x9"},
                                            {"proposed_id": "GT-x8", "status": "unresolved"}]}
    check("revision without a status is confirmed", confirmed_revisions(doc_rev) == {"GT-x9"})

    # 6. Approved is a clean claim whatever the body says; recovery never cancels it.
    approved = dict(base, status="Approved", explicit_clean_claim=True, items=[item("p/r1")])
    d = derive_packet(approved, register, set())
    check("Approved with a recovery still claims clean", d["clean_claim"] is True
          and d["recovered_defect_ids"] == ["GT-x1"])

    # 7. A false observation is not a false finding, and is reported apart.
    obs = dict(base, items=[item("p/r1", kind="observation", defect="false", concept="F3")])
    d = derive_packet(obs, register, set())
    check("false observation is not a raw false finding", d["raw_false_finding_items"] == 0)
    check("false observation is reported apart", d["raw_false_non_finding_items"] == 1)

    # 8. A supported material item on a concept that is not truth cannot be recovered
    #    and validate refuses it.
    packets = {"target_ref": "<target-T>", "packets": [{"packet_id": "p", "status":
                                                         "Changes Requested"}]}
    doc = {"target_ref": "<target-T>", "register_status": "buggy",
           "register_defect_ids": ["GT-x1"],
           "concepts": {"GT-x1": {"description": "d", "source": "register"},
                        "F1": {"description": "d", "source": "adjudicator"}},
           "proposed_truth_revisions": [], "outstanding": [],
           "packets": [dict(base, items=[item("p/r1", concept="F1")])]}
    problems = validate(doc, packets)
    check("validate refuses a material recovery outside truth",
          any("neither a register defect" in p for p in problems))

    # 9. validate accepts a consistent document and refuses an inconsistent ruling.
    good = dict(doc, packets=[dict(base, items=[item("p/r1")])])
    check("validate accepts a consistent table", validate(good, packets) == [])
    bad_item = item("p/r1", defect="false", concept="F1")
    bad_item["ruling"] = "supported"
    bad = dict(doc, packets=[dict(base, items=[bad_item])])
    check("validate refuses a ruling that contradicts its axes",
          any("does not follow" in p for p in validate(bad, packets)))
    missing = dict(doc, packets=[])
    check("validate refuses a packet with no rulings that is not outstanding",
          any("no rulings" in p for p in validate(missing, packets)))
    listed = dict(doc, packets=[], outstanding=["p"])
    check("validate accepts a packet listed as outstanding",
          not any("no rulings" in p for p in validate(listed, packets)))

    # 10. The public scan refuses a path, a slot name and an unknown object id.
    frozen = {"targets": {"slot-9": {"target": {"repository": "acme/widget", "pr": 7,
                                                "head_oid": "d" * 40}}}}
    forbidden, allowed = disclosive_values(frozen)
    check("scan refuses a slot name", leak_scan({"a": "slot-9"}, forbidden, allowed))
    check("scan refuses a repository component", leak_scan({"a": "widget"}, forbidden, allowed))
    check("scan refuses a source path", leak_scan({"a": "src/main.rs"}, forbidden, allowed))
    check("scan refuses a foreign slash path", leak_scan({"a": "pkg/util/notes.md"}, forbidden, allowed))
    check("scan passes this bundle's own paths",
          not leak_scan({"a": "metering/target-A/usage.json docs/research/x/manifest.json handoff.json"},
                        forbidden, allowed))
    check("scan refuses an object id", leak_scan({"a": "e" * 40}, forbidden, allowed))
    check("scan passes counts", not leak_scan({"a": 3, "b": "<target-A>"}, forbidden, allowed))

    # 11. render refuses an unfilled placeholder.
    try:
        render("x {A} {B}", {"A": 1})
        check("render refuses an unfilled placeholder", False)
    except Failed:
        pass
    check("render fills every placeholder", render("x {A}", {"A": 1}) == "x 1")

    for name in failures:
        print("FAIL " + name)
    print("self-test: %d checks, %d failures" % (40, len(failures)))
    return 1 if failures else 0


# --------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("split")
    p.add_argument("--packets", required=True)
    p.add_argument("--out-dir", required=True)

    p = sub.add_parser("render")
    p.add_argument("--template", required=True)
    for name in ("target-ref", "packets", "register", "clone", "base-branch", "work", "out",
                 "exec-note", "budget", "out-prompt"):
        p.add_argument("--" + name, required=True)

    p = sub.add_parser("validate")
    p.add_argument("--rulings", required=True)
    p.add_argument("--packets", required=True)

    p = sub.add_parser("derive")
    p.add_argument("--rulings", nargs="+", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("freeze")
    p.add_argument("--rulings", nargs="+", required=True)
    p.add_argument("--derived", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--check", action="store_true")

    p = sub.add_parser("publish")
    p.add_argument("--derived", required=True)
    p.add_argument("--rulings", nargs="+", required=True)
    p.add_argument("--frozen", required=True)
    p.add_argument("--known-cue", action="append", default=[])
    p.add_argument("--out", required=True)

    p = sub.add_parser("seal")
    p.add_argument("--key", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("files", nargs="+")

    p = sub.add_parser("audit")
    p.add_argument("--transcript", required=True)
    p.add_argument("--root", action="append", default=[])
    p.add_argument("--root-label", action="append", default=[])
    p.add_argument("--out", required=True)

    p = sub.add_parser("meter")
    p.add_argument("--transcript", required=True)
    p.add_argument("--label", default=None)
    p.add_argument("--envelope", nargs="+", required=True)
    p.add_argument("--rates", required=True)
    p.add_argument("--tools", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("scan")
    p.add_argument("--frozen", required=True)
    p.add_argument("files", nargs="+")

    p = sub.add_parser("handoff")
    for name in ("public", "freeze", "seal", "derived", "frozen", "out"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--metering", nargs="+", required=True)
    p.add_argument("--audit", nargs="+", required=True)

    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    try:
        if args.command == "split":
            packets = load(args.packets)
            written = split(packets, args.out_dir)
            digest = sha256_file(args.packets)
            for path in written.values():
                doc = load(path)
                doc["source_packets_sha256"] = digest
                write(path, doc)
            for target_ref, path in sorted(written.items()):
                print("%s -> %s" % (target_ref, path))
        elif args.command == "render":
            template = Path(os.path.expanduser(args.template)).read_text(encoding="utf-8")
            values = {"TARGET_REF": args.target_ref, "PACKETS": args.packets,
                      "REGISTER": args.register, "CLONE": args.clone,
                      "BASE_BRANCH": args.base_branch, "WORK": args.work, "OUT": args.out,
                      "EXEC_NOTE": args.exec_note, "BUDGET": args.budget}
            text = render(template, values)
            target = Path(os.path.expanduser(args.out_prompt))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            print("%s sha256 %s" % (args.out_prompt, sha256_file(target)))
        elif args.command == "validate":
            problems = validate(load(args.rulings), load(args.packets))
            for problem in problems:
                print(problem)
            return 1 if problems else 0
        elif args.command == "derive":
            write(args.out, derive(args.rulings))
            print("wrote " + args.out)
        elif args.command == "freeze":
            if args.check:
                problems = check_freeze(load(args.out), args.rulings, args.derived)
                for problem in problems:
                    print(problem)
                if not problems:
                    print("freeze holds: every file hashes to its frozen digest")
                return 1 if problems else 0
            write(args.out, freeze(args.rulings, args.derived))
            print("wrote " + args.out)
        elif args.command == "publish":
            payload = publish(load(args.derived), [load(p) for p in args.rulings],
                              load(args.frozen), args.known_cue)
            write(args.out, payload)
            print("wrote " + args.out)
        elif args.command == "seal":
            record = seal(args.files, args.key, args.out_dir)
            print("sealed %d file(s), plaintext %s" % (len(record["files_sealed"]),
                                                       record["plaintext_sha256"]))
        elif args.command == "audit":
            record = audit(args.transcript, args.root, args.root_label)
            write(args.out, record)
            print("%s: %d assistant lines, models %s, efforts %s, fresh=%s, outside=%d"
                  % (record["transcript"], record["assistant_lines"], record["models"],
                     record["efforts"], record["fresh_context"],
                     len(record["paths_outside_permitted_roots"])))
            for path in record["paths_outside_permitted_roots"]:
                print("read outside the permitted roots: " + path)
            return 1 if record["read_outside_permitted_roots"] else 0
        elif args.command == "meter":
            record = meter(args.transcript, args.envelope, load(args.rates), args.tools)
            record["target_ref"] = args.label
            write(args.out, record)
            print("transcript %s, self-report %s, charged %s (%s)"
                  % (record["transcript_usd"], record["self_report_usd"],
                     record["charged_usd"], record["charged_from"]))
        elif args.command == "scan":
            forbidden, allowed = disclosive_values(load(args.frozen))
            problems = []
            for path in args.files:
                text = Path(os.path.expanduser(path)).read_text(encoding="utf-8")
                for line in leak_scan({"text": text}, forbidden, allowed):
                    problems.append("%s: %s" % (path, line))
            for problem in problems:
                print(problem)
            if not problems:
                print("scan: %d file(s) carry no disclosive value" % len(args.files))
            return 1 if problems else 0
        elif args.command == "handoff":
            record = handoff(load(args.public), load(args.freeze), load(args.seal),
                             load(args.derived), [load(m) for m in args.metering],
                             [load(a) for a in args.audit], load(args.frozen))
            write(args.out, record)
            print("wrote %s: %s" % (args.out, record["disposition"]))
        else:
            parser.print_help()
            return 2
    except Failed as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
