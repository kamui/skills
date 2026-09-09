#!/usr/bin/env python3
"""Split one pilot cell's evidence into a public summary and a sealed archive.

The pilot runs on two slots chosen by a rule that is public - the adjudicated
clean slot and the lowest-numbered buggy slot, clean first - so naming the slots
a position ran on would disclose which slot holds the clean control. #148 sealed
that truth and #153 reveals it. This script is what keeps #150's own artifacts
from leaking it while still committing real evidence.

Two outputs per position:

**A public summary**, built from an explicit whitelist rather than by redacting a
full record. A whitelist is the safer direction for a blind: a field has to be
named here to become public, so a field nobody considered stays sealed by default.
Slot names, target repository and pull request, leak-set digests, object counts and
mirror refs are all absent from it - the first two obviously, the last three
because each of them identifies a repository just as precisely as its name does.

**A sealed archive** holding everything: the full per-cell artifacts, the rendered
prompts, the transcripts, the review payload and research report, arm C's freeze
and discovery files, and the reconciled ledger, whose frozen attempt IDs contain
slot names. Encrypted under #148's key with its plaintext digest recorded in the
clear, which is the same shape #149 used for the sealed schedule.

Every public string is also passed through a scrub of the known slot labels,
repositories and pull-request numbers, so a stderr tail or a problem message that
happens to quote one cannot carry it into the clear.

Usage::

    python3 archive_pilot.py --config pilot-config.json --out BUNDLE --key KEYFILE
    python3 archive_pilot.py --self-test

Exit: 0 on success, 1 on a content violation with one line per violation on
stdout, 2 when an input cannot be read or a helper fails, naming it on stderr.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


class Failed(Exception):
    """An input could not be read or a subprocess failed: exit 2."""


def load(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        if default is not None:
            return default
        raise Failed("missing %s" % path)
    except (OSError, ValueError) as exc:
        raise Failed("cannot read %s: %s" % (path, exc))


def write(path, document):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(document, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")


def secrets_from(targets) -> list:
    """Every token that would identify a slot: its label, repository and PR number."""
    tokens = set()
    for manifest in sorted(Path(targets).glob("slot-*/manifest.json")):
        document = load(manifest)
        target = document.get("target", {})
        tokens.add(document.get("label", ""))
        tokens.add(target.get("repository", ""))
        repository = target.get("repository", "")
        if repository:
            tokens.add(repository.split("/")[-1])
        if target.get("pr"):
            tokens.add(str(target["pr"]))
        tokens.add(document.get("slot", ""))
    return sorted((token for token in tokens if token and len(token) > 2), key=len,
                  reverse=True)


def scrub(value, secrets):
    """Replace every identifying token in a public string, recursively."""
    if isinstance(value, str):
        for secret in secrets:
            value = value.replace(secret, "<sealed>")
        return value
    if isinstance(value, list):
        return [scrub(item, secrets) for item in value]
    if isinstance(value, dict):
        return {scrub(key, secrets): scrub(item, secrets) for key, item in value.items()}
    return value


def checks_of(document) -> list:
    """Each check's name and verdict, with nothing that identifies a repository."""
    return [{"check": check.get("check"), "passed": check.get("passed")}
            for check in document.get("checks", [])]


