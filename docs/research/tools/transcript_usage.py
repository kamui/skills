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
        --prices 2,10 [--cache-write-mult 1.25] [--cache-write-1h-mult 2.0] \\
        [--cache-read-mult 0.1] [--report <run.md>] [--timing <timing.json>] [--by-kind] \\
        [--row "<label>" | --json]

    python3 docs/research/tools/transcript_usage.py --header
    python3 docs/research/tools/transcript_usage.py --self-test

``--prices IN,OUT`` is dollars per million input and output tokens. Cache
reads cost ``IN × --cache-read-mult`` (default 0.1). Cache writes are priced
by cache lifetime: five-minute writes cost ``IN × --cache-write-mult``
(default 1.25) and one-hour writes ``IN × --cache-write-1h-mult`` (default
2.0), the standard multipliers for the two tiers. ``--report`` names the
research report the run wrote; its size in bytes ÷ 4 is subtracted from the
output column to give a production-shaped cost, the rule ``cost_split.py``
applies to the harness figure, here applied to billed output.

Input schema. Each transcript line is one JSON object. Assistant lines have
``"type": "assistant"`` and, inside ``message``, a ``usage`` object with
``input_tokens``, ``cache_creation_input_tokens``, ``cache_read_input_tokens``,
``output_tokens`` and, when present, ``output_tokens_details.thinking_tokens``
and a ``cache_creation`` object splitting the cache writes by lifetime into
``ephemeral_5m_input_tokens`` and ``ephemeral_1h_input_tokens``;
``message.model`` names the model; ``message.content`` is a list whose
``"type": "tool_use"`` items are tool calls; the top-level ``timestamp`` is
ISO 8601. Lines that are not valid JSON are skipped, as are assistant lines
the harness wrote itself rather than received from the API (``model`` of
``<synthetic>`` or ``isApiErrorMessage`` set, such as a session-limit notice);
they carry a zero usage object and are not billed requests.

Cache-write tiers. ``cache_creation_input_tokens`` is the authoritative
cache-write total. The ``cache_creation`` split is read per turn under the
same largest-recorded rule as the other cumulative fields and classified
against that turn's total. A split that adds up to the total is fully known
and priced per tier. A turn with no split at all (older transcripts) has its
whole total counted as **unknown-tier**. A split short of the total has the
shortfall counted as unknown-tier *residual*. A split that exceeds the total
is *inconsistent usage*: the whole total is counted as unknown-tier rather
than pricing a negative residual or counting the split twice. ``cost`` is a
point estimate that prices unknown-tier tokens at the five-minute multiplier,
the legacy assumption, so a transcript that carries no split prices exactly
as it did before; the cost *bounds* re-price the unknown-tier tokens at the
lower and at the higher of the two multipliers. Unknown-tier tokens are never
priced at zero, and every output that carries the estimate says how many
tokens it covers and why their tier is unknown: the estimate is a declared
fallback, not a billing guarantee.

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
(turns with no tool call), ``input``, ``cache_write`` with its tiers
``cache_write_5m``, ``cache_write_1h`` and ``cache_write_unknown`` (the three
sum to ``cache_write``; the unknown figure is broken down by cause, tokens
and turns, under ``cache_write_unknown_by_cause``), ``cache_read``,
``output``, ``thinking``, ``models`` (distinct, ``<synthetic>`` dropped),
``wall`` (last minus first assistant timestamp, ``H:MM:SS``; the ``TOTAL``
wall is the **agent span sum**, not elapsed time; ``agent_span_sum_seconds``
in the JSON total explicitly names the same historical sum), ``cost`` and its
``cost_bounds`` (``low``, ``high``, ``unknown_tier_tokens``, ``tiers_known``
and the ``assumption`` in words).
Output: one labelled block per transcript and a ``TOTAL`` block; with
``--row`` one Markdown table row of the totals, labelled; when ``--report``
is also given, the row populates the report estimate and production-shaped
cost. With ``--json`` it prints the same numbers as JSON. ``--header`` prints
the table header from the same column list as ``--row``, so the two cannot
diverge; production-shaped cells are ``—`` when no report was supplied. The
columns are the legacy ones: the ``Cache write`` cell names the tiers when
any write is one-hour or unknown-tier, and the cost cells carry the fallback
and the bounds when any write is unknown-tier, so a fully known
all-five-minute row prints exactly as before.

