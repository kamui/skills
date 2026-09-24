#!/usr/bin/env python3
"""Audit one benchmark attempt's transcripts for isolation and extract its native payload.

Usage::

    python3 attempt_audit.py --arm claude-builtin|codex|review-code --attempt-dir <dir> \\
        --clone <path> [--allowed <path>...] [--allowed-prefix <prefix>...] [--json]

``review-code`` attempts read like ``claude-builtin`` ones (root plus sub-agent transcripts) but
need no built-in header; the skill's private store lives under a ``/tmp/review-code-`` prefix,
which the caller allows with ``--allowed-prefix``.

Reads the transcripts the dispatch wrapper collected under ``<attempt-dir>``:
for ``claude-builtin`` the ``home/.claude/projects/**/*.jsonl`` files (root and
``subagents/agent-*.jsonl``), for ``codex`` the ``home/.codex/sessions/**/rollout-*.jsonl``
files. Every shell command and every file-tool path is listed; a path outside the
clone, the attempt directory and the fresh home, or a command that names a
network tool (``curl``, ``wget``, ``gh``, ``git fetch``/``pull``/``push``/``clone``,
``pip``, ``npm install``, ``ssh``), is a violation. Codex walks up the directory tree
looking for ``AGENTS.md``/``AGENTS.override.md`` and the built-in looks for ``CLAUDE.md``;
a probe of such a guidance file in an ancestor of the clone is recorded under
``guidance_probes`` and is a violation only if that file exists. The built-in's prompt header
line and the Codex rubric marker are checked so the arm that ran is the arm
that was dispatched, and the executed diff command is recorded.

Writes ``audit.json`` in the attempt directory and, for ``claude-builtin``, copies
the final result text and any ``ReportFindings`` input into ``payload.json``.

Exit codes: 0 no violation; 1 one or more violations (listed on stdout);
2 unreadable transcripts, named on stderr.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

NETWORK = re.compile(r"(?<![\w-])(curl|wget|gh|ssh|scp|pip3?|npm|pnpm|yarn|cargo|go)\s+|git\s+(fetch|pull|push|clone|ls-remote|remote\s+add)\b")
BUILTIN_HEADER = re.compile(r"^`(high effort|medium effort|low effort|minimal prompt)[^`]*`$", re.M)
CODEX_RUBRIC = "You are acting as a reviewer for a proposed code change"
DIFF_CMD = re.compile(r"git\s+diff\s+[^;&|\n]*")
GUIDANCE = ("AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "CLAUDE.local.md")
CODEX_CMD = re.compile(r'cmd:\s*"((?:[^"\\]|\\.)*)"')


def load_lines(path: Path):
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield number, json.loads(line)
            except json.JSONDecodeError:
                raise ValueError(f"{path}:{number}: malformed JSON")


HOME_DIR = None


def paths_in(text: str):
    found = re.findall(r"(?<![\w.~}\)\"'])(/[\w.@+-][\w./@+-]*)", text or "")
    tilde = re.findall(r"(?<![\w.])~(/[\w./@+-]*)", text or "")
    return found + [HOME_DIR + t for t in tilde if HOME_DIR]


PREFIXES: list = []


def inside(path: str, roots) -> bool:
    real = os.path.realpath(path)
    if any(real.startswith(pre) for pre in PREFIXES):
        return True
    return any(real == r or real.startswith(r + os.sep) for r in roots)


def audit_claude(attempt: Path, roots):
    commands, reads, headers, findings_calls, texts = [], [], [], [], []
    files = sorted((attempt / "home" / ".claude" / "projects").rglob("*.jsonl"))
    for path in files:
        for _, record in load_lines(path):
            message = record.get("message") or {}
            content = message.get("content")
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            for block in content or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text" and record.get("type") == "user":
                    m = BUILTIN_HEADER.search(block.get("text", ""))
                    if m:
                        headers.append(m.group(0))
                if block.get("type") == "text" and record.get("type") == "assistant":
                    texts.append(block.get("text", ""))
                if block.get("type") == "tool_use":
                    name, inp = block.get("name"), block.get("input") or {}
                    if name == "Bash":
                        commands.append(inp.get("command", ""))
                    elif name in ("Read", "Glob", "Grep", "Write", "Edit"):
                        for key in ("file_path", "path"):
                            if inp.get(key):
                                reads.append(inp[key])
                    elif name == "ReportFindings":
                        findings_calls.append(inp)
    return files, commands, reads, headers, findings_calls, texts


def audit_codex(attempt: Path, roots):
    commands, rubric, texts = [], 0, []
    files = sorted((attempt / "home" / ".codex" / "sessions").rglob("rollout-*.jsonl"))
    for path in files:
        for _, record in load_lines(path):
            payload = record.get("payload") or {}
            if record.get("type") == "response_item":
                kind = payload.get("type")
                if kind in ("function_call", "custom_tool_call", "local_shell_call"):
                    args = payload.get("arguments") or payload.get("input") or ""
                    if isinstance(args, str):
                        try:
                            parsed = json.loads(args)
                        except json.JSONDecodeError:
                            parsed = {"cmd": args}
                    else:
                        parsed = args
                    cmd = parsed.get("cmd") or parsed.get("command") or (parsed.get("action") or {}).get("command") if isinstance(parsed, dict) else str(parsed)
                    text = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
                    inner = CODEX_CMD.findall(text)
                    commands.extend(c.encode().decode("unicode_escape") for c in inner) if inner else commands.append(text)
                elif kind == "message" and payload.get("role") == "assistant":
                    for block in payload.get("content") or []:
                        if isinstance(block, dict) and block.get("text"):
                            texts.append(block["text"])
            blob = json.dumps(payload)
            if CODEX_RUBRIC in blob:
                rubric += 1
    return files, commands, rubric, texts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--arm", required=True, choices=["claude-builtin", "codex", "review-code"])
    parser.add_argument("--attempt-dir", required=True)
    parser.add_argument("--clone", required=True)
    parser.add_argument("--allowed", nargs="*", default=[])
    parser.add_argument("--allowed-prefix", nargs="*", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    attempt = Path(args.attempt_dir)
    global HOME_DIR
    HOME_DIR = os.path.realpath(str(attempt / "home"))
    roots = [os.path.realpath(p) for p in [args.clone, str(attempt), *args.allowed]]
    PREFIXES[:] = list(args.allowed_prefix)
    violations = []
    try:
        if args.arm in ("claude-builtin", "review-code"):
            files, commands, reads, headers, calls, texts = audit_claude(attempt, roots)
            report = {"transcripts": [str(f) for f in files], "prompt_headers": headers,
                      "report_findings_calls": len(calls)}
            if args.arm == "claude-builtin" and not headers:
                violations.append("no built-in prompt header found: the built-in did not run")
            if args.arm == "review-code" and headers:
                violations.append("a built-in review prompt ran inside a review-code attempt")
            payload = {"final_text": texts[-1] if texts else None, "report_findings": calls}
            (attempt / "payload.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        else:
            files, commands, rubric, texts = audit_codex(attempt, roots)
            reads = []
            report = {"transcripts": [str(f) for f in files], "rubric_markers": rubric}
            if rubric == 0:
                violations.append("Codex rubric marker absent: review preset did not run")
    except (OSError, ValueError) as error:
        print(f"attempt_audit.py: {error}", file=sys.stderr)
        return 2
    if not report["transcripts"]:
        print("attempt_audit.py: no transcripts found under the attempt's home", file=sys.stderr)
        return 2
    clone_real = os.path.realpath(args.clone)
    ancestors = set()
    d = clone_real
    while d and d != os.path.dirname(d):
        d = os.path.dirname(d)
        ancestors.add(d)
    probes = []
    for cmd in commands:
        if NETWORK.search(cmd):
            violations.append(f"network-capable command: {cmd[:200]}")
        for p in paths_in(cmd):
            if inside(p, roots) or p.startswith(("/usr/", "/bin/", "/dev/", "/proc/", "/etc/")):
                continue
            if os.path.basename(p) in GUIDANCE and os.path.dirname(os.path.realpath(p)) in ancestors:
                probes.append(p)
                if os.path.exists(p):
                    violations.append(f"guidance file exists in an ancestor of the clone and was probed: {p}")
                continue
            violations.append(f"path outside allowed roots in command: {p}")
    for p in reads:
        if p.startswith("/") and not inside(p, roots):
            violations.append(f"file tool read outside allowed roots: {p}")
    diffs = [m.group(0) for cmd in commands for m in DIFF_CMD.finditer(cmd)]
    report.update({"commands": commands, "file_tool_paths": reads, "diff_commands": diffs, "guidance_probes": sorted(set(probes)),
                   "violations": violations, "allowed_roots": roots})
    (attempt / "audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for v in violations:
            print(v)
        print(f"{len(commands)} commands, {len(reads)} file-tool paths, {len(diffs)} diff commands, "
              f"{len(violations)} violations -> {attempt / 'audit.json'}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
