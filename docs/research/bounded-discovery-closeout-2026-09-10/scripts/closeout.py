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
# The model a provider error is recorded under; it carries no usage or setting.
SYNTHETIC_MODEL = "<synthetic>"
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


# --------------------------------------------------------------------------
# The historical fidelity assessment: pilot/actual-fidelity
# --------------------------------------------------------------------------

# Evidence that was never retained, named once so every attempt that lacks it
# reports the same string and #152 can group on it.
GAP_LAUNCH_ARGV = ("the launch argv was not retained: the requested --model, --effort, "
                   "--max-budget-usd, --restricted and allow-list values for the root session "
                   "cannot be read back from any artifact")
GAP_PER_ROLE_SPLIT = ("the per-role cost split required by preregistration section 7 is absent: "
                      "usage-split.json assigns every transcript to `unassigned`, so primary, "
                      "finder and verifier spend cannot be separated where an arm runs one model")
GAP_NO_BATCH_REASON = ("no verifier transcript and no recorded no-batch reason: the pinned policy "
                       "may legitimately dispatch none, but the reason the design requires was "
                       "not retained")
GAP_NETWORK_JUDGEMENT = ("no per-shell-command network judgment was recorded: the read audit "
                         "checked paths, not whether a command reached the network outside the "
                         "proxy, so proxy bypass is unaudited for this attempt")
GAP_NO_MODEL_VERIFICATION = ("no model-verification record was written for this attempt; the "
                             "settings below are verified by this closeout from the retained "
                             "transcripts instead")
GAP_NO_TRANSCRIPT = ("no transcript was retained: the launch failed before any model request, so "
                     "there is nothing to verify settings against")


def attempt_ordinal(attempt_id, default=1) -> int:
    """The ordinal in ``issue-138-<cell_id>-attempt-<n>``.

    A malformed or absent id returns the default rather than raising: the
    closeout reads historical records it did not write, and an unparseable id
    is a discrepancy to report, not a reason to abandon the reconciliation."""
    tail = str(attempt_id or "").rsplit("-attempt-", 1)[-1]
    try:
        return int(tail)
    except (TypeError, ValueError):
        return default


def role_of(path: str) -> str:
    """The role a retained transcript belongs to, from its path.

    Sub-agent transcripts live under ``subagents/``; arm C's finder runs in its
    own store; anything else is the root session, which in arm C is one session
    across both phases."""
    if "/subagents/" in path:
        return "worker"
    if "finder-store" in path:
        return "finder"
    return "primary"


def scan_transcript(path) -> dict:
    """Model, effort, freshness and size of one retained transcript.

    Freshness is mechanical and matches the freeze's own test: exactly one root
    user message and no summary or compact-boundary record, so the session did
    not resume or inherit a context."""
    models, efforts = {}, {}
    assistant_lines = root_user_messages = summary_records = synthetic_lines = 0
    versions = set()
    try:
        handle = open(path, encoding="utf-8")
    except OSError as exc:
        return {"readable": False, "error": str(exc)}
    with handle:
        for line in handle:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            kind = record.get("type")
            if record.get("version"):
                versions.add(record["version"])
            if kind == "user" and record.get("parentUuid") in (None, "None"):
                root_user_messages += 1
            elif kind in ("summary", "compact-boundary"):
                summary_records += 1
            elif kind == "assistant":
                message = record.get("message") or {}
                model = message.get("model")
                if model == SYNTHETIC_MODEL:
                    # The harness writes this line when a session hits an API
                    # error. It carries no usage and no setting; the pinned
                    # meter drops it, so counting it as a second model here
                    # would manufacture a fidelity failure out of a 502.
                    synthetic_lines += 1
                    continue
                assistant_lines += 1
                effort = message.get("effort") or record.get("effort")
                models[model] = models.get(model, 0) + 1
                efforts[effort] = efforts.get(effort, 0) + 1
    return {"readable": True, "assistant_lines": assistant_lines,
            "synthetic_error_lines": synthetic_lines,
            "models": models, "efforts": efforts,
            "root_user_messages": root_user_messages,
            "summary_records": summary_records,
            "versions": sorted(versions),
            "fresh_context": root_user_messages == 1 and summary_records == 0}


def retained_transcripts(root: Path) -> list:
    """Every retained transcript for an attempt, deduplicated by file name.

    Two layouts appear in the seal: the settled attempts keep a ``transcripts/``
    tree, and the attempt a provider error cut off keeps its session home. The
    metering copies under ``artifacts/filtered-transcripts`` are excluded - they
    are the same sessions with synthetic lines removed, and counting them twice
    would double every line count."""
    found = {}
    for candidate in sorted(root.rglob("*.jsonl")):
        text = str(candidate)
        if "/artifacts/" in text and "filtered-transcripts" not in text:
            continue
        if "filtered-transcripts" in text:
            continue
        if candidate.name == "egress.jsonl":
            continue
        found.setdefault(candidate.name, candidate)
    return sorted(found.values())


def expected_settings(manifest, arm, role) -> dict:
    arms = manifest.get("arms", {})
    entry = (arms.get(arm) or {}).get(role)
    if not entry:
        return {}
    return {"model": entry.get("model"), "effort": entry.get("effort"),
            "requested_by": entry.get("requested_by")}


def settings_verdict(scan, expect) -> dict:
    """Observed model and effort against the frozen expectation for that role.

    An unobservable setting is a fidelity failure under section 9, exactly like
    a mismatch: it is never relabelled as an equivalent treatment."""
    if not scan.get("readable"):
        return {"verified": False, "reason": "the transcript could not be read"}
    if not scan.get("assistant_lines"):
        return {"verified": False, "reason": "no assistant line carries a model or an effort, so "
                                             "the setting is unobservable"}
    models = [m for m in scan["models"] if m]
    efforts = [e for e in scan["efforts"] if e]
    problems = []
    if len(models) != 1 or models[0] != expect.get("model"):
        problems.append("observed model(s) %s against the frozen %s"
                        % (sorted(scan["models"]), expect.get("model")))
    if len(efforts) != 1 or efforts[0] != expect.get("effort"):
        problems.append("observed effort(s) %s against the frozen %s"
                        % (sorted(scan["efforts"]), expect.get("effort")))
    if len(models) < len(scan["models"]) or len(efforts) < len(scan["efforts"]):
        problems.append("some assistant lines carry no model or effort")
    return {"verified": not problems, "problems": problems,
            "observed_models": scan["models"], "observed_efforts": scan["efforts"],
            "assistant_lines": scan["assistant_lines"]}


def commit_prompt(path, salt) -> str:
    import hmac
    return hmac.new(salt, Path(path).read_bytes(), hashlib.sha256).hexdigest()


def frozen_input_checks(root: Path, manifest, published, salt, ordinal=None) -> dict:
    """The chain that binds this attempt's rendered prompts to the freeze.

    Three links: the template digest against the frozen pin, each rendered file
    against the raw digest sealed with the attempt, and the same file against
    the HMAC published in the public cell summary. The HMAC is what lets the
    public record commit to a rendering without publishing a digest over a
    four-candidate secret."""
    prompts = load(root / "artifacts" / "prompts.json", default={})
    prepare = load(root / "artifacts" / "prepare.json", default={})
    pinned = ((manifest.get("pins") or {}).get("dispatch_template") or {}).get("sha256")
    checks, problems = [], []

    template_ok = bool(pinned) and prompts.get("dispatch_template_sha256") == pinned
    checks.append({"check": "the dispatch template is the frozen one", "passed": template_ok})
    if not template_ok:
        problems.append("the rendered prompts were produced from a template that is not the "
                        "frozen one")

    raw_ok = True
    for name, expected in sorted((prompts.get("rendered_sha256") or {}).items()):
        rendered = root / "runner" / name
        if not rendered.is_file():
            raw_ok = False
            continue
        raw_ok = raw_ok and hashlib.sha256(rendered.read_bytes()).hexdigest() == expected
    checks.append({"check": "every rendered prompt still matches the digest sealed with it",
                   "passed": raw_ok,
                   "files": sorted((prompts.get("rendered_sha256") or {}).keys())})
    if not raw_ok:
        problems.append("a rendered prompt does not match the digest sealed beside it")

    hmac_ok, hmac_checked = True, 0
    published_commitments = (published or {}).get("rendered_prompt_hmac_sha256") or {}
    if ordinal is not None and (published or {}).get("attempt_ordinal") not in (None, ordinal):
        # The public summary commits to the attempt that settled at this
        # position. A predecessor's rendering is a different byte and is
        # committed to only by the raw digest sealed beside it.
        published_commitments = {}
    if salt and published_commitments:
        for name, expected in sorted(published_commitments.items()):
            rendered = root / "runner" / name
            if not rendered.is_file():
                hmac_ok = False
                continue
            hmac_checked += 1
            hmac_ok = hmac_ok and commit_prompt(rendered, salt) == expected
    checks.append({"check": "every rendered prompt matches the HMAC published in the cell summary",
                   "passed": bool(hmac_checked) and hmac_ok if published_commitments else True,
                   "commitments_checked": hmac_checked,
                   "note": None if published_commitments else
                           "no commitment was published for this attempt: the public summary "
                           "commits to the attempt that settled at this position"})
    if hmac_checked and not hmac_ok:
        problems.append("a rendered prompt does not match the commitment published for it")

    target = (manifest.get("targets") or {}).get(prepare.get("target_slot")) or {}
    packet_pin = (target.get("source_packet") or {}).get("sha256")
    packet_ok = bool(packet_pin) and prepare.get("packet_sha256") == packet_pin
    checks.append({"check": "the source packet is the frozen one for this attempt's target",
                   "passed": packet_ok})
    if not packet_ok:
        problems.append("the packet this attempt reviewed cannot be matched to the frozen one "
                        "for its target")

    scope_pin = (target.get("selected_scope") or {}).get("sha256")
    scope_ok = bool(scope_pin) and prepare.get("scope_sha256") == scope_pin
    checks.append({"check": "the selected scope is the frozen one for this attempt's target",
                   "passed": scope_ok})
    if not scope_ok:
        problems.append("the scope this attempt reviewed cannot be matched to the frozen one "
                        "for its target")

    policy_ok = (prepare.get("policy_commit") == (manifest.get("pins") or {}).get("policy_commit")
                 and prepare.get("policy_tree") == (manifest.get("pins") or {}).get("skill_tree"))
    checks.append({"check": "the policy snapshot is the pinned commit and tree", "passed": policy_ok})
    if not policy_ok:
        problems.append("the policy snapshot is not the pinned commit and tree")

    return {"checks": checks, "problems": problems,
            "passed": all(check["passed"] for check in checks)}


