#!/usr/bin/env python3
"""Verify, rebuild, materialize, and check the review-code artifact-savings task archive.

The archive freezes repository-local review-code interface tasks: text fixtures for a small
repository, a git bundle holding every commit the tasks need, each task's exact prompt, specs,
evidence and packets, and a seeded implementation-gate record, addendum and verifier-accounting
chain. ``manifest.json`` records the SHA-256 and size of every archived file, the fixture commit
SHAs, and the bundle's heads. Nothing here reads the network or the checkout it came from.

Usage::

    python3 docs/research/tools/savings_archive.py verify ARCHIVE
    python3 docs/research/tools/savings_archive.py fixture ARCHIVE --out DIR [--bundle FILE]
    python3 docs/research/tools/savings_archive.py materialize ARCHIVE --root DIR --skill-root DIR [--task NAME ...]
    python3 docs/research/tools/savings_archive.py check ARCHIVE --root DIR [--skill-root DIR]
    python3 docs/research/tools/savings_archive.py seal ARCHIVE

``verify`` checks every manifest entry's size and hash, refuses unlisted files, checks each task's
template declarations, and compares the bundle's heads with the manifest. ``fixture`` rebuilds the
repository from ``fixture/fixture.json`` with pinned identities and dates and compares every
commit SHA with the manifest; ``--bundle`` also writes a bundle of its branches. ``seal`` rewrites
the manifest's ``files``, ``revisions`` and ``bundle.heads`` from the archive as it stands, writing
the bundle from the rebuilt fixture when none exists; it is for maintainers, and the committed
manifest is what ``verify`` trusts.

``materialize`` writes each task under ``ROOT/<task>``: a repository fetched from the bundle
with only the task's branches and its declared branch checked out, and every template realized
by the canonical relocation rule below. It writes ``ROOT/realization.json`` with the path map,
the archive manifest's hash, this tool's hash for provenance, and each file's template and realized
hashes.
``check`` recomputes every realized file from the archive and the recorded path map, compares
bytes and recorded hashes, compares each realized JSON value with its template after masking only
the declared fields, and confirms each repository's branches, checked-out head and clean tree.
With ``--skill-root`` it also realizes each task a second time in a scratch root and replays the
task's declared helper commands there under that skill, requiring byte-identical output: the
context store, context digest, verifier bundle, accounting report and composed record.

Relocation. Templates carry three tokens: ``@TASK_ROOT@`` (``ROOT/<task>``), ``@SKILL_ROOT@`` (the
arm's installed review-code root), and ``@SHA256:<task-relative path>@`` (the SHA-256 of that
realized file). A ``text`` template may carry the two path tokens anywhere; a ``copy`` template
carries none. A ``json`` template carries them only in string values at its declared JSON-pointer
patterns (``*`` matches one segment): ``paths`` values start with a path token, ``carried`` values
are ``carried:@TASK_ROOT@/<file>#<batch>``, and ``hashes`` values are exactly one hash token. A
``brief`` template is a verifier brief whose tail is the canonical JSON of its declared ``input``
file; realization re-renders that tail from the realized input. Files are realized in hash
dependency order, so a relocated bundle input changes the brief, the manifest, the raw return's
``manifest_sha256``, and the accounting report's hashes together. Every other byte, including
revisions and judgments, is copied unchanged. ROOT and the skill root must be absolute and use
only ``A-Z a-z 0-9 . _ + / -``, so substitution never needs JSON escaping.

Exit codes: 0 success; 1 content violations, one per stdout line; 2 an unreadable archive,
a refused output path, or a failed subprocess, named on stderr.
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
from pathlib import Path
from typing import Any, Iterator, Optional

MANIFEST = "manifest.json"
ARCHIVE_FORMAT = "savings-archive/1"
TASK_FORMAT = "savings-task/1"
REALIZATION_FORMAT = "savings-realization/1"
FIXTURE_FORMAT = "savings-fixture/1"
PATH_TOKENS = ("@TASK_ROOT@", "@SKILL_ROOT@")
TOKEN_RE = re.compile(r"@(?:TASK_ROOT|SKILL_ROOT)@|@SHA256:([A-Za-z0-9._/-]+)@")
ANY_TOKEN_RE = re.compile(r"@(?:TASK_ROOT|SKILL_ROOT|SHA256:[^@]*)@")
SAFE_ROOT_RE = re.compile(r"/[A-Za-z0-9._+/-]*")
CARRIED_RE = re.compile(r"carried:@TASK_ROOT@/[^#@]+#[^#@]+")
KINDS = ("copy", "text", "json", "brief")


class Violation(Exception):
    """Archive content that does not satisfy its declarations."""


class Failure(Exception):
    """An unreadable input, a refused output, or a failed subprocess."""


# --- small helpers -------------------------------------------------------------------------------


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def json_text(value: Any) -> str:
    """The canonical JSON review-code's verifier builder writes and embeds in a brief."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key {key}")
        result[key] = value
    return result


