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


def stage_sealed(root, staging):
    """Copy one position's full evidence, identity included, into the seal staging."""
    destination = staging / ("position-%02d" % load(root / "artifacts" / "prepare.json")["position"])
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("artifacts", "runner", "logs"):
        if (root / name).is_dir():
            shutil.copytree(root / name, destination / name, dirs_exist_ok=True)
    work = root / "work"
    if work.is_dir():
        shutil.copytree(work, destination / "work", dirs_exist_ok=True)
    discovery = root / "finder-store" / "discovery.json"
    if discovery.is_file():
        shutil.copyfile(discovery, destination / "discovery.json")
    home = root.parent / "homes" / root.name / ".claude" / "projects"
    if home.is_dir():
        shutil.copytree(home, destination / "transcripts", dirs_exist_ok=True)


def seal(staging, out, key) -> dict:
    """Tar the staging, record the plaintext digest, encrypt under #148's key."""
    tar = out / "sealed" / "pilot-evidence.tar"
    tar.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["tar", "-cf", str(tar), "-C", str(staging), "."],
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise Failed("tar: %s" % result.stderr.strip())
    plaintext = hashlib.sha256(tar.read_bytes()).hexdigest()
    encrypted = out / "sealed" / "pilot-evidence.tar.enc"
    result = subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-salt",
         "-pass", "file:%s" % key, "-in", str(tar), "-out", str(encrypted)],
        capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise Failed("openssl: %s" % result.stderr.strip())
    tar.unlink()
    (out / "sealed" / "SHA256SUMS").write_text(
        "%s  pilot-evidence.tar\n" % plaintext, encoding="utf-8")
    return {"plaintext_sha256": plaintext,
            "ciphertext_sha256": hashlib.sha256(encrypted.read_bytes()).hexdigest(),
            "ciphertext_bytes": encrypted.stat().st_size}


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
        for root in sorted(cells.glob("position-*")):
            if not (root / "artifacts" / "prepare.json").is_file():
                continue
            summary = summarize(root, secrets)
            write(out / "cells" / root.name / "summary.json", summary)
            stage_sealed(root, staging)
            positions.append(summary["position"])
        ledger = Path(os.path.expanduser(config["ledger"]))
        if ledger.is_file():
            shutil.copyfile(ledger, staging / "ledger.json")
        sealed = seal(staging, out, os.path.expanduser(args.key))
        shutil.rmtree(staging)
        write(out / "sealed" / "seal.json",
              {"positions": positions, "ledger_included": ledger.is_file(), **sealed})
        print("sealed %d positions; plaintext %s" % (len(positions), sealed["plaintext_sha256"]))
        return 0
    except Failed as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2


def self_test():
    import tempfile
    checks = []
    secrets = ["grpc/grpc-go", "grpc-go-7417", "slot-2", "7417"]
    scrubbed = scrub({"note": "cell slot-2 on grpc/grpc-go#7417 failed"}, secrets)
    checks.append(("an identifying string is scrubbed",
                   "slot-2" not in scrubbed["note"] and "grpc" not in scrubbed["note"]))
    checks.append(("a longer token is replaced before its substring",
                   scrub("grpc-go-7417", ["grpc-go-7417", "7417"]) == "<sealed>"))
    checks.append(("nested values are scrubbed",
                   scrub({"a": ["slot-2"]}, secrets) == {"a": ["<sealed>"]}))
    checks.append(("non-strings pass through", scrub({"n": 3, "b": True}, secrets)
                   == {"n": 3, "b": True}))
    checks.append(("check lists keep only name and verdict",
                   checks_of({"checks": [{"check": "x", "passed": True, "objects": 40737}]})
                   == [{"check": "x", "passed": True}]))
    root = Path(tempfile.mkdtemp())
    (root / "sealed").mkdir()
    staging = root / "staging"
    (staging / "position-01").mkdir(parents=True)
    (staging / "position-01" / "secret.txt").write_text("slot-2\n", encoding="utf-8")
    key = root / "key"
    key.write_text("test-key\n", encoding="utf-8")
    sealed = seal(staging, root, str(key))
    checks.append(("sealing produces ciphertext and a plaintext digest",
                   (root / "sealed" / "pilot-evidence.tar.enc").is_file()
                   and len(sealed["plaintext_sha256"]) == 64
                   and not (root / "sealed" / "pilot-evidence.tar").exists()))
    blob = (root / "sealed" / "pilot-evidence.tar.enc").read_bytes()
    checks.append(("the ciphertext does not contain the cleartext token",
                   b"slot-2" not in blob))
    for name, passed in checks:
        print("%s %s" % ("ok  " if passed else "FAIL", name))
    return 0 if all(passed for _, passed in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
