#!/usr/bin/env python3
"""Verify one cell's isolation immediately before and after its dispatch.

Probes 2b and 7 established what the runtime does and does not enforce: the file
tools are confined to the session's working directories under ``--restricted``,
but an allow-listed interpreter in the shell reads any path that exists on the
machine, and a raw socket to an IP address bypasses the egress proxy. The control
that actually holds, therefore, is **absence**: hidden truth, the other targets'
mirrors and clones, the other attempts' stores and the experiment's own
documentation must not be on the local filesystem while a cell runs.

This script is that check, run before dispatch and again after the cell stops. It
refuses to report success on anything it could not establish.

The leak-set check and the absence gate cannot run at the same moment, and
pretending otherwise was this script's first mistake: the leak set lives in the
evaluator-only storage that the absence gate requires to be gone. So the check
runs in two phases against the same cell.

**preparation** — evaluator material still present, before it is removed. Pins the
clone and its mirror, reads the sealed leak set, confirms that none of its objects
resolves in either, and writes an **attestation**: the clone head, the base and
merge-base, the mirror's refs, the SHA-256 of the leak-set *file*, and how many
objects were examined and hit. It carries no SHA *from* the set, so it survives
into the dispatch window without carrying truth with it. The file digest names
which set was checked. Nothing during the dispatch window can compare it — the
file is deliberately gone by then — but #152 and #153 can, once the sealed
material comes back, which is what makes the attestation auditable rather than
merely asserted.

**pre-dispatch** and **post-dispatch** — evaluator material gone. Verify absence,
the permitted roots, the clone and mirror still in exactly the state the
attestation pinned, that the attestation reports a non-empty leak set with zero
hits, and that the egress proxy refuses a host outside its allow list. No
evaluator file is read in these phases, and none needs to be.

Usage::

    python3 scripts/check_cell_isolation.py --spec cell-env.json \\
        --phase preparation --out attestation.json
    python3 scripts/check_cell_isolation.py --spec cell-env.json --phase pre-dispatch \\
        --attestation attestation.json --out record.json
    python3 scripts/check_cell_isolation.py --self-test

Spec schema (UTF-8 JSON)::

    {"cell_id": str, "target_slot": str,
     "permitted_roots": [path, ...],
     "forbidden_paths": [path, ...],
     "clone": {"path": path, "head_oid": str, "base_branch": str, "merge_base_oid": str},
     "leak_set": path,          # evaluator-only JSON with a "shas" list; preparation only
     "egress_proxy": {"host": str, "port": int, "probe_host": str}}

Output: a JSON record with one entry per check and an overall ``ready`` flag; in
the preparation phase that record is the attestation the later phases consume.

Exit: 0 when every check passes, 1 when any check fails, with one line per
failure on stdout, 2 when the spec cannot be read or a git call fails.
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


class Unreadable(Exception):
    pass


def git(clone, *args):
    result = subprocess.run(["git", "-C", str(clone), *args], capture_output=True,
                            text=True, encoding="utf-8")
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def check_absence(paths):
    present = []
    for path in paths:
        try:
            os.lstat(os.path.expanduser(path))
            present.append(path)
        except OSError:
            continue
    return {"check": "forbidden paths are absent", "examined": len(paths),
            "present": present, "passed": not present}


def check_roots(roots, forbidden):
    missing = [root for root in roots if not Path(os.path.expanduser(root)).exists()]
    nested = []
    for root in roots:
        resolved = Path(os.path.expanduser(root)).resolve()
        for path in forbidden:
            candidate = Path(os.path.expanduser(path))
            try:
                candidate.resolve().relative_to(resolved)
            except (ValueError, OSError):
                continue
            nested.append({"root": root, "forbidden": path})
    return {"check": "permitted roots exist and hold no forbidden path",
            "missing": missing, "nested": nested, "passed": not missing and not nested}


def check_clone(clone):
    path = os.path.expanduser(clone["path"])
    code, head, error = git(path, "rev-parse", "HEAD")
    if code:
        raise Unreadable("git rev-parse HEAD in " + path + ": " + error)
    _, base, _ = git(path, "rev-parse", clone["base_branch"])
    _, dirty, _ = git(path, "status", "--short")
    return {"check": "clone is at the pinned head with a clean tree",
            "head_oid": head, "expected_head_oid": clone["head_oid"],
            "base_oid": base, "expected_merge_base_oid": clone["merge_base_oid"],
            "dirty_entries": [line for line in dirty.splitlines() if line],
            "passed": head == clone["head_oid"] and base == clone["merge_base_oid"] and not dirty}


def mirror_state(clone):
    """The origin mirror's path and refs, as the clone sees them."""
    path = os.path.expanduser(clone["path"])
    _, origin, _ = git(path, "remote", "get-url", "origin")
    refs = {}
    if origin:
        code, listing, _ = git(origin, "show-ref")
        if code == 0:
            for line in listing.splitlines():
                oid, _, name = line.partition(" ")
                refs[name.strip()] = oid
    return {"origin": origin, "refs": refs}


