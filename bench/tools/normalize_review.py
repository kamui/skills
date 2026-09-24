#!/usr/bin/env python3
"""Normalize one reviewer's native output into the benchmark's common finding schema.

Usage::

    python3 normalize_review.py --arm review-code --composition <composition.json> [--clone <path>] --out <normalized.json>
    python3 normalize_review.py --arm claude-builtin --payload <payload.json> --out <normalized.json>
    python3 normalize_review.py --arm codex --stdout <stdout.txt> [--sessions-dir <dir>] [--clone <path>] --out <normalized.json>
    python3 normalize_review.py --render <normalized.json>     # uniform blind rendering to stdout

``--timing <timing.json>`` stamps ``payload_validated_at`` (UTC, now) in the run's sidecar when
normalization succeeds, which is the benchmark's payload event for arms that have no validator.
    python3 normalize_review.py --self-test

Native shapes:

* ``review-code``: the skill's ``composition.json`` (``summary.status``, ``findings`` with
  ``title``, ``priority``, ``action``, ``kind``, ``trigger``, ``impact``, ``change``, ``anchor``;
  ``questions``; ``observations``).
* ``claude-builtin``: ``payload.json`` written by ``attempt_audit.py`` with ``final_text`` (the
  final message; the ``high`` variant embeds a fenced JSON array of ``file``/``line``/``summary``/
  ``failure_scenario``) and ``report_findings`` (``ReportFindings`` call inputs, used by the
  ``low`` variant, with ``verdict`` and ``level``).
* ``codex``: the review's stdout, a summary paragraph then ``Review comment:`` bullets of the form
  ``- [P<n>] <title> — <path>:<start>-<end>`` followed by an indented body; when ``--sessions-dir``
  is given, the child rollout's final JSON with ``overall_correctness`` supplies the verdict.

Output schema: ``{"arm", "parse_status", "native_verdict", "verdict_source", "items": [...],
"parse_notes": [...]}``; ``parse_status`` is ``parsed`` (a recognized review with items),
``empty`` (a recognized review that reports nothing), or ``unresolved`` (the arm's expected
markers are absent, or some region of the output could not be parsed; the raw text is kept as an
item and the attempt needs adjudication before it can count as a review). An unresolved result
exits 1 after writing the file.
where each item has ``file``, ``line_start``, ``line_end``, ``claim``, ``consequence``,
``proposed_fix`` (nullable), ``native_priority``, ``native_action`` (review-code only),
``native_confidence`` (claude-builtin ``verdict`` when present) and ``kind``
(``finding``/``question``/``observation`` as the arm labelled it; never inferred). Paths are
made repository-relative when ``--clone`` is given. Nothing is dropped: an unparseable region is
kept as an item with ``claim`` set to its raw text and a ``parse_notes`` entry.

``--render`` prints every item uniformly (Location, Claim, Consequence, Fix) with priorities,
verdict words and arm structure removed, for blind scoring.

Exit codes: 0 success; 1 the result is ``unresolved`` (the file is still written; details on
stdout); 2 unreadable input, named on stderr.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

CODEX_BULLET = re.compile(r"^- \[(P\d)\] (.+?) — (\S+?):(\d+)(?:-(\d+))?\s*$")
FENCE = re.compile(r"```(?:json)?\s*(\[.*?\])\s*```", re.S)


def relpath(path: str, clone) -> str:
    if clone and path.startswith("/"):
        try:
            return os.path.relpath(path, clone)
        except ValueError:
            return path
    return path


def item(**fields) -> dict:
    base = {"file": None, "line_start": None, "line_end": None, "claim": "", "consequence": None,
            "proposed_fix": None, "native_priority": None, "native_action": None,
            "native_confidence": None, "kind": "finding"}
    base.update(fields)
    return base


def from_review_code(composition: dict, clone) -> dict:
    items, notes = [], []
    for f in composition.get("findings", []):
        anchor = f.get("anchor") or {}
        items.append(item(file=relpath(anchor.get("path", ""), clone), line_start=anchor.get("start_line"),
                          line_end=anchor.get("end_line"), claim=f"{f.get('title', '')}. {f.get('trigger', '')}".strip(),
                          consequence=f.get("impact"), proposed_fix=f.get("change"), native_priority=f.get("priority"),
                          native_action=f.get("action"), kind="finding"))
    for q in composition.get("questions", []):
        anchor = q.get("anchor") or {}
        items.append(item(file=relpath(anchor.get("path", ""), clone), claim=q.get("title", ""),
                          consequence=q.get("why_it_matters"), proposed_fix=q.get("answer"), kind="question"))
    for o in composition.get("observations", []):
        items.append(item(claim=o.get("fact", ""), consequence=o.get("evidence"), kind="observation"))
    status = (composition.get("summary") or {}).get("status")
    if status is None:
        notes.append("unresolved: composition has no summary.status")
    parse_status = "unresolved" if status is None else ("parsed" if items else "empty")
    return {"parse_status": parse_status, "native_verdict": status, "verdict_source": "composition.summary.status", "items": items, "parse_notes": notes}


def from_claude_builtin(payload: dict) -> dict:
    items, notes = [], []
    calls = payload.get("report_findings") or []
    text = payload.get("final_text") or ""
    source = None
    findings, raw = [], False
    if calls:
        source = "ReportFindings"
        for call in calls:
            findings.extend(call.get("findings") or [])
    else:
        m = FENCE.search(text)
        if m:
            source = "final_text json"
            try:
                findings = json.loads(m.group(1))
            except json.JSONDecodeError as error:
                notes.append(f"unresolved: fenced JSON did not parse: {error.msg}")
                items.append(item(claim=m.group(1)))
                raw = True
        elif text.strip():
            notes.append("unresolved: no fenced JSON array and no ReportFindings call; final text kept raw")
            items.append(item(claim=text.strip()))
            source = None
    for f in findings:
        if not isinstance(f, dict):
            notes.append("unresolved: non-object finding kept raw")
            items.append(item(claim=json.dumps(f)))
            raw = True
            continue
        items.append(item(file=f.get("file"), line_start=f.get("line"), line_end=f.get("line"),
                          claim=f.get("summary", ""), consequence=f.get("failure_scenario"),
                          native_confidence=f.get("verdict"), kind="finding"))
    if source is None and not items:
        notes.append("unresolved: no review output found")
    verdict = "empty-array" if source and not findings and not notes else ("findings" if findings else None)
    status = "unresolved" if source is None or raw else ("parsed" if findings else "empty")
    return {"parse_status": status, "native_verdict": verdict, "verdict_source": source, "items": items, "parse_notes": notes}


def codex_overall(sessions_dir) -> tuple:
    if not sessions_dir:
        return None, None
    best = None
    for path in sorted(Path(sessions_dir).rglob("rollout-*.jsonl")):
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                if 'overall_correctness' not in line:
                    continue
                for m in re.finditer(r'\\"overall_correctness\\":\s*\\"([^\\"]+)\\"|"overall_correctness":\s*"([^"]+)"', line):
                    best = m.group(1) or m.group(2)
    return best, ("rollout overall_correctness" if best else None)


def from_codex(text: str, clone, sessions_dir) -> dict:
    items, notes = [], []
    lines = text.splitlines()
    summary_lines, i = [], 0
    while i < len(lines) and not lines[i].startswith("Review comment"):
        if lines[i].strip():
            summary_lines.append(lines[i].strip())
        i += 1
    has_marker = i < len(lines)
    i += 1
    current, raw = None, False
    while i < len(lines):
        line = lines[i]
        m = CODEX_BULLET.match(line)
        if m:
            start = int(m.group(4)); end = int(m.group(5) or start)
            current = item(file=relpath(m.group(3), clone), line_start=start, line_end=end, claim=m.group(2).strip(),
                           consequence="", native_priority=m.group(1), kind="finding")
            items.append(current)
        elif not line.strip():
            pass
        elif current is not None and line[0].isspace():
            current["consequence"] = (current["consequence"] + " " + line.strip()).strip()
        else:
            # Neither a priority bullet nor an indented body line: keep it raw as its own item.
            notes.append(f"unresolved: line did not match the review-comment form: {line.strip()[:120]}")
            current = item(claim=line.strip(), consequence="", kind="finding")
            items.append(current)
            raw = True
        i += 1
    overall, source = codex_overall(sessions_dir)
    if overall is None:
        overall = " ".join(summary_lines) or None
        source = "stdout summary" if overall else None
    if not has_marker and not items:
        notes.append("unresolved: no 'Review comment:' marker and no bullets; stdout kept raw")
        items.append(item(claim=text.strip()))
        status = "unresolved"
    else:
        status = "unresolved" if raw else ("parsed" if items else "empty")
    return {"parse_status": status, "native_verdict": overall, "verdict_source": source, "items": items, "parse_notes": notes}


def render(doc: dict) -> str:
    out = []
    for n, it in enumerate(doc["items"], 1):
        loc = it["file"] or "(no file)"
        if it["line_start"]:
            loc += f":{it['line_start']}" + (f"-{it['line_end']}" if it["line_end"] and it["line_end"] != it["line_start"] else "")
        out.append(f"### Item {n}\nLocation: {loc}\nClaim: {it['claim']}\nConsequence: {it['consequence'] or '—'}\nFix: {it['proposed_fix'] or '—'}\n")
    if not doc["items"]:
        out.append("(no items)\n")
    return "\n".join(out)


def self_test() -> int:
    comp = {"summary": {"status": "Changes Requested"}, "findings": [{"title": "T", "priority": "P1", "action": "must-fix",
            "trigger": "when x", "impact": "boom", "change": "do y", "anchor": {"path": "/c/src/a.py", "start_line": 3, "end_line": 4}}],
            "questions": [{"title": "Q?", "why_it_matters": "w", "answer": "a", "anchor": {"path": "/c/src/b.py"}}],
            "observations": [{"fact": "f", "evidence": "e"}]}
    doc = from_review_code(comp, "/c")
    assert doc["native_verdict"] == "Changes Requested" and len(doc["items"]) == 3, doc
    assert doc["items"][0]["file"] == "src/a.py" and doc["items"][0]["native_action"] == "must-fix", doc
    assert [i["kind"] for i in doc["items"]] == ["finding", "question", "observation"]
    hi = from_claude_builtin({"final_text": 'x\n```json\n[{"file": "p.py", "line": 17, "summary": "s", "failure_scenario": "f"}]\n```', "report_findings": []})
    assert hi["native_verdict"] == "findings" and hi["items"][0]["line_end"] == 17, hi
    empty = from_claude_builtin({"final_text": "```json\n[]\n```", "report_findings": []})
    assert empty["native_verdict"] == "empty-array" and empty["items"] == [], empty
    lo = from_claude_builtin({"final_text": "done", "report_findings": [{"findings": [{"file": "p.py", "line": 1, "summary": "s", "failure_scenario": "f", "verdict": "CONFIRMED"}], "level": "low"}]})
    assert lo["verdict_source"] == "ReportFindings" and lo["items"][0]["native_confidence"] == "CONFIRMED", lo
    raw = from_claude_builtin({"final_text": "I found nothing structured", "report_findings": []})
    assert raw["parse_status"] == "unresolved" and raw["items"][0]["claim"].startswith("I found"), raw
    assert hi["parse_status"] == "parsed" and empty["parse_status"] == "empty", (hi, empty)
    bad = from_claude_builtin({"final_text": '```json\n[{"file": "p.py", "line": 1, "summary": "s"},]\n```', "report_findings": []})
    assert bad["parse_status"] == "unresolved" and bad["items"][0]["claim"].startswith("[{") and bad["parse_notes"], bad
    cut = from_claude_builtin({"final_text": '```json\n[{"file": "p.py", "line": 1, "summ]\n```', "report_findings": []})
    assert cut["parse_status"] == "unresolved" and len(cut["items"]) == 1, cut
    unknown = from_codex("Findings:\n- something in a new format\n", "/c", None)
    assert unknown["parse_status"] == "unresolved" and unknown["items"][0]["claim"].startswith("Findings:"), unknown
    nothing = from_codex("No issues found.\n\nReview comment:\n", "/c", None)
    assert nothing["parse_status"] == "empty" and nothing["items"] == [], nothing
    cx = from_codex("Summary line.\n\nReview comment:\n\n- [P2] Handle empty — /c/pricing.py:17-17\n  Body one.\n  Body two.\n- weird bullet\n", "/c", None)
    assert cx["items"][0]["file"] == "pricing.py" and cx["items"][0]["native_priority"] == "P2", cx
    assert cx["items"][0]["consequence"] == "Body one. Body two." and cx["native_verdict"] == "Summary line.", cx
    assert len(cx["items"]) == 2 and cx["parse_notes"] and cx["parse_status"] == "unresolved", cx
    ok = from_codex("Summary.\n\nReview comment:\n\n- [P2] Handle empty — /c/pricing.py:17-17\n  Body.\n", "/c", None)
    assert ok["parse_status"] == "parsed" and len(ok["items"]) == 1 and not ok["parse_notes"], ok
    for changed in ("* [P1] Title — /c/a.py:1-2\n  Body.\n", "1. [P2] Other — /c/b.py:3\n"):
        doc = from_codex("Summary.\n\nReview comment:\n\n" + changed, "/c", None)
        assert doc["parse_status"] == "unresolved" and doc["items"][0]["claim"] == changed.splitlines()[0], doc
        assert doc["parse_notes"], doc
    later = from_codex("S.\n\nReview comment:\n\n- [P2] A — /c/a.py:1\n  Body.\n* [P1] B — /c/b.py:2\n  More.\n", "/c", None)
    assert later["parse_status"] == "unresolved" and [i["claim"] for i in later["items"]] == ["A", "* [P1] B — /c/b.py:2"], later
    assert later["items"][1]["consequence"] == "More.", later
    with tempfile.TemporaryDirectory() as temp:
        p = Path(temp) / "rollout-x.jsonl"
        p.write_text(json.dumps({"payload": {"text": '{"overall_correctness": "patch is incorrect"}'}}) + "\n", encoding="utf-8")
        assert codex_overall(temp) == ("patch is incorrect", "rollout overall_correctness")
    assert "Location: pricing.py:17" in render(cx) and "P2" not in render(cx)
    print("self-test ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--arm", choices=["review-code", "claude-builtin", "codex"])
    parser.add_argument("--composition"); parser.add_argument("--payload"); parser.add_argument("--stdout")
    parser.add_argument("--sessions-dir"); parser.add_argument("--clone"); parser.add_argument("--out")
    parser.add_argument("--render"); parser.add_argument("--timing"); parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        if args.render:
            print(render(json.load(open(args.render, encoding="utf-8"))))
            return 0
        if args.arm == "review-code":
            if not args.composition:
                parser.error("--composition is required for review-code")
            doc = from_review_code(json.load(open(args.composition, encoding="utf-8")), args.clone)
        elif args.arm == "claude-builtin":
            if not args.payload:
                parser.error("--payload is required for claude-builtin")
            doc = from_claude_builtin(json.load(open(args.payload, encoding="utf-8")))
        elif args.arm == "codex":
            if not args.stdout:
                parser.error("--stdout is required for codex")
            doc = from_codex(open(args.stdout, encoding="utf-8").read(), args.clone, args.sessions_dir)
        else:
            parser.error("--arm is required")
    except (OSError, json.JSONDecodeError) as error:
        print(f"normalize_review.py: {error}", file=sys.stderr)
        return 2
    doc = {"arm": args.arm, **doc}
    text = json.dumps(doc, indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(text + "\n")
    else:
        print(text)
    if doc["parse_status"] == "unresolved":
        print("unresolved: the native input lacks the arm's expected review markers or has a region that did not parse; adjudication required")
        return 1
    if args.timing:
        from datetime import datetime, timezone
        try:
            sidecar = json.load(open(args.timing, encoding="utf-8"))
            sidecar["payload_validated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            open(args.timing, "w", encoding="utf-8").write(json.dumps(sidecar, indent=2) + "\n")
        except (OSError, json.JSONDecodeError) as error:
            print(f"normalize_review.py: {error}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
