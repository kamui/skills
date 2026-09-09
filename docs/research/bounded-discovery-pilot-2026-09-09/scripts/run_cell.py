#!/usr/bin/env python3
"""Prepare, dispatch and settle one cell of the #138 bounded-discovery grid.

#149 froze the experiment and #147's adapter deliberately returns an immutable
no-cell stop on its Claude entry point, so the coordinator executes the frozen
dispatch template itself, exactly as the preregistration's section 12 lists the
steps. This script is that coordinator. It never decides anything the freeze
decided: every prompt is extracted verbatim from ``dispatch-template.md`` and
every value comes from the sealed schedule row, the slot manifest or the ledger.

Three stages, each restartable and each writing its own record:

``prepare``
    Build the cell's environment from the pinned inputs - a private mirror copy,
    a clone made by the frozen recipe, the policy snapshot extracted by
    ``git archive``, the packet and scope checked against their frozen digests,
    the rendered prompts with an assertion that no placeholder is left - then run
    ``check_cell_isolation.py --phase preparation`` while the evaluator material
    is still present, producing the attestation the dispatch window consumes.

``dispatch``
    Start the egress proxy, reserve the attempt's allowance on the ledger, run
    the pre-dispatch isolation check inside the cell's container, then launch the
    primary (and in arm C the finder, the barrier and the resume) under the
    frozen ceilings, retaining every result envelope and transcript.

``settle``
    Meter the attempt per model with ``meter_split.py``,
    verify model and effort on every assistant line with ``agent_effort.py``,
    audit the transcripts for out-of-sandbox reads and unlogged network use,
    settle the ledger and archive the artifacts.

Isolation deviation (2026-09-09, recorded in the bundle's deviations): the frozen
control is absence of the forbidden material from the machine. This machine
cannot reach that state - 188 worktrees and the primary checkout of this
repository cannot be removed here - so each cell runs in a container that mounts
only its permitted roots, and the absence check runs inside that container
against the host paths. The mount set is asserted from ``docker inspect`` and
recorded, because under this deviation the mount set is the evidence.

Usage::

    python3 run_cell.py prepare --config pilot-config.json --position 1
    python3 run_cell.py dispatch --config pilot-config.json --position 1
    python3 run_cell.py settle  --config pilot-config.json --position 1
    python3 run_cell.py --self-test

Config schema (UTF-8 JSON): ``repo``, ``bundle``, ``targets``, ``tools``,
``ledger``, ``schedule``, ``leak_sets``, ``cells_root``, ``image``,
``auth_env_file``, ``proxy_port``, ``policy_tree``, ``policy_commit``.

Exit: 0 on success, 1 on a content or protocol violation with one line per
violation on stdout, 2 when an input cannot be read or a subprocess fails,
naming the failing command on stderr.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Per-slot toolchain caches. The packets hardcode these paths, so the container
# mounts each cell's private copy at the identical path and the frozen execution
# note stays literally true inside it.
CELL_HOME = "/cell-home"

CACHES = {"slot-1": ["/tmp/bd148/cargo-home"],
          "slot-2": ["/tmp/bd148/gomodcache", "/tmp/bd148/gocache-grpc-go-7417"]}


class Failed(Exception):
    """An input could not be read or a subprocess failed: exit 2."""


def run(*command, cwd=None, check=True, capture=True):
    result = subprocess.run([str(part) for part in command], cwd=cwd, text=True,
                            encoding="utf-8", capture_output=capture)
    if check and result.returncode:
        raise Failed("%s: %s" % (" ".join(str(p) for p in command),
                                 (result.stderr or result.stdout or "").strip()))
    return result


def copy_tree(source, destination):
    """Copy a directory, preferring an APFS clone, and leave it writable.

    Each cell gets its own copy of the mirror and the toolchain caches so that no
    two cells share mutable state. ``cp -Rc`` asks APFS for copy-on-write clones,
    which costs no space and no time until something is written; it falls back to
    a plain recursive copy on a filesystem that cannot clone. Go makes every file
    in its module cache read-only, so the copy is made writable afterwards -
    otherwise ``go`` cannot take its own lock and the copy cannot be removed.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    cloned = run("cp", "-Rc", str(source), str(destination), check=False)
    if cloned.returncode:
        run("cp", "-R", str(source), str(destination))
    run("chmod", "-R", "u+w", str(destination))


def digest(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, default=None):
    try:
        return json.loads(Path(os.path.expanduser(str(path))).read_text(encoding="utf-8"))
    except FileNotFoundError:
        if default is not None:
            return default
        raise Failed("missing %s" % path)
    except (OSError, ValueError) as exc:
        raise Failed("cannot read %s: %s" % (path, exc))


