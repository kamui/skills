#!/usr/bin/env python3
"""Replay #341's two archived verifier batches under the #344 return transports, offline.

Usage: python3 docs/research/review-code-verifier-transport-2026-09-23/demo.py [--output demo.json]

For each baseline cell with a verifier batch (publishable, required-verification) it:

- reads the root transcript for the primary's reads of the return reference, the characters of the
  worker hand-back that entered the primary's context, and the characters of the raw return the
  primary then wrote to raw-return.json;
- rebuilds the archived projected input with this checkout's builder, once inline and once with
  --return-file, and records each brief's size beside the archived brief;
- plays the worker: the archived raw return, with its manifest hash replaced by the rebuilt bundle's,
  is created exclusively at the assigned path (file) or saved as the primary would (inline);
- accounts both with this checkout's helper and compares accounted/withheld IDs, violations,
  completeness, and the return less its manifest hash, with each other and with the archived report.

It also measures the primary's return instructions (verifier-handoff.md plus verifier-return.md at
BASE, handoff alone here). No model runs.

Exit 0 when both transports account every cell identically to the archive; 1 otherwise; 2 when an
input cannot be read or a helper cannot run.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
SAVINGS = ROOT / "docs/research/review-code-artifact-savings-2026-09-22"
SCRIPTS = ROOT / "skills/review-code/scripts"
BASE = "b5f3b04"  # origin/main when #344 began: the merge of #343
CELLS = {"publishable": "verify-initial", "required-verification": "bundle-initial"}
COMPARED = ("accounted", "withheld", "violations", "structurally_complete")
SHOWN = "/tmp/rcs344"  # the scratch root as recorded, so the rows do not depend on it


def transcript(cell: str) -> dict:
    """What the baseline primary read, received from its worker, and wrote as the raw return."""
    agents, row = set(), {"return_reference_reads": 0, "handoff_reads": 0,
                          "worker_handback_chars": 0, "primary_written_return_chars": 0}
    with gzip.open(SAVINGS / "baseline" / cell / "transcript.jsonl.gz", "rt", encoding="utf-8") as lines:
        for line in lines:
            content = (json.loads(line).get("message") or {}).get("content")
            for block in content if isinstance(content, list) else []:
                if block.get("type") == "tool_use":
                    name, data = block["name"], block["input"]
                    if name == "Agent":
                        agents.add(block["id"])
                    elif name == "Read" and data.get("file_path", "").endswith("references/verifier-return.md"):
                        row["return_reference_reads"] += 1
                    elif name == "Read" and data.get("file_path", "").endswith("references/verifier-handoff.md"):
                        row["handoff_reads"] += 1
                    elif name == "Write" and data.get("file_path", "").endswith("/raw-return.json"):
                        row["primary_written_return_chars"] += len(data["content"])
                elif block.get("type") == "tool_result" and block.get("tool_use_id") in agents:
                    parts = block["content"] if isinstance(block["content"], list) else [{"text": block["content"]}]
                    row["worker_handback_chars"] += sum(len(part.get("text", "")) for part in parts)
    return row


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding="utf-8")


def load(text: str) -> tuple[int, int]:
    return len(text.encode("utf-8")), len(text.split())


def replay(scratch: Path, cell: str) -> dict:
    archived = SAVINGS / "baseline" / cell / "work" / "private" / CELLS[cell]
    raw = (archived / "raw-return.json").read_bytes()
    old_hash = json.loads((archived / "accounting.json").read_text(encoding="utf-8"))["manifest_sha256"]
    baseline_report = json.loads((archived / "accounting.json").read_text(encoding="utf-8"))
    row = {"cell": cell, "archived_brief_bytes": (archived / "brief.md").stat().st_size, "raw_return_bytes": len(raw)}
    reports = {}
    for transport in ("inline", "file"):
        work = scratch / cell / transport
        work.mkdir(parents=True)
        bundle, assigned = work / "bundle", work / "returns" / "raw-return.json"
        args = [str(SCRIPTS / "build_verifier_prompt.py"), str(archived / "input.json"), "--output", str(bundle)]
        if transport == "file":
            assigned.parent.mkdir()
            args += ["--return-file", str(assigned)]
        built = run(*args)
        if built.returncode != 0:
            raise OSError(f"{cell} {transport} build exited {built.returncode}: {built.stdout}{built.stderr}")
        new_hash = hashlib.sha256((bundle / "manifest.json").read_bytes()).hexdigest()
        body = raw.replace(old_hash.encode(), new_hash.encode())
        if transport == "file":
            with open(assigned, "xb") as handle:  # what the worker does
                handle.write(body)
            given = str(assigned)
            reply = json.dumps({"return_file": given.replace(str(scratch), SHOWN), "status": "complete"})
        else:
            given, reply = str(work / "raw-return.json"), body.decode("utf-8")
            Path(given).write_bytes(body)  # what the primary does
        accounted = run(str(SCRIPTS / "account_verifier_return.py"), "--bundle", str(bundle),
                        "--output", str(work / "accounting.json"), given)
        report = json.loads((work / "accounting.json").read_text(encoding="utf-8").replace(str(scratch), SHOWN))
        report["return"].pop("manifest_sha256")
        reports[transport] = report
        row[transport] = {"account_exit": accounted.returncode, "brief_bytes": (bundle / "brief.md").stat().st_size,
                          "worker_reply_chars": len(reply),
                          "primary_written_return_chars": 0 if transport == "file" else len(body.decode("utf-8")),
                          "transport": report.get("transport")}
    baseline_report["return"].pop("manifest_sha256")
    row["transports_identical"] = all(reports["inline"][k] == reports["file"][k] for k in COMPARED + ("return",))
    row["matches_archived_accounting"] = all(reports["file"][k] == baseline_report[k] for k in COMPARED + ("return",))
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", help="write the rows as JSON here")
    args = parser.parse_args()
    try:
        refs = ROOT / "skills/review-code/references"
        before = "".join(subprocess.run(["git", "show", f"{BASE}:skills/review-code/references/{name}"], cwd=ROOT,
                                        check=True, capture_output=True, text=True, encoding="utf-8").stdout
                         for name in ("verifier-handoff.md", "verifier-return.md"))
        after = (refs / "verifier-handoff.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="rcs344-") as scratch:
            rows = [dict(replay(Path(scratch), cell), baseline_transcript=transcript(cell)) for cell in CELLS]
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"demo: cannot read an input or run a helper: {error}", file=sys.stderr)
        return 2
    result = {"primary_return_instructions": {"base": BASE, "before_bytes_words": load(before),
                                              "after_bytes_words": load(after)},
              "cells": rows}
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    ok = all(row["inline"]["account_exit"] == 0 and row["file"]["account_exit"] == 0
             and row["transports_identical"] and row["matches_archived_accounting"] for row in rows)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
