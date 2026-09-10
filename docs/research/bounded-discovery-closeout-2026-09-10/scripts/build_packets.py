#!/usr/bin/env python3
"""Build #152's anonymous grading packets from the sealed pilot evidence.

One packet per attempt that produced claims, plus a manifest of the attempts
that produced none. The grader has to be able to judge every claim on its own
prose, and must not be able to tell which arm produced it.

What a packet keeps, verbatim: the published status, the whole review body, and
every finding and observation with its trigger, claimed consequence, remedy and
decisive evidence. What it drops: the position, the arm, the worker model, the
replicate, the operational validity, the completion and the cost - the mapping
#152 must not see while it is forming rulings.

What it masks: every value that names a target - the repository, its url, its
pull request, and each object id including the abbreviations the prose uses.
Masks are sequential tokens assigned in traversal order and recorded in a
redaction map, never digests: a hash over a four-candidate secret is that
secret, and this bundle's own review proved it by inverting four such hashes.

The packets are sealed, not published in the clear. Masking hides the arm; it
cannot hide the target, because the prose has to keep file paths and symbol
names for the grading to mean anything, and naming which two slots the pilot
ran on would disclose which slot holds the clean control. This is label
masking, not guaranteed blinding: a packet's style may still suggest an arm.

Usage::

    build_packets.py --evidence DIR --frozen manifest.json --out-dir DIR \\
        [--seed N]
    build_packets.py --self-test

Exit: 0 on success, 1 on a content violation with one line per violation on
stdout, 2 when an input cannot be read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Fields that would tell the grader which arm produced a packet. None of them
# reaches a packet; every one is recorded in the sealed redaction map instead.
WITHHELD_FROM_GRADER = ("position", "arm", "worker_model", "replicate",
                        "operational_validity", "completion", "settled_usd",
                        "elapsed_seconds", "attempt_ref")

STATUS_VALUES = ("Approved", "Changes Requested", "Comment", "Request Changes")


def load(path, default=None):
    try:
        return json.loads(Path(os.path.expanduser(str(path))).read_text(encoding="utf-8"))
    except FileNotFoundError:
        if default is not None:
            return default
        sys.stderr.write("missing %s\n" % path)
        raise SystemExit(2)
    except (OSError, ValueError) as exc:
        sys.stderr.write("cannot read %s: %s\n" % (path, exc))
        raise SystemExit(2)


def write(path, payload) -> None:
    target = Path(os.path.expanduser(str(path)))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Masker:
    """Replaces every target-identifying value with a sequential token.

    Object ids are masked at every length the prose uses, longest first, so that
    replacing the full id cannot leave a seven-character abbreviation of it
    behind - which would still identify the target."""

    def __init__(self, frozen, rng=None):
        self.map = {}
        self.counters = {}
        self.rules = []
        slots = sorted(((frozen or {}).get("targets") or {}).items())
        if rng is not None:
            # Tokens are numbered in the order the slots are visited, so the
            # order is randomised: `<repository-01>` must not mean "the
            # lowest-numbered slot" to anyone who later opens the packets.
            rng.shuffle(slots)
        for slot, entry in slots:
            target = (entry or {}).get("target") or {}
            repository = target.get("repository")
            if target.get("url"):
                self._rule(str(target["url"]), "url")
            if repository:
                self._rule(str(repository), "repository")
                if target.get("pr"):
                    self._rule("%s#%s" % (repository, target["pr"]), "issue")
            for key in ("head_oid", "base_oid_recorded", "merge_base_oid"):
                if target.get(key):
                    self._rule(str(target[key]), "commit")
            self._rule(slot, "slot")
        # Longest first: a full object id must be replaced before its prefix.
        self.rules.sort(key=lambda rule: len(rule[0]), reverse=True)

    def _token(self, kind) -> str:
        self.counters[kind] = self.counters.get(kind, 0) + 1
        return "<%s-%02d>" % (kind, self.counters[kind])

    def _rule(self, raw, kind) -> None:
        if raw in self.map:
            return
        token = self._token(kind)
        self.map[raw] = token
        self.rules.append((raw, token))
        if kind == "commit" and len(raw) == 40:
            # The prose abbreviates object ids; every abbreviation of a masked
            # id is masked to the same token, so no prefix survives.
            for length in range(12, 6, -1):
                prefix = raw[:length]
                if prefix not in self.map:
                    self.map[prefix] = token
                    self.rules.append((prefix, token))

    def mask(self, text):
        if not isinstance(text, str):
            return text
        for raw, token in self.rules:
            text = text.replace(raw, token)
        return text

    def redaction_map(self) -> dict:
        """Raw value to mask, for #153 to restore at reveal.

        Sealed with the packets: it is the inverse of the blind."""
        return {"masks": {raw: token for raw, token in sorted(self.map.items())},
                "note": ("sequential tokens assigned in traversal order, never digests: a hash "
                         "over an enumerable secret is a lookup table for it")}


def status_of(body) -> str:
    """The published status, from the payload's first line.

    Validated against the output contract's four values so a typo cannot
    quietly become a status the screen does not know."""
    first = (body or "").strip().splitlines()[0] if (body or "").strip() else ""
    match = re.match(r"\*\*([^*]+?)(?:\s*\(advisory\))?\*\*", first.strip())
    candidate = (match.group(1).strip() if match else "")
    return candidate if candidate in STATUS_VALUES else "unrecognised"


def payload_of(root: Path) -> dict:
    """An attempt's published review, from whichever form it wrote.

    Some attempts wrote structured items beside the body and some wrote the
    body alone. The body is carried whole in both cases, so no visible finding
    prose can be lost to a parser that did not recognise a section."""
    structured = root / "work" / "review-payload.json"
    markdown = root / "work" / "review-payload.md"
    if structured.is_file():
        payload = load(structured, default={})
        return {"body": (payload.get("summary") or {}).get("body", ""),
                "items": payload.get("items") or [], "source": "review-payload.json"}
    if markdown.is_file():
        return {"body": markdown.read_text(encoding="utf-8"), "items": [],
                "source": "review-payload.md"}
    return {}


def attempt_dirs(evidence: Path) -> list:
    """Every attempt in the seal that could have produced claims."""
    found = []
    for entry in sorted(evidence.glob("position-*")):
        if entry.is_dir():
            found.append(entry)
    for entry in sorted((evidence / "invalid").glob("position-*")):
        if entry.is_dir() and not entry.name.endswith("-home"):
            found.append(entry)
    return found


def build(evidence: Path, frozen, seed=None) -> dict:
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    masker = Masker(frozen, rng)
    packets, no_packet, mapping = [], [], []

    for root in attempt_dirs(evidence):
        settle = load(root / "artifacts" / "settle.json", default={})
        aborted = sorted(root.glob("artifacts/attempt-*-aborted-dispatch.json"))
        attempt_id = settle.get("attempt_id") or ""
        ordinal = 1
        if "-attempt-" in attempt_id:
            try:
                ordinal = int(attempt_id.rsplit("-attempt-", 1)[-1])
            except ValueError:
                ordinal = 1
        position = int(settle.get("position") or root.name.split("-")[1])
        reference = "position-%02d-attempt-%d" % (position, ordinal)

        for record in aborted:
            number = int(record.name.split("-")[1])
            no_packet.append({
                "attempt_ref": "position-%02d-attempt-%d" % (position, number),
                "why": "the launch was refused before any model request, so the attempt made no "
                       "claim of any kind",
                "raw_final_claims": None,
            })

        payload = payload_of(root)
        if not payload or not (payload.get("body") or "").strip():
            no_packet.append({
                "attempt_ref": reference,
                "why": "the attempt ended before it published a review, so it left no final "
                       "claim to grade",
                "raw_final_claims": None,
            })
            continue

        packet_id = str(uuid_from(rng))
        target_key = settle.get("target_slot") or "unknown"
        items = []
        for item in payload["items"]:
            items.append({"item_id": str(uuid_from(rng)),
                          "kind": item.get("type") or "finding",
                          "markdown": masker.mask(item.get("markdown") or "")})
        body = masker.mask(payload["body"])
        packets.append({
            "packet_id": packet_id,
            "target_ref": target_key,          # replaced with a mask below
            "status": status_of(payload["body"]),
            "body_markdown": body,
            "items": items,
        })
        mapping.append({
            "packet_id": packet_id,
            "attempt_ref": reference,
            "item_count": len(items),
            "source_form": payload["source"],
            "position": position,
            "arm": settle.get("arm"),
            "worker_model": settle.get("worker_model"),
            "replicate": settle.get("replicate", 1),
            "completion": settle.get("completion"),
            "settled_usd": settle.get("settled_usd"),
            "target_slot": settle.get("target_slot"),
            "raw_payload_sha256": hashlib.sha256(
                payload["body"].encode("utf-8")).hexdigest(),
            "masked_packet_sha256": None,      # filled once the packet is final
            "item_ids": [item["item_id"] for item in items],
        })

    # The target has to survive masking so the grader can score a claim against
    # the right adjudicated truth, but it must not survive as a name.
    target_tokens = {}
    for packet in packets:
        raw = packet["target_ref"]
        if raw not in target_tokens:
            target_tokens[raw] = "<target-%s>" % chr(ord("A") + len(target_tokens))
        packet["target_ref"] = target_tokens[raw]
    for raw, token in target_tokens.items():
        masker.map.setdefault(raw, token)

    # Emission order carries no positional information.
    rng.shuffle(packets)
    for packet in packets:
        digest = hashlib.sha256(json.dumps(packet, sort_keys=True).encode("utf-8")).hexdigest()
        for row in mapping:
            if row["packet_id"] == packet["packet_id"]:
                row["masked_packet_sha256"] = digest

    return {
        "packets": packets,
        "no_packet": sorted(no_packet, key=lambda row: row["attempt_ref"]),
        "redaction_map": dict(masker.redaction_map(), target_masks=target_tokens),
        "mapping": sorted(mapping, key=lambda row: row["attempt_ref"]),
    }


def uuid_from(rng):
    import uuid
    return uuid.UUID(int=rng.getrandbits(128), version=4)


def grader_view(built) -> dict:
    """Exactly what #152 receives. Nothing else may be in this file."""
    return {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-151-grading-packets",
        "built_at": now(),
        "packet_count": len(built["packets"]),
        "instructions": (
            "Grade each packet on its own prose. Every visible claim the attempt published is "
            "in `body_markdown`; `items` indexes the ones the attempt also published "
            "structurally, and is empty where it did not. Packets are shuffled and carry no "
            "position, arm, model, replicate, validity, completion or cost; those live in the "
            "sealed mapping and must not be opened until rulings are frozen. Targets are masked "
            "to stable tokens so claims on one target can be scored together. Do not grade this "
            "closeout's own outcomes."),
        "blinding_limit": (
            "Label masking, not guaranteed blinding. The arm labels are removed and the target "
            "names are masked, but the prose keeps file paths, symbol names and the reviewer's "
            "style, and any of those may still suggest which arm wrote a packet. One structural "
            "tell is known and named rather than hidden: in this pilot only one arm published "
            "structured items beside its body, so whether `items` is populated correlates with "
            "that arm. Treat any such inference as a guess, and record rulings before opening "
            "the mapping."),
        "packets": built["packets"],
    }


