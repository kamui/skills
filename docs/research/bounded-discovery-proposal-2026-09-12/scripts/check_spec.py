#!/usr/bin/env python3
"""Check the proposed study's readiness record against the repository it names.

The specification this record accompanies is *proposed*: every row says what a
future freeze must still establish, and none of them says anything is
established. Two ways that degrades silently are a control or test that was
renamed out from under a row, and a status quietly upgraded to a claim. This
program refuses both.

Usage::

    python3 scripts/check_spec.py [--spec FILE] [--repo-root DIR]
    python3 scripts/check_spec.py --self-test

Checked:

* the document is ``proposed`` and names a specification and probe catalogue
  that exist beside it;
* every status is one of ``tooling-delivered``, ``specified-only``, ``unknown``
  or ``budget-dependent`` - a status asserting a requirement is established,
  frozen, qualified, authorized or approved is refused by name, because a
  proposed specification cannot carry one;
* ``tooling-delivered`` names at least one control and one test;
  ``specified-only`` names no test; ``unknown`` and ``budget-dependent`` name at
  least one open question, so an unresolved choice cannot read as a settled one;
* every control and test path is repository-relative and stays inside the
  repository - an absolute path would be checked against the filesystem and never
  against the repository, and ``..`` escapes it just as quietly - and each one
  exists;
* every ``path::test_name`` resolves to a file that *parses* and really defines
  that test, so ``def test_x(`` inside a docstring cannot stand in for one;
* every ``#199`` gap appears exactly once, ids are unique, and every id is
  discussed in the specification;
* every probe a row claims is defined in the probe catalogue, and every probe the
  catalogue defines is claimed by some row, so neither list drifts from the other.

Input schema (UTF-8 JSON)::

    {"schema_version": str, "document_status": "proposed", "written_at": str,
     "specification": <path beside this record>,
     "probe_catalogue": <path beside this record>,
     "produced_for": {...},
     "requirements": [{"id": str, "source": str, "title": str, "status": str,
                       "controls": [repo-relative path],
                       "tests": [repo-relative path + "::" + test name],
                       "probes": [probe id], "evidence_required": str,
                       "open_questions": [str]}]}

Paths are repository-relative. Unknown keys are violations at both levels.

Exit: 0 success, 1 one or more violations, one line each on stdout, 2 an input
cannot be read, named on stderr.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
REPO_ROOT = BUNDLE.parents[2]

DOCUMENT_KEYS = {"schema_version", "document_status", "written_at", "specification",
                 "probe_catalogue", "produced_for", "requirements"}
REQUIREMENT_KEYS = {"id", "source", "title", "status", "controls", "tests", "probes",
                    "evidence_required", "open_questions"}
STATUSES = ("tooling-delivered", "specified-only", "unknown", "budget-dependent")
# A proposed specification may not carry any of these, whatever it calls them.
CLAIMED = ("established", "frozen", "qualified", "authorized", "authorised",
           "approved", "ready", "complete", "done")
REQUIRED_IDS = tuple("gap-%d" % number for number in range(1, 11))
PROBE_ROW = re.compile(r"^\|\s*(P\d{2})\s*\|")


def load(path: Path):
    """Read a JSON document, or exit 2 through OSError/ValueError to the caller."""
    return json.loads(path.read_text(encoding="utf-8"))


def path_problem(where: str, relative: str, repo_root: Path, kind: str):
    """Resolve one repository-relative path, refusing anything that leaves the repository.

    ``repo_root / "/somewhere"`` is ``/somewhere``: an absolute entry would be
    checked against the filesystem and never against the repository at all, and
    ``..`` escapes it just as quietly. Both are refused by shape, and the resolved
    path is required to stay inside the root, so a symlink cannot smuggle one in.
    """
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        return "%s names %s %s, which is not a repository-relative path" % (where, kind, relative)
    path = repo_root / relative
    try:
        inside = path.resolve().is_relative_to(repo_root.resolve())
    except OSError as exc:
        return "%s names %s %s, which cannot be resolved: %s" % (where, kind, relative, exc)
    if not inside:
        return "%s names %s %s, which resolves outside the repository" % (where, kind, relative)
    if not path.is_file():
        return "%s names %s %s, which does not exist" % (where, kind, relative)
    return None


def test_problem(where: str, relative: str, name: str, repo_root: Path):
    """Whether this file really defines that test, so a rename cannot leave a stale row.

    Parsed rather than matched: ``def test_x(`` inside a docstring or a string
    literal is text about a test, not a test, and a row citing one would pass a
    textual check while naming nothing runnable.
    """
    problem = path_problem(where, relative, repo_root, "test file")
    if problem:
        return problem
    path = repo_root / relative
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        return "%s names test file %s, which cannot be read: %s" % (where, relative, exc)
    except SyntaxError as exc:
        return "%s names test file %s, which does not parse: %s" % (where, relative, exc)
    defined = {node.name for node in ast.walk(tree)
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    if name not in defined:
        return "%s names %s, which %s does not define" % (where, name, relative)
    return None


def catalogue_probes(path: Path) -> set:
    return {match.group(1)
            for match in (PROBE_ROW.match(line) for line in
                          path.read_text(encoding="utf-8").splitlines())
            if match}


def key_problems(where: str, mapping, allowed: set) -> list:
    if not isinstance(mapping, dict):
        return ["%s is not an object" % where]
    problems = ["%s has unknown key %s" % (where, key)
                for key in sorted(set(mapping) - allowed)]
    problems += ["%s is missing %s" % (where, key)
                 for key in sorted(allowed - set(mapping))]
    return problems


def text_problems(where: str, value) -> list:
    if not isinstance(value, str) or not value.strip():
        return ["%s must be a non-empty string" % where]
    return []


def list_problems(where: str, value) -> list:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip()
                                          for item in value):
        return ["%s must be a list of non-empty strings" % where]
    return []


def status_problems(where: str, status) -> list:
    if not isinstance(status, str):
        return ["%s status must be a string" % where]
    if status in STATUSES:
        return []
    claimed = next((word for word in CLAIMED
                    if re.search(r"\b%s\b" % word, status.lower())), None)
    if claimed:
        return ["%s status %r claims the requirement is %s; a proposed specification "
                "records what a freeze must still establish" % (where, status, claimed)]
    return ["%s status %r is not one of %s" % (where, status, ", ".join(STATUSES))]


def requirement_problems(requirement, repo_root: Path, probes: set,
                         specification: str) -> list:
    where = "requirement %s" % (requirement.get("id") if isinstance(requirement, dict)
                                else "?")
    problems = key_problems(where, requirement, REQUIREMENT_KEYS)
    if problems:
        return problems
    for field in ("id", "source", "title", "evidence_required"):
        problems += text_problems("%s %s" % (where, field), requirement[field])
    for field in ("controls", "tests", "probes", "open_questions"):
        problems += list_problems("%s %s" % (where, field), requirement[field])
    problems += status_problems(where, requirement["status"])
    if problems:
        return problems

    status = requirement["status"]
    if status == "tooling-delivered" and not (requirement["controls"] and requirement["tests"]):
        problems.append("%s is tooling-delivered but names %d control(s) and %d test(s); "
                        "delivered tooling is named or it is not delivered"
                        % (where, len(requirement["controls"]), len(requirement["tests"])))
    if status == "specified-only" and requirement["tests"]:
        problems.append("%s is specified-only but names tests; a row with tests covering it "
                        "is tooling-delivered" % where)
    if status in ("unknown", "budget-dependent") and not requirement["open_questions"]:
        problems.append("%s is %s and records no open question, so what is unresolved about "
                        "it cannot be read" % (where, status))

    for control in requirement["controls"]:
        problem = path_problem(where, control, repo_root, "control")
        if problem:
            problems.append(problem)
    for entry in requirement["tests"]:
        if entry.count("::") != 1:
            problems.append("%s test %r is not <path>::<test name>" % (where, entry))
            continue
        relative, name = entry.split("::")
        problem = test_problem(where, relative, name, repo_root)
        if problem:
            problems.append(problem)
    for probe in requirement["probes"]:
        if probe not in probes:
            problems.append("%s claims probe %s, which the catalogue does not define"
                            % (where, probe))
    if requirement["id"] not in specification:
        problems.append("%s is not discussed in the specification" % where)
    return problems


def check(spec_path: Path, repo_root: Path) -> list:
    document = load(spec_path)
    problems = key_problems("document", document, DOCUMENT_KEYS)
    if problems:
        return problems
    if document["document_status"] != "proposed":
        problems.append("document_status is %r; this record describes a proposed "
                        "specification" % document["document_status"])
    problems += text_problems("document schema_version", document["schema_version"])
    problems += text_problems("document written_at", document["written_at"])
    if not isinstance(document["produced_for"], dict) or not document["produced_for"]:
        problems.append("produced_for must name the issues this record was written for")

    beside = {}
    for field in ("specification", "probe_catalogue"):
        value = document[field]
        if not isinstance(value, str) or "/" in value or not (spec_path.parent / value).is_file():
            problems.append("%s must name a file beside this record" % field)
        else:
            beside[field] = spec_path.parent / value
    if len(beside) != 2:
        return problems

    probes = catalogue_probes(beside["probe_catalogue"])
    if not probes:
        problems.append("the probe catalogue defines no probe")
    specification = beside["specification"].read_text(encoding="utf-8")

    requirements = document["requirements"]
    if not isinstance(requirements, list) or not requirements:
        return problems + ["requirements must be a non-empty list"]

    seen = []
    claimed_probes = set()
    for requirement in requirements:
        problems += requirement_problems(requirement, repo_root, probes, specification)
        if isinstance(requirement, dict):
            seen.append(requirement.get("id"))
            claimed_probes.update(requirement.get("probes") or [])
    for identifier in REQUIRED_IDS:
        if seen.count(identifier) != 1:
            problems.append("%s appears %d time(s); every #199 gap is carried exactly once"
                            % (identifier, seen.count(identifier)))
    for identifier in sorted({name for name in seen if seen.count(name) > 1}):
        problems.append("requirement id %s is used more than once" % identifier)
    for probe in sorted(probes - claimed_probes):
        problems.append("probe %s is defined in the catalogue and claimed by no requirement"
                        % probe)
    return problems


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--spec", default=str(BUNDLE / "readiness.json"),
                        help="the readiness record to check")
    parser.add_argument("--repo-root", default=str(REPO_ROOT),
                        help="the repository the record's paths are relative to")
    parser.add_argument("--self-test", action="store_true")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        return subprocess.run([sys.executable,
                               str(HERE / "test_check_spec.py")]).returncode
    try:
        problems = check(Path(args.spec), Path(args.repo_root))
    except (OSError, ValueError) as exc:
        print("%s: %s" % (args.spec, exc), file=sys.stderr)
        return 2
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
