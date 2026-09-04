#!/usr/bin/env python3
"""Sum the billed usage of one or more harness sub-agent transcripts and price it.

The harness's ``subagent_tokens`` figure is roughly the agent's final context
size. Billing is per API request: every request re-sends the whole context
(cache reads, at a discount), adds whatever is new (cache writes), and pays
for the output, thinking included. This script reads the per-request
``usage`` objects the harness records in each transcript, sums them, and
prices the sum. It does mechanical arithmetic only.

Usage::

    python3 docs/research/tools/transcript_usage.py <agent-*.jsonl>... \\
        --prices 2,10 [--cache-write-mult 1.25] [--cache-read-mult 0.1] \\
        [--report <run.md>] [--by-kind] [--row "<label>" | --json]

    python3 docs/research/tools/transcript_usage.py --header
    python3 docs/research/tools/transcript_usage.py --self-test

``--prices IN,OUT`` is dollars per million input and output tokens. Cache
writes cost ``IN × --cache-write-mult`` and cache reads ``IN ×
--cache-read-mult``; the defaults are the standard 5-minute-cache
multipliers. ``--report`` names the research report the run wrote; its size
in bytes ÷ 4 is subtracted from the output column to give a production-shaped
cost, the rule ``cost_split.py`` applies to the harness figure, here applied
to billed output.

Input schema. Each transcript line is one JSON object. Assistant lines have
``"type": "assistant"`` and, inside ``message``, a ``usage`` object with
``input_tokens``, ``cache_creation_input_tokens``, ``cache_read_input_tokens``,
``output_tokens`` and, when present, ``output_tokens_details.thinking_tokens``;
``message.model`` names the model; ``message.content`` is a list whose
``"type": "tool_use"`` items are tool calls; the top-level ``timestamp`` is
ISO 8601. Lines that are not valid JSON are skipped, as are assistant lines
the harness wrote itself rather than received from the API (``model`` of
``<synthetic>`` or ``isApiErrorMessage`` set, such as a session-limit notice);
they carry a zero usage object and are not billed requests.

One API request, one turn. The harness writes one line per content block of
a response, and every line of the same response repeats that response's
``usage`` object (the output count grows across the lines and is final on
the last). Lines sharing a ``requestId`` are therefore one turn: the input,
cache-write and cache-read figures are taken once, the output and thinking
figures are the largest recorded, and the tool calls are the distinct
``tool_use`` items across the lines. A line without a ``requestId`` is its
own turn. Summing every line instead counts the context once per content
block and overstates cache reads by the blocks-per-request ratio; the
``lines`` figure in the block is printed so a reader can see that ratio.

Per transcript: ``turns``, ``lines``, ``tool_calls``, ``text_only_turns``
(turns with no tool call), ``input``, ``cache_write``, ``cache_read``,
``output``, ``thinking``, ``models`` (distinct, ``<synthetic>`` dropped),
``wall`` (last minus first assistant timestamp, ``H:MM:SS``; the ``TOTAL``
wall is the sum over transcripts, not the span), and ``cost``.
Output: one labelled block per transcript and a ``TOTAL`` block; with
``--row`` one Markdown table row of the totals, labelled; when ``--report``
is also given, the row populates the report estimate and production-shaped
cost. With ``--json`` it prints the same numbers as JSON. ``--header`` prints
the table header from the same column list as ``--row``, so the two cannot
diverge; production-shaped cells are ``—`` when no report was supplied.

``--by-kind`` adds an ``output by kind`` block after each printed block and a
``by_kind`` object to each ``--json`` entry; it leaves the ``--row`` /
``--header`` columns alone. Thinking comes from ``usage`` (thinking blocks are
stored empty, so their characters cannot be counted); the rest of the output is
*visible*, and is split across ``text`` and one ``tool:<name>`` bucket per tool
in proportion to the characters each contributes: ``len`` of a text block's
text, ``len`` of ``json.dumps`` of a tool call's input. A content block is
counted once per request even where the harness re-emits it on more than one
line. File writes are a **second** accounting of the same characters, reported
on their own line and never summed with the buckets: a ``Write`` call under its
``file_path``, and a ``Bash`` call whose command carries a heredoc under the
redirect target parsed out of that command, each measured in the same
serialized characters as its ``tool:`` bucket so a write is a part of the
bucket it came from. Their per-path counts say how much of the writing is the
same file written again.

Exit codes: ``0`` success; ``1`` a self-test assertion failed, on stdout;
``2`` a transcript cannot be read or has no billed assistant turns, or an
argument is invalid, naming the path or argument on stderr.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Optional

COLUMNS = (
    "Run / agent",
    "Model",
    "Turns",
    "Tool calls",
    "Text-only turns",
    "Input",
    "Cache write",
    "Cache read",
    "Output",
    "Thinking",
    "Wall",
    "Billed cost ($)",
    "Report output (est.)",
    "Production-shaped ($)",
)

COUNT_FIELDS = (
    "turns",
    "lines",
    "tool_calls",
    "text_only_turns",
    "input",
    "cache_write",
    "cache_read",
    "output",
    "thinking",
)


# The redirect target of a heredoc command: ``> path``, ``>> path``, ``tee path``
# or ``tee -a path``, with the path optionally quoted.
WRITE_PATH_RE = re.compile(r"""(?:>>?|tee(?: -a)?)\s*['"]?([^\s'"|;&]+)""")

