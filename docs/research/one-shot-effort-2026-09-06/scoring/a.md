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
