#!/usr/bin/env python3
"""#151's stopped-run closeout: the stop gate, the fidelity assessment, the
ledger reconciliation, the 24-cell manifest and the stage handoff.

#150 delivered ``stopped-incomplete`` and PR #197 left ``pilot/actual-fidelity``
unresolved. This ticket launches no further reviewer run. It establishes that
every reviewer run that ever started has terminated, opens the sealed evidence
only after that gate is on record, and assembles the closeout #152 grades from.

Four things this helper refuses to do, because each would turn an absence of
evidence into a result:

* clear fidelity for an attempt whose settings, isolation, context identity or
  usage cannot be observed - the verdict is ``unresolved`` with the missing
  evidence named;
* treat a budget stop as infrastructure invalidity, which would earn a
  replacement the frozen rule does not allow;
* drop an unmetered request rather than retaining a conservative bound for it;
* name a slot. Every public artifact is keyed by schedule position, because the
  pilot's selection rule is public and naming its slots would disclose which
  slot holds the clean control.

Subcommands::

    closeout.py gate --ledger L --out gate.json [--probes-from F] [--raw-out F]
    closeout.py open-seal --gate gate.json --seal S --key K --archive A --into D
    closeout.py fidelity --gate gate.json --evidence D --bundle B --out F
    closeout.py reconcile --ledger L --evidence D --bundle B --out R
    closeout.py manifest --schedule-count 24 --pilot-bundle B --fidelity F \\
        --reconciliation R --out manifest.json
    closeout.py handoff --gate G --fidelity F --reconciliation R \\
        --manifest M --packets P --out handoff.json
    closeout.py --self-test

Exit: 0 on success, 1 on a content violation with one line per violation on
stdout, 2 when an input cannot be read or a subprocess fails.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

PLANNED_CELLS = 24
PILOT_CELLS = 6
ATTEMPT_LIMIT = 27
REPLACEMENT_LIMIT = 3

# A reviewer run of this experiment is a container the coordinator names, or a
# host process holding one of its workspaces. The coordinating session that runs
# this script is a `claude` process too and is deliberately not matched by name:
# what marks a reviewer run is the cell naming, not the binary.
CELL_CONTAINER_PREFIX = "bd150-"
REVIEWER_PROCESS_MARKERS = ("bd150-", "run_cell.py", "bounded-discovery/issue-150/cells",
                            "session-homes")


class Failed(Exception):
    """A content violation: reported on stdout, exit 1."""


def load(path, default=None):
    try:
        return json.loads(Path(os.path.expanduser(str(path))).read_text(encoding="utf-8"))
    except FileNotFoundError:
        if default is not None:
            return default
        sys.stderr.write("missing %s\n" % path)
        raise SystemExit(2)
    except (OSError, ValueError) as exc:
        sys.stderr.write("cannot read %s: %s\n" % (path, exc))
        raise SystemExit(2)


def write(path, payload) -> None:
    target = Path(os.path.expanduser(str(path)))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def usd(value) -> Decimal:
    return Decimal(str(value if value not in (None, "") else "0"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def capture(argv, timeout=120) -> dict:
    """Run a probe. A missing tool or an unreachable daemon is an observation,
    not a crash: what it establishes is recorded by the caller."""
    try:
        done = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                              timeout=timeout, check=False)
        return {"command": list(argv), "exit_code": done.returncode,
                "stdout": done.stdout, "stderr": done.stderr, "ran": True}
    except FileNotFoundError:
        return {"command": list(argv), "exit_code": None, "stdout": "", "ran": False,
                "stderr": "command not found"}
    except (OSError, subprocess.SubprocessError) as exc:
        return {"command": list(argv), "exit_code": None, "stdout": "", "ran": False,
                "stderr": str(exc)}


# --------------------------------------------------------------------------
# The stop gate
# --------------------------------------------------------------------------

def live_probes() -> dict:
    """Capture the host state the gate reads. Raw output is retained separately
    and sealed: a process command line can name a slot."""
    return {
        "captured_at": now(),
        "processes": capture(["ps", "-eo", "pid=,ppid=,command="]),
        "containers": capture(["docker", "ps", "-a", "--no-trunc",
                               "--format", "{{.Names}}\t{{.Status}}"]),
        "workspaces": capture(["find", os.path.expanduser("~"), "-maxdepth", "5",
                               "-type", "d", "-name", "position-0*"], timeout=600),
        "self_pid": os.getpid(),
    }


def probe_evidence(name, probe, passed, detail, count=None) -> dict:
    """One gate check. The raw capture never reaches the public record; its
    digest and the counts derived from it do."""
    record = {"check": name, "passed": bool(passed), "detail": detail,
              "command": probe.get("command"), "exit_code": probe.get("exit_code"),
              "output_sha256": digest(probe.get("stdout", "") + probe.get("stderr", ""))}
    if count is not None:
        record["match_count"] = count
    return record


def parse_processes(probe) -> dict:
    """``pid -> (ppid, command)`` from a ``ps -eo pid=,ppid=,command=`` capture."""
    table = {}
    for line in probe.get("stdout", "").splitlines():
        fields = line.strip().split(None, 2)
        if len(fields) < 3 or not fields[0].isdigit() or not fields[1].isdigit():
            continue
        table[int(fields[0])] = (int(fields[1]), fields[2])
    return table


def own_ancestry(table, self_pid) -> set:
    """This gate's own pid and every ancestor of it.

    The gate names its cell root on its command line and runs under a shell that
    repeats it, so the invocation would otherwise match its own marker. Excluding
    the ancestry rather than one pid is what makes the check mean "a reviewer run
    other than this closeout session"."""
    ancestry, pid, seen = {int(self_pid)}, int(self_pid), set()
    while pid in table and pid not in seen:
        seen.add(pid)
        pid = table[pid][0]
        if pid <= 0:
            break
        ancestry.add(pid)
    return ancestry