def check_leak_set(clone, leak_set_path):
    """Resolve nothing to stdout: report only how many SHAs were checked and how many hit."""
    try:
        raw = Path(os.path.expanduser(leak_set_path)).read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, ValueError) as exc:
        raise Unreadable("leak set " + leak_set_path + ": " + str(exc))
    shas = [str(sha) for sha in document.get("shas", [])]
    path = os.path.expanduser(clone["path"])
    _, origin, _ = git(path, "remote", "get-url", "origin")
    hits = 0
    for sha in shas:
        for repository in [path] + ([origin] if origin else []):
            code, _, _ = git(repository, "cat-file", "-e", sha + "^{object}")
            if code == 0:
                hits += 1
                break
    return {"check": "no sealed leak-set object resolves in the clone or its mirror",
            "examined": len(shas), "hits": hits, "passed": bool(shas) and hits == 0,
            # Which leak set this was, without saying what is in it. Nothing during the dispatch
            # window can compare it — the file is deliberately gone by then — but #152 and #153 can,
            # once the sealed material comes back, and that is what makes the attestation auditable
            # rather than merely asserted.
            "leak_set_sha256": hashlib.sha256(raw).hexdigest(),
            "note": "" if shas else "the leak set is empty, so this check establishes nothing"}


def check_egress(proxy):
    host, port = proxy["host"], int(proxy["port"])
    probe = proxy.get("probe_host", "api.github.com") + ":443"
    try:
        connection = http.client.HTTPConnection(host, port, timeout=10)
        connection.request("CONNECT", probe)
        status = connection.getresponse().status
        connection.close()
    except OSError as exc:
        return {"check": "egress proxy refuses a host that is not allow-listed",
                "error": str(exc), "passed": False}
    return {"check": "egress proxy refuses a host that is not allow-listed",
            "probe": probe, "status": status, "passed": status == 403}


def check_attestation(spec, attestation, mirror):
    """The dispatch-window stand-in for the leak-set check, bound to this exact clone."""
    problems = []
    if not attestation:
        problems.append("no attestation supplied; run --phase preparation first")
    else:
        if attestation.get("phase") != "preparation":
            problems.append("the attestation was not produced by the preparation phase")
        if attestation.get("cell_id") != spec["cell_id"]:
            problems.append("the attestation names cell %r, this is %r"
                            % (attestation.get("cell_id"), spec["cell_id"]))
        leak = next((c for c in attestation.get("checks", [])
                     if c["check"].startswith("no sealed leak-set object")), None)
        if not leak or not leak.get("passed"):
            problems.append("the attestation does not record a passing leak-set check")
        elif not leak.get("examined"):
            problems.append("the attestation's leak set was empty, so it establishes nothing")
        elif not leak.get("leak_set_sha256"):
            problems.append("the attestation names no leak-set digest, so which set it checked "
                            "cannot be audited at reveal")
        pinned = attestation.get("mirror") or {}
        if pinned.get("refs") != mirror["refs"]:
            problems.append("the mirror's refs changed since the attestation: %s then, %s now"
                            % (pinned.get("refs"), mirror["refs"]))
        clone = next((c for c in attestation.get("checks", [])
                      if c["check"].startswith("clone is at the pinned head")), None)
        if not clone or clone.get("head_oid") != spec["clone"]["head_oid"]:
            problems.append("the attestation pinned a different clone head")
    return {"check": "the preparation attestation covers this clone and mirror, with no leak-set hit",
            "attestation_observed_at": (attestation or {}).get("observed_at"),
            "problems": problems, "passed": not problems}