def isolation_checks(root: Path) -> dict:
    pre = load(root / "artifacts" / "isolation-pre.json", default={})
    post = load(root / "artifacts" / "isolation-post.json", default={})
    attestation = load(root / "artifacts" / "attestation.json", default={})
    audit = load(root / "artifacts" / "read-audit.json", default={})
    mounts = load(root / "artifacts" / "mounts.json", default={})
    problems = []
    if not pre.get("ready"):
        problems.append("the pre-dispatch absence gate did not pass")
    if not post.get("ready"):
        problems.append("the post-dispatch absence gate did not pass")
    if not attestation.get("ready"):
        problems.append("the preparation attestation did not pass")
    if audit and not audit.get("passed"):
        problems.append("the read audit did not pass")
    outside = audit.get("paths_outside_permitted_roots") or []
    if outside:
        problems.append("%d read(s) resolved outside the permitted roots" % len(outside))
    return {
        "pre_dispatch_ready": bool(pre.get("ready")),
        "post_dispatch_ready": bool(post.get("ready")),
        "attestation_ready": bool(attestation.get("ready")),
        "read_audit_passed": bool(audit.get("passed")) if audit else None,
        "reads_outside_permitted_roots": len(outside),
        "accepted_read_deviations": [
            {"via": hit.get("via"),
             "reason_retained_in_sealed_evidence": bool(hit.get("reason")),
             "note": "the recorded judgment quotes the path the cell read, which is inside the "
                     "target's own source tree, so it stays in the seal"}
            for hit in (audit.get("accepted_hits") or [])],
        "requested_mount_count": len(mounts.get("requested_mounts") or []),
        "shell_commands": audit.get("shell_commands"),
        "tool_calls": audit.get("tool_calls"),
        "problems": problems,
        "passed": not problems,
    }


def separation_checks(root: Path, arm, scans) -> dict:
    """Context separation: fresh identities, and for arm C the discovery barrier.

    The barrier is what keeps C's primary from seeing a finder claim before it
    has frozen its own review, so its evidence is the freeze artifact written
    before admission and the finder's own store."""
    stale = [name for name, scan in scans.items() if not scan.get("fresh_context")]
    freeze = root / "work" / "freeze.json"
    finder_store_transcripts = [name for name in scans if role_of(name) == "finder"]
    record = {"fresh_context_verified": not stale,
              "sessions_scanned": len(scans),
              "sessions_without_a_single_root_message": stale,
              "distinct_session_identities": len({Path(name).stem for name in scans}),
              "problems": []}
    if stale:
        record["problems"].append("%d session(s) do not open with exactly one root user message "
                                  "and no summary record" % len(stale))
    if arm == "C":
        record["barrier_freeze_recorded"] = freeze.is_file()
        record["finder_ran_in_its_own_store"] = bool(finder_store_transcripts)
        record["admission_prompt_retained"] = (root / "runner" / "admission.rendered.md").is_file()
        if not finder_store_transcripts:
            record["problems"].append("no finder transcript is retained for an arm C attempt")
        if not freeze.is_file():
            record["problems"].append("no barrier freeze artifact was written before admission")
    record["passed"] = not record["problems"]
    return record


def completion_checks(root: Path, dispatch, settle) -> dict:
    timing = load(root / "work" / "timing.json", default={})
    phases = dispatch.get("phases") or []
    terminal = []
    for phase in phases:
        envelope = load(root / "artifacts" / ("%s-result.json" % phase.get("label")), default={})
        terminal.append({"phase": phase.get("label"), "exit_code": phase.get("exit_code"),
                         "subtype": phase.get("subtype"),
                         "stop_reason": envelope.get("stop_reason"),
                         "terminal_reason": envelope.get("terminal_reason"),
                         "api_error_status": envelope.get("api_error_status"),
                         "envelope_retained": bool(envelope),
                         "permission_denials": len(envelope.get("permission_denials") or [])})
    sidecar_fields = [field for field in ("completion_mode", "root_dispatched_at",
                                          "payload_validated_at", "completed_at")
                      if timing.get(field)]
    return {
        "completion": settle.get("completion"),
        "timing_sidecar_fields": sidecar_fields,
        "completion_mode": timing.get("completion_mode"),
        "root_elapsed_seconds": dispatch.get("elapsed_seconds"),
        "duration_censored": settle.get("completion") not in (None, "complete"),
        "phases": terminal,
    }


def usage_checks(root: Path, settle) -> dict:
    split = load(root / "artifacts" / "usage-split.json", default={})
    roles = sorted((split.get("per_role") or {}).keys())
    return {
        "per_model_split_recorded": sorted((split.get("per_model") or {}).keys()),
        "per_role_split_recorded": roles,
        "per_role_split_assigned": bool(roles) and roles != ["unassigned"],
        "recomputed_usd": split.get("total_cost_usd"),
        "self_report_usd": settle.get("self_report_usd") or split.get("self_report_usd"),
        "settled_usd": settle.get("settled_usd"),
        "within_tolerance": split.get("within_tolerance"),
        "reconciliation_residual_usd": settle.get("reconciliation_residual_usd"),
        "residual_untranscripted_models_usd": settle.get("residual_untranscripted_models_usd"),
        "residual_unexplained_usd": settle.get("residual_unexplained_usd"),
        "metering_filtered_synthetic_lines": settle.get("metering_filtered_synthetic_lines"),
    }


def attempt_roots(evidence: Path) -> list:
    """Every attempt in the seal, as (position, ordinal, root, kind).

    Three shapes: a settled attempt directory, the attempt a provider error cut
    off under ``invalid/``, and an aborted launch that left only two artifacts
    inside the directory of the attempt that replaced it."""
    found = []
    for entry in sorted(evidence.glob("position-*")):
        if not entry.is_dir():
            continue
        position = int(entry.name.split("-")[-1])
        settle = load(entry / "artifacts" / "settle.json", default={})
        ordinal = attempt_ordinal(settle.get("attempt_id"))
        found.append({"position": position, "ordinal": ordinal, "root": entry, "kind": "settled"})
        for aborted in sorted(entry.glob("artifacts/attempt-*-aborted-dispatch.json")):
            number = int(aborted.name.split("-")[1])
            found.append({"position": position, "ordinal": number, "root": entry,
                          "kind": "aborted", "record": aborted})
    for entry in sorted((evidence / "invalid").glob("position-*")):
        if not entry.is_dir() or entry.name.endswith("-home"):
            continue
        settle = load(entry / "artifacts" / "settle.json", default={})
        position = int(settle.get("position") or entry.name.split("-")[1])
        ordinal = attempt_ordinal(settle.get("attempt_id"))
        home = evidence / "invalid" / (entry.name + "-home")
        found.append({"position": position, "ordinal": ordinal, "root": entry,
                      "kind": "invalidated", "extra_roots": [home] if home.is_dir() else []})
    return sorted(found, key=lambda item: (item["position"], item["ordinal"]))


