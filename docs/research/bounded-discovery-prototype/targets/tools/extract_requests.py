#!/usr/bin/env python3
"""Write one record per unique API request found in harness transcripts.

Usage: python3 extract_requests.py OUT.jsonl TRANSCRIPT.jsonl...
       python3 extract_requests.py --self-test
Input: Claude Code session or sub-agent transcripts (one JSON object per line).
Output: OUT.jsonl with request id, model, effort, timestamps and the usage
fields the billing arithmetic uses; a streamed request appears on several
assistant lines with identical usage, so each counter keeps its maximum, the
same rule transcript_usage.py applies. Non-assistant lines are skipped.
Exit codes: 0 written (or self-test passed); 1 a transcript held no usable
request record, one line on stdout; 2 a transcript cannot be read or the
output cannot be written, with the path on stderr.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile

COUNTERS = ("input_tokens", "cache_creation_input_tokens", "cache_write_5m", "cache_write_1h",
            "cache_read_input_tokens", "output_tokens", "thinking_tokens")


def record(o: dict, path: str) -> dict | None:
    if o.get("type") != "assistant":
        return None
    m = o.get("message") or {}
    u = m.get("usage")
    rid = o.get("requestId")
    if not u or not rid:
        return None
    cc = u.get("cache_creation") or {}
    return {"request_id": rid, "message_id": m.get("id"), "transcript": os.path.basename(path),
            "model": m.get("model"), "effort": o.get("effort"),
            "first_seen": o.get("timestamp"), "last_seen": o.get("timestamp"),
            "input_tokens": u.get("input_tokens", 0),
            "cache_creation_input_tokens": u.get("cache_creation_input_tokens", 0),
            "cache_write_5m": cc.get("ephemeral_5m_input_tokens"),
            "cache_write_1h": cc.get("ephemeral_1h_input_tokens"),
            "cache_read_input_tokens": u.get("cache_read_input_tokens", 0),
            "output_tokens": u.get("output_tokens", 0),
            "thinking_tokens": (u.get("output_tokens_details") or {}).get("thinking_tokens"),
            "service_tier": u.get("service_tier")}


def extract(paths: list) -> tuple:
    reqs: dict = {}
    order: list = []
    skipped = 0
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                try:
                    o = json.loads(line)
                except ValueError:
                    skipped += 1
                    continue
                rec = record(o, p)
                if rec is None:
                    skipped += 1
                    continue
                rid = rec["request_id"]
                if rid not in reqs:
                    reqs[rid] = rec
                    order.append(rid)
                    continue
                r = reqs[rid]
                for k in COUNTERS:
                    vals = [x for x in (r.get(k), rec.get(k)) if x is not None]
                    r[k] = max(vals) if vals else None
                r["last_seen"] = rec["last_seen"]
                if r["model"] != rec["model"] or r["effort"] != rec["effort"]:
                    r.setdefault("inconsistent", []).append({"model": rec["model"], "effort": rec["effort"]})
    return [reqs[rid] for rid in order], skipped


def self_test() -> int:
    line = lambda rid, out, ts, model="claude-sonnet-5": json.dumps({
        "type": "assistant", "requestId": rid, "effort": "high", "timestamp": ts,
        "message": {"id": "m" + rid, "model": model, "usage": {"input_tokens": 10, "output_tokens": out,
                    "cache_read_input_tokens": 5, "cache_creation": {"ephemeral_1h_input_tokens": 7}}}})
    with tempfile.TemporaryDirectory() as tmp:
        t = os.path.join(tmp, "agent-x.jsonl")
        with open(t, "w", encoding="utf-8") as f:
            f.write(line("r1", 3, "t1") + "\n" + line("r1", 9, "t2") + "\n" + "not json\n" +
                    json.dumps({"type": "user"}) + "\n" + line("r2", 4, "t3") + "\n")
        out = os.path.join(tmp, "out.jsonl")
        run = subprocess.run([sys.executable, __file__, out, t], capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 0, run.stdout + run.stderr
        rows = [json.loads(l) for l in open(out, encoding="utf-8")]
        assert [r["request_id"] for r in rows] == ["r1", "r2"], rows
        assert rows[0]["output_tokens"] == 9 and rows[0]["last_seen"] == "t2" and rows[0]["cache_write_1h"] == 7, rows[0]
        assert "2 requests" in run.stdout and "2 non-usage lines skipped" in run.stdout, run.stdout
        empty = os.path.join(tmp, "empty.jsonl")
        open(empty, "w", encoding="utf-8").write(json.dumps({"type": "user"}) + "\n")
        run = subprocess.run([sys.executable, __file__, os.path.join(tmp, "o2.jsonl"), empty], capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 1 and "no request records" in run.stdout, run.stdout + run.stderr
        run = subprocess.run([sys.executable, __file__, os.path.join(tmp, "o3.jsonl"), os.path.join(tmp, "missing.jsonl")], capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 2, run.stdout + run.stderr
    print("self-test passed (3 cases)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("out", nargs="?", help="output JSON-lines path, one record per request")
    parser.add_argument("transcripts", nargs="*", help="harness transcript files")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.out or not args.transcripts:
        parser.error("OUT.jsonl and at least one transcript are required")
    try:
        rows, skipped = extract(args.transcripts)
    except OSError as exc:
        print(f"extract_requests: cannot read transcript: {exc}", file=sys.stderr)
        return 2
    if not rows:
        print("no request records found in the given transcripts")
        return 1
    try:
        with open(args.out, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    except OSError as exc:
        print(f"extract_requests: cannot write {args.out}: {exc}", file=sys.stderr)
        return 2
    print(f"{args.out}: {len(rows)} requests from {len(args.transcripts)} transcript(s); {skipped} non-usage lines skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
