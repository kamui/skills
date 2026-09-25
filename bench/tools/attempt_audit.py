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
clone, the attempt directory and the fresh home that names something on disk when the audit
runs (a glob by any match; absent ones are listed as ``absent_outside_paths``; a symlink inside the
roots that was made before ``timing.json``'s dispatch instant may lead out of them, as a provisioned
venv's interpreter does), or a command that runs a
network tool in command position (``curl``, ``wget``, ``gh``, ``ssh``, ``scp``, ``cargo``,
``git fetch``/``pull``/``push``/``clone``; ``npm``, ``pnpm``, ``yarn`` or ``pip`` with a subcommand
that reaches a registry; ``go`` unless the command sets ``GOPROXY=off`` and ``GOTOOLCHAIN=local``
before it), is a violation. Every relative path with a ``..`` segment, or
with a dot-led glob segment such as ``.*`` that bash can expand to ``..`` (a whole word, or a run
inside one after whitespace, a redirection, ``=``, ``:``, a quote or a bracket), and every
relative operand once a ``cd`` or a Codex call's ``workdir`` has moved off the clone, is resolved
against the command's working directory (the clone or that ``workdir``, following ``cd`` across
``;``, ``&&``, ``||`` and ``|``) and judged like an absolute path; a ``workdir`` outside the
allowed roots is itself a violation. Codex walks up the directory tree
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
import datetime
import fnmatch
import glob
import json
import os
from pathlib import Path
import re
import shlex
import sys

# A tool counts only in command position: at the start, after a separator, a ``do``/``then``-style
# keyword or a wrapper such as ``env``/``xargs``/``timeout N``, or opening a ``-c`` script, past any
# ``NAME=value`` assignments.
# A shell given a script: ``sh -c``, ``bash -lc``, ``zsh -fc``, ``bash --norc -c``.
SHELL_C = r"\b(?:ba|z|da|k)?sh\s+(?:-\S+\s+)*?-[A-Za-z]*c[A-Za-z]*\s+"
NETWORK = re.compile(
    r"(?:^|[;&|(){}\n`]|\$\(|" + SHELL_C + r"['\"]|\b(?:do|then|else|exec|xargs|env|nohup|time|command|sudo)\s)"
    r"\s*(?P<assign>(?:[A-Za-z_]\w*=[^\s;&|()]*\s+)*)(?:timeout\s+(?:-\S+\s+)*\S+\s+)?"
    r"(?:(?P<tool>curl|wget|gh|ssh|scp|pip3?|npm|pnpm|yarn|cargo|go)\s+(?P<sub>\S*)"
    r"|git\s+(?:fetch|pull|push|clone|ls-remote|remote\s+add)\b)")
# The package managers reach a registry only through these subcommands; the rest (a build, a script
# run, ``--version``) work offline, as target (o)'s allowance uses pnpm.
FETCHING = {"npm": {"install", "i", "add", "ci", "update", "upgrade", "up", "dlx", "exec", "x", "fetch", "publish",
                    "view", "info", "outdated", "audit", "create", "init"},
            "pip": {"install", "download"}}