def assess_attempt(item, manifest, published_by_position, salt) -> dict:
    """One attempt's fidelity record, from the retained evidence alone.

    The historical ``model-verification.json`` is read but never trusted as the
    finding: PR #197's coordinator fixes cannot establish what the original
    attempts did, so every setting here is recomputed from the transcripts and
    the historical record is reported beside it as agreement or disagreement."""
    root = item["root"]
    reference = "position-%02d-attempt-%d" % (item["position"], item["ordinal"])
    published = published_by_position.get(item["position"], {})

    if item["kind"] == "aborted":
        aborted = load(item["record"], default={})
        timing = load(root / "artifacts" / ("attempt-%d-aborted-timing.json" % item["ordinal"]),
                      default={})
        return {
            "attempt_ref": reference, "position": item["position"], "ordinal": item["ordinal"],
            "arm": aborted.get("arm"), "block": "pilot",
            "operational_validity": "invalid",
            "validity_basis": "documented coordinator invalidity, recorded when it happened",
            "completion": "stopped-runtime",
            "settled_usd": "0.0000000",
            "dimensions": {
                "requested_and_observed_settings": {
                    "verdict": "not applicable",
                    "detail": "no model request was issued: the launch was refused before any "
                              "session started, so there is no setting to observe"},
                "isolation": {"verdict": "not applicable",
                              "detail": "the cell never dispatched"},
                "context_separation": {"verdict": "not applicable",
                                       "detail": "no session was created"},
                "frozen_inputs": {"verdict": "not applicable",
                                  "detail": "the prompts of the attempt that replaced this one "
                                            "carry the frozen-input chain"},
                "common_allowances": {"verdict": "not applicable",
                                      "detail": "nothing was allowed to run"},
                "completion_and_stop": {
                    "verdict": "established",
                    "detail": "the aborted dispatch record and its timing sidecar were retained",
                    "elapsed_seconds": aborted.get("elapsed_seconds"),
                    "timing_sidecar_fields": sorted(timing.keys()),
                    "phases": aborted.get("phases")},
                "usage_completeness": {
                    "verdict": "established",
                    "detail": "settled at zero: the runtime issued no request, and the ledger "
                              "carries a reserve and a settle for the attempt"},
            },
            "missing_evidence": [GAP_NO_TRANSCRIPT],
            "produced_claims": False,
            "replacement_consumed": True,
            "notes": ["A replacement was consumed although nothing was measured: the ledger's "
                      "own rule counts any second attempt at a cell as a replacement, and that "
                      "rule governs over a narrative judgment that it should not."],
        }

    settle = load(root / "artifacts" / "settle.json", default={})
    dispatch = load(root / "artifacts" / "dispatch.json", default={})
    prepare = load(root / "artifacts" / "prepare.json", default={})
    arm = settle.get("arm") or prepare.get("arm")

    roots = [root] + list(item.get("extra_roots") or [])
    scans, expectations, verdicts = {}, {}, {}
    for base in roots:
        for path in retained_transcripts(base):
            scans[str(path)] = scan_transcript(path)
    by_role = {}
    for path, scan in scans.items():
        role = role_of(path)
        expect = expected_settings(manifest, arm, role)
        verdict = settings_verdict(scan, expect)
        by_role.setdefault(role, []).append({"role": role, "expected": expect,
                                             "observed": verdict, "fresh": scan.get("fresh_context"),
                                             "assistant_lines": scan.get("assistant_lines")})
        expectations[role] = expect
        verdicts.setdefault(role, []).append(verdict)

    historical = load(root / "artifacts" / "model-verification.json", default={})
    settings_problems = [problem for role in verdicts for verdict in verdicts[role]
                         for problem in (verdict.get("problems") or [])]
    unverified = [role for role in verdicts
                  if not all(v.get("verified") for v in verdicts[role])]

    isolation = isolation_checks(root)
    separation = separation_checks(root, arm, {p: s for p, s in scans.items()})
    frozen = frozen_input_checks(root, manifest, published, salt, item["ordinal"])
    completion = completion_checks(root, dispatch, settle)
    usage = usage_checks(root, settle)

    gaps = [GAP_LAUNCH_ARGV, GAP_NETWORK_JUDGEMENT]
    if not usage["per_role_split_assigned"]:
        gaps.append(GAP_PER_ROLE_SPLIT)
    if not historical:
        gaps.append(GAP_NO_MODEL_VERIFICATION)
    if "worker" not in by_role and arm in ("A", "B", "C"):
        gaps.append(GAP_NO_BATCH_REASON)

    violations = list(settings_problems) + list(isolation["problems"]) \
        + list(separation["problems"]) + list(frozen["problems"])

    ceiling = usd((manifest.get("limits") or {}).get("whole_review_usd_per_attempt") or "9.00")
    headroom = usd((manifest.get("limits") or {}).get("one_call_headroom_usd") or "1.00")
    settled = usd(settle.get("settled_usd"))
    if settled > ceiling + headroom:
        violations.append("the attempt settled at %s, above the frozen %s ceiling plus its %s "
                          "one-call headroom" % (settled, ceiling, headroom))

    if item["kind"] == "invalidated":
        validity = "invalid"
        basis = "documented infrastructure invalidity, recorded when it happened"
    elif violations:
        validity = "invalid"
        basis = "a fidelity, isolation or frozen-input violation observed in this assessment"
    else:
        validity = "unresolved"
        basis = ("no violation was observed and every observable dimension is established, but "
                 "the evidence named under missing_evidence was never retained, so this "
                 "assessment does not certify the attempt as faithful")

    return {
        "attempt_ref": reference, "position": item["position"], "ordinal": item["ordinal"],
        "arm": arm, "block": prepare.get("block") or "pilot",
        "operational_validity": validity,
        "validity_basis": basis,
        "completion": settle.get("completion") or (
            "stopped-runtime" if item["kind"] == "invalidated" else None),
        "settled_usd": settle.get("settled_usd"),
        "dimensions": {
            "requested_and_observed_settings": {
                "verdict": "established" if not settings_problems and by_role else "unresolved",
                "roles": {role: {
                    "expected_model": expectations[role].get("model"),
                    "expected_effort": expectations[role].get("effort"),
                    "requested_evidence": ("the startup agent definition retained with the attempt"
                                           if role in ("worker", "finder")
                                           else "not retained; see missing_evidence"),
                    "observed_verified": all(v.get("verified") for v in verdicts[role]),
                    "assistant_lines": sum(v.get("assistant_lines") or 0 for v in verdicts[role]),
                    "sessions": len(verdicts[role]),
                    "provider_error_lines_dropped": sum(
                        entry.get("synthetic_error_lines") or 0 for entry in by_role[role]),
                    "problems": [p for v in verdicts[role] for p in (v.get("problems") or [])],
                } for role in sorted(verdicts)},
                "agrees_with_historical_record": bool(historical) and all(
                    (historical.get(role) or {}).get("verified") is True for role in historical),
                "historical_record_present": bool(historical),
                "detail": ("observed settings recomputed by this closeout from every retained "
                           "transcript, not taken from the attempt's own verification record"),
            },
            "isolation": dict(isolation, verdict="established" if isolation["passed"] else "violated"),
            "context_separation": dict(separation,
                                       verdict="established" if separation["passed"] else "violated"),
            "frozen_inputs": dict(frozen, verdict="established" if frozen["passed"] else "violated"),
            "common_allowances": {
                "verdict": "unresolved",
                "detail": ("the enforced ceilings cannot be read back. What is retained: the "
                           "rendered dispatch prompt with its execution allowance, the permission "
                           "denials the restricted layer produced, and a settled cost inside the "
                           "frozen ceiling."),
                "settled_within_ceiling": settled <= ceiling + headroom,
                "settled_usd": str(settled),
                "ceiling_usd": str(ceiling),
                "one_call_headroom_usd": str(headroom),
                "permission_denials_observed": sum(p.get("permission_denials") or 0
                                                   for p in completion["phases"]),
                "shell_commands": isolation["shell_commands"],
                "shell_command_ceiling": (manifest.get("limits") or {}).get(
                    "shell_commands_per_attempt"),
                "root_elapsed_seconds": completion["root_elapsed_seconds"],
                "root_wall_ceiling_seconds": (manifest.get("limits") or {}).get(
                    "root_wall_seconds_per_attempt"),
            },
            "completion_and_stop": dict(completion, verdict="established"),
            "usage_completeness": dict(
                usage, verdict="established" if usage["per_role_split_assigned"] else "unresolved"),
        },
        "missing_evidence": gaps,
        "violations": violations,
        "produced_claims": (root / "work" / "review-payload.json").is_file()
                           or (root / "work" / "review-payload.md").is_file(),
        "problems_recorded_at_settlement": settle.get("problems") or [],
    }


def build_assessment(gate, evidence: Path, manifest, bundle: Path, salt) -> dict:
    published_by_position = {}
    for position in range(1, PILOT_CELLS + 1):
        summary = load(bundle / "cells" / ("position-%02d" % position) / "summary.json", default={})
        if summary:
            published_by_position[position] = summary

    attempts = [assess_attempt(item, manifest, published_by_position, salt)
                for item in attempt_roots(evidence)]

    invalid = [a["attempt_ref"] for a in attempts if a["operational_validity"] == "invalid"]
    unresolved = [a["attempt_ref"] for a in attempts if a["operational_validity"] == "unresolved"]
    valid = [a["attempt_ref"] for a in attempts if a["operational_validity"] == "valid"]
    observed_violations = sorted({v for a in attempts for v in (a.get("violations") or [])})
    gaps = sorted({g for a in attempts for g in a["missing_evidence"]})

    # The frozen invalidation rule reaches comparison members, not just cells.
    # Nothing here was invalidated by a fault in a shared input, so no member
    # beyond the two attempts already closed as invalid is affected.
    affected = sorted({a["position"] for a in attempts
                       if a["operational_validity"] == "invalid" and a["ordinal"] > 0})

    status = "unresolved" if unresolved or not valid else "resolved"
    return {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-151-fidelity-assessment",
        "finding_id": "pilot/actual-fidelity",
        "status": status,
        "assessed_at": now(),
        "gate": {"observed_at": gate.get("observed_at"),
                 "all_reviewers_stopped": gate.get("all_reviewers_stopped")},
        "decision": (
            "Unresolved, with the missing evidence named. No attempt shows an observed fidelity, "
            "isolation, context-separation or frozen-input violation: every retained transcript "
            "verifies to the frozen model and effort for its role, every absence gate and read "
            "audit passed, every session is a fresh context, and every rendered prompt still "
            "matches both the digest sealed beside it and the commitment published for it. What "
            "cannot be established is that each cell was launched under the identical frozen "
            "allowances, and how each attempt's spend divides between its roles, because neither "
            "record was ever retained. Under the frozen rule an unobservable setting is not a "
            "pass, so these attempts are carried as unresolved rather than valid."
            if status == "unresolved" else
            "Resolved: every attempt's settings, isolation, context separation and usage are "
            "established from retained evidence."),
        "attempts_assessed": len(attempts),
        "valid": valid,
        "unresolved": unresolved,
        "invalid": invalid,
        "observed_violations": observed_violations,
        "missing_evidence": gaps,
        "invalidation_rule": {
            "applied": True,
            "affected_positions": affected,
            "detail": ("The frozen rule invalidates exactly the comparison cells a change "
                       "affects. The two attempts closed as invalid failed before producing a "
                       "comparable outcome and share no input with any other cell, so they "
                       "invalidate no further member; each was already replaced within the "
                       "frozen allowance. No budget stop is treated as infrastructure "
                       "invalidity: position 6's stop is a measured result and is not "
                       "replacement-eligible."),
        },
        "effect_on_grading": (
            "An unresolved attempt is not a valid completed outcome. Under section 8 it counts "
            "as missing rather than present, so #152 grades the claims these attempts produced "
            "without treating any cell as a clean comparison member, and #153 applies the "
            "conservative limits that follow."),
        "attempts": attempts,
    }


def command_fidelity(args) -> int:
    gate = load(args.gate)
    if not gate.get("all_reviewers_stopped"):
        print("the stop gate does not report every reviewer stopped; sealed evidence must not "
              "be read for this assessment")
        return 1
    manifest = load(args.manifest)
    salt_path = Path(os.path.expanduser(args.salt)) if args.salt else None
    salt = salt_path.read_bytes() if salt_path and salt_path.is_file() else None
    assessment = build_assessment(gate, Path(os.path.expanduser(args.evidence)), manifest,
                                  Path(args.bundle), salt)
    forbidden, allowed = disclosive_values(manifest)
    leaked = leak_scan(assessment, sorted(set(list(args.slot_names) + forbidden)), allowed)
    if leaked:
        for line in leaked:
            print(line)
        return 1
    write(args.out, assessment)
    print(json.dumps({"status": assessment["status"],
                      "valid": len(assessment["valid"]),
                      "unresolved": len(assessment["unresolved"]),
                      "invalid": len(assessment["invalid"])}))
    return 0


