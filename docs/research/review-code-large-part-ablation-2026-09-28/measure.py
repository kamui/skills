#!/usr/bin/env python3
"""Measure review-code's functional parts: size, exercise, outcomes and cost.

Usage:
    python3 -B measure.py sizes     [--repo PATH]
    python3 -B measure.py exercise  [--repo PATH]
    python3 -B measure.py outcomes  [--repo PATH]
    python3 -B measure.py phases    [--repo PATH] [--transcripts PATH]
    python3 -B measure.py machinery [--repo PATH] [--transcripts PATH]
    python3 -B measure.py rules     [--repo PATH]
    python3 -B measure.py all       [--repo PATH] [--transcripts PATH]

Read-only. It opens files under the repository and, for `phases` and
`machinery`, the archived transcripts of review-code attempts only. The arm is
read from attempt.json before an archive is opened, so built-in and Codex
archives are never read. It prints aggregates, never transcript text, and reads
archives in memory.

`phases` prices each request's actual usage at the repository's frozen rates and
allocates it to a phase. The allocation is an estimate, stated in README.md:
  * output tokens go to the phase of the action the request emits;
  * tokens new to the context go to whatever entered it since the previous
    request, split by character length;
  * cache reads, and tokens a request caches again, go to the phases in
    proportion to what each has put in context.
Totals are exact; the split is not a counterfactual saving.

`rules` simulates the staged test's decision rules from the filed per-defect
recovery rates, so each rule states how often it rejects a variant that changes
nothing and how often it catches a real loss.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import math
import os
import random
import re
import statistics
import subprocess
import sys
import tarfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
TRANSCRIPTS = os.path.expanduser("~/.t3/bench-cache/transcripts")
SKILL = "skills/review-code"
REFS = ("targets.md", "rubric.md", "output.md", "verification.md", "verifier.md",
        "verifier-concurrency.md", "prior-state.md")
RATES = {"input": 2.0, "output": 10.0, "cache_read": 0.2, "w5m": 2.5, "w1h": 4.0}
RUNS_BEFORE = "2026-09-28"  # the runs filed at ca29bad; later runs would change every population here
Counter = collections.Counter


# ---------------------------------------------------------------- sizes

def sections(path):
    """Heading-to-next-heading byte spans, with 1-based first and last lines."""
    data = open(path, "rb").read().decode("utf-8")
    lines = data.splitlines(keepends=True)
    out, name, start, size, fence = [], "(preamble)", 1, 0, False
    for number, line in enumerate(lines, 1):
        if line.startswith("```"):
            fence = not fence
        if not fence and re.match(r"#{1,3} ", line):
            if size:
                out.append((name, start, number - 1, size))
            name, start, size = line.strip(), number, 0
        size += len(line.encode("utf-8"))
    out.append((name, start, len(lines), size))
    return out


def helper_output(repo, script, flag):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    done = subprocess.run([sys.executable, "-B", os.path.join(repo, SKILL, "scripts", script), flag],
                          capture_output=True, env=env, check=True)
    return len(done.stdout)


def functions(path):
    import ast
    source = open(path, encoding="utf-8").read()
    lines = source.splitlines(keepends=True)
    out = {}
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            first = node.lineno - 1 - len(node.decorator_list)
            out[node.name] = (node.lineno, len("".join(lines[first:node.end_lineno]).encode("utf-8")))
    return out


EVERY = ("RT", "AL", "RV", "RQ", "RR")
FILE_SETS = {"SKILL.md": EVERY, "references/rubric.md": EVERY, "references/output.md": EVERY,
             "references/targets.md": ("RT", "RV", "RQ", "RR"), "references/verification.md": ("RT", "RQ"),
             "references/prior-state.md": ("RT", "RR"), "references/verifier.md": ("RT", "WB"),
             "references/verifier-concurrency.md": ("RT", "WB")}
HELPER_SETS = {("review_context.py", "--help"): ("L", ("RV", "RQ", "RR")),
               ("render_review.py", "--example"): ("R", ("RV", "RQ", "RR")),
               ("build_verifier_prompt.py", "--example"): ("V", ("RQ",))}

PARTS = [
    # id, name, [(file, heading prefix or None for whole file)], scripts, loaded sets
    ("V", "Independent verification (fresh-context verifier)",
     [("SKILL.md", "## Verification"), ("references/verification.md", None),
      ("references/verifier.md", None), ("references/verifier-concurrency.md", None)],
     ["build_verifier_prompt.py", "account_verifier_return.py", "test_verifier_handoff.py"]),
    ("R", "Structured record, finalizer and rendering contract",
     [("SKILL.md", "## Return"), ("references/output.md", None)],
     ["render_review.py", "test_render_review.py", "test_render_composition.py",
      "test_deleted_file_links.py"]),
    ("P", "Re-review: prior state, duplicate shortcut, prior records",
     [("references/prior-state.md", None)], []),
    ("F", "Pull-request target: fetch, identity, recorded deferrals",
     [("references/targets.md", "## Pull request"), ("references/targets.md", "### Recorded deferrals")],
     ["forge_packet.py", "test_forge_packet.py"]),
    ("L", "Local target pinning and context store",
     [("references/targets.md", "# Targets"), ("references/targets.md", "## Range or working tree"),
      ("references/targets.md", "### Resolve and pin"), ("references/targets.md", "### Snapshot and context"),
      ("references/targets.md", "### Description and record inputs")],
     ["review_context.py", "test_review_context.py"]),
    ("Q", "Requirements ledger and conformance",
     [("references/rubric.md", "## Requirements ledger")], []),
    ("C", "Released-compatibility procedure",
     [("references/rubric.md", "## Released compatibility")], []),
    ("T", "Changed tests: inspection and bounded execution",
     [("references/rubric.md", "## Changed tests")], []),
    ("S", "Supplied check evidence",
     [("references/rubric.md", "## Supplied checks")], []),
    ("A", "Admission core: admission, questions, priority and action, survivor record",
     [("references/rubric.md", "(preamble)"), ("references/rubric.md", "# Review rubric"),
      ("references/rubric.md", "## Admission"),
      ("references/rubric.md", "## Questions, observations, and gaps"),
      ("references/rubric.md", "## Priority and action"), ("references/rubric.md", "## Survivor record")], []),
    ("K", "Skill frame: inputs, boundaries, steps, status, modes",
     [("SKILL.md", "(preamble)"), ("SKILL.md", "# Review code"), ("SKILL.md", "## Inputs"),
      ("SKILL.md", "## Boundaries"), ("SKILL.md", "## Steps"), ("SKILL.md", "## Status"),
      ("SKILL.md", "## Modes")], ["test_instruction_budget.py"]),
]


def cmd_sizes(args):
    root = os.path.join(args.repo, SKILL)
    spans, files = {}, {}
    for rel in ["SKILL.md"] + ["references/" + name for name in REFS]:
        path = os.path.join(root, rel)
        files[rel] = os.path.getsize(path)
        for name, first, last, size in sections(path):
            spans[(rel, name)] = (first, last, size)
    print("## Files (runtime instruction set)")
    for rel, size in files.items():
        print(f"{size:7,d}  {rel}")
    print(f"{sum(files.values()):7,d}  runtime total")
    print("\n## Sections")
    for (rel, name), (first, last, size) in spans.items():
        print(f"{size:7,d}  {rel}:{first}-{last}  {name}")
    helpers = {("review_context.py", "--help"): 0, ("render_review.py", "--example"): 0,
               ("build_verifier_prompt.py", "--example"): 0}
    for key in helpers:
        helpers[key] = helper_output(args.repo, *key)
    print("\n## Helper outputs the primary reads")
    for (script, flag), size in helpers.items():
        print(f"{size:7,d}  {script} {flag}")
    print("\n## Parts")
    used, total_text, matrix = set(), 0, {}
    for ident, name, texts, scripts in PARTS:
        text, by_set = 0, Counter()
        for rel, heading in texts:
            if heading is None:
                size = files[rel]
                used.update(key for key in spans if key[0] == rel)
            else:
                size = spans[(rel, heading)][2]
                used.add((rel, heading))
            text += size
            for loaded in FILE_SETS[rel]:
                by_set[loaded] += size
        for (script, flag), (owner, loaded_sets) in HELPER_SETS.items():
            if owner == ident:
                for loaded in loaded_sets:
                    by_set[loaded] += helpers[(script, flag)]
        matrix[ident] = by_set
        code = sum(os.path.getsize(os.path.join(root, "scripts", s)) for s in scripts if not s.startswith("test_"))
        tests = sum(os.path.getsize(os.path.join(root, "scripts", s)) for s in scripts if s.startswith("test_"))
        total_text += text
        print(f"{ident}  text {text:6,d}  scripts {code:7,d}  tests {tests:7,d}  {name}")
    missing = [key for key in spans if key not in used]
    print(f"   text in parts {total_text:,d} of {sum(files.values()):,d}; unassigned sections: {missing}")
    print("\n## Parts by loaded set, helper output included (RT runtime files, AL always loaded, RV review,")
    print("## RQ required verifier, RR re-review, WB source of the worker brief)")
    columns = ("RT", "AL", "RV", "RQ", "RR", "WB")
    print("part " + "".join(f"{c:>8s}" for c in columns))
    for ident, by_set in matrix.items():
        print(f"{ident:5s}" + "".join(f"{by_set[c]:8,d}" for c in columns))
    print("all  " + "".join(f"{sum(m[c] for m in matrix.values()):8,d}" for c in columns))
    print("\n## Units nested inside a part")
    nested = (("V safety premises", [("SKILL.md", "**Safety premises.** "), ("references/verification.md", "A failed premise reopens")],
               [("references/verifier.md", "## Safety premises and scoped safety rulings")]),
              ("V concurrency bug-class check", [], [("references/verifier-concurrency.md", None)]),
              ("Q conformance", [("references/rubric.md", "**Conformance.** "),
                                 ("references/rubric.md", "Locate each obligation in the consuming tree")], []),
              ("K status", [], [("SKILL.md", "## Status")]), ("K modes", [], [("SKILL.md", "## Modes")]),
              ("A licence header", [], [("references/rubric.md", "(preamble)")]))
    for label, paragraphs, headed in nested:
        size = sum(files[rel] if heading is None else spans[(rel, heading)][2] for rel, heading in headed)
        for rel, opening in paragraphs:
            text = open(os.path.join(root, rel), encoding="utf-8").read()
            start = text.index("\n" + opening) + 1
            size += len(text[start:text.index("\n\n", start) + 2].encode("utf-8"))
        print(f"{size:7,d}  {label}")
    render = functions(os.path.join(root, "scripts", "render_review.py"))
    groups = {
        "verification checks in the finalizer": ["read_verification", "check_accounting", "accounted_ruling",
                                                 "carried_accounting", "derive_batch", "finalization_problem",
                                                 "role_list", "names_task", "task_id"],
        "prior record and replies in the finalizer": ["load_prior", "check_carried", "check_prior", "check_replies",
                                                      "packet_threads", "rendered_replies", "read_prior_item",
                                                      "derive_packet"],
        "self-test fixtures in the finalizer": ["valid_payload", "plain_payload", "deleted_file_payload",
                                                "consider_payload", "unanchored_payload", "abbreviation_payload",
                                                "finding_payload", "consider_finding_payload",
                                                "unanchored_finding_payload", "reference_payload", "line_anchor",
                                                "render_cases", "_mutate", "compatibility_payload",
                                                "_rewrite_fragment", "failing_cases", "emit_batch_cases",
                                                "self_test"],
    }
    print("\n## render_review.py function groups")
    for label, names in groups.items():
        print(f"{sum(render[n][1] for n in names):7,d}  {label}")
    context = functions(os.path.join(root, "scripts", "review_context.py"))
    print(f"{context['self_test'][1]:7,d}  self_test in review_context.py")


# ------------------------------------------------------------- attempts

def latest_mappings(repo, run):
    out = {}
    for directory in glob.glob(os.path.join(repo, "bench/runs", run, "scoring/*/")):
        found = glob.glob(directory + "mapping.v*.json")
        if not found:
            continue
        found.sort(key=lambda p: int(re.search(r"mapping\.v(\d+)", p).group(1)))
        mapping = json.load(open(found[-1]))
        for attempt in mapping["attempts"]:
            out[attempt["attempt_id"]] = attempt
    return out


def attempts(repo, include_toy=False):
    rows = []
    for run in sorted(os.listdir(os.path.join(repo, "bench/runs"))):
        base = os.path.join(repo, "bench/runs", run)
        if not os.path.isdir(base) or run >= RUNS_BEFORE or (run.endswith("-toy") and not include_toy):
            continue
        mappings = latest_mappings(repo, run)
        for path in sorted(glob.glob(os.path.join(base, "attempts/att-*/attempt.json"))):
            attempt = json.load(open(path))
            arm = attempt["cell"]["arm"]
            if not arm.startswith("review-code"):
                continue
            directory = os.path.dirname(path)
            rows.append({
                "run": run, "id": attempt["attempt_id"], "arm": arm, "target": attempt["cell"]["target"],
                "valid": attempt["disposition"] == "valid completed", "attempt": attempt,
                "composition": json.load(open(os.path.join(directory, "composition.json"))),
                "normalized": json.load(open(os.path.join(directory, "normalized.json"))),
                "mapping": mappings.get(attempt["attempt_id"]),
                "enforced": ("enforced" in arm or "isolated" in arm),
                "dir": directory,
            })
    return rows


def elapsed(attempt):
    from datetime import datetime
    timing = attempt["timing"]
    if not timing.get("payload_validated_at"):
        return None
    parse = lambda value: datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return (parse(timing["payload_validated_at"]) - parse(timing["dispatched_at"])).total_seconds()


def cmd_exercise(args):
    rows = attempts(args.repo)
    for label, chosen in (("all filed review-code compositions", rows),
                          ("valid reviews", [r for r in rows if r["valid"]]),
                          ("valid baseline reviews", [r for r in rows if r["valid"] and "baseline" in r["run"]])):
        comps = [r["composition"] for r in chosen]
        tasks = [t for c in comps for t in c["record"]["verification"]["tasks"]]
        print(f"\n## {label}: {len(chosen)}")
        print("target kind     ", dict(Counter(c["run"].get("target_kind") for c in comps)))
        print("status          ", dict(Counter(c["summary"]["status"] for c in comps)))
        print("coverage        ", dict(Counter(c["run"].get("coverage") for c in comps)))
        print("questions       ", sum(len(c["questions"]) for c in comps))
        print("prior items     ", sum(len(c["prior_items"]) for c in comps))
        print("outstanding     ", sum(len(c["record"]["verification"]["outstanding"]) for c in comps))
        print("routed entries  ", sum(len(v) for c in comps for v in c["record"]["routed"].values()))
        print("ambiguities     ", sum(len(c["summary"].get("ambiguities", [])) for c in comps))
        print("coverage gaps   ", sum(len(c["summary"].get("coverage_gaps", [])) for c in comps))
        print("findings        ", sum(len(c["findings"]) for c in comps),
              dict(Counter(f["action"] for c in comps for f in c["findings"])))
        print("finding kinds   ", dict(Counter(f["kind"] for c in comps for f in c["findings"])))
        print("observations    ", sum(len(c["observations"]) for c in comps),
              "in", sum(1 for c in comps if c["observations"]), "reviews")
        rows_req = [q for c in comps for q in c["record"]["requirements"]]
        print("ledger rows     ", len(rows_req), dict(Counter((q.get("class"), q.get("disposition")) for q in rows_req)))
        print("ledger sources  ", dict(Counter(re.split(r"[-/]", q["source"])[0] for q in rows_req)))
        print("artifact rows   ", sum(1 for q in rows_req if q["source"].startswith("artifact-")))
        print("compat rows     ", sum(1 for q in rows_req if "compatibility" in q))
        print("files           ", dict(Counter(f["state"] for c in comps for f in c["record"]["files"])))
        checks = [e for c in comps for e in c["record"].get("check_evidence", [])]
        print("check evidence  ", len(checks), dict(Counter(e.get("outcome") for e in checks)))
        print("batches/review  ", dict(Counter(len(c["record"]["verification"]["batches"]) for c in comps)))
        print("batch phases    ", dict(Counter(t.get("batch") for t in tasks)))
        print("candidate tasks ", dict(Counter((t.get("trigger"), t["ruling"]) for t in tasks if t["type"] == "candidate")))
        print("premise tasks   ", dict(Counter((t.get("area") or t.get("trigger"), t["ruling"]) for t in tasks if t["type"] != "candidate")))
        only_premise = sum(1 for c in comps if c["record"]["verification"]["tasks"]
                           and all(t["type"] != "candidate" for t in c["record"]["verification"]["tasks"]))
        print("premise-only batches", only_premise)
        concurrency = sum(1 for c in comps for f in c["findings"] if f["kind"] in ("concurrency", "invariant"))
        print("concurrency/invariant findings", concurrency)
        sizes = Counter()
        for c in comps:
            sizes["findings"] += len(json.dumps(c["findings"]))
            sizes["observations"] += len(json.dumps(c["observations"]))
            sizes["summary"] += len(json.dumps(c["summary"]))
            sizes["run"] += len(json.dumps(c["run"]))
            for key, value in c["record"].items():
                sizes["record." + key] += len(json.dumps(value))
        total = sum(sizes.values())
        print("composition bytes by section:",
              {k: f"{v / len(comps):.0f} ({100 * v / total:.0f}%)" for k, v in sizes.most_common()})


def cmd_outcomes(args):
    rows = attempts(args.repo)
    table, events = Counter(), []
    for row in rows:
        mapping, comp = row["mapping"], row["composition"]
        if mapping is None:
            continue
        tasks = {t["id"]: t for t in comp["record"]["verification"]["tasks"]}
        items = mapping["items"]
        assert len(items) == len(row["normalized"]["items"]), row["id"]
        for index, (graded, native) in enumerate(zip(items, row["normalized"]["items"])):
            grade = graded["assignment"].split(":")[0]
            if native["kind"] == "finding":
                finding = comp["findings"][index]
                task = tasks.get(finding["id"])
                key = (row["valid"], "finding", finding["action"], task["ruling"] if task else "unverified", grade)
                if grade == "false-finding" or (task and grade != "defect"):
                    events.append((row["run"], row["id"], row["target"], row["valid"], finding["id"],
                                   finding["action"], task["ruling"] if task else "unverified", grade))
            else:
                key = (row["valid"], native["kind"], "-", "-", grade)
            table[key] += 1
        for task in comp["record"]["verification"]["tasks"]:
            if task["ruling"] not in ("confirmed", "holds"):
                events.append((row["run"], row["id"], row["target"], row["valid"], task["id"], task["type"],
                               task["ruling"], "task"))
    print("## Graded items by native kind, action, verifier ruling and grade")
    print("valid  kind         action    ruling      grade          n")
    for key, count in sorted(table.items(), key=lambda kv: (not kv[0][0], kv[0][1:])):
        print(f"{str(key[0]):6s} {key[1]:12s} {key[2]:9s} {key[3]:11s} {key[4]:14s} {count}")
    print("\n## Events: non-confirming rulings, false findings, confirmed non-defects")
    for event in events:
        print("  ", event)

    print("\n## Review level, valid reviews on buggy targets")
    print("population          n  approved  approved+recovered  approved+zero  premise batch among approved+zero")
    clean = {"m-grpc-go-7390", "q-soba-195"}
    for label, test in (("baseline", lambda r: "baseline" in r["run"]),
                        ("variants, unenforced", lambda r: "baseline" not in r["run"] and not r["enforced"]),
                        ("enforced isolation", lambda r: r["enforced"])):
        chosen = [r for r in rows if r["valid"] and r["target"] not in clean and test(r) and r["mapping"]]
        approved = [r for r in chosen if r["composition"]["summary"]["status"] == "Approved"]
        recovered = [r for r in approved if any(i["assignment"].startswith("defect:") for i in r["mapping"]["items"])]
        zero = [r for r in approved if r not in recovered]
        premised = [r for r in zero if r["composition"]["record"]["verification"]["tasks"]]
        print(f"{label:20s}{len(chosen):3d}{len(approved):9d}{len(recovered):19d}{len(zero):15d}{len(premised):10d}")
        for r in zero:
            print("     zero-recovery approval:", r["run"][11:], r["id"], r["target"],
                  "premises:", [(t.get("area"), t["ruling"]) for t in r["composition"]["record"]["verification"]["tasks"]])

    print("\n## Cost and elapsed per valid review")
    for label, test in (("baseline", lambda r: "baseline" in r["run"]),
                        ("variants, unenforced", lambda r: "baseline" not in r["run"] and not r["enforced"]),
                        ("enforced isolation", lambda r: r["enforced"])):
        chosen = [r for r in rows if r["valid"] and test(r)]
        costs = [r["attempt"]["usage"]["priced_total_usd"] for r in chosen]
        times = [e for e in (elapsed(r["attempt"]) for r in chosen) if e is not None]
        batch = [r["attempt"]["usage"]["priced_total_usd"] for r in chosen
                 if r["composition"]["record"]["verification"]["batches"]]
        plain = [r["attempt"]["usage"]["priced_total_usd"] for r in chosen
                 if not r["composition"]["record"]["verification"]["batches"]]
        print(f"{label:22s} n={len(chosen):2d} cost mean {statistics.mean(costs):.3f} median {statistics.median(costs):.3f} "
              f"min {min(costs):.3f} max {max(costs):.3f}; elapsed median {statistics.median(times):.0f} s (n={len(times)}); "
              f"with batch n={len(batch)} mean {statistics.mean(batch) if batch else 0:.3f}; "
              f"without n={len(plain)} mean {statistics.mean(plain) if plain else 0:.3f}")


# --------------------------------------------------------------- phases

SEGMENT = re.compile(r"\s*(?:&&|\|\||;|\n)\s*")
READERS = ("cat", "sed", "head", "tail", "less", "nl", "batcat", "bat", "awk", "rg", "grep")
RUNNERS = re.compile(r"\b(pytest|vitest|jest|mocha|tsc|tsx|cargo|go (?:test|vet|build|run)|npm|pnpm|yarn|npx|"
                     r"node|deno|bun|tox|unittest|timeout|python3? -c|python3? - <<|venv/bin/python|make)\b")


def runs(script, command):
    """Whether a command executes a skill script, as opposed to reading its source."""
    return re.search(r"python3?\s+(?:-\w+\s+)*\S*" + re.escape(script), command) is not None


EXAMPLES = (("render_review.py", "render-example"), ("build_verifier_prompt.py", "builder-example"),
            ("review_context.py", "context-help"))


def instruction_reads(command):
    """Instruction sources whose text a command prints; a byte count is not a read."""
    names = []
    for segment in SEGMENT.split(command):
        words = segment.split()
        if not words:
            continue
        for script, label in EXAMPLES:
            if runs(script, segment) and ("--example" in segment or "--help" in segment):
                names.append(label)
        if os.path.basename(words[0]) not in READERS:
            continue
        if re.search(r"references/\*(\.md)?(\s|$)", segment) or re.search(r"(^|\s)\*\.md(\s|$)", segment):
            names.extend(REFS)
        for name in ("SKILL.md", "DESIGN.md") + REFS:
            if re.search(r"(^|[\s/'\"])" + re.escape(name) + r"($|[\s'\"|;])", segment):
                names.append(name)
        if re.search(r"(scripts/|\s)\w+\.py\b", segment) and "review-code" in command + segment or \
                re.search(r"\b(render_review|review_context|forge_packet|build_verifier_prompt|account_verifier_return)\.py", segment):
            names.append("script-source")
    return sorted(set(names))


def real_run(script, command):
    return any(runs(script, segment) and "--example" not in segment and "--help" not in segment
               for segment in SEGMENT.split(command))


def classify(name, tool_input):
    """Phase of one tool call, by precedence."""
    if name == "Skill":
        return "instr:SKILL.md"
    if name in ("Agent", "Task"):
        return "verify:dispatch"
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    command = tool_input.get("command") or ""
    text = command or path or json.dumps(tool_input)
    if name != "Bash":
        base = os.path.basename(path)
        if base in ("composition.json", "report.md", "record.json", "payload.json", "batch.json"):
            return "record"
        if base in ("input.json", "brief.md", "accounting.json", "manifest.json") or "return" in base:
            return "verify:primary"
        if "/skills/review-code/" in path:
            if "/scripts/" in path:
                return "instr:script-source"
            return "instr:" + base if base in REFS + ("SKILL.md",) else "instr:other"
        return "inspect"
    if real_run("render_review.py", text) or "composition.json" in text:
        return "record"
    if real_run("build_verifier_prompt.py", text) or real_run("account_verifier_return.py", text) or any(
            token in text for token in ("input.json", "accounting.json", "brief.md", "-return.json", "_return.json")):
        return "verify:primary"
    if real_run("review_context.py", text):
        return "context"
    reads = instruction_reads(text)
    if reads:
        return "instr:" + "+".join(reads)
    if "report.md" in text or "record.json" in text:
        return "record"
    if "/skills/review-code" in text:
        return "instr:other"
    if RUNNERS.search(text):
        return "execute"
    return "inspect"


def content_chars(content):
    if isinstance(content, str):
        return len(content)
    total = 0
    for block in content or []:
        if isinstance(block, dict):
            if block.get("type") == "text":
                total += len(block.get("text", ""))
            elif block.get("type") == "tool_result":
                total += content_chars(block.get("content"))
            elif block.get("type") == "tool_use":
                total += len(json.dumps(block.get("input")))
            elif block.get("type") == "tool_reference":
                total += 20
        elif isinstance(block, str):
            total += len(block)
    return total


def parse_time(value):
    from datetime import datetime
    return datetime.strptime(value[:26].rstrip("Z"), "%Y-%m-%dT%H:%M:%S.%f" if "." in value else "%Y-%m-%dT%H:%M:%S")


def price(usage):
    creation = usage.get("cache_creation") or {}
    w1h = creation.get("ephemeral_1h_input_tokens", 0)
    w5m = creation.get("ephemeral_5m_input_tokens", 0)
    if not creation:
        w1h = usage.get("cache_creation_input_tokens", 0)
    return {
        "write": (w1h * RATES["w1h"] + w5m * RATES["w5m"]) / 1e6,
        "read": (usage.get("cache_read_input_tokens", 0) * RATES["cache_read"]
                 + usage.get("input_tokens", 0) * RATES["input"]) / 1e6,
        "output": usage.get("output_tokens", 0) * RATES["output"] / 1e6,
    }


def split_by_reference(phase, chars, sizes):
    """Apportion a multi-file reference read by the files' sizes."""
    if not phase.startswith("instr:") or "+" not in phase:
        return {phase: chars}
    names = phase[len("instr:"):].split("+")
    total = sum(sizes.get(n, 1) for n in names)
    return {"instr:" + n: chars * sizes.get(n, 1) / total for n in names}