Timing sidecar (``--timing PATH``). One JSON object per run, with a required
``completion_mode`` of ``publication`` (confirmed final publication), ``result``
(production without publication), or ``render-only`` (evaluation's final
rendered result). The only other keys are ``root_dispatched_at``,
``payload_validated_at`` (final payload passed validation), and ``completed_at``
(final publication/result for the chosen mode). Each event is an ISO-8601
timestamp with date, time including seconds, and timezone, for example
``2026-09-05T12:00:00.250Z`` or ``2026-09-05T08:00:00.250-04:00``. Fractions
are padded or truncated to six digits before parsing, so all supported Python
versions measure and check ordering at microsecond precision. Missing or
null events stay unavailable. All available events must be in that order;
equal instants are allowed. Unknown keys, invalid timestamps, a missing/invalid
mode, or invalid ordering are input errors (exit 2, sidecar path on stderr).
Record events as they happen, starting immediately before root dispatch.
``review-code``'s ``scripts/run_events.py summarize --timing-sidecar`` writes
this shape from a run's recorded events, with ``root_dispatched_at`` null
because no review script observes root dispatch.

JSON adds a top-level ``timing`` object with the mode, events normalized to UTC,
``elapsed_to_payload_seconds`` and ``elapsed_to_completion_seconds``. Each
elapsed value is the corresponding event minus root dispatch, counted once
regardless of child overlap. Without a sidecar these fields are null. Default
report blocks append the same run timing with unavailable values labelled;
``--report`` still only reads the report for cost estimation. ``--row`` and
``--header`` retain their legacy columns and values, including ``Wall`` as the
agent span sum; use JSON or blocks alongside them for elapsed metrics. No
transcript timestamp or summed span substitutes for a missing timing event.

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
    "cache_write_5m",
    "cache_write_1h",
    "cache_write_unknown",
    "cache_read",
    "output",
    "thinking",
    # Why a cache write's tier is unknown: tokens and turns per cause. The
    # three token figures sum to cache_write_unknown.
    "unknown_no_breakdown",
    "unknown_residual",
    "unknown_inconsistent",
    "turns_no_breakdown",
    "turns_residual",
    "turns_inconsistent",
)

# The causes of an unknown cache-write tier, with how each reads in a block.
UNKNOWN_CAUSES = (
    ("no_breakdown", "without a tier breakdown"),
    ("residual", "whose breakdown is short of the total"),
    ("inconsistent", "whose breakdown exceeds the total (inconsistent usage)"),
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


TIMING_EVENTS = ("root_dispatched_at", "payload_validated_at", "completed_at")


def read_timing(path: Optional[str]) -> dict:
    """Read explicit run boundaries; never infer them from transcript spans."""
    data: dict = {}
    stamps: dict = {}
    if path is not None:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                raise ValueError("expected a JSON object")
            unknown = set(data) - {"completion_mode", *TIMING_EVENTS}
            if unknown:
                raise ValueError(f"unknown timing keys: {', '.join(sorted(unknown))}")
            if data.get("completion_mode") not in ("publication", "result", "render-only"):
                raise ValueError("completion_mode must be publication, result, or render-only")
            previous = None
            previous_name = None
            for name in TIMING_EVENTS:
                value = data.get(name)
                if value is None:
                    continue
                if not isinstance(value, str) or not re.fullmatch(
                    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)", value
                ):
                    raise ValueError(f"{name} must be an ISO-8601 timestamp with timezone")
                # Python 3.9/3.10 accept only three- or six-digit fractions.
                normalized = re.sub(r"\.(\d+)", lambda match: "." + match[1][:6].ljust(6, "0"), value)
                try:
                    stamp = datetime.fromisoformat(normalized.replace("Z", "+00:00")).astimezone(timezone.utc)
                except (ValueError, OverflowError) as exc:
                    raise ValueError(f"invalid {name}: {value!r}") from exc
                if previous is not None and stamp < previous:
                    raise ValueError(f"{name} precedes {previous_name}")
                stamps[name] = stamp
                previous, previous_name = stamp, name
        except (OSError, ValueError) as exc:
            raise SystemExit(f"transcript_usage: cannot read timing {path}: {exc}") from exc

    result = {"completion_mode": data.get("completion_mode")}
    result.update({name: stamps[name].isoformat() if name in stamps else None for name in TIMING_EVENTS})
    root = stamps.get("root_dispatched_at")
    for metric, event in (("elapsed_to_payload_seconds", "payload_validated_at"),
                          ("elapsed_to_completion_seconds", "completed_at")):
        end = stamps.get(event)
        result[metric] = (end - root).total_seconds() if root is not None and end is not None else None
    return result


def timing_lines(timing: dict) -> list[str]:
    lines = ["RUN TIMING"]
    for name, value in timing.items():
        label = name.replace("_", " ")
        lines.append(f"{label}: {value if value is not None else 'unavailable'}")
    return lines


