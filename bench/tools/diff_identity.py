#!/usr/bin/env python3
"""Compute the diff identity of a base..head pair: the changed-file manifest and its SHA-256.

Usage::

    python3 bench/tools/diff_identity.py <repo> <base> <head> [--expect <sha256>] [--quiet]
    python3 bench/tools/diff_identity.py --self-test

The manifest is the canonical text a target's ``diff_manifest_sha256`` is computed from, so a
rebuilt mirror or a fresh clone can be checked against the frozen diff identity without trusting
branch names. Definition: ``git diff-tree -r --no-renames -z <base> <head>`` gives one record per
changed path with the base and head blob ids; records are sorted by path and rendered as
``<status>\\t<path>\\t<base-blob>\\t<head-blob>\\n`` (UTF-8, paths as git reports them, one
trailing newline). The SHA-256 is over those bytes. An empty diff has the hash of the empty
string, which is a valid identity for a no-op pair and is reported as such.

Output: the manifest lines on stdout followed by ``sha256 <hex>``; ``--quiet`` prints only the
hex. With ``--expect``, exit 1 and print both hashes when they differ.

Exit codes: 0 computed (and matched, if expected); 1 the identity does not match ``--expect``;
2 the repository or a revision cannot be read, with the failing command on stderr.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile


class RepoError(Exception):
    """A git command failed; exit code 2."""


def git(repo: str, *args: str, binary: bool = False):
    command = ["git", "-C", repo, *args]
    try:
        done = subprocess.run(command, check=True, capture_output=True, text=not binary,
                              **({} if binary else {"encoding": "utf-8"}))
    except FileNotFoundError as error:
        raise RepoError(f"cannot run git: {error}") from error
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.decode("utf-8", "replace") if binary else (error.stderr or "")
        raise RepoError(f"command failed: {' '.join(command)}\n{stderr.strip()}") from error
    return done.stdout


def manifest(repo: str, base: str, head: str) -> list:
    """Return the sorted list of (status, path, base_blob, head_blob) tuples."""
    raw = git(repo, "diff-tree", "-r", "--no-renames", "-z", base, head, binary=True)
    fields = raw.split(b"\0")
    rows = []
    index = 0
    while index < len(fields) and fields[index]:
        meta = fields[index].decode("utf-8")
        if not meta.startswith(":"):
            raise RepoError(f"unexpected diff-tree record {meta!r}")
        _old_mode, _new_mode, old_blob, new_blob, status = meta[1:].split(" ")
        path = fields[index + 1].decode("utf-8", "surrogateescape")
        rows.append((status, path, old_blob, new_blob))
        index += 2
    rows.sort(key=lambda row: row[1])
    return rows


def render(rows: list) -> bytes:
    return "".join(f"{status}\t{path}\t{old}\t{new}\n" for status, path, old, new in rows).encode("utf-8", "surrogateescape")


def identity(repo: str, base: str, head: str) -> tuple:
    rows = manifest(repo, base, head)
    text = render(rows)
    return rows, hashlib.sha256(text).hexdigest()


def self_test() -> int:
    with tempfile.TemporaryDirectory() as temp:
        repo = str(Path(temp, "r"))
        subprocess.run(["git", "init", "-q", repo], check=True)
        env_args = ["-c", "user.name=t", "-c", "user.email=t@example.com"]

        def commit(message: str) -> str:
            subprocess.run(["git", "-C", repo, "add", "-A"], check=True)
            subprocess.run(["git", *env_args, "-C", repo, "commit", "-q", "-m", message], check=True)
            return subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], check=True, capture_output=True,
                                  text=True, encoding="utf-8").stdout.strip()

        Path(repo, "b.txt").write_text("base\n", encoding="utf-8")
        Path(repo, "a.txt").write_text("keep\n", encoding="utf-8")
        base = commit("base")
        Path(repo, "b.txt").write_text("head\n", encoding="utf-8")
        Path(repo, "z.txt").write_text("new\n", encoding="utf-8")
        Path(repo, "a.txt").unlink()
        head = commit("head")
        rows, digest = identity(repo, base, head)
        assert [row[0] for row in rows] == ["D", "M", "A"], rows
        assert [row[1] for row in rows] == ["a.txt", "b.txt", "z.txt"], rows
        assert rows[2][2] == "0" * 40 and rows[0][3] == "0" * 40, rows
        assert len(digest) == 64
        rows_again, digest_again = identity(repo, base, head)
        assert digest_again == digest and rows_again == rows, "identity must be deterministic"
        _rows, same = identity(repo, head, head)
        assert same == hashlib.sha256(b"").hexdigest(), "an empty diff hashes the empty manifest"
        try:
            identity(repo, base, "nonexistent")
        except RepoError:
            pass
        else:
            raise AssertionError("a bad revision must raise")
        here = Path(__file__).resolve()
        run = subprocess.run([sys.executable, str(here), repo, base, head, "--expect", "0" * 64], capture_output=True,
                             text=True, encoding="utf-8")
        assert run.returncode == 1 and "expected" in run.stdout, (run.returncode, run.stdout)
        run = subprocess.run([sys.executable, str(here), repo, base, head, "--expect", digest, "--quiet"],
                             capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 0 and run.stdout.strip() == digest, (run.returncode, run.stdout)
    print("self-test ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", nargs="?")
    parser.add_argument("base", nargs="?")
    parser.add_argument("head", nargs="?")
    parser.add_argument("--expect", help="SHA-256 the identity must equal")
    parser.add_argument("--quiet", action="store_true", help="print only the hex digest")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not (args.repo and args.base and args.head):
        parser.error("give a repository, a base revision and a head revision")
    try:
        rows, digest = identity(args.repo, args.base, args.head)
    except RepoError as error:
        print(f"diff_identity.py: {error}", file=sys.stderr)
        return 2
    if args.quiet:
        print(digest)
    else:
        sys.stdout.write(render(rows).decode("utf-8", "surrogateescape"))
        print(f"sha256 {digest}")
    if args.expect and args.expect != digest:
        print(f"diff identity mismatch: expected {args.expect}, computed {digest}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
