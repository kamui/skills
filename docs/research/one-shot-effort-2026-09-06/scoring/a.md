# Scoring — target (a) `hyperium/hyper#3952`

Register: holdout README Target (a), one material defect GT-a1; `D_a = 1`. Scored by the
orchestrator from blind copies (`/tmp/effort124/scoring/blind/`), each payload read in full
before the mapping was revealed, except where noted.

**Blinding deviation (recorded 08:41Z).** The control attempt's payload (att-01) names its own
cell and attempt in a leading HTML comment, so its arm was visible while it was being read; the
candidate attempt's payload (att-02) carried no identifier and was read first, blind. From
replicate 2 onward the sealing step redacts cell and attempt identifiers from the blind copies.
Both payloads were scored on the same written criteria before unblinding; the deviation is
disclosed, not repaired.

| Attempt | Cell | Complete | Status | GT-a1 | Finding items (priority/action/kind) | False items | False clean | Band | Fix | Other items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| att-01 | `high` r1 | yes | Changes Requested (advisory) | **recovered** — steady-state trigger (body `poll_frame` pending, buffer empty so `poll_flush` trivially ready), `can_write_again` = `body_rx.is_some()`, 16-iteration spin re-woken by `yield_now` | P1/must-fix/concurrency (GT-a1); P2/consider/maintainability (new test never runs in CI, asserts nothing, no timeout — accurate, in band per register) | 0 | no | in band | **sufficient, invariant-level**: gate `wants_write_again` on real write progress this cycle | 1 observation (pre-existing `!can_write_body()` branch returns `Pending` without visible waker registration; verified accurate at `dispatch.rs:424`) |
| att-02 | `medium` r1 | yes | Changes Requested (advisory) | **recovered** — same steady-state mechanism ("any body that is not always instantly ready"), names `Buffered::poll_flush` trivially `Ready` and `yield_now` re-queue | P1/must-fix/**performance** (GT-a1; `kind` label nuance, register requires `concurrency` — recorded as a label error, not a band violation); P3/consider/maintainability (test asserts no byte count — accurate hygiene) | 0 | no | in band | **sufficient, invariant-level**: require a signal that `poll_write` made progress or the body became ready, not `body_rx` presence | 0 observations published |

Recall: att-01 1/1, att-02 1/1. Fix sufficiency 1/1 each. No question items. Neither payload
proposes a branch-level workaround (lower bound, backoff, type detection, `body_rx` emptiness),
so both are `invariant` under the register's dimension-4 rule. Neither asserts any "not ground
truth" item as a defect.

## Replicate 2 (scored blind from redacted copies, mapping revealed afterwards)

| Attempt | Cell | Complete | Status | GT-a1 | Finding items (priority/action/kind) | False items | False clean | Band | Fix | Other items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| att-03 | `medium` r2 | yes | Changes Requested (advisory) | **recovered** — steady-state (body `poll_frame` pending, write buffer empty so `Buffered::poll_flush` resolves `Ready`), `yield_now` self-wake, "busy-spinning at full CPU until the body next produces data" | P1/must-fix/concurrency (GT-a1); P2/consider/maintainability (CI never runs `ready_stream`; accurate) | 0 | no | in band | **sufficient, invariant-level**: edge-triggered progress bit like `notify_read`, not `body_rx` presence | 1 observation (test asserts no byte count; accurate, evidence cited) |
| att-04 | `high` r2 | yes (under the skill's own rules: no mandatory trigger fired, two `consider` survivors made zero-survivor mode inapplicable, so no verifier was required) | **Approved (advisory)** | **missed** — ledger row `dispatch/poll-loop-write-retry-gap` (kind `concurrency`) dropped as "consequence unproven"; the reviewer traced the test's mock alternation but never the always-ready `poll_flush` case | P2/consider/maintainability ×2 (CI never runs the test; test cannot fail — both accurate) | 0 | **yes** | **under** | none | no verifier batch; no observations |

Replicate-2 note: att-04 is the holdout's seed-3 pattern in a new form — a primary-only acquittal of
the concurrency candidate on the ground-truth surface, unchecked because two hygiene survivors
suppressed zero-survivor mode and none met a mandatory trigger. It is a skill outcome, not a
harness failure, so it stands as a valid completed attempt with a false clean.
