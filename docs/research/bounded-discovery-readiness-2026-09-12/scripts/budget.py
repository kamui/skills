#!/usr/bin/env python3
"""Reserve, settle, freeze and stop a prospective bounded-discovery ledger.

Usage: python3 scripts/budget.py LEDGER reserve|settle --id ID --amount USD
       [--phase pre-freeze|review|grading|closeout] [--attempt ID]
       [--attempt-cap USD] [--uncertainty USD] [--evidence REF] [--ticket N]
       python3 scripts/budget.py LEDGER cap-freeze --amount USD --reserve USD
       --evidence REF [--ticket N]
       python3 scripts/budget.py LEDGER stop --reason TEXT --evidence REF --ticket N
This prospective copy preserves the #149-pinned budget.py unchanged. A stop
blocks new attempts, pre-freeze/review reservations and cap freezing. Existing
reservations can settle and attempts can close; protected grading/closeout
reservations remain available. It neither cancels processes nor proves shutdown.
Input: DESIGN.md BudgetEvent ledger; pre-freeze permits an unset cap/reserve.
Reserve amounts include request/cancellation headroom. Settlement amount is actual
cost; uncertainty retains part of the reservation. Re-settlement is prohibited.
cap-freeze is #149's gate: it sets the frozen total cap and the protected
grading/closeout reserve once, and every later review-phase reservation is
checked against them. All work is serialised by a POSIX lock.
Exit: 0 success, 1 content/budget violation on stdout, 2 unreadable input on stderr.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import fcntl
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import uuid


class Violation(ValueError):
    pass


def usd(value, signed=False):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise Violation("invalid USD amount") from exc
    if not result.is_finite() or not signed and result < 0:
        raise Violation("USD amounts must be finite" + ("" if signed else " and nonnegative"))
    return result


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def locked(path):
    # Lock a stable inode, not the snapshot replaced by os.replace below.
    with open(str(path) + ".lock", "a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def save(path, data):
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".ledger-")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def totals(data):
    actual = reserved = uncertain = pre_actual = pre_reserved = Decimal(0)
    prior = None
    ids = set()
    reservations = {}
    protected_used = Decimal(0)
    stopped = False
    for event in data["events"]:
        if event["event_id"] in ids or event["previous_event_id"] != prior:
            raise Violation("broken budget event chain")
        ids.add(event["event_id"])
        prior = event["event_id"]
        a = usd(event["actual_delta_usd"])
        r = usd(event["reservation_delta_usd"], signed=True)
        u = usd(event["uncertainty_usd"])
        if stopped and (event["operation"] in ("stop", "attempt-open", "cap-freeze") or
                        event["operation"] == "reserve" and
                        event["phase"] not in ("grading", "closeout")):
            raise Violation("new work after ledger stop")
        if event["operation"] == "stop":
            if not event.get("reason") or not event.get("rate_usage_evidence"):
                raise Violation("stop requires reason and evidence")
            stopped = True
        actual += a
        reserved += r
        uncertain += u
        if event["phase"] == "pre-freeze":
            pre_actual += a
            pre_reserved += r
        if event["operation"] == "reserve":
            rid = event["reservation_id"]
            if rid in reservations or r <= 0 or a or u:
                raise Violation("invalid or duplicate reservation")
            reservations[rid] = dict(event, remaining=r, settled=False)
            if event["phase"] in ("grading", "closeout"):
                protected_used += r
        elif event["operation"] == "settle":
            reservation = reservations.get(event["reservation_id"])
            if not reservation or reservation["settled"]:
                raise Violation("unknown or already settled reservation")
            if event["phase"] != reservation["phase"] or event["attempt_id"] != reservation["attempt_id"]:
                raise Violation("settlement changed reservation ownership")
            if r != -reservation["remaining"] or a + u > -r:
                raise Violation("settlement exceeds reserved bound")
            reservation.update(remaining=Decimal(0), settled=True)
            if event["phase"] in ("grading", "closeout"):
                protected_used -= -r - a - u
        elif event["operation"] not in ("open", "attempt-open", "attempt-close", "cap-freeze", "stop") or a or r or u:
            raise Violation("unsupported budget event operation")
    values = dict(actual_usd=actual, reserved_usd=reserved, uncertainty_usd=uncertain,
                  pre_freeze_actual_usd=pre_actual, pre_freeze_reserved_usd=pre_reserved)
    for key, value in values.items():
        if usd(data[key]) != value:
            raise Violation("budget snapshot does not reconcile: " + key)
    return values, reservations, protected_used


def attempt_event(path, config, close=None):
    """Claim a unique cell/context set atomically; close keeps its history."""
    path = Path(path)
    with locked(path):
        data = json.loads(path.read_text(encoding="utf-8"))
        totals(data)
        starts = [e for e in data["events"] if e["operation"] == "attempt-open"]
        ends = {e["attempt_id"]: e for e in data["events"] if e["operation"] == "attempt-close"}
        aid = config["attempt_id"]
        if close is None:
            require_running(data)
            if any(e["attempt_id"] == aid for e in starts):
                raise Violation("attempt ID already used")
            if len(starts) >= min(data["attempt_limit"], 27) or len(starts) - len(ends) >= 2:
                raise Violation("attempt or simultaneous cell cap")
            used_contexts = {c for e in starts for c in e["contexts"]}
            if used_contexts.intersection(config["contexts"].values()):
                raise Violation("context ID used by a previous attempt")
            predecessor = config["predecessor"]
            previous_cell = [e for e in starts if e["cell_id"] == config["cell_id"]]
            if predecessor:
                replacements = sum(bool(e["predecessor"]) for e in starts)
                if replacements >= min(data["replacement_limit"], 3):
                    raise Violation("replacement cap")
                if not previous_cell or previous_cell[-1]["attempt_id"] != predecessor:
                    raise Violation("replacement must name the latest same-cell attempt")
                end = ends.get(predecessor)
                if not end or end["disposition"] != "stopped-invalid":
                    raise Violation("only documented protocol/input invalidity earns replacement")
                if not config.get("replacement_evidence"):
                    raise Violation("replacement evidence required")
                if config["replacement_ordinal"] != previous_cell[-1]["replacement_ordinal"] + 1:
                    raise Violation("replacement ordinal mismatch")
            elif previous_cell or config["replacement_ordinal"] != 0:
                raise Violation("cell already attempted or replacement predecessor missing")
        elif not any(e["attempt_id"] == aid for e in starts) or aid in ends:
            raise Violation("unknown or already closed attempt")
        event = dict(event_id=str(uuid.uuid4()), previous_event_id=data["events"][-1]["event_id"],
                     observed_at=now(), ticket=147, actor=data["owner"], phase="review",
                     operation="attempt-close" if close else "attempt-open", attempt_id=aid,
                     helper_id=None, request_refs=[], reservation_id=None, actual_delta_usd="0",
                     reservation_delta_usd="0", uncertainty_usd="0", rate_usage_evidence=[],
                     reason=close or "Claim fresh attempt before root dispatch",
                     disposition=close, cell_id=config["cell_id"], contexts=list(config["contexts"].values()),
                     predecessor=config["predecessor"], replacement_ordinal=config["replacement_ordinal"])
        data["events"].append(event)
        totals(data)
        save(path, data)
        return event


def transact(path, operation, rid, amount, phase="review", attempt=None,
             attempt_cap=None, uncertainty="0", evidence=None, ticket=147):
    path = Path(path)
    amount, uncertainty = usd(amount), usd(uncertainty)
    if phase not in ("pre-freeze", "review", "grading", "closeout"):
        raise Violation("invalid budget phase")
    if not rid or not evidence:
        raise Violation("reservation ID and evidence are required")
    with locked(path):
        data = json.loads(path.read_text(encoding="utf-8"))
        values, reservations, used = totals(data)
        if operation == "reserve" and phase not in ("grading", "closeout"):
            require_running(data)
        if operation == "settle":
            reservation = reservations.get(rid)
            if not reservation or reservation["settled"]:
                raise Violation("unknown or already settled reservation")
            phase, attempt = reservation["phase"], reservation["attempt_id"]
        frozen = data["frozen_total_cap_usd"]
        reserve = data["grading_closeout_reserve_usd"]
        if phase != "pre-freeze" and (frozen is None or reserve is None):
            raise Violation("frozen cap and grading/closeout reserve must be set before " + phase)
        cap = min(usd(data["total_ceiling_usd"]),
                  usd(data["total_ceiling_usd"] if frozen is None else frozen), Decimal(150))
        protected = usd("0" if reserve is None else reserve) - used
        if protected < 0:
            raise Violation("protected reserve overdrawn")
        if operation == "reserve":
            if rid in reservations or amount <= 0 or uncertainty:
                raise Violation("reservation must be new, positive and include its uncertainty")
            occupied = values["actual_usd"] + values["reserved_usd"] + values["uncertainty_usd"]
            transfer = amount if phase in ("grading", "closeout") else Decimal(0)
            if transfer > protected or occupied + protected - transfer + amount > cap:
                raise Violation("total budget or protected reserve cannot fit reservation")
            pre_uncertain = sum((usd(e["uncertainty_usd"]) for e in data["events"]
                                 if e["phase"] == "pre-freeze"), Decimal(0))
            if phase == "pre-freeze" and (values["pre_freeze_actual_usd"] +
                    values["pre_freeze_reserved_usd"] + pre_uncertain + amount >
                    min(usd(data["pre_freeze_ceiling_usd"]), Decimal(15))):
                raise Violation("pre-freeze budget cannot fit reservation")
            if attempt:
                spent = sum((usd(e["actual_delta_usd"]) + usd(e["reservation_delta_usd"], signed=True) +
                             usd(e["uncertainty_usd"]) for e in data["events"]
                             if e["attempt_id"] == attempt), Decimal(0))
                if attempt_cap is None or spent + amount > usd(attempt_cap):
                    raise Violation("attempt budget cannot fit reservation")
            actual_delta, reservation_delta = Decimal(0), amount
        elif operation == "settle":
            if amount + uncertainty > reservation["remaining"]:
                raise Violation("actual plus uncertainty exceeds reservation; retain bound and stop")
            actual_delta, reservation_delta = amount, -reservation["remaining"]
        else:
            raise Violation("unsupported operation")
        event = dict(event_id=str(uuid.uuid4()), previous_event_id=data["events"][-1]["event_id"],
                     observed_at=now(), ticket=ticket, actor=data["owner"], phase=phase,
                     operation=operation, attempt_id=attempt, helper_id=None,
                     request_refs=[evidence], reservation_id=rid,
                     actual_delta_usd=str(actual_delta), reservation_delta_usd=str(reservation_delta),
                     uncertainty_usd=str(uncertainty), rate_usage_evidence=[evidence],
                     reason="Conservative reservation" if operation == "reserve" else "Usage settlement")
        data["events"].append(event)
        for key, delta in (("actual_usd", actual_delta), ("reserved_usd", reservation_delta),
                           ("uncertainty_usd", uncertainty)):
            data[key] = str(values[key] + delta)
        if phase == "pre-freeze":
            data["pre_freeze_actual_usd"] = str(values["pre_freeze_actual_usd"] + actual_delta)
            data["pre_freeze_reserved_usd"] = str(values["pre_freeze_reserved_usd"] + reservation_delta)
        totals(data)
        save(path, data)
        return event


def freeze_cap(path, cap, reserve, evidence, ticket=149):
    """Set the frozen total cap and the protected grading/closeout reserve, once."""
    path = Path(path)
    cap, reserve = usd(cap), usd(reserve)
    if not evidence:
        raise Violation("evidence is required")
    with locked(path):
        data = json.loads(path.read_text(encoding="utf-8"))
        values, _, _ = totals(data)
        require_running(data)
        if data["frozen_total_cap_usd"] is not None or data["grading_closeout_reserve_usd"] is not None:
            raise Violation("the cap and reserve are already frozen; append a dated adjustment instead")
        if reserve <= 0:
            raise Violation("the grading/closeout reserve must be positive")
        ceiling = min(usd(data["total_ceiling_usd"]), Decimal(150))
        if cap > ceiling:
            raise Violation("the frozen cap cannot exceed the total ceiling")
        occupied = values["actual_usd"] + values["reserved_usd"] + values["uncertainty_usd"]
        if occupied > cap:
            raise Violation("the frozen cap cannot discard sunk spend, reservations or uncertainty")
        if occupied + reserve > cap:
            raise Violation("the frozen cap cannot hold the incurred spend and the protected reserve")
        event = dict(event_id=str(uuid.uuid4()), previous_event_id=data["events"][-1]["event_id"],
                     observed_at=now(), ticket=ticket, actor=data["owner"], phase="pre-freeze",
                     operation="cap-freeze", attempt_id=None, helper_id=None,
                     request_refs=[evidence], reservation_id=None, actual_delta_usd="0",
                     reservation_delta_usd="0", uncertainty_usd="0", rate_usage_evidence=[evidence],
                     reason="Freeze the total cap and the protected grading/closeout reserve",
                     frozen_total_cap_usd=str(cap), grading_closeout_reserve_usd=str(reserve))
        data["events"].append(event)
        data["frozen_total_cap_usd"] = str(cap)
        data["grading_closeout_reserve_usd"] = str(reserve)
        totals(data)
        save(path, data)
        return event


def require_running(data):
    if any(event["operation"] == "stop" for event in data["events"]):
        raise Violation("ledger is stopped; only settlement, attempt closure and protected closeout are allowed")


def stop(path, reason, evidence, ticket):
    """Append one immutable global stop without releasing any exposure."""
    if not reason or not reason.strip() or not evidence or not evidence.strip() or not ticket or ticket < 1:
        raise Violation("stop requires reason, evidence and producing ticket")
    path = Path(path)
    with locked(path):
        data = json.loads(path.read_text(encoding="utf-8"))
        totals(data)
        require_running(data)
        event = dict(event_id=str(uuid.uuid4()), previous_event_id=data["events"][-1]["event_id"],
                     observed_at=now(), ticket=ticket, actor=data["owner"], phase="closeout",
                     operation="stop", attempt_id=None, helper_id=None, request_refs=[evidence],
                     reservation_id=None, actual_delta_usd="0", reservation_delta_usd="0",
                     uncertainty_usd="0", rate_usage_evidence=[evidence], reason=reason)
        data["events"].append(event)
        totals(data)
        save(path, data)
        return event


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, nargs="?")
    parser.add_argument("operation", choices=("reserve", "settle", "cap-freeze", "stop"), nargs="?")
    parser.add_argument("--id")
    parser.add_argument("--amount")
    parser.add_argument("--phase", default="review")
    parser.add_argument("--attempt")
    parser.add_argument("--attempt-cap")
    parser.add_argument("--uncertainty", default="0")
    parser.add_argument("--reserve", help="protected grading/closeout reserve, with cap-freeze")
    parser.add_argument("--evidence")
    parser.add_argument("--reason", help="terminal reason, required with stop")
    parser.add_argument("--ticket", type=int, help="producing issue; required for stop, otherwise defaults to 147")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return subprocess.run([sys.executable, str(Path(__file__).with_name("test_budget.py"))]).returncode
    if args.operation == "stop":
        if not all((args.ledger, args.reason, args.evidence, args.ticket)):
            parser.error("ledger, --reason, --evidence and --ticket are required for stop")
    elif args.operation == "cap-freeze":
        if not all((args.ledger, args.amount, args.reserve, args.evidence)):
            parser.error("ledger, --amount, --reserve and --evidence are required for cap-freeze")
    elif not all((args.ledger, args.operation, args.id, args.amount, args.evidence)):
        parser.error("ledger, operation, --id, --amount and --evidence are required")
    try:
        if args.operation == "stop":
            print(json.dumps(stop(args.ledger, args.reason, args.evidence, args.ticket)))
            return 0
        if args.operation == "cap-freeze":
            print(json.dumps(freeze_cap(args.ledger, args.amount, args.reserve,
                                        args.evidence, args.ticket or 147)))
            return 0
        print(json.dumps(transact(args.ledger, args.operation, args.id, args.amount,
                                  args.phase, args.attempt, args.attempt_cap,
                                  args.uncertainty, args.evidence, args.ticket or 147)))
        return 0
    except (ValueError, KeyError, TypeError) as exc:
        print(str(exc))
        return 1
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