def parse_json(raw: bytes, where: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates)
    except (UnicodeDecodeError, ValueError) as error:
        raise Violation(f"{where}: not JSON: {error}") from None


def git(args: list[str], cwd: Optional[Path] = None, env: Optional[dict] = None,
        stdin: Optional[bytes] = None) -> str:
    command = ["git", *args]
    try:
        result = subprocess.run(command, cwd=cwd, env=env, input=stdin, capture_output=True)
    except OSError as error:
        raise Failure(f"cannot run {' '.join(command)}: {error}") from None
    if result.returncode != 0:
        raise Failure(f"{' '.join(command)} exited {result.returncode}: "
                      f"{result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout.decode("utf-8")


def walk(value: Any, pointer: str = "") -> Iterator[tuple[str, Any]]:
    """Yield (pointer, value) for every scalar, and ('<pointer>#key', key) for every object key."""
    if isinstance(value, dict):
        for key, item in value.items():
            child = pointer + "/" + key.replace("~", "~0").replace("/", "~1")
            yield child + "#key", key
            yield from walk(item, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f"{pointer}/{index}")
    else:
        yield pointer, value


def matches(pattern: str, pointer: str) -> bool:
    left, right = pattern.split("/"), pointer.split("/")
    return len(left) == len(right) and all(a in ("*", b) for a, b in zip(left, right))


def safe_root(value: str, name: str) -> str:
    if not (SAFE_ROOT_RE.fullmatch(value) and value != "/" and not value.endswith("/")
            and "//" not in value and "/./" not in value + "/" and "/../" not in value + "/"):
        raise Failure(f"{name} must be a normalized absolute path using only A-Z a-z 0-9 . _ + / -: {value!r}")
    return value


# --- archive and declarations --------------------------------------------------------------------


class Archive:
    def __init__(self, path: str):
        self.path = Path(path).resolve()
        try:
            self.manifest_raw = (self.path / MANIFEST).read_bytes()
        except OSError as error:
            raise Failure(f"cannot read {self.path / MANIFEST}: {error}") from None
        try:
            self.manifest = parse_json(self.manifest_raw, MANIFEST)
        except Violation as error:
            raise Failure(str(error)) from None
        if not isinstance(self.manifest, dict) or self.manifest.get("format") != ARCHIVE_FORMAT:
            raise Failure(f"{MANIFEST}: expected format {ARCHIVE_FORMAT}")

    def read(self, rel: str) -> bytes:
        entry = self.manifest.get("files", {}).get(rel)
        if entry is None:
            raise Violation(f"{rel}: not in the manifest")
        try:
            raw = (self.path / rel).read_bytes()
        except OSError:
            raise Violation(f"{rel}: missing") from None
        if len(raw) != entry.get("bytes") or digest(raw) != entry.get("sha256"):
            raise Violation(f"{rel}: altered (manifest sha256 {entry.get('sha256')})")
        return raw

    def tasks(self) -> list[str]:
        return list(self.manifest.get("tasks", []))

    def task(self, name: str) -> dict:
        task = parse_json(self.read(f"tasks/{name}/task.json"), f"tasks/{name}/task.json")
        if not isinstance(task, dict) or task.get("format") != TASK_FORMAT or task.get("name") != name:
            raise Violation(f"tasks/{name}/task.json: expected format {TASK_FORMAT} named {name}")
        return task


def hash_refs(raw: bytes) -> list[str]:
    return [match.group(1) for match in TOKEN_RE.finditer(raw.decode("utf-8")) if match.group(1)]


def check_template(name: str, rel: str, spec: dict, raws: dict, files: dict) -> None:
    """Refuse a template whose tokens fall outside its declarations."""
    where = f"tasks/{name}/{rel}"
    kind, raw = spec.get("kind"), raws[rel]
    if kind not in KINDS:
        raise Violation(f"{where}: unknown kind {kind!r}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = None
    tokens = ANY_TOKEN_RE.findall(text) if text is not None else []
    bad = [token for token in tokens if not TOKEN_RE.fullmatch(token)]
    if bad:
        raise Violation(f"{where}: malformed token {bad[0]}")
    for target in hash_refs(raw):
        if target not in files or target == rel:
            raise Violation(f"{where}: hash token names {target}, not another file of this task")
    if kind == "copy":
        if tokens:
            raise Violation(f"{where}: a copy template carries tokens")
        return
    if text is None:
        raise Violation(f"{where}: {kind} template is not UTF-8")
    if kind == "text":
        if hash_refs(raw):
            raise Violation(f"{where}: a text template carries a hash token")
        return
    if kind == "brief":
        source = spec.get("input")
        if files.get(source, {}).get("kind") != "json":
            raise Violation(f"{where}: input must name a json template of this task")
        tail = json_text(parse_json(raws[source], where)).encode("utf-8")
        if not raw.endswith(tail):
            raise Violation(f"{where}: brief does not end with its input's canonical JSON")
        if ANY_TOKEN_RE.search(raw[: len(raw) - len(tail)].decode("utf-8")):
            raise Violation(f"{where}: token outside the brief's supplied-records JSON")
        return
    declared = {"paths": spec.get("paths", []), "carried": spec.get("carried", []), "hashes": spec.get("hashes", [])}
    document = parse_json(raw, where)
    used = {pattern: 0 for group in declared.values() for pattern in group}
    for pointer, value in walk(document):
        if not (isinstance(value, str) and ANY_TOKEN_RE.search(value)):
            continue
        if pointer.endswith("#key"):
            raise Violation(f"{where}: token in object key {pointer[:-4]}")
        groups = [group for group, patterns in declared.items() if any(matches(p, pointer) for p in patterns)]
        if len(groups) != 1:
            raise Violation(f"{where}{pointer}: token outside exactly one declared field group")
        group = groups[0]
        for pattern in declared[group]:
            if matches(pattern, pointer):
                used[pattern] += 1
        if group == "paths" and not any(value == t or value.startswith(t + "/") for t in PATH_TOKENS):
            raise Violation(f"{where}{pointer}: a path field must start with a path token")
        if group == "carried" and not CARRIED_RE.fullmatch(value):
            raise Violation(f"{where}{pointer}: a carried field is carried:@TASK_ROOT@/<file>#<batch>")
        if group == "hashes" and not (TOKEN_RE.fullmatch(value) and value.startswith("@SHA256:")):
            raise Violation(f"{where}{pointer}: a hash field is exactly one hash token")
        if group != "hashes" and hash_refs(value.encode("utf-8")):
            raise Violation(f"{where}{pointer}: hash token in a {group} field")
        if len(ANY_TOKEN_RE.findall(value)) != 1:
            raise Violation(f"{where}{pointer}: more than one token in one field")
    for pattern, count in used.items():
        if count == 0:
            raise Violation(f"{where}: declared field {pattern} matches no token-bearing value")


def order(name: str, files: dict, raws: dict) -> list[str]:
    """Templates in hash-dependency order; a brief follows its input."""
    needs = {rel: set(hash_refs(raws[rel])) | ({spec["input"]} if spec.get("kind") == "brief" else set())
             for rel, spec in files.items()}
    done: list[str] = []
    while len(done) < len(files):
        ready = sorted(rel for rel in files if rel not in done and needs[rel] <= set(done))
        if not ready:
            raise Violation(f"tasks/{name}: hash dependencies form a cycle")
        done.extend(ready)
    return done


def task_templates(archive: Archive, name: str) -> tuple[dict, dict, dict]:
    task = archive.task(name)
    files = task.get("files")
    if not isinstance(files, dict) or not files:
        raise Violation(f"tasks/{name}/task.json: no files")
    raws = {rel: archive.read(f"tasks/{name}/{rel}") for rel in files}
    for rel, spec in files.items():
        if not isinstance(spec, dict):
            raise Violation(f"tasks/{name}/task.json: files[{rel}] is not an object")
        check_template(name, rel, spec, raws, files)
    order(name, files, raws)
    return task, files, raws


def verify(archive: Archive) -> list[str]:
    violations: list[str] = []
    listed = archive.manifest.get("files")
    if not isinstance(listed, dict):
        return [f"{MANIFEST}: files must be an object"]
    for rel in sorted(listed):
        try:
            archive.read(rel)
        except Violation as error:
            violations.append(str(error))
    for path in sorted(archive.path.rglob("*")):
        rel = path.relative_to(archive.path).as_posix()
        if path.is_file() and rel != MANIFEST and rel not in listed:
            violations.append(f"{rel}: unlisted file")
    for name in archive.tasks():
        try:
            task, _, _ = task_templates(archive, name)
            revisions = set(archive.manifest.get("revisions", {}).values())
            for ref, sha in task.get("repository", {}).get("refs", {}).items():
                if sha not in revisions:
                    violations.append(f"tasks/{name}/task.json: ref {ref} names {sha}, not a fixture revision")
        except Violation as error:
            violations.append(str(error))
    bundle = archive.manifest.get("bundle", {})
    try:
        archive.read(bundle.get("path", ""))
        heads = bundle_heads(archive.path / bundle["path"])
        if heads != bundle.get("heads"):
            violations.append(f"{bundle.get('path')}: heads {heads} differ from the manifest")
    except Violation as error:
        violations.append(str(error))
    return list(dict.fromkeys(violations))


def bundle_heads(path: Path) -> dict:
    heads = {}
    for line in git(["bundle", "list-heads", str(path)]).splitlines():
        sha, ref = line.split(" ", 1)
        heads[ref] = sha
    return heads


def require_verified(archive: Archive) -> None:
    violations = verify(archive)
    if violations:
        raise Violation("\n".join(["archive does not verify:"] + violations))


# --- fixture repository --------------------------------------------------------------------------


def build_fixture(archive: Archive, out: Path) -> dict:
    """Rebuild the fixture repository with plumbing and pinned metadata; return label -> SHA."""
    fixture = parse_json(archive.read("fixture/fixture.json"), "fixture/fixture.json")
    if fixture.get("format") != FIXTURE_FORMAT:
        raise Violation(f"fixture/fixture.json: expected format {FIXTURE_FORMAT}")
    if out.exists():
        raise Failure(f"refusing to overwrite {out}")
    out.mkdir(parents=True)
    git(["init", "-q", "--initial-branch=fixture-build", str(out)])
    identity = fixture["identity"]
    shas: dict = {}
    trees: dict = {}
    with tempfile.TemporaryDirectory(prefix="savings-index-") as scratch:
        for commit in fixture["commits"]:
            label, parent = commit["label"], commit["parent"]
            env = dict(os.environ, GIT_INDEX_FILE=os.path.join(scratch, "index"),
                       GIT_AUTHOR_NAME=identity["name"], GIT_AUTHOR_EMAIL=identity["email"],
                       GIT_COMMITTER_NAME=identity["name"], GIT_COMMITTER_EMAIL=identity["email"],
                       GIT_AUTHOR_DATE=commit["date"], GIT_COMMITTER_DATE=commit["date"])
            if parent is None:
                git(["read-tree", "--empty"], out, env)
            else:
                git(["read-tree", trees[parent]], out, env)
            for rel in commit["files"]:
                blob = git(["hash-object", "-w", "--stdin"], out, env,
                           archive.read(f"fixture/files/{label}/{rel}")).strip()
                git(["update-index", "--add", "--cacheinfo", f"100644,{blob},{rel}"], out, env)
            trees[label] = git(["write-tree"], out, env).strip()
            parents = [] if parent is None else ["-p", shas[parent]]
            shas[label] = git(["commit-tree", trees[label], *parents], out, env,
                              commit["message"].encode("utf-8")).strip()
    for ref, label in fixture["refs"].items():
        git(["update-ref", f"refs/heads/{ref}", shas[label]], out)
    git(["symbolic-ref", "HEAD", "refs/heads/main"], out)
    return shas


# --- realization ---------------------------------------------------------------------------------


def substitute(text: str, path_map: dict, hashes: dict) -> str:
    def replace(match):
        return hashes[match.group(1)] if match.group(1) else path_map[match.group(0)]
    return TOKEN_RE.sub(replace, text)


def realize(name: str, files: dict, raws: dict, path_map: dict) -> dict:
    """Realized bytes for every template of one task: a pure function of templates and path map."""
    realized: dict = {}
    hashes: dict = {}
    for rel in order(name, files, raws):
        spec, raw = files[rel], raws[rel]
        if spec["kind"] == "copy":
            out = raw
        elif spec["kind"] == "brief":
            tail = json_text(parse_json(raws[spec["input"]], rel)).encode("utf-8")
            if not raw.endswith(tail):
                raise Violation(f"tasks/{name}/{rel}: brief does not end with its input's canonical JSON")
            new_tail = json_text(parse_json(realized[spec["input"]], rel)).encode("utf-8")
            out = raw[: len(raw) - len(tail)] + new_tail
        else:
            out = substitute(raw.decode("utf-8"), path_map, hashes).encode("utf-8")
        realized[rel] = out
        hashes[rel] = digest(out)
    return realized


def masked_equal(name: str, rel: str, spec: dict, template: bytes, out: bytes, path_map: dict) -> list[str]:
    """Every undeclared JSON value is unchanged; declared paths are exactly relocated."""
    left, right = parse_json(template, rel), parse_json(out, rel)
    patterns = spec.get("paths", []) + spec.get("carried", []) + spec.get("hashes", [])
    a, b = list(walk(left)), list(walk(right))
    if [pointer for pointer, _ in a] != [pointer for pointer, _ in b]:
        return [f"{name}/{rel}: realized JSON shape differs from its template"]
    problems = []
    for (pointer, before), (_, after) in zip(a, b):
        hash_field = any(matches(p, pointer) for p in spec.get("hashes", []))
        declared = any(matches(p, pointer) for p in patterns)
        if not (declared and isinstance(before, str) and ANY_TOKEN_RE.search(before)):
            if before != after:
                problems.append(f"{name}/{rel}{pointer}: undeclared value changed")
        elif hash_field:
            if not (isinstance(after, str) and re.fullmatch(r"[0-9a-f]{64}", after)):
                problems.append(f"{name}/{rel}{pointer}: declared hash is not a SHA-256")
        elif substitute(before, path_map, {}) != after:
            problems.append(f"{name}/{rel}{pointer}: declared path not relocated by the path map")
    return problems


def fetch_repository(archive: Archive, task: dict, target: Path) -> None:
    repo = task["repository"]
    git(["init", "-q", "--initial-branch=materialize-empty", str(target)])
    bundle = archive.path / archive.manifest["bundle"]["path"]
    git(["fetch", "-q", "--no-tags", str(bundle), *[f"refs/heads/{ref}:refs/heads/{ref}" for ref in repo["refs"]]], target)
    git(["checkout", "-q", repo["checkout"]], target)


def repository_problems(task: dict, target: Path) -> list[str]:
    repo, problems = task["repository"], []
    for ref, sha in repo["refs"].items():
        try:
            actual = git(["rev-parse", "--verify", f"refs/heads/{ref}^{{commit}}"], target).strip()
        except Failure:
            actual = None
        if actual != sha:
            problems.append(f"{task['name']}/repo: branch {ref} is {actual}, not {sha}")
    try:
        head = git(["rev-parse", "HEAD"], target).strip()
        dirty = git(["status", "--porcelain", "--untracked-files=all"], target).strip()
    except Failure as error:
        return problems + [f"{task['name']}/repo: {error}"]
    if head != repo["refs"][repo["checkout"]]:
        problems.append(f"{task['name']}/repo: HEAD is {head}, not {repo['checkout']}")
    if dirty:
        problems.append(f"{task['name']}/repo: working tree is not clean")
    return problems


def tool_digest() -> str:
    return digest(Path(__file__).read_bytes())


def materialize(archive: Archive, root: Path, skill_root: str, names: list[str]) -> dict:
    require_verified(archive)
    safe_root(str(root), "--root")
    safe_root(skill_root, "--skill-root")
    if not (Path(skill_root) / "SKILL.md").is_file():
        raise Failure(f"--skill-root has no SKILL.md: {skill_root}")
    if root.exists():
        raise Failure(f"refusing to overwrite {root}")
    unknown = sorted(set(names) - set(archive.tasks()))
    if unknown:
        raise Failure(f"unknown task: {', '.join(unknown)}")
    root.mkdir(parents=True)
    record = {"format": REALIZATION_FORMAT, "archive_manifest_sha256": digest(archive.manifest_raw),
              "tool_sha256": tool_digest(), "root": str(root), "skill_root": skill_root, "tasks": {}}
    for name in names or archive.tasks():
        task, files, raws = task_templates(archive, name)
        task_root = root / name
        path_map = {"@TASK_ROOT@": str(task_root), "@SKILL_ROOT@": skill_root}
        fetch_repository(archive, task, task_root / "repo")
        realized = realize(name, files, raws, path_map)
        entries = {}
        for rel in sorted(realized):
            destination = task_root / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(realized[rel])
            entries[rel] = {"template_sha256": digest(raws[rel]), "realized_sha256": digest(realized[rel])}
        for directory in task.get("directories", []):
            (task_root / directory).mkdir(parents=True, exist_ok=True)
        record["tasks"][name] = {"path_map": path_map, "refs": task["repository"]["refs"],
                                 "checkout": task["repository"]["checkout"], "files": entries}
    (root / "realization.json").write_text(json_text(record), encoding="utf-8")
    return record


def check(archive: Archive, root: Path, skill_root: Optional[str]) -> list[str]:
    require_verified(archive)
    try:
        record = parse_json((root / "realization.json").read_bytes(), "realization.json")
    except OSError as error:
        raise Failure(f"cannot read {root / 'realization.json'}: {error}") from None
    problems = []
    if record.get("format") != REALIZATION_FORMAT:
        return [f"realization.json: expected format {REALIZATION_FORMAT}"]
    if record.get("archive_manifest_sha256") != digest(archive.manifest_raw):
        problems.append("realization.json: realized from a different archive manifest")
    for name, entry in record.get("tasks", {}).items():
        task, files, raws = task_templates(archive, name)
        path_map = entry["path_map"]
        if path_map != {"@TASK_ROOT@": str(root / name), "@SKILL_ROOT@": record.get("skill_root")}:
            problems.append(f"{name}: path map does not follow the canonical rule")
        realized = realize(name, files, raws, path_map)
        if sorted(entry["files"]) != sorted(realized):
            problems.append(f"{name}: realized file list differs from the archive")
        for rel, expected in realized.items():
            try:
                actual = (root / name / rel).read_bytes()
            except OSError:
                problems.append(f"{name}/{rel}: missing")
                continue
            recorded = entry["files"].get(rel, {})
            if actual != expected:
                problems.append(f"{name}/{rel}: differs from its canonical realization")
            if recorded.get("realized_sha256") != digest(expected) or recorded.get("template_sha256") != digest(raws[rel]):
                problems.append(f"{name}/{rel}: recorded hashes differ")
            if files[rel]["kind"] == "json":
                try:
                    problems.extend(masked_equal(name, rel, files[rel], raws[rel], actual, path_map))
                except Violation as error:
                    problems.append(str(error))
        problems.extend(repository_problems(task, root / name / "repo"))
    if skill_root is not None:
        problems.extend(replay_all(archive, record, skill_root))
    return problems


# --- helper replay -------------------------------------------------------------------------------


def run_helper(command: list[str], cwd: Path, stdin: Optional[bytes] = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(command, cwd=cwd, input=stdin, capture_output=True)
    except OSError as error:
        raise Failure(f"cannot run {' '.join(command)}: {error}") from None


def replay(skill_root: str, task: dict, task_root: Path, realized: dict) -> list[str]:
    """Run each declared helper under the skill and require its realized output byte for byte."""
    problems = []
    scripts = Path(skill_root) / "scripts"
    repo = task_root / "repo"
    for index, step in enumerate(task.get("replay", [])):
        where = f"{task['name']} replay[{index}] {step['run']}"
        with tempfile.TemporaryDirectory(prefix="savings-replay-") as scratch:
            out = Path(scratch) / "out"
            if step["run"] == "review_context":
                command = ["python3", str(scripts / "review_context.py"), "--merge-base", step["merge_base"],
                           "--head", step["head"], "--store", str(out)]
                result, produced = run_helper(command, repo), None
                if result.returncode == 0:
                    produced = {step["store"]: out.read_bytes()}
            elif step["run"] == "context_fingerprint":
                command = ["python3", str(scripts / "context_fingerprint.py"), "--guidance-base", step["guidance_base"],
                           "--store", str(task_root / step["store"])]
                result = run_helper(command, repo, realized[step["input"]])
                produced = None
                if result.returncode == 0 and result.stdout.decode().strip() != step["context"]:
                    problems.append(f"{where}: digest {result.stdout.decode().strip()} is not {step['context']}")
            elif step["run"] == "build_verifier_prompt":
                command = ["python3", str(scripts / "build_verifier_prompt.py"), str(task_root / step["input"]),
                           "--output", str(out)]
                result, produced = run_helper(command, repo), None
                if result.returncode == 0:
                    produced = {f"{step['bundle']}/{leaf}": (out / leaf).read_bytes()
                                for leaf in ("input.json", "brief.md", "manifest.json")}
            elif step["run"] == "account_verifier_return":
                command = ["python3", str(scripts / "account_verifier_return.py"), "--bundle",
                           str(task_root / step["bundle"]), "--output", str(out), str(task_root / step["raw_return"])]
                result, produced = run_helper(command, repo), None
                if result.returncode == 0:
                    produced = {step["accounting"]: out.read_bytes()}
            elif step["run"] == "compose_review":
                command = ["python3", str(scripts / "compose_review.py"), "--profile", step["profile"], "--store",
                           str(task_root / step["store"]), str(task_root / step["composition"])]
                result = run_helper(command, repo)
                produced = {step["record"]: result.stdout} if result.returncode == 0 else None
            else:
                problems.append(f"{where}: unknown replay step")
                continue
            if result.returncode != 0:
                problems.append(f"{where}: exited {result.returncode}: "
                                f"{(result.stdout + result.stderr).decode('utf-8', 'replace').strip()}")
                continue
            for rel, raw in (produced or {}).items():
                if raw != realized.get(rel):
                    problems.append(f"{where}: output differs from realized {rel}")
    return problems


def replay_all(archive: Archive, record: dict, skill_root: str) -> list[str]:
    """Realize every replayed task again in a scratch root and replay its helpers there."""
    safe_root(skill_root, "--skill-root")
    problems = []
    with tempfile.TemporaryDirectory(prefix="savings-check-") as scratch:
        scratch_root = Path(scratch).resolve() / "root"
        safe_root(str(scratch_root), "scratch root")
        for name in record.get("tasks", {}):
            task, files, raws = task_templates(archive, name)
            if not task.get("replay"):
                continue
            task_root = scratch_root / name
            path_map = {"@TASK_ROOT@": str(task_root), "@SKILL_ROOT@": skill_root}
            fetch_repository(archive, task, task_root / "repo")
            realized = realize(name, files, raws, path_map)
            for rel, raw in realized.items():
                (task_root / rel).parent.mkdir(parents=True, exist_ok=True)
                (task_root / rel).write_bytes(raw)
            problems.extend(replay(skill_root, task, task_root, realized))
    return problems


# --- seal ----------------------------------------------------------------------------------------


def seal(archive: Archive) -> dict:
    manifest = archive.manifest
    for key in ("baseline", "tasks", "bundle"):
        if key not in manifest:
            raise Failure(f"{MANIFEST}: seal needs a hand-written {key}")
    files = {}
    for path in sorted(archive.path.rglob("*")):
        rel = path.relative_to(archive.path).as_posix()
        if path.is_file() and rel != MANIFEST:
            raw = path.read_bytes()
            files[rel] = {"bytes": len(raw), "sha256": digest(raw)}
    manifest["files"] = files
    archive.manifest = manifest
    bundle = archive.path / manifest["bundle"]["path"]
    with tempfile.TemporaryDirectory(prefix="savings-seal-") as scratch:
        manifest["revisions"] = build_fixture(archive, Path(scratch) / "repo")
        if not bundle.exists():
            git(["bundle", "create", "-q", str(bundle), "--branches"], Path(scratch) / "repo")
            raw = bundle.read_bytes()
            files[manifest["bundle"]["path"]] = {"bytes": len(raw), "sha256": digest(raw)}
    manifest["bundle"]["heads"] = bundle_heads(bundle)
    (archive.path / MANIFEST).write_text(json_text(manifest), encoding="utf-8")
    return manifest


# --- command line --------------------------------------------------------------------------------


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify").add_argument("archive")
    fixture = commands.add_parser("fixture")
    fixture.add_argument("archive")
    fixture.add_argument("--out", required=True)
    fixture.add_argument("--bundle")
    materialize_parser = commands.add_parser("materialize")
    materialize_parser.add_argument("archive")
    materialize_parser.add_argument("--root", required=True)
    materialize_parser.add_argument("--skill-root", required=True)
    materialize_parser.add_argument("--task", action="append", default=[])
    check_parser = commands.add_parser("check")
    check_parser.add_argument("archive")
    check_parser.add_argument("--root", required=True)
    check_parser.add_argument("--skill-root")
    commands.add_parser("seal").add_argument("archive")
    args = parser.parse_args(argv)
    try:
        archive = Archive(args.archive)
        if args.command == "verify":
            problems = verify(archive)
        elif args.command == "fixture":
            out = Path(args.out).resolve()
            shas = build_fixture(archive, out)
            expected = archive.manifest.get("revisions")
            problems = [f"fixture {label}: rebuilt {sha}, manifest {expected.get(label)}"
                        for label, sha in shas.items() if expected and expected.get(label) != sha]
            if args.bundle:
                git(["bundle", "create", "-q", str(Path(args.bundle).resolve()), "--branches"], out)
            for label, sha in shas.items():
                print(f"{label} {sha}")
        elif args.command == "materialize":
            record = materialize(archive, Path(args.root), args.skill_root, args.task)
            for name in record["tasks"]:
                print(Path(args.root) / name)
            problems = []
        elif args.command == "check":
            problems = check(archive, Path(args.root), args.skill_root)
            if not problems:
                print(f"realization at {args.root} matches the archive")
        else:
            seal(archive)
            problems = []
    except Violation as error:
        print(error)
        return 1
    except Failure as error:
        print(f"savings_archive: {error}", file=sys.stderr)
        return 2
    for problem in problems:
        print(problem)
    if args.command == "verify" and not problems:
        print(f"archive verified: {len(archive.manifest['files'])} files, manifest sha256 {digest(archive.manifest_raw)}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
