#!/usr/bin/env python3
"""Build strict Claude review settings and gate file tools before execution.

Usage: python3 review_isolation.py settings --attempt DIR --clone DIR --out FILE
           [--profile claude-strict-v1|claude-strict-v2] [--target DIR]
       python3 review_isolation.py hook --attempt DIR --clone DIR

The hook reads Claude's PreToolUse JSON on stdin and returns a deny decision on
malformed input or a file operation outside the attempt's declared directories.
Bash uses Claude's OS sandbox, with network access and unsandboxed retries disabled.
``claude-strict-v2`` also gives the shell the offline cache environment of the target
in ``--target``, and ``attempt_audit.py`` judges its requests by what these settings
let the reviewer reach. ``claude-strict-v1`` keeps its request-level audit.
Exit codes: 0 settings or hook decision written; 2 setup/input failure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

PROFILES = ("claude-strict-v1", "claude-strict-v2")
ENFORCED = "claude-strict-v2"
SYSTEM = ("usr", "bin", "sbin", "lib", "lib64", "etc", "dev", "proc")
TOOLS = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "Agent", "Skill"]
DENIAL = "Benchmark isolation: "
# Claude's sandbox binds these when they exist on the host, whatever the settings deny.
BUILT_IN = ("/tmp/claude", "/private/tmp/claude")


def prepare_runtime_cache(clone: Path) -> None:
    modules = []
    for directory, dirs, _files in os.walk(clone, followlinks=False):
        if "node_modules" in dirs:
            modules.append(Path(directory, "node_modules"))
            dirs.remove("node_modules")
        if ".git" in dirs:
            dirs.remove(".git")
    for directory in modules:
        for name in (".vite-temp", ".vite"):
            relocate_cache(clone, directory / name)


def relocate_cache(clone: Path, link: Path) -> None:
    target = Path(str(clone) + "-work") / "runtime-cache" / link.relative_to(clone)
    ignored = subprocess.run(["git", "-C", str(clone), "check-ignore", "-q", str(link)], capture_output=True)
    if ignored.returncode != 0:
        raise ValueError(f"runtime cache must be git-ignored: {link}")
    if link.is_symlink() and link.resolve() == target:
        return
    if link.exists() or link.is_symlink():
        raise ValueError(f"runtime cache already exists: {link}")
    target.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target, target_is_directory=True)


def contained(path: Path, roots: list) -> bool:
    resolved = path.resolve()
    return any(resolved == root or root in resolved.parents for root in roots)


def roots(attempt: Path, clone: Path) -> tuple:
    writable = [Path(str(clone) + suffix) for suffix in ("-cache", "-work")]
    writable += [attempt / "tmp", attempt / "artifacts"]
    readable = [clone, attempt / "home/.claude/skills/review-code", *writable]
    return readable, writable


def file_decision(event: dict, attempt: Path, clone: Path) -> str:
    if not isinstance(event, dict) or not isinstance(event.get("tool_input"), dict):
        return "malformed tool event"
    tool, inputs = event["tool_name"], event["tool_input"]
    if tool not in TOOLS:
        return "tool is outside the frozen tool list"
    if tool == "Bash":
        if inputs.get("run_in_background") or inputs.get("timeout", 120000) > 300000:
            return "shell commands must be awaited and limited to five minutes"
        return ""
    if tool in ("Agent", "Skill"):
        return ""
    readable, writable = roots(attempt, clone)
    writing = tool in ("Write", "Edit")
    path = inputs.get("file_path") if tool in ("Read", "Write", "Edit") else inputs.get("path", event.get("cwd", str(clone)))
    if not isinstance(path, str) or not path:
        return "missing file path"
    path = Path(path).expanduser()
    if not path.is_absolute():
        path = Path(event.get("cwd", str(clone))) / path
    if not contained(path, writable if writing else readable):
        return "path is outside the permitted read or write directories"
    if tool == "Glob":
        pattern = inputs.get("pattern", "")
        if not isinstance(pattern, str) or pattern.startswith(("/", "~")) or ".." in Path(pattern).parts:
            return "glob must stay beneath its declared directory"
    if tool in ("Grep", "Glob") and path.is_dir():
        for directory, dirs, files in os.walk(path, followlinks=False):
            for name in dirs + files:
                entry = Path(directory, name)
                if entry.is_symlink() and not contained(entry, readable):
                    return "recursive search contains a symlink outside the permitted directories"
    return ""


def target_env(target: Path, clone: Path) -> dict:
    import provision
    try:
        config = provision.cache_config(provision.load_target(str(target)))
    except provision.ProvisionError as error:
        raise ValueError(str(error)) from error
    paths = provision.substitutions(str(clone) + "-cache", provision.DEFAULT_CACHE_ROOT, str(clone), str(clone) + "-work")
    return {name: provision.render(value, paths) for name, value in config["env"].items()}


def exposes(path: str, config: dict) -> bool:
    """Whether a read at or beneath ``path`` reaches anything the sandbox neither denies nor
    declares readable. A denied directory that holds a declared one exposes only that one."""
    files = config["sandbox"]["filesystem"]
    real = os.path.realpath(path)

    def under(roots) -> bool:
        return any(real == root or real.startswith(root.rstrip("/") + "/") for root in roots)
    if any(os.path.lexists(bound) and (under([bound]) or bound.startswith(real.rstrip("/") + "/")) for bound in BUILT_IN):
        return True
    if under(files["allowRead"]) or under(["/" + name for name in SYSTEM]) or under(files["denyRead"]):
        return False
    if real == "/":
        return any(entry.name not in SYSTEM and str(entry) not in files["denyRead"] for entry in Path("/").iterdir())
    return True


def settings(attempt: Path, clone: Path, env: dict = None) -> dict:
    readable, writable = roots(attempt, clone)
    denied = sorted(str(p) for p in Path("/").iterdir() if p.name not in SYSTEM)
    denied += ["/dev/shm", "/proc"]
    runtime = ["/proc/self", "/proc/thread-self", "/proc/cpuinfo", "/proc/meminfo", "/proc/stat", "/proc/sys", "/proc/uptime", "/proc/version"]
    binaries = []
    for name in ("python3", "node", "go", "rg", "bwrap", "socat"):
        executable = shutil.which(name)
        if not executable:
            raise ValueError(f"required executable is missing: {name}")
        resolved = Path(executable).resolve()
        binaries.append(str(resolved.parent))
        runtime.append(str(resolved.parent.parent if name in ("python3", "node", "go") else resolved.parent))
    command = shlex.join([sys.executable, str(Path(__file__).resolve()), "hook", "--attempt", str(attempt), "--clone", str(clone)])
    return {
        "env": {**(env or {}), "PATH": ":".join(dict.fromkeys(binaries + ["/usr/local/bin", "/usr/bin", "/bin", "/usr/sbin", "/sbin"]))},
        "sandbox": {
            "enabled": True, "failIfUnavailable": True,
            "allowUnsandboxedCommands": False, "excludedCommands": [],
            "network": {"allowedDomains": [], "allowLocalBinding": True, "allowAllUnixSockets": False},
            "filesystem": {
                "denyRead": denied, "allowRead": sorted(set(runtime + [str(p) for p in readable])),
                "allowWrite": [str(p) for p in writable], "denyWrite": [str(clone)],
            },
            "credentials": {"envVars": [{"name": name, "mode": "deny"} for name in (
                "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN",
                "GH_TOKEN", "GITHUB_TOKEN", "OPENAI_API_KEY",
            )]},
        },
        "permissions": {
            "defaultMode": "dontAsk", "blockReadsOutsideWorkingDirectories": True,
            "additionalDirectories": [str(p) for p in readable],
            "disableBypassPermissionsMode": "disable", "disableAutoMode": "disable",
        },
        "hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": command, "timeout": 30}]}]},
    }


def verify_evidence(attempt: Path, profile: str) -> list:
    try:
        config_bytes = (attempt / "isolation-settings.json").read_bytes()
        evidence = json.loads((attempt / "isolation.json").read_text(encoding="utf-8"))
        config = json.loads(config_bytes)
        sandbox = config["sandbox"]
        if evidence["profile"] != profile or evidence["settings_sha256"] != hashlib.sha256(config_bytes).hexdigest():
            return ["isolation profile or settings hash changed"]
        if evidence["hook_sha256"] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
            return ["isolation hook code changed since setup"]
        if not sandbox["enabled"] or not sandbox["failIfUnavailable"] or sandbox["allowUnsandboxedCommands"] or sandbox["excludedCommands"] or sandbox["network"]["allowedDomains"]:
            return ["isolation settings do not require an offline sandbox"]
        if not config["hooks"]["PreToolUse"] or not config["permissions"]["blockReadsOutsideWorkingDirectories"]:
            return ["isolation file-tool boundary is missing"]
        return []
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [f"cannot verify isolation evidence: {error}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("settings", "hook"))
    parser.add_argument("--attempt", type=Path, required=True)
    parser.add_argument("--clone", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--profile", choices=PROFILES, default=PROFILES[0])
    parser.add_argument("--target", type=Path)
    args = parser.parse_args()
    attempt, clone = args.attempt.resolve(), args.clone.resolve()
    if args.action == "hook":
        try:
            reason = file_decision(json.load(sys.stdin), attempt, clone)
        except Exception as error:
            reason = f"cannot verify tool boundaries: {type(error).__name__}"
        if reason:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": DENIAL + reason}}))
        return 0
    try:
        if args.out is None:
            raise ValueError("settings requires --out")
        if not contained(clone, [attempt]) or clone == attempt:
            raise ValueError("clone must be a directory beneath the attempt")
        if args.profile == ENFORCED and args.target is None:
            raise ValueError(f"{ENFORCED} requires --target")
        bound = [path for path in BUILT_IN if os.path.lexists(path)]
        if args.profile == ENFORCED and bound:
            raise ValueError(f"the sandbox would expose {', '.join(bound)}; remove it before dispatch")
        config = settings(attempt, clone, target_env(args.target, clone) if args.profile == ENFORCED else None)
        prepare_runtime_cache(clone)
        args.out.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        evidence = {"profile": args.profile, "settings_sha256": hashlib.sha256(args.out.read_bytes()).hexdigest(),
                    "hook_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        (attempt / "isolation.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        print(args.out)
        return 0
    except (OSError, ValueError) as error:
        print(f"review_isolation.py: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