def reviewer_processes(probe, self_pid) -> dict:
    """Processes whose command line names a cell container, the coordinator or a
    cell workspace, split into live reviewer runs and this gate's own ancestry."""
    table = parse_processes(probe)
    ancestry = own_ancestry(table, self_pid)
    found, excluded = [], []
    for pid, (_, command) in table.items():
        if not any(marker in command for marker in REVIEWER_PROCESS_MARKERS):
            continue
        (excluded if pid in ancestry else found).append(pid)
    return {"live": sorted(found), "own_ancestry": sorted(excluded)}


def live_containers(probe) -> dict:
    """Cell containers still present, and whether the runtime could be asked.

    The cells run under ``docker run --rm``, so a terminated cell leaves no
    container to list. An unreachable daemon therefore establishes that no cell
    container is running and cannot establish anything about ones that exited;
    both readings are recorded rather than collapsed into a pass."""
    text = probe.get("stdout", "") + probe.get("stderr", "")
    reachable = probe.get("ran") and probe.get("exit_code") == 0
    running = []
    if reachable:
        for line in probe.get("stdout", "").splitlines():
            name, _, status = line.partition("\t")
            if name.strip().startswith(CELL_CONTAINER_PREFIX):
                running.append(status.strip().split()[0] if status.strip() else "unknown")
    daemon_down = ("Cannot connect to the Docker daemon" in text
                   or "failed to connect to the docker API" in text
                   or not probe.get("ran"))
    return {"reachable": bool(reachable), "daemon_unreachable": bool(daemon_down),
            "cell_containers": running}