def public_index(built) -> dict:
    """What may be committed in the clear beside the sealed packets."""
    return {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-151-packet-index",
        "built_at": now(),
        "packet_count": len(built["packets"]),
        "packets": sorted(({"packet_id": packet["packet_id"],
                            "masked_packet_sha256": hashlib.sha256(
                                json.dumps(packet, sort_keys=True).encode("utf-8")).hexdigest()}
                           for packet in built["packets"]),
                          key=lambda row: row["packet_id"]),
        "note": ("Packet ids are random and map to nothing published. The mapping from a packet "
                 "to its attempt, arm and target is sealed with the packets, and the raw payload "
                 "digests are sealed with it: a digest over the rendering of a four-candidate "
                 "secret is that secret."),
    }


def no_packet_manifest(built) -> dict:
    return {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-151-no-packet-manifest",
        "built_at": now(),
        "attempts": built["no_packet"],
        "note": ("An attempt with no packet still appears in the cell manifest and still carries "
                 "its cost. No output is fabricated for it, and neither invalid attempt left a "
                 "raw final claim to retain: one was refused before any model request, and the "
                 "other lost its primary to a provider error before it published."),
    }


def command_build(args) -> int:
    evidence = Path(os.path.expanduser(args.evidence))
    frozen = load(args.frozen)
    built = build(evidence, frozen, args.seed)

    violations = []
    grader = grader_view(built)
    text = json.dumps(grader)
    for field in WITHHELD_FROM_GRADER:
        if '"%s"' % field in text:
            violations.append("the grader view carries %r, which identifies the arm" % field)
    for raw in built["redaction_map"]["masks"]:
        if len(str(raw)) > 6 and str(raw) in text:
            violations.append("the grader view still contains the unmasked value %r" % raw[:24])
    if not built["packets"]:
        violations.append("no packet was built; the seal should hold at least one review payload")
    for line in violations:
        print(line)
    if violations:
        return 1

    out = Path(os.path.expanduser(args.out_dir))
    out.mkdir(parents=True, exist_ok=True)
    write(out / "grading-packets.json", grader)
    write(out / "redaction-map.json", dict(built["redaction_map"],
                                           mapping=built["mapping"],
                                           artifact_id="issue-151-redaction-map",
                                           note_for_153=("open only after #152 freezes its "
                                                         "rulings")))
    write(out / "no-packet-manifest.json", no_packet_manifest(built))
    write(out / "packet-index.json", public_index(built))
    print(json.dumps({"packets": len(built["packets"]),
                      "items": sum(len(p["items"]) for p in built["packets"]),
                      "no_packet": len(built["no_packet"])}))
    return 0


