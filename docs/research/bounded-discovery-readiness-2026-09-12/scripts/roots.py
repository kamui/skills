#!/usr/bin/env python3
"""Record actual cell roots outside the seal and check their removal at shutdown.

Usage: python3 scripts/roots.py record --out FILE --root DIRECTORY [--root ...]
       python3 scripts/roots.py check --record FILE
       python3 scripts/roots.py --self-test
Input: record writes exclusive UTF-8 JSON {recorded_at, roots: [absolute paths]}.
Check enumerates each root's parent, including hidden entries, and refuses any
surviving root or unreadable parent. It proves only the recorded roots absent;
process, container and ledger checks are still required before opening a seal.
Exit: 0 success, 1 surviving root/invalid record, 2 unreadable input or probe failure.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys


def record(destination, roots):
    paths = [Path(root).expanduser().resolve(strict=True) for root in roots]
    destination = Path(destination).resolve()
    if len(set(paths)) != len(paths) or not paths:
        raise ValueError("record at least one distinct cell root")
    for root in paths:
        if not root.is_dir() or root == root.parent:
            raise ValueError("each cell root must be a non-root directory")
        if destination == root or root in destination.parents:
            raise ValueError("retain the root record outside every cell root and its seal")
    with open(destination, "x", encoding="utf-8") as stream:
        json.dump({"recorded_at": datetime.now(timezone.utc).isoformat(),
                   "roots": [str(root) for root in paths]}, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def check(source):
    document = json.loads(Path(source).read_text(encoding="utf-8"))
    roots = document.get("roots")
    if not document.get("recorded_at") or not isinstance(roots, list) or not roots:
        raise ValueError("root record requires timestamp and nonempty roots")
    present = []
    for value in roots:
        if not isinstance(value, str):
            raise ValueError("root must be an absolute path")
        root = Path(value)
        if not root.is_absolute() or root == root.parent or ".." in root.parts:
            raise ValueError("root must be an absolute non-root path without traversal")
        # Enumerate the parent: a missing root is a successful absence probe,
        # whereas a missing/unreadable parent is an incomplete probe, never a pass.
        with os.scandir(root.parent) as entries:
            if any(entry.name == root.name for entry in entries):
                present.append(str(root))
    return {"probe_completed": True, "roots": roots, "present": present,
            "passed": not present}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", nargs="?", choices=("record", "check"))
    parser.add_argument("--root", action="append", default=[])
    parser.add_argument("--out")
    parser.add_argument("--record")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return subprocess.run([sys.executable, str(Path(__file__).with_name("test_roots.py"))]).returncode
    if args.operation == "record" and not (args.root and args.out):
        parser.error("record requires --root and --out")
    if args.operation == "check" and not args.record:
        parser.error("check requires --record")
    if not args.operation:
        parser.error("operation is required")
    try:
        if args.operation == "record":
            record(args.out, args.root)
            return 0
        result = check(args.record)
        print(json.dumps(result))
        return 0 if result["passed"] else 1
    except (ValueError, TypeError, AttributeError) as exc:
        print(str(exc))
        return 1
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
