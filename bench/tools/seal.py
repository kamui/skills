#!/usr/bin/env python3
"""Seal evaluator-only truth as ciphertext, and open it again with a hash check.

Usage::

    python3 bench/tools/seal.py keygen [--key PATH]
    python3 bench/tools/seal.py seal <plaintext> <out.enc> [--key PATH]
    python3 bench/tools/seal.py open <in.enc> <plaintext> --sha256 <hex> [--key PATH]
    python3 bench/tools/seal.py --self-test

A fresh target's register, its hunt report and its adjudication stay unreadable to reviewers
until scoring (design §5), so they are committed only as ciphertext. Encryption is
``openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt`` under one random 256-bit key, the #148
precedent. The key lives at ``~/.config/bench/seal.key`` (mode 0600 in a 0700 directory),
outside the repository and every attempt directory; the read audit flags any reviewer command
that touches it, and a separate Unix user would make it unreachable rather than detectable.

``keygen`` writes a key only if none exists. ``seal`` prints the plaintext's SHA-256, which the
caller records beside the ciphertext (``target.json`` ``sealed``, or a ``SHA256SUMS`` file) so a
reveal is checkable without trusting the ciphertext. ``open`` decrypts to a temporary sibling of
the plaintext path and moves it into place only when its SHA-256 matches ``--sha256``; a mismatch
or a failed decryption removes the sibling and leaves any existing file at that path untouched.

Exit codes: 0 done; 1 ``open`` produced a plaintext whose hash does not match; 2 a file or the key
cannot be read or written, or ``openssl`` failed.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile

DEFAULT_KEY = Path.home() / ".config" / "bench" / "seal.key"
CIPHER = ["-aes-256-cbc", "-pbkdf2", "-iter", "200000"]


class SealError(Exception):
    """A file, the key or openssl failed; exit code 2."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def keygen(key: Path) -> bool:
    if key.exists():
        return False
    key.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(key.parent, 0o700)
    descriptor = os.open(key, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as handle:
        handle.write(secrets.token_hex(32) + "\n")
    return True


def openssl(key: Path, source: Path, target: Path, decrypt: bool) -> None:
    if not key.is_file():
        raise SealError(f"no key at {key}; run keygen")
    command = ["openssl", "enc", *(["-d"] if decrypt else ["-salt"]), *CIPHER,
               "-pass", f"file:{key}", "-in", str(source), "-out", str(target)]
    try:
        subprocess.run(command, check=True, capture_output=True)
    except FileNotFoundError as error:
        raise SealError(f"cannot run openssl: {error}") from error
    except subprocess.CalledProcessError as error:
        raise SealError(f"openssl failed on {source}: {error.stderr.decode('utf-8', 'replace').strip()}") from error


def seal(key: Path, plaintext: Path, out: Path) -> str:
    if not plaintext.is_file():
        raise SealError(f"cannot read {plaintext}")
    digest = sha256(plaintext)
    openssl(key, plaintext, out, decrypt=False)
    return digest


def open_sealed(key: Path, sealed: Path, out: Path, expected: str) -> bool:
    if not sealed.is_file():
        raise SealError(f"cannot read {sealed}")
    # openssl writes before it can tell the key or ciphertext is wrong, so decrypt beside `out`
    descriptor, name = tempfile.mkstemp(dir=out.parent, prefix=f".{out.name}.", suffix=".tmp")
    os.close(descriptor)
    partial = Path(name)
    try:
        openssl(key, sealed, partial, decrypt=True)
        if sha256(partial) != expected:
            return False
        os.replace(partial, out)
        return True
    finally:
        partial.unlink(missing_ok=True)


def self_test() -> int:
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        key = base / "keys" / "seal.key"
        assert keygen(key) and not keygen(key)
        assert (key.stat().st_mode & 0o777) == 0o600 and (key.parent.stat().st_mode & 0o777) == 0o700
        plain = base / "register.v1.json"
        plain.write_text('{"defects": [{"id": "GT-x1"}]}\n', encoding="utf-8")
        digest = seal(key, plain, base / "register.v1.json.enc")
        assert b"GT-x1" not in (base / "register.v1.json.enc").read_bytes()
        assert open_sealed(key, base / "register.v1.json.enc", base / "opened.json", digest)
        assert (base / "opened.json").read_bytes() == plain.read_bytes()
        assert not open_sealed(key, base / "register.v1.json.enc", base / "bad.json", "0" * 64)
        assert not (base / "bad.json").exists()
        other = base / "other.key"
        other.write_text(secrets.token_hex(32) + "\n", encoding="utf-8")
        try:
            open_sealed(other, base / "register.v1.json.enc", base / "wrong.json", digest)
        except SealError:
            pass
        else:
            raise AssertionError("a wrong key decrypted")
        assert not (base / "wrong.json").exists()
        try:  # an earlier reveal survives a failed open onto it
            open_sealed(other, base / "register.v1.json.enc", base / "opened.json", digest)
        except SealError:
            pass
        else:
            raise AssertionError("a wrong key decrypted")
        assert not open_sealed(key, base / "register.v1.json.enc", base / "opened.json", "0" * 64)
        assert (base / "opened.json").read_bytes() == plain.read_bytes()
        assert not list(base.glob(".*.tmp"))
        run = subprocess.run([sys.executable, __file__, "seal", str(plain), str(base / "cli.enc"), "--key", str(key)],
                             capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 0 and run.stdout.strip() == digest, run
        run = subprocess.run([sys.executable, __file__, "open", str(base / "cli.enc"), str(base / "cli.json"),
                              "--sha256", "f" * 64, "--key", str(key)], capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 1 and not (base / "cli.json").exists(), run
        run = subprocess.run([sys.executable, __file__, "seal", str(base / "missing"), str(base / "x.enc"), "--key", str(key)],
                             capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 2, run
    print("self-test ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    for name in ("keygen", "seal", "open"):
        command = sub.add_parser(name)
        command.add_argument("--key", type=Path, default=DEFAULT_KEY)
        if name != "keygen":
            command.add_argument("source", type=Path)
            command.add_argument("out", type=Path)
        if name == "open":
            command.add_argument("--sha256", required=True)
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        if args.command == "keygen":
            print(f"{'wrote' if keygen(args.key) else 'kept existing'} {args.key}")
        elif args.command == "seal":
            print(seal(args.key, args.source, args.out))
        elif args.command == "open":
            if not open_sealed(args.key, args.source, args.out, args.sha256):
                print(f"{args.source}: plaintext SHA-256 does not match {args.sha256}; {args.out} not written")
                return 1
            print(f"{args.out} ok")
        else:
            parser.error("give keygen, seal, open or --self-test")
    except (OSError, SealError) as error:
        print(f"seal.py: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
