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
    Re-check isolation, meter the attempt per model with ``meter_split.py``,
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

CONTAINER = {"clone": "/cell/clone", "snapshot": "/cell/snapshot",
             "packet": "/cell/packet", "work": "/cell/work",
             "runner": "/cell/runner", "finder_store": "/cell/finder-store",
             "artifacts": "/cell/artifacts"}

# Per-slot toolchain caches. The packets hardcode these paths, so the container
# mounts each cell's private copy at the identical path and the frozen execution
# note stays literally true inside it.
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


def digest(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    try:
        return json.loads(Path(os.path.expanduser(str(path))).read_text(encoding="utf-8"))
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
    shutil.copytree(os.path.expanduser(manifest["mirror"]["path"]), mirror)
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
        shutil.copytree(cache, destination, symlinks=True)

    shutil.copyfile(Path(__file__).resolve().parent / "mark_event.py",
                    root / "runner" / "mark_event.py")

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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stage", nargs="?", choices=("prepare", "dispatch", "settle"))
    parser.add_argument("--config")
    parser.add_argument("--position", type=int)
    parser.add_argument("--force", action="store_true")
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
        print("%s is not implemented in this revision" % args.stage)
        return 1
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
    for name, passed in checks:
        print("%s %s" % ("ok  " if passed else "FAIL", name))
    return 0 if all(passed for _, passed in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