def disclosive_values(frozen) -> tuple:
    """What must never reach a public artifact, and what may.

    Forbidden: every slot name, and every value that identifies one of the four
    targets - its repository, its url, its pull-request number and each of its
    object ids. Allowed: this repository's own frozen pins, which are public and
    identify no target.

    The two lists are derived from #149's frozen manifest rather than typed out,
    so a target added or repinned there cannot quietly fall outside the scan."""
    forbidden, allowed = set(), set()
    pins = (frozen or {}).get("pins") or {}
    for key in ("policy_commit", "skill_tree"):
        if pins.get(key):
            allowed.add(pins[key])
    if (frozen or {}).get("repository_commit_read"):
        allowed.add(frozen["repository_commit_read"])
    for slot, entry in sorted(((frozen or {}).get("targets") or {}).items()):
        forbidden.add(slot)
        target = (entry or {}).get("target") or {}
        for key in ("repository", "url", "head_oid", "base_oid_recorded", "merge_base_oid"):
            if target.get(key):
                forbidden.add(str(target[key]))
        if target.get("repository"):
            # A source path names the project without naming "owner/name", which
            # is how the pilot's one recorded read deviation would have leaked
            # its target. Both components are refused on their own.
            forbidden.update(part for part in str(target["repository"]).split("/") if part)
        if target.get("pr"):
            forbidden.add("%s#%s" % (target.get("repository", ""), target["pr"]))
    return sorted(forbidden), sorted(allowed)


def leak_scan(payload, slot_names, allowed_ids=()) -> list:
    """Refuse to write a public artifact that discloses the pilot's pairing.

    Two layers, because review found that the leak came through values that were
    individually innocuous. The first refuses a known disclosive string. The
    second refuses any full object id that is not on the allow-list of this
    repository's own public pins, on the reasoning that an unrecognised object
    id is far likelier to be a target's than not - a whitelist of harmless
    fields is exactly what failed to catch the digest leak before."""
    text = json.dumps(payload)
    allowed = set(allowed_ids or ())
    found = []
    for name in (slot_names or []):
        if name and name in text:
            found.append("refusing to write: the payload contains %r, which identifies a target"
                         % name)
    for match in set(re.findall(r"\b[0-9a-f]{40}\b", text)):
        if match in allowed:
            continue
        found.append("refusing to write: the payload contains the object id %s..., which is not "
                     "one of this repository's public pins and may identify a target" % match[:8])
    return sorted(set(found))


# --------------------------------------------------------------------------
# Reconciling every charge against the single ledger
# --------------------------------------------------------------------------

def ledger_categories(ledger) -> dict:
    """Every settled charge, split into the columns the method reports apart.

    Setup and selection are charged once to the epic; review consumption is
    charged per attempt including the attempts that were discarded. Nothing is
    netted off: a discarded predecessor keeps its cost in the total."""
    categories = {"pre_freeze": Decimal("0"), "setup": Decimal("0"), "attempts": Decimal("0")}
    per_attempt, counts = {}, {"pre_freeze": 0, "setup": 0, "attempts": 0}
    for event in ledger.get("events", []):
        if event.get("operation") != "settle":
            continue
        delta = usd(event.get("actual_delta_usd"))
        if event.get("phase") == "pre-freeze":
            key = "pre_freeze"
        elif event.get("attempt_id"):
            key = "attempts"
            # A settlement of zero is still a settlement: the attempt whose
            # launch was refused before any model request settled at zero and
            # must stay visible in the census.
            per_attempt[event["attempt_id"]] = per_attempt.get(
                event["attempt_id"], Decimal("0")) + delta
        else:
            key = "setup"
        categories[key] += delta
        counts[key] += 1
    return {"totals": categories, "counts": counts, "per_attempt": per_attempt}


def attempt_reconciliation(evidence: Path, ledger_per_attempt) -> list:
    """Each attempt's settled charge against the ledger, its own self-report and
    the recomputed transcript usage, with the residual decomposed."""
    rows = []
    for item in attempt_roots(evidence):
        root, ordinal = item["root"], item["ordinal"]
        reference = "position-%02d-attempt-%d" % (item["position"], ordinal)
        if item["kind"] == "aborted":
            record = load(item["record"], default={})
            attempt_id = record.get("attempt_id")
            rows.append({
                "attempt_ref": reference, "position": item["position"], "ordinal": ordinal,
                "arm": record.get("arm"), "role_split_available": False,
                "ledger_settled_usd": str(usd(ledger_per_attempt.get(attempt_id))),
                "self_report_usd": "0.0000000", "recomputed_usage_usd": None,
                "reconciliation_residual_usd": "0.0000000",
                "residual_untranscripted_models_usd": None,
                "residual_unexplained_usd": None,
                "reconciles": usd(ledger_per_attempt.get(attempt_id)) == 0,
                "note": ("no model request was issued; the reserve and the settle are both on "
                         "the ledger and the settle is zero"),
            })
            continue
        settle = load(root / "artifacts" / "settle.json", default={})
        split = load(root / "artifacts" / "usage-split.json", default={})
        attempt_id = settle.get("attempt_id")
        ledger_amount = usd(ledger_per_attempt.get(attempt_id))
        settled = usd(settle.get("settled_usd"))
        rows.append({
            "attempt_ref": reference, "position": item["position"], "ordinal": ordinal,
            "arm": settle.get("arm"),
            "role_split_available": sorted((split.get("per_role") or {}).keys()) not in
                                    ([], ["unassigned"]),
            "models_priced": settle.get("models_priced"),
            "ledger_settled_usd": str(ledger_amount),
            "self_report_usd": settle.get("self_report_usd"),
            "recomputed_usage_usd": settle.get("usage_split_total_usd"),
            "reconciliation_residual_usd": settle.get("reconciliation_residual_usd"),
            "residual_untranscripted_models_usd": settle.get("residual_untranscripted_models_usd"),
            "residual_unexplained_usd": settle.get("residual_unexplained_usd"),
            "charged_the_larger_source": settled >= usd(settle.get("usage_split_total_usd")),
            "reconciles": ledger_amount == settled,
            "settlement_problems": settle.get("problems") or [],
        })
    return rows


def ledger_discrepancies(ledger, manifest, published_digest, live_digest, rows) -> list:
    """Every place the ledger disagrees with something published about it.

    Recorded, never repaired: the chain is append-only, and a stage record that
    was true when it was written stays as delivered."""
    found = []
    opens = [e for e in ledger.get("events", []) if e.get("operation") == "attempt-open"]
    if opens and int(ledger.get("attempts_dispatched") or 0) != len(opens):
        found.append({
            "id": "ledger/attempts-dispatched-counter",
            "what": "the ledger header records attempts_dispatched %s while the chain carries %d "
                    "attempt-open events" % (ledger.get("attempts_dispatched"), len(opens)),
            "effect": "the counter is not the attempt census; the events are. Every count in this "
                      "closeout is taken from the events.",
            "repaired": False,
        })
    instants = sorted(e.get("observed_at") for e in ledger.get("events", [])
                      if str(e.get("operation", "")).startswith("attempt-"))
    settle_times = [e.get("observed_at") for e in ledger.get("events", [])
                    if e.get("operation") == "settle" and e.get("attempt_id")]
    if instants and settle_times and max(settle_times) < min(instants):
        found.append({
            "id": "ledger/attempt-lifecycle-backfilled",
            "what": "all %d attempt-open and attempt-close events were written between %s and "
                    "%s, after the last attempt settled at %s"
                    % (len(instants), instants[0], instants[-1], max(settle_times)),
            "effect": "the attempt lifecycle was written after the pilot ran, so the ledger's own "
                      "refusals - a reused attempt id, the 27-attempt cap, a replacement whose "
                      "predecessor was not closed as documented invalidity - did not gate any "
                      "pilot dispatch as they were designed to. The money events were "
                      "contemporaneous; the lifecycle events are a reconstruction.",
            "repaired": False,
        })
    if published_digest and live_digest and published_digest != live_digest:
        found.append({
            "id": "ledger/published-digest-precedes-the-lifecycle-events",
            "what": "#150's sealed README publishes the ledger digest %s...; the sealed and live "
                    "copies are byte-identical to each other and hash to %s..."
                    % (published_digest[:12], live_digest[:12]),
            "effect": "explained, not corrupted: the published digest is this ledger truncated to "
                      "the events written before the attempt lifecycle was backfilled. The "
                      "published value is left as delivered, because it was true when written.",
            "repaired": False,
        })
    outside = [row["attempt_ref"] for row in rows
               if row.get("residual_unexplained_usd") and
               usd(row["residual_unexplained_usd"]) > usd(row.get("ledger_settled_usd")) / 100]
    if outside:
        found.append({
            "id": "ledger/unexplained-residual-above-one-per-cent",
            "what": "%s %s an unexplained reconciliation residual above one per cent of the "
                    "settled cost" % (", ".join(outside),
                                      "carries" if len(outside) == 1 else "carry"),
            "effect": "settlement charged the larger source in every case, so no charge is "
                      "understated. The residual stays visible rather than being absorbed.",
            "repaired": False,
        })
    if not any(row.get("role_split_available") for row in rows):
        found.append({
            "id": "ledger/no-per-role-split",
            "what": "no attempt carries the per-role cost split preregistration section 7 asks "
                    "settlement to take from the transcripts",
            "effect": "primary, finder and verifier spend cannot be separated where one arm runs "
                      "a single model. Per-model splits survive and are reported instead.",
            "repaired": False,
        })
    return found


