# Bounded discovery — prospective prerequisites

This is the reusable tooling portion of [#199](https://github.com/kamui/skills/issues/199).
**Study-specific validation remains open.** The [#153 decision](../bounded-discovery-decision-2026-09-11/README.md)
closed #138 as inconclusive and recommended no confirmation study. This bundle runs no
study, selects no targets and changes no historical result, ledger or freeze.

A future study's freeze ticket must establish every row below on its actual runtime and
new targets before dispatch. A passing synthetic test proves the mechanical behavior it
exercises; it cannot establish runtime controls or blind-study readiness. Issue #199 closes
only when that future ticket supplies the evidence its probes require.

## Tooling delivered

- The [coordinator](../bounded-discovery-pilot-2026-09-09/scripts/run_cell.py) writes an
  exclusive, flushed `*-launch.json` before each primary phase and finder launch. It retains
  the exact container argv, including requested model, effort, tools, allow list, restriction
  flag, dollar allowance, prompt and worker definitions. These records belong in the private
  evidence seal. They record a requested launch even if process creation fails; transcripts
  and result records establish what actually ran. Retention failure prevents that launch.
- Settlement supplies a role for every transcript to the pinned `meter_split.py`, records
  `usage_per_role`, and refuses an unknown session identity. Filtered copies carry explicit
  labels from their original inputs plus a `sources.json` mapping with source/copy digests.
  Copy directories prevent equal basenames overwriting each other. The current coordinator
  groups verifier sessions as `worker`; a future study must retain any finer batch/helper
  attribution its design requires. Missing usage retains the existing conservative bounds.
- Detected sandbox violations fail settlement even when an acceptance calls them tidiness.
  Directory boundaries and lexical `..` traversal are checked. The audit remains a transcript
  path detector, not an interpreter or a proof against symlinks and arbitrary shell programs;
  actual isolation and the per-command network judgments still require runtime evidence.
- New dispatches require an external `roots_record` naming their actual `cells_root`.
  The dispatch record retains its digest. [roots.py](scripts/roots.py) creates that exclusive
  record and checks shutdown against precisely those roots, without filename-pattern or depth
  assumptions. A surviving root, including a dangling symlink, fails. A missing or unreadable
  parent is an incomplete probe and exits 2. Retain each parent until this check completes.
- [payload.py](scripts/payload.py) is the one payload contract for arms A, B and C.
  Every payload is a single JSON file, `work/review-payload.json`, with the same key set
  in every arm and every outcome: a `summary.body`, an `items` array that always exists,
  and a `stop` member that is null or names why the attempt ended. A findings payload has
  items and a body; a clean payload has the empty array and a body; a stopped or
  unavailable payload has the empty array and an empty body, and an item may never be
  invented for it. Unknown keys are refused at every level, so no arm can carry a
  structure the others do not — which is the pilot's structural tell, removed at its
  source. `accept` is the production gate for one attempt: it refuses a second payload
  form rather than converting or discarding it, validates what the arm wrote, writes the
  stopped payload itself when the arm produced none, refuses to invent one for a complete
  attempt, and refuses a payload that changed after acceptance. A payload it had to write
  gets an origin record named after the receipt and kept beside it, so a re-run — settlement
  is re-runnable — still records who produced it instead of inferring it from the file
  already being there. That record lives in the cell's artifacts directory, which no cell
  container mounts: a provenance record the arm could write establishes nothing about the arm.
  `uniformity` runs before masking over the acceptance receipts and checks one schema, one
  validator, one file form and the outcome coverage a freeze probes. A field only one arm
  carries blocks masking until a freeze rules on that field by name with
  `--allow-shape-correlation`; the ruling is recorded in the report.
  `--contract-validator` runs the study's own pinned output-contract program over the same
  review in every arm; it is not run against a stopped payload, which holds no review.
- The coordinator binds that contract at dispatch. A new dispatch requires `payload_contract`
  in its config, retains the path and digest in the dispatch record, and ships the same
  program into the cell at `runner/payload.py`. Preparation and dispatch are separate
  invocations, so dispatch checks that prepared copy against the digest it is about to pin
  and refuses to launch a worker against a missing or drifted validator — the cell runs the
  copy, not the configured file. Settlement accepts the attempt under exactly the pinned
  program: a missing or changed contract, a refused payload and a second payload form all
  become settlement problems, which make the attempt operationally invalid. A dispatch record
  that bound no contract — every historical one — settles exactly as before.
- [shutdown.py](scripts/shutdown.py) is the complete stop gate. Eleven checks, all required,
  none corroborating: the root record is the digest pinned before dispatch, it lies outside
  the seal it would release, every recorded root is absent, no process names a recorded root
  or a cell container or the coordinator, no cell container is present, every attempt is
  closed, no reservation is outstanding, the chain is unbroken, the ledger carries its
  terminal stop, no ledger event followed the probe, and the capture the gate scored is
  itself recent. A check clears only when its probe completed *and* its condition held, so a
  missing executable, a permission error, a timeout, an unreachable container runtime, an
  unreadable root parent, an unreadable ledger and a record that is not the pinned one all
  block clearance. The historical gate's daemon-down and corroborating-workspace exceptions
  are gone.
- The gate reads the ledger **after** the host probes and under the same writer lock
  `budget.py` appends with, so a reservation taken while the host was being probed is in the
  snapshot the decision rests on rather than behind it; a lock still held at the timeout is a
  failed read, not a quiet ledger. The gate retains the ledger's digest. `--probes-from`
  re-scores a retained capture, and the capture keeps its own age: an unusable timestamp, one
  stamped after the gate ran, and one older than `--max-probe-age-seconds` all block, so an
  old process table cannot be replayed into a present-day clearance. `authorize` is what the
  unsealing step calls. It re-reads the gate *and* the ledger, and exits 0 only when every
  required check is present and established, the ledger still digests to what the gate
  cleared, and — with `--max-age-seconds` — the older of the gate and its capture is still
  within the bound.
- [budget.py](scripts/budget.py) adds an atomic, immutable `stop`. It preserves the prior
  event chain, actual cost, reservations and uncertainty. It refuses new attempts,
  pre-freeze/review reservations, cap freezing and a second stop. Existing work can settle
  and attempts can close; protected grading/closeout reservations remain possible under the
  existing budget gates. It does not terminate workers or establish that they stopped.

The prospective budget script starts from the #149-pinned implementation at
`a34bc3e7dfe22efadca176a95664899782c792ae`; the original stays byte-identical so the historical
freeze still verifies. This is an intentional frozen/prospective fork, not two implementations
to synchronize. Set the coordinator config's `budget_script` to this prospective file for
future use. Every reservation, settlement and attempt claim then uses that implementation.
Historical settlement continues to default to the original pinned script.

## Evidence a future freeze must retain

| #199 gap | Required evidence and refusal case |
| --- | --- |
| 1. Launch argv | Before every phase and attempt, retain exact argv plus runtime/image identity and frozen worker definitions. Compare all arms against the prospective allowances. Probe a failed launch and confirm its request remains; block dispatch if retention fails. The recorded argv proves requested settings, not observed settings. |
| 2. Role metering | At settlement, retain per-role totals reconciling to the total, original session IDs, rates and transcript digests. Exercise primary, finder and verifier costs, including a provider error requiring filtered copies. Resolve every copy to its source before pricing; unknown role or missing usage is unresolved, never all-primary or zero. |
| 3. Lifecycle enforcement | Use the coordinator's existing claim-before-reservation path. Probe duplicate IDs, concurrency, attempt/replacement caps and an ineligible replacement; assert no worker starts after refusal. Check open precedes launch and close follows actual terminal accounting. Historical `claim-history` is reconstruction only and supplies no evidence of prospective enforcement. |
| 4. Sandbox rule | Freeze every permitted root, including any scratch and image allowance, identically across arms before probing. Try an actual outside read and a tidiness acceptance: both must fail under the frozen rule. A detector false positive requires correcting the detector and re-probing before freeze, not a settlement exception. |
| 5. Completed stop probes | Create the unsealed root record before dispatch, bind it to the config, and pin its digest outside the evidence seal. At shutdown run `shutdown.py check` and require every check to be established. Permission denial, timeout, missing executable, inaccessible daemon, wrong/unrecorded roots and a stale replayed capture establish nothing and block clearance. Call `shutdown.py authorize --ledger` immediately before opening the seal, and probe the host again rather than re-scoring an old capture or an older gate. The historical closeout gate's corroborating-workspace and daemon-down exceptions are not a future clearance. |
| 6. Uniform payloads | Freeze `payload.py` and the study's own output-contract validator for A/B/C, and render a dispatch template that writes `{PAYLOAD_CONTRACT}` — the #149 template writes the Markdown form only, and settlement refuses to mask it rather than converting it. Probe finding, clean and stopped outcomes in each arm and run `payload.py uniformity --require-arm ... --require-outcome ...` before masking. The historical packet builder remains unchanged and is not a future uniformity check. |
| 7. Network judgments | Freeze the coordinator's per-command network audit as a requirement. Retain each shell command's evidence judgment against the proxy log (or affirmative evidence of no traffic), including commands that look local and indirect interpreter traffic. An unreviewed command or unresolved proxy bypass invalidates fidelity. |
| 8. Fresh targets | Apply #148's selection criteria to newly selected candidates with new leak sets and registers. Exclude all four revealed #138 targets and any candidate whose truth the future reviewers already saw; issue closure or a renamed slot cannot restore blindness. No selection occurs in this PR. |
| 9. Runtime re-probe | Inventory version/help/image/config, then re-establish **every** control in the old preregistration section 4 on the actual future runtime before freezing. Include Bash availability under `--restricted`, actual model/effort, allowances, cancellation, storage and egress isolation. The #153 observation about Claude Code 2.1.268 is historical evidence to re-probe, not a current capability claim. Unsupported controls stop the study. |
| 10. Ledger stop | Pin the prospective budget implementation. Exercise stop with outstanding reservations and uncertainty, subsequent settlement/attempt closure and refused new review dispatch. Retain the producing ticket, reason and handoff evidence; separately cancel workers and pass shutdown probes. A stop event must not release unknown costs or rewrite the handoff. |

This checklist is input to a future freeze, not its completed evidence index. The mechanical
parts of rows 5 and 6 are now tooling; what stays open is study-specific and cannot be done
here. A future freeze must render a dispatch template that writes the contract payload, pin
its own output-contract validator, select fresh targets under row 8, re-probe every control
of old preregistration section 4 on the runtime it will actually dispatch with, and run every
probe in this table on that runtime and those targets. Neither the closed #138 handoff nor
these synthetic tests authorize dispatch, and a passing test here establishes only the
mechanical behavior it exercises.

## Invocation and verification

All scripts use standard-library Python 3.9+ on macOS/Linux. Commands below are relative to
this bundle. Any nonzero exit blocks its step: retain the output, fix the cause and re-probe;
never turn an incomplete probe into passing evidence.

For a separately authorized future study, create the roots record while the real roots exist,
at an unsealed path outside every cell root. Pin this record and these scripts in the new
freeze. Set `roots_record` and `budget_script` in the coordinator config to their exact paths.

```sh
python3 scripts/roots.py record --out <unsealed-roots.json> --root <actual-cells-root>
# Per attempt, at settlement; the coordinator runs this from its pinned copy:
python3 scripts/payload.py accept --work <cell>/work --receipt <cell>/artifacts/payload-receipt.json \
  --arm <A|B|C> --attempt <attempt-id> --completion <complete|stopped-...> \
  --contract-validator <the study's pinned output-contract validator>
# Before anything is masked, over every attempt's receipt:
python3 scripts/payload.py uniformity --receipt <...> --require-arm A --require-arm B \
  --require-arm C --require-outcome findings --require-outcome clean --require-outcome stopped \
  --out <uniformity.json>
# At the terminal decision:
python3 scripts/budget.py <future-ledger.json> stop --ticket <producing-ticket> \
  --reason '<terminal reason>' --evidence <retained-handoff-reference>
# After workers are stopped, accounted for and their workspaces archived/removed:
python3 scripts/shutdown.py check --ledger <future-ledger.json> \
  --roots-record <unsealed-roots.json> --roots-sha256 <the digest pinned at dispatch> \
  --seal <sealed-evidence-path> --out <gate.json> --raw-out <retained-outside-the-repo.json>
# Immediately before the seal is opened:
python3 scripts/shutdown.py authorize --gate <gate.json> --ledger <future-ledger.json> \
  --max-age-seconds 3600
```

Verify the pinned root-record digest before shutdown probing. After recording stop, cancel
workers, settle outstanding bounds and check shutdown.
The stop's evidence reference names a handoff retaining available claims and unattempted work.
It never mutates the closed pilot's ledger.

Unpaid local checks:

```sh
python3 scripts/budget.py --self-test
python3 scripts/roots.py --self-test
python3 scripts/payload.py --self-test
python3 scripts/shutdown.py --self-test
python3 ../bounded-discovery-pilot-2026-09-09/scripts/mark_event.py --self-test
python3 ../bounded-discovery-pilot-2026-09-09/scripts/run_cell.py --self-test
python3 ../bounded-discovery-pilot-2026-09-09/scripts/test_review_fixes.py
```

The budget suite includes the original CLI tests for reservation concurrency, settlement,
phase/attempt limits, corruption, replacement and context identity, routed to the prospective
script. The coordinator suite exercises real metering on synthetic transcripts, filtered-copy
role attribution, retained failed launches, sandbox rejection and the dispatch/root binding.
Docker mount checks remain opt-in and require `--docker-image`; this PR's validation launches
no container or provider session. The historical `verify_freeze.py --json` also passes with all
its pinned files unchanged.