def summarize(root, secrets) -> dict:
    """The public record of one position: process and fidelity, never identity."""
    prepared = load(root / "artifacts" / "prepare.json")
    dispatched = load(root / "artifacts" / "dispatch.json", {})
    settled = load(root / "artifacts" / "settle.json", {})
    attestation = load(root / "artifacts" / "attestation.json", {})
    pre = load(root / "artifacts" / "isolation-pre.json", {})
    post = load(root / "artifacts" / "isolation-post.json", {})
    mounts = load(root / "artifacts" / "mounts.json", {})
    prompts = load(root / "artifacts" / "prompts.json", {})
    usage = load(root / "artifacts" / "usage-split.json", {})
    effort = ""
    if (root / "artifacts" / "effort.txt").is_file():
        effort = (root / "artifacts" / "effort.txt").read_text(encoding="utf-8")

    summary = {
        "schema_version": "bounded-discovery-v1",
        "position": prepared["position"],
        "arm": prepared["arm"],
        "replicate": prepared["replicate"],
        "block": prepared["block"],
        "worker_model": prompts.get("worker_model"),
        # The ordinal alone is publishable; the full attempt ID names a slot.
        "attempt_ordinal": int(str(dispatched.get("attempt_id", "-attempt-1")
                                   ).rsplit("-attempt-", 1)[-1] or 1),
        "dispatch_template_sha256": prompts.get("dispatch_template_sha256"),
        "rendered_prompt_sha256": prompts.get("rendered_sha256"),
        "preparation": {"attestation_ready": attestation.get("ready"),
                        "checks": checks_of(attestation)},
        "isolation": {
            "pre_dispatch_ready": pre.get("ready"), "pre_dispatch_checks": checks_of(pre),
            "post_dispatch_ready": post.get("ready"), "post_dispatch_checks": checks_of(post),
            "forbidden_paths_examined": next(
                (c.get("examined") for c in pre.get("checks", [])
                 if str(c.get("check", "")).startswith("forbidden paths")), None),
            "mount_count": len(mounts.get("requested_mounts", [])),
        },
        "disposition": dispatched.get("disposition"),
        "completion": settled.get("completion") or dispatched.get("completion"),
        "elapsed_seconds": dispatched.get("elapsed_seconds"),
        "phases": [{"label": phase.get("label"), "exit_code": phase.get("exit_code"),
                    "subtype": phase.get("subtype"), "is_error": phase.get("is_error"),
                    "num_turns": phase.get("num_turns"),
                    "elapsed_seconds": phase.get("elapsed_seconds"),
                    "cost_usd": phase.get("cost_usd")}
                   for phase in dispatched.get("phases", [])],
        "fidelity": {
            "effort_report": effort,
            "transcript_count": settled.get("transcript_count"),
            "models_priced": sorted(usage.get("per_model", {})),
        },
        "accounting": {
            "self_report_usd": settled.get("self_report_usd"),
            "usage_split_total_usd": settled.get("usage_split_total_usd"),
            "settled_usd": settled.get("settled_usd"),
            "reconciliation_residual_usd": settled.get("reconciliation_residual_usd"),
            "within_tolerance": settled.get("usage_within_tolerance"),
        },
        "egress": {"attempts": settled.get("egress_attempts"),
                   "refused": settled.get("egress_refused")},
        "read_audit_passed": load(root / "artifacts" / "read-audit.json",
                                  {}).get("passed"),
        "problems": (dispatched.get("problems") or []) + (settled.get("problems") or []),
    }
    if dispatched.get("finder"):
        summary["finder"] = {"cost_usd": dispatched["finder"].get("cost_usd"),
                             "problem_count": len(dispatched["finder"].get("problems") or []),
                             "discovery_sha256": dispatched["finder"].get("discovery_sha256")}
    return scrub(summary, secrets)


# Compiler output is not evidence. A cargo target directory runs to hundreds of
# megabytes and is fully reproducible from the pinned clone, so it is excluded by
# name, and any other oversized file is excluded by size and listed.
# Build output plus the inputs that are reproducible from the freeze: the clone and
# its mirror come from the pinned recipe and OIDs, and the toolchain caches from the
# recorded provisioning. The attestation already pins both object stores by digest,
# so sealing the bytes again would add hundreds of megabytes and no evidence.
BUILD_DIRS = ("target", "target-scratch", "incremental", ".fingerprint",
              "caches", "clone", "mirror.git")
MAX_FILE_BYTES = 4 * 1024 * 1024


def copy_evidence(source, destination) -> list:
    """Copy a tree, skipping build output, and report what was left behind."""
    skipped = []
    for path in sorted(Path(source).rglob("*")):
        relative = path.relative_to(source)
        if any(part in BUILD_DIRS for part in relative.parts):
            continue
        if path.is_dir():
            (destination / relative).mkdir(parents=True, exist_ok=True)
            continue
        if path.is_symlink() or not path.is_file():
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            skipped.append({"path": str(relative), "bytes": path.stat().st_size})
            continue
        (destination / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination / relative)
    return skipped


