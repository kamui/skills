#!/usr/bin/env python3
"""Execute a disposable fake worker's finite read-tool requests and complete report.

Usage: python3 scripts/fake_worker.py < request.json
Input: {packet, response, read_roots, ranges, request_id, requested}, as assembled
by adapter.py. response is trusted synthetic fixture data, never model code.
Only the read tool exists. There is no shell, eval, network or history tool.
This is a tool-boundary test, not an OS sandbox for arbitrary Python or Claude.
Exit: 0 complete JSONL records, 1 invalid tool content, 2 unreadable input.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import subprocess
import time

from budget import now


def read_tool(request, roots, ranges):
    path = Path(request["path"]).resolve()
    permitted = any(path.is_relative_to(Path(root).resolve()) for root in roots)
    start, end = request.get("start", 1), request.get("end", 1)
    if type(start) is not int or type(end) is not int or not 1 <= start <= end:
        return {"status": "denied", "reason": "invalid range"}
    if ranges is not None:
        permitted = permitted and any(path == Path(row["path"]).resolve() and
                                      row["start"] <= start <= end <= row["end"] for row in ranges)
    if not permitted:
        return {"status": "denied", "reason": "outside permitted read roots or selected range"}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        return {"status": "read", "content": "\n".join(lines[start - 1:end])}
    except OSError as exc:
        return {"status": "unavailable", "reason": str(exc)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return subprocess.run([sys.executable, str(Path(__file__).with_name("test_adapter.py")),
            "AdapterTests.test_barrier_freshness_compact_packets_and_actual_tool_reads"]).returncode
    try:
        data = json.load(sys.stdin)
        response = data["response"]
        time.sleep(response.get("delay_seconds", 0))
        for call in response.get("tools", []):
            result = (read_tool(call, data["read_roots"], data["ranges"])
                      if call["name"] == "read" else {"status": "denied", "reason": "tool unavailable"})
            print(json.dumps({"type": "tool-result", "call": call, "result": result}), flush=True)
        observed = response.get("observed", data["requested"])
        usage = response.get("usage", {"input_tokens": 20, "output_tokens": 10,
                                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0})
        print(json.dumps({"type": "assistant", "timestamp": now(), "requestId": data["request_id"],
                          "effort": observed.get("effort"), "requested": data["requested"],
                          "message": {"model": observed.get("model"), "usage": usage,
                                      "content": [{"type": "text", "text": "synthetic fixture response"}]}}), flush=True)
        if response.get("malformed"):
            print('{"type":"result","report":', flush=True)
        elif not response.get("missing"):
            print(json.dumps({"type": "result", "complete": True, "report": response["report"]}), flush=True)
        return 0
    except (ValueError, KeyError, TypeError) as exc:
        print(str(exc))
        return 1
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
