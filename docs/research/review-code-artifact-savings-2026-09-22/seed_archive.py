#!/usr/bin/env python3
"""Regenerate the derived files of this directory's task archive, then seal its manifest.

Provenance for ``archive/``, not part of its reconstruction: ``savings_archive.py`` verifies and
materializes the committed archive without this script. Run it only to rebuild the archive after
changing an authored fixture or template, with the baseline skill named explicitly::

    python3 docs/research/review-code-artifact-savings-2026-09-22/seed_archive.py \\
        --skill-root /abs/path/to/baseline/skills/review-code

Authored inputs: ``archive/fixture/`` (repository text and commit metadata), every task's
``task.json``, ``prompt.md``, specs and evidence, the pull-request page contents below, and the
continuation chain's judgments (``review/initial-input.json``, ``review/initial/raw-return.json``,
``review/composition.json`` and the addendum). Derived here: ``ledger.bundle``; each
``forge-1.json`` and its ``packet.json`` from the skill's ``forge_packet.py normalize``; the suite
and acceptance-exercise outputs; and, by running the skill's own helpers in a scratch task root,
the context store and digest, the verifier bundle, the accounting report, and the composed record,
which are then tokenized under ``savings_archive.py``'s relocation rule. The fixture's suite output
records its own timing, so a rerun changes those bytes and the manifest.

Exit codes: 0 sealed; 1 a helper refused the seed input (its output is printed); 2 unreadable input.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / "archive"
sys.path.insert(0, str(HERE.parent / "tools"))
import savings_archive as sa  # noqa: E402

REPOSITORY_URL = "https://github.com/example/ledger"
PULL_REQUESTS = {
    "publishable": {
        "head": "A1", "created": "2026-09-02T10:05:00Z", "title": "Add CSV statement export",
        "body": "Adds `--format csv` to `ledger statement`, backed by a new `ledger/export.py` that reuses "
                "`statement_rows`.\n\nCloses #3.\n",
        "issue": (3, "Export statements as CSV",
                  "Statements are text-only today; accountants want to open them in a spreadsheet.\n\n"
                  "Acceptance:\n\n"
                  "1. `ledger statement FILE ACCOUNT --format csv` prints the statement as CSV; text stays the default.\n"
                  "2. The first row is the header `date,description,amount,balance`.\n"
                  "3. Amounts and balances use the text statement's decimal format, for example `-4.50`.\n"
                  "4. Descriptions containing commas, quotes, or newlines round-trip through Python's `csv.reader`.\n",
                  "2026-09-01T15:00:00Z")},
    "required-verification": {
        "head": "C1", "created": "2026-09-04T10:05:00Z", "title": "Let delegates read statements",
        "body": "Adds a `delegate` role. Owners grant and revoke delegates with `Ledger.grant` and `Ledger.revoke`; "
                "`can_view` admits a delegate only for accounts that list them.\n\nCloses #5.\n",
        "issue": (5, "Let owners delegate statement access",
                  "Owners want an accountant to read their statements without sharing credentials.\n\n"
                  "Acceptance:\n\n"
                  "1. An account owner can grant another user read-only access to that account's statement, and revoke it.\n"
                  "2. Only the account's owner can grant or revoke; anyone else gets `LedgerError` and nothing changes.\n"
                  "3. A delegate can view only the accounts that granted them access.\n"
                  "4. A delegate can never post entries.\n"
                  "5. Owner, auditor, and teller access is unchanged.\n",
                  "2026-09-01T16:00:00Z")},
}


class Loose(sa.Archive):
    """The archive as it stands on disk, before sealing: every file is trusted as read."""

    def __init__(self, path: Path):
        self.path = path
        self.manifest_raw = (path / sa.MANIFEST).read_bytes()
        self.manifest = json.loads(self.manifest_raw)
        self.manifest["files"] = {p.relative_to(path).as_posix(): {"bytes": p.stat().st_size,
                                                                     "sha256": sa.digest(p.read_bytes())}
                                  for p in sorted(path.rglob("*")) if p.is_file()}


def run(command: list[str], cwd: Path, stdin: bytes = None) -> bytes:
    result = subprocess.run(command, cwd=cwd, input=stdin, capture_output=True)
    if result.returncode != 0:
        sys.stdout.buffer.write(result.stdout + result.stderr)
        raise SystemExit(1)
    return result.stdout


def connection(nodes: list) -> dict:
    return {"totalCount": len(nodes), "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": nodes}


def forge_page(shas: dict, pr: dict) -> dict:
    number, title, body, created = pr["issue"]
    issue = {"number": number, "title": title, "body": body, "url": f"{REPOSITORY_URL}/issues/{number}",
             "updatedAt": created, "lastEditedAt": None, "comments": connection([])}
    return {"data": {"repository": {"url": REPOSITORY_URL, "pullRequest": {
        "title": pr["title"], "body": pr["body"], "state": "OPEN", "merged": False, "isDraft": False,
        "baseRefName": "main", "baseRefOid": shas["M0"], "headRefOid": shas[pr["head"]],
        "updatedAt": pr["created"], "lastEditedAt": None, "baseRepository": {"url": REPOSITORY_URL},
        "closingIssuesReferences": connection([issue]), "reviews": connection([]),
        "reviewThreads": connection([]), "comments": connection([])}}}}


def write(rel: str, raw: bytes) -> None:
    (ARCHIVE / rel).parent.mkdir(parents=True, exist_ok=True)
    (ARCHIVE / rel).write_bytes(raw)


def tokenize(raw: bytes, task_root: Path, skill_root: str, hashes: dict) -> bytes:
    text = raw.decode("utf-8").replace(str(task_root), "@TASK_ROOT@").replace(skill_root, "@SKILL_ROOT@")
    for rel, value in hashes.items():
        text = text.replace(value, f"@SHA256:{rel}@")
    return text.encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skill-root", required=True, help="the baseline review-code skill root")
    skill_root = sa.safe_root(str(Path(parser.parse_args().skill_root).resolve()), "--skill-root")
    scripts = Path(skill_root) / "scripts"
    python = sys.executable
    with tempfile.TemporaryDirectory(prefix="savings-seed-") as scratch:
        scratch = Path(scratch).resolve()
        loose = Loose(ARCHIVE)
        repo = scratch / "fixture"
        shas = sa.build_fixture(loose, repo)
        (ARCHIVE / "ledger.bundle").unlink(missing_ok=True)
        run(["git", "bundle", "create", "-q", str(ARCHIVE / "ledger.bundle"), "--branches"], repo)

        for name, pr in PULL_REQUESTS.items():
            page = (json.dumps(forge_page(shas, pr), indent=2) + "\n").encode("utf-8")
            write(f"tasks/{name}/inputs/forge-1.json", page)
            write(f"tasks/{name}/inputs/packet.json",
                  run([python, str(scripts / "forge_packet.py"), "normalize",
                       str(ARCHIVE / f"tasks/{name}/inputs/forge-1.json")], scratch))

        suite = [python, "-m", "unittest", "discover", "-s", "tests", "-v"]
        for branch, rel in (("date-filter", "tasks/implementation-gate/inputs/unittest-head.txt"),
                            ("freeze", "tasks/continuation/inputs/unittest-D3.txt")):
            run(["git", "checkout", "-q", branch], repo)
            result = subprocess.run(suite, cwd=repo, capture_output=True)
            write(rel, result.stdout + result.stderr)
        run(["git", "checkout", "-q", "date-filter"], repo)
        exercise = b""
        for argv in (["--since", "2026-13-01"], ["--since", "2026-09-03", "--until", "2026-09-01"]):
            command = [python, "-m", "ledger.cli", "statement", "/dev/null", "1001", *argv]
            result = subprocess.run(command, cwd=repo, capture_output=True)
            shown = "python3 -m ledger.cli statement /dev/null 1001 " + " ".join(argv)
            exercise += (f"$ {shown}\nexit {result.returncode}\nstdout:\n{result.stdout.decode()}"
                         f"stderr:\n{result.stderr.decode()}\n").encode("utf-8")
        write("tasks/implementation-gate/inputs/criterion-5.txt", exercise)

        loose = Loose(ARCHIVE)
        task = json.loads((ARCHIVE / "tasks/continuation/task.json").read_text(encoding="utf-8"))
        root = scratch / "root" / "continuation"
        sa.fetch_repository(loose, task, root / "repo")
        path_map = {"@TASK_ROOT@": str(root), "@SKILL_ROOT@": skill_root}
        for rel in ("inputs/spec.md", "review/fingerprint-input.json", "review/initial-input.json",
                    "review/composition.json"):
            raw = (ARCHIVE / "tasks/continuation" / rel).read_bytes()
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes(sa.substitute(raw.decode("utf-8"), path_map, {}).encode("utf-8"))
        steps = {step["run"]: step for step in task["replay"]}
        store = root / steps["review_context"]["store"]
        run([python, str(scripts / "review_context.py"), "--merge-base", steps["review_context"]["merge_base"],
             "--head", steps["review_context"]["head"], "--store", str(store)], root / "repo")
        context = run([python, str(scripts / "context_fingerprint.py"), "--guidance-base",
                       steps["context_fingerprint"]["guidance_base"], "--store", str(store)], root / "repo",
                      (root / "review/fingerprint-input.json").read_bytes()).decode().strip()
        for rel in ("task.json", "review/composition.json"):
            path = ARCHIVE / "tasks/continuation" / rel
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("@SEED:context@", context), encoding="utf-8")
        composition = root / "review/composition.json"
        composition.write_text(composition.read_text(encoding="utf-8").replace("@SEED:context@", context),
                               encoding="utf-8")
        bundle = root / "review/initial"
        run([python, str(scripts / "build_verifier_prompt.py"), str(root / "review/initial-input.json"),
             "--output", str(bundle)], root / "repo")
        hashes = {f"review/initial/{leaf}": sa.digest((bundle / leaf).read_bytes())
                  for leaf in ("input.json", "brief.md", "manifest.json")}
        raw_return = (ARCHIVE / "tasks/continuation/review/initial/raw-return.json").read_text(encoding="utf-8")
        (bundle / "raw-return.json").write_text(sa.substitute(raw_return, path_map, hashes), encoding="utf-8")
        hashes["review/initial/raw-return.json"] = sa.digest((bundle / "raw-return.json").read_bytes())
        run([python, str(scripts / "account_verifier_return.py"), "--bundle", str(bundle), "--output",
             str(bundle / "accounting.json"), str(bundle / "raw-return.json")], root / "repo")
        run([python, str(scripts / "finalize_review.py"), "--profile", "implementation-gate", "--store", str(store),
             str(root / "review")], root / "repo")

        derived = [steps["review_context"]["store"], "review/initial/input.json", "review/initial/brief.md",
                   "review/initial/manifest.json", "review/initial/accounting.json", "review/record.json"]
        for rel in derived:
            raw = (root / rel).read_bytes()
            token_hashes = {} if rel == "review/initial/brief.md" else {
                key: value for key, value in hashes.items() if key != rel}
            write(f"tasks/continuation/{rel}", tokenize(raw, root, skill_root, token_hashes))
        record = json.loads((root / "review/record.json").read_text(encoding="utf-8"))
        pointers = [pointer for pointer, value in sa.walk(record)
                    if not pointer.endswith("#key") and isinstance(value, str)
                    and (value.startswith(str(root)) or value.startswith(skill_root))]
        path = ARCHIVE / "tasks/continuation/task.json"
        text = path.read_text(encoding="utf-8").replace('"@RECORD_PATHS@"', ", ".join(json.dumps(p) for p in pointers))
        path.write_text(json.dumps(json.loads(text), indent=2) + "\n", encoding="utf-8")

    manifest = sa.seal(sa.Archive(str(ARCHIVE)))
    print(f"sealed {len(manifest['files'])} files; context {context}")
    for label, sha in manifest["revisions"].items():
        print(f"{label} {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
