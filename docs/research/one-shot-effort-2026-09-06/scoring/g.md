# Scoring — target (g) `tokio-rs/bytes#698`

Register: [`../g-bytes-698/register.md`](../g-bytes-698/register.md), one material defect GT-g1;
`D_g = 1`. Scored blind from redacted copies, mapping revealed afterwards.

## Replicate 1

| Attempt | Cell | Complete | Status | GT-g1 | Finding items | False items | False clean | Band | Fix | Other items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| att-07 | `high` r1 | yes (zero survivors; clean-verdict batch ran over the full ledger and returned `clean verdict stands`) | **Approved (advisory)** | **missed** — ledger row `bytes_mut/advance-capacity-compat` states GT-g1 exactly ("`capacity()` reporting a larger value after `advance(len())` … is an observable, possibly-breaking behavior change") and drops it as `intentional` because the PR body wants the outcome and both maintainers approved; the verifier's clean-verdict batch did not re-open it | none | 0 | **yes** | **under** | none | summary asserts the `Buf` contract is satisfied (an unsupported acquittal in prose; not a finding). `context` digest `ea945261…` |
| att-08 | `medium` r1 | yes (candidate batch on an `invariant` candidate; refuted) | **Approved (advisory)** | **missed** — the ledger never raised the capacity/cursor change; its `invariant` candidate was split-aliasing, correctly refuted | none | 0 | **yes** | **under** | none | 1 observation (`set_len`'s bound is a `debug_assert!`; accurate, evidence cited). Ran the pre-existing `bytes_buf_mut_reuse_when_fully_consumed` test once (pass). `context` digest `b19e2ac8…` |

Replicate-1 notes. Neither arm recovered GT-g1; the control came closer (it named the defect and
acquitted it on intent), the candidate never framed the capacity change as a candidate. The two
`context` digests differ although the packet is byte-identical, so the two reviewers fed the
fingerprint script different inputs (hygiene; not a scoring item). No false findings; no
question items.

## Replicate 2

| Attempt | Cell | Complete | Status | GT-g1 | Finding items | False items | False clean | Band | Fix | Other items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| att-09 | `medium` r2 | yes (zero survivors; clean-verdict batch over the acquittals: `clean verdict stands`) | **Approved (advisory)** | **missed** — ran a scratch probe that measured the exact behavior change (capacity retained 64→64 at the head versus 64→53 at the merge-base for the same full-consume sequence) and reported it as "the described optimization"; no candidate framed it as an observable contract change | none | 0 | **yes** | **under** | none | focused execution: `cargo test --test test_bytes advance` (7 passed) and the scratch probe at both revisions. `context` digest `ea945261…` |
| att-10 | `high` r2 | yes (zero survivors; clean-verdict batch: `clean verdict stands`) | **Approved (advisory)** | **missed** — three candidates, all memory-safety/bookkeeping (`set_len` safety, `vec_pos`, `split_to` interaction), all correctly refuted; the capacity contract was never a candidate | none | 0 | **yes** | **under** | none | 1 observation (fast path duplicates `clear()`/`truncate(0)`; accurate). Scratch program over five scenarios at the head (pass). `context` digest `ea945261…` |

## Bytes summary (four valid completed attempts, `D_g = 1`)

| Arm | Attempts | GT-g1 recovered | Target recall | False findings (raw) | False clean (count / rate) | Verifier batches |
| --- | --- | --- | --- | --- | --- | --- |
| `high` (control) | att-07, att-10 | 0 of 2 | 0% | 0 | 2 / 100% | 2 (clean-verdict) |
| `medium` (candidate) | att-08, att-09 | 0 of 2 | 0% | 0 | 2 / 100% | 2 (one candidate batch, one clean-verdict) |

All four attempts ran the pinned skill to completion with a verifier batch and approved. The
miss is the same in every cell: the change's stated purpose ("reuse the full capacity") was
taken as the specification, so the capacity/cursor contract change was either never raised
(att-08, att-09, att-10) or raised and acquitted as intentional (att-07). Two attempts executed
code that demonstrates the change and still did not treat it as a candidate. No false findings;
the observations published are accurate. Union recall (diagnostic): 0/1 in both arms.