class Rates:
    """Dollar prices per million tokens and the cache multipliers on the input price."""

    def __init__(self, prices: tuple[float, float], write_5m_mult: float, write_1h_mult: float, read_mult: float) -> None:
        self.price_in, self.price_out = prices
        self.write_5m_mult = write_5m_mult
        self.write_1h_mult = write_1h_mult
        self.read_mult = read_mult

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Rates":
        return cls(args.prices, args.cache_write_mult, args.cache_write_1h_mult, args.cache_read_mult)

    # An unknown-tier cache write is one of the two tiers; these bracket it.
    @property
    def unknown_low_mult(self) -> float:
        return min(self.write_5m_mult, self.write_1h_mult)

    @property
    def unknown_high_mult(self) -> float:
        return max(self.write_5m_mult, self.write_1h_mult)

    def as_dict(self) -> dict:
        return {
            "input": self.price_in,
            "output": self.price_out,
            "cache_write_mult": self.write_5m_mult,
            "cache_write_1h_mult": self.write_1h_mult,
            "cache_read_mult": self.read_mult,
            "unknown_tier_fallback": "unknown-tier cache writes are priced at cache_write_mult (5m) in cost; "
                                     "cost_bounds price them at the lower and the higher of the two multipliers",
        }


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
        self.wall_seconds += other.wall_seconds  # Agent span sum; overlapping waits count in each transcript.
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

    def cost(self, rates: Rates, output: Optional[int] = None, unknown_mult: Optional[float] = None) -> float:
        """Dollars. Unknown-tier cache writes are priced at ``unknown_mult``, by default the 5m multiplier."""
        c = self.counts
        out = c["output"] if output is None else output
        if unknown_mult is None:
            unknown_mult = rates.write_5m_mult
        return (
            c["input"] * rates.price_in
            + c["cache_write_5m"] * rates.price_in * rates.write_5m_mult
            + c["cache_write_1h"] * rates.price_in * rates.write_1h_mult
            + c["cache_write_unknown"] * rates.price_in * unknown_mult
            + c["cache_read"] * rates.price_in * rates.read_mult
            + out * rates.price_out
        ) / 1_000_000

    def cost_summary(self, rates: Rates, output: Optional[int] = None) -> dict:
        """The point estimate, the bounds that bracket the unknown-tier writes, and the assumption in words."""
        unknown = self.counts["cache_write_unknown"]
        if unknown == 0:
            assumption = "all cache-write tiers known"
        else:
            assumption = (
                f"{fmt(unknown)} unknown-tier cache-write tokens priced at the 5m multiplier ×{rates.write_5m_mult:g} "
                f"in the estimate and at ×{rates.unknown_low_mult:g} / ×{rates.unknown_high_mult:g} in the bounds"
            )
        return {
            "estimate": self.cost(rates, output),
            "low": self.cost(rates, output, rates.unknown_low_mult),
            "high": self.cost(rates, output, rates.unknown_high_mult),
            "unknown_tier_tokens": unknown,
            "tiers_known": unknown == 0,
            "assumption": assumption,
        }

    def unknown_causes(self) -> str:
        """Why the unknown-tier tokens are unknown, one clause per cause that occurred."""
        clauses = []
        for cause, reading in UNKNOWN_CAUSES:
            tokens = self.counts[f"unknown_{cause}"]
            turns = self.counts[f"turns_{cause}"]
            if tokens == 0 and turns == 0:
                continue
            noun = "turn" if turns == 1 else "turns"
            what = f"{fmt(tokens)} residual" if cause == "residual" else fmt(tokens)
            clauses.append(f"{what} in {fmt(turns)} {noun} {reading}")
        return "; ".join(clauses)

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
        for field in COUNT_FIELDS:
            if not field.startswith(("unknown_", "turns_")):
                data[field] = self.counts[field]
        data["cache_write_unknown_by_cause"] = {
            cause: {"tokens": self.counts[f"unknown_{cause}"], "turns": self.counts[f"turns_{cause}"]}
            for cause, _ in UNKNOWN_CAUSES
        }
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
            turn = {"input": 0, "cache_write": 0, "cache_write_5m": 0, "cache_write_1h": 0, "breakdown": False,
                    "cache_read": 0, "output": 0, "thinking": 0,
                    "tool_ids": set(), "tool_uses": 0, "lines": 0, "stamps": []}
            turns[key] = turn
        turn["lines"] += 1
        turn["input"] = max(turn["input"], int(used.get("input_tokens") or 0))
        turn["cache_write"] = max(turn["cache_write"], int(used.get("cache_creation_input_tokens") or 0))
        tiers = used.get("cache_creation")
        if isinstance(tiers, dict):
            five = tiers.get("ephemeral_5m_input_tokens")
            hour = tiers.get("ephemeral_1h_input_tokens")
            if five is not None or hour is not None:
                turn["breakdown"] = True
                turn["cache_write_5m"] = max(turn["cache_write_5m"], int(five or 0))
                turn["cache_write_1h"] = max(turn["cache_write_1h"], int(hour or 0))
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
        classify_cache_write(turn, counts)
        for stamp in turn["stamps"]:
            if usage.first is None or stamp < usage.first:
                usage.first = stamp
            if usage.last is None or stamp > usage.last:
                usage.last = stamp
    if usage.first is not None and usage.last is not None:
        usage.wall_seconds = (usage.last - usage.first).total_seconds()
    counts["cache_write_unknown"] = sum(counts[f"unknown_{cause}"] for cause, _ in UNKNOWN_CAUSES)
    assert counts["cache_write"] == counts["cache_write_5m"] + counts["cache_write_1h"] + counts["cache_write_unknown"], \
        "cache-write tiers do not sum to the total"

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