def stage_sealed(root, staging) -> list:
    """Copy one position's full evidence, identity included, into the seal staging."""
    destination = staging / ("position-%02d" % load(root / "artifacts" / "prepare.json")["position"])
    destination.mkdir(parents=True, exist_ok=True)
    skipped = []
    for name in ("artifacts", "runner", "logs", "work"):
        if (root / name).is_dir():
            skipped.extend(copy_evidence(root / name, destination / name))
    discovery = root / "finder-store" / "discovery.json"
    if discovery.is_file():
        shutil.copyfile(discovery, destination / "discovery.json")
    home = root.parent / "homes" / root.name / ".claude" / "projects"
    if home.is_dir():
        skipped.extend(copy_evidence(home, destination / "transcripts"))
    if skipped:
        write(destination / "excluded-from-seal.json",
              {"reason": "build output and oversized files are reproducible from the "
                         "pinned clone and are not evidence",
               "excluded": skipped})
    return skipped


def seal(staging, out, key) -> dict:
    """Tar the staging, record the plaintext digest, encrypt under #148's key."""
    # Compressed before encryption: the bulk is JSONL transcripts, which compress by
    # roughly an order of magnitude, and encrypting afterwards means the committed blob
    # is small without revealing anything about its contents.
    tar = out / "sealed" / "pilot-evidence.tar.gz"
    tar.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["tar", "-czf", str(tar), "-C", str(staging), "."],
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise Failed("tar: %s" % result.stderr.strip())
    plaintext = hashlib.sha256(tar.read_bytes()).hexdigest()
    encrypted = out / "sealed" / "pilot-evidence.tar.gz.enc"
    result = subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-salt",
         "-pass", "file:%s" % key, "-in", str(tar), "-out", str(encrypted)],
        capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise Failed("openssl: %s" % result.stderr.strip())
    tar.unlink()
    (out / "sealed" / "SHA256SUMS").write_text(
        "%s  pilot-evidence.tar.gz\n" % plaintext, encoding="utf-8")
    return {"plaintext_sha256": plaintext,
            "ciphertext_sha256": hashlib.sha256(encrypted.read_bytes()).hexdigest(),
            "ciphertext_bytes": encrypted.stat().st_size}


