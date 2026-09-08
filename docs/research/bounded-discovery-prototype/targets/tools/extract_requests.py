#!/usr/bin/env python3
"""Write one record per unique API request found in harness transcripts.

Usage: python3 extract_requests.py OUT.jsonl TRANSCRIPT.jsonl...
Input: Claude Code session or sub-agent transcripts (one JSON object per line).
Output: OUT.jsonl with request id, model, effort, timestamps and the usage
fields the billing arithmetic uses; a streamed request appears on several
assistant lines with identical usage, so each counter keeps its maximum, the
same rule transcript_usage.py applies. Non-assistant lines are skipped.
Exit codes: 0 written; 2 a transcript cannot be read.
"""
from __future__ import annotations

import json
import os
import sys

COUNTERS = ("input_tokens", "cache_creation_input_tokens", "cache_write_5m", "cache_write_1h",
            "cache_read_input_tokens", "output_tokens", "thinking_tokens")


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: extract_requests.py OUT.jsonl TRANSCRIPT.jsonl...", file=sys.stderr)
        return 2
    out, paths = sys.argv[1], sys.argv[2:]
    reqs: dict = {}
    order: list = []
    skipped = 0
    for p in paths:
        try:
            fh = open(p, encoding="utf-8")
        except OSError as exc:
            print(f"extract_requests: cannot read {p}: {exc}", file=sys.stderr)
            return 2
        with fh:
            for line in fh:
                try:
                    o = json.loads(line)
                except ValueError:
                    skipped += 1
                    continue
                if o.get("type") != "assistant":
                    continue
                m = o.get("message") or {}
                u = m.get("usage")
                rid = o.get("requestId")
                if not u or not rid:
                    skipped += 1
                    continue
                cc = u.get("cache_creation") or {}
                rec = {"request_id": rid, "message_id": m.get("id"), "transcript": os.path.basename(p),
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
                if rid not in reqs:
                    reqs[rid] = rec
                    order.append(rid)
                    continue
                r = reqs[rid]
                for k in COUNTERS:
                    a, b = r.get(k), rec.get(k)
                    vals = [x for x in (a, b) if x is not None]
                    r[k] = max(vals) if vals else None
                r["last_seen"] = rec["last_seen"]
                if r["model"] != rec["model"] or r["effort"] != rec["effort"]:
                    r.setdefault("inconsistent", []).append({"model": rec["model"], "effort": rec["effort"]})
    with open(out, "w", encoding="utf-8") as f:
        for rid in order:
            f.write(json.dumps(reqs[rid]) + "\n")
    print(f"{out}: {len(order)} requests from {len(paths)} transcript(s); {skipped} non-usage lines skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