def primary_ledger(lines, sizes):
    """Allocate one primary transcript's usage and time to phases."""
    dollars = collections.defaultdict(lambda: Counter())
    turn, removable = Counter(), Counter()
    seconds = Counter()
    calls = Counter()
    context = Counter()          # estimated tokens each phase has placed in context
    pending = Counter()          # characters entered since the previous request, by phase
    tool_phase, tool_start = {}, {}
    requests, order = {}, []
    last_event = None
    refused = 0
    for line in lines:
        kind = line.get("type")
        if kind == "assistant":
            rid = line.get("requestId")
            message = line["message"]
            entry = requests.get(rid)
            if entry is None:
                entry = requests[rid] = {"usage": message["usage"], "phases": Counter(), "start": last_event,
                                         "end": line["timestamp"], "pending": pending, "chars": 0}
                pending = Counter()
                order.append(rid)
            entry["usage"] = message["usage"]
            entry["end"] = line["timestamp"]
            for block in message["content"]:
                if block.get("type") == "tool_use":
                    phase = classify(block["name"], block.get("input") or {})
                    weight = len(json.dumps(block.get("input")))
                    entry["phases"][phase] += weight
                    entry["chars"] += weight
                    tool_phase[block["id"]] = phase
                    tool_start[block["id"]] = line["timestamp"]
                    for name in split_by_reference(phase, 1, sizes):
                        calls[name] += 1
                elif block.get("type") == "text":
                    entry["chars"] += len(block.get("text", ""))
            last_event = line["timestamp"]
        elif kind == "user":
            content = line["message"]["content"]
            if isinstance(content, str):
                pending["harness"] += len(content)
            else:
                for block in content:
                    if block.get("type") == "tool_result":
                        phase = tool_phase.get(block.get("tool_use_id"), "inspect")
                        chars = content_chars(block.get("content"))
                        for name, share in split_by_reference(phase, chars, sizes).items():
                            pending[name] += share
                        started = tool_start.get(block.get("tool_use_id"))
                        if started:
                            wait = (parse_time(line["timestamp"]) - parse_time(started)).total_seconds()
                            seconds["tool:" + phase.split(":")[0] if not phase.startswith("verify:dispatch")
                                    else "tool:verifier-wait"] += max(wait, 0)
                        if phase == "record" and was_refused(block):
                            refused += 1
                    elif block.get("type") == "text":
                        # the Skill tool delivers SKILL.md as a user text block
                        pending["instr:SKILL.md"] += len(block.get("text", ""))
            last_event = line["timestamp"]
    previous, held_before = None, 0
    for index, rid in enumerate(order):
        entry = requests[rid]
        cost = price(entry["usage"])
        usage = entry["usage"]
        phases = entry["phases"] or Counter({"return": 1})
        total = sum(phases.values())
        shares = {}
        for phase, weight in phases.items():
            for name, part in split_by_reference(phase, weight, sizes).items():
                shares[name] = shares.get(name, 0) + part / total
        for phase, share in shares.items():
            dollars[phase]["output"] += cost["output"] * share
            turn[phase] += sum(cost.values()) * share
        before = {phase: value["read"] + value["write"] for phase, value in dollars.items()}
        if entry["start"]:
            think = (parse_time(entry["end"]) - parse_time(entry["start"])).total_seconds()
            for phase, share in shares.items():
                seconds["model:" + phase.split(":")[0]] += max(think, 0) * share
        written = usage.get("cache_creation_input_tokens", 0)
        holds = written + usage.get("cache_read_input_tokens", 0) + usage.get("input_tokens", 0)
        if index == 0:
            # the system prompt, tool definitions, task packet and session attachments
            dollars["harness"]["read"] += cost["read"]
            dollars["harness"]["write"] += cost["write"]
            context["harness"] += holds
        else:
            in_context = sum(context.values()) or 1
            for phase, tokens in context.items():
                dollars[phase]["read"] += cost["read"] * tokens / in_context
            # tokens that are new to the context, against tokens the request cached again
            fresh = max(holds - held_before, 0)
            again = max(written - fresh, 0)
            per_token = cost["write"] / written if written else 0.0
            for phase, tokens in list(context.items()):
                dollars[phase]["write"] += per_token * again * tokens / in_context
            entered = Counter(entry["pending"])
            if previous is not None:
                for phase, share in previous["shares"].items():
                    entered[phase] += previous["chars"] * share
            weight = sum(entered.values())
            if weight == 0:
                entered, weight = Counter({"harness": 1}), 1
            for phase, chars in entered.items():
                dollars[phase]["write"] += per_token * min(fresh, written) * chars / weight
                context[phase] += fresh * chars / weight
        held_before = holds
        previous = {"shares": shares, "chars": entry["chars"]}
        for phase, value in dollars.items():
            owned = value["read"] + value["write"] - before.get(phase, 0.0)
            removable[phase] += owned * (1 - shares.get(phase, 0.0))
    for phase, value in turn.items():
        removable[phase] += value
    return dollars, seconds, calls, len(order), refused, turn, removable