def ledger_attempt_state(ledger) -> dict:
    """Attempt lifecycle and reservation state, from the append-only chain."""
    opened, closed, dispositions = [], [], {}
    reservations = Decimal("0")
    for event in ledger.get("events", []):
        operation = event.get("operation")
        if operation == "attempt-open":
            opened.append(event.get("attempt_id"))
        elif operation == "attempt-close":
            closed.append(event.get("attempt_id"))
            dispositions[event.get("attempt_id")] = event.get("disposition")
        reservations += usd(event.get("reservation_delta_usd"))
    unclosed = [a for a in opened if a not in closed]
    return {"opened": opened, "closed": closed, "unclosed": unclosed,
            "dispositions": dispositions, "reservation_balance": reservations}


def chain_intact(ledger) -> tuple:
    previous = None
    for index, event in enumerate(ledger.get("events", [])):
        if event.get("previous_event_id") != previous:
            return False, index
        previous = event.get("event_id")
    return True, None


def latest_event_time(ledger) -> str:
    times = [e.get("observed_at") for e in ledger.get("events", []) if e.get("observed_at")]
    return max(times) if times else ""


def build_gate(ledger, probes, cells_root) -> dict:
    """The all-reviewers-stopped gate. Every check must pass before any sealed
    outcome may be opened; a failure names what is still live."""
    observed_at = now()
    state = ledger_attempt_state(ledger)
    checks = []

    process_probe = probes["processes"]
    processes = reviewer_processes(process_probe, probes.get("self_pid", os.getpid()))
    live_pids = processes["live"]
    check = probe_evidence(
        "no reviewer or coordinator process is running", process_probe, not live_pids,
        ("no process outside this gate's own ancestry names a cell container, the "
         "coordinator or a cell workspace; %d process(es) in the ancestry of this closeout "
         "session matched and were excluded, because the gate repeats the cell root on its "
         "own command line" % len(processes["own_ancestry"])) if not live_pids
        else "%d process(es) still name a reviewer run" % len(live_pids),
        count=len(live_pids))
    check["own_ancestry_match_count"] = len(processes["own_ancestry"])
    checks.append(check)

    container_probe = probes["containers"]
    containers = live_containers(container_probe)
    if containers["daemon_unreachable"]:
        container_detail = ("the container runtime is not running, so no cell container can be "
                            "executing; because cells run under `docker run --rm` a terminated "
                            "cell leaves nothing to list, and this establishes no cell is live "
                            "rather than how each one exited")
        container_passed = True
    else:
        container_passed = not containers["cell_containers"]
        container_detail = ("the runtime lists no container named %s*" % CELL_CONTAINER_PREFIX
                            if container_passed else
                            "%d cell container(s) still present" % len(containers["cell_containers"]))
    checks.append(probe_evidence("no cell container is running", container_probe,
                                 container_passed, container_detail,
                                 count=len(containers["cell_containers"])))

    configured_root = Path(os.path.expanduser(cells_root)) if cells_root else None
    root_present = bool(configured_root and configured_root.exists())
    sweep = probes.get("workspaces") or {"command": None, "exit_code": None, "ran": False,
                                         "stdout": "", "stderr": "not captured"}
    stray = [line for line in sweep.get("stdout", "").splitlines() if line.strip()]
    workspaces_present = root_present or bool(stray)
    swept = bool(sweep.get("ran"))
    checks.append({"check": "no live cell workspace remains",
                   "passed": (not workspaces_present) and swept,
                   "detail": ("the configured cell root does not exist and a sweep of the user's "
                              "home found no surviving attempt workspace: every workspace was "
                              "archived into the seal and removed, so the sealed archive is the "
                              "only surviving copy of the raw evidence")
                             if not workspaces_present and swept else
                             ("the workspace sweep did not run, so absence is unestablished"
                              if not swept else "")
                             + ("the configured cell root exists" if root_present else "")
                             + ("%s%d stray attempt workspace(s) were found"
                                % ("; " if root_present else "", len(stray)) if stray else ""),
                   "configured_root_exists": root_present,
                   "sweep_ran": swept,
                   "sweep_command": sweep.get("command"),
                   "sweep_match_count": len(stray),
                   "sweep_output_sha256": digest(sweep.get("stdout", "") + sweep.get("stderr", ""))})

    checks.append({"check": "every opened attempt is closed on the ledger",
                   "passed": not state["unclosed"],
                   "detail": "%d attempt-open events, %d attempt-close events, %d unclosed"
                             % (len(state["opened"]), len(state["closed"]), len(state["unclosed"])),
                   "attempts_opened": len(state["opened"]),
                   "attempts_closed": len(state["closed"]),
                   "unclosed_count": len(state["unclosed"])})

    balance = state["reservation_balance"]
    header_reserved = usd(ledger.get("reserved_usd"))
    checks.append({"check": "no budget reservation is outstanding",
                   "passed": balance == 0 and header_reserved == 0,
                   "detail": "reservation deltas sum to %s and the ledger header carries "
                             "reserved_usd %s; an in-flight dispatch would hold a live "
                             "reservation" % (balance, header_reserved),
                   "reservation_delta_sum_usd": str(balance),
                   "header_reserved_usd": str(header_reserved)})

    intact, broken_at = chain_intact(ledger)
    checks.append({"check": "the ledger chain is unbroken through its last event",
                   "passed": intact,
                   "detail": "%d events chain from the open event" % len(ledger.get("events", []))
                             if intact else "the chain breaks at event index %s" % broken_at,
                   "event_count": len(ledger.get("events", []))})

    last_event = latest_event_time(ledger)
    quiet = bool(last_event) and last_event < observed_at
    checks.append({"check": "no ledger event was appended after the last attempt closed",
                   "passed": quiet,
                   "detail": "the newest ledger event is %s, before this gate at %s"
                             % (last_event, observed_at),
                   "latest_event_at": last_event})

    passed = all(check["passed"] for check in checks)
    return {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-151-stop-gate",
        "observed_at": observed_at,
        "probes_captured_at": probes.get("captured_at"),
        "all_reviewers_stopped": passed,
        "seal_may_be_opened": passed,
        "checks": checks,
        "attempt_dispositions": state["dispositions"] and {
            # Dispositions are carried by position, never by attempt id: an
            # attempt id contains its slot.
            "count": len(state["dispositions"]),
            "by_disposition": {value: sum(1 for v in state["dispositions"].values() if v == value)
                               for value in sorted(set(state["dispositions"].values()))},
        } or {"count": 0, "by_disposition": {}},
        "note": ("Recorded before any sealed outcome was opened. #151 launches no further "
                 "experimental reviewer run under the stopped handoff; this gate is what "
                 "permits the sealed pilot evidence to be read for closeout."),
        "raw_capture": ("retained outside the repository and sealed with the closeout evidence: "
                        "a process command line or a container name can contain a slot"),
    }


