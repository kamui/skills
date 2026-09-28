#!/usr/bin/env python3
"""Build trimmed copies of review-code and run the repository's free checks on them.

Usage:
    python3 -B variants.py [--repo PATH] [--work DIR] [--tests] [V] [S] [Q] [base]

The repository is only read. Each variant is a copy of `skills/` under --work
(default: a new temporary directory), edited there. With --tests the copy's own
test files run as well as its instruction budget check. Every edit must match
its source text exactly once, so a moved line fails loudly instead of trimming
something else.

V  removes the independent verification phase: the Verification section, step 6,
   the verification clauses elsewhere in the always-loaded text, and the
   finalizer's requirement that a must-fix or risk-kind finding carry a confirmed
   task. The three verification references and two helper scripts stay on disk
   and are never loaded; the byte table reports them as removed from the runtime
   set.
S  removes safety premises only, the fallback if V is rejected on candidate
   confirmation: the Safety premises paragraph and the reconcile rule for a failed
   premise. The worker's premise section stays, because a test asserts its heading.
Q  removes the requirements ledger: the rubric section and step 3's row keeping.
   The finalizer already accepts an empty `record.requirements`.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
SKILL = "skills/review-code"
ALWAYS = ("SKILL.md", "references/rubric.md", "references/output.md")


def section(text, heading):
    """The span from `heading` to the next heading of the same or a higher level."""
    start = text.index("\n" + heading + "\n") + 1
    level = len(heading) - len(heading.lstrip("#"))
    position = start + len(heading)
    while True:
        position = text.index("\n#", position) + 1
        marks = len(text[position:].split(" ", 1)[0])
        if marks <= level:
            return start, position


V_EDITS = [
    ("SKILL.md", "6. **Verify** under Verification below, after the complete pass.\n7. **Record.**", "6. **Record.**"),
    ("SKILL.md", ", every required fetch finished, and no required verification is unfinished.",
     ", and every required fetch finished."),
    ("SKILL.md", "a changed file, required check, required verification, or required input did not finish.",
     "a changed file, required check, or required input did not finish."),
    ("SKILL.md", " starts a new run in a new private directory with its own allowance;",
     " starts a new run in a new private directory;"),
    ("references/rubric.md", ", and the compatibility verification trigger;", ";"),
    ("references/rubric.md", " so ordinarily `must-fix`, verified under the red-test rule.", " so ordinarily `must-fix`."),
    ("references/rubric.md", "Reuse never replaces changed-test inspection, verification, or safety-premise challenges, never widens",
     "Reuse never replaces changed-test inspection, never widens"),
    ("references/rubric.md", " but no qualifying consequence, or a verifier aside;", " but no qualifying consequence;"),
    ("references/rubric.md", " A required unresolved verification task ends as a qualifying question or outstanding work, never a private drop.", ""),
    ("references/rubric.md", "; use `concurrency` or `invariant` for shared-state rules needing the verifier's bug-class check. "
     "Keep the falsifiable claim apart from private support, which never enters a verifier brief. "
     "Only primary-admitted survivors render, confirmed when required, and a confirmation survives a lowered priority or action.",
     ". Only primary-admitted survivors render."),
    ("references/output.md", "After verification, author judgments", "Author judgments"),
    ("references/output.md", "or drop a verified finding to pass validation", "or drop a finding to pass validation"),
]

S_PARAGRAPHS = [
    ("SKILL.md", "**Safety premises.** "),
    ("references/verification.md", "A failed premise reopens as a candidate named by `reopened_as`"),
]

Q_EDITS = [
    ("SKILL.md", "3. **Ledger intent.** Read [`rubric.md`](references/rubric.md). List the requirements from issues and specs, "
     "then from the change description, before reading the diff for compliance. Each row ends `met`, `partial`, or "
     "`not-verifiable` with evidence. A requirement missed",
     "3. **Read intent.** Read [`rubric.md`](references/rubric.md), then the issues, specs and change description, before "
     "reading the diff. A requirement missed"),
    ("references/rubric.md", "When a ledger promise changes an externally observable contract",
     "When a stated promise changes an externally observable contract"),
    ("references/rubric.md", ", give the row a `compliance` disposition", ", record a `compliance` disposition"),
    ("references/rubric.md", "raise a linked `kind=compatibility` candidate, keep its id in the row, and falsify it",
     "raise a linked `kind=compatibility` candidate and falsify it"),
]

FINALIZER_CHECK = '''    for finding in findings:
        mandatory = "must-fix" if finding["action"] == "must-fix" else finding["kind"] if finding["kind"] in MANDATORY_KINDS else None
        task = by_id.get(finding["id"], {})
        if mandatory is not None and not (task.get("type") == "candidate" and task.get("trigger") not in (None, "optional")
                                          and task.get("ruling") == "confirmed"):
'''


def edit(root, relative, old, new):
    path = os.path.join(root, relative)
    text = open(path, encoding="utf-8").read()
    if text.count(old) != 1:
        raise SystemExit(f"{relative}: expected one match, found {text.count(old)}: {old[:70]!r}")
    open(path, "w", encoding="utf-8").write(text.replace(old, new))


def drop_section(root, relative, heading):
    path = os.path.join(root, relative)
    text = open(path, encoding="utf-8").read()
    start, end = section(text, heading)
    open(path, "w", encoding="utf-8").write(text[:start] + text[end:])
    return len(text[start:end].encode("utf-8"))


def drop_paragraph(root, relative, opening):
    """Remove the one paragraph that starts with `opening`, and the blank line after it."""
    path = os.path.join(root, relative)
    text = open(path, encoding="utf-8").read()
    if text.count("\n" + opening) != 1:
        raise SystemExit(f"{relative}: expected one paragraph starting {opening[:50]!r}")
    start = text.index("\n" + opening) + 1
    end = text.index("\n\n", start) + 2
    open(path, "w", encoding="utf-8").write(text[:start] + text[end:])
    return len(text[start:end].encode("utf-8"))


def build(repo, work, name):
    target = os.path.join(work, name)
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(os.path.join(repo, "skills"), os.path.join(target, "skills"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    root = os.path.join(target, SKILL)
    notes = []
    if "V" in name:
        notes.append(("SKILL.md ## Verification", drop_section(root, "SKILL.md", "## Verification")))
        for relative, old, new in V_EDITS:
            edit(root, relative, old, new)
        script = os.path.join(root, "scripts/render_review.py")
        text = open(script, encoding="utf-8").read()
        start = text.index(FINALIZER_CHECK)
        end = text.index("\n", text.index("report.add(", start)) + 1
        notes.append(("render_review.py mandatory-confirmation check", len(text[start:end].encode("utf-8"))))
        open(script, "w", encoding="utf-8").write(text[:start] + text[end:])
    if "S" in name:
        for relative, opening in S_PARAGRAPHS:
            notes.append((f"{relative} paragraph {opening[:28]!r}", drop_paragraph(root, relative, opening)))
    if "Q" in name:
        notes.append(("rubric.md ## Requirements ledger", drop_section(root, "references/rubric.md", "## Requirements ledger")))
        for relative, old, new in Q_EDITS:
            edit(root, relative, old, new)
    return root, notes


def measure(root, name):
    read = lambda relative: len(open(os.path.join(root, relative), "rb").read())
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

    def helper(script, flag):
        done = subprocess.run([sys.executable, "-B", os.path.join(root, "scripts", script), flag],
                              capture_output=True, env=env)
        return len(done.stdout)
    references = ["targets.md", "prior-state.md", "verification.md", "verifier.md", "verifier-concurrency.md"]
    if "V" in name:
        references = ["targets.md", "prior-state.md"]
    always = sum(read(relative) for relative in ALWAYS)
    review = always + helper("review_context.py", "--help") + read("references/targets.md") + helper("render_review.py", "--example")
    out = {
        "always loaded": always,
        "review": review,
        "re-review": review + read("references/prior-state.md"),
        "runtime total": always + sum(read("references/" + r) for r in references),
    }
    if "V" not in name:
        out["required verifier"] = review + read("references/verification.md") + helper("build_verifier_prompt.py", "--example")
    return out


def tests(root):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    results = {}
    scripts = os.path.join(root, "scripts")
    for name in sorted(os.listdir(scripts)):
        if name.startswith("test_") and name.endswith(".py"):
            done = subprocess.run([sys.executable, "-B", name], cwd=scripts, capture_output=True, env=env, text=True)
            tail = (done.stdout + done.stderr).strip().splitlines()[-1:] or [""]
            results[name] = (done.returncode, tail[0][:110])
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("names", nargs="*", default=["base", "V", "S", "Q"])
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--work", help="directory for the copies; default is a new temporary directory")
    parser.add_argument("--tests", action="store_true")
    parser.add_argument("--keep", action="store_true", help="leave the copies in --work")
    args = parser.parse_args()
    work = args.work or tempfile.mkdtemp(prefix="review-code-variants-")
    os.makedirs(work, exist_ok=True)
    table = {}
    for name in args.names:
        root, notes = build(args.repo, work, name)
        table[name] = measure(root, name)
        print(f"\n## {name}")
        for label, size in notes:
            print(f"   removed {size:6,d} B  {label}")
        for key, value in table[name].items():
            base = table.get("base", {}).get(key)
            change = f"  ({value - base:+,d})" if base is not None and name != "base" else ""
            print(f"   {key:18s} {value:7,d}{change}")
        if args.tests:
            for test, (code, tail) in tests(root).items():
                print(f"   {test:32s} exit {code}  {tail}")
        if not args.keep:
            shutil.rmtree(os.path.join(work, name), ignore_errors=True)
    if args.keep:
        print(f"\ncopies kept in {work}")
    elif not args.work:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