def worker_cost(lines):
    seen, total = {}, 0.0
    for line in lines:
        if line.get("type") == "assistant" and line.get("requestId"):
            seen[line["requestId"]] = line["message"]["usage"]
    for usage in seen.values():
        total += sum(price(usage).values())
    return total, len(seen)


GROUPS = [
    ("harness, tool definitions and task packet", lambda p: p == "harness"),
    ("instructions: SKILL.md, rubric, output, targets", lambda p: p in ("instr:SKILL.md", "instr:rubric.md", "instr:output.md", "instr:targets.md", "instr:other", "instr:DESIGN.md")),
    ("instructions: verification.md", lambda p: p == "instr:verification.md"),
    ("instructions: worker-only references", lambda p: p in ("instr:verifier.md", "instr:verifier-concurrency.md")),
    ("instructions: prior-state.md", lambda p: p == "instr:prior-state.md"),
    ("instructions: helper examples and help", lambda p: p in ("instr:render-example", "instr:builder-example", "instr:context-help")),
    ("instructions: script source read by the primary", lambda p: p == "instr:script-source"),
    ("context store (build and selector reads)", lambda p: p == "context"),
    ("inspection of the repository", lambda p: p == "inspect"),
    ("execution (tests and scratch experiments)", lambda p: p == "execute"),
    ("verification, primary side", lambda p: p in ("verify:primary", "verify:dispatch")),
    ("record authoring and finalizer", lambda p: p == "record"),
    ("closing message", lambda p: p == "return"),
]


