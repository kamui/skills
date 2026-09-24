#!/usr/bin/env python3
"""Build, check and clone the truncated mirror of a benchmark target, and build its dependency cache.

Usage::

    python3 bench/tools/provision.py mirror  --target bench/targets/<id> --staging <full-clone.git> [--cache-root DIR]
    python3 bench/tools/provision.py check   --target bench/targets/<id> [--cache-root DIR]
    python3 bench/tools/provision.py clone   --target bench/targets/<id> --out <dir> [--cache-root DIR]
    python3 bench/tools/provision.py cache   --target bench/targets/<id> [--cache-root DIR]
    python3 bench/tools/provision.py prepare --target bench/targets/<id> --out <dir> [--cache-root DIR]
    python3 bench/tools/provision.py smoke   --target bench/targets/<id> [--out smoke.json] [--cache-root DIR]
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
clone, which is what a runner does before dispatch.

The dependency cache is described by ``provisioning.cache`` in ``target.json``: ``kind`` (a
label), ``build`` (commands run once, online, in a scratch clone at the head, to populate
``<cache-root>/caches/<id>``), ``post_clone`` (commands run offline in every attempt clone after
cloning, which must leave the tracked tree clean), ``env`` (variables exported for build,
post-clone and smoke commands), and ``smoke`` (named commands run in a prepared clone at the head).
Commands run through ``sh -c`` with the placeholders ``{cache}`` (the target's cache directory),
``{clone}``, ``{work}`` (a scratch directory outside the clone) and ``{cache_root}`` substituted.
Whether a post-clone command is offline is the command's own business (``--offline``,
``GOPROXY=off``); the tool does not cut the network.

``cache`` runs the build commands, archives the cache directory to
``<cache-root>/archives/<id>.tar.gz``, records the archive's SHA-256 in
``<cache-root>/caches/<id>.json`` and prints the ``dependency_identity`` entry to paste into
``target.json``. ``prepare`` clones and runs the post-clone commands, printing the outcome as JSON.
``smoke`` prepares a scratch clone, runs the smoke commands and writes a ``smoke.json``
(``source: measured``) with the platform, the provisioning duration, every check's exit code and
duration, and the existing file's ``mirror`` block carried over. A non-zero smoke check is an
observation, not a failure; a post-clone step that fails or dirties the tree is a failure.

The cache root defaults to ``~/.t3/bench-cache``. Nothing under it enters the repository.

Exit codes: 0 built, verified or written; 1 a check failed, one line per failure on stdout (a
failed ``mirror`` or ``cache`` build leaves nothing behind); 2 an input cannot be read, a pinned
revision is missing from the staging clone, or a git command failed, with the command on stderr.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform as platform_module
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diff_identity  # noqa: E402

DEFAULT_CACHE_ROOT = os.path.join(os.path.expanduser("~"), ".t3", "bench-cache")
EMPTY_CACHE = {"kind": "none", "build": [], "post_clone": [], "env": {}, "smoke": []}


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


def cache_config(target: dict) -> dict:
    cfg = dict(EMPTY_CACHE)
    cfg.update(target.get("provisioning", {}).get("cache") or {})
    return cfg


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


def cache_path(cache_root: str, target: dict) -> str:
    return os.path.join(cache_root, "caches", target["id"])


def make_clone(target: dict, cache_root: str, out: str) -> list:
    """Clone the mirror into ``out`` with the attempt layout; return check failures (the clone is
    removed when any fail)."""
    path = mirror_path(cache_root, target)
    if not os.path.isdir(path):
        raise ProvisionError(f"no mirror at {path}")
    if os.path.exists(out):
        raise ProvisionError(f"clone target exists: {out} (attempt directories are never reused)")
    base = target["local_base_branch"]
    git("clone", "-q", path, out)
    git("-C", out, "checkout", "-q", "--detach", target["head"])
    git("-C", out, "branch", "-q", "-f", base, target["merge_base"])
    git("-C", out, "checkout", "-q", "-B", "review-head", target["head"])
    failures = []
    if git("-C", out, "rev-parse", "HEAD").strip() != target["head"]:
        failures.append("head mismatch after checkout")
    failures.extend(checks(out, target, base, "review-head", date_check=False))
    if failures:
        shutil.rmtree(out)
    return failures


def render(text: str, subs: dict) -> str:
    for key, value in subs.items():
        text = text.replace("{" + key + "}", value)
    return text


def shell(command: str, cwd: str, env: dict) -> tuple:
    """Run one command through sh -c; return (exit_code, duration_seconds, combined output, stdout)."""
    started = time.monotonic()
    try:
        done = subprocess.run(["sh", "-c", command], cwd=cwd, env=env, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    except FileNotFoundError as error:
        raise ProvisionError(f"cannot run sh: {error}") from error
    return done.returncode, round(time.monotonic() - started, 2), (done.stdout or "") + (done.stderr or ""), done.stdout or ""


def command_env(cfg: dict, subs: dict) -> dict:
    env = dict(os.environ)
    for key, value in cfg.get("env", {}).items():
        env[key] = render(value, subs)
    return env


def substitutions(target: dict, cache_root: str, clone: str, work: str) -> dict:
    return {"cache": cache_path(cache_root, target), "clone": clone, "work": work, "cache_root": cache_root}


def platform_record() -> str:
    parts = [f"{platform_module.system()} {platform_module.release()} {platform_module.machine()}"]
    for probe in (["python3", "--version"], ["node", "--version"], ["go", "version"], ["zsh", "--version"], ["git", "--version"]):
        try:
            out = subprocess.run(probe, capture_output=True, text=True, encoding="utf-8").stdout.strip()
        except (FileNotFoundError, OSError):
            continue
        if out:
            parts.append(out.replace("go version go", "go ").replace("version ", "").splitlines()[0])
    return "; ".join(parts)


def tail(output: str, lines: int = 20) -> str:
    kept = [line for line in output.splitlines() if line.strip()]
    return "\n".join(kept[-lines:])


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    out = os.path.abspath(args.out)
    failures = make_clone(target, args.cache_root, out)
    for line in failures:
        print(line)
    if failures:
        return 1
    print(f"clone {out}: review-head checked out at {target['head'][:12]}, {target['local_base_branch']} at {target['merge_base'][:12]}")
    return 0


def cmd_cache(args) -> int:
    target = load_target(args.target)
    cfg = cache_config(target)
    cache = cache_path(args.cache_root, target)
    scratch = os.path.join(args.cache_root, "scratch", target["id"] + "-cache")
    work = scratch + "-work"
    for path in (cache, scratch, work):
        if os.path.exists(path):
            shutil.rmtree(path)
    os.makedirs(cache)
    os.makedirs(work)
    failures = make_clone(target, args.cache_root, scratch)
    if failures:
        for line in failures:
            print(line)
        shutil.rmtree(cache)
        return 1
    subs = substitutions(target, args.cache_root, scratch, work)
    env = command_env(cfg, subs)
    steps = []
    started = now()
    try:
        for command in cfg["build"]:
            rendered = render(command, subs)
            code, duration, output, _stdout = shell(rendered, scratch, env)
            steps.append({"command": command, "exit_code": code, "duration_seconds": duration})
            if code != 0:
                print(f"build step failed (exit {code}): {rendered}")
                print(tail(output))
                shutil.rmtree(cache)
                return 1
        record = {"target": target["id"], "kind": cfg["kind"], "built_at": started, "finished_at": now(),
                  "platform": platform_record(), "cache": cache, "build": steps, "archive": None}
        if cfg["build"]:
            archives = os.path.join(args.cache_root, "archives")
            os.makedirs(archives, exist_ok=True)
            archive = os.path.join(archives, target["id"] + ".tar.gz")
            code, duration, output, _stdout = shell(f"tar -C {os.path.dirname(cache)!s} -czf {archive!s} {target['id']}", scratch, env)
            if code != 0:
                print(f"archive failed (exit {code})")
                print(tail(output))
                shutil.rmtree(cache)
                return 1
            record["archive"] = {"path": archive, "sha256": sha256_file(archive), "bytes": os.path.getsize(archive),
                                 "duration_seconds": duration}
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
        shutil.rmtree(work, ignore_errors=True)
    Path(os.path.dirname(cache), target["id"] + ".json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if record["archive"]:
        entry = {"name": f"cache archive ({cfg['kind']})", "sha256": record["archive"]["sha256"],
                 "location": record["archive"]["path"].replace(os.path.expanduser("~"), "~", 1)}
        print(f"cache {cache}: {len(steps)} build step(s), archive {record['archive']['bytes']} bytes")
        print("dependency_identity entry: " + json.dumps(entry))
    else:
        print(f"cache {cache}: nothing to build (kind {cfg['kind']})")
    return 0


def prepare(target: dict, cache_root: str, out: str) -> dict:
    """Clone and run the post-clone steps; return the provisioning record with a ``failures`` list."""
    cfg = cache_config(target)
    failures = make_clone(target, cache_root, out)
    record = {"recipe": "; ".join(cfg["post_clone"]) or "none", "duration_seconds": 0.0, "tree_clean_after": None,
              "steps": [], "failures": failures}
    if failures:
        return record
    work = out + "-work"
    os.makedirs(work, exist_ok=True)
    subs = substitutions(target, cache_root, out, work)
    env = command_env(cfg, subs)
    total = 0.0
    for command in cfg["post_clone"]:
        code, duration, output, _stdout = shell(render(command, subs), out, env)
        total += duration
        record["steps"].append({"command": command, "exit_code": code, "duration_seconds": duration})
        if code != 0:
            record["failures"].append(f"post-clone step failed (exit {code}): {command}\n{tail(output, 10)}")
            break
    record["duration_seconds"] = round(total, 2)
    if not record["failures"]:
        dirty = git("-C", out, "status", "--porcelain").strip()
        record["tree_clean_after"] = not dirty
        if dirty:
            record["failures"].append("post-clone provisioning dirtied the tracked tree:\n" + "\n".join(dirty.splitlines()[:5]))
    return record


def cmd_prepare(args) -> int:
    target = load_target(args.target)
    record = prepare(target, args.cache_root, os.path.abspath(args.out))
    print(json.dumps(record, indent=2))
    return 1 if record["failures"] else 0


def cmd_smoke(args) -> int:
    target = load_target(args.target)
    cfg = cache_config(target)
    out = os.path.abspath(args.out) if args.out else os.path.join(os.path.abspath(args.target), "smoke.json")
    scratch = os.path.join(args.cache_root, "scratch", target["id"] + "-smoke")
    for path in (scratch, scratch + "-work"):
        if os.path.exists(path):
            shutil.rmtree(path)
    os.makedirs(os.path.dirname(scratch), exist_ok=True)
    measured_at = now()
    try:
        record = prepare(target, args.cache_root, scratch)
        if record["failures"]:
            for line in record["failures"]:
                print(line)
            return 1
        subs = substitutions(target, args.cache_root, scratch, scratch + "-work")
        env = command_env(cfg, subs)
        checks_out = []
        for item in cfg["smoke"]:
            code, duration, output, stdout = shell(render(item["command"], subs), scratch, env)
            # The result line of a test runner is on stdout; stderr carries warnings that would hide it.
            last = (tail(stdout, 1) or tail(output, 1))[:200]
            checks_out.append({"name": item["name"], "command": item["command"], "revision": item.get("revision", "head"),
                               "exit_code": code, "duration_seconds": duration, "summary": last or "(no output)"})
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
        shutil.rmtree(scratch + "-work", ignore_errors=True)
    previous = {}
    if os.path.exists(out):
        try:
            previous = json.loads(Path(out).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
    smoke = {
        "schema_version": 1, "target": target["id"], "source": "measured", "measured_at": measured_at,
        "platform": platform_record(),
        "provisioning": {"recipe": record["recipe"], "duration_seconds": record["duration_seconds"],
                         "tree_clean_after": record["tree_clean_after"]},
        "checks": checks_out,
        "notes": [f"Measured by provision.py smoke on this machine; cache kind {cfg['kind']}."],
    }
    if previous.get("source") == "recorded" and previous.get("source_document"):
        smoke["notes"].append(f"The earlier recorded figures were transcribed from {previous['source_document']}.")
    if previous.get("mirror"):
        smoke["mirror"] = previous["mirror"]
    Path(out).write_text(json.dumps(smoke, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    failed = [c["name"] for c in checks_out if c["exit_code"] != 0]
    print(f"smoke {out}: provisioning {record['duration_seconds']}s, {len(checks_out)} check(s)"
          + (f", non-zero: {', '.join(failed)}" if failed else ""))
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
        # No cache configured: cache builds nothing, smoke still measures provisioning.
        done = run("cache", "--target", str(target_dir))
        assert done.returncode == 0 and "nothing to build" in done.stdout, done
        # A cache with build, post-clone, env and smoke commands using every placeholder.
        with_cache = dict(target, provisioning={"cache": {
            "kind": "test",
            "build": ["mkdir -p {cache}/store && printf hi > {cache}/store/f", "test -f {clone}/f.txt"],
            "post_clone": ["test -f {cache}/store/f && printf x > {work}/marker && test \"$BENCH_TEST_ENV\" = {cache}/store"],
            "env": {"BENCH_TEST_ENV": "{cache}/store"},
            "smoke": [{"name": "read", "command": "cat $BENCH_TEST_ENV/f", "revision": "head"},
                      {"name": "fails", "command": "echo nope; exit 3", "revision": "head"}]}})
        (target_dir / "target.json").write_text(json.dumps(with_cache), encoding="utf-8")
        done = run("cache", "--target", str(target_dir))
        assert done.returncode == 0 and "dependency_identity entry" in done.stdout, done
        archive = Path(cache, "archives", "t-1.tar.gz")
        assert archive.is_file() and Path(cache, "caches", "t-1", "store", "f").read_text() == "hi"
        rec = json.loads(Path(cache, "caches", "t-1.json").read_text(encoding="utf-8"))
        assert rec["archive"]["sha256"] == sha256_file(str(archive)) and len(rec["build"]) == 2, rec
        assert not Path(cache, "scratch", "t-1-cache").exists(), "the scratch clone must be removed"
        prepared = str(Path(temp, "prepared"))
        done = run("prepare", "--target", str(target_dir), "--out", prepared)
        assert done.returncode == 0 and json.loads(done.stdout)["tree_clean_after"] is True, done
        assert Path(prepared + "-work", "marker").is_file()
        smoke_out = str(Path(temp, "smoke.json"))
        Path(smoke_out).write_text(json.dumps({"source": "recorded", "source_document": "old.md", "mirror": {"built_at": "x"}}),
                                   encoding="utf-8")
        done = run("smoke", "--target", str(target_dir), "--out", smoke_out)
        assert done.returncode == 0 and "non-zero: fails" in done.stdout, done
        smoke = json.loads(Path(smoke_out).read_text(encoding="utf-8"))
        assert smoke["source"] == "measured" and smoke["provisioning"]["tree_clean_after"] is True
        assert [c["exit_code"] for c in smoke["checks"]] == [0, 3] and smoke["checks"][0]["summary"] == "hi", smoke
        assert smoke["mirror"] == {"built_at": "x"} and any("old.md" in n for n in smoke["notes"])
        assert not Path(cache, "scratch", "t-1-smoke").exists()
        # A failing build leaves no cache; a dirtying post-clone step fails prepare and smoke.
        bad = dict(with_cache)
        bad["provisioning"] = {"cache": dict(with_cache["provisioning"]["cache"], build=["exit 7"])}
        (target_dir / "target.json").write_text(json.dumps(bad), encoding="utf-8")
        done = run("cache", "--target", str(target_dir))
        assert done.returncode == 1 and "exit 7" in done.stdout and not Path(cache, "caches", "t-1").exists(), done
        dirty = dict(with_cache)
        dirty["provisioning"] = {"cache": dict(with_cache["provisioning"]["cache"], post_clone=["echo dirty >> f.txt"])}
        (target_dir / "target.json").write_text(json.dumps(dirty), encoding="utf-8")
        done = run("smoke", "--target", str(target_dir), "--out", smoke_out)
        assert done.returncode == 1 and "dirtied" in done.stdout, done
        # A wrong diff identity is a check failure, and a failed build leaves no mirror.
        (target_dir / "target.json").write_text(json.dumps(dict(target, diff_manifest_sha256="0" * 64)), encoding="utf-8")
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
    for name in ("mirror", "check", "clone", "cache", "prepare", "smoke"):
        p = sub.add_parser(name)
        p.add_argument("--target", required=True, help="target directory holding target.json")
        p.add_argument("--cache-root", default=DEFAULT_CACHE_ROOT)
        if name == "mirror":
            p.add_argument("--staging", required=True, help="full clone holding the head and the merge-base")
        if name in ("clone", "prepare"):
            p.add_argument("--out", required=True, help="new directory for the working clone")
        if name == "smoke":
            p.add_argument("--out", help="smoke.json to write (default: <target>/smoke.json)")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.command:
        parser.error("give a subcommand or --self-test")
    handlers = {"mirror": cmd_mirror, "check": cmd_check, "clone": cmd_clone, "cache": cmd_cache,
                "prepare": cmd_prepare, "smoke": cmd_smoke}
    try:
        return handlers[args.command](args)
    except ProvisionError as error:
        print(f"provision.py: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
