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
| 5. Completed stop probes | Create the unsealed root record before dispatch, bind it to the config, and pin its digest outside the evidence seal. At shutdown require a completed roots check **and** completed process/container/ledger checks. Permission denial, timeout, missing executable, inaccessible daemon or wrong/unrecorded roots establish nothing. The historical closeout gate's corroborating-workspace and daemon-down exceptions are not a future clearance. |
| 6. Uniform payloads | Freeze one output schema and one pinned validator for A/B/C before rendering or masking. Each arm must emit structured items as well as the body under the same contract; use the same valid empty-items representation for clean outcomes. Probe finding, clean and stopped outcomes in each arm. Reject mixed Markdown/JSON forms and arm-specific optional structures; never invent items for a stopped or unavailable payload. The historical packet builder remains unchanged and is not a future uniformity check. |
| 7. Network judgments | Freeze the coordinator's per-command network audit as a requirement. Retain each shell command's evidence judgment against the proxy log (or affirmative evidence of no traffic), including commands that look local and indirect interpreter traffic. An unreviewed command or unresolved proxy bypass invalidates fidelity. |
| 8. Fresh targets | Apply #148's selection criteria to newly selected candidates with new leak sets and registers. Exclude all four revealed #138 targets and any candidate whose truth the future reviewers already saw; issue closure or a renamed slot cannot restore blindness. No selection occurs in this PR. |
| 9. Runtime re-probe | Inventory version/help/image/config, then re-establish **every** control in the old preregistration section 4 on the actual future runtime before freezing. Include Bash availability under `--restricted`, actual model/effort, allowances, cancellation, storage and egress isolation. The #153 observation about Claude Code 2.1.268 is historical evidence to re-probe, not a current capability claim. Unsupported controls stop the study. |
| 10. Ledger stop | Pin the prospective budget implementation. Exercise stop with outstanding reservations and uncertainty, subsequent settlement/attempt closure and refused new review dispatch. Retain the producing ticket, reason and handoff evidence; separately cancel workers and pass shutdown probes. A stop event must not release unknown costs or rewrite the handoff. |

This checklist is input to a future freeze, not its completed evidence index. Uniform output
production, an all-required shutdown gate, fresh targets and real-runtime validation remain
that ticket's work. Neither the closed #138 handoff nor these toy tests authorize dispatch.

## Invocation and verification

All scripts use standard-library Python 3.9+ on macOS/Linux. Commands below are relative to
this bundle. Any nonzero exit blocks its step: retain the output, fix the cause and re-probe;
never turn an incomplete probe into passing evidence.

For a separately authorized future study, create the roots record while the real roots exist,
at an unsealed path outside every cell root. Pin this record and these scripts in the new
freeze. Set `roots_record` and `budget_script` in the coordinator config to their exact paths.

```sh
python3 scripts/roots.py record --out <unsealed-roots.json> --root <actual-cells-root>
# At the terminal decision:
python3 scripts/budget.py <future-ledger.json> stop --ticket <producing-ticket> \
  --reason '<terminal reason>' --evidence <retained-handoff-reference>
# After workers are stopped, accounted for and their workspaces archived/removed:
python3 scripts/roots.py check --record <unsealed-roots.json>
```

Verify the pinned root-record digest before shutdown probing. After recording stop, cancel
workers, settle outstanding bounds and check shutdown.
The stop's evidence reference names a handoff retaining available claims and unattempted work.
It never mutates the closed pilot's ledger.

Unpaid local checks:

```sh
python3 scripts/budget.py --self-test
python3 scripts/roots.py --self-test
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
