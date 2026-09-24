#!/usr/bin/env python3
"""Build, check and clone the truncated mirror of a benchmark target.

Usage::

    python3 bench/tools/provision.py mirror --target bench/targets/<id> --staging <full-clone.git> [--cache-root DIR]
    python3 bench/tools/provision.py check  --target bench/targets/<id> [--cache-root DIR]
    python3 bench/tools/provision.py clone  --target bench/targets/<id> --out <dir> [--cache-root DIR]
    python3 bench/tools/provision.py --self-test

``mirror`` creates ``<cache-root>/mirrors/<id>.git`` from a staging clone that holds the full
upstream history: ``review-head`` at the target's ``head`` and ``main`` at its ``merge_base``
(design §5: every mirror names the base ``main`` because the Claude built-in diffs ``main...HEAD``).
It then verifies the mirror the way the #137 runner did, plus the suite's diff identity:

1. every ``negative_shas`` entry is absent from the mirror (a hit deletes the mirror and fails);
2. the newest commit date reachable from ``review-head`` equals the head's own date, so nothing
   later than the pinned head is reachable;
3. ``diff_identity.py`` over ``main..review-head`` equals ``target.json``'s ``diff_manifest_sha256``.

It writes ``<cache-root>/mirrors/<id>.json`` with the outcome. ``check`` repeats the three checks
on an existing mirror. ``clone`` makes a working clone for one attempt from the mirror, with
``main`` at the merge-base and ``review-head`` checked out, and repeats checks 1 and 3 on the
clone, which is what a runner does before dispatch. Dependency caches are not built here yet.

The cache root defaults to ``~/.t3/bench-cache``. Nothing under it enters the repository.

Exit codes: 0 built or verified; 1 a check failed, one line per failure on stdout (a failed
``mirror`` build leaves no mirror behind); 2 an input cannot be read, a pinned revision is
missing from the staging clone, or a git command failed, with the command on stderr.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diff_identity  # noqa: E402

DEFAULT_CACHE_ROOT = os.path.join(os.path.expanduser("~"), ".t3", "bench-cache")


class ProvisionError(Exception):
    """Exit code 2."""


def git(*args: str, cwd: str = None) -> str:
    command = ["git", *args]
    try:
        return subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8", cwd=cwd).stdout
    except FileNotFoundError as error:
        raise ProvisionError(f"cannot run git: {error}") from error
    except subprocess.CalledProcessError as error:
        raise ProvisionError(f"command failed: {' '.join(command)}\n{(error.stderr or '').strip()}") from error


def has_object(repo: str, sha: str) -> bool:
    return subprocess.run(["git", "-C", repo, "cat-file", "-e", sha], capture_output=True).returncode == 0


def load_target(target_dir: str) -> dict:
    path = Path(target_dir, "target.json")
    try:
        target = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProvisionError(f"{path}: {error}") from error
    for key in ("id", "head", "merge_base", "negative_shas", "diff_manifest_sha256", "local_base_branch"):
        if key not in target:
            raise ProvisionError(f"{path}: missing {key}")
    return target


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def checks(repo: str, target: dict, base_ref: str, head_ref: str, date_check: bool) -> list:
    """Return a list of failure lines (empty when everything holds)."""
    failures = []
    for entry in target["negative_shas"]:
        if has_object(repo, entry["sha"]):
            failures.append(f"leak: negative sha {entry['sha']} is present ({entry.get('reason', 'no reason recorded')})")
    if date_check:
        # Unix timestamps, not ISO strings: upstream histories carry malformed offsets (psf/requests has a
        # 2011 commit stamped +518:00) that no ISO parser accepts, and git itself compares by %ct.
        try:
            stamps = [int(s) for s in git("-C", repo, "log", "--format=%ct", head_ref).split()]
            head_stamp = int(git("-C", repo, "log", "-1", "--format=%ct", head_ref).strip())
        except (ProvisionError, ValueError) as error:
            failures.append(f"history: {error}")
        else:
            newest = max(stamps)
            if newest != head_stamp:
                later = datetime.fromtimestamp(newest, timezone.utc).isoformat()
                head_iso = datetime.fromtimestamp(head_stamp, timezone.utc).isoformat()
                failures.append(f"history: newest reachable commit {later} is later than the head's {head_iso}")
    try:
        _rows, digest = diff_identity.identity(repo, base_ref, head_ref)
    except diff_identity.RepoError as error:
        failures.append(f"diff identity: {error}")
    else:
        if digest != target["diff_manifest_sha256"]:
            failures.append(f"diff identity mismatch: expected {target['diff_manifest_sha256']}, computed {digest}")
    return failures


def mirror_path(cache_root: str, target: dict) -> str:
    return os.path.join(cache_root, "mirrors", target["id"] + ".git")


def cmd_mirror(args) -> int:
    target = load_target(args.target)
    staging = os.path.abspath(args.staging)
    for sha in (target["head"], target["merge_base"]):
        if not has_object(staging, sha):
            raise ProvisionError(f"staging clone {staging} lacks {sha}")
    base = target["local_base_branch"]
    path = mirror_path(args.cache_root, target)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    git("init", "-q", "--bare", path)
    git("-C", staging, "push", "-q", path, f"{target['head']}:refs/heads/review-head", f"{target['merge_base']}:refs/heads/{base}")
    git("-C", path, "symbolic-ref", "HEAD", f"refs/heads/{base}")
    failures = checks(path, target, base, "review-head", date_check=True)
    record = {
        "target": target["id"], "built_at": now(), "staging": staging, "mirror": path,
        "refs": {"review-head": target["head"], base: target["merge_base"]},
        "negative_shas_checked": [e["sha"] for e in target["negative_shas"]],
        "diff_manifest_sha256": target["diff_manifest_sha256"], "ok": not failures, "failures": failures,
    }
    if failures:
        shutil.rmtree(path)
        for line in failures:
            print(line)
        return 1
    Path(os.path.dirname(path), target["id"] + ".json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"mirror {path}: review-head={target['head'][:12]} {base}={target['merge_base'][:12]}; "
          f"{len(target['negative_shas'])} negative sha(s) absent; diff identity verified")
    return 0


def cmd_check(args) -> int:
    target = load_target(args.target)
    path = mirror_path(args.cache_root, target)
    if not os.path.isdir(path):
        raise ProvisionError(f"no mirror at {path}")
    for ref, sha in (("review-head", target["head"]), (target["local_base_branch"], target["merge_base"])):
        try:
            actual = git("-C", path, "rev-parse", "--verify", f"refs/heads/{ref}").strip()
        except ProvisionError:
            print(f"ref: {ref} is missing from {path}")
            return 1
        if actual != sha:
            print(f"ref: {ref} is {actual}, expected {sha}")
            return 1
    failures = checks(path, target, target["local_base_branch"], "review-head", date_check=True)
    for line in failures:
        print(line)
    if not failures:
        print(f"mirror {path}: ok")
    return 1 if failures else 0


def cmd_clone(args) -> int:
    target = load_target(args.target)
    path = mirror_path(args.cache_root, target)
    if not os.path.isdir(path):
        raise ProvisionError(f"no mirror at {path}")
    out = os.path.abspath(args.out)
    if os.path.exists(out):
        raise ProvisionError(f"clone target exists: {out} (attempt directories are never reused)")
    base = target["local_base_branch"]
    git("clone", "-q", path, out)
    git("-C", out, "checkout", "-q", "--detach", target["head"])
    git("-C", out, "branch", "-q", "-f", base, target["merge_base"])
    git("-C", out, "checkout", "-q", "-B", "review-head", target["head"])
    if git("-C", out, "rev-parse", "HEAD").strip() != target["head"]:
        print("head mismatch after checkout")
        return 1
    failures = checks(out, target, base, "review-head", date_check=False)
    for line in failures:
        print(line)
    if failures:
        shutil.rmtree(out)
        return 1
    print(f"clone {out}: review-head checked out at {target['head'][:12]}, {base} at {target['merge_base'][:12]}")
    return 0


def self_test() -> int:
    here = Path(__file__).resolve()
    with tempfile.TemporaryDirectory() as temp:
        staging = str(Path(temp, "staging"))
        subprocess.run(["git", "init", "-q", "-b", "trunk", staging], check=True)
        ident = ["-c", "user.name=t", "-c", "user.email=t@example.com"]

        def commit(message: str) -> str:
            subprocess.run(["git", "-C", staging, "add", "-A"], check=True)
            subprocess.run(["git", *ident, "-C", staging, "commit", "-q", "-m", message], check=True)
            return subprocess.run(["git", "-C", staging, "rev-parse", "HEAD"], check=True, capture_output=True,
                                  text=True, encoding="utf-8").stdout.strip()

        Path(staging, "f.txt").write_text("base\n", encoding="utf-8")
        base = commit("base")
        Path(staging, "f.txt").write_text("head\n", encoding="utf-8")
        head = commit("head")
        Path(staging, "f.txt").write_text("fix\n", encoding="utf-8")
        leak = commit("fix that reveals the answer")
        _rows, digest = diff_identity.identity(staging, base, head)
        target_dir = Path(temp, "targets", "t-1")
        target_dir.mkdir(parents=True)
        target = {"id": "t-1", "head": head, "merge_base": base, "local_base_branch": "main",
                  "negative_shas": [{"sha": leak, "reason": "the fix"}], "diff_manifest_sha256": digest}
        (target_dir / "target.json").write_text(json.dumps(target), encoding="utf-8")
        cache = str(Path(temp, "cache"))

        def run(*argv):
            return subprocess.run([sys.executable, str(here), *argv, "--cache-root", cache], capture_output=True,
                                  text=True, encoding="utf-8")

        done = run("mirror", "--target", str(target_dir), "--staging", staging)
        assert done.returncode == 0, done
        mirror = Path(cache, "mirrors", "t-1.git")
        assert mirror.is_dir() and Path(cache, "mirrors", "t-1.json").is_file()
        assert not has_object(str(mirror), leak), "the leak commit must not be in the mirror"
        assert git("-C", str(mirror), "symbolic-ref", "HEAD").strip() == "refs/heads/main"
        done = run("check", "--target", str(target_dir))
        assert done.returncode == 0 and "ok" in done.stdout, done
        clone = str(Path(temp, "clone"))
        done = run("clone", "--target", str(target_dir), "--out", clone)
        assert done.returncode == 0, done
        assert git("-C", clone, "rev-parse", "--abbrev-ref", "HEAD").strip() == "review-head"
        assert git("-C", clone, "rev-parse", "main").strip() == base
        done = run("clone", "--target", str(target_dir), "--out", clone)
        assert done.returncode == 2, "an existing clone directory must be refused"
        # A wrong diff identity is a check failure, and a failed build leaves no mirror.
        bad = dict(target, diff_manifest_sha256="0" * 64)
        (target_dir / "target.json").write_text(json.dumps(bad), encoding="utf-8")
        done = run("mirror", "--target", str(target_dir), "--staging", staging)
        assert done.returncode == 1 and "diff identity mismatch" in done.stdout, done
        assert not mirror.exists(), "a failed build must not leave a mirror"
        # A negative sha that is reachable from the head is a leak.
        leaky = dict(target, negative_shas=[{"sha": base, "reason": "reachable on purpose"}])
        (target_dir / "target.json").write_text(json.dumps(leaky), encoding="utf-8")
        done = run("mirror", "--target", str(target_dir), "--staging", staging)
        assert done.returncode == 1 and "leak:" in done.stdout, done
        # A staging clone missing the head is an input error.
        (target_dir / "target.json").write_text(json.dumps(dict(target, head="f" * 40)), encoding="utf-8")
        done = run("mirror", "--target", str(target_dir), "--staging", staging)
        assert done.returncode == 2, done
    print("self-test ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    for name in ("mirror", "check", "clone"):
        p = sub.add_parser(name)
        p.add_argument("--target", required=True, help="target directory holding target.json")
        p.add_argument("--cache-root", default=DEFAULT_CACHE_ROOT)
        if name == "mirror":
            p.add_argument("--staging", required=True, help="full clone holding the head and the merge-base")
        if name == "clone":
            p.add_argument("--out", required=True, help="new directory for the working clone")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.command:
        parser.error("give a subcommand or --self-test")
    try:
        return {"mirror": cmd_mirror, "check": cmd_check, "clone": cmd_clone}[args.command](args)
    except ProvisionError as error:
        print(f"provision.py: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