def write(path, document):
    Path(path).write_text(json.dumps(document, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")


def fenced(text: str, heading: str) -> str:
    """The first fenced block after a heading, with the fence itself removed.

    The prompts are extracted from the frozen template rather than copied into
    this script, so a rendered prompt cannot drift from the byte the freeze
    pinned. The template hashes into every cell record alongside the rendering.
    """
    start = text.find(heading)
    if start < 0:
        raise Failed("dispatch template has no heading %r" % heading)
    rest = text[start + len(heading):]
    opened = None
    lines = []
    for line in rest.splitlines():
        stripped = line.rstrip()
        if opened is None:
            if stripped.startswith("```"):
                opened = stripped[:len(stripped) - len(stripped.lstrip("`"))]
            continue
        if stripped.startswith(opened) and not stripped[len(opened):].strip():
            return "\n".join(lines) + "\n"
        lines.append(line)
    raise Failed("dispatch template block after %r is not closed" % heading)


def render(template: str, values: dict) -> str:
    text = template
    for key, value in values.items():
        text = text.replace("{%s}" % key, str(value))
    return text


def unfilled(text: str) -> list:
    """Every remaining {PLACEHOLDER}; a dispatch precondition is that there are none."""
    import re
    return sorted(set(re.findall(r"\{[A-Z][A-Z0-9_]*\}", text)))


HEADINGS = {
    "agents_a": "Arm A (`agents-A.json`):",
    "agents_bc": "Arms B and C (`agents-BC.json`) — byte-identical to A except the model:",
    "primary": "## Primary dispatch prompt",
    "barrier": "### `{ARM_C_BARRIER_BLOCK}` — empty in arms A and B, this text in arm C",
    "admission": "### `{ADMISSION}` — the resume prompt for arm C's phase 2",
    "finder": "## Finder prompt (arm C only)",
}

WORKER_MODEL = {"A": "claude-sonnet-5", "B": "claude-opus-5", "C": "claude-opus-5"}


def session_id(attempt_id, role="primary") -> str:
    """A stable UUID per attempt and role.

    ``claude`` refuses a ``--session-id`` that is not a UUID, so the attempt ID
    cannot be used directly. Deriving it with uuid5 keeps the mapping
    deterministic - the same attempt always names the same session, which is what
    arm C's ``--resume`` and the transcript audit both need - while staying a
    valid UUID.
    """
    import uuid
    return str(uuid.uuid5(uuid.NAMESPACE_URL,
                          "bounded-discovery/%s/%s" % (attempt_id, role)))


def paths_for(root) -> dict:
    """Every path the rendered prompts name, all inside the cell's own tree."""
    return {"CLONE": str(root / "clone"), "SKILL_DIR": str(root / "snapshot"),
            "PACKET_DIR": str(root / "packet"), "PACKET": str(root / "packet" / "packet.md"),
            "WORK": str(root / "work"), "RUNNER": str(root / "runner"),
            "PAYLOAD": str(root / "work" / "review-payload.md"),
            "REPORT": str(root / "work" / "research-report.md"),
            "TIMING": str(root / "work" / "timing.json"),
            "FREEZE": str(root / "work" / "freeze.json"),
            "FINDER_STORE": str(root / "finder-store"),
            "SCOPE": str(root / "finder-store" / "scope.json")}


def render_prompts(config, root, row, manifest) -> list:
    """Render this cell's prompts and worker definitions from the frozen template.

    Every byte that is not a placeholder comes from ``dispatch-template.md``, and
    a rendering that still contains a placeholder is refused: the template makes
    "no unfilled placeholder" a dispatch precondition.
    """
    template_path = Path(config["bundle"]) / "dispatch-template.md"
    template = template_path.read_text(encoding="utf-8")
    arm = row["arm"]
    target = manifest["target"]
    values = dict(paths_for(root))
    values.update({
        "TARGET_SLOT": row["target_slot"],
        "REPO_PR": "%s#%s" % (target["repository"], target["pr"]),
        "CELL": row["cell_id"], "ATTEMPT": row["attempt_id"],
        "WORKER_MODEL": WORKER_MODEL[arm],
        "BASE_BRANCH": target["base_ref"],
        "EXEC_NOTE": manifest["execution"]["note"],
    })
    # The barrier block is itself a template - it names {FREEZE} - so it is
    # rendered before being substituted into the dispatch prompt. One pass over an
    # already-substituted value would leave that placeholder behind.
    barrier = fenced(template, HEADINGS["barrier"]) if arm == "C" else ""
    values["ARM_C_BARRIER_BLOCK"] = render(barrier, values)
    problems = []
    written = {}
    prompts = {"dispatch.md": fenced(template, HEADINGS["primary"]),
               "agents.json": fenced(template, HEADINGS["agents_a"] if arm == "A"
                                     else HEADINGS["agents_bc"])}
    if arm == "C":
        prompts["finder-prompt.md"] = fenced(template, HEADINGS["finder"])
        prompts["admission.md"] = fenced(template, HEADINGS["admission"])
    for name, text in prompts.items():
        rendered = render(text, values)
        # The admission prompt keeps {FINDER_CLAIMS} until the finder has run.
        remaining = [p for p in unfilled(rendered) if p != "{FINDER_CLAIMS}"]
        if remaining:
            problems.append("%s still contains %s" % (name, ", ".join(remaining)))
        destination = root / "runner" / name
        destination.write_text(rendered, encoding="utf-8")
        written[name] = digest(destination)
    write(root / "artifacts" / "prompts.json",
          {"dispatch_template": str(template_path),
           "dispatch_template_sha256": digest(template_path),
           "rendered_sha256": written, "worker_model": WORKER_MODEL[arm]})
    return problems


def checkouts(config) -> list:
    """Every checkout of this repository, which the frozen absence gate forbids.

    A linked worktree shares the primary checkout's object store, so it reaches
    ``targets/README.md`` and the whole sealed bundle at any commit whatever its
    own tree holds. They are all forbidden, and listing them by path is what lets
    the in-container check establish that none of them is reachable.
    """
    result = run("git", "-C", config["repo"], "worktree", "list", "--porcelain")
    paths = [line.split(" ", 1)[1].strip()
             for line in result.stdout.splitlines() if line.startswith("worktree ")]
    common = run("git", "-C", config["repo"], "rev-parse", "--path-format=absolute",
                 "--git-common-dir").stdout.strip()
    primary = str(Path(common).parent)
    if primary not in paths:
        paths.append(primary)
    return sorted(set(paths))


def forbidden_paths(config, position, slot, manifest) -> list:
    """The frozen forbidden set for this cell, as concrete paths."""
    paths = [os.path.expanduser("~/.config/bounded-discovery")]
    paths.extend(checkouts(config))
    mirrors = Path(os.path.expanduser(manifest["mirror"]["path"])).parent
    own = Path(os.path.expanduser(manifest["mirror"]["path"])).name
    if mirrors.is_dir():
        paths.extend(str(mirrors / entry.name) for entry in mirrors.iterdir()
                     if entry.name != own)
    staging = mirrors.parent
    paths.extend(str(staging / name) for name in ("staging", "clones", "adjudication",
                                                  "selector", "sessions", "hunt",
                                                  "ledger.live.json"))
    cells = Path(os.path.expanduser(config["cells_root"]))
    if cells.is_dir():
        paths.extend(str(entry) for entry in cells.iterdir()
                     if entry.name != ("position-%02d" % int(position)))
    return sorted(set(paths))


def specs(config, position, slot, manifest, root, cell_id) -> tuple:
    """The preparation spec (host) and the dispatch spec (inside the container).

    Both name the same clone, because the cell tree is mounted at its identical
    absolute path; they differ in the proxy address, which the container reaches
    through ``host.docker.internal``, and in whether a leak set is named at all.
    """
    target = manifest["target"]
    clone = {"path": str(root / "clone"), "head_oid": target["head_oid"],
             "base_branch": target["base_ref"],
             "merge_base_oid": target["merge_base_oid"]}
    permitted = [str(root / name) for name in ("clone", "work", "snapshot", "packet",
                                               "finder-store", "artifacts", "runner")]
    permitted.append(str(root / "mirror.git"))
    permitted.extend(CACHES.get(slot, []))
    leak_set = Path(os.path.expanduser(config["leak_sets"])) / (manifest["label"] + ".json")
    preparation = {"cell_id": cell_id, "target_slot": slot, "clone": clone,
                   "permitted_roots": permitted, "forbidden_paths": [],
                   "leak_set": str(leak_set),
                   "egress_proxy": {"host": "127.0.0.1", "port": int(config["proxy_port"]),
                                    "probe_host": "api.github.com"}}
    dispatch_spec = dict(preparation)
    dispatch_spec["forbidden_paths"] = forbidden_paths(config, position, slot, manifest)
    dispatch_spec.pop("leak_set")
    dispatch_spec["egress_proxy"] = {"host": "host.docker.internal",
                                     "port": int(config["proxy_port"]),
                                     "probe_host": "api.github.com"}
    return preparation, dispatch_spec


def schedule_row(config, position):
    schedule = load(config["schedule"])
    for row in schedule["ordered_cells"]:
        if int(row["position"]) == int(position):
            return row
    raise Failed("no cell at position %s in the sealed schedule" % position)


def cell_root(config, position):
    return Path(os.path.expanduser(config["cells_root"])) / ("position-%02d" % int(position))


def prepare(config, position, force=False):
    row = schedule_row(config, position)
    slot = row["target_slot"]
    arm = row["arm"]
    manifest = load(Path(config["targets"]) / slot / "manifest.json")
    root = cell_root(config, position)
    if root.exists():
        if not force:
            print("%s already exists; pass --force to rebuild it" % root)
            return 1
        shutil.rmtree(root)
    problems = []

    for name in ("clone", "work", "snapshot", "packet", "finder-store",
                 "claude-home", "logs", "artifacts", "runner"):
        (root / name).mkdir(parents=True)

    # A private mirror copy, so no other slot's mirror has to be present.
    mirror = root / "mirror.git"
    copy_tree(os.path.expanduser(manifest["mirror"]["path"]), mirror)
    target = manifest["target"]
    base_branch = target["base_ref"]
    clone = root / "clone"
    shutil.rmtree(clone)
    run("git", "clone", "--quiet", str(mirror), str(clone))
    run("git", "-C", str(clone), "remote", "set-url", "origin", str(mirror))
    run("git", "-C", str(clone), "checkout", "--quiet", "--detach", target["head_oid"])
    run("git", "-C", str(clone), "branch", "-f", base_branch, target["merge_base_oid"])
    run("git", "-C", str(clone), "checkout", "--quiet", "-B", "review-head", target["head_oid"])

    observed = run("git", "-C", str(clone), "rev-parse", "HEAD").stdout.strip()
    if observed != target["head_oid"]:
        problems.append("clone head is %s, expected %s" % (observed, target["head_oid"]))
    observed_base = run("git", "-C", str(clone), "rev-parse", base_branch).stdout.strip()
    if observed_base != target["merge_base_oid"]:
        problems.append("clone %s is %s, expected the merge-base %s"
                        % (base_branch, observed_base, target["merge_base_oid"]))
    if run("git", "-C", str(clone), "status", "--short").stdout.strip():
        problems.append("the fresh clone's tracked tree is not clean")

    # The policy under test, extracted from the pinned tree. Cells never read a checkout.
    snapshot = root / "snapshot"
    tar = root / "logs" / "snapshot.tar"
    run("git", "-C", config["repo"], "archive", "--output", str(tar), config["policy_tree"])
    run("tar", "-xf", str(tar), "-C", str(snapshot))
    tar.unlink()
    if not (snapshot / "SKILL.md").is_file():
        problems.append("the policy snapshot has no SKILL.md")

    # Packet and scope, checked against the digests #148 froze and #149 bound.
    packet_source = Path(config["targets"]) / slot / manifest["packet"]["path"]
    packet = root / "packet" / "packet.md"
    shutil.copyfile(packet_source, packet)
    packet_sha = digest(packet)
    if packet_sha != manifest["packet"]["sha256"]:
        problems.append("packet digest %s does not match the frozen %s"
                        % (packet_sha, manifest["packet"]["sha256"]))
    scope_source = Path(config["targets"]) / slot / manifest["scope"]["path"]
    scope_sha = digest(scope_source)
    if scope_sha != manifest["scope"]["sha256"]:
        problems.append("scope digest %s does not match the frozen %s"
                        % (scope_sha, manifest["scope"]["sha256"]))
    scope = load(scope_source)
    if scope.get("source_hash") != packet_sha:
        problems.append("scope source_hash %s is not the packet digest %s"
                        % (scope.get("source_hash"), packet_sha))
    if arm == "C":
        shutil.copyfile(packet_source, root / "finder-store" / "packet.md")
        shutil.copyfile(scope_source, root / "finder-store" / "scope.json")

    # Each cell gets its own copy of the caches, at the path the packet names.
    for cache in CACHES.get(slot, []):
        destination = root / "caches" / cache.lstrip("/")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not Path(cache).is_dir():
            problems.append("toolchain cache %s is missing" % cache)
            continue
        copy_tree(cache, destination)

    shutil.copyfile(Path(__file__).resolve().parent / "mark_event.py",
                    root / "runner" / "mark_event.py")
    problems.extend(render_prompts(config, root, row, manifest))
    isolation = Path(config["bundle"]) / "scripts" / "check_cell_isolation.py"
    shutil.copyfile(isolation, root / "runner" / "check_cell_isolation.py")

    # The attestation has to be taken while the evaluator material is still
    # present, because the leak-set check reads the very storage the absence gate
    # requires to be gone. It carries no SHA from the set into the dispatch window.
    preparation, dispatch_spec = specs(config, position, slot, manifest, root,
                                       row["cell_id"])
    write(root / "artifacts" / "cell-env-preparation.json", preparation)
    write(root / "artifacts" / "cell-env-dispatch.json", dispatch_spec)
    attestation = root / "artifacts" / "attestation.json"
    attested = run(sys.executable, str(isolation), "--spec",
                   str(root / "artifacts" / "cell-env-preparation.json"),
                   "--phase", "preparation", "--out", str(attestation), check=False)
    if attested.returncode:
        problems.append("preparation attestation failed: %s"
                        % (attested.stdout or attested.stderr).strip())

    record = {"schema_version": "bounded-discovery-v1", "position": int(position),
              "cell_id": row["cell_id"], "attempt_id": row["attempt_id"],
              "target_slot": slot, "arm": arm, "replicate": row["replicate"],
              "block": row["block"], "clone_head": observed,
              "clone_base_branch": base_branch, "clone_base_oid": observed_base,
              "packet_sha256": packet_sha, "scope_sha256": scope_sha,
              "policy_commit": config["policy_commit"],
              "policy_tree": config["policy_tree"],
              "caches": CACHES.get(slot, []), "problems": problems}
    write(root / "artifacts" / "prepare.json", record)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


ATTEMPT_CEILING = "9.00"
CALL_HEADROOM = "1.00"
FINDER_CEILING = "2.00"
ROOT_WALL_SECONDS = 5400
FINDER_WALL_SECONDS = 1800

ALLOWED_TOOLS = ["Write", "Edit", "Bash(git:*)", "Bash(go:*)", "Bash(cargo:*)",
                 "Bash(python3:*)", "Bash(cat:*)", "Bash(ls:*)", "Bash(head:*)",
                 "Bash(tail:*)", "Bash(wc:*)", "Bash(sed:*)", "Bash(grep:*)"]


def proxy_start(config, root):
    """Start the cell's allow-list egress proxy and wait until it is listening.

    It binds every interface rather than loopback only, because the cell reaches it
    from inside a container; that is a consequence of the isolation deviation and is
    recorded with it. The allow list stays exactly the frozen ``.anthropic.com``.
    """
    log = root / "artifacts" / "egress.jsonl"
    output = open(root / "logs" / "proxy.log", "w", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, str(Path(config["bundle"]) / "scripts" / "egress_proxy.py"),
         "--host", "0.0.0.0", "--port", str(config["proxy_port"]),
         "--log", str(log), "--allow", ".anthropic.com"],
        stdout=output, stderr=subprocess.STDOUT)
    for _ in range(100):
        text = Path(root / "logs" / "proxy.log").read_text(encoding="utf-8")
        if "listening" in text:
            return process, log
        if process.poll() is not None:
            raise Failed("egress proxy exited: %s" % text.strip())
        __import__("time").sleep(0.1)
    process.terminate()
    raise Failed("egress proxy did not report listening")


def mounts_for(config, root, slot) -> list:
    """Only the cell's own tree and its private caches, at their host paths.

    Mounting at the identical absolute path is what keeps the frozen packet's
    hardcoded cache paths and the rendered prompts literally true inside the
    container, and it is why no path translation is needed anywhere else.
    """
    arguments = ["-v", "%s:%s" % (root, root)]
    for cache in CACHES.get(slot, []):
        arguments += ["-v", "%s:%s" % (root / "caches" / cache.lstrip("/"), cache)]
    # The whole home is mounted, not just .claude: claude keeps .claude.json
    # beside it and refuses to start cleanly when that file cannot persist.
    home = root.parent / "homes" / root.name
    home.mkdir(parents=True, exist_ok=True)
    arguments += ["-v", "%s:%s" % (home, CELL_HOME)]
    return arguments


def docker_argv(config, root, slot, name, argv, workdir) -> list:
    url = "http://host.docker.internal:%s" % config["proxy_port"]
    return ["docker", "run", "--rm", "--name", name,
            "--env-file", os.path.expanduser(config["auth_env_file"]),
            "-e", "HOME=%s" % CELL_HOME,
            # rustup's proxies resolve the toolchain under RUSTUP_HOME, which
            # defaults to $HOME; the toolchain lives in the image's own root.
            "-e", "RUSTUP_HOME=/root/.rustup",
            "-e", "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0",
            "-e", "HTTPS_PROXY=%s" % url, "-e", "HTTP_PROXY=%s" % url,
            "-e", "ALL_PROXY=%s" % url,
            *mounts_for(config, root, slot), "-w", str(workdir),
            config["image"], *argv]


def primary_argv(root, wall, sid, allowance, prompt, agents, resume=False) -> list:
    """The frozen primary launch, with the template's flags in the template's order."""
    paths = paths_for(root)
    return ["timeout", str(int(wall)), "claude", "-p",
            *(["--resume", sid] if resume else ["--session-id", sid]),
            "--model", "claude-sonnet-5", "--effort", "high", "--restricted",
            "--tools", "Bash,Read,Write,Edit,Glob,Grep,Agent,Task",
            "--allowedTools", *ALLOWED_TOOLS,
            "--add-dir", paths["CLONE"], "--add-dir", paths["SKILL_DIR"],
            "--add-dir", paths["PACKET_DIR"],
            "--permission-prompts", "none", "--agents", agents,
            "--max-budget-usd", str(allowance), "--output-format", "json", prompt]


def finder_argv(root, sid, prompt) -> list:
    paths = paths_for(root)
    return ["timeout", str(FINDER_WALL_SECONDS), "claude", "-p", "--session-id", sid,
            "--model", "claude-opus-5", "--effort", "high", "--restricted",
            "--tools", "Read,Grep,Glob",
            "--add-dir", paths["CLONE"], "--add-dir", paths["FINDER_STORE"],
            "--permission-prompts", "none", "--max-budget-usd", FINDER_CEILING,
            "--output-format", "json", prompt]


def envelope(text):
    """The result envelope from a ``--output-format json`` session, or None."""
    for line in reversed(text.strip().splitlines()):
        try:
            document = json.loads(line)
        except ValueError:
            continue
        if isinstance(document, dict) and document.get("type") == "result":
            return document
    return None


def finder_claims(result: str) -> tuple:
    """The finder's single fenced JSON block, checked key by key.

    The finder has no write tool on purpose, so the coordinator persists its output.
    A missing, unparsable or incomplete block is a malformed finder, which the
    design's transition table treats as an operational failure - never as an empty
    discovery pass and never as arm B's shape.
    """
    required = ("context_id", "packet_sha256", "scope_id", "claims", "inspected",
                "frontier_expansions", "unavailable")
    fields = ("id", "kind", "claim", "trigger", "impact", "citations")
    if not result:
        return None, ["the finder produced no result to parse"]
    start = result.find("```json")
    if start < 0:
        return None, ["the finder's result has no fenced json block"]
    end = result.find("```", start + len("```json"))
    if end < 0:
        return None, ["the finder's fenced json block is not closed"]
    try:
        document = json.loads(result[start + len("```json"):end])
    except ValueError as exc:
        return None, ["the finder's fenced json block does not parse: %s" % exc]
    problems = ["the finder's block has no %s" % key
                for key in required if key not in document]
    if not isinstance(document.get("claims"), list):
        problems.append("the finder's claims is not a list")
    else:
        for claim in document["claims"]:
            problems.extend("a finder claim has no %s" % field
                            for field in fields if field not in claim)
    return (document, problems) if not problems else (None, problems)


def attempt_exposure() -> str:
    """The most one attempt can cost: the review ceiling plus one call of overshoot.

    ``--max-budget-usd`` holds the frozen $9.00 whole-review ceiling, but probe 4
    showed the allowance is only checked after a call completes, so a session can
    finish slightly above it. The preregistration adds $1.00 of one-call headroom to
    every reservation for exactly that, and the ledger requires a reservation to fit
    inside the attempt cap - so the cap is the ceiling plus the headroom, not the
    ceiling alone. The ceiling itself is unchanged.
    """
    return "%.2f" % (float(ATTEMPT_CEILING) + float(CALL_HEADROOM))


def reserve(config, row, amount, evidence):
    budget = Path(config["targets"]).parent / "scripts" / "budget.py"
    return run(sys.executable, str(budget), config["ledger"], "reserve",
               "--id", "%s-reservation" % row["attempt_id"], "--amount", str(amount),
               "--phase", "review", "--attempt", row["attempt_id"],
               "--attempt-cap", attempt_exposure(), "--ticket", "150",
               "--evidence", evidence, check=False)


def isolation_phase(config, root, slot, phase, out):
    """Run the absence gate inside the cell's own container.

    Under the isolation deviation this is where the check belongs: the property
    being established is that the forbidden material is not reachable from the
    cell, and the cell's filesystem is the container's. The spec still names the
    host paths, so a mount that accidentally exposed one would fail here.
    """
    argv = ["python3", str(root / "runner" / "check_cell_isolation.py"),
            "--spec", str(root / "artifacts" / "cell-env-dispatch.json"),
            "--phase", phase,
            "--attestation", str(root / "artifacts" / "attestation.json"),
            "--out", str(out)]
    name = "bd150-%s-%s" % (root.name, phase)
    return run(*docker_argv(config, root, slot, name, argv, root / "work"), check=False)


def record_mounts(config, root, slot, destination):
    """The asserted mount set, which under the deviation is the isolation evidence."""
    argv = docker_argv(config, root, slot, "bd150-%s-mounts" % root.name,
                       ["sh", "-c", "ls -1 / && echo --- && cat /proc/mounts"],
                       root / "work")
    observed = run(*argv, check=False)
    requested = [argv[index + 1] for index, part in enumerate(argv) if part == "-v"]
    write(destination, {"requested_mounts": requested,
                        "container_root_listing": observed.stdout,
                        "exit_code": observed.returncode})
    return requested


def attempt_id_for(row, attempt) -> str:
    base = row["attempt_id"].rsplit("-attempt-", 1)[0]
    return "%s-attempt-%d" % (base, int(attempt))


def dispatch(config, position, attempt=1):
    import time

    row = dict(schedule_row(config, position))
    row["attempt_id"] = attempt_id_for(row, attempt)
    root = cell_root(config, position)
    slot, arm = row["target_slot"], row["arm"]
    manifest = load(Path(config["targets"]) / slot / "manifest.json")
    prepared = load(root / "artifacts" / "prepare.json")
    problems = []
    if prepared["problems"]:
        print("the cell's prepare stage reported problems; rerun prepare")
        return 1
    if not load(root / "artifacts" / "attestation.json").get("ready"):
        print("the preparation attestation is not ready")
        return 1
    auth = Path(os.path.expanduser(config["auth_env_file"]))
    if not auth.is_file() or not auth.stat().st_size:
        print("no container credential at %s" % auth)
        return 1

    # Regenerate the forbidden set so the record describes the machine as it is now.
    _, dispatch_spec = specs(config, position, slot, manifest, root, row["cell_id"])
    write(root / "artifacts" / "cell-env-dispatch.json", dispatch_spec)

    proxy, egress_log = proxy_start(config, root)
    started = time.time()
    result = {"schema_version": "bounded-discovery-v1", "position": int(position),
              "cell_id": row["cell_id"], "attempt_id": row["attempt_id"], "arm": arm,
              "target_slot": slot, "phases": [], "problems": problems}
    try:
        record_mounts(config, root, slot, root / "artifacts" / "mounts.json")
        pre = isolation_phase(config, root, slot, "pre-dispatch",
                              root / "artifacts" / "isolation-pre.json")
        if pre.returncode:
            problems.append("pre-dispatch isolation failed: %s"
                            % (pre.stdout or pre.stderr).strip())
            result["disposition"] = "stopped-isolation"
            return finish(root, result, problems)

        reservation = reserve(config, row, attempt_exposure(),
                              "cell %s attempt %s: container dispatch under the frozen "
                              "ceilings, reserved before launch"
                              % (row["cell_id"], row["attempt_id"]))
        if reservation.returncode:
            problems.append("ledger reservation refused: %s"
                            % (reservation.stdout or reservation.stderr).strip())
            result["disposition"] = "stopped-budget"
            return finish(root, result, problems)
        result["reservation"] = (reservation.stdout or "").strip()

        timing = Path(paths_for(root)["TIMING"])
        created = run(sys.executable, str(root / "runner" / "mark_event.py"),
                      str(timing), "root_dispatched_at", "--create", check=False)
        if created.returncode:
            problems.append("could not create the timing sidecar: %s" % created.stdout.strip())
            result["disposition"] = "stopped-runtime"
            return finish(root, result, problems)
        dispatched = time.time()

        agents = (root / "runner" / "agents.json").read_text(encoding="utf-8")
        prompt = (root / "runner" / "dispatch.md").read_text(encoding="utf-8")
        finder = None
        if arm == "C":
            finder_prompt = (root / "runner" / "finder-prompt.md").read_text(encoding="utf-8")
            finder = subprocess.Popen(
                docker_argv(config, root, slot, "bd150-%s-finder" % root.name,
                            finder_argv(root, session_id(row["attempt_id"], "finder"),
                                        finder_prompt),
                            root / "finder-store"),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                encoding="utf-8")

        phase1 = run_phase(config, root, slot, row, "primary-phase-1",
                           primary_argv(root, ROOT_WALL_SECONDS,
                                        session_id(row["attempt_id"]), ATTEMPT_CEILING,
                                        prompt, agents))
        result["phases"].append(phase1)
        if not phase1["envelope"]:
            # No result envelope means the session never reported: a launch refusal
            # or a cancellation. Either way it is not a measured attempt, and
            # calling it dispatched would hide a runtime failure.
            problems.append("primary phase 1 produced no result envelope (exit %s): %s"
                            % (phase1["exit_code"], phase1["stderr_tail"]))
            result["disposition"] = "stopped-runtime"
            return finish(root, result, problems)

        if arm == "C":
            spent = phase1["cost_usd"] or 0.0
            freeze = Path(paths_for(root)["FREEZE"])
            if not freeze.is_file():
                problems.append("arm C phase 1 ended without writing its freeze artifact")
            finder_output = ""
            try:
                finder_output = finder.communicate(
                    timeout=max(60, FINDER_WALL_SECONDS - (time.time() - dispatched)))[0]
            except subprocess.TimeoutExpired:
                run("docker", "kill", "bd150-%s-finder" % root.name, check=False)
                finder_output = finder.communicate()[0] or ""
            (root / "logs" / "finder.log").write_text(finder_output, encoding="utf-8")
            finder_envelope = envelope(finder_output)
            claims, finder_problems = finder_claims(
                (finder_envelope or {}).get("result", ""))
            finder_cost = float((finder_envelope or {}).get("total_cost_usd") or 0.0)
            result["finder"] = {"cost_usd": finder_cost, "problems": finder_problems,
                                "envelope_subtype": (finder_envelope or {}).get("subtype")}
            if finder_problems or claims is None:
                problems.extend(finder_problems)
                problems.append("missing or malformed finder: the attempt closes as an "
                                "operational failure rather than an empty discovery pass")
                result["disposition"] = "stopped-finder"
                return finish(root, result, problems)
            discovery = root / "finder-store" / "discovery.json"
            write(discovery, claims)
            result["finder"]["discovery_sha256"] = digest(discovery)

            if not problems:
                admission = render(
                    (root / "runner" / "admission.md").read_text(encoding="utf-8"),
                    {"FINDER_CLAIMS": json.dumps(claims["claims"], indent=2, sort_keys=True)})
                left = unfilled(admission)
                if left:
                    problems.append("the admission prompt still contains %s" % ", ".join(left))
                (root / "runner" / "admission.rendered.md").write_text(admission,
                                                                      encoding="utf-8")
                # The whole attempt gets 5400 s counted once, and the finder's spend
                # is charged inside C's ceiling rather than in addition to it.
                remaining_wall = ROOT_WALL_SECONDS - (time.time() - dispatched)
                remaining_usd = float(ATTEMPT_CEILING) - spent - finder_cost
                if remaining_wall < 60 or remaining_usd <= 0:
                    problems.append("arm C had no allowance left to resume: %.0f s and $%.4f"
                                    % (remaining_wall, remaining_usd))
                    result["disposition"] = "stopped-budget"
                    return finish(root, result, problems)
                phase2 = run_phase(config, root, slot, row, "primary-phase-2",
                                   primary_argv(root, remaining_wall,
                                                session_id(row["attempt_id"]),
                                                "%.4f" % remaining_usd, admission, agents,
                                                resume=True))
                result["phases"].append(phase2)

        # #130's render-only completion: the final rendered result has returned,
        # with the payload and the research report the dispatch requires.
        completed = run(sys.executable, str(root / "runner" / "mark_event.py"),
                        str(timing), "completed_at", check=False)
        if completed.returncode:
            problems.append("could not record completed_at: %s" % completed.stdout.strip())

        post = isolation_phase(config, root, slot, "post-dispatch",
                               root / "artifacts" / "isolation-post.json")
        if post.returncode:
            problems.append("post-dispatch isolation failed: %s"
                            % (post.stdout or post.stderr).strip())
        result["elapsed_seconds"] = round(time.time() - started, 3)
        result.setdefault("disposition", "dispatched")
        return finish(root, result, problems)
    finally:
        proxy.terminate()


def run_phase(config, root, slot, row, label, argv) -> dict:
    """One container invocation of the primary, with its envelope retained."""
    import time

    name = "bd150-%s-%s" % (root.name, label)
    started = time.time()
    observed = run(*docker_argv(config, root, slot, name, argv, root / "work"),
                   check=False)
    (root / "logs" / ("%s.log" % label)).write_text(
        (observed.stdout or "") + "\n--- stderr ---\n" + (observed.stderr or ""),
        encoding="utf-8")
    found = envelope(observed.stdout or "")
    if found:
        write(root / "artifacts" / ("%s-result.json" % label), found)
    return {"label": label, "exit_code": observed.returncode,
            "stderr_tail": (observed.stderr or "").strip()[-400:],
            "elapsed_seconds": round(time.time() - started, 3),
            "subtype": (found or {}).get("subtype"),
            "is_error": (found or {}).get("is_error"),
            "cost_usd": float((found or {}).get("total_cost_usd") or 0.0),
            "num_turns": (found or {}).get("num_turns"),
            "envelope": bool(found)}


def finish(root, result, problems) -> int:
    write(root / "artifacts" / "dispatch.json", result)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def transcripts_for(root) -> list:
    """Every transcript this cell's sessions wrote, root and workers alike."""
    home = root.parent / "homes" / root.name / ".claude" / "projects"
    return sorted(str(path) for path in home.rglob("*.jsonl")) if home.is_dir() else []


FILE_TOOLS = ("Read", "Write", "Edit", "Glob", "Grep", "NotebookEdit")

# Paths every container session touches that belong to the image, not to the host:
# the runtime, the toolchains and the session's own home. A read of one of these is
# not a read of forbidden material, and flagging them would bury a real hit.
IMAGE_ROOTS = ("/usr/", "/bin/", "/sbin/", "/lib/", "/etc/", "/proc/", "/sys/",
               "/dev/", "/var/", "/opt/", "/root/", "/cell-home", "/tmp/bd148/")


def audit_reads(root, transcripts, permitted, accepted=()) -> dict:
    """What the cell's tools actually addressed, against its permitted roots.

    A read outside the permitted roots, or network use absent from the egress log,
    invalidates the attempt on protocol grounds - so this looks at the arguments the
    session really passed to its file tools and its shell, not at every path-shaped
    string anywhere in the transcript. Tool output quotes paths constantly; treating
    those as reads produces enough false positives to hide a true one.

    It reports evidence, not a verdict: whether a hit is a real escape stays a
    judgment for the researcher, which is why each one is recorded with the tool
    that made it.
    """
    import re

    suspects = {}
    # Only a path that starts a token is an absolute path. Without the lookbehind
    # this also matches inside "./xds/internal/..." and inside a URL's
    # "https://github.com/...", which are relative paths and text, not reads. The
    # glob characters are excluded too: find's -not -path '*/target/*' names a
    # pattern, not a path, and matching inside it manufactured a false hit.
    absolute = re.compile(r"(?<![A-Za-z0-9_.:/@+~*?\]\[-])(/[A-Za-z0-9_][A-Za-z0-9_./@+-]*)")
    allowed = tuple(str(Path(entry)) for entry in permitted) + IMAGE_ROOTS
    commands = 0
    tool_calls = 0

    # An acceptance is a recorded judgment that one hit is not an escape, with its
    # reason. It keeps the hit visible instead of widening the pattern until the
    # check stops firing, and #152 can overrule every one of them.
    acceptances = {entry["path"]: entry.get("reason", "") for entry in accepted}
    ruled = []

    def suspicious(candidate, transcript, origin):
        if candidate.startswith(allowed) or candidate in ("/", "/tmp"):
            return
        if candidate in acceptances:
            ruled.append({"path": candidate, "via": origin,
                          "reason": acceptances[candidate]})
            return
        suspects.setdefault(transcript, []).append({"path": candidate, "via": origin})

    for transcript in transcripts:
        try:
            lines = Path(transcript).read_text(encoding="utf-8",
                                              errors="replace").splitlines()
        except OSError as exc:
            suspects.setdefault("unreadable", []).append({"path": transcript,
                                                          "via": str(exc)})
            continue
        for line in lines:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            content = (entry.get("message") or {}).get("content")
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name = block.get("name")
                arguments = block.get("input") or {}
                tool_calls += 1
                if name in FILE_TOOLS:
                    for key in ("file_path", "path", "notebook_path"):
                        value = arguments.get(key)
                        if isinstance(value, str) and value.startswith("/"):
                            suspicious(value, transcript, name)
                elif name == "Bash":
                    commands += 1
                    command = arguments.get("command")
                    if isinstance(command, str):
                        for candidate in set(absolute.findall(command)):
                            suspicious(candidate, transcript, "Bash")
    return {"transcripts": len(transcripts), "tool_calls": tool_calls,
            "shell_commands": commands,
            "paths_outside_permitted_roots": suspects,
            "accepted_hits": ruled,
            "passed": not suspects}


def without_synthetic(transcripts, destination) -> tuple:
    """Copies of the transcripts with the harness's own synthetic lines removed.

    When a session hits an API error the harness writes an assistant line with model
    ``<synthetic>``. ``transcript_usage.py`` drops it, but ``meter_split.py`` counts
    it as a second model and refuses the transcript as mixed-model, which costs the
    attempt its per-role split. Rather than edit a script the manifest pins by
    digest, the input is filtered into a copy and the filtering is recorded: the
    removed lines carry no usage, so no cost moves.
    """
    destination.mkdir(parents=True, exist_ok=True)
    copies = []
    removed = 0
    for transcript in transcripts:
        kept = []
        for line in Path(transcript).read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except ValueError:
                kept.append(line)
                continue
            if (entry.get("message") or {}).get("model") == "<synthetic>":
                removed += 1
                continue
            kept.append(line)
        copy = destination / Path(transcript).name
        copy.write_text("\n".join(kept) + "\n", encoding="utf-8")
        copies.append(str(copy))
    return copies, removed


def settle(config, position, attempt=1):
    row = dict(schedule_row(config, position))
    row["attempt_id"] = attempt_id_for(row, attempt)
    root = cell_root(config, position)
    slot, arm = row["target_slot"], row["arm"]
    dispatched = load(root / "artifacts" / "dispatch.json")
    spec = load(root / "artifacts" / "cell-env-dispatch.json")
    problems = []
    record = {"schema_version": "bounded-discovery-v1", "position": int(position),
              "cell_id": row["cell_id"], "attempt_id": row["attempt_id"], "arm": arm,
              "target_slot": slot, "dispatch_disposition": dispatched.get("disposition")}

    transcripts = transcripts_for(root)
    record["transcript_count"] = len(transcripts)
    if not transcripts:
        problems.append("no transcript was retained, so nothing can be metered from it")

    # Model and effort on every assistant line of every transcript, per role.
    effort = run(sys.executable, str(Path(config["tools"]) / "agent_effort.py"),
                 *transcripts, check=False) if transcripts else None
    if effort is not None:
        (root / "artifacts" / "effort.txt").write_text(effort.stdout or "", encoding="utf-8")
        if effort.returncode:
            problems.append("agent_effort.py exited %s" % effort.returncode)

    # Price each transcript at its own model's rate and sum the groups.
    self_report = sum(phase.get("cost_usd") or 0.0 for phase in dispatched.get("phases", []))
    self_report += float((dispatched.get("finder") or {}).get("cost_usd") or 0.0)
    if transcripts:
        split = run(sys.executable,
                    str(Path(config["bundle"]) / "scripts" / "meter_split.py"),
                    "--rates", str(Path(config["bundle"]) / "rates.json"),
                    "--out", str(root / "artifacts" / "usage-split.json"),
                    "--label", row["attempt_id"],
                    "--self-report", "%.7f" % self_report,
                    *transcripts, check=False)
        (root / "logs" / "meter.log").write_text(
            (split.stdout or "") + (split.stderr or ""), encoding="utf-8")
        # meter_split exits 1 when the two sources differ by more than its default
        # tolerance, but it still writes the split. The preregistration expects every
        # cell to differ - it names the cause - so the split is kept and the
        # difference is decomposed below rather than failing the settlement.
        if split.returncode and not (root / "artifacts" / "usage-split.json").is_file():
            log = (split.stdout or "") + (split.stderr or "")
            if "<synthetic>" in log:
                filtered, removed = without_synthetic(
                    transcripts, root / "artifacts" / "filtered-transcripts")
                record["metering_filtered_synthetic_lines"] = removed
                split = run(sys.executable,
                            str(Path(config["bundle"]) / "scripts" / "meter_split.py"),
                            "--rates", str(Path(config["bundle"]) / "rates.json"),
                            "--out", str(root / "artifacts" / "usage-split.json"),
                            "--label", row["attempt_id"],
                            "--self-report", "%.7f" % self_report,
                            *filtered, check=False)
                (root / "logs" / "meter-filtered.log").write_text(
                    (split.stdout or "") + (split.stderr or ""), encoding="utf-8")
            if not (root / "artifacts" / "usage-split.json").is_file():
                problems.append("meter_split.py exited %s and wrote no split; see logs/meter.log"
                                % split.returncode)

    accepted = load(root / "artifacts" / "audit-acceptances.json", [])
    audit = audit_reads(root, transcripts, spec["permitted_roots"], accepted)
    write(root / "artifacts" / "read-audit.json", audit)
    if not audit["passed"]:
        problems.append("the transcripts name paths outside the permitted roots; "
                        "the attempt is invalid on protocol grounds unless the "
                        "researcher rules each one a false positive")
    try:
        egress = [json.loads(line) for line
                  in (root / "artifacts" / "egress.jsonl").read_text(
                      encoding="utf-8").splitlines() if line.strip()]
    except OSError:
        egress = []
    record["egress_attempts"] = len(egress)
    record["egress_refused"] = sum(1 for entry in egress
                                   if entry.get("decision") not in ("allow", "allowed"))

    # Settlement charges the larger of the self-report and the retained records, and
    # records the difference between them as a reconciliation residual. The probes
    # found the runtime bills a small Haiku request it never writes to a transcript,
    # so the residual is decomposed: the part the envelopes attribute to an
    # untranscripted model, and whatever is left unexplained.
    metered = self_report
    transcript_total = None
    try:
        split_document = load(root / "artifacts" / "usage-split.json")
        transcript_total = float(split_document.get("total_cost_usd") or 0.0)
        metered = max(metered, transcript_total)
        record["usage_split_total_usd"] = split_document.get("total_cost_usd")
        record["usage_within_tolerance"] = split_document.get("within_tolerance")
        record["models_priced"] = sorted(split_document.get("per_model", {}))
    except Failed:
        problems.append("no usage split was produced")

    envelope_models = {}
    for result_file in sorted((root / "artifacts").glob("*-result.json")):
        for model, usage in (load(result_file).get("modelUsage") or {}).items():
            envelope_models[model] = envelope_models.get(model, 0.0) + (usage.get("costUSD") or 0.0)
    record["envelope_per_model_usd"] = {m: "%.7f" % c for m, c in sorted(envelope_models.items())}
    record["self_report_usd"] = "%.7f" % self_report
    record["settled_usd"] = "%.7f" % metered
    if transcript_total is None:
        # Without a transcript total there is nothing to reconcile against, so the
        # residual is undetermined rather than zero, and saying zero would claim the
        # two sources agree when one of them is missing.
        record["reconciliation_residual_usd"] = None
        record["residual_note"] = ("no transcript split was produced, so the settlement rests "
                                   "on the runtime self-report alone and the residual is "
                                   "undetermined")
    else:
        priced = set(split_document.get("per_model", {}))
        untranscripted = sum(cost for model, cost in envelope_models.items()
                             if model not in priced)
        residual = self_report - transcript_total
        unexplained = residual - untranscripted
        record["reconciliation_residual_usd"] = "%.7f" % residual
        record["residual_untranscripted_models_usd"] = "%.7f" % untranscripted
        record["residual_unexplained_usd"] = "%.7f" % unexplained
        # One per cent of the attempt is this runner's reporting threshold, not a
        # frozen value: below it the residual is noted, above it a researcher looks.
        if metered and abs(unexplained) > 0.01 * metered:
            problems.append("%.7f of the reconciliation residual is unexplained, above one "
                            "per cent of the settled cost; meter by hand before trusting "
                            "this cell" % unexplained)

    # Re-settlement is prohibited by the ledger and rightly so, but this stage has to
    # be re-runnable to correct a record without charging twice, so an existing
    # settlement for this reservation is reported rather than attempted again.
    reservation_id = "%s-reservation" % row["attempt_id"]
    ledger = load(config["ledger"])
    already = next((event for event in ledger["events"]
                    if event.get("reservation_id") == reservation_id
                    and event.get("operation") == "settle"), None)
    if already:
        record["ledger_already_settled_usd"] = already["actual_delta_usd"]
        record["ledger_settled_at"] = already["observed_at"]
        if abs(float(already["actual_delta_usd"]) - metered) > 0.0000005:
            problems.append("the ledger settled %s for this attempt but metering now says "
                            "%.7f; the ledger is append-only and stands"
                            % (already["actual_delta_usd"], metered))
    else:
        budget = Path(config["targets"]).parent / "scripts" / "budget.py"
        settled = run(sys.executable, str(budget), config["ledger"], "settle",
                      "--id", reservation_id,
                      "--amount", "%.7f" % metered, "--phase", "review",
                      "--attempt", row["attempt_id"], "--ticket", "150",
                      "--evidence", "metered from the retained per-request records and the "
                                    "result envelopes of cell %s" % row["cell_id"], check=False)
        if settled.returncode:
            problems.append("ledger settlement refused: %s"
                            % (settled.stdout or settled.stderr).strip())
    record["problems"] = problems
    write(root / "artifacts" / "settle.json", record)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def audit_self_test() -> list:
    """The read audit, against the false positives a real cell transcript produced."""
    import tempfile

    root = Path(tempfile.mkdtemp())
    permitted = ["/tmp/bd150/cells/position-01/clone"]

    def transcript(*tool_uses):
        path = root / ("t%d.jsonl" % len(list(root.glob("*.jsonl"))))
        with open(path, "w", encoding="utf-8") as handle:
            for name, arguments in tool_uses:
                handle.write(json.dumps({"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": name, "input": arguments}]}}) + "\n")
        return [str(path)]

    checks = []
    # Every one of these appeared in cell 1's transcript and must not be a hit.
    benign = transcript(
        ("Bash", {"command": "find . -not -path '*/target/*' | head -5"}),
        ("Bash", {"command": "go vet ./xds/internal/balancer/priority/"}),
        ("Bash", {"command": "echo https://github.com/grpc/grpc-go/blob/abc/x.go"}),
        ("Bash", {"command": "ls /usr/local/go/bin"}),
        ("Read", {"file_path": "/tmp/bd150/cells/position-01/clone/go.mod"}),
    )
    result = audit_reads(root, benign, permitted)
    checks.append(("a glob, a relative path, a URL and an image path are not reads",
                   result["passed"] and result["shell_commands"] == 4
                   and result["tool_calls"] == 5))
    scratch = transcript(("Bash", {"command": "git show master:a.rs > /tmp/view.txt"}))
    checks.append(("an unaccepted out-of-root path still fails",
                   not audit_reads(root, scratch, permitted)["passed"]))
    ruled = audit_reads(root, scratch, permitted,
                        [{"path": "/tmp/view.txt", "reason": "its own clone's content"}])
    checks.append(("an accepted hit passes but stays visible with its reason",
                   ruled["passed"] and len(ruled["accepted_hits"]) == 1
                   and ruled["accepted_hits"][0]["reason"]))
    escaped = transcript(("Read", {"file_path": "/Users/jack/Development/skills/AGENTS.md"}))
    result = audit_reads(root, escaped, permitted)
    checks.append(("a read outside the permitted roots is a hit",
                   not result["passed"]
                   and result["paths_outside_permitted_roots"][escaped[0]][0]["via"] == "Read"))
    shell = transcript(("Bash", {"command": "cat /Users/jack/.config/bounded-discovery/x"}))
    checks.append(("a shell path outside the permitted roots is a hit",
                   not audit_reads(root, shell, permitted)["passed"]))
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stage", nargs="?", choices=("prepare", "dispatch", "settle"))
    parser.add_argument("--config")
    parser.add_argument("--position", type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--attempt-number", type=int, default=1,
                        help="attempt ordinal for this cell; IDs are never recycled")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.stage or not args.config or args.position is None:
        parser.error("a stage, --config and --position are required")
    config = load(args.config)
    try:
        if args.stage == "prepare":
            return prepare(config, args.position, force=args.force)
        if args.stage == "dispatch":
            return dispatch(config, args.position, attempt=args.attempt_number)
        return settle(config, args.position, attempt=args.attempt_number)
    except Failed as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2


