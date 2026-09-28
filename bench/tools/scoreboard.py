#!/usr/bin/env python3
"""Generate the benchmark scoreboard (bench/SCOREBOARD.md) from its registry (bench/scoreboard.json).

Usage::

    python3 bench/tools/scoreboard.py [--registry PATH] [--out PATH]
    python3 bench/tools/scoreboard.py --check [--registry PATH] [--out PATH]

The registry (``schema_version`` 1) lists suites, newest first. A suite has ``id``, ``title``,
``summary``, ``reference`` (the id of the entry to beat), ``cohort_run`` (a run directory relative
to the registry whose manifest cohort fixes the suite's targets, packet hashes, diff identities
and register versions) and ``entries``. An entry has ``id``, ``label``, ``version`` (free text for
the reviewer version it ran), ``sources`` and an optional ``note``. A source has ``run`` (a run
directory relative to the registry), ``results`` (a ``results.v<N>.json`` in that run written by
``score.py``, or null while the run is not scored) and ``arm`` (an arm id of that run's manifest).
An entry with any unscored source is pending everywhere.

Each scored entry gets one status per suite target. At most one of its sources may have attempts
on a target, since one target is never pooled across separately graded runs. With none the target
is ``not run``. With one, the target is ``ran`` when that source's packet hash and diff identity
(from its run's manifest cohort) and the register version its results were graded against (the
results ``inputs``) all equal the suite's, and ``not comparable`` otherwise.

A suite has two headline tables. The first shows each entry over its own ``ran`` targets. The
second pairs each other entry with the reference on the targets both ran. Both sum the chosen
source's ``by_target_arm`` rows per target (recall is the macro mean over buggy targets, cost is
summed cost over summed attempts) and take the median time to completion from the attempt records
the results ``cells`` list, the way ``score.py`` does. The attempt records also give ``billing``.
A target's shape comes from ``targets/<id>/target.json`` beside the registry when that file exists.

Before rendering, every scored source whose arm has attempts on its whole run cohort must
reproduce its ``by_arm`` row from its ``by_target_arm`` rows and attempt records, so the
per-target aggregation cannot drift from ``score.py``. ``--check`` validates the same way, then
compares the page on disk with what would be written.

Exit codes: 0 written, or with ``--check`` the page is current; 1 a problem in the registry or its
inputs (a missing manifest or results file, an arm absent from its run or with no ``by_arm`` row,
a rubric version that differs from the cohort run's, an unknown ``reference``, a duplicate entry
id, two sources of one entry with attempts on the same target, a ``by_arm`` row the per-target
rows do not reproduce), or with ``--check`` a stale page, one line per problem on stdout; 2 an
input cannot be read.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
BENCH = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from score import mean, median, seconds_between  # noqa: E402

SUITE_KEYS = ("id", "title", "summary", "reference", "cohort_run", "entries")
ENTRY_KEYS = ("id", "label", "version", "sources")
SOURCE_KEYS = ("run", "results", "arm")
VALID_KEYS = ("count", "buggy_count", "false_findings_raw", "approved_on_buggy", "zero_recovery", "noise_items")
RAN, NOT_RUN, NOT_COMPARABLE = "ran", "not run", "not comparable"
LIST_PRICE = "list-price-equivalent"
METRICS = ("Valid reviews", "Recall", "Missed every bug", "Approved a buggy change", "False findings",
           "Noise per review", "Sufficient fixes", "Cost per attempt", "Median time")
LEGEND = ("Higher is better for valid reviews, recall and sufficient fixes. Lower is better for missed every bug, "
          "approved a buggy change, false findings, noise, cost and time. Recall is the macro mean over buggy "
          "targets. Per-review figures divide by valid completed reviews. Cost divides the metered price at the "
          "run's rates by every included attempt.")
LIST_PRICE_NOTE = ("† List-price equivalent. These attempts ran on a plan that consumes quota, not dollars, "
                   "so the figure prices their tokens at list rates.")
STATUS_LEGEND = ("*not run* means no run of the row included the target. *not comparable* means the row's run "
                 "graded the target under a different register, packet or diff than this suite. "
                 "*pending* means the row's run is not scored yet.")


class InputError(Exception):
    """An input cannot be read; exit code 2."""


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise InputError(f"cannot read {path}: {error}") from error


def missing_keys(obj, keys) -> list:
    return [k for k in keys if not isinstance(obj, dict) or k not in obj]


def identities(manifest: dict, registers: dict) -> dict:
    return {c["target"]: {"packet": c["packet_sha256"], "diff": c["diff_manifest_sha256"],
                          "register": registers.get(c["target"])} for c in manifest["cohort"]}


def load_cohort(root: Path, suite: dict, problems: list):
    path = root / suite["cohort_run"] / "manifest.json"
    if not path.is_file():
        problems.append(f"{suite['id']}: cohort run manifest {os.path.relpath(path, root)} is missing")
        return None
    manifest = read_json(path)
    return {"rubric": manifest["rubric_version"],
            "targets": identities(manifest, {c["target"]: c["register_version"] for c in manifest["cohort"]})}


def load_source(root: Path, where: str, spec: dict, problems: list):
    run_dir = root / spec["run"]
    paths = [run_dir / "manifest.json"] + ([run_dir / spec["results"]] if spec["results"] is not None else [])
    absent = [p for p in paths if not p.is_file()]
    for path in absent:
        problems.append(f"{where}: {os.path.relpath(path, root)} is missing")
    if absent:
        return None
    manifest, arm = read_json(paths[0]), spec["arm"]
    source = {"spec": spec, "run_dir": run_dir, "rubric": manifest["rubric_version"], "list_price": False}
    if arm not in {a["id"] for a in manifest["arms"]}:
        problems.append(f"{where}: arm {arm} is not in {os.path.relpath(paths[0], root)}")
        return None
    if spec["results"] is None:
        return source
    results = read_json(paths[1])
    row = next((r for r in results["by_arm"] if r["key"]["arm"] == arm), None)
    if row is None:
        problems.append(f"{where}: {os.path.relpath(paths[1], root)} has no by_arm row for arm {arm}")
        return None
    cells = [c for c in results["cells"] if c["arm"] == arm]
    records = {a: read_json(run_dir / "attempts" / a / "attempt.json") for c in cells for a in c["attempts"]}
    source.update({
        "rubric": results.get("rubric_version", manifest["rubric_version"]), "row": row, "cells": cells,
        "by_target": {r["key"]["target"]: r for r in results["by_target_arm"]
                      if r["key"]["arm"] == arm and r["attempts_included"]},
        "targets": identities(manifest, {i["target"]: i["register_version"] for i in results.get("inputs", [])}),
        "planned": [c["target"] for c in manifest["planned_cells"] if c["arm"] == arm],
        "elapsed": {a: seconds_between(r["timing"].get("dispatched_at"), r["timing"].get("completed_at"))
                    for a, r in records.items()},
        "list_price": any(r.get("usage", {}).get("billing") == LIST_PRICE for r in records.values()),
    })
    return source


def load_entry(root: Path, suite_id: str, entry: dict, problems: list):
    where = f"{suite_id}/{entry['id']}"
    specs = entry["sources"] if isinstance(entry["sources"], list) else []
    if not specs:
        problems.append(f"{where}: sources must be a non-empty list")
        return None
    sources = []
    for position, spec in enumerate(specs):
        absent = missing_keys(spec, SOURCE_KEYS)
        if absent:
            problems.append(f"{where}/source {position}: missing {', '.join(absent)}")
            sources.append(None)
        else:
            sources.append(load_source(root, where, spec, problems))
    if any(s is None for s in sources):
        return None
    return {"entry": entry, "sources": sources, "pending": any(s["spec"]["results"] is None for s in sources),
            "list_price": any(s["list_price"] for s in sources)}


def placements(item: dict) -> dict:
    placed = {}
    for source in item["sources"]:
        for target in source.get("by_target", {}):
            placed.setdefault(target, []).append(source)
    return placed


def status(item: dict, suite_targets: dict, target: str) -> tuple:
    chosen = placements(item).get(target)
    mine = chosen and chosen[0]["targets"].get(target)
    if not mine or mine["register"] is None:
        return NOT_RUN, ""
    suite = suite_targets[target]
    reasons = []
    if mine["register"] != suite["register"]:
        reasons.append(f"register v{mine['register']}, suite v{suite['register']}")
    reasons += [f"{field} differs" for field in ("packet", "diff") if mine[field] != suite[field]]
    return (NOT_COMPARABLE, "; ".join(reasons)) if reasons else (RAN, "")


def aggregate(pairs: list) -> dict:
    """Sum (source, target) by_target_arm rows the way score.py builds a row spanning targets."""
    rows = [source["by_target"][target] for source, target in pairs]
    cells = [c for source, target in pairs for c in source["cells"] if c["target"] == target]
    elapsed = [source["elapsed"][a] for source, target in pairs
               for c in source["cells"] if c["target"] == target for a in c["attempts"]]
    costs = [r["cost_contemporaneous_usd"] for r in rows]
    return {
        "attempts_included": sum(r["attempts_included"] for r in rows),
        "valid_reviews": {k: sum(r["valid_reviews"][k] for r in rows) for k in VALID_KEYS},
        "recall_attempt_level": mean([r["recall_attempt_level"] for r in rows if r["recall_attempt_level"] is not None]),
        "false_findings_raw": sum(r["false_findings_raw"] for r in rows),
        "fix_sufficient": {k: sum(r["fix_sufficient"][k] for r in rows) for k in ("sufficient", "partial", "absent")},
        "cost_contemporaneous_usd": None if any(c is None for c in costs) else sum(costs),
        "elapsed_to_completion_s": median(elapsed),
        "cells_valid": sum(c["status"] == "valid completed" for c in cells),
        "cells_planned": sum(t == target for source, target in pairs for t in source["planned"]),
    }


def by_arm_disagreements(source: dict) -> list:
    own = list(source["targets"])
    if any(t not in source["by_target"] for t in own):
        return []
    total, row = aggregate([(source, t) for t in own]), source["row"]

    def differs(a, b) -> bool:
        return a is not b if a is None or b is None else abs(a - b) > 1e-5

    fields = [k for k in ("attempts_included", "false_findings_raw", "recall_attempt_level",
                          "cost_contemporaneous_usd", "elapsed_to_completion_s") if differs(total[k], row[k])]
    fields += [f"valid_reviews.{k}" for k in VALID_KEYS if total["valid_reviews"][k] != row["valid_reviews"][k]]
    fields += ["fix_sufficient"] if total["fix_sufficient"] != row["fix_sufficient"] else []
    return fields


def suite_problems(suite: dict, cohort, loaded: list) -> list:
    problems = []
    ids = [e.get("id") for e in suite["entries"] if isinstance(e, dict)]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"{suite['id']}: duplicate entry id {dup}")
    if suite["reference"] not in ids:
        problems.append(f"{suite['id']}: reference {suite['reference']} names no entry")
    for item in filter(None, loaded):
        where = f"{suite['id']}/{item['entry']['id']}"
        for source in item["sources"]:
            run = source["spec"]["run"]
            if cohort is not None and source["rubric"] != cohort["rubric"]:
                problems.append(f"{where}: {run} uses rubric v{source['rubric']}, the cohort run v{cohort['rubric']}")
            disagreeing = by_arm_disagreements(source) if "row" in source else []
            if disagreeing:
                problems.append(f"{where}: {run} by_target_arm rows do not reproduce its by_arm row on "
                                f"{', '.join(disagreeing)}")
        for target, sources in sorted(placements(item).items()):
            if len(sources) > 1:
                problems.append(f"{where}: {' and '.join(s['spec']['run'] for s in sources)} both have attempts "
                                f"on {target}")
    return problems


def ratio(numerator, denominator) -> str:
    return "n/a" if numerator is None or not denominator else f"{numerator}/{denominator}"


def percent(value) -> str:
    return "n/a" if value is None else f"{value * 100:.0f}%"


def per(numerator, denominator, digits: int) -> str:
    return "n/a" if numerator is None or not denominator else f"{numerator / denominator:.{digits}f}"


def duration(seconds) -> str:
    if seconds is None:
        return "n/a"
    minutes, rest = divmod(int(seconds + 0.5), 60)
    return f"{minutes}m {rest}s" if minutes else f"{rest}s"


class Board:
    def __init__(self, root: Path, out_dir: Path, suite: dict, cohort: dict, loaded: list):
        self.root, self.out_dir, self.suite, self.loaded = root, out_dir, suite, loaded
        self.targets = list(cohort["targets"])
        self.states = {i["entry"]["id"]: {t: status(i, cohort["targets"], t) for t in self.targets}
                       for i in loaded if not i["pending"]}
        self.reference = next(i for i in loaded if i["entry"]["id"] == suite["reference"])

    def ran(self, item: dict) -> list:
        return [t for t in self.targets if self.states[item["entry"]["id"]][t][0] == RAN]

    def metrics(self, item: dict, targets: list) -> list:
        if item["pending"]:
            return ["pending"] * len(METRICS)
        if not targets:
            return ["n/a"] * len(METRICS)
        placed = placements(item)
        m = aggregate([(placed[t][0], t) for t in targets])
        valid, fixes = m["valid_reviews"], m["fix_sufficient"]
        cost = per(m["cost_contemporaneous_usd"], m["attempts_included"], 2)
        return [
            ratio(m["cells_valid"], m["cells_planned"]),
            percent(m["recall_attempt_level"]),
            ratio(valid["zero_recovery"], valid["buggy_count"]),
            ratio(valid["approved_on_buggy"], valid["buggy_count"]),
            f"{m['false_findings_raw']} ({per(valid['false_findings_raw'], valid['count'], 2)} per review)",
            per(valid["noise_items"], valid["count"], 1),
            ratio(fixes["sufficient"], sum(fixes.values())),
            cost if cost == "n/a" else f"${cost}" + (" †" if item["list_price"] else ""),
            duration(m["elapsed_to_completion_s"]),
        ]

    def cell(self, item: dict, target: str) -> str:
        if item["pending"]:
            return "*pending*"
        kind, detail = self.states[item["entry"]["id"]][target]
        if kind == NOT_COMPARABLE:
            return f"*not comparable ({detail})*"
        if kind == NOT_RUN:
            return f"*{kind}*"
        row = placements(item)[target][0]["by_target"][target]
        recall = row["recall_attempt_level"]
        return f"{'clean' if recall is None else percent(recall)} · {row['false_findings_raw']} FF"

    def label(self, item: dict) -> str:
        return item["entry"]["label"] + (" (reference)" if item is self.reference else "")

    def link(self, path: Path) -> str:
        readme = path / "README.md"
        return os.path.relpath(readme if readme.is_file() else path, self.out_dir)

    def sources_section(self) -> list:
        cohort_dir = self.root / self.suite["cohort_run"]
        lines = [f"The {len(self.targets)} targets and their register versions come from "
                 f"[`{cohort_dir.name}`]({self.link(cohort_dir)}). Rows come from:", ""]
        grouped = {}
        for item in self.loaded:
            for source in item["sources"]:
                grouped.setdefault((source["run_dir"], source["spec"]["results"]), []).append(item["entry"]["id"])
        for (run_dir, results), ids in grouped.items():
            scored_as = "not scored yet" if results is None else f"`{results}`"
            lines.append(f"- [`{run_dir.name}`]({self.link(run_dir)}), {scored_as}, for {code_list(ids)}")
        return lines

    def own_targets_table(self) -> list:
        rows = [[self.label(i), i["entry"]["version"],
                 "pending" if i["pending"] else f"{len(self.ran(i))} of {len(self.targets)}",
                 *self.metrics(i, [] if i["pending"] else self.ran(i))] for i in self.loaded]
        lines = ["### Each row on the targets it ran", "",
                 "Rows here cover different target sets, so their numbers do not compare directly. "
                 "The next table compares each row with the reference on the targets both ran.", "",
                 *table(["Reviewer", "Version", "Targets", *METRICS], rows), ""]
        for item in self.loaded:
            if item["pending"]:
                continue
            state = self.states[item["entry"]["id"]]
            gaps = [t for t in self.targets if state[t][0] == NOT_RUN]
            odd = [f"`{t}` ({state[t][1]})" for t in self.targets if state[t][0] == NOT_COMPARABLE]
            said = (([f"did not run {code_list(gaps)}"] if gaps else [])
                    + ([f"is not comparable on {', '.join(odd)}"] if odd else []))
            if said:
                lines.append(f"- **{item['entry']['label']}** at {item['entry']['version']} {' and '.join(said)}.")
        return lines

    def pairwise_table(self) -> list:
        ref = self.reference
        lines = ["### Each row against the reference", "",
                 f"Each row is paired with the reference, {ref['entry']['label']}, on the targets both ran. "
                 "Each cell shows this row, then the reference."]
        if ref["pending"]:
            lines[-1] += " The reference is not scored yet, so every pair is pending."
        rows = []
        for item in self.loaded:
            if item is ref:
                continue
            if item["pending"] or ref["pending"]:
                rows.append([item["entry"]["label"], item["entry"]["version"], "pending", *["pending"] * len(METRICS)])
                continue
            shared = [t for t in self.ran(item) if t in self.ran(ref)]
            pairs = zip(self.metrics(item, shared), self.metrics(ref, shared))
            rows.append([item["entry"]["label"], item["entry"]["version"], str(len(shared)),
                         *(f"{mine} / {theirs}" for mine, theirs in pairs)])
        return lines + ["", *table(["Reviewer", "Version", "Shared targets", *METRICS], rows)]

    def per_target_table(self) -> list:
        header = ["Target", "Shape", *(i["entry"]["label"] for i in self.loaded)]
        rows = [["Version", "", *(i["entry"]["version"] for i in self.loaded)]]
        rows += [[f"`{t}`", target_shape(self.root, t), *(self.cell(i, t) for i in self.loaded)] for t in self.targets]
        return ["### Per target", "",
                "Each cell is attempt-level recall, or clean when the target has no registered defect, "
                "then the raw false-finding count.", "", *table(header, rows), "", STATUS_LEGEND]

    def render(self) -> list:
        lines = [f"## {self.suite['title']}", "", self.suite["summary"], "", *self.sources_section(), "",
                 *self.own_targets_table(), "", *self.pairwise_table(), "", LEGEND]
        if any(i["list_price"] for i in self.loaded):
            lines += ["", LIST_PRICE_NOTE]
        notes = [f"- **{i['entry']['label']}** at {i['entry']['version']}. {i['entry']['note']}"
                 for i in self.loaded if i["entry"].get("note")]
        if notes:
            lines += ["", *notes]
        return lines + ["", *self.per_target_table(), ""]


def table(header, rows) -> list:
    return ["| " + " | ".join(header) + " |", "|" + " --- |" * len(header),
            *("| " + " | ".join(r) + " |" for r in rows)]


def code_list(targets) -> str:
    return ", ".join(f"`{t}`" for t in targets)


def target_shape(root: Path, target: str) -> str:
    path = root / "targets" / target / "target.json"
    return read_json(path).get("shape", "") if path.is_file() else ""


def render(boards: list) -> str:
    lines = [
        "# Reviewer benchmark scoreboard", "",
        "This page holds the headline numbers of the reviewer benchmark, one section per suite. "
        "A suite fixes its targets, packets, diffs, registers and rubric, and every row is marked on each target "
        "it did not run or ran under a different identity. "
        "The legend under each table says which direction is better for each column. "
        "The method and its rules are in [README.md](README.md).", "",
        "The page is generated from `bench/scoreboard.json`. "
        "Regenerate it with `python3 bench/tools/scoreboard.py`. "
        "`python3 bench/tools/scoreboard.py --check` fails when it is stale.", "",
    ]
    for board in boards:
        lines += board.render()
    return "\n".join(lines)


def build(registry_path: Path, out_dir: Path):
    registry = read_json(registry_path)
    root = registry_path.parent
    if not isinstance(registry, dict) or registry.get("schema_version") != 1:
        return None, [f"{registry_path}: schema_version must be 1"]
    problems, suites = [], []
    for index, suite in enumerate(registry.get("suites", [])):
        absent = missing_keys(suite, SUITE_KEYS)
        if absent:
            problems.append(f"suite {index}: missing {', '.join(absent)}")
            continue
        cohort = load_cohort(root, suite, problems)
        loaded = []
        for position, entry in enumerate(suite["entries"]):
            absent = missing_keys(entry, ENTRY_KEYS)
            if absent:
                problems.append(f"{suite['id']}/entry {position}: missing {', '.join(absent)}")
                loaded.append(None)
            else:
                loaded.append(load_entry(root, suite["id"], entry, problems))
        problems += suite_problems(suite, cohort, loaded)
        suites.append((suite, cohort, loaded))
    if problems:
        return None, problems
    return render([Board(root, out_dir, *s) for s in suites]), []


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=Path, default=BENCH / "scoreboard.json")
    parser.add_argument("--out", type=Path, default=BENCH / "SCOREBOARD.md")
    parser.add_argument("--check", action="store_true", help="exit 1 when the page on disk is stale")
    args = parser.parse_args(argv)
    try:
        page, problems = build(args.registry.resolve(), args.out.resolve().parent)
        current = args.out.read_text(encoding="utf-8") if args.check and args.out.is_file() else None
    except (InputError, OSError) as error:
        print(error, file=sys.stderr)
        return 2
    except (KeyError, TypeError) as error:
        print(f"malformed input: {error!r}")
        return 1
    if problems:
        print("\n".join(problems))
        return 1
    if args.check:
        if current != page:
            print(f"{args.out} is stale; run python3 bench/tools/scoreboard.py")
            return 1
        return 0
    args.out.write_text(page, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