NO_PATH = "(no path)"


def block_identity(item: dict) -> tuple:
    """What makes a content block itself, for counting it once per request.

    The harness writes one line per content block and re-emits a block on a
    later line of the same request, so a block's position in its line's
    ``content`` list does not distinguish it from its neighbours: in a recorded
    transcript every line carries one block at index 0. A tool call is
    identified by its ``id`` and anything else by a digest of the block, so a
    re-emission matches the first sighting and a different block does not.
    """
    tool_id = item.get("id")
    if item.get("type") == "tool_use" and isinstance(tool_id, str) and tool_id:
        return ("tool_use", tool_id)
    blob = json.dumps(item, ensure_ascii=False, sort_keys=True, default=str)
    return (item.get("type"), hashlib.sha256(blob.encode("utf-8")).hexdigest())


def add_block_chars(item: dict, kinds: dict, writes: dict) -> None:
    """Add one content block's characters to the per-kind and per-file-write tallies.

    ``kinds`` buckets every visible character exactly once. ``writes`` is a
    second accounting of some of the same characters, per destination path, so
    the two are reported separately and never summed.
    """
    kind = item.get("type")
    if kind == "text":
        text = item.get("text")
        if isinstance(text, str):
            kinds["text"] = kinds.get("text", 0) + len(text)
        return
    if kind != "tool_use":
        return  # thinking blocks are stored empty; nothing else is billed as visible output
    name = item.get("name")
    if not isinstance(name, str) or not name:
        name = "unknown"
    data = item.get("input")
    if not isinstance(data, dict):
        data = {}
    bucket = f"tool:{name}"
    chars = len(json.dumps(data))
    kinds[bucket] = kinds.get(bucket, 0) + chars

    # Where the call wrote a file, the same characters again under that path, so a
    # write is measured in the same unit as the bucket it is a part of.
    path: Optional[str] = None
    if name == "Write":
        target = data.get("file_path")
        path = target if isinstance(target, str) and target else NO_PATH
    elif name == "Bash":
        command = data.get("command")
        if isinstance(command, str) and "<<" in command:
            match = WRITE_PATH_RE.search(command)
            path = match.group(1) if match else NO_PATH
    if path is None:
        return
    entry = writes.setdefault(path, {"count": 0, "chars": 0})
    entry["count"] += 1
    entry["chars"] += chars


def token_share(chars: int, total_chars: int, visible: int) -> int:
    """The share of ``visible`` tokens that ``chars`` characters account for."""
    if total_chars <= 0 or visible <= 0:
        return 0
    return round(chars * visible / total_chars)


def allocate(kind_chars: dict, visible: int) -> dict:
    """Split ``visible`` tokens across the buckets in proportion to characters.

    Each bucket is rounded and the rounding remainder lands on the largest one,
    so the parts sum to ``visible`` exactly.
    """
    total_chars = sum(kind_chars.values())
    parts = {name: {"chars": chars, "tokens": 0} for name, chars in kind_chars.items()}
    if not parts or total_chars <= 0 or visible <= 0:
        return parts
    for name, chars in kind_chars.items():
        parts[name]["tokens"] = token_share(chars, total_chars, visible)
    largest = max(kind_chars, key=lambda name: (kind_chars[name], name))
    parts[largest]["tokens"] += visible - sum(part["tokens"] for part in parts.values())
    return parts