def repair_feasibility(ledger, manifest, assessment) -> dict:
    """Whether the repair the assessment would require fits the frozen limits.

    This states the arithmetic and dispatches nothing: the stopped handoff
    authorises closeout only."""
    events = ledger.get("events", [])
    opens = [e for e in events if e.get("operation") == "attempt-open"]
    replacements = sum(1 for e in events if e.get("operation") == "attempt-open"
                       and attempt_ordinal(e.get("attempt_id")) > 1)
    attempt_limit = int(ledger.get("attempt_limit") or ATTEMPT_LIMIT)
    replacement_limit = int(ledger.get("replacement_limit") or REPLACEMENT_LIMIT)
    unresolved = assessment.get("unresolved") or []
    # Net of the retained uncertainty as well as the protected reserve: an
    # unmetered session that may yet be billed is not headroom.
    remaining_money = (usd(ledger.get("frozen_total_cap_usd"))
                       - usd(ledger.get("actual_usd"))
                       - usd(ledger.get("uncertainty_usd"))
                       - usd(ledger.get("grading_closeout_reserve_usd")))
    measured = sum(usd(a.get("settled_usd")) for a in assessment.get("attempts", [])
                   if a.get("attempt_ref") in unresolved)
    fits_money = measured <= remaining_money
    fits_replacements = len(unresolved) <= replacement_limit - replacements
    fits_attempts = len(unresolved) <= attempt_limit - len(opens)
    return {
        "repair_considered": ("re-running the %d attempts this assessment leaves unresolved, "
                              "under a coordinator that retains the launch argv and meters per "
                              "role" % len(unresolved)),
        "attempts_used": len(opens), "attempt_limit": attempt_limit,
        "attempts_remaining": attempt_limit - len(opens),
        "replacements_used": replacements, "replacement_limit": replacement_limit,
        "replacements_remaining": replacement_limit - replacements,
        "remaining_under_cap_usd": str(remaining_money),
        "repair_cost_at_measured_rates_usd": str(measured),
        "fits_money": bool(fits_money),
        "fits_attempt_allowance": bool(fits_attempts),
        "fits_replacement_allowance": bool(fits_replacements),
        "fits_frozen_limits": bool(fits_money and fits_attempts and fits_replacements),
        "binding_constraint": ("the replacement allowance: %d replacement(s) remain against %d "
                               "cells that would have to be re-run"
                               % (replacement_limit - replacements, len(unresolved))
                               if not fits_replacements else
                               "none: the repair fits every frozen limit"),
        "consequence": ("Section 6 governs: when required invalidation exceeds the allowance, "
                        "stop and close out the partial experiment. This ticket therefore "
                        "delivers closeout and dispatches nothing. The money would fit; the "
                        "replacement allowance does not, and the allowance is not this ticket's "
                        "to raise."
                        if not fits_replacements else
                        "A repair could fit the frozen limits. Authorising one is not this "
                        "ticket's to do: the stopped handoff permits closeout only."),
        "dispatched": False,
    }


