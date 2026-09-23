#!/usr/bin/env python3
"""Measure one review-code interface cell: usage, validation tail, repairs, loads, and authored fields.

It extends ``transcript_usage.py`` and ``agent_effort.py`` for the artifact-savings baseline rather
than adding a telemetry framework. It reads harness transcripts and the cell's files and does
arithmetic only; it judges nothing about the review.

Usage::

    python3 docs/research/tools/interface_metrics.py cell --transcript ROOT.jsonl \\
        --skill-root DIR --task-root DIR [--worker agent-*.jsonl ...] [--result stdout.json]
    python3 docs/research/tools/interface_metrics.py fields FILE [FILE ...]
    python3 docs/research/tools/interface_metrics.py static --skill-root DIR

``cell`` prints one JSON object:

- ``usage``: ``transcript_usage.py`` totals for the root, each worker, and all together (turns,
  tool calls, input, cache writes and reads, output, thinking), plus the observed model and
  effort on every assistant line (``settings``).
- ``harness``: from ``--result``, the harness's own turn count, duration, cost, spawned-agent count
  and permission denials; ``null`` fields when not supplied.
- ``finalizer``: every root Bash call that runs ``finalize_review.py`` or ``compose_review.py`` with
  Python and without ``--help`` or ``--example``, with its exit: ``failed`` when the tool result is
  an error or prints ``Exit code N``, ``exit=N`` or ``failed with exit N`` for a nonzero N, the
  forms a wrapped call reports; ``repair_loops`` counts failed calls. ``validation`` is the first
  successful call's result time, then the root turns, tool calls and seconds after it to the last
  assistant line. With no finalizer call, ``validation`` is ``unavailable``; ``after_last_addendum``
  does the same from the last write to an ``addenda/`` JSON file, when one exists.
- ``loads``: each root load of a skill file, classified ``entrypoint``, ``reference`` or
  ``script-source``, and each helper run with ``--help`` or ``--example`` as ``helper-help`` or
  ``helper-example``. A load is a Read of a skill file; a Bash reader (``cat``/``sed``/``head``/
  ``tail``/``less``/``bat``/``grep``/``rg``/``awk``/``nl``) naming a skill file it does not run, one
  load per file named; an ``open("...")`` of a skill file in inline Python; or one helper
  invocation. A Bash call is read after substituting one-line ``NAME=value`` assignments and
  unrolling simple ``for`` loops. Relative paths resolve against the directory the call starts in:
  the ``cwd`` the harness records on the previous call's result line, or for a transcript's first
  call its own line's ``cwd``. The call's own line is not used later, because in a message with
  several tool calls it can record where the call ended. Where no line records a directory, the
  directory is tracked from the task root through every top-level ``cd``. Within a call, top-level
  ``cd`` commands move it. Heuristic limits: a ``cd`` inside a subshell is not tracked, ``cd ~`` and
  ``cd -`` resolve literally as path names, a reader given a directory rather than a file counts
  nothing, and an inline-Python ``open()`` resolves against the directory at the end of its call.
  Each item lists its call's loads with the call's result bytes and words as delivered (Read
  results include the harness's line-number prefixes). Each total counts invocations of its kind
  and the output of calls making only that kind of load; a call mixing kinds puts its output in
  ``mixed``, because one result cannot be split by kind. ``worker_loads`` applies the same rule to
  each worker, adds reads of verifier bundle files as ``bundle``, and counts the dispatch prompt
  each worker received.
- ``authored``: every Write/Edit/MultiEdit and heredoc Bash write, root and workers, with
  characters by artifact class, and the ``fields`` inventory of each JSON artifact the model wrote
  that still exists under the task root (``written_by: tool``). A known-shape JSON file under
  ``work/`` that no observed write names, such as one a program inside a heredoc wrote, is
  inventoried too with ``written_by: unobserved``; a helper's bundle ``input.json`` is excluded.

``fields`` prints the inventory alone. For a composition input, addendum, verifier input, raw
verifier return or fingerprint input, it counts leaf values and words and splits them into
``mechanical`` fields, which an authoritative packet, store, input, record or helper already
determines, and ``judgment`` fields the model decides; every fingerprint-input leaf is mechanical,
and a composition's ``run.coverage`` is a judgment the composer only checks. The table below is
the small authored-field inventory the consumer map in
``docs/research/review-code-artifact-savings-2026-09-22/consumers.md`` explains; unknown shapes
count as ``other``.

``static`` measures what a load could cost at one skill revision, independent of any run: UTF-8
bytes and whitespace-separated words of ``SKILL.md``, each ``references/*.md`` file and each
``scripts/*.py`` source, and the stdout of every helper's ``--help`` and ``--example`` variant the
runtime text names. A reference count is not a load; ``cell`` measures what a run read.

Exit codes: 0 printed; 2 an unreadable transcript, result or artifact, or a helper that fails,
named on stderr.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agent_effort  # noqa: E402
import transcript_usage  # noqa: E402

READERS = re.compile(r"(?:^|[\s;&|(])(?:cat|sed|head|tail|less|bat|batcat|grep|rg|awk|nl)\b")
LOOP = re.compile(r"for\s+(\w+)\s+in\s+([^;\n]+?)\s*(?:;|\n)\s*do\b(.*?)(?:;|\n)\s*done\b", re.S)
RUN_SCRIPT = re.compile(r"python3?\s+(?:-\S+\s+)*[\"']?(?P<path>[^\s\"']*?(?P<name>[\w]+\.py))[\"']?(?P<args>[^\n|;&]*)")
FINALIZERS = ("finalize_review.py", "compose_review.py")
FAILED_TEXT = re.compile(r"(?m)^(?:Exit code [1-9]|\s*exit(?: code)?\s*[=:]\s*[1-9])|failed with exit [1-9]")

# (artifact, JSON-pointer pattern) -> class. The first matching pattern wins; "*" is one segment.
# An empty list is one leaf at its own pointer, so a list whose items are wholly mechanical names
# both the list and its items; a list of mixed items (files, tasks, delta) stays a judgment when empty.
MECHANICAL = {
    "composition": ["/run/target_kind", "/run/target", "/run/tree", "/run/change_description", "/run/specs",
                    "/run/specs/*", "/run/head", "/run/base_ref", "/run/base_sha", "/run/merge_base", "/run/context",
                    "/run/issues", "/run/issues/*", "/run/repository_url", "/run/merged", "/run/publication_authorized",
                    "/run/prior_head", "/record/repository", "/record/paths/*", "/record/files/*/path",
                    "/record/check_evidence/*/head", "/record/verification/batches",
                    "/record/verification/batches/*/name",
                    "/record/verification/batches/*/phase", "/record/verification/batches/*/bundle",
                    "/record/verification/batches/*/raw_return", "/record/verification/batches/*/accounting",
                    "/record/verification/batches/*/operation", "/record/verification/allowance/*",
                    "/record/verification/tasks/*/batch", "/record/verification/tasks/*/ruling"],
    "addendum": ["/format", "/workflow", "/record", "/record_format", "/reviewed_head", "/final_head",
                 "/delta/*/path", "/check_evidence/*/head", "/verification/batches", "/verification/batches/*/name",
                 "/verification/batches/*/phase", "/verification/batches/*/bundle",
                 "/verification/batches/*/raw_return", "/verification/batches/*/accounting",
                 "/verification/batches/*/operation", "/verification/allowance/*",
                 "/verification/tasks/*/batch", "/verification/tasks/*/ruling"],
    "verifier-input": ["/run/*", "/batch/*", "/run_policy"],
    "raw-return": ["/manifest_sha256"],
}
# Every leaf of these shapes transcribes an authority: the packet, git, or the caller's specs.
ALL_MECHANICAL = ("fingerprint-input",)


def fail(message: str) -> None:
    print(f"interface_metrics: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_lines(path: str) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as handle:
            lines = []
            for raw in handle:
                try:
                    item = json.loads(raw)
                except ValueError:
                    continue
                if isinstance(item, dict):
                    lines.append(item)
            return lines
    except OSError as error:
        fail(f"cannot read {path}: {error.strerror}")
    return []


def stamp(line: dict) -> Optional[datetime]:
    return transcript_usage.parse_timestamp(line.get("timestamp"))


def text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return ""


def calls_and_results(lines: list[dict]) -> tuple[list[dict], dict]:
    """Tool calls in order, each with its result text, error flag and result time."""
    calls, results = [], {}
    for line in lines:
        message = line.get("message") or {}
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict):
                continue
            if line.get("type") == "assistant" and item.get("type") == "tool_use":
                if not any(call["id"] == item.get("id") for call in calls):
                    calls.append({"id": item.get("id"), "name": item.get("name"), "input": item.get("input") or {},
                                  "at": stamp(line), "request": line.get("requestId"),
                                  "cwd": line.get("cwd") if isinstance(line.get("cwd"), str) else None})
            elif line.get("type") == "user" and item.get("type") == "tool_result":
                results[item.get("tool_use_id")] = {"text": text_of(item.get("content")),
                                                   "error": bool(item.get("is_error")), "at": stamp(line),
                                                   "cwd": line.get("cwd") if isinstance(line.get("cwd"), str) else None}
    return calls, results


def words(text: str) -> int:
    return len(text.split())


def classify_path(path: str, skill_root: str) -> Optional[str]:
    root = skill_root.rstrip("/") + "/"
    if not path.startswith(root):
        return None
    rel = path[len(root):]
    if rel == "SKILL.md":
        return "entrypoint"
    if rel.startswith("references/"):
        return "reference"
    if rel.startswith("scripts/") and rel.endswith(".py"):
        return "script-source"
    return "other-skill-file"


def expand(command: str) -> str:
    """Substitute one-line ``NAME=value`` assignments and unroll simple ``for`` loops.

    A loop ``for V in A B C; do BODY; done`` becomes BODY once per item with ``$V`` replaced, so each
    helper call inside it counts. Nothing else is interpreted.
    """
    values = {}
    for name, value in re.findall(r"(?m)^\s*(?:export\s+)?([A-Za-z_]\w*)=(\S+)\s*$", command):
        values[name] = value.strip("\"'")
    for name in sorted(values, key=len, reverse=True):
        command = re.sub(r"\$\{%s\}|\$%s\b" % (name, name), lambda _: values[name], command)

    def unroll(match):
        variable, items, body = match.group(1), match.group(2).split(), match.group(3)
        return "\n".join(re.sub(r"\$\{%s\}|\$%s\b" % (variable, variable), lambda _: item, body) for item in items)
    return LOOP.sub(unroll, command)


def resolve(path: str, cwd: str) -> str:
    return os.path.normpath(path if path.startswith("/") else os.path.join(cwd, path))


def bash_loads(command: str, skill_root: str, cwd: str) -> tuple[list[tuple[str, str]], str]:
    """Every load one Bash call makes, in order, and the working directory it leaves.

    The harness keeps the shell's directory between calls, so a top-level ``cd`` persists and
    relative ``scripts/`` or ``references/`` paths resolve against it. Each helper run with
    ``--help`` or ``--example`` is one load; each reader command naming a skill file or a
    verifier bundle file it does not run is one load; each ``open("...")`` of a skill file inside
    inline Python is one load. A ``cd`` inside a subshell is not tracked.
    """
    found: list[tuple[str, str]] = []
    command = expand(command)
    for segment in re.split(r"\n|&&|\|\||;", command):
        move = re.match(r"\s*cd\s+[\"']?([^\s\"']+)[\"']?\s*$", segment)
        if move:
            cwd = resolve(move.group(1), cwd)
            continue
        executed = set()
        for match in RUN_SCRIPT.finditer(segment):
            path = resolve(match.group("path"), cwd)
            executed.add(path)
            if classify_path(path, skill_root) != "script-source":
                continue
            if re.search(r"(?:^|\s)(?:--help|-h)(?:\s|$)", match.group("args")):
                found.append(("helper-help", path))
            elif re.search(r"(?:^|\s)--example(?:\s|$)", match.group("args")):
                found.append(("helper-example", path))
        if READERS.search(segment):
            for token in re.findall(r"[\"']?([\w./-]*(?:SKILL\.md|\.md|\.py|\.json))[\"']?", segment):
                path = resolve(token, cwd)
                kind = classify_path(path, skill_root)
                if path in executed:
                    continue
                if kind in ("entrypoint", "reference", "script-source"):
                    found.append((kind, path))
                elif kind is None and re.search(r"/(brief\.md|manifest\.json)$", path):
                    found.append(("bundle", path))
    if re.search(r"python3?\s+(?:-c\b|-\s)", command):
        for token in re.findall(r"open\(\s*[\"']([^\"']+)[\"']", command):
            path = resolve(token, cwd)
            if classify_path(path, skill_root) in ("entrypoint", "reference", "script-source"):
                found.append((classify_path(path, skill_root), path))
    return found, cwd


def loads(calls: list[dict], results: dict, skill_root: str, cwd: str) -> dict:
    """Loads per call, with totals: each kind's invocations and the output of calls of that kind alone.

    A call that makes loads of more than one kind delivers one result the tool cannot split, so its
    bytes and words go to ``mixed`` rather than to any kind; its invocations still count.
    """
    items = []
    previous = None
    for call in calls:
        data = call["input"]
        # A call starts where the previous call's result left the shell. A tool_use line can record
        # where its own call ended (seen in multi-tool messages), so it serves only for the first call.
        recorded = results.get(previous["id"], {}).get("cwd") if previous else call["cwd"]
        previous = call
        if call["name"] == "Read":
            path = str(data.get("file_path", ""))
            kind = classify_path(path, skill_root)
            if kind is None and re.search(r"/(brief\.md|manifest\.json)$", path):
                kind = "bundle"
            found = [(kind, path)] if kind in ("entrypoint", "reference", "script-source", "bundle") else []
        elif call["name"] == "Bash":
            found, cwd = bash_loads(str(data.get("command", "")), skill_root, recorded or cwd)
        else:
            found = []
        if not found:
            continue
        text = results.get(call["id"], {}).get("text", "")
        items.append({"tool": call["name"], "loads": [{"kind": kind, "what": what} for kind, what in found],
                      "bytes": len(text.encode("utf-8")), "words": words(text)})
    totals: dict = {}
    mixed = {"calls": 0, "bytes": 0, "words": 0}
    for item in items:
        kinds = {load["kind"] for load in item["loads"]}
        for load in item["loads"]:
            totals.setdefault(load["kind"], {"count": 0, "bytes": 0, "words": 0})["count"] += 1
        target = totals[kinds.pop()] if len(kinds) == 1 else mixed
        if target is mixed:
            mixed["calls"] += 1
        target["bytes"] += item["bytes"]
        target["words"] += item["words"]
    return {"items": items, "totals": totals, "mixed": mixed}


def finalizer(calls: list[dict], results: dict, lines: list[dict]) -> dict:
    runs = []
    for call in calls:
        command = str(call["input"].get("command", "")) if call["name"] == "Bash" else ""
        if not any(match.group("name") in FINALIZERS
                   and not re.search(r"(?:^|\s)(?:--help|-h|--example)(?:\s|$)", match.group("args"))
                   for match in RUN_SCRIPT.finditer(command)):
            continue
        result = results.get(call["id"], {})
        failed = result.get("error", False) or bool(FAILED_TEXT.search(result.get("text", "")))
        runs.append({"command": command, "failed": failed, "at": result.get("at")})
    ok = [run for run in runs if not run["failed"] and run["at"] is not None]
    report = {"invocations": len(runs), "failed": sum(run["failed"] for run in runs),
              "repair_loops": sum(run["failed"] for run in runs),
              "runs": [{"command": run["command"], "failed": run["failed"],
                        "at": run["at"].isoformat() if run["at"] else None} for run in runs]}
    report["validation"] = tail(lines, ok[0]["at"]) if ok else {
        "status": "unavailable", "reason": "no successful finalize_review.py or compose_review.py call"}
    return report


def tail(lines: list[dict], start: datetime) -> dict:
    """Root turns, tool calls and seconds after one instant, to the last assistant line."""
    requests, tools, last = set(), set(), None
    for line in lines:
        at = stamp(line)
        if line.get("type") != "assistant" or at is None or at <= start:
            continue
        requests.add(line.get("requestId") or id(line))
        for item in (line.get("message") or {}).get("content") or []:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                tools.add(item.get("id"))
        last = at if last is None or at > last else last
    return {"status": "captured", "at": start.isoformat(), "turns_after": len(requests),
            "tool_calls_after": len(tools),
            "seconds_after": round((last - start).total_seconds(), 3) if last else 0.0}


def written(calls: list[dict]) -> list[dict]:
    out = []
    for call in calls:
        data, path, chars = call["input"], None, 0
        if call["name"] == "Write":
            path, chars = data.get("file_path"), len(str(data.get("content", "")))
        elif call["name"] == "Edit":
            path, chars = data.get("file_path"), len(str(data.get("new_string", "")))
        elif call["name"] == "MultiEdit":
            path = data.get("file_path")
            chars = sum(len(str(edit.get("new_string", ""))) for edit in data.get("edits", []) if isinstance(edit, dict))
        elif call["name"] == "Bash" and "<<" in str(data.get("command", "")):
            match = transcript_usage.WRITE_PATH_RE.search(str(data["command"]))
            path, chars = (match.group(1) if match else None), len(str(data["command"]))
        if path:
            out.append({"path": path, "tool": call["name"], "chars": chars})
    return out


def artifact_class(path: str) -> str:
    name = os.path.basename(path)
    if "/addenda/" in path and name.endswith(".json"):
        return "addendum"
    if name.startswith("composition") and name.endswith(".json"):
        return "composition"
    if "raw-return" in name:
        return "raw-return"
    if name == "report.md":
        return "report"
    if name.endswith(".json") and ("verif" in name or "batch" in name or "input" in name):
        return "verifier-input"
    return "other"


def matches(pattern: str, pointer: str) -> bool:
    left, right = pattern.split("/"), pointer.split("/")
    return len(left) == len(right) and all(a in ("*", b) for a, b in zip(left, right))


def leaves(value: Any, pointer: str = ""):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, f"{pointer}/{key}")
    elif isinstance(value, list):
        if not value:
            yield pointer, value
        for index, item in enumerate(value):
            yield from leaves(item, f"{pointer}/{index}")
    else:
        yield pointer, value


def shape(document: Any) -> str:
    if not isinstance(document, dict):
        return "other"
    if str(document.get("format", "")).startswith("implementation-gate-addendum/"):
        return "addendum"
    if "manifest_sha256" in document and "candidates" in document:
        return "raw-return"
    if {"run", "batch"} <= document.keys() and ("candidates" in document or "premises" in document):
        return "verifier-input"
    if {"run", "summary"} <= document.keys() and "schema" not in document:
        return "composition"
    if "pr" in document and document.keys() <= {"pr", "issues", "specs", "guidance"}:
        return "fingerprint-input"
    return "other"


def inventory(path: str) -> dict:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        fail(f"cannot read JSON artifact {path}: {error}")
    kind = shape(document)
    counts = {name: {"fields": 0, "words": 0} for name in ("mechanical", "judgment")}
    sections: dict = {}
    for pointer, value in leaves(document):
        group = "judgment"
        if kind in ALL_MECHANICAL or (kind in MECHANICAL and any(matches(p, pointer) for p in MECHANICAL[kind])):
            group = "mechanical"
        size = words(value) if isinstance(value, str) else 0
        counts[group]["fields"] += 1
        counts[group]["words"] += size
        section = sections.setdefault(pointer.split("/")[1] if pointer.count("/") else "(root)",
                                      {"fields": 0, "words": 0})
        section["fields"] += 1
        section["words"] += size
    return {"path": path, "shape": kind, "bytes": Path(path).stat().st_size, **counts, "sections": sections}


def usage_block(paths: list[str]) -> dict:
    per = []
    total = transcript_usage.Usage("total")
    for path in paths:
        usage = transcript_usage.read_transcript(path)
        total.absorb(usage)
        per.append({**usage.as_dict(), "path": path, "settings": agent_effort.scan(path)})
    return {"transcripts": per, "total": total.as_dict()}


def cell(args: argparse.Namespace) -> dict:
    skill_root = str(Path(args.skill_root).resolve())
    task_root = str(Path(args.task_root).resolve())
    root_lines = load_lines(args.transcript)
    calls, results = calls_and_results(root_lines)
    report: dict = {"format": "interface-metrics/1", "transcript": args.transcript, "skill_root": skill_root,
                    "task_root": task_root}
    report["usage"] = {"root": usage_block([args.transcript]), "workers": usage_block(args.worker) if args.worker else None,
                       "all": usage_block([args.transcript, *args.worker])["total"]}
    harness = {"num_turns": None, "duration_ms": None, "total_cost_usd": None, "subagents_spawned": None,
               "permission_denials": None}
    if args.result:
        try:
            result = json.loads(Path(args.result).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            fail(f"cannot read result {args.result}: {error}")
        harness = {"num_turns": result.get("num_turns"), "duration_ms": result.get("duration_ms"),
                   "total_cost_usd": result.get("total_cost_usd"),
                   "subagents_spawned": (result.get("subagent_stats") or {}).get("spawned"),
                   "permission_denials": len(result.get("permission_denials") or [])}
    report["harness"] = harness
    report["finalizer"] = finalizer(calls, results, root_lines)
    addendum_writes = [call for call in calls if call["name"] in ("Write", "Edit")
                       and "/addenda/" in str(call["input"].get("file_path", ""))
                       and results.get(call["id"], {}).get("at")]
    report["after_last_addendum"] = (tail(root_lines, results[addendum_writes[-1]["id"]]["at"]) if addendum_writes
                                     else {"status": "unavailable", "reason": "no addendum write"})
    report["loads"] = loads(calls, results, skill_root, task_root)
    worker_loads, authored_calls = [], [dict(entry, agent="root") for entry in written(calls)]
    for path in args.worker:
        lines = load_lines(path)
        worker_calls, worker_results = calls_and_results(lines)
        first = next((line for line in lines if line.get("type") == "user"), None)
        prompt = text_of((first or {}).get("message", {}).get("content")) if first else ""
        worker_loads.append({"transcript": path, "dispatch_prompt": {"bytes": len(prompt.encode("utf-8")),
                                                                     "words": words(prompt)},
                             **loads(worker_calls, worker_results, skill_root, task_root)})
        authored_calls.extend(dict(entry, agent=os.path.basename(path)) for entry in written(worker_calls))
    report["worker_loads"] = worker_loads
    by_class: dict = {}
    for entry in authored_calls:
        entry["class"] = artifact_class(entry["path"])
        total = by_class.setdefault(entry["class"], {"writes": 0, "chars": 0})
        total["writes"] += 1
        total["chars"] += entry["chars"]
    tool_written = {entry["path"] for entry in authored_calls
                    if entry["path"].endswith(".json") and entry["path"].startswith(task_root)
                    and os.path.isfile(entry["path"])}
    fields = [dict(inventory(path), written_by="tool") for path in sorted(tool_written)]
    for path in sorted(Path(task_root, "work").rglob("*.json")):
        if str(path) in tool_written or (path.name == "input.json" and (path.parent / "manifest.json").exists()):
            continue
        try:
            found = shape(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
        if found != "other":
            fields.append(dict(inventory(str(path)), written_by="unobserved"))
    report["authored"] = {"writes": authored_calls, "by_class": by_class, "fields": fields}
    return report


HELPERS = (("review_context.py", "--help"), ("context_fingerprint.py", "--help"), ("context_fingerprint.py", "--example"),
           ("compose_review.py", "--help"), ("compose_review.py", "--example"),
           ("compose_review.py", "--example", "--profile", "implementation-gate"),
           ("build_verifier_prompt.py", "--help"), ("build_verifier_prompt.py", "--example"),
           ("account_verifier_return.py", "--help"), ("finalize_review.py", "--help"),
           ("forge_packet.py", "--help"), ("run_events.py", "--help"))


def size(raw: bytes) -> dict:
    return {"bytes": len(raw), "words": len(raw.decode("utf-8").split())}


def static(skill_root: str) -> dict:
    root = Path(skill_root).resolve()
    try:
        files = {"SKILL.md": size((root / "SKILL.md").read_bytes())}
        files.update({p.relative_to(root).as_posix(): size(p.read_bytes()) for p in sorted((root / "references").glob("*.md"))})
        sources = {p.relative_to(root).as_posix(): size(p.read_bytes()) for p in sorted((root / "scripts").glob("*.py"))
                   if not p.name.startswith("test_")}
    except OSError as error:
        fail(f"cannot read {root}: {error}")
    helpers = {}
    for script, *flags in HELPERS:
        command = [sys.executable, str(root / "scripts" / script), *flags]
        result = subprocess.run(command, capture_output=True)
        if result.returncode != 0:
            fail(f"{' '.join(command)} exited {result.returncode}")
        helpers[" ".join([script, *flags])] = size(result.stdout)
    references = [value for name, value in files.items() if name.startswith("references/")]
    return {"format": "interface-static/1", "skill_root": str(root), "entrypoint": files["SKILL.md"],
            "references": {"count": len(references), "bytes": sum(v["bytes"] for v in references),
                           "words": sum(v["words"] for v in references)},
            "files": files, "helper_output": helpers, "script_sources": sources}


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    cell_parser = commands.add_parser("cell")
    cell_parser.add_argument("--transcript", required=True)
    cell_parser.add_argument("--worker", action="append", default=[])
    cell_parser.add_argument("--skill-root", required=True)
    cell_parser.add_argument("--task-root", required=True)
    cell_parser.add_argument("--result")
    fields_parser = commands.add_parser("fields")
    fields_parser.add_argument("files", nargs="+")
    commands.add_parser("static").add_argument("--skill-root", required=True)
    args = parser.parse_args(argv)
    if args.command == "cell":
        output = cell(args)
    elif args.command == "static":
        output = static(args.skill_root)
    else:
        output = [inventory(path) for path in args.files]
    print(json.dumps(output, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
