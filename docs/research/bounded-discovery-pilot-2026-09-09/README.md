# Bounded discovery — the six-cell pilot

**In progress (2026-09-09, UTC).** This bundle is [#150](https://github.com/kamui/skills/issues/150),
the first dispatch stage of the [#138](https://github.com/kamui/skills/issues/138) epic. It runs the
six `pilot` cells of the grid [#149](https://github.com/kamui/skills/issues/149) froze, and records
their dispositions, their fidelity evidence and a reconciled ledger.

**No cell has been dispatched yet and no experiment spend has been charged.** The ledger stands where
#149 left it: `$10.9378407` actual, `$0.00` reserved, 0 attempts dispatched.

## The gate

#150 dispatches nothing if #149 delivered a terminal stop. It did not:
[`handoff.json`](../bounded-discovery-runs-2026-09-08/handoff.json) records disposition `ready` with
`dispatch_authorized: true`, so the pilot is authorized. `verify_freeze.py` exits 0 against the
frozen bundle at this commit — every pinned digest, git pin, scope-to-packet binding and ledger
invariant holds.

The six pilot cells are positions 1–6 of the sealed schedule. **Which slots they run on stays
sealed**, exactly as [`sealed/README.md`](../bounded-discovery-runs-2026-09-08/sealed/README.md)
requires: the selection rule is public ("the adjudicated clean slot and the lowest-numbered buggy
slot, clean first"), so naming the pilot pair would disclose which slots hold the clean target. Every
artifact here is therefore keyed by **position**, never by slot, and the outcome evidence is sealed
until every reviewer run has stopped.

## Isolation: why this bundle carries a deviation

The preregistration's frozen isolation control is **absence** — the evaluator key and plaintexts,
the other slots' mirrors and clones, the other attempts' stores and *every checkout of this
repository* are off the machine while a cell runs, because probe 7 established that an allow-listed
interpreter reads any path that exists. That state is unreachable on the machine preparing this run:

| Precondition | Why it could not be met |
| --- | --- |
| every checkout of this repository absent | 188 linked worktrees plus the primary checkout, sharing one object store that reaches `targets/README.md` and the whole sealed bundle at any commit; the operations that would remove them are not available to the runner |
| `~/.config/bounded-discovery/` absent | it holds the only plaintext registers and leak sets plus `vault.tar.enc`, which is encrypted under the key in that same directory, and no off-machine storage was available to move it to |

So each cell runs in a **container that mounts only its permitted roots**, and the absence check runs
inside that container against the host paths. This is recorded as a dated deviation in
[`deviations.md`](deviations.md), with what it does and does not establish, because under it the
asserted mount set — not unconditional absence — is the evidence.

## Scripts

Standard-library Python 3.9+, macOS and Linux, each with `--self-test`:

| Script | What it does |
| --- | --- |
| [mark_event.py](scripts/mark_event.py) | records one #130 timing event in a cell's completion sidecar; the frozen dispatch prompt calls it by path and the repository did not yet carry it |
| [run_cell.py](scripts/run_cell.py) | the per-cell coordinator: `prepare`, `dispatch`, `settle`, following preregistration section 12 step for step |

`run_cell.py` extracts every prompt **verbatim from the frozen
[`dispatch-template.md`](../bounded-discovery-runs-2026-09-08/dispatch-template.md)** rather than
carrying its own copy, so a rendered prompt cannot drift from the byte the freeze pinned, and it
asserts that no `{PLACEHOLDER}` survives rendering before any dispatch.

#147's adapter is not in the dispatch path: its Claude entry point is an immutable no-cell
`stopped-runtime` by design, so the coordinator executes the frozen template directly, which is what
preregistration section 12 lists.

## Status

| Stage | State |
| --- | --- |
| freeze verified, gate evaluated | done |
| `mark_event.py` | done, 9 self-test checks pass |
| `run_cell.py prepare` | done, 7 self-test checks pass; position 1 prepared and verified |
| `run_cell.py dispatch` / `settle` | not yet implemented |
| six cells dispatched | none |
| handoff, dispositions, reconciled ledger | not yet written |

`prepare` builds a cell from the pinned inputs only: a private mirror copy, a clone made by the
frozen recipe and checked against the pinned head and merge-base, the policy snapshot extracted by
`git archive` from tree `bea6be14…` (the skill alone — cells never read a checkout), the packet and
scope verified against the digests #148 froze and #149 bound, and a private copy of the target's
toolchain caches mounted at the paths the packet hardcodes.