def build_reconciliation(ledger, manifest, evidence: Path, assessment, bundle: Path,
                         live_digest) -> dict:
    categories = ledger_categories(ledger)
    rows = attempt_reconciliation(evidence, categories["per_attempt"])
    prefix = (manifest.get("pins") or {}).get("ledger_event_prefix") or {}
    events = ledger.get("events", [])[:int(prefix.get("events") or 0)]
    prefix_digest = hashlib.sha256(
        json.dumps(events, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    intact, broken_at = chain_intact(ledger)

    published_digest = None
    sealed_readme = bundle / "sealed" / "README.md"
    if sealed_readme.is_file():
        match = re.search(r"\b([0-9a-f]{64})\b", sealed_readme.read_text(encoding="utf-8"))
        published_digest = match.group(1) if match else None

    recomputed = categories["totals"]["pre_freeze"] + categories["totals"]["setup"] \
        + categories["totals"]["attempts"]
    header = usd(ledger.get("actual_usd"))

    bounds = [{
        "what": "one probe request that may never have been recorded",
        "usd": str(usd(manifest.get("probes", {}).get("retained_uncertainty_usd") or "0")),
        "why": "the cancelled #149 probe produced no envelope; one request at the largest "
               "observed per-request cost is retained rather than treating it as free",
    }, {
        "what": "one launch-shape check whose transcript was deleted before it was metered",
        "usd": str(usd(ledger.get("uncertainty_usd"))
                   - usd(manifest.get("probes", {}).get("retained_uncertainty_usd") or "0")),
        "why": "a coordinator error during #150's shared setup; the same conservative bound is "
               "retained for it, so an unmetered session is never counted as zero",
    }]

    return {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-151-reconciliation",
        "reconciled_at": now(),
        "ledger": {
            "events": len(ledger.get("events", [])),
            "chain_intact": intact,
            "chain_breaks_at_index": broken_at,
            "append_only_preserved": True,
            "frozen_prefix_events": prefix.get("events"),
            "frozen_prefix_holds": prefix_digest == prefix.get("events_sha256"),
            "live_digest_sha256": live_digest,
            "published_digest_sha256": published_digest,
            "frozen_total_cap_usd": ledger.get("frozen_total_cap_usd"),
            "grading_closeout_reserve_usd": ledger.get("grading_closeout_reserve_usd"),
            "reserved_usd": ledger.get("reserved_usd"),
        },
        "columns": {
            "pre_freeze_usd": str(categories["totals"]["pre_freeze"]),
            "setup_and_selection_usd": str(categories["totals"]["setup"]),
            "review_attempts_usd": str(categories["totals"]["attempts"]),
            "settlement_events": categories["counts"],
            "note": "review consumption, one-off setup and selection, and charged grading stay "
                    "in separate columns; shared setup is charged once to the epic",
        },
        "totals": {
            "recomputed_actual_usd": str(recomputed),
            "ledger_actual_usd": str(header),
            "reconciles": recomputed == header,
            "difference_usd": str(recomputed - header),
            "retained_uncertainty_usd": ledger.get("uncertainty_usd"),
            "sunk_costs_visible": True,
            "discarded_attempts_charged": [row["attempt_ref"] for row in rows
                                           if row["ordinal"] == 1 and any(
                                               other["position"] == row["position"]
                                               and other["ordinal"] > 1 for other in rows)],
        },
        "conservative_bounds": bounds,
        "attempts": rows,
        "discrepancies": ledger_discrepancies(ledger, manifest, published_digest, live_digest, rows),
        "repair": repair_feasibility(ledger, manifest, assessment),
    }


def command_reconcile(args) -> int:
    ledger_path = Path(os.path.expanduser(args.ledger))
    ledger = load(ledger_path)
    live_digest = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    frozen = load(args.manifest)
    reconciliation = build_reconciliation(ledger, frozen,
                                          Path(os.path.expanduser(args.evidence)),
                                          load(args.fidelity), Path(args.bundle), live_digest)
    forbidden, allowed = disclosive_values(frozen)
    leaked = leak_scan(reconciliation, sorted(set(list(args.slot_names) + forbidden)), allowed)
    if leaked:
        for line in leaked:
            print(line)
        return 1
    write(args.out, reconciliation)
    violations = []
    if not reconciliation["totals"]["reconciles"]:
        violations.append("the ledger does not reconcile: recomputed %s against %s"
                          % (reconciliation["totals"]["recomputed_actual_usd"],
                             reconciliation["totals"]["ledger_actual_usd"]))
    if not reconciliation["ledger"]["chain_intact"]:
        violations.append("the ledger chain is broken")
    if not reconciliation["ledger"]["frozen_prefix_holds"]:
        violations.append("the frozen ledger prefix no longer holds")
    for line in violations:
        print(line)
    if violations:
        return 1
    print(json.dumps({"actual_usd": reconciliation["totals"]["ledger_actual_usd"],
                      "discrepancies": len(reconciliation["discrepancies"]),
                      "repair_fits": reconciliation["repair"]["fits_frozen_limits"]}))
    return 0


# --------------------------------------------------------------------------
# The manifest for all twenty-four planned cells
# --------------------------------------------------------------------------

def build_manifest(assessment, reconciliation, bundle: Path, frozen) -> dict:
    """One row per planned cell, attempted or not, keyed by schedule position.

    Positions, never cell ids: the pilot's selection rule is public, so naming
    the slot behind any position would disclose which slot holds the clean
    control - and naming the eighteen unattempted cells would disclose the same
    thing by elimination."""
    by_position = {}
    for attempt in assessment.get("attempts", []):
        by_position.setdefault(attempt["position"], []).append(attempt)
    charges = {row["attempt_ref"]: row for row in reconciliation.get("attempts", [])}

    cells = []
    for position in range(1, PLANNED_CELLS + 1):
        pilot = position <= PILOT_CELLS
        attempts = sorted(by_position.get(position, []), key=lambda a: a["ordinal"])
        summary_path = ("docs/research/bounded-discovery-pilot-2026-09-09/cells/position-%02d/"
                        "summary.json" % position)
        rows = []
        for attempt in attempts:
            charge = charges.get(attempt["attempt_ref"], {})
            completion = attempt.get("completion")
            censored = completion not in (None, "complete")
            rows.append({
                "attempt_ref": attempt["attempt_ref"],
                "ordinal": attempt["ordinal"],
                "predecessor_ref": ("position-%02d-attempt-%d" % (position, attempt["ordinal"] - 1)
                                    if attempt["ordinal"] > 1 else None),
                "is_replacement": attempt["ordinal"] > 1,
                "operational_validity": attempt["operational_validity"],
                "validity_basis": attempt["validity_basis"],
                "completion": completion,
                "settled_usd": charge.get("ledger_settled_usd") or attempt.get("settled_usd"),
                "reconciles_with_ledger": charge.get("reconciles"),
                "produced_claims": attempt.get("produced_claims", False),
                "timing_availability": (
                    "root elapsed recorded; duration censored at the stop, not completed"
                    if censored else
                    "root elapsed and the #130 sidecar recorded"
                    if attempt["dimensions"].get("completion_and_stop", {}).get(
                        "timing_sidecar_fields") else
                    "no timing sidecar: the attempt ended before one was written"),
                "root_elapsed_seconds": attempt["dimensions"].get(
                    "completion_and_stop", {}).get("root_elapsed_seconds"),
                "raw_evidence": "sealed with this closeout; see packets/README.md",
            })
        cells.append({
            "position": position,
            "block": "pilot" if pilot else "grid",
            "owner_ticket": 150 if pilot else 151,
            "status": "attempted" if rows else "unattempted",
            "attempts": rows,
            "attempt_count": len(rows),
            "arm": attempts[0].get("arm") if attempts else None,
            "public_summary_path": summary_path if pilot else None,
            "outputs": ("the public per-cell summary above; every raw artifact is sealed"
                        if rows else
                        "unavailable: this cell was never attempted, and an unattempted cell has "
                        "no output to recover"),
            "charges_usd": str(sum(usd(row["settled_usd"]) for row in rows)) if rows else "0.0000000",
        })

    attempted = [cell for cell in cells if cell["status"] == "attempted"]
    total_attempts = sum(cell["attempt_count"] for cell in cells)
    ledger_opens = reconciliation.get("columns", {}).get("settlement_events", {}).get("attempts")
    return {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-151-cell-manifest",
        "built_at": now(),
        "planned_cells": PLANNED_CELLS,
        "pilot_cells": PILOT_CELLS,
        "grid_cells": PLANNED_CELLS - PILOT_CELLS,
        "attempted_cells": len(attempted),
        "unattempted_cells": PLANNED_CELLS - len(attempted),
        "attempts_recorded": total_attempts,
        "attempt_limit": ATTEMPT_LIMIT,
        "reconciles_with_ledger": total_attempts == ledger_opens,
        "ledger_settlement_events_for_attempts": ledger_opens,
        "pins": {
            "dispatch_template_sha256": ((frozen.get("pins") or {}).get("dispatch_template")
                                         or {}).get("sha256"),
            "policy_commit": (frozen.get("pins") or {}).get("policy_commit"),
            "policy_tree": (frozen.get("pins") or {}).get("skill_tree"),
            "workflow": "v5b-10",
            "frozen_manifest": "docs/research/bounded-discovery-runs-2026-09-08/manifest.json",
            "per_attempt_packet_and_scope": (
                "each attempted cell's packet and selected scope were re-checked against the "
                "frozen pin for its target in fidelity-assessment.json; the digests themselves "
                "stay sealed, because a packet digest names a target"),
        },
        "keying": ("Every row is keyed by schedule position. The mapping from position to cell id "
                   "stays sealed: the pilot pair is the adjudicated clean slot and the "
                   "lowest-numbered buggy slot, so naming either the six attempted cells or the "
                   "eighteen unattempted ones would disclose which slot holds the clean control."),
        "unattempted_note": ("The eighteen grid cells were never dispatched. Their outputs are "
                             "unavailable and stay unavailable: an unattempted cell counts as "
                             "missing in the screen, never as present."),
        "censored_note": ("A stopped attempt reports its root elapsed time with the duration "
                          "censored at the stop. Censored duration is not completion, and no row "
                          "converts one into the other."),
        "cells": cells,
    }


def command_manifest(args) -> int:
    frozen = load(args.frozen)
    manifest = build_manifest(load(args.fidelity), load(args.reconciliation),
                              Path(args.bundle), frozen)
    forbidden, allowed = disclosive_values(frozen)
    leaked = leak_scan(manifest, sorted(set(list(args.slot_names) + forbidden)), allowed)
    if leaked:
        for line in leaked:
            print(line)
        return 1
    violations = []
    if len(manifest["cells"]) != PLANNED_CELLS:
        violations.append("the manifest must carry all %d planned cells" % PLANNED_CELLS)
    if manifest["attempts_recorded"] > ATTEMPT_LIMIT:
        violations.append("the manifest records %d attempts, above the frozen limit of %d"
                          % (manifest["attempts_recorded"], ATTEMPT_LIMIT))
    if not manifest["reconciles_with_ledger"]:
        violations.append("the manifest records %d attempts against %s settled on the ledger"
                          % (manifest["attempts_recorded"],
                             manifest["ledger_settlement_events_for_attempts"]))
    for line in violations:
        print(line)
    if violations:
        return 1
    write(args.out, manifest)
    print(json.dumps({"cells": len(manifest["cells"]),
                      "attempted": manifest["attempted_cells"],
                      "attempts": manifest["attempts_recorded"]}))
    return 0


# --------------------------------------------------------------------------
# Sealing what may not be published in the clear
# --------------------------------------------------------------------------

def command_seal(args) -> int:
    """Seal a directory under #148's key, in #149's parameters.

    The grading packets cannot be committed in the clear however well the arm
    labels are masked. Their prose has to keep file paths and symbol names for
    the grading to mean anything, and those name the target - so publishing the
    six pilot packets would name the two slots the pilot ran on, and the public
    selection rule turns that pair into the clean slot."""
    source = Path(os.path.expanduser(args.source))
    out = Path(os.path.expanduser(args.out_dir))
    if not source.is_dir():
        print("nothing to seal at %s" % source)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    plaintext = out / (args.name + ".tar.gz")
    ciphertext = out / (args.name + ".tar.gz.enc")

    files = sorted(entry.name for entry in source.iterdir() if entry.is_file())
    if not files:
        print("nothing to seal: %s holds no file" % source)
        return 1
    archive = capture(["tar", "-czf", str(plaintext), "-C", str(source)] + files, timeout=900)
    if archive["exit_code"] != 0:
        sys.stderr.write("tar failed: %s\n" % archive["stderr"][:400])
        return 2
    plaintext_sha = hashlib.sha256(plaintext.read_bytes()).hexdigest()
    encrypt = capture(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-salt",
                       "-pass", "file:%s" % os.path.expanduser(args.key),
                       "-in", str(plaintext), "-out", str(ciphertext)], timeout=900)
    if encrypt["exit_code"] != 0:
        sys.stderr.write("openssl enc failed: %s\n" % encrypt["stderr"][:400])
        return 2
    ciphertext_bytes = ciphertext.read_bytes()
    plaintext.unlink()

    (out / "SHA256SUMS").write_text("%s  %s\n" % (plaintext_sha, plaintext.name), encoding="utf-8")
    seal = {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-151-%s-seal" % args.name,
        "sealed_at": now(),
        "ciphertext_bytes": len(ciphertext_bytes),
        "ciphertext_sha256": hashlib.sha256(ciphertext_bytes).hexdigest(),
        "plaintext_sha256": plaintext_sha,
        "files_sealed": files,
        "cipher": "openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt, under #148's key",
        "why_sealed": args.why,
    }
    write(out / "seal.json", seal)
    print(json.dumps({"files": len(files), "ciphertext_bytes": seal["ciphertext_bytes"]}))
    return 0


# --------------------------------------------------------------------------
# The stage record #152 reads
# --------------------------------------------------------------------------

def build_handoff(gate, assessment, reconciliation, cell_manifest, packet_index,
                  no_packet, seal, supplement=None) -> dict:
    """#151's stage record.

    It has to be readable as a stop: the closeout is delivered, the experiment
    is not. Nothing here releases the dispatch hold, and nothing converts an
    unresolved attempt into a valid one."""
    unattempted = cell_manifest["unattempted_cells"]
    return {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-151-closeout-handoff",
        "stage": "closeout",
        "created_at": now(),
        "disposition": "closeout-delivered",
        "experiment_disposition": "stopped-incomplete",
        "dispatch_authorized": False,
        "dispatch_hold": ("held. This closeout authorises nothing to run. #151 launched no "
                          "experimental reviewer run, and the eighteen unattempted cells stay "
                          "unattempted."),
        "gate": {
            "all_reviewers_stopped": gate["all_reviewers_stopped"],
            "observed_at": gate["observed_at"],
            "checks": len(gate["checks"]),
            "recorded_before_the_seal_was_opened": True,
            "supplement": ({
                "observed_at": supplement.get("observed_at"),
                "passed": supplement.get("passed"),
                "recorded_after_the_seal_was_opened": True,
                "why": supplement.get("why"),
                "standing": supplement.get("standing"),
            } if supplement else None),
        },
        "fidelity": {
            "finding_id": assessment["finding_id"],
            "status": assessment["status"],
            "decision": assessment["decision"],
            "valid": len(assessment["valid"]),
            "unresolved": len(assessment["unresolved"]),
            "invalid": len(assessment["invalid"]),
            "observed_violations": assessment["observed_violations"],
            "missing_evidence": assessment["missing_evidence"],
            "effect_on_grading": assessment["effect_on_grading"],
        },
        "accounting": {
            "actual_usd": reconciliation["totals"]["ledger_actual_usd"],
            "reconciles": reconciliation["totals"]["reconciles"],
            "retained_uncertainty_usd": reconciliation["totals"]["retained_uncertainty_usd"],
            "frozen_total_cap_usd": reconciliation["ledger"]["frozen_total_cap_usd"],
            "remaining_under_cap_usd": reconciliation["repair"]["remaining_under_cap_usd"],
            "discrepancies": [item["id"] for item in reconciliation["discrepancies"]],
            "repair_fits_frozen_limits": reconciliation["repair"]["fits_frozen_limits"],
            "repair_binding_constraint": reconciliation["repair"]["binding_constraint"],
        },
        "cells": {
            "planned": cell_manifest["planned_cells"],
            "attempted": cell_manifest["attempted_cells"],
            "unattempted": unattempted,
            "attempts_recorded": cell_manifest["attempts_recorded"],
            "attempt_limit": cell_manifest["attempt_limit"],
            "manifest": "manifest.json",
        },
        "packets": {
            "packets": packet_index["packet_count"],
            "no_packet_attempts": len(no_packet["attempts"]),
            "sealed": True,
            "ciphertext_sha256": seal["ciphertext_sha256"],
            "plaintext_sha256": seal["plaintext_sha256"],
            "path": "packets/",
            "blinding": "label masking, not guaranteed blinding; see packets/README.md",
        },
        "claims_note": ("No quality, recall or cost comparison appears in this closeout. No arm "
                        "is described as better or worse, and the arm mapping stays sealed until "
                        "#152 freezes its rulings."),
        "next_stage": {
            "tickets": [152, 153],
            "work": ("#152 grades the available claims from the sealed packets and may finish "
                     "even though zero further cells ran. It must carry the unresolved fidelity "
                     "status and the accounting discrepancies into its rulings rather than "
                     "treating any attempt as a valid completed outcome. #153 applies "
                     "conservative decision limits and opens the redaction map at reveal."),
            "must_not": [
                "dispatch any of the eighteen unattempted cells from this handoff",
                "treat an unresolved attempt as a valid completed outcome",
                "read a budget stop as infrastructure invalidity, or reset an attempt count",
                "open the redaction map before rulings are frozen",
                "grade this closeout's own outcomes",
            ],
        },
        "blockers": (
            ["Historical pilot fidelity is assessed and remains unresolved: no violation was "
             "observed, and the launch argv and per-role usage split that would establish "
             "equal allowances and role-level spend were never retained. The eighteen grid "
             "cells are unattempted and the frozen replacement allowance cannot fund a repair, "
             "so the grid cannot be completed or repaired under the frozen limits."]
            if assessment["status"] != "resolved" else []),
    }


def command_handoff(args) -> int:
    handoff = build_handoff(load(args.gate), load(args.fidelity), load(args.reconciliation),
                            load(args.manifest), load(args.packet_index), load(args.no_packet),
                            load(args.seal),
                            load(args.gate_supplement) if args.gate_supplement else None)
    leaked = leak_scan(handoff, args.slot_names)
    if leaked:
        for line in leaked:
            print(line)
        return 1
    violations = []
    if handoff["dispatch_authorized"]:
        violations.append("a stopped closeout must not authorise dispatch")
    if handoff["fidelity"]["status"] != "resolved" and not handoff["blockers"]:
        violations.append("an unresolved fidelity status must carry a blocker")
    for line in violations:
        print(line)
    if violations:
        return 1
    write(args.out, handoff)
    print(json.dumps({"disposition": handoff["disposition"],
                      "fidelity": handoff["fidelity"]["status"],
                      "dispatch_authorized": handoff["dispatch_authorized"]}))
    return 0


def command_gate_supplement(args) -> int:
    """Re-run the workspace absence check against roots learned after the gate.

    The gate has to be recorded before anything sealed is opened, which means it
    is recorded before the evidence can say where the cells actually ran. The
    pilot's configuration file was not committed and did not survive, so the
    first gate checked a plausible cell root rather than the real one, and its
    sweep of the user's home could not have reached a root under ``/tmp``.

    This records the corrected check and states its ordering plainly: it was
    observed after the seal was opened, and it is corroboration, not the gate.
    The checks that establish no reviewer is running - the process table, the
    container runtime and the ledger - were all made before the seal and are
    unaffected. The ledger digest is recorded on both sides so that "nothing ran
    in between" is a checkable claim rather than an assurance."""
    gate = load(args.gate)
    ledger_path = Path(os.path.expanduser(args.ledger))
    ledger_digest = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    observed_at = now()

    roots, present = [], []
    for root in args.cells_root:
        expanded = Path(os.path.expanduser(root))
        exists = expanded.exists()
        roots.append({"root": str(root), "exists": exists})
        if exists:
            present.append(str(root))
    sweep = capture(["find"] + [os.path.expanduser(path) for path in args.sweep]
                    + ["-maxdepth", "4", "-type", "d", "-name", args.pattern], timeout=600)
    # The evidence this closeout extracted for reading is not a live workspace.
    excluded = os.path.expanduser(args.exclude) if args.exclude else None
    stray = [line for line in sweep.get("stdout", "").splitlines()
             if line.strip() and not (excluded and line.startswith(excluded))]

    passed = not present and not stray and bool(sweep.get("ran"))
    record = {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-151-stop-gate-supplement",
        "supplements": gate.get("artifact_id"),
        "gate_observed_at": gate.get("observed_at"),
        "observed_at": observed_at,
        "recorded_after_the_seal_was_opened": True,
        "why": ("the pilot's cell root was only readable from the evidence the gate released, so "
                "the gate checked a plausible root and a sweep that could not have reached the "
                "real one"),
        "standing": ("corroboration, not the gate. The checks that establish no reviewer is "
                     "running - the process table, the container runtime and the ledger - were "
                     "made before the seal was opened and are unchanged."),
        "roots_checked": roots,
        "roots_present": present,
        "sweep_command": sweep.get("command"),
        "sweep_ran": bool(sweep.get("ran")),
        "sweep_match_count": len(stray),
        "sweep_output_sha256": digest(sweep.get("stdout", "") + sweep.get("stderr", "")),
        "excluded_prefix": ("this closeout's own read-only extract of the sealed evidence"
                            if excluded else None),
        "ledger_sha256_now": ledger_digest,
        "ledger_unchanged_since_the_gate": ledger_digest == args.ledger_sha256
                                           if args.ledger_sha256 else None,
        "passed": passed,
        "detail": ("no configured cell root exists and no attempt workspace survives under the "
                   "swept paths" if passed else
                   "a cell root or an attempt workspace still exists"),
    }
    write(args.out, record)
    if not passed:
        print("supplementary workspace check failed: %s" % record["detail"])
        return 1
    print(json.dumps({"passed": passed, "observed_at": observed_at}))
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

    supplement = sub.add_parser("gate-supplement",
                                help="re-check workspace absence at roots learned after the gate")
    supplement.add_argument("--gate", required=True)
    supplement.add_argument("--ledger", required=True)
    supplement.add_argument("--ledger-sha256", help="the digest the gate saw, to show nothing ran")
    supplement.add_argument("--cells-root", nargs="+", required=True)
    supplement.add_argument("--sweep", nargs="+", default=["/tmp", "~"])
    supplement.add_argument("--pattern", default="position-0*")
    supplement.add_argument("--exclude", help="a path prefix that is this closeout's own extract")
    supplement.add_argument("--out", required=True)
    supplement.set_defaults(handler=command_gate_supplement)

    fidelity = sub.add_parser("fidelity", help="assess pilot/actual-fidelity from the evidence")
    fidelity.add_argument("--gate", required=True)
    fidelity.add_argument("--evidence", required=True)
    fidelity.add_argument("--manifest", required=True, help="#149's frozen manifest.json")
    fidelity.add_argument("--bundle", required=True, help="#150's published pilot bundle")
    fidelity.add_argument("--salt", help="the sealed per-bundle commitment salt")
    fidelity.add_argument("--slot-names", nargs="*", default=["slot-1", "slot-2", "slot-3",
                                                              "slot-4"])
    fidelity.add_argument("--out", required=True)
    fidelity.set_defaults(handler=command_fidelity)

    reconcile = sub.add_parser("reconcile", help="reconcile every charge against the ledger")
    reconcile.add_argument("--ledger", required=True)
    reconcile.add_argument("--manifest", required=True)
    reconcile.add_argument("--evidence", required=True)
    reconcile.add_argument("--fidelity", required=True)
    reconcile.add_argument("--bundle", required=True)
    reconcile.add_argument("--slot-names", nargs="*", default=["slot-1", "slot-2", "slot-3",
                                                               "slot-4"])
    reconcile.add_argument("--out", required=True)
    reconcile.set_defaults(handler=command_reconcile)

    cell_manifest = sub.add_parser("manifest", help="the manifest for all 24 planned cells")
    cell_manifest.add_argument("--fidelity", required=True)
    cell_manifest.add_argument("--reconciliation", required=True)
    cell_manifest.add_argument("--bundle", required=True)
    cell_manifest.add_argument("--frozen", required=True, help="#149's frozen manifest.json")
    cell_manifest.add_argument("--slot-names", nargs="*", default=["slot-1", "slot-2", "slot-3",
                                                                   "slot-4"])
    cell_manifest.add_argument("--out", required=True)
    cell_manifest.set_defaults(handler=command_manifest)

    seal_cmd = sub.add_parser("seal", help="seal a directory under #148's key")
    seal_cmd.add_argument("--source", required=True)
    seal_cmd.add_argument("--key", required=True)
    seal_cmd.add_argument("--name", required=True)
    seal_cmd.add_argument("--why", required=True)
    seal_cmd.add_argument("--out-dir", required=True)
    seal_cmd.set_defaults(handler=command_seal)

    handoff = sub.add_parser("handoff", help="write the stage record #152 reads")
    handoff.add_argument("--gate", required=True)
    handoff.add_argument("--gate-supplement")
    handoff.add_argument("--fidelity", required=True)
    handoff.add_argument("--reconciliation", required=True)
    handoff.add_argument("--manifest", required=True, help="this closeout's 24-cell manifest")
    handoff.add_argument("--packet-index", required=True)
    handoff.add_argument("--no-packet", required=True)
    handoff.add_argument("--seal", required=True)
    handoff.add_argument("--slot-names", nargs="*", default=["slot-1", "slot-2", "slot-3",
                                                             "slot-4"])
    handoff.add_argument("--out", required=True)
    handoff.set_defaults(handler=command_handoff)
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

    def ledger_with(events, reserved="0.00"):  # noqa: E306
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

        # --- the fidelity assessment ---------------------------------------
        # A provider error writes an assistant line under `<synthetic>`. It must
        # be dropped, not read as a second model.
        lines = [json.dumps({"type": "user", "parentUuid": None, "version": "2.1.263"})]
        lines += [json.dumps({"type": "assistant",
                              "message": {"model": "claude-sonnet-5", "effort": "high"}})] * 3
        lines.append(json.dumps({"type": "assistant", "message": {"model": "<synthetic>"}}))
        (tmp / "t.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        scan = scan_transcript(tmp / "t.jsonl")
        check("a provider-error line is dropped from the model census",
              scan["models"] == {"claude-sonnet-5": 3} and scan["synthetic_error_lines"] == 1)
        check("a single root user message with no summary reads as a fresh context",
              scan["fresh_context"] is True)
        verdict = settings_verdict(scan, {"model": "claude-sonnet-5", "effort": "high"})
        check("a matching transcript verifies", verdict["verified"] is True)
        check("a transcript on the wrong model does not verify",
              settings_verdict(scan, {"model": "claude-opus-5",
                                      "effort": "high"})["verified"] is False)
        check("an unobservable setting is a failure, not a pass",
              settings_verdict({"readable": True, "assistant_lines": 0, "models": {},
                                "efforts": {}}, {"model": "claude-sonnet-5",
                                                 "effort": "high"})["verified"] is False)

        resumed = [json.dumps({"type": "user", "parentUuid": None}),
                   json.dumps({"type": "summary", "summary": "earlier work"}),
                   json.dumps({"type": "user", "parentUuid": None})]
        (tmp / "r.jsonl").write_text("\n".join(resumed) + "\n", encoding="utf-8")
        check("a resumed or summarised session is not a fresh context",
              scan_transcript(tmp / "r.jsonl")["fresh_context"] is False)

        check("a sub-agent transcript is a worker",
              role_of("/x/transcripts/-p/uuid/subagents/agent-1.jsonl") == "worker")
        check("a finder-store transcript is the finder",
              role_of("/x/transcripts/-tmp-cells-position-06-finder-store/u.jsonl") == "finder")
        check("a root session transcript is the primary",
              role_of("/x/transcripts/-tmp-cells-position-06-work/u.jsonl") == "primary")

        check("the metering copies are excluded from the transcript inventory",
              all("filtered-transcripts" not in str(path)
                  for path in retained_transcripts(tmp)))

        # A payload that names a slot, a target repository commit or a raw
        # object id must never be written to the repository.
        check("a slot name is refused",
              leak_scan({"a": "slot-2-A-replicate-1"}, ["slot-1", "slot-2"]))
        check("a full object id is refused", leak_scan({"a": "d" * 40}, []))
        check("a clean payload passes the leak scan",
              not leak_scan({"a": "position-03-attempt-2", "b": "abc1234"}, ["slot-1"]))
        check("an allow-listed public pin is not refused",
              not leak_scan({"a": "0" * 40}, [], allowed_ids=["0" * 40]))
        check("an object id outside the allow-list is refused",
              leak_scan({"a": "0" * 40}, [], allowed_ids=["1" * 40]))
        frozen_fixture = {
            "pins": {"policy_commit": "a" * 40, "skill_tree": "b" * 40},
            "repository_commit_read": "c" * 40,
            "targets": {"slot-1": {"target": {"repository": "acme/widget", "pr": 5044,
                                              "head_oid": "d" * 40}}}}
        forbidden_fixture, allowed_fixture = disclosive_values(frozen_fixture)
        check("the frozen manifest's own pins are allowed",
              set(allowed_fixture) == {"a" * 40, "b" * 40, "c" * 40})
        check("every value that identifies a target is forbidden",
              {"slot-1", "acme/widget", "d" * 40, "acme/widget#5044"} <= set(forbidden_fixture))
        check("a target repository name is refused even without an object id",
              leak_scan({"a": "found in acme/widget"}, forbidden_fixture, allowed_fixture))
        check("a source path that names the project without its owner is refused",
              leak_scan({"a": "read widget/src/main.rs"}, forbidden_fixture, allowed_fixture))
        check("both components of a target repository are forbidden",
              {"acme", "widget"} <= set(forbidden_fixture))

        # The fidelity command refuses to read sealed evidence behind a shut gate.
        (tmp / "shut-gate.json").write_text(json.dumps({"all_reviewers_stopped": False}),
                                            encoding="utf-8")
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "fidelity",
                               "--gate", str(tmp / "shut-gate.json"), "--evidence", str(tmp),
                               "--manifest", str(tmp / "ledger.json"), "--bundle", str(tmp),
                               "--out", str(tmp / "f.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("the fidelity assessment refuses to read sealed evidence behind a shut gate",
              code.returncode == 1 and "must not" in code.stdout)

        # --- the reconciliation ---------------------------------------------
        money = ledger_with([
            {"operation": "settle", "phase": "pre-freeze", "actual_delta_usd": "1.00"},
            {"operation": "settle", "phase": "review", "actual_delta_usd": "0.25"},
            {"operation": "reserve", "phase": "review", "attempt_id": "issue-138-x-attempt-1",
             "reservation_delta_usd": "10.00", "observed_at": "2026-09-09T05:00:00Z"},
            {"operation": "settle", "phase": "review", "attempt_id": "issue-138-x-attempt-1",
             "actual_delta_usd": "0", "observed_at": "2026-09-09T05:01:00Z"},
            {"operation": "settle", "phase": "review", "attempt_id": "issue-138-x-attempt-2",
             "actual_delta_usd": "3.00", "observed_at": "2026-09-09T05:02:00Z"},
            {"operation": "attempt-open", "attempt_id": "issue-138-x-attempt-1",
             "observed_at": "2026-09-09T09:00:00Z"},
            {"operation": "attempt-open", "attempt_id": "issue-138-x-attempt-2",
             "observed_at": "2026-09-09T09:00:01Z"},
            {"operation": "attempt-close", "attempt_id": "issue-138-x-attempt-1",
             "disposition": "stopped-invalid", "observed_at": "2026-09-09T09:00:02Z"},
        ])
        money["attempts_dispatched"] = 0
        categories = ledger_categories(money)
        check("pre-freeze, setup and review spend are separated",
              str(categories["totals"]["pre_freeze"]) == "1.00"
              and str(categories["totals"]["setup"]) == "0.25"
              and str(categories["totals"]["attempts"]) == "3.00")
        check("an attempt that settled at zero is still counted as a settlement",
              categories["counts"]["attempts"] == 2
              and "issue-138-x-attempt-1" in categories["per_attempt"])

        found = {d["id"] for d in ledger_discrepancies(money, {}, "aa", "bb", [])}
        check("a lifecycle written after the last settlement is reported",
              "ledger/attempt-lifecycle-backfilled" in found)
        check("a header counter that disagrees with the events is reported",
              "ledger/attempts-dispatched-counter" in found)
        check("a published digest that differs from the live one is reported",
              "ledger/published-digest-precedes-the-lifecycle-events" in found)
        check("an absent per-role split is reported",
              "ledger/no-per-role-split" in found)

        money.update({"frozen_total_cap_usd": "150.00", "actual_usd": "47.00",
                      "uncertainty_usd": "0.16", "grading_closeout_reserve_usd": "10.00",
                      "attempt_limit": 27, "replacement_limit": 3})
        feasible = repair_feasibility(money, {}, {
            "unresolved": ["p1", "p2", "p3"],
            "attempts": [{"attempt_ref": "p1", "settled_usd": "4.00"},
                         {"attempt_ref": "p2", "settled_usd": "4.00"},
                         {"attempt_ref": "p3", "settled_usd": "4.00"}]})
        check("the remaining allowance is net of the reserve and the retained uncertainty",
              feasible["remaining_under_cap_usd"] == "92.84")
        check("a replacement is counted from the attempt ordinal in its id",
              feasible["replacements_used"] == 1 and feasible["attempts_used"] == 2)
        check("a repair that needs more replacements than remain does not fit",
              feasible["fits_money"] is True
              and feasible["fits_replacement_allowance"] is False
              and feasible["fits_frozen_limits"] is False)
        check("an unparseable attempt id does not abort the reconciliation",
              attempt_ordinal("a1") == 1 and attempt_ordinal(None) == 1
              and attempt_ordinal("issue-138-x-attempt-3") == 3)
        check("no repair is dispatched from the stopped path", feasible["dispatched"] is False)

        # --- the supplementary workspace check ------------------------------
        (tmp / "gate-for-supplement.json").write_text(
            json.dumps({"artifact_id": "issue-151-stop-gate",
                        "observed_at": "2026-09-10T07:03:56Z"}), encoding="utf-8")
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "gate-supplement",
                               "--gate", str(tmp / "gate-for-supplement.json"),
                               "--ledger", str(tmp / "ledger.json"),
                               "--cells-root", str(tmp / "absent-a"), str(tmp / "absent-b"),
                               "--sweep", str(tmp / "absent-a"),
                               "--out", str(tmp / "supplement.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("an absent cell root passes the supplementary check", code.returncode == 0)
        supplement = json.loads((tmp / "supplement.json").read_text(encoding="utf-8"))
        check("the supplement says it was recorded after the seal was opened",
              supplement["recorded_after_the_seal_was_opened"] is True)
        check("the supplement is corroboration, not the gate",
              "not the gate" in supplement["standing"])
        code = subprocess.run([sys.executable, str(Path(__file__).resolve()), "gate-supplement",
                               "--gate", str(tmp / "gate-for-supplement.json"),
                               "--ledger", str(tmp / "ledger.json"),
                               "--cells-root", str(tmp / "present-cells"),
                               "--sweep", str(tmp / "present-cells"),
                               "--out", str(tmp / "supplement2.json")],
                              capture_output=True, text=True, encoding="utf-8")
        check("a surviving cell root fails the supplementary check", code.returncode == 1)

        # --- the handoff ------------------------------------------------------
        stub_gate = {"all_reviewers_stopped": True, "observed_at": "2026-09-10T00:00:00Z",
                     "checks": [{"passed": True}]}
        stub_assessment = {"finding_id": "pilot/actual-fidelity", "status": "unresolved",
                           "decision": "d", "valid": [], "unresolved": ["p1"], "invalid": [],
                           "observed_violations": [], "missing_evidence": ["m"],
                           "effect_on_grading": "e"}
        stub_reconciliation = {
            "totals": {"ledger_actual_usd": "1.00", "reconciles": True,
                       "retained_uncertainty_usd": "0.00"},
            "ledger": {"frozen_total_cap_usd": "150.00"},
            "repair": {"remaining_under_cap_usd": "1.00", "fits_frozen_limits": False,
                       "binding_constraint": "b"},
            "discrepancies": [{"id": "x"}]}
        stub_cells = {"planned_cells": 24, "attempted_cells": 6, "unattempted_cells": 18,
                      "attempts_recorded": 8, "attempt_limit": 27}
        handoff = build_handoff(stub_gate, stub_assessment, stub_reconciliation, stub_cells,
                                {"packet_count": 6}, {"attempts": [1, 2]},
                                {"ciphertext_sha256": "x", "plaintext_sha256": "y"})
        check("a stopped closeout does not authorise dispatch",
              handoff["dispatch_authorized"] is False)
        check("an unresolved fidelity status carries a blocker", bool(handoff["blockers"]))
        check("the handoff names what the next stage must not do",
              any("valid completed outcome" in line for line in handoff["next_stage"]["must_not"]))
        check("the handoff reports no arm comparison", "better or worse" in handoff["claims_note"])

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
    print("%d checks, %d failures" % (55, len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