def cmd_phases(args):
    root = os.path.join(args.repo, SKILL)
    sizes = {name: os.path.getsize(os.path.join(root, "references", name)) for name in REFS}
    sizes["SKILL.md"] = os.path.getsize(os.path.join(root, "SKILL.md"))
    sizes["DESIGN.md"] = os.path.getsize(os.path.join(root, "DESIGN.md"))
    sizes["render-example"] = helper_output(args.repo, "render_review.py", "--example")
    sizes["builder-example"] = helper_output(args.repo, "build_verifier_prompt.py", "--example")
    sizes["context-help"] = helper_output(args.repo, "review_context.py", "--help")
    sizes["script-source"] = 4000
    rows = [r for r in attempts(args.repo) if r["valid"]]
    results = []
    for row in rows:
        archive = os.path.join(args.transcripts, row["run"], row["id"] + ".tar.gz")
        if not os.path.exists(archive):
            print("missing archive", row["run"], row["id"], file=sys.stderr)
            continue
        primary, workers = None, []
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                if not member.name.endswith(".jsonl"):
                    continue
                lines = [json.loads(l) for l in tar.extractfile(member).read().decode("utf-8").splitlines() if l.strip()]
                if "/subagents/" in member.name:
                    workers.append(lines)
                else:
                    primary = lines if primary is None or len(lines) > len(primary) else primary
        dollars, seconds, calls, count, refused, turn, removable = primary_ledger(primary, sizes)
        worker = [worker_cost(lines) for lines in workers]
        total = sum(sum(v.values()) for v in dollars.values()) + sum(w[0] for w in worker)
        filed = row["attempt"]["usage"]["priced_total_usd"]
        results.append({"row": row, "dollars": dollars, "seconds": seconds, "calls": calls, "requests": count,
                        "worker": sum(w[0] for w in worker), "worker_requests": sum(w[1] for w in worker),
                        "total": total, "filed": filed, "refused": refused, "turn": turn,
                        "removable": removable})
    drift = max(abs(r["total"] - r["filed"]) for r in results)
    print(f"attempts joined: {len(results)}; largest difference between the join's total and the filed charge: ${drift:.6f}")

    def report(label, chosen):
        if not chosen:
            return
        total = sum(r["total"] for r in chosen)
        print(f"\n## {label}: {len(chosen)} valid reviews, ${total:.2f}, "
              f"{sum(r['requests'] for r in chosen) / len(chosen):.1f} primary requests per review")
        print(f"{'group':52s} {'$':>8s} {'share':>7s}   {'write':>7s} {'read':>7s} {'output':>7s}  calls"
              f"  {'by turn $':>9s} {'share':>6s}  {'turns+content $':>15s} {'share':>6s}")
        for name, test in GROUPS:
            parts = Counter()
            calls = 0
            for r in chosen:
                for phase, value in r["dollars"].items():
                    if test(phase):
                        parts.update(value)
                calls += sum(n for phase, n in r["calls"].items() if test(phase))
            amount = sum(parts.values())
            by_turn = sum(v for r in chosen for p, v in r["turn"].items() if test(p))
            both = sum(v for r in chosen for p, v in r["removable"].items() if test(p))
            print(f"{name:52s} {amount:8.3f} {100 * amount / total:6.1f}%   {parts['write']:7.3f} {parts['read']:7.3f} "
                  f"{parts['output']:7.3f}  {calls:5d}  {by_turn:9.3f} {100 * by_turn / total:5.1f}%  "
                  f"{both:15.3f} {100 * both / total:5.1f}%")
        known = set()
        for r in chosen:
            for phase in r["dollars"]:
                if not any(test(phase) for _, test in GROUPS):
                    known.add(phase)
        worker = sum(r["worker"] for r in chosen)
        print(f"{'verifier workers':52s} {worker:8.3f} {100 * worker / total:6.1f}%")
        if known:
            print("unassigned phases:", sorted(known))
        time = Counter()
        for r in chosen:
            time.update(r["seconds"])
        whole = sum(time.values())
        print("seconds by activity (share of the transcript's own envelope):")
        for key, value in time.most_common():
            print(f"   {key:26s} {value:8.0f} {100 * value / whole:5.1f}%")
        reads = Counter()
        for r in chosen:
            for phase, n in r["calls"].items():
                if phase.startswith("instr:"):
                    for name in phase[6:].split("+"):
                        reads[name] += 1
        print("reviews reading each instruction source at least once:",
              {name: sum(1 for r in chosen if any(name in p[6:].split("+") for p in r["calls"] if p.startswith("instr:")))
               for name in sorted(reads)})
        finals = [sum(n for p, n in r["calls"].items() if p == "record") for r in chosen]
        print("record-phase tool calls per review: median", statistics.median(finals), "max", max(finals),
              "; finalizer or record calls returning an error:", sum(r["refused"] for r in chosen))
        with_batch = [r for r in chosen if r["row"]["composition"]["record"]["verification"]["batches"]]
        without = [r for r in chosen if r not in with_batch]
        premise_only = [r for r in with_batch
                        if all(t["type"] != "candidate" for t in r["row"]["composition"]["record"]["verification"]["tasks"])]

        verify = ("verify:primary", "verify:dispatch", "instr:verification.md", "instr:verifier.md",
                  "instr:verifier-concurrency.md", "instr:builder-example")
        record = ("record", "instr:output.md", "instr:render-example")

        def owned(r, names):
            return sum(sum(v.values()) for p, v in r["dollars"].items() if p in names)

        def removable(r, names):
            return sum(v for p, v in r["removable"].items() if p in names)

        for label, names, group, which, extra in (
                ("verification", verify, with_batch, "with a batch", lambda r: r["worker"]),
                ("verification", verify, premise_only, "with a premise-only batch", lambda r: r["worker"]),
                ("verification", verify, without, "without a batch", lambda r: r["worker"]),
                ("record and finalizer", record, chosen, "all", lambda r: 0.0)):
            if not group:
                continue
            whole = sum(r["total"] for r in group)
            by_owner = sum(owned(r, names) + extra(r) for r in group)
            by_both = sum(removable(r, names) + extra(r) for r in group)
            print(f"{label}, reviews {which}: n={len(group)}, mean review ${whole / len(group):.3f}; "
                  f"owned ${by_owner / len(group):.3f} ({100 * by_owner / whole:.1f}%); "
                  f"turns plus content ${by_both / len(group):.3f} ({100 * by_both / whole:.1f}%, "
                  f"{100 * by_both / total:.1f}% of this population's spend); "
                  + (f"verifier wait mean {statistics.mean(r['seconds']['tool:verifier-wait'] for r in group):.0f} s; "
                     if label == "verification" else "") +
                  f"model time on the phase mean "
                  f"{statistics.mean(r['seconds']['model:verify' if label == 'verification' else 'model:record'] for r in group):.0f} s; "
                  f"elapsed mean {statistics.mean(elapsed(r['row']['attempt']) or 0 for r in group):.0f} s")

    report("Frozen baseline arm A", [r for r in results if "baseline" in r["row"]["run"]])
    report("Variant runs without enforced isolation", [r for r in results if "baseline" not in r["row"]["run"] and not r["row"]["enforced"]])
    report("Runs under enforced isolation", [r for r in results if r["row"]["enforced"]])
    report("All valid review-code reviews", results)


