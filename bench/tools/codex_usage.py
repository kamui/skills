#!/usr/bin/env python3
"""Sum the billed usage of a Codex CLI session's rollout logs and price it.

``codex review`` and ``codex exec`` write one rollout JSONL per thread under
``$CODEX_HOME/sessions/YYYY/MM/DD/rollout-<stamp>-<thread id>.jsonl``. The
review itself runs in a subagent thread whose ``session_meta`` carries
``parent_thread_id``; the parent thread records no usage. This script gathers
the root thread and every descendant thread, sums their per-request usage,
and prices the sum. It does mechanical arithmetic only.

Usage::

    python3 docs/research/tools/codex_usage.py --sessions-dir <CODEX_HOME>/sessions \\
        --session <root thread id> --prices 10,50 [--cached-mult 0.1] \\
        [--cache-write-mult 1.25] [--report <run.md>] [--row "<label>" | --json]

    python3 docs/research/tools/codex_usage.py <rollout.jsonl>... --prices 10,50 [...]
    python3 docs/research/tools/codex_usage.py --header
    python3 docs/research/tools/codex_usage.py --self-test

``--prices IN,OUT`` is dollars per million ordinary input and output tokens.
OpenAI's ``input_tokens`` is the whole prompt: cached tokens and cache-write
tokens are subsets of it and are billed instead of, not on top of, the
ordinary rate. Ordinary input is therefore ``input − cached − cache_write``;
a request whose subsets exceed its input is inconsistent usage (exit 2).
Cached input costs ``IN × --cached-mult`` (default 0.1) and cache writes
``IN × --cache-write-mult`` (default 1.25); pass the provider's dated rates.
Prices and multipliers must be finite and non-negative.
``--report`` names the research report the run wrote; its size in bytes ÷ 4
is subtracted from the output column, never below zero, to give a
production-shaped cost, the rule ``transcript_usage.py`` applies to harness
transcripts.

Input schema. Each rollout line is one JSON object with ``timestamp``,
``type`` and ``payload``. The first line is ``session_meta`` whose payload
has ``id`` and, for a child thread, ``parent_thread_id``. Each billed API
request is one ``token_usage_record`` line whose ``payload.usage`` carries
``input_tokens`` (cached tokens included), ``cached_input_tokens``,
``cache_write_input_tokens``, ``output_tokens`` (reasoning included) and
``reasoning_output_tokens``; ``payload.response_id`` identifies the request,
so a repeated record for one response is counted once. ``turn_context``
lines name the ``model``. ``response_item`` lines whose payload type is
``function_call``, ``custom_tool_call`` or ``local_shell_call`` are tool
calls, attributed to the next ``token_usage_record`` in file order; a
request that produced no tool call is a text-only turn.

Output: one block per thread and a ``TOTAL`` block; ``--row`` prints one
Markdown table row of the totals under the same columns as
``transcript_usage.py --header`` (``Cache read`` is cached input,
``Thinking`` is reasoning output, ``Wall`` is first-to-last usage record);
``--json`` prints the same numbers as JSON.

Exit codes: 0 success; 1 no billed request found; 2 unreadable input,
a malformed rollout line (named as ``file:line`` so the meter never reports a
complete total over a damaged log), inconsistent usage, or a missing root
thread, named on stderr.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile

TOOL_TYPES = {"function_call", "custom_tool_call", "local_shell_call"}
COLUMNS = ["Run / agent", "Model", "Turns", "Tool calls", "Text-only turns", "Input",
           "Cache write", "Cache read", "Output", "Thinking", "Wall", "Billed cost ($)",
           "Report output (est.)", "Production-shaped ($)"]


def parse_stamp(value):
    if not value:
        return None
    text = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


class RolloutError(ValueError):
    pass


def read_rollout(path: Path) -> dict:
    meta = {}
    usage_by_response = {}
    order = []
    models = set()
    tool_calls_by_response = {}
    pending_tool_calls = 0
    first = last = None
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise RolloutError(f"{path}:{number}: malformed JSON ({error.msg})") from None
            if not isinstance(record, dict):
                raise RolloutError(f"{path}:{number}: rollout line is not an object")
            kind = record.get("type")
            payload = record.get("payload") or {}
            if kind == "session_meta" and not meta:
                meta = payload
            elif kind == "turn_context" and payload.get("model"):
                models.add(payload["model"])
            elif kind == "response_item" and payload.get("type") in TOOL_TYPES:
                pending_tool_calls += 1
            elif kind == "token_usage_record":
                usage = payload.get("usage")
                if not isinstance(usage, dict):
                    raise RolloutError(f"{path}:{number}: token_usage_record without usage object")
                key = payload.get("response_id") or f"ordinal-{record.get('ordinal')}"
                if key not in usage_by_response:
                    order.append(key)
                    tool_calls_by_response[key] = pending_tool_calls
                    pending_tool_calls = 0
                usage_by_response[key] = usage
                stamp = parse_stamp(record.get("timestamp"))
                if stamp:
                    first = stamp if first is None or stamp < first else first
                    last = stamp if last is None or stamp > last else last
    return {"path": str(path), "meta": meta,
            "usage": [(usage_by_response[k], tool_calls_by_response[k]) for k in order],
            "models": models, "first": first, "last": last}


def summarize(rollout: dict, prices: tuple[float, float], cached_mult: float, write_mult: float) -> dict:
    ordinary = cached = write = out = reasoning = 0
    tool_calls = 0
    text_only = 0
    for index, (usage, calls) in enumerate(rollout["usage"], 1):
        inp = int(usage.get("input_tokens") or 0)
        c = int(usage.get("cached_input_tokens") or 0)
        w = int(usage.get("cache_write_input_tokens") or 0)
        if c + w > inp:
            raise RolloutError(f"{rollout['path']}: request {index} has cached+cache_write "
                               f"({c}+{w}) above input_tokens ({inp})")
        ordinary += inp - c - w
        cached += c
        write += w
        out += int(usage.get("output_tokens") or 0)
        reasoning += int(usage.get("reasoning_output_tokens") or 0)
        tool_calls += calls
        text_only += 1 if calls == 0 else 0
    turns = len(rollout["usage"])
    uncached = ordinary
    in_price, out_price = prices
    cost = (uncached * in_price + cached * in_price * cached_mult
            + write * in_price * write_mult + out * out_price) / 1_000_000
    wall = None
    if rollout["first"] and rollout["last"]:
        wall = int((rollout["last"] - rollout["first"]).total_seconds())
    return {"turns": turns, "tool_calls": tool_calls, "text_only_turns": text_only, "input": uncached,
            "cache_write": write, "cache_read": cached, "output": out, "thinking": reasoning,
            "models": sorted(rollout["models"]), "wall_seconds": wall, "cost": cost}


def add(total: dict, part: dict) -> dict:
    for key in ("turns", "tool_calls", "text_only_turns", "input", "cache_write", "cache_read",
                "output", "thinking", "cost"):
        total[key] = total.get(key, 0) + part[key]
    total["models"] = sorted(set(total.get("models", [])) | set(part["models"]))
    total["wall_seconds"] = (total.get("wall_seconds") or 0) + (part["wall_seconds"] or 0)
    return total


def gather(sessions_dir: Path, root: str) -> list[Path]:
    rollouts = {}
    for path in sorted(sessions_dir.rglob("rollout-*.jsonl")):
        with open(path, encoding="utf-8") as handle:
            head = handle.readline()
        try:
            meta = json.loads(head).get("payload") or {}
        except json.JSONDecodeError:
            continue
        thread = meta.get("id") or meta.get("session_id")
        if thread:
            rollouts[thread] = (path, meta.get("parent_thread_id"))
    if root not in rollouts:
        raise FileNotFoundError(f"root thread {root} not found under {sessions_dir}")
    selected = []
    frontier = [root]
    while frontier:
        current = frontier.pop()
        selected.append(rollouts[current][0])
        frontier.extend(t for t, (_, parent) in rollouts.items() if parent == current)
    return selected


def hms(seconds):
    if seconds is None:
        return "—"
    return f"{seconds // 3600}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def fmt(n: int) -> str:
    return f"{n:,}"


def row(label: str, total: dict, report_bytes) -> str:
    model = ", ".join(total["models"]) or "—"
    est = min(report_bytes // 4, total["output"]) if report_bytes is not None else None
    shaped = total["cost"] - est * total["out_price"] / 1_000_000 if est is not None else None
    cells = [label, model, str(total["turns"]), str(total["tool_calls"]), str(total["text_only_turns"]),
             fmt(total["input"]), fmt(total["cache_write"]), fmt(total["cache_read"]), fmt(total["output"]),
             fmt(total["thinking"]), hms(total["wall_seconds"]), f"{total['cost']:.2f}",
             fmt(est) if est is not None else "—", f"**{shaped:.2f}**" if shaped is not None else "—"]
    return "| " + " | ".join(cells) + " |"


def header() -> str:
    return "| " + " | ".join(COLUMNS) + " |\n|" + " --- |" * len(COLUMNS)


def self_test() -> int:
    with tempfile.TemporaryDirectory() as temp:
        sessions = Path(temp) / "sessions" / "2026" / "09" / "24"
        sessions.mkdir(parents=True)
        parent = sessions / "rollout-2026-09-24T00-00-00-root.jsonl"
        child = sessions / "rollout-2026-09-24T00-00-01-child.jsonl"
        parent.write_text(json.dumps({"timestamp": "2026-09-24T00:00:00Z", "type": "session_meta",
                                      "payload": {"id": "root"}}) + "\n", encoding="utf-8")
        lines = [
            {"timestamp": "2026-09-24T00:00:01Z", "type": "session_meta",
             "payload": {"id": "child", "parent_thread_id": "root"}},
            {"timestamp": "2026-09-24T00:00:02Z", "type": "turn_context", "payload": {"model": "m", "turn_id": "t1"}},
            {"timestamp": "2026-09-24T00:00:03Z", "type": "response_item",
             "payload": {"type": "custom_tool_call", "turn_id": "t1"}},
            {"timestamp": "2026-09-24T00:00:04Z", "type": "token_usage_record",
             "payload": {"response_id": "r1", "turn_id": "t1", "usage": {
                 "input_tokens": 1000, "cached_input_tokens": 400, "cache_write_input_tokens": 100,
                 "output_tokens": 50, "reasoning_output_tokens": 10}}},
            {"timestamp": "2026-09-24T00:00:04Z", "type": "token_usage_record",
             "payload": {"response_id": "r1", "turn_id": "t1", "usage": {
                 "input_tokens": 1000, "cached_input_tokens": 400, "cache_write_input_tokens": 100,
                 "output_tokens": 50, "reasoning_output_tokens": 10}}},
            {"timestamp": "2026-09-24T00:01:04Z", "type": "token_usage_record",
             "payload": {"response_id": "r2", "turn_id": "t2", "usage": {
                 "input_tokens": 2000, "cached_input_tokens": 1500, "cache_write_input_tokens": 0,
                 "output_tokens": 30, "reasoning_output_tokens": 0}}},
        ]
        child.write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")
        paths = gather(Path(temp) / "sessions", "root")
        assert {p.name for p in paths} == {parent.name, child.name}, paths
        total = {}
        for path in paths:
            total = add(total, summarize(read_rollout(path), (10.0, 50.0), 0.1, 1.25))
        assert total["turns"] == 2, total
        assert total["tool_calls"] == 1 and total["text_only_turns"] == 1, total
        assert total["input"] == 1000 and total["cache_read"] == 1900 and total["cache_write"] == 100, total
        assert total["output"] == 80 and total["thinking"] == 10, total
        expected = (1000 * 10 + 1900 * 1 + 100 * 12.5 + 80 * 50) / 1_000_000
        assert abs(total["cost"] - expected) < 1e-9, (total["cost"], expected)
        assert total["wall_seconds"] == 60, total
        try:
            gather(Path(temp) / "sessions", "missing")
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("missing root must raise")
        broken = sessions / "rollout-2026-09-24T00-00-02-broken.jsonl"
        broken.write_text(child.read_text(encoding="utf-8") + "{not json\n", encoding="utf-8")
        try:
            read_rollout(broken)
        except RolloutError as error:
            assert broken.name in str(error) and ":7:" in str(error), error
        else:
            raise AssertionError("malformed line must raise")
        bad = sessions / "rollout-2026-09-24T00-00-03-bad.jsonl"
        bad.write_text(json.dumps({"type": "token_usage_record", "payload": {"response_id": "x", "usage": {
            "input_tokens": 10, "cached_input_tokens": 8, "cache_write_input_tokens": 8}}}) + "\n", encoding="utf-8")
        try:
            summarize(read_rollout(bad), (10.0, 50.0), 0.1, 1.25)
        except RolloutError:
            pass
        else:
            raise AssertionError("inconsistent usage must raise")
    print("self-test ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", help="rollout JSONL files")
    parser.add_argument("--sessions-dir")
    parser.add_argument("--session", help="root thread id")
    parser.add_argument("--prices", help="IN,OUT dollars per million tokens")
    parser.add_argument("--cached-mult", type=float, default=0.1)
    parser.add_argument("--cache-write-mult", type=float, default=1.25)
    parser.add_argument("--report")
    parser.add_argument("--row")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--header", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.header:
        print(header())
        return 0
    if args.self_test:
        return self_test()
    if not args.prices:
        parser.error("--prices IN,OUT is required")
    try:
        in_price, out_price = (float(x) for x in args.prices.split(","))
    except ValueError:
        parser.error("--prices must be IN,OUT")
    rates = {"input price": in_price, "output price": out_price, "--cached-mult": args.cached_mult,
             "--cache-write-mult": args.cache_write_mult}
    for name, value in rates.items():
        if value != value or value in (float("inf"), float("-inf")) or value < 0:
            parser.error(f"{name} must be finite and non-negative")
    try:
        if args.sessions_dir and args.session:
            paths = gather(Path(args.sessions_dir), args.session)
        elif args.paths:
            paths = [Path(p) for p in args.paths]
        else:
            parser.error("give rollout paths or --sessions-dir with --session")
        rollouts = [read_rollout(p) for p in paths]
    except (OSError, RolloutError) as error:
        print(f"codex_usage.py: {error}", file=sys.stderr)
        return 2
    report_bytes = None
    if args.report:
        try:
            report_bytes = os.path.getsize(args.report)
        except OSError as error:
            print(f"codex_usage.py: {error}", file=sys.stderr)
            return 2
    total = {}
    blocks = []
    try:
        for rollout in rollouts:
            part = summarize(rollout, (in_price, out_price), args.cached_mult, args.cache_write_mult)
            blocks.append((rollout["path"], part))
            total = add(total, part)
    except RolloutError as error:
        print(f"codex_usage.py: {error}", file=sys.stderr)
        return 2
    if not total or total["turns"] == 0:
        print("no billed request found in the given rollouts")
        return 1
    total["out_price"] = out_price
    if args.row:
        print(row(args.row, total, report_bytes))
    elif args.json:
        out = {"threads": [{"path": p, **s} for p, s in blocks], "total": {k: v for k, v in total.items() if k != "out_price"},
               "prices": {"input": in_price, "output": out_price, "cached_mult": args.cached_mult,
                          "cache_write_mult": args.cache_write_mult}, "report_bytes": report_bytes}
        print(json.dumps(out, indent=2))
    else:
        for path, part in blocks + [("TOTAL", total)]:
            print(f"{path}: turns={part['turns']} tool_calls={part['tool_calls']} input={part['input']} "
                  f"cache_read={part['cache_read']} cache_write={part['cache_write']} output={part['output']} "
                  f"thinking={part['thinking']} wall={hms(part['wall_seconds'])} cost=${part['cost']:.4f} "
                  f"models={','.join(part['models'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
