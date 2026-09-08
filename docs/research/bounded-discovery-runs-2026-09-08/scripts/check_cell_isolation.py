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

Checks, in order:

1. every forbidden path is absent (``os.lstat`` fails), including the evaluator
   key directory, the other slots' mirrors and clones, and the repository
   checkouts holding this bundle;
2. every permitted root exists, and no permitted root contains a forbidden one;
3. the clone is at the pinned head, its base branch at the pinned merge-base, and
   its tracked tree is clean;
4. no SHA in the slot's sealed leak set resolves in the clone or its origin
   mirror (the leak set is read from evaluator-only storage and never printed);
5. the egress proxy is listening and refuses a host that is not on its allow list.

Usage::

    python3 scripts/check_cell_isolation.py --spec cell-env.json \\
        --phase pre-dispatch|post-dispatch --out record.json
    python3 scripts/check_cell_isolation.py --self-test

Spec schema (UTF-8 JSON)::

    {"cell_id": str, "target_slot": str,
     "permitted_roots": [path, ...],
     "forbidden_paths": [path, ...],
     "clone": {"path": path, "head_oid": str, "base_branch": str, "merge_base_oid": str},
     "leak_set": path,          # evaluator-only JSON with a "shas" list; optional
     "egress_proxy": {"host": str, "port": int, "probe_host": str}}

Output: a JSON record with one entry per check and an overall ``ready`` flag.

Exit: 0 when every check passes, 1 when any check fails, with one line per
failure on stdout, 2 when the spec cannot be read or a git call fails.
"""
from __future__ import annotations

import argparse
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


def check_leak_set(clone, leak_set_path):
    """Resolve nothing to stdout: report only how many SHAs were checked and how many hit."""
    try:
        document = json.loads(Path(os.path.expanduser(leak_set_path)).read_text(encoding="utf-8"))
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


def run(spec, phase):
    checks = [check_absence(spec["forbidden_paths"]),
              check_roots(spec["permitted_roots"], spec["forbidden_paths"]),
              check_clone(spec["clone"])]
    if spec.get("leak_set"):
        checks.append(check_leak_set(spec["clone"], spec["leak_set"]))
    else:
        checks.append({"check": "no sealed leak-set object resolves in the clone or its mirror",
                       "passed": False, "note": "no leak set was supplied, so this is unestablished"})
    checks.append(check_egress(spec["egress_proxy"]))
    return {"schema_version": "bounded-discovery-v1", "cell_id": spec["cell_id"],
            "target_slot": spec["target_slot"], "phase": phase,
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
    for name, ok in checks:
        print(("ok   " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in checks) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--spec")
    parser.add_argument("--phase", choices=("pre-dispatch", "post-dispatch"), default="pre-dispatch")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.spec:
        parser.error("--spec is required")
    try:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        record = run(spec, args.phase)
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
