#!/usr/bin/env python3
"""Run one bounded-discovery cell or produce a no-cell runtime stop.

Usage: python3 scripts/adapter.py --config CONFIG --scenario SCENARIO --out NEW_DIR
       [--runtime fake|claude]
Input: bounded-discovery-v1 ExperimentConfig and explicit fake worker responses.
See ../ADAPTER.md for the executable schema, supported controls and limitations.
All output artifacts are created exclusively. No forge calls or paid dispatch.
Exit: 0 delivered fake cell, 1 stopped/content violation, 2 unreadable input or
failed helper command. Every readable invocation creates a closeout, even if no
worker or review payload exists. Reusing an output directory is an input error.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

from budget import Violation, attempt_event, now, totals, transact, usd


SCHEMA = "bounded-discovery-v1"
POLICY = "83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6"
TREE = "bea6be143582e75bada966ee85964623ef31f167"
ROLES = ("primary", "finder", "initial-verifier", "follow-up-verifier")
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


class Stop(Violation):
    def __init__(self, disposition, reason):
        super().__init__(reason)
        self.disposition = disposition


def require(condition, reason):
    if not condition:
        raise Violation(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(data):
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def artifact(path, access="coordinator-only"):
    return dict(uri=str(path), sha256=digest(path.read_bytes()), access=access)


def write(path, data, access="coordinator-only"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "xb") as stream:
        stream.write(data if isinstance(data, bytes) else encode(data))
    return artifact(path, access)


def load_ref(ref, roots, access=None):
    require(isinstance(ref, dict) and set(ref) == {"uri", "sha256", "access"}, "invalid ArtifactRef")
    path = Path(ref["uri"]).resolve()
    require(any(path.is_relative_to(root) for root in roots), "artifact outside permitted input roots")
    require(access is None or ref["access"] == access, "artifact access mismatch")
    raw = path.read_bytes()
    require(digest(raw) == ref["sha256"], "artifact hash mismatch: " + str(path))
    return raw


def oid(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value)


def positive(value):
    return not isinstance(value, bool) and usd(value) > 0


def validate_config(config, out):
    require(config["schema_version"] == SCHEMA, "wrong schema version")
    require(config["arm"] in "ABC" and len(config["arm"]) == 1, "invalid arm")
    require(config["policy_commit"] == POLICY and config["skill_tree"] == TREE, "common #136 policy pin mismatch")
    roots = [Path(p).resolve() for p in config["permitted_input_roots"]]
    require(roots and all(p.exists() for p in roots), "input roots must exist")
    require(not any(out.is_relative_to(p) or p.is_relative_to(out) for p in roots), "input and output roots overlap")
    for name in ("method", "design", "prototype", "primary_task", "verifier_task", "source", "scope", "target"):
        load_ref(config[name], roots, "reviewer-common" if name in ("source", "target") else None)
    require(set(config["prototype_files"]) == {"adapter.py", "budget.py", "fake_worker.py"}, "prototype file pins incomplete")
    for name, ref in config["prototype_files"].items():
        require(load_ref(ref, roots) == (HERE / name).read_bytes(), "executed prototype file differs from pin: " + name)
    require(config["verifier_tasks"]["B"] == config["verifier_tasks"]["C"] == config["verifier_task"],
            "B/C verifier task bytes differ")
    for task in config["verifier_tasks"].values():
        load_ref(task, roots)
    require(config["workers"]["B"] == config["workers"]["C"], "B/C worker settings differ")
    for worker in [config["primary_config"], *config["workers"].values()]:
        require(all(isinstance(worker[k], str) and worker[k] for k in ("model", "effort", "permissions")),
                "worker settings incomplete")
    if config["arm"] == "C":
        require(config["finder_config"] == config["workers"]["B"], "finder setting differs from B verifier")
        load_ref(config["finder_task"], roots)
    else:
        require(config.get("finder_task") is None and config.get("finder_config") is None,
                "A/B cannot have finder configuration")
    source = json.loads(load_ref(config["source"], roots, "reviewer-common"))
    for name in ("packet_id", "repository", "repository_url", "pr", "state", "posting_identity",
                 "review_identity", "base_ref", "cutoff", "permitted_history", "content"):
        require(source.get(name), "source missing " + name)
    require(source["schema_version"] == SCHEMA and type(source.get("merged")) is bool and
            source["state"] in ("OPEN", "CLOSED", "MERGED"), "source identity/state invalid")
    for name in ("base_oid", "head_oid", "merge_base_oid"):
        require(oid(source[name]), "invalid source OID")
    require(source["provenance"] == {"complete": True, "origin": "common-preparation", "contains_arm_output": False},
            "source must come from complete common preparation")
    for name in ("pr_ref", "spec_ref", "rules_ref", "diff_ref", "manifest_ref", "ranges_ref",
                 "dependencies_ref", "execution_policy_ref"):
        load_ref(source[name], roots, "reviewer-common")
    target = json.loads(load_ref(config["target"], roots))
    require(all(target[k] == source[k] for k in ("repository", "pr", "base_oid", "head_oid", "merge_base_oid")),
            "target SHA or identity mismatch")
    scope = json.loads(load_ref(config["scope"], roots))
    require(scope["source_hash"] == config["source"]["sha256"], "scope source hash mismatch")
    require(scope["selection_mode"] in ("mechanical", "model-assisted") and scope["scope_id"], "scope selection missing")
    require(type(scope["max_hops"]) is int and 0 <= scope["max_hops"] <= 2, "scope frontier exceeds two hops")
    require(scope["roots"] and scope["alternatives"] and scope["rationale"] and scope["citations"], "scope selection incomplete")
    ranges = list(scope["roots"])
    known = {r["symbol"]: 0 for r in ranges}
    for edge in scope["frontier"]:
        require(edge["from"] in known and edge["kind"] in ("caller", "callee", "contract") and edge["citation"],
                "frontier edge lacks a cited predecessor")
        hop = known[edge["from"]] + 1
        require(hop <= scope["max_hops"], "frontier hop limit")
        require(edge["to"]["symbol"] not in known, "duplicate frontier symbol")
        known[edge["to"]["symbol"]] = hop
        ranges.append(edge["to"])
    clone = Path(config["clone_root"]).resolve()
    require(clone.is_dir() and any(clone.is_relative_to(p) for p in roots), "clone outside input roots")
    for row in ranges:
        path = Path(row["path"])
        require(not path.is_absolute() and (clone / path).resolve().is_relative_to(clone), "scope path escapes clone")
        require(type(row["start"]) is int and type(row["end"]) is int and 1 <= row["start"] <= row["end"], "invalid scope range")
    contexts = config["contexts"]
    expected = set(ROLES) - (set() if config["arm"] == "C" else {"finder"})
    require(set(contexts) == expected and len(set(contexts.values())) == len(contexts), "workers need separate fresh context IDs")
    require(all(re.fullmatch(r"[A-Za-z0-9_-]+", v) for v in contexts.values()), "unsafe context ID")
    require(re.fullmatch(r"[A-Za-z0-9_-]+", config["attempt_id"]), "invalid attempt ID")
    require(len(config["ordered_cells"]) == 24 and config["cell_id"] in config["ordered_cells"] and len(set(config["ordered_cells"])) == 24,
            "config needs 24 unique planned cell IDs")
    require(config["replicate"] in (1, 2), "invalid replicate")
    limits = config["limits"]
    for name in ("attempt_usd", "request_usd", "headroom_usd", "wall_seconds", "finder_seconds",
                 "worker_seconds", "requests", "tokens", "finder_tokens", "tokens_per_request", "commands"):
        require(positive(limits[name]), "limit must be positive: " + name)
    for name in ("requests", "tokens", "finder_tokens", "tokens_per_request", "commands"):
        require(type(limits[name]) is int, "count limit must be integer: " + name)
    require(limits["finder_seconds"] <= limits["worker_seconds"] <= limits["wall_seconds"], "phase time bounds exceed root")
    require(config["completion_mode"] == "render-only", "only render-only is supported")
    require(config["session_shape"] and config["cache_policy"] and config["rates"]["evidence"], "runtime/rate controls missing")
    for key in ("input", "output", "cache_write_5m", "cache_write_1h", "cache_read"):
        require(positive(config["rates"][key]), "rate missing")
    require(config["rates"]["observed_at"], "dated rate evidence required")
    rates = config["rates"]
    max_rate = max(usd(rates["output"]), *(usd(rates["input"]) * usd(rates[k])
                   for k in ("cache_write_5m", "cache_write_1h", "cache_read")), usd(rates["input"]))
    require(usd(limits["request_usd"]) >= max_rate * limits["tokens_per_request"] / 1000000,
            "request USD allowance cannot cover the conservative token bound")
    for name in ("validate_review", "transcript_usage", "agent_effort"):
        load_ref(config["helpers"][name], roots)
    # Check the actual baseline validator, not just a user-supplied matching hash.
    pinned = subprocess.run(["git", "show", POLICY + ":skills/code-review-publish/scripts/validate_review.py"],
                            cwd=REPO, capture_output=True)
    if pinned.returncode:
        raise OSError("git show pinned validate_review.py failed: " + pinned.stderr.decode("utf-8"))
    require(digest(pinned.stdout) == config["helpers"]["validate_review"]["sha256"], "validator is not the pinned policy helper")
    for name in ("transcript_usage", "agent_effort"):
        require(config["helpers"][name]["sha256"] == digest((HERE.parents[1] / "tools" / (name + ".py")).read_bytes()),
                "meter helper differs from delivered research helper")
    return source, scope, ranges


class Cell:
    def __init__(self, config, scenario, out):
        self.c, self.scenario, self.out = config, scenario, out
        self.events, self.workers, self.freezes, self.batches, self.stages = [], {}, {}, [], []
        self.lock = threading.Lock()
        self.cancel = threading.Event()
        self.requests = self.commands = 0
        self.token_reserved = self.tokens = 0
        self.finder_reserved = self.finder_tokens = 0
        self.rows = []
        self.started = time.monotonic()
        self.timing = dict(completion_mode="render-only", root_dispatched_at=None,
                           payload_validated_at=None, completed_at=None)
        self.gaps, self.claims = [], []
        self.disposition, self.reason = "ready", "Fake cell completed"

    def event(self, kind, **fields):
        with self.lock:
            record = dict(event_id="event-" + str(len(self.events) + 1), observed_at=now(), kind=kind, **fields)
            self.events.append(record)
            write(self.out / "events" / (record["event_id"] + ".json"), record)
            return record

    def packet(self, role, candidates=None, rows=None, discoveries=None):
        task = self.c["primary_task"] if role == "primary" else (
            self.c["finder_task"] if role == "finder" else self.c["verifier_tasks"][self.c["arm"]])
        result = dict(source=self.c["source"], task=task, target=self.c["target"])
        result["source_content"] = self.source
        result["task_content"] = Path(task["uri"]).read_text(encoding="utf-8")
        if role == "finder":
            result.update(scope=self.c["scope"], scope_content=self.scope, limits=self.c["limits"])
        if candidates is not None:
            result["candidates"] = [{key: c[key] for key in
                ("id", "kind", "claim", "trigger", "impact", "change", "anchor", "fix", "citations", "requirements")}
                for c in candidates]
            result["rows"] = [{key: r[key] for key in
                ("id", "kind", "surface", "safety_premise", "asserted_scope", "inspected_evidence")}
                for r in rows]
        if discoveries is not None:
            result["discoveries"] = [{key: c[key] for key in
                ("id", "kind", "claim", "trigger", "impact", "change", "anchor", "fix", "citations", "requirements")}
                for c in discoveries]
        return result

    def helper(self, name, args, input_text=None):
        command = [sys.executable, self.c["helpers"][name]["uri"], *args]
        result = subprocess.run(command, input=input_text, text=True, encoding="utf-8", capture_output=True, timeout=30)
        if result.returncode == 2:
            raise OSError("helper command failed: " + " ".join(command) + ": " + result.stderr)
        require(result.returncode == 0, result.stdout or result.stderr)
        return result.stdout

    def work(self, role, phase, packet):
        if self.cancel.is_set():
            raise Stop("stopped-runtime", "peer worker failed; dispatch cancelled")
        context = self.c["contexts"][role]
        with self.lock:
            previous = self.workers.get(role)
            require(not previous or role == "primary" and previous["state"] == "frozen", "terminated or reused worker context")
            requested = self.c["primary_config"] if role == "primary" else self.c["workers"][self.c["arm"]]
            if previous is None:
                self.workers[role] = dict(context_id=context, role=role, state="new", requests=[], requested=requested,
                                          attempt_id=self.c["attempt_id"], output_store=str(self.out / context),
                                          permitted_read_roots=[self.c["clone_root"]],
                                          permitted_write_roots=[], started_at=now())
            worker = self.workers[role]
            worker["state"] = "running"
        packet_ref = write(self.out / context / (phase + "-input.json"), packet, role.split("-")[-1] + "-private")
        worker["packet_hash"] = packet_ref["sha256"]
        self.event("worker-start", context_id=context, phase=phase, packet=packet_ref, requested=requested)
        response = self.scenario.get(role, {}).get(phase)
        require(isinstance(response, dict), "missing worker response: " + role + "/" + phase)
        responses = response.get("requests", [response])
        require(responses and isinstance(responses, list), "worker needs complete request records")
        report = None
        phase_started = time.monotonic()
        for index, item in enumerate(responses):
            if self.cancel.is_set():
                raise Stop("stopped-runtime", "peer failure cancelled continuation")
            with self.lock:
                self.requests += 1
                self.commands += len(item.get("tools", []))
                allowance = self.c["limits"]["tokens_per_request"]
                if (self.requests > self.c["limits"]["requests"] or self.commands > self.c["limits"]["commands"] or
                        self.tokens + self.token_reserved + allowance > self.c["limits"]["tokens"] or
                        role == "finder" and self.finder_tokens + self.finder_reserved + allowance > self.c["limits"]["finder_tokens"]):
                    raise Stop("stopped-budget", "request, command or conservative token allowance exhausted")
                self.token_reserved += allowance
                if role == "finder":
                    self.finder_reserved += allowance
            request_id = context + "-" + phase + "-" + str(index)
            reservation = usd(self.c["limits"]["request_usd"]) + usd(self.c["limits"]["headroom_usd"])
            try:
                transact(self.ledger, "reserve", request_id, reservation, "review", self.c["attempt_id"],
                         self.c["limits"]["attempt_usd"], evidence=packet_ref["sha256"])
            except Violation as exc:
                raise Stop("stopped-budget", str(exc)) from exc
            remaining = float(self.c["limits"]["wall_seconds"]) - (time.monotonic() - self.started)
            phase_remaining = float(self.c["limits"]["finder_seconds" if role == "finder" else "worker_seconds"]) - (time.monotonic() - phase_started)
            timeout = min(remaining, phase_remaining)
            if timeout <= 0:
                raise Stop("stopped-budget", "root or worker phase time limit exhausted")
            ranges = [dict(r, path=str(Path(self.c["clone_root"]) / r["path"])) for r in self.ranges] if role == "finder" else None
            invocation = dict(packet=packet, response=item, requested=requested, request_id=request_id,
                              read_roots=[self.c["clone_root"]], ranges=ranges)
            request_ref = write(self.out / context / (request_id + "-request.json"), invocation, "coordinator-only")
            self.event("request-dispatch", context_id=context, request_id=request_id, input=request_ref,
                       reservation_id=request_id, timeout_seconds=timeout)
            try:
                with subprocess.Popen([sys.executable, str(HERE / "fake_worker.py")], stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8") as process:
                    deadline = time.monotonic() + timeout
                    first = True
                    while True:
                        try:
                            stdout, error = process.communicate(json.dumps(invocation) if first else None,
                                                                timeout=min(0.05, max(0.001, deadline - time.monotonic())))
                            break
                        except subprocess.TimeoutExpired:
                            first = False
                            if self.cancel.is_set() or time.monotonic() >= deadline:
                                process.kill()
                                stdout, error = process.communicate()
                                raise subprocess.TimeoutExpired(process.args, timeout, stdout.encode("utf-8"), error.encode("utf-8"))
                    raw = stdout.encode("utf-8")
                    require(process.returncode == 0, "fake worker failed: " + error + stdout)
            except subprocess.TimeoutExpired as exc:
                write(self.out / context / (request_id + ".jsonl"), exc.stdout or b"", "coordinator-only")
                self.event("worker-cancelled", context_id=context, request_id=request_id, reason="timeout; process killed and reaped")
                self.cancel.set()
                raise Stop("stopped-budget", "worker/root time limit; usage unavailable, reservation retained") from exc
            transcript = write(self.out / context / (request_id + ".jsonl"), raw, "coordinator-only")
            worker["requests"].append(dict(request_id=request_id, input=request_ref, transcript=transcript))
            records = []
            try:
                records = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
                assistant = [r for r in records if r["type"] == "assistant"]
                require(len(assistant) == 1 and assistant[0]["requestId"] == request_id, "missing or duplicate request usage")
                usage = assistant[0]["message"]["usage"]
                for key in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
                    require(type(usage[key]) is int and usage[key] >= 0, "invalid token usage")
                token_count = sum(usage[k] for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
                with self.lock:
                    self.token_reserved -= allowance
                    self.tokens += token_count
                    if role == "finder":
                        self.finder_reserved -= allowance
                        self.finder_tokens += token_count
                rates = self.c["rates"]
                meter = json.loads(self.helper("transcript_usage", [transcript["uri"], "--prices", rates["input"] + "," + rates["output"],
                    "--cache-write-mult", rates["cache_write_5m"], "--cache-write-1h-mult", rates["cache_write_1h"],
                    "--cache-read-mult", rates["cache_read"], "--json"]))
                meter_ref = write(self.out / context / (request_id + "-usage.json"), meter)
                cost = usd(meter["total"]["cost_bounds"]["low"])
                unknown = usd(meter["total"]["cost_bounds"]["high"]) - cost
                transact(self.ledger, "settle", request_id, cost, uncertainty=unknown, evidence=meter_ref["sha256"])
                worker["requests"][-1]["meter"] = meter_ref
                if token_count > self.c["limits"]["tokens_per_request"]:
                    raise Stop("stopped-budget", "token allowance exceeded")
                observed = dict(model=assistant[0]["message"].get("model"), effort=assistant[0].get("effort"))
                state = "unavailable" if None in observed.values() else (
                    "matched" if all(observed[k] == requested[k] for k in observed) else "mismatched")
                self.event("observed-settings", context_id=context, request_id=request_id, requested=requested,
                           observed=observed, state=state, transcript=transcript)
                require(state == "matched", "worker settings " + state)
                effort = self.helper("agent_effort", [transcript["uri"], "--expect-model", requested["model"], "--expect-effort", requested["effort"]])
                write(self.out / context / (request_id + "-effort.txt"), effort.encode("utf-8"))
                complete = [r for r in records if r["type"] == "result"]
                require(len(complete) == 1 and complete[0]["complete"] is True and isinstance(complete[0]["report"], dict),
                        "partial or missing worker report")
                report = complete[0]["report"]
                # Every continuation output is retained, even though only the final one freezes.
                write(self.out / context / (request_id + "-report.json"), report)
            except Stop:
                self.cancel.set()
                raise
            except (ValueError, KeyError, TypeError) as exc:
                self.cancel.set()
                raise Stop("stopped-invalid", "incomplete/invalid stream: " + str(exc)) from exc
        require(report.get("complete") is True, "report did not declare a complete record")
        if phase == "discovery":
            require(report.get("pass_complete") is True and isinstance(report.get("claims"), list), "discovery pass incomplete")
            if role == "primary":
                require(report.get("manifest_complete") is True and report.get("first_falsification_complete") is True,
                        "primary cannot freeze before full manifest and first falsification")
        frozen = write(self.out / context / (phase + "-frozen.json"), report,
                       "finder-private" if role == "finder" else "primary-private" if role == "primary" else "verifier-private")
        freeze = self.event("freeze", freeze_id=context + "-" + phase, context_id=context, role=role, phase=phase, input_hash=packet_ref["sha256"], output=frozen)
        self.freezes[(role, phase)] = freeze
        worker["state"] = "frozen" if role == "primary" else "terminated"
        worker["frozen_at"] = freeze["observed_at"]
        worker["terminated_at"] = now() if role != "primary" else None
        self.event("worker-end", context_id=context, phase=phase, state=worker["state"])
        return report

    def evidence(self, ref):
        require(ref["availability"] in ("inspected", "not-inspected", "unavailable", "unknown"), "invalid evidence availability")
        require(ref["locator"] and ref["observed_at"] and ref["reason"], "evidence needs locator, time and reason")
        load_ref(ref["artifact"], [*map(lambda p: Path(p).resolve(), self.c["permitted_input_roots"]), self.out])
        if ref["availability"] == "not-inspected":
            require(ref.get("complete_access_trace") is True, "not-inspected needs positive omission evidence")

    def stage(self, report, phase):
        claims = report["claims"]
        rows = report["rows"]
        ids = [c["id"] for c in claims] + [r["id"] for r in rows]
        require(len(set(ids)) == len(ids), "duplicate claim/row IDs")
        source_ids = {}
        for (role, pass_name), freeze in self.freezes.items():
            if pass_name == "discovery":
                source_ids[role] = {c["id"] for c in json.loads(Path(freeze["output"]["uri"]).read_text(encoding="utf-8"))["claims"]}
        for claim in claims:
            require(claim["origin"] in ("primary", "finder", "both", "unknown"), "invalid origin")
            require(claim["canonical_id"] == claim["id"] and claim["dedup_decision"], "model-authored canonical identity required")
            require(claim["sources"], "claim source identity missing")
            for source in claim["sources"]:
                require(source["id"] in source_ids.get(source["role"], set()), "claim source ID does not resolve")
                require(source["freeze_id"] == self.freezes[(source["role"], "discovery")]["freeze_id"], "source freeze reference mismatch")
            roles = {s["role"] for s in claim["sources"]}
            require(claim["origin"] == "unknown" or roles == ({"primary", "finder"} if claim["origin"] == "both" else {claim["origin"]}),
                    "claimed origin and explicit sources differ")
            require(claim["admission"]["disposition"] in ("survives", "rejected", "duplicate", "question", "observation", "unknown"), "invalid admission")
            require(claim["admission"]["original_text"] and claim["admission"]["evidence"], "preserve admission evidence and original text")
            for ref in claim["inspected_evidence"]:
                self.evidence(ref)
            require(type(claim["verification"]["required"]) is bool and claim["verification"]["trigger_evidence"], "explicit verification decision required")
            require(claim["verification"]["disposition"] in (
                "not-required-policy", "confirmed", "refuted", "unresolved", "missing-required-dispatch",
                "missing-required-ruling", "pending", "unknown"), "invalid verification disposition")
            require(claim["publication"]["disposition"] in ("rendered", "withheld", "not-admitted", "pending", "unknown"), "invalid publication disposition")
            if claim["admission"]["disposition"] == "rejected":
                require(all(claim.get(k) for k in ("safety_premise", "asserted_scope", "disposition_evidence")), "acquittal stage evidence missing")
        for row in rows:
            require(all(k in row for k in ("kind", "surface", "safety_premise", "asserted_scope", "disposition_evidence",
                                          "triggers", "required_batches", "received_batches", "rulings", "fidelity")), "coverage record incomplete")
            for ref in row["inspected_evidence"]:
                self.evidence(ref)
        ref = write(self.out / (phase + "-stages.json"), report)
        self.stages.append(ref)
        self.claims = claims
        self.rows = rows
        return claims, rows

    def batch(self, decision, claims, rows, ordinal):
        required_claims = {c["id"] for c in claims if c["verification"]["required"] and
                           c["admission"]["disposition"] == "survives" and ordinal in c["verification"]["required_batches"]}
        required_rows = {r["id"] for r in rows if ordinal in r["required_batches"]}
        if not decision["dispatch"]:
            require(decision["phase"] == ordinal and decision["baseline_clause"] and decision["evidence"], "no-batch evidence missing")
            require(decision["reason"] in ("no-eligible-trigger", "no-new-required-work", "policy-permitted-omission", "required-unavailable", "unknown"), "invalid no-batch reason")
            require(set(decision["survivor_ids"]) == {c["id"] for c in claims if c["admission"]["disposition"] == "survives"}, "no-batch survivor IDs differ")
            require(set(decision["affected_row_ids"]) <= {r["id"] for r in rows}, "unknown no-batch row")
            require(all(type(decision["triggers"][k]) is bool for k in ("candidate", "related", "zero_survivor", "high_risk")), "trigger decisions missing")
            require(not any(decision["triggers"][k] for k in ("candidate", "related", "zero_survivor")) or
                    decision["reason"] in ("required-unavailable", "unknown"), "positive trigger contradicts no-batch reason")
            if required_claims or required_rows:
                require(decision["reason"] == "required-unavailable", "required dispatch mislabeled as policy omission")
                self.gaps.append(dict(kind="missing-required-dispatch", phase=ordinal, ids=sorted(required_claims | required_rows)))
            self.event("no-batch", decision=decision)
            return
        require(len(self.batches) < 2 and not any(b["ordinal"] == ordinal for b in self.batches), "verification batch cap")
        require(ordinal != "follow-up" or any(b["ordinal"] == "initial" for b in self.batches), "follow-up without initial batch")
        require(decision["mode"] in ("candidate", "clean-verdict", "mixed", "related-acquittal"), "invalid batch mode")
        require(ordinal != "initial" or decision["mode"] != "related-acquittal", "related-only cannot trigger initial batch")
        require(decision["baseline_clause"] and decision["trigger_evidence"], "batch needs explicit baseline trigger")
        candidate_ids, row_ids = decision["candidate_ids"], decision["row_ids"]
        require(len(candidate_ids) == len(set(candidate_ids)) and len(row_ids) == len(set(row_ids)), "duplicate batch IDs")
        require(required_claims <= set(candidate_ids) and required_rows <= set(row_ids), "batch omits required ID")
        require(set(candidate_ids) <= {c["id"] for c in claims} and set(row_ids) <= {r["id"] for r in rows}, "batch references unknown ID")
        packet = self.packet(ordinal + "-verifier", [c for c in claims if c["id"] in candidate_ids],
                             [r for r in rows if r["id"] in row_ids])
        result = self.work(ordinal + "-verifier", "verification", packet)
        rulings = result["rulings"]
        require(len({r["id"] for r in rulings}) == len(rulings), "duplicate ruling")
        for ruling in rulings:
            require(ruling["id"] in candidate_ids + row_ids and ruling["evidence"] and ruling["scope"], "invalid or uncited ruling")
            require(ruling["verdict"] in (("confirmed", "refuted") if ruling["id"] in candidate_ids else ("holds", "re-open")), "wrong ruling kind")
            if ruling["verdict"] == "refuted":
                require(ruling["basis"] in ("contradicted", "prevented", "intentional", "pre-existing", "no-consequence", "unresolved"), "invalid refutation basis")
                require(ruling["basis"] != "unresolved" or ruling.get("settling_fact"), "unresolved refutation lacks settling fact")
        if decision["mode"] in ("clean-verdict", "mixed"):
            require(result.get("conclusion"), "clean batch conclusion missing")
        missing = set(candidate_ids + row_ids) - {r["id"] for r in rulings}
        if missing:
            self.gaps.append(dict(kind="missing-required-ruling", phase=ordinal, ids=sorted(missing)))
        batch = dict(batch_id="batch-" + ordinal, ordinal=ordinal, context_id=self.c["contexts"][ordinal + "-verifier"],
                     decision=decision, rulings=rulings, complete=not missing,
                     packet=packet,
                     freeze_id=self.freezes[(ordinal + "-verifier", "verification")]["event_id"])
        self.batches.append(batch)
        self.event("batch-return", batch=batch)

    def execute(self):
        require("invalid_input" not in self.c, "config must be a JSON object")
        self.ledger = Path(self.c["ledger"])
        ledger = json.loads(self.ledger.read_text(encoding="utf-8"))
        totals(ledger)
        self.source, self.scope, self.ranges = validate_config(self.c, self.out)
        if self.c["runtime"] != "fake":
            raise Stop("stopped-runtime", "Claude worker settings, file/process/network isolation, cancellation and conservative token bounds remain unprobed; no paid dispatch")
        require(ledger.get("synthetic") is True, "fake runs require a disposable synthetic ledger")
        require(self.c.get("isolation") == "finite-fake-tools", "normal settings lack supported independence")
        require(set(self.scenario) <= set(self.c["contexts"]), "scenario attempts an unconfigured worker")
        for role, phases in self.scenario.items():
            permitted = {"discovery", "admission", "reconcile", "final"} if role == "primary" else (
                {"discovery"} if role == "finder" else {"verification"})
            require(set(phases) <= permitted, "finder restart or unsupported worker phase")
        try:
            attempt_event(self.ledger, self.c)
        except Violation as exc:
            raise Stop("stopped-budget", str(exc)) from exc
        self.timing["root_dispatched_at"] = now()
        self.event("root-dispatch", attempt_id=self.c["attempt_id"])
        if self.c["arm"] == "C":
            with ThreadPoolExecutor(max_workers=2) as pool:
                primary = pool.submit(self.work, "primary", "discovery", self.packet("primary"))
                finder = pool.submit(self.work, "finder", "discovery", self.packet("finder"))
                # Consume both results so no exception or reservation is lost.
                errors, results = [], []
                for future in (primary, finder):
                    try:
                        results.append(future.result())
                    except Exception as exc:
                        self.cancel.set()
                        errors.append(exc)
                if errors:
                    raise errors[0]
            self.event("cross-feed", source_context=self.c["contexts"]["finder"], destination_context=self.c["contexts"]["primary"],
                       primary_freeze=self.freezes[("primary", "discovery")]["event_id"],
                       finder_freeze=self.freezes[("finder", "discovery")]["event_id"],
                       finder_termination=next(e["event_id"] for e in self.events if e["kind"] == "worker-end" and e["context_id"] == self.c["contexts"]["finder"]),
                       released_hash=digest(encode(self.packet("primary", discoveries=results[1]["claims"]))))
            admitted = self.work("primary", "admission", self.packet("primary", discoveries=results[1]["claims"]))
        else:
            admitted = self.work("primary", "discovery", self.packet("primary"))
        claims, rows = self.stage(admitted, "admission")
        self.batch(admitted["initial"], claims, rows, "initial")
        reconciled = self.work("primary", "reconcile", dict(self.packet("primary"), batches=self.batches))
        claims, rows = self.stage(reconciled, "reconcile")
        self.batch(reconciled["follow-up"], claims, rows, "follow-up")
        final = self.work("primary", "final", dict(self.packet("primary"), batches=self.batches))
        require(final["completion"] in ("complete", "incomplete"), "invalid completion disposition")
        claims, rows = self.stage(final, "final")
        pending = final["pending_required_ids"]
        require(set(pending) <= {r["id"] for r in rows} | {c["id"] for c in claims}, "unknown pending ID")
        if pending:
            self.gaps.append(dict(kind="required-unavailable-at-cap", ids=pending))
        published = []
        for claim in claims:
            if claim["publication"]["disposition"] == "rendered":
                require(claim["admission"]["disposition"] == "survives", "rejected claim cannot render")
                if claim["verification"]["required"]:
                    verdicts = [r for b in self.batches for r in b["rulings"] if r["id"] == claim["id"]]
                    require(verdicts and verdicts[-1]["verdict"] == "confirmed" and claim["id"] not in pending,
                            "unconfirmed required claim cannot render")
                    supplied = [c for b in self.batches for c in b["packet"]["candidates"] if c["id"] == claim["id"]]
                    require(supplied and supplied[-1] == self.packet("initial-verifier", [claim], [])["candidates"][0],
                            "changed claim needs fresh verification")
                published.append(claim["publication"]["payload_item_id"])
        if final.get("payload") is not None:
            payload = final["payload"]
            finding_ids = [re.search(r"\bid=([^\s>]+)", item["trailer"]).group(1)
                           for item in payload["items"] if item["type"] == "finding"]
            require(sorted(finding_ids) == sorted(published), "payload and publication records differ")
            require(not self.gaps or final["completion"] == "incomplete", "mandatory coverage gaps cannot become complete")
            rendered = self.helper("validate_review", ["--emit-batch"], json.dumps(payload))
            require(json.loads(rendered)["commit_id"] == self.source["head_oid"], "rendered payload targets a different head")
            self.timing["payload_validated_at"] = now()
            self.payload = write(self.out / "payload.json", payload)
            write(self.out / "rendered.json", json.loads(rendered))
            self.timing["completed_at"] = now()
        else:
            require(final.get("payload_absence_reason"), "missing payload requires a reason")
        self.reason = "Fake cell delivered; " + final["completion"]

    def close(self, disposition, reason):
        stopped = now() if disposition != "ready" else None
        if self.timing["root_dispatched_at"] is not None:
            attempt_event(self.ledger, self.c, disposition)
        write(self.out / "timing.json", self.timing)
        try:
            snapshot = json.loads((self.ledger if hasattr(self, "ledger") else HERE.parent / "ledger.json").read_text(encoding="utf-8"))
            totals(snapshot)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            snapshot = dict(actual_usd="unknown", reserved_usd="unknown", uncertainty_usd="unknown",
                            evidence_gap="Ledger unreadable or unreconciled: " + str(exc))
        ledger_ref = write(self.out / "ledger-snapshot.json", snapshot)
        attempted = self.timing["root_dispatched_at"] is not None
        cells = self.c.get("ordered_cells", [f"slot-{slot}-{arm}-replicate-{rep}" for slot in range(1, 5) for arm in "ABC" for rep in (1, 2)])
        available = self.claims or [
            dict(origin=role, admission="unknown", source_claim=claim, freeze=freeze["output"])
            for (role, phase), freeze in self.freezes.items() if phase == "discovery"
            for claim in json.loads(Path(freeze["output"]["uri"]).read_text(encoding="utf-8"))["claims"]]
        for worker in self.workers.values():
            if not worker.get("terminated_at"):
                worker.update(state="terminated", terminated_at=now())
                self.event("worker-termination", context_id=worker["context_id"], reason="attempt closeout")
        record = dict(schema_version=SCHEMA, artifact_id="issue-147-" + self.c.get("attempt_id", "no-cell"),
                      stage="adapter-fake" if self.c.get("runtime") == "fake" else "adapter-runtime", disposition=disposition,
                      created_at=now(), stopped_at=stopped, reason=reason, evidence=[artifact(self.out / "config.json")],
                      ledger_ref=ledger_ref, actual_usd=snapshot["actual_usd"], reserved_usd=snapshot["reserved_usd"],
                      uncertainty_usd=snapshot["uncertainty_usd"], available_claims=available,
                      unattempted_cells=[dict(cell_id=c, reason=reason) for c in cells if not attempted or c != self.c.get("cell_id")],
                      dispatch_authorized=False, next_stage={"tickets": [149, 150, 151, 152, 153], "work": "Probe controls before dispatch; propagate stop and grade available claims only."})
        attempt = dict(schema_version=SCHEMA, attempt_id=self.c.get("attempt_id") if attempted else None,
                       cell_id=self.c.get("cell_id") if attempted else None, config_hash=digest(encode(self.c)),
                       source=self.c.get("source"), scope=self.c.get("scope"), stopped_at=stopped,
                       workers=self.workers, events=self.events, batches=self.batches, stages=self.stages,
                       gaps=self.gaps, validity="synthetic-only" if disposition == "ready" else disposition,
                       final_payload=getattr(self, "payload", None), payload_absence_reason=None if hasattr(self, "payload") else reason)
        write(self.out / "attempt.json", attempt)
        # Record actual routing alongside unchanged model-authored stage snapshots.
        write(self.out / "coverage.json", [
            dict(id=item["id"], declared=item.get("verification", item),
                 received_batches=[b["batch_id"] for b in self.batches
                                   if item["id"] in b["decision"]["candidate_ids"] + b["decision"]["row_ids"]],
                 returned_rulings=[r for b in self.batches for r in b["rulings"] if r["id"] == item["id"]],
                 gaps=[g for g in self.gaps if item["id"] in g["ids"]])
            for item in self.claims + self.rows])
        transcripts = sorted(self.out.glob("*/*.jsonl"))
        if transcripts and self.c.get("helpers"):
            rates = self.c["rates"]
            try:
                metered = self.helper("transcript_usage", [*map(str, transcripts), "--prices", rates["input"] + "," + rates["output"],
                    "--cache-write-mult", rates["cache_write_5m"], "--cache-write-1h-mult", rates["cache_write_1h"],
                    "--cache-read-mult", rates["cache_read"], "--timing", str(self.out / "timing.json"), "--json"])
                write(self.out / "usage.json", json.loads(metered))
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                write(self.out / "meter-failure.json", dict(reason=str(exc)))
        write(self.out / "meter-status.json", dict(synthetic=True, rates=self.c.get("rates"),
              missing_usage_bound_usd=snapshot["reserved_usd"], uncertain_usd=snapshot["uncertainty_usd"],
              root_elapsed_seconds=(time.monotonic() - self.started) if attempted else None,
              censored=stopped is not None, tokens=self.tokens, reserved_tokens=self.token_reserved,
              tool_charges_usd="0", tool_charge_reason="Finite fake read tools have no paid services; real runtime unsupported"))
        write(self.out / "handoff.json", record)
        if stopped:
            write(self.out / "stop.json", record)
        write(self.out / "outcome-join.json", dict(access="evaluator-only", truth_version=None, ruling_ref=None,
              attempt_id=attempt["attempt_id"], payload_item_id=None, defect_id=None, recovered=None,
              sufficient_outcome="unknown", action_errors=None, priority_errors=None, false_clean=None,
              reason="Independent grading owns every outcome judgment."))
        write(self.out / "manifest.json", {str(p.relative_to(self.out)): digest(p.read_bytes()) for p in sorted(self.out.rglob("*")) if p.is_file()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--scenario", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--runtime", choices=("fake", "claude"), default="fake")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        scenario = json.loads(args.scenario.read_text(encoding="utf-8"))
        args.out.mkdir(parents=True, exist_ok=False)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not isinstance(config, dict):
        config = {"invalid_input": config}
    config["runtime"] = args.runtime
    out = args.out.resolve()
    write(out / "config.json", config)
    write(out / "scenario.json", scenario)
    cell = Cell(config, scenario, out)
    disposition, reason, rc = "ready", "Fake cell delivered", 0
    try:
        cell.execute()
        reason = cell.reason
    except Stop as exc:
        disposition, reason, rc = exc.disposition, str(exc), 1
    except (ValueError, KeyError, TypeError) as exc:
        disposition, reason, rc = "stopped-invalid", str(exc), 1
    except (OSError, subprocess.SubprocessError) as exc:
        disposition, reason, rc = "stopped-runtime", str(exc), 2
    cell.close(disposition, reason)
    print(reason, file=sys.stderr if rc == 2 else sys.stdout)
    return rc


if __name__ == "__main__":
    sys.exit(main())
