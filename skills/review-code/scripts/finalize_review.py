#!/usr/bin/env python3
"""Compose, validate, and write review-code's step-5 artifacts in one call.

Usage:
    python3 scripts/finalize_review.py --store STORE PRIVATE_DIR
    python3 scripts/finalize_review.py --profile implementation-gate --store STORE PRIVATE_DIR

Reads PRIVATE_DIR/composition.json. Under the default `publishable` profile it
runs three stages in order, each writing one artifact in PRIVATE_DIR, and then
prints `fragments.md`:

    compose     compose_review.py --store STORE composition.json  -> payload.json
    emit-batch  validate_review.py --emit-batch < payload.json    -> batch.json
    render      validate_review.py --render < payload.json        -> fragments.md

Under `implementation-gate` it creates PRIVATE_DIR/addenda, where continuations
append, runs one stage, and prints `record PRIVATE_DIR/record.json`:

    record      compose_review.py --profile implementation-gate --store STORE
                composition.json                                  -> record.json

Artifacts from an earlier run are removed first. Each stage writes
`<artifact>.part`, renamed only on exit 0, so no later stage or reader sees a
stale or partial file. The first non-zero stage stops the run: it prints
`<stage> failed with exit <status>; later stages did not run:` followed by the
stage's stdout, where the scripts print violations, and its stderr, removes
the partial artifact, and exits with that status. Stages run as
`python3 <script>`, the interpreter the step itself names.

Exit codes:
    0  every stage passed
    2  the addenda directory cannot be created, or a stage cannot be started
    *  otherwise, the failing stage's own status
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def stage(name: str, artifact: Path, command: list[str], stdin: bytes | None = None) -> None:
    part = artifact.with_name(artifact.name + ".part")
    try:
        result = subprocess.run(["python3", *command], input=stdin, capture_output=True)
    except OSError as error:
        print(f"finalize_review: cannot start {name}: {error}", file=sys.stderr)
        raise SystemExit(2)
    if result.returncode != 0:
        sys.stdout.buffer.write(f"{name} failed with exit {result.returncode}; later stages did not run:\n".encode("utf-8"))
        sys.stdout.buffer.write(result.stdout + result.stderr)
        part.unlink(missing_ok=True)
        raise SystemExit(result.returncode)
    part.write_bytes(result.stdout)
    os.replace(part, artifact)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--profile", choices=("publishable", "implementation-gate"), default="publishable")
    parser.add_argument("--store", required=True, help="the step-2 review-context store")
    parser.add_argument("private_dir", help="directory holding composition.json")
    args = parser.parse_args()

    private = Path(args.private_dir)
    composition = str(private / "composition.json")
    compose = str(SCRIPTS / "compose_review.py")
    validate = str(SCRIPTS / "validate_review.py")

    if args.profile == "implementation-gate":
        record = private / "record.json"
        record.unlink(missing_ok=True)
        try:
            (private / "addenda").mkdir(parents=True, exist_ok=True)
        except OSError as error:
            print(f"finalize_review: cannot create {private / 'addenda'}: {error}", file=sys.stderr)
            return 2
        stage("record", record, [compose, "--profile", "implementation-gate", "--store", args.store, composition])
        print(f"record {record}")
        return 0

    payload, batch, fragments = private / "payload.json", private / "batch.json", private / "fragments.md"
    for artifact in (payload, batch, fragments):
        artifact.unlink(missing_ok=True)
    stage("compose", payload, [compose, "--store", args.store, composition])
    stage("emit-batch", batch, [validate, "--emit-batch"], payload.read_bytes())
    stage("render", fragments, [validate, "--render"], payload.read_bytes())
    sys.stdout.buffer.write(fragments.read_bytes())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