# ------------------------------------------------------------ machinery

def was_refused(block):
    """A tool result that failed, or that carries a script stage's refusal inside a pipeline that exited 0."""
    text = block.get("content")
    if isinstance(text, list):
        text = "".join(part.get("text", "") for part in text if isinstance(part, dict))
    return bool(block.get("is_error")) or "failed with exit" in (text or "")


def load_primary(transcripts, row):
    archive = os.path.join(transcripts, row["run"], row["id"] + ".tar.gz")
    primary = None
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            if member.name.endswith(".jsonl") and "/subagents/" not in member.name:
                lines = [json.loads(l) for l in tar.extractfile(member).read().decode("utf-8").splitlines() if l.strip()]
                if primary is None or len(lines) > len(primary):
                    primary = lines
    return primary


RUN_FIELDS = ("target_kind", "change_description", "base_ref", "repository", "issues", "base_sha", "head_sha",
              "merge_base")


def reads_finalizer_source(block):
    """A tool call that prints or searches the finalizer's source, not one that runs it."""
    tool_input = block["input"]
    if block["name"] in ("Read", "Grep"):
        return "render_review.py" in (tool_input.get("file_path") or tool_input.get("path") or "")
    if block["name"] != "Bash":
        return False
    return any("render_review.py" in segment and segment.split() and os.path.basename(segment.split()[0]) in READERS
               for part in SEGMENT.split(tool_input.get("command") or "") for segment in part.split("|")[:1])