def leak_scan(public, secrets, extra) -> list:
    """Refuse to publish if any identifying token survived into a public file.

    The whitelist and the scrub are both things a future edit can get wrong, so the
    last step is a mechanical check of the bytes actually being published rather than
    trust in the two steps that produced them.
    """
    hits = []
    for path in sorted(Path(public).rglob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in list(secrets) + list(extra):
            if token and token in text:
                hits.append("%s names %r" % (path, token))
    return hits


def leak_tokens(config) -> list:
    """The leak-set digests, which identify a target as precisely as its name."""
    tokens = []
    leaks = Path(os.path.expanduser(config.get("leak_sets", "")))
    if leaks.is_dir():
        for entry in sorted(leaks.glob("*.json")):
            tokens.append(hashlib.sha256(entry.read_bytes()).hexdigest())
            tokens.append(entry.stem)
    return tokens


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config")
    parser.add_argument("--out")
    parser.add_argument("--key")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.config or not args.out or not args.key:
        parser.error("--config, --out and --key are required")

    try:
        config = load(args.config)
        secrets = secrets_from(config["targets"])
        out = Path(args.out)
        cells = Path(os.path.expanduser(config["cells_root"]))
        staging = cells / "seal-staging"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        positions = []
        excluded = []
        for root in sorted(cells.glob("position-*")):
            if not (root / "artifacts" / "prepare.json").is_file():
                continue
            summary = summarize(root, secrets)
            write(out / "cells" / root.name / "summary.json", summary)
            excluded.extend(stage_sealed(root, staging))
            positions.append(summary["position"])
        # Invalidated attempts are sealed too: the replacement policy requires the raw
        # output and the costs of an invalid attempt to be retained, not discarded.
        invalid = cells.parent / "invalid"
        invalidated = []
        if invalid.is_dir():
            for entry in sorted(invalid.iterdir()):
                if entry.is_dir():
                    excluded.extend(copy_evidence(entry, staging / "invalid" / entry.name))
                    invalidated.append(entry.name)
        ledger = Path(os.path.expanduser(config["ledger"]))
        if ledger.is_file():
            shutil.copyfile(ledger, staging / "ledger.json")
        hits = leak_scan(out / "cells", secrets, leak_tokens(config))
        if hits:
            for hit in hits:
                print(hit)
            print("refusing to seal: the public summaries would disclose sealed truth")
            return 1
        sealed = seal(staging, out, os.path.expanduser(args.key))
        shutil.rmtree(staging)
        write(out / "sealed" / "seal.json",
              {"positions": positions, "ledger_included": ledger.is_file(),
               "invalidated_attempts_sealed": invalidated,
               "excluded_file_count": len(excluded), **sealed})
        print("sealed %d positions; plaintext %s" % (len(positions), sealed["plaintext_sha256"]))
        return 0
    except Failed as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2


def self_test():
    import tempfile
    checks = []
    # Fixtures deliberately name a slot outside the real range and a fictional
    # repository, so nothing in this file can be misread as evidence about the run.
    secrets = ["example/repo", "repo-9999", "slot-9", "9999"]
    scrubbed = scrub({"note": "cell slot-9 on example/repo#9999 failed"}, secrets)
    checks.append(("an identifying string is scrubbed",
                   "slot-9" not in scrubbed["note"] and "example" not in scrubbed["note"]))
    checks.append(("a longer token is replaced before its substring",
                   scrub("repo-9999", ["repo-9999", "9999"]) == "<sealed>"))
    checks.append(("nested values are scrubbed",
                   scrub({"a": ["slot-9"]}, secrets) == {"a": ["<sealed>"]}))
    checks.append(("non-strings pass through", scrub({"n": 3, "b": True}, secrets)
                   == {"n": 3, "b": True}))
    checks.append(("check lists keep only name and verdict",
                   checks_of({"checks": [{"check": "x", "passed": True, "objects": 40737}]})
                   == [{"check": "x", "passed": True}]))
    root = Path(tempfile.mkdtemp())
    (root / "sealed").mkdir()
    staging = root / "staging"
    (staging / "position-99").mkdir(parents=True)
    (staging / "position-99" / "secret.txt").write_text("slot-9\n", encoding="utf-8")
    key = root / "key"
    key.write_text("test-key\n", encoding="utf-8")
    sealed = seal(staging, root, str(key))
    checks.append(("sealing produces ciphertext and a plaintext digest",
                   (root / "sealed" / "pilot-evidence.tar.gz.enc").is_file()
                   and len(sealed["plaintext_sha256"]) == 64
                   and not (root / "sealed" / "pilot-evidence.tar.gz").exists()))
    blob = (root / "sealed" / "pilot-evidence.tar.gz.enc").read_bytes()
    checks.append(("the ciphertext does not contain the cleartext token",
                   b"slot-9" not in blob))
    tree = root / "evidence"
    (tree / "work" / "target" / "deps").mkdir(parents=True)
    (tree / "work" / "target" / "deps" / "libx.rlib").write_bytes(b"x" * 1024)
    (tree / "work" / "report.md").write_text("report\n", encoding="utf-8")
    (tree / "work" / "huge.bin").write_bytes(b"y" * (MAX_FILE_BYTES + 1))
    out = root / "staged"
    left = copy_evidence(tree, out)
    checks.append(("build output is excluded by name",
                   not (out / "work" / "target").exists()))
    checks.append(("ordinary evidence is copied",
                   (out / "work" / "report.md").is_file()))
    checks.append(("an oversized file is excluded and listed",
                   not (out / "work" / "huge.bin").exists()
                   and [entry["path"] for entry in left] == ["work/huge.bin"]))
    public = root / "public"
    (public / "position-99").mkdir(parents=True)
    (public / "position-99" / "summary.json").write_text(
        json.dumps({"arm": "A", "position": 99}) + "\n", encoding="utf-8")
    checks.append(("a clean public tree passes the leak scan",
                   leak_scan(public, secrets, []) == []))
    (public / "position-99" / "oops.json").write_text(
        json.dumps({"note": "ran on slot-9"}) + "\n", encoding="utf-8")
    checks.append(("a leaked token is caught by the scan",
                   len(leak_scan(public, secrets, [])) == 1))
    (public / "position-99" / "oops.json").write_text(
        json.dumps({"digest": "deadbeef"}) + "\n", encoding="utf-8")
    checks.append(("an extra token such as a leak-set digest is caught",
                   len(leak_scan(public, secrets, ["deadbeef"])) == 1))
    for name, passed in checks:
        print("%s %s" % ("ok  " if passed else "FAIL", name))
    return 0 if all(passed for _, passed in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