def classify_cache_write(turn: dict, counts: dict) -> None:
    """Sort one turn's cache writes into known tiers and unknown-tier tokens by cause.

    The turn's ``cache_write`` total is authoritative. A split that adds up to it
    is known per tier; a missing split leaves the whole total unknown-tier; a
    short split leaves the shortfall unknown-tier as residual; a split larger
    than the total is inconsistent usage and leaves the whole total unknown-tier,
    so nothing is priced twice and no residual goes negative.
    """
    total = turn["cache_write"]
    five, hour = turn["cache_write_5m"], turn["cache_write_1h"]
    if not turn["breakdown"]:
        if total > 0:
            counts["unknown_no_breakdown"] += total
            counts["turns_no_breakdown"] += 1
        return
    if five + hour > total:
        counts["unknown_inconsistent"] += total
        counts["turns_inconsistent"] += 1
        return
    counts["cache_write_5m"] += five
    counts["cache_write_1h"] += hour
    residual = total - five - hour
    if residual > 0:
        counts["unknown_residual"] += residual
        counts["turns_residual"] += 1


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
    unknown = c["cache_write_unknown"]
    tiers = f"5m {fmt(c['cache_write_5m'])}, 1h {fmt(c['cache_write_1h'])}"
    if unknown:
        tiers += f", unknown tier {fmt(unknown)}"
    lines.append(f"{'cache write':<{width}} {fmt(c['cache_write']):>12} tokens ({tiers})")
    if unknown:
        lines.append(f"{'unknown tier':<{width}} {fmt(unknown):>12} tokens: {usage.unknown_causes()}")
    lines.append(f"{'cache read':<{width}} {fmt(c['cache_read']):>12} tokens")
    lines.append(f"{'output':<{width}} {fmt(c['output']):>12} tokens (thinking {fmt(c['thinking'])})")
    lines.append(f"{'models':<{width}} {', '.join(usage.models) if usage.models else 'none recorded':>12}")
    wall_label = "agent span sum" if usage.label == "TOTAL" else "wall"
    wall_note = " (summed over transcripts; not elapsed)" if usage.label == "TOTAL" else " (assistant timestamp span)"
    lines.append(f"{wall_label:<{width}} {wall_text(usage.wall_seconds):>12}{wall_note}")
    rates = Rates.from_args(args)
    summary = usage.cost_summary(rates)
    tier_note = "all cache-write tiers known" if summary["tiers_known"] else "unknown-tier cache writes priced as 5m"
    lines.append(
        f"{'cost':<{width}} {summary['estimate']:>12.2f} $ at {rates.price_in:g}/{rates.price_out:g} per M, "
        f"cache write ×{rates.write_5m_mult:g} (5m) ×{rates.write_1h_mult:g} (1h), cache read ×{rates.read_mult:g}; "
        f"{tier_note}"
    )
    if not summary["tiers_known"]:
        lines.append(
            f"{'cost bounds':<{width}} {summary['low']:>12.2f} – {summary['high']:.2f} $ ({summary['assumption']})"
        )
    if shaped_tokens is not None:
        shaped_output = max(0, c["output"] - shaped_tokens)
        shaped = usage.cost_summary(rates, output=shaped_output)
        bounds = "" if shaped["tiers_known"] else f"; bounds {shaped['low']:.2f} – {shaped['high']:.2f} $"
        lines.append(
            f"{'production-shaped':<{width}} {shaped['estimate']:>12.2f} $ (output {fmt(shaped_output)} after subtracting "
            f"the report's {fmt(shaped_tokens)} est. tokens){bounds}"
        )
    if getattr(args, "by_kind", False):
        lines.extend(by_kind_lines(usage, width))
    return lines