def cmd_machinery(args):
    """Script runs, refusals and verifier rulings, read from the primaries' tool calls."""
    rows = [r for r in attempts(args.repo) if r["valid"]]
    table, verdicts, lookups = [], Counter(), Counter()
    for row in rows:
        uses = {}
        count = Counter()
        looked = set()
        for line in load_primary(args.transcripts, row):
            if line.get("type") == "assistant":
                for block in line["message"]["content"]:
                    if block.get("type") == "tool_use":
                        uses[block["id"]] = block
                        command = (block["input"].get("command") or "") if block["name"] == "Bash" else ""
                        if reads_finalizer_source(block):
                            count["source read"] += 1
                            count["source read before the first run"] += count["finalizer started"] == 0
                            looked.update(f for f in RUN_FIELDS if f in json.dumps(block["input"]))
                        elif real_run("render_review.py", command):
                            count["finalizer started"] += 1
            elif line.get("type") == "user" and isinstance(line["message"]["content"], list):
                for block in line["message"]["content"]:
                    if block.get("type") != "tool_result" or block.get("tool_use_id") not in uses:
                        continue
                    use = uses[block["tool_use_id"]]
                    command = (use["input"].get("command") or "") if use["name"] == "Bash" else ""
                    text = block.get("content")
                    if isinstance(text, list):
                        text = "".join(part.get("text", "") for part in text if isinstance(part, dict))
                    text = text or ""
                    failed = was_refused(block)
                    if use["name"] in ("Agent", "Task"):
                        count["dispatch"] += 1
                        body = text.split('"premises"', 1)
                        for value in re.findall(r'"verdict"\s*:\s*"([\w-]+)"', text):
                            verdicts["candidate " + value] += 1
                        if len(body) == 2:
                            # premise rulings follow the `premises` key; scoped safety rulings sit inside candidates
                            for value in re.findall(r'"ruling"\s*:\s*"([\w-]+)"', body[1]):
                                verdicts["premise " + value] += 1
                    for script, key in (("render_review.py", "finalizer"), ("build_verifier_prompt.py", "builder"),
                                        ("account_verifier_return.py", "accounting")):
                        if real_run(script, command):
                            count[key] += 1
                            count[key + " failed"] += failed
        lookups.update(looked)
        table.append((row, count))
    print("population              n  dispatches  builder runs (failed)  accounting runs (failed)  finalizer runs (failed)  "
          "reviews finalized first time")
    for label, test in (("baseline", lambda r: "baseline" in r["run"]),
                        ("variants, unenforced", lambda r: "baseline" not in r["run"] and not r["enforced"]),
                        ("enforced isolation", lambda r: r["enforced"]), ("all valid", lambda r: True)):
        chosen = [c for r, c in table if test(r)]
        total = lambda key: sum(c[key] for c in chosen)
        print(f"{label:22s}{len(chosen):3d}{total('dispatch'):12d}{total('builder'):10d} ({total('builder failed')})"
              f"{total('accounting'):18d} ({total('accounting failed')}){total('finalizer'):18d} ({total('finalizer failed')})"
              f"{sum(1 for c in chosen if c['finalizer failed'] == 0):22d}")
    print("reviews needing two or more finalizer runs:", sum(1 for r, c in table if c["finalizer"] >= 2), "of", len(table))
    print("worker returns, all valid reviews:", dict(verdicts))
    print("\nreads of the finalizer's source by the primary")
    for label, test in (("baseline", lambda r: "baseline" in r["run"]),
                        ("variants, unenforced", lambda r: "baseline" not in r["run"] and not r["enforced"]),
                        ("enforced isolation", lambda r: r["enforced"]), ("all valid", lambda r: True)):
        chosen = [c for r, c in table if test(r)]
        print(f"   {label:22s} reviews {sum(1 for c in chosen if c['source read']):3d} of {len(chosen):2d}; "
              f"reads {sum(c['source read'] for c in chosen):4d}, "
              f"{sum(c['source read before the first run'] for c in chosen)} before the first finalizer run")
    print("   reviews whose source reads name each `run` field:", dict(lookups.most_common()))

    print("\nper target, valid reviews: n, with a batch, candidate batch, premise-only batch, enforced-isolation costs")
    by_target = collections.defaultdict(list)
    for row in rows:
        by_target[row["target"]].append(row)
    for target, group in sorted(by_target.items()):
        batch = [r for r in group if r["composition"]["record"]["verification"]["batches"]]
        premise = [r for r in batch if all(t["type"] != "candidate" for t in r["composition"]["record"]["verification"]["tasks"])]
        enforced = [round(r["attempt"]["usage"]["priced_total_usd"], 2) for r in group if r["enforced"]]
        print(f"   {target:20s}{len(group):3d}{len(batch):4d}{len(batch) - len(premise):4d}{len(premise):4d}   {enforced}")