def self_test() -> int:
    import tempfile
    failures = []

    def check(name, condition):
        if not condition:
            failures.append(name)

    frozen = {"targets": {
        "slot-1": {"target": {"repository": "acme/widget", "url": "https://x/acme/widget/pull/7",
                              "pr": 7, "head_oid": "a" * 40, "merge_base_oid": "b" * 40}},
        "slot-2": {"target": {"repository": "acme/gadget", "pr": 9, "head_oid": "c" * 40}}}}

    masker = Masker(frozen, random.Random(11))
    masked = masker.mask("fixed in acme/widget at %s (short %s), see acme/widget#7"
                         % ("a" * 40, "a" * 7))
    check("a repository name is masked", "acme/widget" not in masked)
    check("a full object id is masked", "a" * 40 not in masked)
    check("an abbreviated object id is masked too", "a" * 7 not in masked)
    check("an abbreviation masks to the same token as its full id",
          masked.count(masker.map["a" * 40]) >= 2)
    check("the redaction map is tokens, not digests",
          all(not re.fullmatch(r"[0-9a-f]{64}", token)
              for token in masker.redaction_map()["masks"].values()))

    check("a contract status is recognised",
          status_of("**Changes Requested (advisory)** - 2 must-fix findings.")
          == "Changes Requested")
    check("an off-contract status is not invented",
          status_of("**Approvedd (advisory)** - 0 findings.") == "unrecognised")
    check("an empty body has no status", status_of("") == "unrecognised")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for position, arm, body, items in (
                (1, "A", "**Approved (advisory)** - 0 must-fix findings.\n\nseen in acme/widget",
                 None),
                (2, "B", "**Changes Requested (advisory)** - 1 must-fix finding.", [
                    {"type": "finding", "markdown": "**[P1] fix it** at %s" % ("a" * 40)}]),
        ):
            root = tmp / "evidence" / ("position-%02d" % position)
            (root / "artifacts").mkdir(parents=True)
            (root / "work").mkdir(parents=True)
            write(root / "artifacts" / "settle.json", {
                "attempt_id": "issue-138-slot-1-%s-replicate-1-attempt-1" % arm,
                "position": position, "arm": arm, "target_slot": "slot-1",
                "completion": "complete", "settled_usd": "1.00"})
            if items is None:
                (root / "work" / "review-payload.md").write_text(body, encoding="utf-8")
            else:
                write(root / "work" / "review-payload.json",
                      {"summary": {"body": body, "repository_url": "https://x/acme/widget"},
                       "items": items})
        empty = tmp / "evidence" / "position-03"
        (empty / "artifacts").mkdir(parents=True)
        (empty / "work").mkdir(parents=True)
        write(empty / "artifacts" / "settle.json", {
            "attempt_id": "issue-138-slot-1-C-replicate-1-attempt-1", "position": 3,
            "arm": "C", "target_slot": "slot-1"})

        built = build(tmp / "evidence", frozen, seed=7)
        check("one packet per attempt that published", len(built["packets"]) == 2)
        check("the grader view carries the whole published body",
              all(packet["body_markdown"].strip() for packet in built["packets"]))
        check("an attempt that published nothing gets a no-packet row",
              [row["attempt_ref"] for row in built["no_packet"]] == ["position-03-attempt-1"])
        check("finding prose is preserved", any(
            "fix it" in item["markdown"] for packet in built["packets"] for item in packet["items"]))
        check("packet ids are distinct and random-looking",
              len({packet["packet_id"] for packet in built["packets"]}) == 2)
        check("item ids are distinct from packet ids",
              not ({item["item_id"] for packet in built["packets"] for item in packet["items"]}
                   & {packet["packet_id"] for packet in built["packets"]}))
        check("the target survives as a mask, not as a name",
              all(packet["target_ref"].startswith("<target-") for packet in built["packets"]))
        check("both packets on one target share its mask",
              len({packet["target_ref"] for packet in built["packets"]}) == 1)

        grader = json.dumps(grader_view(built))
        for field in WITHHELD_FROM_GRADER:
            check("the grader view withholds %s" % field, '"%s"' % field not in grader)
        check("the grader view carries no repository name", "acme/widget" not in grader)
        check("the grader view carries no object id", "a" * 40 not in grader)
        check("the redaction map keeps the arm mapping",
              all(row.get("arm") for row in built["mapping"]))
        check("the redaction map keeps the raw payload digest",
              all(row.get("raw_payload_sha256") for row in built["mapping"]))
        check("the payload form and item count stay in the sealed mapping",
              all(row.get("source_form") for row in built["mapping"])
              and "source_form" not in json.dumps(grader_view(built)))
        check("the public index publishes no item count",
              all("item_count" not in row for row in public_index(built)["packets"]))
        class Reversing:
            @staticmethod
            def shuffle(items):
                items.reverse()

        check("mask token numbering follows the visiting order, which is randomised",
              Masker(frozen).map["acme/widget"] == "<repository-01>"
              and Masker(frozen, Reversing).map["acme/gadget"] == "<repository-01>")
        check("the public index publishes no raw digest",
              all("raw_payload_sha256" not in row for row in public_index(built)["packets"]))

        import subprocess
        out = tmp / "out"
        write(tmp / "frozen.json", frozen)
        done = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                               "--evidence", str(tmp / "evidence"),
                               "--frozen", str(tmp / "frozen.json"),
                               "--out-dir", str(out), "--seed", "3"],
                              capture_output=True, text=True, encoding="utf-8")
        check("the build command succeeds end to end", done.returncode == 0)
        check("the grader file, the map, the index and the no-packet manifest are written",
              all((out / name).is_file() for name in ("grading-packets.json",
                                                      "redaction-map.json",
                                                      "no-packet-manifest.json",
                                                      "packet-index.json")))

    for failure in failures:
        print("self-test failure: %s" % failure)
    print("%d checks, %d failures" % (32, len(failures)))
    return 1 if failures else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--evidence")
    parser.add_argument("--frozen")
    parser.add_argument("--out-dir")
    parser.add_argument("--seed", type=int,
                        help="deterministic ids for the self-test; omit for a real build")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not (args.evidence and args.frozen and args.out_dir):
        parser.print_help()
        return 2
    return command_build(args)


if __name__ == "__main__":
    raise SystemExit(main())