def run(spec, phase, attestation=None):
    clone = check_clone(spec["clone"])
    mirror = mirror_state(spec["clone"])
    if phase == "preparation":
        # Evaluator material is still present here, and this is the only phase that reads it.
        checks = [clone, check_leak_set(spec["clone"], spec["leak_set"])
                  if spec.get("leak_set") else
                  {"check": "no sealed leak-set object resolves in the clone or its mirror",
                   "passed": False, "examined": 0,
                   "note": "no leak set was supplied, so this is unestablished"}]
    else:
        checks = [check_absence(spec["forbidden_paths"]),
                  check_roots(spec["permitted_roots"], spec["forbidden_paths"]),
                  clone,
                  check_attestation(spec, attestation, mirror),
                  check_egress(spec["egress_proxy"])]
    return {"schema_version": "bounded-discovery-v1", "cell_id": spec["cell_id"],
            "target_slot": spec["target_slot"], "phase": phase, "mirror": mirror,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "checks": checks, "ready": all(check["passed"] for check in checks)}


def self_test():
    import tempfile
    checks = []
    root = Path(tempfile.mkdtemp())
    absent = check_absence([str(root / "nothing"), str(root)])
    checks.append(("an existing forbidden path fails", absent["passed"] is False and
                   absent["present"] == [str(root)]))
    checks.append(("absent forbidden paths pass", check_absence([str(root / "nothing")])["passed"]))
    nested = check_roots([str(root)], [str(root / "inside")])
    checks.append(("a forbidden path inside a permitted root fails", nested["passed"] is False))
    checks.append(("a missing permitted root fails", check_roots([str(root / "gone")], [])["passed"] is False))
    clone = root / "clone"
    clone.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(clone)], check=True,
                   capture_output=True, text=True, encoding="utf-8")
    (clone / "a.txt").write_text("a\n", encoding="utf-8")
    for command in (["add", "a.txt"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "a"]):
        git(clone, *command)
    _, head, _ = git(clone, "rev-parse", "HEAD")
    good = check_clone({"path": str(clone), "head_oid": head, "base_branch": "main",
                        "merge_base_oid": head})
    checks.append(("a pinned clean clone passes", good["passed"]))
    (clone / "a.txt").write_text("dirtied\n", encoding="utf-8")
    dirty = check_clone({"path": str(clone), "head_oid": head, "base_branch": "main",
                         "merge_base_oid": head})
    checks.append(("a dirtied tree fails", dirty["passed"] is False))
    wrong = check_clone({"path": str(clone), "head_oid": "0" * 40, "base_branch": "main",
                         "merge_base_oid": head})
    checks.append(("a head mismatch fails", wrong["passed"] is False))
    try:
        check_leak_set({"path": str(clone)}, str(root / "missing-leak-set.json"))
        checks.append(("an unreadable leak set is an input error", False))
    except Unreadable:
        checks.append(("an unreadable leak set is an input error", True))
    (root / "leak.json").write_text(json.dumps({"shas": [head]}), encoding="utf-8")
    present = check_leak_set({"path": str(clone)}, str(root / "leak.json"))
    checks.append(("a leak-set object present in the clone fails",
                   present["passed"] is False and present["hits"] == 1))
    (root / "clean-leak.json").write_text(json.dumps({"shas": ["0" * 40]}), encoding="utf-8")
    clean = check_leak_set({"path": str(clone)}, str(root / "clean-leak.json"))
    checks.append(("a leak set that resolves nowhere passes", clean["passed"] and clean["hits"] == 0))
    (root / "empty-leak.json").write_text(json.dumps({"shas": []}), encoding="utf-8")
    empty = check_leak_set({"path": str(clone)}, str(root / "empty-leak.json"))
    checks.append(("an empty leak set establishes nothing", empty["passed"] is False))
    checks.append(("a proxy that is not listening fails",
                   check_egress({"host": "127.0.0.1", "port": 1, "probe_host": "example.invalid"})["passed"] is False))

    # The two phases, end to end: preparation reads the leak set, dispatch reads only the
    # attestation it left behind, and the evaluator file is gone by then.
    (clone / "a.txt").write_text("a\n", encoding="utf-8")     # undo the dirtying above
    mirror = root / "mirror.git"
    subprocess.run(["git", "init", "-q", "--bare", str(mirror)], check=True,
                   capture_output=True, text=True, encoding="utf-8")
    git(clone, "remote", "add", "origin", str(mirror))
    git(clone, "push", "-q", "origin", "main")
    evaluator = root / "evaluator"
    evaluator.mkdir()
    (evaluator / "leak.json").write_text(json.dumps({"shas": ["0" * 40]}), encoding="utf-8")
    spec = {"cell_id": "slot-1-A-replicate-1", "target_slot": "slot-1",
            "permitted_roots": [str(clone)], "forbidden_paths": [str(evaluator)],
            "clone": {"path": str(clone), "head_oid": head, "base_branch": "main",
                      "merge_base_oid": head},
            "leak_set": str(evaluator / "leak.json"),
            "egress_proxy": {"host": "127.0.0.1", "port": 1, "probe_host": "example.invalid"}}
    prepared = run(spec, "preparation")
    checks.append(("preparation passes with evaluator material present", prepared["ready"]))
    checks.append(("preparation does not gate on absence",
                   not any(c["check"].startswith("forbidden paths") for c in prepared["checks"])))
    checks.append(("the attestation carries no leak-set SHA",
                   "0" * 40 not in json.dumps(prepared)))
    leak_check = next(c for c in prepared["checks"] if c["check"].startswith("no sealed leak-set"))
    checks.append(("the attestation names which leak-set file it read",
                   leak_check["leak_set_sha256"] ==
                   hashlib.sha256((evaluator / "leak.json").read_bytes()).hexdigest()))
    other = root / "other-leak.json"
    other.write_text(json.dumps({"shas": ["1" * 40]}), encoding="utf-8")
    checks.append(("a different leak-set file gets a different digest",
                   check_leak_set({"path": str(clone)}, str(other))["leak_set_sha256"]
                   != leak_check["leak_set_sha256"]))
    import shutil
    shutil.rmtree(evaluator)                                   # the dispatch window begins
    gate = run(spec, "pre-dispatch", prepared)
    attested = next(c for c in gate["checks"] if c["check"].startswith("the preparation attestation"))
    checks.append(("the attestation stands in for the leak set once it is gone", attested["passed"]))
    checks.append(("absence passes once evaluator material is removed",
                   next(c for c in gate["checks"] if c["check"].startswith("forbidden paths"))["passed"]))
    checks.append(("a dispatch phase with no attestation fails",
                   not run(spec, "pre-dispatch", None)["checks"][3]["passed"]))
    empty = json.loads(json.dumps(prepared))
    for c in empty["checks"]:
        if c["check"].startswith("no sealed leak-set object"):
            c["examined"] = 0
    checks.append(("an attestation over an empty leak set fails",
                   not run(spec, "pre-dispatch", empty)["checks"][3]["passed"]))
    undigested = json.loads(json.dumps(prepared))
    for c in undigested["checks"]:
        c.pop("leak_set_sha256", None)
    checks.append(("an attestation with no leak-set digest fails",
                   not run(spec, "pre-dispatch", undigested)["checks"][3]["passed"]))
    swapped = json.loads(json.dumps(prepared))
    swapped["mirror"]["refs"] = {"refs/heads/main": "1" * 40}
    checks.append(("a swapped mirror fails",
                   not run(spec, "pre-dispatch", swapped)["checks"][3]["passed"]))
    for name, ok in checks:
        print(("ok   " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in checks) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--spec")
    parser.add_argument("--phase", choices=("preparation", "pre-dispatch", "post-dispatch"),
                        default="pre-dispatch")
    parser.add_argument("--attestation", help="the preparation record, required outside preparation")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.spec:
        parser.error("--spec is required")
    if args.phase != "preparation" and not args.attestation:
        parser.error("--attestation is required outside the preparation phase")
    try:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        attestation = (json.loads(Path(args.attestation).read_text(encoding="utf-8"))
                       if args.attestation else None)
        record = run(spec, args.phase, attestation)
    except (OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Unreadable as exc:
        print(str(exc), file=sys.stderr)
        return 2
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    for check in record["checks"]:
        if not check["passed"]:
            print("FAILED: " + check["check"] + (" — " + check["note"] if check.get("note") else ""))
    if not args.out:
        sys.stdout.write(text)
    return 0 if record["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