# ----------------------------------------------------------------- rules

STAGE_ONE = ("i-requests-6667", "l-bokeh-9232", "p-hono-5067", "m-grpc-go-7390")
STAGE_TWO = STAGE_ONE + ("k-graphql-js-1582",)
X394_STAGE_TWO = STAGE_TWO + ("q-soba-195", "j-trpc-5017", "n-ripgrep-2957", "r-base-ui-5460")


def filed_rates(repo):
    """Per target: each registered defect's recovery, must-fix and sufficient-remedy rates in valid reviews."""
    rows = [r for r in attempts(repo) if r["valid"] and r["mapping"]]
    out = {}
    for target in X394_STAGE_TWO:
        group = [r for r in rows if r["target"] == target]
        registers = glob.glob(os.path.join(repo, "bench/targets", target, "register.v*.json"))
        registers.sort(key=lambda p: int(re.search(r"register\.v(\d+)", p).group(1)))
        defects = []
        for defect in json.load(open(registers[-1])).get("defects", []):
            recovered = must_fix = sufficient = 0
            for row in group:
                hits = [i for i, item in enumerate(row["mapping"]["items"]) if item["assignment"] == "defect:" + defect["id"]]
                if not hits:
                    continue
                recovered += 1
                must_fix += any(row["normalized"]["items"][i]["kind"] == "finding"
                                and row["composition"]["findings"][i]["action"] == "must-fix" for i in hits)
                sufficient += any(row["mapping"]["items"][i]["fix_sufficiency"] == "sufficient" for i in hits)
            defects.append((defect["id"], recovered, len(group), must_fix, sufficient))
        costs = [math.log(r["attempt"]["usage"]["priced_total_usd"]) for r in group if r["enforced"]]
        out[target] = {"defects": defects, "enforced_cost": math.exp(statistics.mean(costs)) if costs else None}
    return out


def smoothed(hits, total):
    return (hits + 0.5) / (total + 1)


def draw_arm(rng, rates, targets, replicates, recall_scale, stray, cost_ratio, spread):
    """One arm's reviews: per target and replicate, the defects recovered, their action and remedy, and cost."""
    arm = {}
    for target in targets:
        cells = []
        for _ in range(replicates):
            found = {}
            for ident, recovered, total, must_fix, sufficient in rates[target]["defects"]:
                if rng.random() < min(1.0, smoothed(recovered, total) * recall_scale):
                    found[ident] = (rng.random() < smoothed(must_fix, max(recovered, 1)),
                                    rng.random() < smoothed(sufficient, max(recovered, 1)))
            cells.append({"found": found, "stray": rng.random() < stray,
                          "cost": rates[target]["enforced_cost"] * cost_ratio * math.exp(rng.gauss(0, spread))})
        arm[target] = cells
    return arm


def recovered(cells, defect=None):
    return sum((defect in cell["found"]) if defect else len(cell["found"]) for cell in cells)


def stage_one(control, variant, any_miss=False):
    """Four single pairs. `any_miss` is the first draft's recall rule, kept to show why it was replaced."""
    buggy = [t for t in STAGE_ONE if t != "m-grpc-go-7390"]
    stray = sum(variant[t][0]["stray"] and not control[t][0]["stray"] for t in STAGE_ONE)
    if any_miss:
        lost = sum(bool(set(control[t][0]["found"]) - set(variant[t][0]["found"])) for t in buggy)
    else:
        lost = sum(bool(control[t][0]["found"]) and not variant[t][0]["found"] for t in buggy)
    dearer = sum(variant[t][0]["cost"] for t in STAGE_ONE) >= sum(control[t][0]["cost"] for t in STAGE_ONE)
    return {"stray": stray >= 2, "recall": lost >= 2, "cost": dearer}