def cost_cell(summary: dict, rates: Rates, bold: bool = False) -> str:
    """A cost cell: the estimate, and when any write is unknown-tier, its fallback and bounds."""
    cell = f"**{summary['estimate']:.2f}**" if bold else f"{summary['estimate']:.2f}"
    if not summary["tiers_known"]:
        cell += f" (unknown tier at ×{rates.write_5m_mult:g}; {summary['low']:.2f}–{summary['high']:.2f})"
    return cell


def row_line(usage: Usage, label: str, args: argparse.Namespace, shaped_tokens: Optional[int]) -> str:
    c = usage.counts
    rates = Rates.from_args(args)
    unknown = c["cache_write_unknown"]
    cache_write = fmt(c["cache_write"])
    if c["cache_write_1h"] or unknown:
        cache_write += f" (5m {fmt(c['cache_write_5m'])}, 1h {fmt(c['cache_write_1h'])}"
        cache_write += f", unknown {fmt(unknown)})" if unknown else ")"
    shaped_cost = "—"
    report_output = "—"
    if shaped_tokens is not None:
        shaped_output = max(0, c["output"] - shaped_tokens)
        shaped_cost = cost_cell(usage.cost_summary(rates, output=shaped_output), rates, bold=True)
        report_output = fmt(shaped_tokens)
    by_column = {
        "Run / agent": label,
        "Model": ", ".join(usage.models) if usage.models else "—",
        "Turns": fmt(c["turns"]),
        "Tool calls": fmt(c["tool_calls"]),
        "Text-only turns": fmt(c["text_only_turns"]),
        "Input": fmt(c["input"]),
        "Cache write": cache_write,
        "Cache read": fmt(c["cache_read"]),
        "Output": fmt(c["output"]),
        "Thinking": fmt(c["thinking"]),
        "Wall": wall_text(usage.wall_seconds),
        "Billed cost ($)": cost_cell(usage.cost_summary(rates), rates),
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
    parser.add_argument("--cache-write-mult", type=non_negative_float, default=1.25, help="five-minute cache-write price as a multiple of the input price (default 1.25); also the price assumed for cache writes whose tier is unknown")
    parser.add_argument("--cache-write-1h-mult", type=non_negative_float, default=2.0, help="one-hour cache-write price as a multiple of the input price (default 2.0)")
    parser.add_argument("--cache-read-mult", type=non_negative_float, default=0.1, help="cache-read price as a multiple of the input price (default 0.1)")
    parser.add_argument("--report", metavar="PATH", help="research report file; its bytes ÷ 4 come off the output for the production-shaped cost")
    parser.add_argument("--timing", metavar="PATH", help="run timing JSON sidecar with explicit dispatch, validated payload, and completion events")
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
        timing = read_timing(args.timing)
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
        rates = Rates.from_args(args)
        data = {"prices": rates.as_dict(), "transcripts": [], "timing": timing}

        def add_costs(entry: dict, usage: Usage) -> None:
            summary = usage.cost_summary(rates)
            entry["cost"] = round(summary["estimate"], 6)
            entry["cost_bounds"] = {
                "low": round(summary["low"], 6),
                "high": round(summary["high"], 6),
                "unknown_tier_tokens": summary["unknown_tier_tokens"],
                "tiers_known": summary["tiers_known"],
                "assumption": summary["assumption"],
            }

        for usage in usages:
            entry = usage.as_dict()
            entry["path"] = args.transcripts[usages.index(usage)]
            add_costs(entry, usage)
            if args.by_kind:
                entry["by_kind"] = usage.by_kind()
            data["transcripts"].append(entry)
        entry = total.as_dict()
        entry["agent_span_sum_seconds"] = entry["wall_seconds"]
        add_costs(entry, total)
        if args.by_kind:
            entry["by_kind"] = total.by_kind()
        if shaped_tokens is not None:
            shaped_output = max(0, total.counts["output"] - shaped_tokens)
            shaped = total.cost_summary(rates, output=shaped_output)
            entry["report_tokens"] = shaped_tokens
            entry["production_shaped_output"] = shaped_output
            entry["production_shaped_cost"] = round(shaped["estimate"], 6)
            entry["production_shaped_cost_bounds"] = {"low": round(shaped["low"], 6), "high": round(shaped["high"], 6)}
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
    print()
    for line in timing_lines(timing):
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

    def split_of(five: int, hour: int) -> dict:
        return {"ephemeral_5m_input_tokens": five, "ephemeral_1h_input_tokens": hour}

    # The simple transcript is fully known all-5m usage: the historical shape.
    first_usage = {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000,
                   "output_tokens": 50, "output_tokens_details": {"thinking_tokens": 20},
                   "cache_creation": split_of(100, 0)}
    second_usage = {"input_tokens": 0, "cache_creation_input_tokens": 50, "cache_read_input_tokens": 1150,
                    "output_tokens": 30, "output_tokens_details": {"thinking_tokens": 0},
                    "cache_creation": split_of(50, 0)}
    tool_use = {"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"command": "true"}}
    expected_cost = (10 * 2 + 150 * 2 * 1.25 + 2150 * 2 * 0.1 + 80 * 10) / 1e6

    def tiers_sum(total: dict) -> bool:
        return total.get("cache_write") == (total.get("cache_write_5m", -1) + total.get("cache_write_1h", -1)
                                            + total.get("cache_write_unknown", -1))

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
        check("all-5m tiers", (total.get("cache_write_5m"), total.get("cache_write_1h"), total.get("cache_write_unknown")) == (150, 0, 0),
              repr({k: total.get(k) for k in ("cache_write_5m", "cache_write_1h", "cache_write_unknown")}))
        check("all-5m tiers sum", tiers_sum(total), repr(total))
        bounds = total.get("cost_bounds", {})
        check("all-5m tiers known", bounds.get("tiers_known") is True and bounds.get("unknown_tier_tokens") == 0, repr(bounds))
        check("all-5m bounds collapse", bounds.get("low") == bounds.get("high") == total.get("cost"), repr(bounds))
        check("all-5m assumption", bounds.get("assumption") == "all cache-write tiers known", repr(bounds))
        check("all-5m no unknown causes", all(part == {"tokens": 0, "turns": 0} for part in total.get("cache_write_unknown_by_cause", {}).values())
              and set(total.get("cache_write_unknown_by_cause", {})) == {"no_breakdown", "residual", "inconsistent"},
              repr(total.get("cache_write_unknown_by_cause")))
        check("prices carry both multipliers", data.get("prices", {}).get("cache_write_mult") == 1.25
              and data.get("prices", {}).get("cache_write_1h_mult") == 2.0, repr(data.get("prices")))

        r = run(simple, "--prices", "2,10")
        check("block exits 0", r.returncode == 0, r.stderr)
        check("block turns", "turns                         2 (API requests; 2 assistant lines)" in r.stdout, r.stdout)
        check("block output", "output                       80 tokens (thinking 20)" in r.stdout, r.stdout)
        check("block wall", "wall                    0:00:10" in r.stdout, r.stdout)
        check("block cost", f"cost               {expected_cost:>12.2f} $ at 2/10 per M, cache write ×1.25 (5m) ×2 (1h), cache read ×0.1; all cache-write tiers known" in r.stdout, r.stdout)
        check("block cache write tiers", "cache write                 150 tokens (5m 150, 1h 0)" in r.stdout, r.stdout)
        check("block no unknown-tier line", "unknown tier" not in r.stdout and "cost bounds" not in r.stdout, r.stdout)
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

        # Cache-write tiers. One transcript per shape of ``cache_creation``; each is
        # one request (repeated as ``repeat`` lines) with only cache writes billed.
        def tier_file(name: str, total: int, split: Optional[dict], repeat: int = 1) -> str:
            used = {"input_tokens": 0, "cache_creation_input_tokens": total, "cache_read_input_tokens": 0,
                    "output_tokens": 0, "output_tokens_details": {"thinking_tokens": 0}}
            if split is not None:
                used["cache_creation"] = split
            path = os.path.join(tmp, name)
            with open(path, "w", encoding="utf-8") as fh:
                for n in range(repeat):
                    fh.write(json.dumps(assistant(used, [{"type": "text", "text": f"line {n}"}], f"2026-09-03T22:00:0{n}.000Z", "req_1")) + "\n")
            return path

        def tier_total(path: str, *extra: str) -> dict:
            r = run(path, "--prices", "2,10", "--json", *extra)
            check(f"{os.path.basename(path)} exits 0", r.returncode == 0, r.stderr)
            try:
                return json.loads(r.stdout)["total"]
            except (ValueError, KeyError):
                check(f"{os.path.basename(path)} json parses", False, r.stdout)
                return {}

        def tier_check(case: str, total: dict, five: int, hour: int, unknown: int, cost: float, low: float, high: float) -> None:
            got = (total.get("cache_write_5m"), total.get("cache_write_1h"), total.get("cache_write_unknown"))
            check(f"{case} tiers", got == (five, hour, unknown), f"got {got!r}, want {(five, hour, unknown)!r}")
            check(f"{case} tiers sum", tiers_sum(total), repr(total))
            check(f"{case} unknown never negative", (total.get("cache_write_unknown") or 0) >= 0, repr(total))
            bounds = total.get("cost_bounds", {})
            check(f"{case} cost", abs(total.get("cost", -1) - cost) < 1e-9, f"got {total.get('cost')!r}, want {cost!r}")
            check(f"{case} low bound", abs(bounds.get("low", -1) - low) < 1e-9, f"got {bounds.get('low')!r}, want {low!r}")
            check(f"{case} high bound", abs(bounds.get("high", -1) - high) < 1e-9, f"got {bounds.get('high')!r}, want {high!r}")
            check(f"{case} tiers_known", bounds.get("tiers_known") is (unknown == 0) and bounds.get("unknown_tier_tokens") == unknown, repr(bounds))

        def causes(total: dict) -> dict:
            return {cause: (part.get("tokens"), part.get("turns")) for cause, part in total.get("cache_write_unknown_by_cause", {}).items()}

        # All one-hour.
        all_1h = tier_file("all-1h.jsonl", 300, split_of(0, 300))
        total = tier_total(all_1h)
        tier_check("all-1h", total, 0, 300, 0, 300 * 2 * 2 / 1e6, 300 * 2 * 2 / 1e6, 300 * 2 * 2 / 1e6)
        r = run(all_1h, "--prices", "2,10", "--row", "x")
        check("all-1h row names the tiers", "| 300 (5m 0, 1h 300) |" in r.stdout and f"| {300 * 2 * 2 / 1e6:.2f} | — | — |" in r.stdout, r.stdout)

        # A 100/200 split that adds up to the 300 total: fully known, priced per tier.
        mixed = tier_file("mixed.jsonl", 300, split_of(100, 200))
        total = tier_total(mixed)
        mixed_cost = (100 * 1.25 + 200 * 2) * 2 / 1e6
        tier_check("mixed", total, 100, 200, 0, mixed_cost, mixed_cost, mixed_cost)
        check("mixed no unknown causes", all(part == (0, 0) for part in causes(total).values()), repr(causes(total)))

        # No breakdown at all: the legacy 5m estimate, marked assumed and bounded.
        absent = tier_file("no-split.jsonl", 300, None)
        total = tier_total(absent)
        tier_check("absent", total, 0, 0, 300, 300 * 1.25 * 2 / 1e6, 300 * 1.25 * 2 / 1e6, 300 * 2 * 2 / 1e6)
        check("absent cause", causes(total).get("no_breakdown") == (300, 1) and causes(total).get("residual") == (0, 0)
              and causes(total).get("inconsistent") == (0, 0), repr(causes(total)))
        check("absent assumption named", total.get("cost_bounds", {}).get("assumption") ==
              "300 unknown-tier cache-write tokens priced at the 5m multiplier ×1.25 in the estimate and at ×1.25 / ×2 in the bounds",
              repr(total.get("cost_bounds")))
        r = run(absent, "--prices", "2,10")
        check("absent block cache write", "cache write                 300 tokens (5m 0, 1h 0, unknown tier 300)" in r.stdout, r.stdout)
        check("absent block unknown line", "unknown tier                300 tokens: 300 in 1 turn without a tier breakdown" in r.stdout, r.stdout)
        check("absent block cost note", "; unknown-tier cache writes priced as 5m" in r.stdout, r.stdout)
        check("absent block bounds", f"cost bounds        {300 * 1.25 * 2 / 1e6:>12.2f} – {300 * 2 * 2 / 1e6:.2f} $ (300 unknown-tier" in r.stdout, r.stdout)
        r = run(absent, "--prices", "2,10", "--row", "x")
        check("absent row states the fallback",
              f"| 300 (5m 0, 1h 0, unknown 300) | 0 | 0 | 0 | 0:00:00 | {300 * 1.25 * 2 / 1e6:.2f} (unknown tier at ×1.25; "
              f"{300 * 1.25 * 2 / 1e6:.2f}–{300 * 2 * 2 / 1e6:.2f}) | — | — |" in r.stdout, r.stdout)
        # The legacy transcript shape prices as it always did: the same figures without a split.
        legacy = os.path.join(tmp, "legacy.jsonl")
        with open(legacy, "w", encoding="utf-8") as fh:
            for used, stamp in ((first_usage, "2026-09-03T22:00:05.000Z"), (second_usage, "2026-09-03T22:00:15.000Z")):
                stripped = {k: v for k, v in used.items() if k != "cache_creation"}
                fh.write(json.dumps(assistant(stripped, [{"type": "text", "text": "x"}], stamp)) + "\n")
        total = tier_total(legacy)
        check("legacy estimate unchanged", abs(total.get("cost", -1) - expected_cost) < 1e-9, f"got {total.get('cost')!r}, want {expected_cost!r}")
        check("legacy marked unknown-tier", total.get("cache_write_unknown") == 150 and causes(total).get("no_breakdown") == (150, 2), repr(total))

        # A partial split, 100 of 300 known: the known part is priced, the residual bounded.
        partial_file = tier_file("partial.jsonl", 300, split_of(100, 0))
        total = tier_total(partial_file)
        tier_check("partial", total, 100, 0, 200, (100 * 1.25 + 200 * 1.25) * 2 / 1e6,
                   (100 * 1.25 + 200 * 1.25) * 2 / 1e6, (100 * 1.25 + 200 * 2) * 2 / 1e6)
        check("partial cause", causes(total).get("residual") == (200, 1) and causes(total).get("no_breakdown") == (0, 0), repr(causes(total)))
        r = run(partial_file, "--prices", "2,10")
        check("partial block unknown line", "unknown tier                200 tokens: 200 residual in 1 turn whose breakdown is short of the total" in r.stdout, r.stdout)

        # A split larger than the total: inconsistent usage, the whole total bounded, nothing negative or doubled.
        over = tier_file("over.jsonl", 300, split_of(200, 200))
        total = tier_total(over)
        tier_check("inconsistent", total, 0, 0, 300, 300 * 1.25 * 2 / 1e6, 300 * 1.25 * 2 / 1e6, 300 * 2 * 2 / 1e6)
        check("inconsistent cause", causes(total).get("inconsistent") == (300, 1), repr(causes(total)))
        r = run(over, "--prices", "2,10")
        check("inconsistent block names it", "300 in 1 turn whose breakdown exceeds the total (inconsistent usage)" in r.stdout, r.stdout)
        r = run(over, "--prices", "2,10", "--row", "x")
        check("inconsistent row bounded", "(5m 0, 1h 0, unknown 300)" in r.stdout and "(unknown tier at ×1.25;" in r.stdout, r.stdout)

        # One request written as three lines repeating the same usage and split: counted once.
        repeated = tier_file("repeated.jsonl", 300, split_of(100, 200), repeat=3)
        total = tier_total(repeated)
        check("repeated one turn", total.get("turns") == 1 and total.get("lines") == 3, repr(total))
        check("repeated cache write once", total.get("cache_write") == 300, repr(total.get("cache_write")))
        tier_check("repeated", total, 100, 200, 0, mixed_cost, mixed_cost, mixed_cost)

        # Configurable multipliers reach both tiers and both bounds.
        total = tier_total(mixed, "--cache-write-mult", "1.5", "--cache-write-1h-mult", "3")
        configured = (100 * 1.5 + 200 * 3) * 2 / 1e6
        tier_check("configured mixed", total, 100, 200, 0, configured, configured, configured)
        total = tier_total(partial_file, "--cache-write-mult", "1.5", "--cache-write-1h-mult", "3")
        tier_check("configured partial", total, 100, 0, 200, (100 * 1.5 + 200 * 1.5) * 2 / 1e6,
                   (100 * 1.5 + 200 * 1.5) * 2 / 1e6, (100 * 1.5 + 200 * 3) * 2 / 1e6)
        # With the 1h multiplier below the 5m one the bounds still bracket the estimate.
        total = tier_total(partial_file, "--cache-write-mult", "2", "--cache-write-1h-mult", "1")
        tier_check("inverted multipliers", total, 100, 0, 200, (100 * 2 + 200 * 2) * 2 / 1e6,
                   (100 * 2 + 200 * 1) * 2 / 1e6, (100 * 2 + 200 * 2) * 2 / 1e6)
        r = run(mixed, "--prices", "2,10", "--cache-write-1h-mult", "-1")
        check("negative 1h multiplier exits 2", r.returncode == 2, f"rc={r.returncode}")

        # A report against an unknown-tier transcript: the production-shaped figures carry bounds too.
        r = run(absent, "--prices", "2,10", "--report", report, "--json")
        check("absent report exits 0", r.returncode == 0, r.stderr)
        try:
            total = json.loads(r.stdout)["total"]
        except (ValueError, KeyError):
            total = {}
        check("absent production-shaped bounds", total.get("production_shaped_cost_bounds", {}).get("high") == round(300 * 2 * 2 / 1e6, 6)
              and total.get("production_shaped_cost") == round(300 * 1.25 * 2 / 1e6, 6), repr(total))
        r = run(absent, "--prices", "2,10", "--report", report, "--row", "x")
        check("absent report row bounds", f"| **{300 * 1.25 * 2 / 1e6:.2f}** (unknown tier at ×1.25; {300 * 1.25 * 2 / 1e6:.2f}–{300 * 2 * 2 / 1e6:.2f}) |" in r.stdout, r.stdout)

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