def self_test():
    checks = []
    template = ("## Primary dispatch prompt\n\n````markdown\nhello {NAME}\n````\n\n"
                "### `{ADMISSION}` section\n\n````markdown\nresume {WHAT}\n````\n")
    block = fenced(template, "## Primary dispatch prompt")
    checks.append(("a fenced block is extracted verbatim", block == "hello {NAME}\n"))
    checks.append(("a later heading's block is found",
                   fenced(template, "### `{ADMISSION}` section") == "resume {WHAT}\n"))
    try:
        fenced(template, "## Absent")
        checks.append(("a missing heading is an input error", False))
    except Failed:
        checks.append(("a missing heading is an input error", True))
    checks.append(("rendering substitutes every placeholder",
                   render("hello {NAME}", {"NAME": "world"}) == "hello world"))
    checks.append(("an unfilled placeholder is reported",
                   unfilled("a {ONE} b {TWO_X} c") == ["{ONE}", "{TWO_X}"]))
    checks.append(("a rendered prompt reports none",
                   unfilled(render("hello {NAME}", {"NAME": "world"})) == []))
    checks.append(("lowercase braces are not placeholders", unfilled("{braces}") == []))
    # Arm C's barrier block is substituted into the dispatch prompt and itself
    # names {FREEZE}: a single pass over the outer template leaves that behind.
    values = {"FREEZE": "/cell/work/freeze.json"}
    values["BLOCK"] = render("write {FREEZE} and stop", values)
    checks.append(("a block rendered before substitution leaves no placeholder",
                   unfilled(render("prompt: {BLOCK}", values)) == []))
    checks.append(("substituting an unrendered block would leave one",
                   unfilled(render("prompt: {BLOCK}", {"BLOCK": "write {FREEZE}"}))
                   == ["{FREEZE}"]))
    checks.extend(audit_self_test())
    for name, passed in checks:
        print("%s %s" % ("ok  " if passed else "FAIL", name))
    return 0 if all(passed for _, passed in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