def stage_two(control, variant, recall_margin, action_margin, ratio, target_margin=None):
    """Fifteen pairs. With no `target_margin` the per-target rule is a defect the control recovers 3/3 and the variant 0/3."""
    total = lambda arm, pick: sum(pick(cell) for cells in arm.values() for cell in cells)
    if target_margin is None:
        per_target = any(recovered(control[t], d[0]) == len(control[t]) and recovered(variant[t], d[0]) == 0
                         for t in STAGE_TWO for d in RATES_IN_USE[t]["defects"])
    else:
        per_target = any(recovered(control[t]) - recovered(variant[t]) >= target_margin for t in STAGE_TWO)
    must_fix = lambda cell: sum(action for action, _ in cell["found"].values())
    sufficient = lambda cell: sum(remedy for _, remedy in cell["found"].values())
    ratios = [statistics.median(c["cost"] for c in variant[t]) / statistics.median(c["cost"] for c in control[t])
              for t in STAGE_TWO]
    return {
        "stray": total(variant, lambda c: c["stray"]) - total(control, lambda c: c["stray"]) > 1,
        "recall": total(control, len_found) - total(variant, len_found) > recall_margin or per_target,
        "action": total(control, must_fix) - total(variant, must_fix) > action_margin,
        "remedy": total(control, sufficient) - total(variant, sufficient) > action_margin,
        "cost": statistics.median(ratios) > ratio,
    }


def len_found(cell):
    return len(cell["found"])


RATES_IN_USE = {}
ADOPTED = {"recall_margin": 3, "action_margin": 3, "ratio": 0.90}
FIRST_DRAFT = {"recall_margin": 1, "action_margin": 1, "ratio": 0.85, "target_margin": 2}


def cmd_rules(args):
    """How often each decision rule rejects, under no effect and under a real loss."""
    rates = filed_rates(args.repo)
    RATES_IN_USE.update(rates)
    print("## Inputs: valid reviews per defect (recovered/reviews, must-fix, sufficient remedy); enforced geometric-mean cost")
    for target, entry in rates.items():
        print(f"   {target:20s} ${entry['enforced_cost']:.2f}  "
              + "; ".join(f"{d} {r}/{n} mf {m} suf {s}" for d, r, n, m, s in entry["defects"]))
    print("   rates are smoothed as (hits + 0.5) / (n + 1); reviews are drawn independently")
    rng, runs = random.Random(394), 20_000
    scenarios = (("no effect", 1.0, 1.0), ("no effect, control recall x0.7", 0.7, 1.0),
                 ("variant loses 20% of recoveries", 1.0, 0.8), ("variant loses 40% of recoveries", 1.0, 0.6))

    def rate(stage, replicates, targets, control_scale, loss, stray, extra_stray, cost_ratio, spread, **margins):
        tally = Counter()
        for _ in range(runs):
            control = draw_arm(rng, rates, targets, replicates, control_scale, stray, 1.0, spread)
            variant = draw_arm(rng, rates, targets, replicates, control_scale * loss, stray + extra_stray, cost_ratio, spread)
            verdict = stage(control, variant, **margins)
            tally.update(k for k, v in verdict.items() if v)
            tally["quality"] += any(v for k, v in verdict.items() if k != "cost")
            tally["any"] += any(verdict.values())
        return {k: tally[k] / runs for k in ("stray", "recall", "action", "remedy", "cost", "quality", "any")}

    fmt = lambda r, keys: "  ".join(f"{k} {r[k]:6.1%}" for k in keys)
    print("\n## Stage 1, four matched pairs, true cost ratio 0.75, cost spread (log sd) 0.25")
    for title, options in (("adopted: the variant recovers nothing where its control recovers something, on 2 of 3 targets", {}),
                           ("first draft: the variant misses any defect its control recovers, on 2 of 3 targets",
                            {"any_miss": True})):
        print("   " + title)
        for label, control_scale, loss in scenarios:
            print(f"      {label:34s}", fmt(rate(stage_one, 1, STAGE_ONE, control_scale, loss, 1 / 65, 0, 0.75, 0.25, **options),
                                            ("stray", "recall", "cost", "any")))
    print("   cost rule alone, by true cost ratio and spread:")
    for ratio in (1.0, 0.85, 0.75):
        print(f"      true ratio {ratio:.2f}:", "  ".join(
            f"spread {spread:.2f} rejects {rate(stage_one, 1, STAGE_ONE, 1.0, 1.0, 0, 0, ratio, spread)['cost']:6.1%}"
            for spread in (0.15, 0.25, 0.40)))
    print("   stray-finding rule, by the rate of reviews carrying an in-jurisdiction false or non-material finding:")
    strays = ((1 / 65, 0), (4 / 85, 0), (1 / 65, 0.10), (1 / 65, 0.25))
    for stray, extra in strays:
        print(f"      control {stray:.3f}, variant +{extra:.2f}: rejects "
              f"{rate(stage_one, 1, STAGE_ONE, 1.0, 1.0, stray, extra, 0.75, 0.25)['stray']:6.1%}")

    print("\n## Stage 2, fifteen matched pairs, true cost ratio 0.75, cost spread 0.25")
    for title, margins in (("adopted", ADOPTED), ("tighter", {"recall_margin": 2, "action_margin": 3, "ratio": 0.90}),
                           ("first draft", FIRST_DRAFT)):
        print(f"   {title}: {margins}")
        for label, control_scale, loss in scenarios:
            print(f"      {label:34s}", fmt(rate(stage_two, 3, STAGE_TWO, control_scale, loss, 1 / 65, 0, 0.75, 0.25, **margins),
                                            ("stray", "recall", "action", "remedy", "cost", "quality", "any")))
    print("   #394's Stage 2 recall rule on its nine targets, 3 reviews per arm: no target's recall below the control's")
    for label, control_scale, loss in scenarios[:2]:
        lower = 0
        for _ in range(runs):
            control = draw_arm(rng, rates, X394_STAGE_TWO, 3, control_scale, 0, 1.0, 0.25)
            variant = draw_arm(rng, rates, X394_STAGE_TWO, 3, control_scale, 0, 1.0, 0.25)
            lower += any(recovered(variant[t]) < recovered(control[t]) for t in X394_STAGE_TWO)
        print(f"      {label:34s} rejects {lower / runs:6.1%}")
    print("   stray-finding rule over fifteen pairs (variant minus control above 1):")
    for stray, extra in strays:
        result = rate(stage_two, 3, STAGE_TWO, 1.0, 1.0, stray, extra, 0.75, 0.25, **ADOPTED)
        print(f"      control {stray:.3f}, variant +{extra:.2f}: rejects {result['stray']:6.1%}")
    print("   cost rule over fifteen pairs, by true cost ratio and spread (limit 0.85 / 0.90):")
    for ratio in (1.0, 0.85, 0.75, 0.70):
        cells = []
        for spread in (0.15, 0.25, 0.40):
            tight, loose = (rate(stage_two, 3, STAGE_TWO, 1.0, 1.0, 0, 0, ratio, spread,
                                 recall_margin=99, action_margin=99, ratio=limit)["cost"] for limit in (0.85, 0.90))
            cells.append(f"spread {spread:.2f} rejects {tight:6.1%} / {loose:6.1%}")
        print(f"      true ratio {ratio:.2f}:", "  ".join(cells))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["sizes", "exercise", "outcomes", "phases", "machinery", "rules", "all"])
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--transcripts", default=TRANSCRIPTS)
    args = parser.parse_args()
    commands = {"sizes": cmd_sizes, "exercise": cmd_exercise, "outcomes": cmd_outcomes, "phases": cmd_phases,
                "machinery": cmd_machinery, "rules": cmd_rules}
    for name in (commands if args.command == "all" else [args.command]):
        if args.command == "all":
            print(f"\n# {name}")
        commands[name](args)


if __name__ == "__main__":
    sys.exit(main())