def prices_arg(text: str) -> tuple[float, float]:
    parts = text.split(",")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"expected IN,OUT dollars per million tokens: {text!r}")
    try:
        values = tuple(float(p) for p in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not numbers: {text!r}") from exc
    if any(v < 0 for v in values):
        raise argparse.ArgumentTypeError(f"prices must not be negative: {text!r}")
    return values  # type: ignore[return-value]


def non_negative_float(text: str) -> float:
    try:
        value = float(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from exc
    if value < 0:
        raise argparse.ArgumentTypeError(f"must not be negative: {text!r}")
    return value


def fmt(value: int) -> str:
    return f"{value:,}"


def table_row(cells) -> str:
    return "| " + " | ".join(cells) + " |"


def header_lines() -> list[str]:
    return [table_row(COLUMNS), table_row("---" for _ in COLUMNS)]


def parse_timestamp(text) -> Optional[datetime]:
    if not isinstance(text, str):
        return None
    try:
        stamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp


def wall_text(seconds: float) -> str:
    total = int(round(seconds))
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


class Usage:
    """Summed usage for one transcript or for a set of them."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.counts = {field: 0 for field in COUNT_FIELDS}
        self.models: list[str] = []
        self.first: Optional[datetime] = None
        self.last: Optional[datetime] = None
        self.wall_seconds = 0.0
        # Visible-output accounting, filled by read_transcript(): characters and
        # their share of the visible tokens, per bucket and per written path.
        self.chars = 0
        self.kinds: dict = {}
        self.writes: dict = {}

    def add_model(self, model) -> None:
        if isinstance(model, str) and model and model != "<synthetic>" and model not in self.models:
            self.models.append(model)

    def absorb(self, other: "Usage") -> None:
        for field in COUNT_FIELDS:
            self.counts[field] += other.counts[field]
        for model in other.models:
            self.add_model(model)
        self.wall_seconds += other.wall_seconds
        self.chars += other.chars
        for name, part in other.kinds.items():
            mine = self.kinds.setdefault(name, {"chars": 0, "tokens": 0})
            mine["chars"] += part["chars"]
            mine["tokens"] += part["tokens"]
        for path, part in other.writes.items():
            mine = self.writes.setdefault(path, {"count": 0, "chars": 0, "tokens": 0})
            mine["count"] += part["count"]
            mine["chars"] += part["chars"]
            mine["tokens"] += part["tokens"]

    def cost(self, prices: tuple[float, float], write_mult: float, read_mult: float, output: Optional[int] = None) -> float:
        price_in, price_out = prices
        out = self.counts["output"] if output is None else output
        return (
            self.counts["input"] * price_in
            + self.counts["cache_write"] * price_in * write_mult
            + self.counts["cache_read"] * price_in * read_mult
            + out * price_out
        ) / 1_000_000

    def by_kind(self) -> dict:
        """Thinking, and the visible output split by bucket and by written path.

        Buckets and paths are ordered by characters, largest first.
        """
        def ordered(table: dict) -> dict:
            return {name: dict(part)
                    for name, part in sorted(table.items(), key=lambda kv: (-kv[1]["chars"], kv[0]))}

        return {
            "thinking": self.counts["thinking"],
            "visible": max(0, self.counts["output"] - self.counts["thinking"]),
            "chars": self.chars,
            "kinds": ordered(self.kinds),
            "writes": ordered(self.writes),
        }

    def as_dict(self) -> dict:
        data = {"label": self.label}
        data.update(self.counts)
        data["models"] = list(self.models)
        data["wall"] = wall_text(self.wall_seconds)
        data["wall_seconds"] = round(self.wall_seconds, 3)
        return data


def read_transcript(path: str) -> Usage:
    """Sum one transcript. Raises SystemExit with a message on unreadable or empty input."""
    usage = Usage(os.path.basename(path))
    try:
        with open(path, encoding="utf-8") as fh:
            raw_lines = fh.readlines()
    except OSError as exc:
        raise SystemExit(f"transcript_usage: cannot read {path}: {exc.strerror}")

    # One entry per turn, in first-seen order. Lines that share a requestId
    # are one API request; lines without one stand alone.
    turns: dict = {}
    anonymous = 0
    # Characters per bucket and per written path, over the whole transcript, with
    # the content blocks already accounted for keyed by (turn, block identity).
    kind_chars: dict = {}
    write_chars: dict = {}
    seen_blocks: set = set()
    for raw in raw_lines:
        try:
            obj = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(obj, dict) or obj.get("type") != "assistant":
            continue
        message = obj.get("message")
        if not isinstance(message, dict):
            continue
        used = message.get("usage")
        if not isinstance(used, dict):
            continue
        if obj.get("isApiErrorMessage") or message.get("model") == "<synthetic>":
            continue  # a harness-written error line, not a billed request
        key = obj.get("requestId")
        if not isinstance(key, str) or not key:
            anonymous += 1
            key = ("line", anonymous)
        turn = turns.get(key)
        if turn is None:
            turn = {"input": 0, "cache_write": 0, "cache_read": 0, "output": 0, "thinking": 0,
                    "tool_ids": set(), "tool_uses": 0, "lines": 0, "stamps": []}
            turns[key] = turn
        turn["lines"] += 1
        turn["input"] = max(turn["input"], int(used.get("input_tokens") or 0))
        turn["cache_write"] = max(turn["cache_write"], int(used.get("cache_creation_input_tokens") or 0))
        turn["cache_read"] = max(turn["cache_read"], int(used.get("cache_read_input_tokens") or 0))
        turn["output"] = max(turn["output"], int(used.get("output_tokens") or 0))
        details = used.get("output_tokens_details")
        if isinstance(details, dict):
            turn["thinking"] = max(turn["thinking"], int(details.get("thinking_tokens") or 0))
        content = message.get("content")
        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "tool_use":
                    tool_id = item.get("id")
                    if isinstance(tool_id, str) and tool_id:
                        turn["tool_ids"].add(tool_id)
                    else:
                        turn["tool_uses"] += 1
                # One block's characters count once per request: the harness
                # re-emits a block on more than one line of the same request.
                block_key = (key, block_identity(item))
                if block_key in seen_blocks:
                    continue
                seen_blocks.add(block_key)
                add_block_chars(item, kind_chars, write_chars)
        usage.add_model(message.get("model"))
        stamp = parse_timestamp(obj.get("timestamp"))
        if stamp is not None:
            turn["stamps"].append(stamp)

    if not turns:
        raise SystemExit(f"transcript_usage: no billed assistant turns in {path}")

    counts = usage.counts
    for turn in turns.values():
        counts["turns"] += 1
        counts["lines"] += turn["lines"]
        calls = len(turn["tool_ids"]) + turn["tool_uses"]
        counts["tool_calls"] += calls
        if calls == 0:
            counts["text_only_turns"] += 1
        for field in ("input", "cache_write", "cache_read", "output", "thinking"):
            counts[field] += turn[field]
        for stamp in turn["stamps"]:
            if usage.first is None or stamp < usage.first:
                usage.first = stamp
            if usage.last is None or stamp > usage.last:
                usage.last = stamp
    if usage.first is not None and usage.last is not None:
        usage.wall_seconds = (usage.last - usage.first).total_seconds()

    # Thinking is billed but unreadable; the rest of the output is what the
    # characters above account for.
    visible = max(0, counts["output"] - counts["thinking"])
    usage.chars = sum(kind_chars.values())
    usage.kinds = allocate(kind_chars, visible)
    usage.writes = {
        path: {"count": part["count"], "chars": part["chars"],
               "tokens": token_share(part["chars"], usage.chars, visible)}
        for path, part in write_chars.items()
    }
    return usage


def report_tokens(path: Optional[str]) -> Optional[int]:
    if path is None:
        return None
    try:
        return round(os.path.getsize(path) / 4)
    except OSError as exc:
        raise SystemExit(f"transcript_usage: cannot read {path}: {exc.strerror}")


def by_kind_lines(usage: Usage, width: int) -> list[str]:
    """The ``output by kind`` block: thinking, the visible buckets, then file writes."""
    data = usage.by_kind()
    lines = ["output by kind"]
    lines.append(f"{'thinking':<{width}} {fmt(data['thinking']):>12} tokens (from usage)")
    lines.append(f"{'visible':<{width}} {fmt(data['visible']):>12} tokens over {fmt(data['chars'])} chars")
    for name, part in data["kinds"].items():
        lines.append(f"  {name:<{width - 2}} {fmt(part['tokens']):>12} tokens {fmt(part['chars']):>9} chars")
    writes = data["writes"]
    lines.append(
        f"{'file writes':<{width}} {fmt(sum(p['tokens'] for p in writes.values())):>12} tokens "
        f"{fmt(sum(p['chars'] for p in writes.values())):>9} chars in "
        f"{fmt(sum(p['count'] for p in writes.values()))} writes to {fmt(len(writes))} paths"
    )
    for path, part in writes.items():
        # A path written once is not a rewrite, so the count is only worth printing above one.
        again = f", written {fmt(part['count'])} times" if part["count"] > 1 else ""
        lines.append(f"  {path:<{width - 2}} {fmt(part['tokens']):>12} tokens {fmt(part['chars']):>9} chars{again}")
    return lines


def block_lines(usage: Usage, args: argparse.Namespace, shaped_tokens: Optional[int]) -> list[str]:
    width = 18
    c = usage.counts
    lines = [f"{usage.label}"]
    lines.append(f"{'turns':<{width}} {fmt(c['turns']):>12} (API requests; {fmt(c['lines'])} assistant lines)")
    lines.append(f"{'tool calls':<{width}} {fmt(c['tool_calls']):>12}")
    lines.append(f"{'text-only turns':<{width}} {fmt(c['text_only_turns']):>12}")
    lines.append(f"{'input':<{width}} {fmt(c['input']):>12} tokens (uncached)")
    lines.append(f"{'cache write':<{width}} {fmt(c['cache_write']):>12} tokens")
    lines.append(f"{'cache read':<{width}} {fmt(c['cache_read']):>12} tokens")
    lines.append(f"{'output':<{width}} {fmt(c['output']):>12} tokens (thinking {fmt(c['thinking'])})")
    lines.append(f"{'models':<{width}} {', '.join(usage.models) if usage.models else 'none recorded':>12}")
    wall_note = " (summed over transcripts)" if usage.label == "TOTAL" else ""
    lines.append(f"{'wall':<{width}} {wall_text(usage.wall_seconds):>12}{wall_note}")
    cost = usage.cost(args.prices, args.cache_write_mult, args.cache_read_mult)
    lines.append(
        f"{'cost':<{width}} {cost:>12.2f} $ at {args.prices[0]:g}/{args.prices[1]:g} per M, "
        f"cache write ×{args.cache_write_mult:g}, cache read ×{args.cache_read_mult:g}"
    )
    if shaped_tokens is not None:
        shaped_output = max(0, c["output"] - shaped_tokens)
        shaped = usage.cost(args.prices, args.cache_write_mult, args.cache_read_mult, output=shaped_output)
        lines.append(
            f"{'production-shaped':<{width}} {shaped:>12.2f} $ (output {fmt(shaped_output)} after subtracting "
            f"the report's {fmt(shaped_tokens)} est. tokens)"
        )
    if getattr(args, "by_kind", False):
        lines.extend(by_kind_lines(usage, width))
    return lines


def row_line(usage: Usage, label: str, args: argparse.Namespace, shaped_tokens: Optional[int]) -> str:
    c = usage.counts
    shaped_cost = "—"
    report_output = "—"
    if shaped_tokens is not None:
        shaped_output = max(0, c["output"] - shaped_tokens)
        cost = usage.cost(
            args.prices, args.cache_write_mult, args.cache_read_mult, output=shaped_output
        )
        shaped_cost = f"**{cost:.2f}**"
        report_output = fmt(shaped_tokens)
    by_column = {
        "Run / agent": label,
        "Model": ", ".join(usage.models) if usage.models else "—",
        "Turns": fmt(c["turns"]),
        "Tool calls": fmt(c["tool_calls"]),
        "Text-only turns": fmt(c["text_only_turns"]),
        "Input": fmt(c["input"]),
        "Cache write": fmt(c["cache_write"]),
        "Cache read": fmt(c["cache_read"]),
        "Output": fmt(c["output"]),
        "Thinking": fmt(c["thinking"]),
        "Wall": wall_text(usage.wall_seconds),
        "Billed cost ($)": f"{usage.cost(args.prices, args.cache_write_mult, args.cache_read_mult):.2f}",
        "Report output (est.)": report_output,
        "Production-shaped ($)": shaped_cost,
    }
    assert tuple(by_column) == COLUMNS, "row cells and COLUMNS disagree"
    return table_row(by_column[name] for name in COLUMNS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="transcript_usage.py",
        description="Sum the billed usage recorded in harness sub-agent transcripts and price it.",
    )
    parser.add_argument("transcripts", nargs="*", help="one or more agent-*.jsonl transcript paths")
    parser.add_argument("--prices", type=prices_arg, metavar="IN,OUT", help="dollars per million input and output tokens, e.g. 2,10")
    parser.add_argument("--cache-write-mult", type=non_negative_float, default=1.25, help="cache-write price as a multiple of the input price (default 1.25)")
    parser.add_argument("--cache-read-mult", type=non_negative_float, default=0.1, help="cache-read price as a multiple of the input price (default 0.1)")
    parser.add_argument("--report", metavar="PATH", help="research report file; its bytes ÷ 4 come off the output for the production-shaped cost")
    parser.add_argument("--by-kind", action="store_true", help="add an output-by-kind block splitting visible output across text, tool inputs and file writes")
    parser.add_argument("--row", metavar="LABEL", help="print one Markdown table row of the totals labelled LABEL instead of the blocks")
    parser.add_argument("--header", action="store_true", help="print the Markdown table header matching --row and exit")
    parser.add_argument("--json", action="store_true", help="print the numbers as JSON instead of blocks")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checks and exit")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.header:
        for line in header_lines():
            print(line)
        return 0
    if not args.transcripts:
        parser.error("at least one transcript path is required")
    if args.prices is None:
        parser.error("--prices IN,OUT is required")

    try:
        usages = [read_transcript(path) for path in args.transcripts]
        shaped_tokens = report_tokens(args.report)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 2

    total = Usage("TOTAL")
    for usage in usages:
        total.absorb(usage)

    if args.row is not None:
        print(row_line(total, args.row, args, shaped_tokens))
        return 0

    if args.json:
        data = {
            "prices": {"input": args.prices[0], "output": args.prices[1],
                       "cache_write_mult": args.cache_write_mult, "cache_read_mult": args.cache_read_mult},
            "transcripts": [],
        }
        for usage in usages:
            entry = usage.as_dict()
            entry["path"] = args.transcripts[usages.index(usage)]
            entry["cost"] = round(usage.cost(args.prices, args.cache_write_mult, args.cache_read_mult), 6)
            if args.by_kind:
                entry["by_kind"] = usage.by_kind()
            data["transcripts"].append(entry)
        entry = total.as_dict()
        entry["cost"] = round(total.cost(args.prices, args.cache_write_mult, args.cache_read_mult), 6)
        if args.by_kind:
            entry["by_kind"] = total.by_kind()
        if shaped_tokens is not None:
            shaped_output = max(0, total.counts["output"] - shaped_tokens)
            entry["report_tokens"] = shaped_tokens
            entry["production_shaped_output"] = shaped_output
            entry["production_shaped_cost"] = round(
                total.cost(args.prices, args.cache_write_mult, args.cache_read_mult, output=shaped_output), 6
            )
        data["total"] = entry
        print(json.dumps(data, indent=2))
        return 0

    first = True
    for usage in usages:
        if not first:
            print()
        first = False
        for line in block_lines(usage, args, None):
            print(line)
    print()
    for line in block_lines(total, args, shaped_tokens):
        print(line)
    return 0


# --- self-test -------------------------------------------------------------


def self_test() -> int:
    failures: list[str] = []
    script = os.path.abspath(__file__)

    def run(*extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, script, *extra], capture_output=True, text=True, encoding="utf-8"
        )

    def check(case: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(f"{case}: {detail}".rstrip(": "))

    def assistant(usage: dict, content: list, stamp: str, request: Optional[str] = None) -> dict:
        line = {
            "type": "assistant",
            "timestamp": stamp,
            "message": {"model": "claude-sonnet-5", "usage": usage, "content": content},
        }
        if request is not None:
            line["requestId"] = request
        return line

    first_usage = {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000,
                   "output_tokens": 50, "output_tokens_details": {"thinking_tokens": 20}}
    second_usage = {"input_tokens": 0, "cache_creation_input_tokens": 50, "cache_read_input_tokens": 1150,
                    "output_tokens": 30, "output_tokens_details": {"thinking_tokens": 0}}
    tool_use = {"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"command": "true"}}
    expected_cost = (10 * 2 + 150 * 2 * 1.25 + 2150 * 2 * 0.1 + 80 * 10) / 1e6

    with tempfile.TemporaryDirectory() as tmp:
        simple = os.path.join(tmp, "simple.jsonl")
        with open(simple, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "user", "timestamp": "2026-09-03T22:00:00.000Z", "message": {"content": "go"}}) + "\n")
            fh.write(json.dumps(assistant(first_usage, [{"type": "text", "text": "thinking it over"}], "2026-09-03T22:00:05.000Z")) + "\n")
            fh.write(json.dumps(assistant(second_usage, [tool_use], "2026-09-03T22:00:15.000Z")) + "\n")

        r = run(simple, "--prices", "2,10", "--json")
        check("simple exits 0", r.returncode == 0, r.stderr)
        try:
            data = json.loads(r.stdout)
            total = data["total"]
        except (ValueError, KeyError):
            data, total = {}, {}
            check("simple json parses", False, r.stdout)
        for field, want in (("turns", 2), ("tool_calls", 1), ("text_only_turns", 1), ("cache_read", 2150),
                            ("output", 80), ("thinking", 20), ("input", 10), ("cache_write", 150), ("wall", "0:00:10")):
            check(f"simple {field}", total.get(field) == want, f"got {total.get(field)!r}, want {want!r}")
        check("simple cost", abs(total.get("cost", -1) - expected_cost) < 1e-9, f"got {total.get('cost')!r}, want {expected_cost!r}")
        check("simple model", total.get("models") == ["claude-sonnet-5"], repr(total.get("models")))

        r = run(simple, "--prices", "2,10")
        check("block exits 0", r.returncode == 0, r.stderr)
        check("block turns", "turns                         2 (API requests; 2 assistant lines)" in r.stdout, r.stdout)
        check("block output", "output                       80 tokens (thinking 20)" in r.stdout, r.stdout)
        check("block wall", "wall                    0:00:10" in r.stdout, r.stdout)
        check("block cost", f"cost               {expected_cost:>12.2f} $ at 2/10 per M" in r.stdout, r.stdout)
        check("block total", "TOTAL" in r.stdout, r.stdout)
        check("block no production line", "production-shaped" not in r.stdout, r.stdout)

        # One API request written as three lines (thinking, tool_use, tool_use), the usage
        # repeated on each with the output count final on the last: one turn, two tool calls.
        split = os.path.join(tmp, "split.jsonl")
        partial = dict(first_usage, output_tokens=5, output_tokens_details={"thinking_tokens": 5})
        other_tool = dict(tool_use, id="toolu_2")
        with open(split, "w", encoding="utf-8") as fh:
            fh.write("this line is not JSON\n")
            fh.write(json.dumps(assistant(partial, [{"type": "thinking", "thinking": "hm"}], "2026-09-03T22:00:05.000Z", "req_1")) + "\n")
            fh.write(json.dumps(assistant(partial, [tool_use], "2026-09-03T22:00:06.000Z", "req_1")) + "\n")
            fh.write(json.dumps(assistant(first_usage, [other_tool], "2026-09-03T22:00:07.000Z", "req_1")) + "\n")
            fh.write(json.dumps(assistant(second_usage, [{"type": "text", "text": "done"}], "2026-09-03T22:00:15.000Z", "req_2")) + "\n")
            zero = {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0}
            fh.write(json.dumps({"type": "assistant", "isApiErrorMessage": True, "timestamp": "2026-09-03T23:00:00.000Z",
                                 "requestId": "req_3", "message": {"model": "<synthetic>", "usage": zero,
                                                                    "content": [{"type": "text", "text": "You've hit your session limit"}]}}) + "\n")

        r = run(split, "--prices", "2,10", "--json")
        check("split exits 0", r.returncode == 0, r.stderr)
        try:
            total = json.loads(r.stdout)["total"]
        except (ValueError, KeyError):
            total = {}
            check("split json parses", False, r.stdout)
        for field, want in (("turns", 2), ("lines", 4), ("tool_calls", 2), ("text_only_turns", 1),
                            ("cache_read", 2150), ("cache_write", 150), ("output", 80), ("thinking", 20), ("wall", "0:00:10")):
            check(f"split {field}", total.get(field) == want, f"got {total.get(field)!r}, want {want!r}")
        check("split cost", abs(total.get("cost", -1) - expected_cost) < 1e-9, f"got {total.get('cost')!r}")
        check("split synthetic model dropped", total.get("models") == ["claude-sonnet-5"], repr(total.get("models")))
        check("split error line not a turn", total.get("turns") == 2 and total.get("wall") == "0:00:10", f"{total.get('turns')!r} {total.get('wall')!r}")

        r = run(simple, split, "--prices", "2,10", "--json")
        check("two files exit 0", r.returncode == 0, r.stderr)
        try:
            data = json.loads(r.stdout)
        except ValueError:
            data = {"transcripts": [], "total": {}}
            check("two files json parses", False, r.stdout)
        check("two files listed", len(data["transcripts"]) == 2, repr(data.get("transcripts")))
        check("two files total turns", data["total"].get("turns") == 4, repr(data["total"].get("turns")))
        check("two files total cache_read", data["total"].get("cache_read") == 4300, repr(data["total"].get("cache_read")))
        check("two files total wall", data["total"].get("wall") == "0:00:20", repr(data["total"].get("wall")))

        report = os.path.join(tmp, "report.md")
        with open(report, "w", encoding="utf-8") as fh:
            fh.write("r" * 200)  # 50 tokens at 4 bytes/token
        r = run(simple, "--prices", "2,10", "--report", report)
        check("report exits 0", r.returncode == 0, r.stderr)
        shaped = (10 * 2 + 150 * 2 * 1.25 + 2150 * 2 * 0.1 + 30 * 10) / 1e6
        check("report production line", f"production-shaped  {shaped:>12.2f} $ (output 30 after subtracting the report's 50 est. tokens)" in r.stdout, r.stdout)
        with open(report, "w", encoding="utf-8") as fh:
            fh.write("r" * 4000)  # 1,000 tokens, more than the output
        r = run(simple, "--prices", "2,10", "--report", report, "--json")
        check("report floor exits 0", r.returncode == 0, r.stderr)
        try:
            total = json.loads(r.stdout)["total"]
        except (ValueError, KeyError):
            total = {}
        check("report floor at zero", total.get("production_shaped_output") == 0, repr(total.get("production_shaped_output")))

        r = run(simple, "--prices", "2,10", "--row", "v5a primary")
        check("row exits 0", r.returncode == 0, r.stderr)
        expected_row = f"| v5a primary | claude-sonnet-5 | 2 | 1 | 1 | 10 | 150 | 2,150 | 80 | 20 | 0:00:10 | {expected_cost:.2f} | — | — |"
        check("row content", r.stdout.strip() == expected_row, r.stdout)

        r = run(simple, "--prices", "2,10", "--report", report, "--row", "v5a primary")
        check("report row exits 0", r.returncode == 0, r.stderr)
        report_row = f"| v5a primary | claude-sonnet-5 | 2 | 1 | 1 | 10 | 150 | 2,150 | 80 | 20 | 0:00:10 | {expected_cost:.2f} | 1,000 | **0.00** |"
        check("report row content", r.stdout.strip() == report_row, r.stdout)

        # Two requests, the second written as two lines that re-emit one block: the
        # visible output splits across text, tool inputs and the file the calls wrote.
        heredoc = {"command": "cat > /tmp/x.md <<'EOF'\nbody\nEOF"}
        write_input = {"file_path": "/tmp/x.md", "content": "xxxxxxxx"}
        bash_chars = len(json.dumps(heredoc))
        write_chars = len(json.dumps(write_input))
        kinds_usage = {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                       "output_tokens": 100, "output_tokens_details": {"thinking_tokens": 40}}
        write_usage = {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                       "output_tokens": 60, "output_tokens_details": {"thinking_tokens": 0}}
        write_block = {"type": "tool_use", "id": "toolu_2", "name": "Write", "input": write_input}
        kinds_file = os.path.join(tmp, "kinds.jsonl")
        with open(kinds_file, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(assistant(kinds_usage, [
                {"type": "text", "text": "aaaa"},
                {"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": heredoc},
            ], "2026-09-03T22:00:05.000Z", "req_1")) + "\n")
            fh.write(json.dumps(assistant(write_usage, [write_block], "2026-09-03T22:00:06.000Z", "req_2")) + "\n")
            fh.write(json.dumps(assistant(write_usage, [write_block], "2026-09-03T22:00:07.000Z", "req_2")) + "\n")

        r = run(kinds_file, "--prices", "2,10", "--by-kind", "--json")
        check("by-kind exits 0", r.returncode == 0, r.stderr)
        try:
            by_kind = json.loads(r.stdout)["total"]["by_kind"]
        except (ValueError, KeyError):
            by_kind = {"kinds": {}, "writes": {}}
            check("by-kind json parses", False, r.stdout)
        kinds = by_kind.get("kinds", {})
        writes = by_kind.get("writes", {})
        check("by-kind thinking", by_kind.get("thinking") == 40, repr(by_kind.get("thinking")))
        check("by-kind visible", by_kind.get("visible") == 120, repr(by_kind.get("visible")))
        check("by-kind chars", by_kind.get("chars") == 4 + bash_chars + write_chars, repr(by_kind.get("chars")))
        check("by-kind text chars", kinds.get("text", {}).get("chars") == 4, repr(kinds.get("text")))
        check("by-kind bash chars", kinds.get("tool:Bash", {}).get("chars") == bash_chars, repr(kinds.get("tool:Bash")))
        check("by-kind write counted once", kinds.get("tool:Write", {}).get("chars") == write_chars,
              f"got {kinds.get('tool:Write')!r}, want {write_chars} (not {2 * write_chars})")
        check("by-kind allocation sums to visible", sum(part["tokens"] for part in kinds.values()) == 120,
              repr({name: part["tokens"] for name, part in kinds.items()}))
        check("by-kind largest bucket first", list(kinds) == ["tool:Bash", "tool:Write", "text"], repr(list(kinds)))
        check("by-kind write count", writes.get("/tmp/x.md", {}).get("count") == 2, repr(writes.get("/tmp/x.md")))
        check("by-kind write chars", writes.get("/tmp/x.md", {}).get("chars") == bash_chars + write_chars,
              repr(writes.get("/tmp/x.md")))

        r = run(kinds_file, "--prices", "2,10", "--by-kind")
        check("by-kind block exits 0", r.returncode == 0, r.stderr)
        check("by-kind block heading", "output by kind" in r.stdout, r.stdout)
        check("by-kind block thinking", "thinking                     40 tokens (from usage)" in r.stdout, r.stdout)
        check("by-kind block visible", f"visible                     120 tokens over {fmt(4 + bash_chars + write_chars)} chars" in r.stdout, r.stdout)
        check("by-kind block writes", "in 2 writes to 1 paths" in r.stdout, r.stdout)
        check("by-kind block rewrite noted", "written 2 times" in r.stdout, r.stdout)

        r = run(kinds_file, "--prices", "2,10")
        check("without the flag exits 0", r.returncode == 0, r.stderr)
        check("without the flag no by-kind block", "output by kind" not in r.stdout, r.stdout)

        plain_row = run(kinds_file, "--prices", "2,10", "--row", "x")
        by_kind_row = run(kinds_file, "--prices", "2,10", "--by-kind", "--row", "x")
        check("row unchanged by the flag", plain_row.stdout == by_kind_row.stdout,
              f"{plain_row.stdout!r} vs {by_kind_row.stdout!r}")

        r = run("--header")
        check("header exits 0", r.returncode == 0, r.stderr)
        header = "| Run / agent | Model | Turns | Tool calls | Text-only turns | Input | Cache write | Cache read | Output | Thinking | Wall | Billed cost ($) | Report output (est.) | Production-shaped ($) |"
        check("header row", r.stdout.splitlines()[0] == header, r.stdout)
        check("header separator", r.stdout.splitlines()[1] == "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |", r.stdout)
        check("header cell count matches row", header.count("|") == expected_row.count("|"), f"{header} vs {expected_row}")

        r = run(simple, "--prices", "2,10", "--cache-write-mult", "2", "--cache-read-mult", "0.5", "--json")
        check("mult exits 0", r.returncode == 0, r.stderr)
        try:
            cost = json.loads(r.stdout)["total"]["cost"]
        except (ValueError, KeyError):
            cost = -1
        check("mult cost", abs(cost - (10 * 2 + 150 * 2 * 2 + 2150 * 2 * 0.5 + 80 * 10) / 1e6) < 1e-9, repr(cost))

        r = run(os.path.join(tmp, "absent.jsonl"), "--prices", "2,10")
        check("missing file exits 2", r.returncode == 2, f"rc={r.returncode}")
        check("missing file names it", "absent.jsonl" in r.stderr, r.stderr)

        empty = os.path.join(tmp, "empty.jsonl")
        with open(empty, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "user", "message": {"content": "only a user line"}}) + "\n")
        r = run(empty, "--prices", "2,10")
        check("no usage exits 2", r.returncode == 2, f"rc={r.returncode}")
        check("no usage names it", "empty.jsonl" in r.stderr, r.stderr)
        died = os.path.join(tmp, "died.jsonl")
        with open(died, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "assistant", "isApiErrorMessage": True, "timestamp": "2026-09-03T23:00:00.000Z",
                                 "message": {"model": "<synthetic>", "usage": zero, "content": []}}) + "\n")
        r = run(died, "--prices", "2,10")
        check("only error line exits 2", r.returncode == 2, f"rc={r.returncode}")
        check("only error line names it", "died.jsonl" in r.stderr, r.stderr)

        r = run(simple)
        check("missing prices exits 2", r.returncode == 2, f"rc={r.returncode}")
        r = run(simple, "--prices", "2")
        check("bad prices exits 2", r.returncode == 2, f"rc={r.returncode}")
        r = run("--prices", "2,10")
        check("no transcript exits 2", r.returncode == 2, f"rc={r.returncode}")
        r = run(simple, "--prices", "2,10", "--report", os.path.join(tmp, "absent.md"))
        check("missing report exits 2", r.returncode == 2, f"rc={r.returncode}")

    for line in failures:
        print(line)
    if not failures:
        print("transcript_usage.py self-test: all cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
