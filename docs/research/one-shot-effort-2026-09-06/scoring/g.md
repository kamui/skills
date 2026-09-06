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