# A heredoc: its header line (group 1), then the body up to the delimiter line or the end.
HEREDOC = re.compile(r"^([^\n]*<<-?\s*(['\"]?)(\w+)\2[^\n]*)\n.*?(?:\n[ \t]*\3[ \t]*(?=\n|\Z)|\Z)", re.M | re.S)
BUILTIN_HEADER = re.compile(r"^`(high effort|medium effort|low effort|minimal prompt)[^`]*`$", re.M)
CODEX_RUBRIC = "You are acting as a reviewer for a proposed code change"
DIFF_CMD = re.compile(r"git\s+diff\s+[^;&|\n]*")
GUIDANCE = ("AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "CLAUDE.local.md")
CODEX_CMD = re.compile(r'cmd"?:\s*"((?:[^"\\]|\\.)*)"')
# One exec_command object literal whose values are strings or bare scalars, so its cmd and workdir pair up.
CODEX_OBJ = re.compile(r'\{((?:\s*"?[\w$]+"?\s*:\s*(?:"(?:[^"\\]|\\.)*"|[^,{}"\[\]]+)\s*,?)+)\}')
CODEX_FIELD = re.compile(r'"?([\w$]+)"?\s*:\s*(?:"((?:[^"\\]|\\.)*)"|[^,{}"\[\]]+)')
CODEX_WORKDIR = re.compile(r'(?:workdir|cwd|working_directory)"?\s*:\s*"((?:[^"\\]|\\.)*)"')


def commands_only(cmd: str) -> str:
    """``cmd`` with each heredoc body dropped, since a body is data, not commands, unless a shell
    reads it."""
    return HEREDOC.sub(lambda m: m.group(0) if re.search(r"\b(?:ba|z|da|k)?sh\b", m.group(1)) else m.group(1), cmd)


def unquoted(cmd: str) -> str:
    """``cmd`` with quoted text masked, since a quoted pattern or message is data (``rg "a|go b"``),
    except a script handed to a shell's ``-c`` and a ``$(...)`` inside double quotes, which run.
    Every character keeps its position, so a match in the result indexes the original."""
    out, i, quote, depth = [], 0, None, 0
    while i < len(cmd):
        c = cmd[i]
        if quote is None:
            if c == "\\":
                out.append(cmd[i:i + 2]); i += 2; continue
            if c in "'\"" and not re.search(SHELL_C + "$", cmd[:i]):
                quote = c
            out.append(c)
        elif c == quote and depth == 0 and not (quote == '"' and cmd[i - 1] == "\\"):
            quote = None
            out.append(c)
        elif quote == '"' and cmd.startswith("$(", i):
            depth += 1; out.append("$("); i += 2; continue
        elif depth:
            depth += c == "("
            depth -= c == ")"
            out.append(c)
        else:
            out.append("_")
        i += 1
    return "".join(out)


def go_env(text: str, m) -> dict:
    """The environment a ``go`` match runs with: variables exported earlier in ``text`` and not
    unset since, then the match's own prefix assignments, which reach that one command only."""
    env = {}
    assignment = re.compile(r"([A-Za-z_]\w*)=([^\s;&|()]*)")
    for e in re.finditer(r"\bexport\s+((?:[A-Za-z_]\w*=[^\s;&|()]*[ \t]*)+)|\bunset\s+((?:[A-Za-z_]\w*[ \t]*)+)",
                         text[:m.start()]):
        if e.group(1):
            env.update(assignment.findall(e.group(1)))
        else:
            for name in e.group(2).split():
                env.pop(name, None)
    env.update(assignment.findall(text[m.start("assign"):m.end("assign")]))
    return {k: v.strip("'\"") for k, v in env.items()}


def network_use(cmd: str) -> bool:
    """True when ``cmd`` runs a network tool; ``go`` is offline when it runs with ``GOPROXY=off``
    and ``GOTOOLCHAIN=local``, as the Go targets' allowances do."""
    text = commands_only(cmd)
    for m in NETWORK.finditer(unquoted(text)):
        tool, sub = m.group("tool"), m.group("sub")
        if tool == "go":
            env = go_env(text, m)
            if env.get("GOPROXY") == "off" and env.get("GOTOOLCHAIN") == "local":
                continue
        elif tool in ("npm", "pnpm", "yarn", "pip", "pip3"):
            if sub not in FETCHING["pip" if tool.startswith("pip") else "npm"]:
                continue
        return True
    return False


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
# The reviewer's dispatch instant (epoch seconds) from the attempt's timing.json, one second late
# because the stamp is truncated to the second.
DISPATCHED = None


SPLIT = re.compile(r"\s*(?:&&|\|\||;|\|)\s*")
# A path-like run starting a word or following whitespace (inside a quoted word), a redirection,
# `=`, `:`, a quote or a bracket.
RUN = re.compile(r"(?:^|(?<=[\s<>=:'\"(\[,]))([\w.@+*?\[\]-]*(?:/[\w.@+*?\[\]-]*)*)")
GLOB_CLASS = re.compile(r"\[[!^]?\]?(?:\[:\w+:\]|[^\]])*\]")


def climbs(path: str) -> str:
    """``path`` with ``..`` for every segment a shell glob could expand to ``..``: one that starts
    with a literal dot and matches ``..`` once each bracket expression is read as any character
    (bash 5.1 expands ``.*``, ``.?`` and ``.[.]`` to ``..``), so a globbed climb is judged like a
    literal one."""
    return "/".join(".." if s[:1] == "." and set(s) & set("*?[") and fnmatch.fnmatchcase("..", GLOB_CLASS.sub("?", s))
                    else s for s in path.split("/"))


def tokens(segment: str) -> list:
    try:
        return shlex.split(segment)
    except ValueError:  # an unbalanced quote, e.g. a quoted pattern split at a pipe
        return [t.strip("'\"") for t in segment.split()]


def paths_in(text: str, cwd: str, base: str = None):
    """Absolute paths, ``~`` paths expanded against the fresh home, every relative word or path
    run with a ``..`` segment, a dot-led glob segment that can expand to ``..`` counting as one
    (the command word, ``key=value`` and redirection operands, and paths inside a quoted script or
    a quoted path with spaces included), and every relative operand while the working directory is
    not ``base`` (the clone), each resolved against the command's working directory. The walk
    starts at ``cwd`` and tracks ``cd`` across ``;``, ``&&``, ``||`` and ``|``. A ``cd`` target is
    not itself a read (a fallback ``|| cd /tmp`` may never run); what is read relative to it is."""
    # A slash after a glob character (``python*/site-packages``) continues a relative word; it does
    # not start an absolute path. Glob characters inside an absolute path (``/opt/py*/x``) stay part
    # of it, so the whole path is judged against the roots; a first segment that starts with one
    # (``/*/x``) counts once another slash follows, so a regex class such as ``/[a-z]+`` does not.
    # A URL's authority (``http://localhost/``) is not a path: no match starts at a slash after ``:/``.
    found = [os.path.normpath(climbs(p)) for p in re.findall(
        r"(?<![\w.~}\)\"'*?\]])(?<!:/)(/(?:[\w.@+-]|[*?\[][\w.@+*?\[\]-]*/)[\w./@+*?\[\]-]*)", text or "")]
    tilde = [climbs(t) for t in re.findall(r"(?<![\w.])~(/[\w./@+*?\[\]-]*)", text or "")]
    relative = []
    here, base = cwd, base or cwd
    for segment in SPLIT.split(commands_only(text or "")):
        words = tokens(segment.strip().lstrip("({ "))
        for index, word in enumerate(words):
            if index == 1 and words[0] == "cd":
                if word.startswith("/") and os.path.normpath(climbs(word)) in found:
                    found.remove(os.path.normpath(climbs(word)))
                elif word.startswith("~/") and word[1:] in tilde:
                    tilde.remove(word[1:])
                continue
            for run in map(climbs, RUN.findall(word)):
                if run and not run.startswith("/") and ".." in run.split("/"):
                    relative.append(os.path.normpath(os.path.join(here, run)))
            operand = climbs(word.split("=", 1)[1] if word.startswith("-") and "=" in word else word)
            if operand and not operand.startswith(("/", "~", "-")) and (
                    ".." in operand.split("/") or (index and here != base)):
                relative.append(os.path.normpath(os.path.join(here, operand)))
        if words and words[0] == "cd":
            target = words[1] if len(words) > 1 else "~"
            if target != "-":
                target = HOME_DIR + target[1:] if target.startswith("~") and HOME_DIR else target
                here = os.path.normpath(os.path.join(here, climbs(target)))
    return list(dict.fromkeys(found + [os.path.normpath(HOME_DIR + t) for t in tilde if HOME_DIR] + relative))


PREFIXES: list = []


def present(path: str) -> bool:
    """Whether ``path`` names anything on disk now, a glob by any match. A path that names nothing
    was read by nothing (route strings, JSX closing tags, import specifiers, sed patterns)."""
    return bool(glob.glob(path)) if any(c in path for c in "*?[") else os.path.lexists(path)


def inside(path: str, roots) -> bool:
    real = os.path.realpath(path)
    if any(real.startswith(pre) for pre in PREFIXES):
        return True
    return any(real == r or real.startswith(r + os.sep) for r in roots) or provisioned(path, roots)


def provisioned(path: str, roots) -> bool:
    """Whether ``path`` is inside the roots as written and leaves them only through symlinks made
    before the reviewer was dispatched, such as a provisioned venv's ``bin/python``. A symlink's
    ctime is set when it is made, so a link the reviewer plants is later than the dispatch instant."""
    lexical = os.path.normpath(path)
    if DISPATCHED is None or not any(lexical == r or lexical.startswith(r + os.sep) for r in roots):
        return False
    prefix = os.sep
    for part in lexical.split(os.sep)[1:]:
        prefix = os.path.join(prefix, part)
        if os.path.islink(prefix) and os.lstat(prefix).st_ctime >= DISPATCHED:
            return False
    return True


def audit_claude(attempt: Path, roots):
    """Returns the transcripts, commands, file-tool paths, built-in headers, ReportFindings inputs,
    the final assistant text of the transcript that carried the built-in header (or of the root
    when none did), so a worker's chatter never stands in for the review, and the directory each
    command ran in. Claude Code keeps a ``cd`` between Bash calls and records the directory on
    every transcript line."""
    commands, cwds, reads, headers, findings_calls = [], [], [], [], []
    texts_by_file = {}
    header_files = []
    files = sorted((attempt / "home" / ".claude" / "projects").rglob("*.jsonl"))
    for path in files:
        texts_by_file[path] = []
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
                        header_files.append(path)
                if block.get("type") == "text" and record.get("type") == "assistant":
                    texts_by_file[path].append(block.get("text", ""))
                if block.get("type") == "tool_use":
                    name, inp = block.get("name"), block.get("input") or {}
                    if name == "Bash":
                        commands.append(inp.get("command", ""))
                        cwds.append(record.get("cwd"))
                    elif name in ("Read", "Glob", "Grep", "Write", "Edit"):
                        for key in ("file_path", "path"):
                            if inp.get(key):
                                reads.append(inp[key])
                    elif name == "ReportFindings":
                        findings_calls.append(inp)
    authoritative = header_files[-1] if header_files else (files[0] if files else None)
    texts = texts_by_file.get(authoritative, []) if authoritative else []
    return files, commands, reads, headers, findings_calls, texts, cwds


def codex_calls(text: str) -> tuple:
    """(command, workdir) pairs from one Codex tool call's text, and the workdirs it names that no
    pair carries. Each ``exec_command`` object's ``cmd`` pairs with its own ``workdir``; a ``cmd``
    outside a parseable object gets the call's only ``workdir`` when it names exactly one, else
    none; with no ``cmd`` the whole text is the command."""
    decode = lambda value: value.encode().decode("unicode_escape")
    pairs, spans = [], []
    for obj in CODEX_OBJ.finditer(text):
        fields = {m.group(1): m.group(2) for m in CODEX_FIELD.finditer(obj.group(1))}
        if fields.get("cmd") is not None:
            workdir = fields.get("workdir")
            pairs.append((obj.start(), decode(fields["cmd"]), decode(workdir) if workdir is not None else None))
            spans.append(obj.span())
    workdirs = {decode(w) for w in CODEX_WORKDIR.findall(text)}
    lone = next(iter(workdirs)) if len(workdirs) == 1 else None
    for m in CODEX_CMD.finditer(text):
        if not any(start <= m.start() < end for start, end in spans):
            pairs.append((m.start(), decode(m.group(1)), lone))
    pairs.sort(key=lambda pair: pair[0])
    calls = [(cmd, workdir) for _, cmd, workdir in pairs] or [(text, lone)]
    return calls, sorted(workdirs - {w for _, w in calls})


def audit_codex(attempt: Path, roots):
    """Returns the transcripts, the (command, workdir) calls, the workdirs no call carries, the
    rubric marker count, and the assistant texts."""
    commands, stray, rubric, texts = [], [], 0, []
    files = sorted((attempt / "home" / ".codex" / "sessions").rglob("rollout-*.jsonl"))
    for path in files:
        for _, record in load_lines(path):
            payload = record.get("payload") or {}
            if record.get("type") == "response_item":
                kind = payload.get("type")
                if kind in ("function_call", "custom_tool_call", "local_shell_call"):
                    args = payload.get("arguments") or payload.get("input") or (payload if kind == "local_shell_call" else "")
                    if isinstance(args, str):
                        try:
                            parsed = json.loads(args)
                        except json.JSONDecodeError:
                            parsed = {"cmd": args}
                    else:
                        parsed = args
                    cmd = parsed.get("cmd") or parsed.get("command") or (parsed.get("action") or {}).get("command") if isinstance(parsed, dict) else str(parsed)
                    text = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
                    workdir = None
                    if isinstance(parsed, dict):
                        action = parsed.get("action") if isinstance(parsed.get("action"), dict) else {}
                        workdir = parsed.get("workdir") or parsed.get("cwd") or action.get("working_directory") or action.get("workdir")
                        workdir = workdir if isinstance(workdir, str) else None
                    inner, unpaired = codex_calls(text)
                    commands.extend((c, w if w is not None else workdir) for c, w in inner)
                    stray.extend(unpaired)
                elif kind == "message" and payload.get("role") == "assistant":
                    for block in payload.get("content") or []:
                        if isinstance(block, dict) and block.get("text"):
                            texts.append(block["text"])
            blob = json.dumps(payload)
            if CODEX_RUBRIC in blob:
                rubric += 1
    return files, commands, stray, rubric, texts


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
    global HOME_DIR, DISPATCHED
    HOME_DIR = os.path.realpath(str(attempt / "home"))
    try:
        stamp = json.loads((attempt / "timing.json").read_text(encoding="utf-8"))["root_dispatched_at"]
        DISPATCHED = datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc).timestamp() + 1
    except (OSError, ValueError, KeyError, TypeError):
        DISPATCHED = None
    roots = [os.path.realpath(p) for p in [args.clone, str(attempt), *args.allowed]]
    PREFIXES[:] = list(args.allowed_prefix)
    violations = []
    try:
        if args.arm in ("claude-builtin", "review-code"):
            files, commands, reads, headers, calls, texts, cwds = audit_claude(attempt, roots)
            clone_path = os.path.realpath(args.clone)
            workdirs = [None if not c or os.path.realpath(c) == clone_path else c for c in cwds]
            stray = []
            report = {"transcripts": [str(f) for f in files], "prompt_headers": headers,
                      "report_findings_calls": len(calls)}
            if args.arm == "claude-builtin" and not headers:
                violations.append("no built-in prompt header found: the built-in did not run")
            if args.arm == "review-code" and headers:
                violations.append("a built-in review prompt ran inside a review-code attempt")
            payload = {"final_text": texts[-1] if texts else None, "report_findings": calls}
            (attempt / "payload.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        else:
            files, calls, stray, rubric, texts = audit_codex(attempt, roots)
            commands, workdirs = [c for c, _ in calls], [w for _, w in calls]
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
    probes, absent = [], []
    for cmd, workdir in list(zip(commands, workdirs)) + [("", w) for w in stray]:
        if network_use(cmd):
            violations.append(f"network-capable command: {cmd[:200]}")
        start = clone_real
        if workdir:
            start = os.path.normpath(os.path.join(clone_real, HOME_DIR + workdir[1:] if workdir.startswith("~") else workdir))
            if not inside(start, roots):
                violations.append(f"working directory outside allowed roots: {workdir}")
            start = os.path.realpath(start)
        for p in paths_in(cmd, start, clone_real):
            if inside(p, roots) or p.startswith(("/usr/", "/bin/", "/dev/", "/proc/", "/etc/")):
                continue
            if os.path.basename(p) in GUIDANCE and os.path.dirname(os.path.realpath(p)) in ancestors:
                probes.append(p)
                if os.path.exists(p):
                    violations.append(f"guidance file exists in an ancestor of the clone and was probed: {p}")
                continue
            if present(p):
                violations.append(f"path outside allowed roots in command: {p}")
            else:
                absent.append(p)
    for p in reads:
        if p.startswith("/") and not inside(p, roots):
            if present(p):
                violations.append(f"file tool read outside allowed roots: {p}")
            else:
                absent.append(p)
    diffs = [m.group(0) for cmd in commands for m in DIFF_CMD.finditer(cmd)]
    report.update({"commands": commands, "workdirs": workdirs, "unpaired_workdirs": stray, "file_tool_paths": reads, "diff_commands": diffs, "guidance_probes": sorted(set(probes)),
                   "absent_outside_paths": sorted(set(absent)),
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