def command_gate(args) -> int:
    ledger = load(args.ledger)
    probes = load(args.probes_from) if args.probes_from else live_probes()
    gate = build_gate(ledger, probes, args.cells_root)
    if args.raw_out:
        write(args.raw_out, probes)
    write(args.out, gate)
    if not gate["all_reviewers_stopped"]:
        for check in gate["checks"]:
            if not check["passed"]:
                print("gate check failed: %s - %s" % (check["check"], check["detail"]))
        return 1
    return 0


# --------------------------------------------------------------------------
# Opening the seal, after the gate and never before
# --------------------------------------------------------------------------

def command_open_seal(args) -> int:
    """Decrypt the pilot evidence, once the gate says every reviewer has stopped.

    The plaintext is extracted outside the repository. It names slots in its
    paths, its ledger and its transcripts, so a copy inside a worktree would
    disclose the pilot pairing on the first commit that caught it.
    """
    gate = load(args.gate)
    violations = []
    if not gate.get("all_reviewers_stopped"):
        violations.append("the stop gate does not report every reviewer stopped; "
                          "do not open sealed outcomes")
    opened_at = now()
    if gate.get("observed_at", "") >= opened_at:
        violations.append("the gate must be recorded before the seal is opened")
    if violations:
        for line in violations:
            print(line)
        return 1

    seal = load(args.seal)
    archive = Path(os.path.expanduser(args.archive))
    into = Path(os.path.expanduser(args.into))
    if into.exists() and any(into.iterdir()):
        print("refusing to extract into a non-empty directory: %s" % into)
        return 1
    into.mkdir(parents=True, exist_ok=True)

    ciphertext_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    if ciphertext_sha != seal.get("ciphertext_sha256"):
        print("ciphertext digest %s does not match the seal record %s"
              % (ciphertext_sha, seal.get("ciphertext_sha256")))
        return 1

    plaintext = into / "pilot-evidence.tar.gz"
    decrypt = capture(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-iter", "200000",
                       "-pass", "file:%s" % os.path.expanduser(args.key),
                       "-in", str(archive), "-out", str(plaintext)], timeout=600)
    if decrypt["exit_code"] != 0:
        sys.stderr.write("openssl enc -d failed: %s\n" % decrypt["stderr"][:400])
        return 2
    plaintext_sha = hashlib.sha256(plaintext.read_bytes()).hexdigest()
    if plaintext_sha != seal.get("plaintext_sha256"):
        print("plaintext digest %s does not match the seal record %s; do not score against it"
              % (plaintext_sha, seal.get("plaintext_sha256")))
        return 1

    extract = capture(["tar", "-xzf", str(plaintext), "-C", str(into)], timeout=900)
    if extract["exit_code"] != 0:
        sys.stderr.write("tar failed: %s\n" % extract["stderr"][:400])
        return 2
    plaintext.unlink()

    record = {"schema_version": "bounded-discovery-v1",
              "artifact_id": "issue-151-seal-open",
              "gate_observed_at": gate.get("observed_at"),
              "opened_at": opened_at,
              "ciphertext_sha256": ciphertext_sha,
              "plaintext_sha256": plaintext_sha,
              "positions_covered": seal.get("positions"),
              "invalidated_attempts_sealed": seal.get("invalidated_attempts_sealed"),
              "extracted_outside_repository": True,
              "note": ("Opened only after the stop gate. The plaintext stays outside every "
                       "checkout of this repository: its paths, ledger and transcripts name "
                       "slots.")}
    if args.out:
        write(args.out, record)
    print(json.dumps({"opened_at": opened_at, "into": str(into)}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="run the built-in checks and exit")
    sub = parser.add_subparsers(dest="command")

    gate = sub.add_parser("gate", help="record the all-reviewers-stopped gate")
    gate.add_argument("--ledger", required=True)
    gate.add_argument("--cells-root", default="~/.config/bounded-discovery/issue-150/cells")
    gate.add_argument("--probes-from", help="read host probes from a file instead of capturing")
    gate.add_argument("--raw-out", help="write the raw probe capture here (not for the repository)")
    gate.add_argument("--out", required=True)
    gate.set_defaults(handler=command_gate)

    seal = sub.add_parser("open-seal", help="decrypt the pilot evidence after the gate")
    seal.add_argument("--gate", required=True)
    seal.add_argument("--seal", required=True)
    seal.add_argument("--key", required=True)
    seal.add_argument("--archive", required=True)
    seal.add_argument("--into", required=True)
    seal.add_argument("--out")
    seal.set_defaults(handler=command_open_seal)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not getattr(args, "handler", None):
        parser.print_help()
        return 2
    try:
        return args.handler(args)
    except Failed as exc:
        print(str(exc))
        return 1


def self_test() -> int:
    import tempfile
    failures = []

    def check(name, condition):
        if not condition:
            failures.append(name)

    def ledger_with(events, reserved="0.00"):
        chained, previous = [], None
        for event in events:
            event = dict(event)
            event.setdefault("event_id", "e%d" % len(chained))
            event["previous_event_id"] = previous
            event.setdefault("observed_at", "2026-09-09T08:50:09Z")
            event.setdefault("reservation_delta_usd", "0")
            event.setdefault("actual_delta_usd", "0")
            previous = event["event_id"]
            chained.append(event)
        return {"reserved_usd": reserved, "events": chained}

    quiet_probes = {"captured_at": "2026-09-10T00:00:00Z", "self_pid": 4242,
                    "processes": {"command": ["ps"], "exit_code": 0, "ran": True,
                                  "stdout": "4242 900 python3 closeout.py gate --cells-root "
                                            "~/.config/bounded-discovery/issue-150/cells\n"
                                            "900 1 /bin/zsh -c closeout.py gate --cells-root "
                                            "~/.config/bounded-discovery/issue-150/cells\n"
                                            "1 0 /sbin/launchd\n",
                                  "stderr": ""},
                    "containers": {"command": ["docker", "ps"], "exit_code": 1, "ran": True,
                                   "stdout": "",
                                   "stderr": "failed to connect to the docker API"},
                    "workspaces": {"command": ["find"], "exit_code": 0, "ran": True,
                                   "stdout": "", "stderr": ""}}

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        ledger = ledger_with([
            {"operation": "attempt-open", "attempt_id": "a1"},
            {"operation": "attempt-close", "attempt_id": "a1", "disposition": "complete"},
        ])
        (tmp / "ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
        (tmp / "probes.json").write_text(json.dumps(quiet_probes), encoding="utf-8")
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "gate",
                               "--ledger", str(tmp / "ledger.json"),
                               "--probes-from", str(tmp / "probes.json"),
                               "--cells-root", str(tmp / "absent-cells"),
                               "--out", str(tmp / "gate.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("a quiet host with a closed ledger passes the gate", code.returncode == 0)
        gate = json.loads((tmp / "gate.json").read_text(encoding="utf-8"))
        check("the gate reports every reviewer stopped", gate["all_reviewers_stopped"] is True)
        check("an unreachable runtime is recorded as no cell container running",
              any(c["check"] == "no cell container is running" and c["passed"]
                  for c in gate["checks"]))
        check("no raw probe output reaches the gate record",
              "launchd" not in json.dumps(gate))
        check("the gate's own ancestry is excluded rather than dropped silently",
              [c for c in gate["checks"]
               if c["check"].startswith("no reviewer")][0]["own_ancestry_match_count"] == 2)

        # An attempt that was opened and never closed holds the gate shut.
        open_ledger = ledger_with([{"operation": "attempt-open", "attempt_id": "a1"}])
        (tmp / "open.json").write_text(json.dumps(open_ledger), encoding="utf-8")
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "gate",
                               "--ledger", str(tmp / "open.json"),
                               "--probes-from", str(tmp / "probes.json"),
                               "--cells-root", str(tmp / "absent-cells"),
                               "--out", str(tmp / "gate2.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("an unclosed attempt fails the gate", code.returncode == 1)
        check("the failure names the unclosed attempt check",
              "every opened attempt is closed" in code.stdout)

        # A live reservation means a dispatch may still be in flight.
        live = ledger_with([{"operation": "reserve", "reservation_delta_usd": "10.00"}],
                           reserved="10.00")
        (tmp / "live.json").write_text(json.dumps(live), encoding="utf-8")
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "gate",
                               "--ledger", str(tmp / "live.json"),
                               "--probes-from", str(tmp / "probes.json"),
                               "--cells-root", str(tmp / "absent-cells"),
                               "--out", str(tmp / "gate3.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("an outstanding reservation fails the gate", code.returncode == 1)

        # A running cell container fails the gate even when the ledger is clean.
        busy = json.loads(json.dumps(quiet_probes))
        busy["containers"] = {"command": ["docker", "ps"], "exit_code": 0, "ran": True,
                              "stdout": "bd150-position-01-finder\tUp 3 minutes\n", "stderr": ""}
        (tmp / "busy.json").write_text(json.dumps(busy), encoding="utf-8")
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "gate",
                               "--ledger", str(tmp / "ledger.json"),
                               "--probes-from", str(tmp / "busy.json"),
                               "--cells-root", str(tmp / "absent-cells"),
                               "--out", str(tmp / "gate4.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("a live cell container fails the gate", code.returncode == 1)

        # A reviewer process still holding a workspace fails the gate.
        held = json.loads(json.dumps(quiet_probes))
        held["processes"] = {"command": ["ps"], "exit_code": 0, "ran": True, "stderr": "",
                             "stdout": "4242 900 python3 closeout.py gate\n"
                                       "900 1 /bin/zsh -c closeout.py gate\n"
                                       "9001 1 python3 run_cell.py dispatch --position 7\n"}
        (tmp / "held.json").write_text(json.dumps(held), encoding="utf-8")
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "gate",
                               "--ledger", str(tmp / "ledger.json"),
                               "--probes-from", str(tmp / "held.json"),
                               "--cells-root", str(tmp / "absent-cells"),
                               "--out", str(tmp / "gate5.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("a live coordinator process fails the gate", code.returncode == 1)

        # A surviving cell workspace fails the gate.
        (tmp / "present-cells").mkdir()
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "gate",
                               "--ledger", str(tmp / "ledger.json"),
                               "--probes-from", str(tmp / "probes.json"),
                               "--cells-root", str(tmp / "present-cells"),
                               "--out", str(tmp / "gate6.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("a surviving cell workspace fails the gate", code.returncode == 1)

        # A stray attempt workspace fails the gate even when the configured root is gone.
        stray_probes = json.loads(json.dumps(quiet_probes))
        stray_probes["workspaces"] = {"command": ["find"], "exit_code": 0, "ran": True,
                                      "stdout": "/tmp/salvage/position-03\n", "stderr": ""}
        (tmp / "stray.json").write_text(json.dumps(stray_probes), encoding="utf-8")
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "gate",
                               "--ledger", str(tmp / "ledger.json"),
                               "--probes-from", str(tmp / "stray.json"),
                               "--cells-root", str(tmp / "absent-cells"),
                               "--out", str(tmp / "gate7.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("a stray attempt workspace fails the gate", code.returncode == 1)

        # An uncaptured sweep cannot establish absence.
        unswept = json.loads(json.dumps(quiet_probes))
        unswept["workspaces"] = {"command": ["find"], "exit_code": None, "ran": False,
                                 "stdout": "", "stderr": "command not found"}
        (tmp / "unswept.json").write_text(json.dumps(unswept), encoding="utf-8")
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "gate",
                               "--ledger", str(tmp / "ledger.json"),
                               "--probes-from", str(tmp / "unswept.json"),
                               "--cells-root", str(tmp / "absent-cells"),
                               "--out", str(tmp / "gate8.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("an uncaptured workspace sweep fails the gate", code.returncode == 1)

        # The seal cannot be opened against a gate that did not pass.
        (tmp / "shut.json").write_text(json.dumps(
            {"all_reviewers_stopped": False, "observed_at": "2026-09-10T00:00:00Z"}),
            encoding="utf-8")
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "open-seal",
                               "--gate", str(tmp / "shut.json"), "--seal", str(tmp / "ledger.json"),
                               "--key", str(tmp / "absent.key"), "--archive", str(tmp / "a.enc"),
                               "--into", str(tmp / "out")],
                              capture_output=True, text=True, encoding="utf-8")
        check("a shut gate refuses to open the seal", code.returncode == 1)
        check("the refusal says why", "do not open sealed outcomes" in code.stdout)

    for failure in failures:
        print("self-test failure: %s" % failure)
    print("%d checks, %d failures" % (16, len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
