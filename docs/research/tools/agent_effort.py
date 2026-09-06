#!/usr/bin/env python3
"""Report the model and effort observed on every assistant line of harness transcripts.

A Claude Code transcript (a session's ``<uuid>.jsonl`` or a sub-agent's ``agent-*.jsonl``)
carries ``message.model`` and a top-level ``effort`` on each assistant line. This script
counts both per transcript so a run's requested effort can be checked against what actually
ran, on the whole transcript rather than its first turns (a resumed agent can change either).

Usage::

    python3 docs/research/tools/agent_effort.py <transcript>... [--expect-model M] [--expect-effort E]
    python3 docs/research/tools/agent_effort.py --self-test

Exit codes: 0 when every transcript matches the expectations (or none were given); 1 when any
transcript has an assistant line whose model or effort differs from an expectation, with one
line per violation on stdout; 2 when a transcript cannot be read. Output is one line per
transcript: ``<name> lines=<n> models=<model×count,…> efforts=<effort×count,…>``. A transcript
with no assistant lines reports ``lines=0`` and never violates an expectation.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile


def scan(path: str) -> dict:
    models: dict = {}
    efforts: dict = {}
    n = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get("type") != "assistant":
                continue
            n += 1
            m = (o.get("message") or {}).get("model")
            e = o.get("effort")
            models[m] = models.get(m, 0) + 1
            efforts[e] = efforts.get(e, 0) + 1
    return {"lines": n, "models": models, "efforts": efforts}


def fmt(counts: dict) -> str:
    return ",".join(f"{k}×{v}" for k, v in sorted(counts.items(), key=lambda kv: str(kv[0]))) or "-"


def run(paths: list, expect_model: str | None, expect_effort: str | None) -> int:
    rc = 0
    for p in paths:
        try:
            r = scan(p)
        except OSError as exc:
            print(f"agent_effort: cannot read {p}: {exc}", file=sys.stderr)
            return 2
        print(f"{os.path.basename(p)} lines={r['lines']} models={fmt(r['models'])} efforts={fmt(r['efforts'])}")
        if expect_model and any(k != expect_model for k in r["models"]):
            print(f"{os.path.basename(p)}: model violation: expected {expect_model}, saw {fmt(r['models'])}")
            rc = 1
        if expect_effort and any(k != expect_effort for k in r["efforts"]):
            print(f"{os.path.basename(p)}: effort violation: expected {expect_effort}, saw {fmt(r['efforts'])}")
            rc = 1
    return rc


def self_test() -> int:
    import subprocess

    me = os.path.abspath(__file__)
    with tempfile.TemporaryDirectory() as d:
        ok = os.path.join(d, "agent-ok.jsonl")
        with open(ok, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "user", "message": {"content": "x"}}) + "\n")
            fh.write("not json\n")
            for _ in range(3):
                fh.write(json.dumps({"type": "assistant", "effort": "high", "message": {"model": "claude-sonnet-5", "content": []}}) + "\n")
        bad = os.path.join(d, "agent-bad.jsonl")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "assistant", "effort": "high", "message": {"model": "claude-sonnet-5", "content": []}}) + "\n")
            fh.write(json.dumps({"type": "assistant", "effort": "medium", "message": {"model": "claude-sonnet-5", "content": []}}) + "\n")
        empty = os.path.join(d, "agent-empty.jsonl")
        open(empty, "w", encoding="utf-8").close()
        cases = [
            ([ok], ["--expect-model", "claude-sonnet-5", "--expect-effort", "high"], 0, "agent-ok.jsonl lines=3 models=claude-sonnet-5×3 efforts=high×3"),
            ([bad], ["--expect-effort", "high"], 1, "agent-bad.jsonl: effort violation: expected high, saw high×1,medium×1"),
            ([ok], ["--expect-model", "claude-opus-5"], 1, "agent-ok.jsonl: model violation: expected claude-opus-5, saw claude-sonnet-5×3"),
            ([empty], ["--expect-effort", "high"], 0, "agent-empty.jsonl lines=0 models=- efforts=-"),
            ([os.path.join(d, "missing.jsonl")], [], 2, None),
        ]
        for paths, extra, want_rc, want_line in cases:
            r = subprocess.run([sys.executable, me, *paths, *extra], capture_output=True, text=True, encoding="utf-8")
            assert r.returncode == want_rc, (paths, extra, r.returncode, r.stdout, r.stderr)
            if want_line is not None:
                assert want_line in r.stdout.splitlines(), (want_line, r.stdout)
    print("self-test passed (5 cases)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("transcripts", nargs="*")
    ap.add_argument("--expect-model")
    ap.add_argument("--expect-effort")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.transcripts:
        ap.error("no transcripts given")
    return run(a.transcripts, a.expect_model, a.expect_effort)


if __name__ == "__main__":
    sys.exit(main())
