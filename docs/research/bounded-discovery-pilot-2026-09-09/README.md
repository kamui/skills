# Bounded discovery — the six-cell pilot

**Delivered 2026-09-09 (UTC).** This bundle is [#150](https://github.com/kamui/skills/issues/150),
the first dispatch stage of the [#138](https://github.com/kamui/skills/issues/138) epic. It runs the
six `pilot` cells of the grid [#149](https://github.com/kamui/skills/issues/149) froze, and records
their dispositions, their fidelity evidence and a reconciled ledger.

**Disposition: `stopped-incomplete`** ([handoff.json](handoff.json)). Historical pilot fidelity is
unverified following [PR #197's review](https://github.com/kamui/skills/pull/197#pullrequestreview-5156879681).
The recorded costs and per-cell summaries below are preserved historical reports, not a fresh
validation of the pilot. #151 must not dispatch from this handoff while that assessment is open.
See [deviation 11](deviations.md#11-coordinator-corrections-and-historical-fidelity-2026-09-09).

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

Keying by position is necessary but **not sufficient**, and review proved it. The pairing was also
recoverable two other ways, each from a value that looks inert: a published SHA-256 of a cell's rendered
dispatch prompt, and a derived session UUID printed in the fidelity report. Both are hashes over a
four-candidate secret — which slot filled the placeholders — so a preimage search inverts them, and four
of the six positions were matched that way against their own committed digests. The public prompt
commitments are now HMACs under a salt that lives inside the seal, which binds each rendering at
publication without being invertible, and the fidelity record publishes per-role verdicts and line counts
instead of file names. [`observations.md`](observations.md) section 5 states the general rule.

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
## What the pilot did

All six frozen pilot cells were dispatched in sealed schedule order, one at a time, each in its own
container. **Five completed; one stopped against the frozen dollar allowance.** Cells are identified by
schedule position only — naming their slots would disclose which slot holds the clean control.

| Position | Arm | Worker model | Completion | Settled (USD) | Isolation | Read audit |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | A | claude-sonnet-5 | complete | 3.8595330 | yes | yes |
| 2 | B | claude-opus-5 | complete | 3.8777270 | yes | yes |
| 3 | C | claude-opus-5 | complete | 7.0003047 | yes | yes |
| 4 | A | claude-sonnet-5 | complete | 4.5304828 | yes | yes |
| 5 | B | claude-opus-5 | complete | 6.3671277 | yes | yes |
| 6 | C | claude-opus-5 | stopped-budget | 9.0040632 | yes | yes |

Position 6 ended `error_max_budget_usd` at $9.0040632 — the $9.00 per-attempt ceiling plus
exactly the one-call overshoot probe 4 measured, absorbed by the $1.00 of reservation headroom the
freeze requires. That is a **measured incomplete result in every arm alike**, not an infrastructure
failure and not replacement-eligible. It counts as missing in #152's screen rather than as present.

### Two invalid attempts, both retained

| Position | Attempt | Cost | Why invalid | Replacement consumed |
| --- | --- | --- | --- | --- |
| 1 | 1 | $0.0000000 | coordinator defect: `--session-id` was the attempt ID, not a UUID, so the launch was refused before any model request | **yes** |
| 3 | 1 | $1.5838690 | documented infrastructure invalidity: provider 502 at turn 43, `terminal_reason: api_error`, before the arm C freeze artifact was written | **yes** |

**Two of three replacements are consumed**, and the ledger — not a narrative — is what says so. Every
attempt is claimed through `budget.py`'s `attempt_event`, which refuses a reused attempt ID or worker
context ID, enforces the 27-attempt and three-replacement caps, and refuses a replacement whose
predecessor was not closed as documented invalidity. Position 1's retry was initially recorded as *not*
consuming a replacement on the grounds that nothing had been measured; the ledger's rule is that any
second attempt at a cell is a replacement, and that rule governs. Eight attempt IDs of 27 are used,
none recycled, and all sixteen worker contexts are distinct — which is how "no finder context resumes
as verifier" is established rather than asserted.

Both invalid attempts' raw output and costs are retained inside the sealed archive, as the replacement
policy requires.

### Fidelity

Every arm's worker configuration is **verified from transcripts**, not assumed: `agent_effort.py` is run
per role with `--expect-model` and `--expect-effort` for that role, over every assistant line of every
transcript, and a mismatch is a fidelity failure that invalidates the attempt. All six cells pass:

- arm A: primary and verifier `claude-sonnet-5`, effort `high`
- arm B: primary `claude-sonnet-5`, verifier `claude-opus-5`, both effort `high`
- arm C: primary `claude-sonnet-5`, **finder and verifier** `claude-opus-5`, all effort `high`

Arm C's barrier held in both of its cells: the primary wrote its freeze artifact — its own complete
candidate ledger, hashed — and stopped, before the coordinator released any finder claim to it. The
finder returned a valid fenced block with all seven required keys in both cells, and it has no write
tool, so the coordinator persisted it.

One position dispatched **no verifier at all**, which §9 expressly permits for arms A and B under the
pinned rules and requires be counted rather than forced into a batch.

### Isolation

Every cell passed the absence gate before and after its dispatch, inside its own container, against
52–55 forbidden host paths. Every mount set was exactly four entries. The egress proxy allowed only
`api.anthropic.com` and refused everything else — Datadog telemetry in every cell, and `api.github.com`
only where the isolation checks probe it deliberately. **No cell attempted a forge fetch.** Every clone
was verified at its pinned head with a clean tracked tree afterwards, so the no-mutation rule held even
though every completed cell ran its focused tests.

One sandbox-audit hit survived review and is recorded as an acceptance with its reason rather than
pattern-matched away: a cell redirected `git show` of a base file **from its own clone** into a
container-local `/tmp` scratch path and read it back, instead of writing under its work directory.
#152 can overrule that judgment.

### Accounting

The total reconciles from its parts, which `handoff.json` now carries explicitly: pre-freeze
`$10.9378407` plus `$36.2231074` across all eight attempts plus `$0.1527100` of one-off shared setup
equals the ledger's `$47.3136581`, to the last digit. The setup charges — establishing that the cell
image authenticates, that the frozen flag set runs inside it, and that a session's transcript can be
metered and fidelity-checked — were charged before any attempt was reserved, so an infrastructure
failure could not burn an attempt ID, and are itemised rather than folded into a cell.


Pre-freeze spend was $47.3136581 at the close of #149 plus this ticket's cells. Actual now
**$47.3136581** of the $150.00 cap, with $0.164316 retained as
uncertainty and $92.5220259 remaining after the $10.00
protected grading reserve. Every cell's residual is decomposed into the part the result envelopes
attribute to an untranscripted model and the part left unexplained; settlement charges the larger of
the runtime self-report and the retained records in every case.

### The grid no longer fits

Measured means: **A $4.1950, B $5.1224,
C $8.0022** — a triple costs $17.3196 against the freeze's
$12.79 projection. The eighteen remaining cells therefore project to
**$103.9177 against $92.5220 available**: a shortfall.
The allowance covers 5 of the 6 remaining triples, leaving 3 cells unrun.

The preregistration accepted this risk prospectively and said the headroom was thin. What makes it
survivable is the frozen contiguous-triple order: #151 must stop on a triple boundary, which leaves an
interpretable partial grid rather than a ragged one.

### No result is reported here

`available_claims` is empty. No recall, cost ratio, quality comparison or statement that any arm is
better or worse appears in this bundle or in its handoff. The outcomes — payloads, research reports,
finder claims, transcripts and the reconciled ledger — are **sealed** under #148's key in
[`sealed/`](sealed/), with the plaintext digest in [`SHA256SUMS`](sealed/SHA256SUMS), and stay sealed
until every reviewer run has stopped. #152 scores; this ticket only ran the cells and proved they were
run faithfully.


### Regenerating the handoff and settling interrupted usage

[write_handoff.py](scripts/write_handoff.py) reads the recorded historical fidelity judgment from
[fidelity-review.json](fidelity-review.json), or the file named by `--fidelity-review`. The preserved
judgment is blocked. Missing or unresolved judgments produce `stopped-incomplete` and retain the
#151 dispatch hold. A researcher may record `status: cleared` only after reviewing permitted evidence,
with a nonempty `evidence` list and a `rationale`. The helper checks those fields and carries the
judgment into the handoff; it does not inspect seals or make the fidelity judgment.

[run_cell.py](scripts/run_cell.py) treats missing, malformed and nonfinite primary costs as unknown.
When a single primary phase or finder has no self-report, settlement charges each worker group's
larger observed subtotal and retains one extra request at each affected transcript's largest observed
request cost. Streamed records are grouped before the retained usage helper prices them. Missing
transcripts or prices keep the full reservation. A worker with no self-report that launched other
workers also keeps the reservation, since retained files cannot establish that every child survived
archival. A resumed primary with any missing phase report also
keeps the reservation because its shared transcript cannot separate the billed phases. Such records
report `settled_usd: null` until reconciliation establishes a bound. None of these coordinator changes
recomputes or clears the preserved pilot's historical accounting or fidelity.
