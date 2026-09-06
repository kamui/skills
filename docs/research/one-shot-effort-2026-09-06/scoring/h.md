# Scoring — target (h) `etcd-io/etcd#18749`

Register: [`../h-etcd-18749/register.md`](../h-etcd-18749/register.md), adjudicated clean;
`D_h = 0`, recall N/A. Scored blind from redacted copies, mapping revealed afterwards. On this
target the screen counts false findings (any item asserting a ground-truth-surface objection as a
defect) and action errors; there is no false-clean outcome.

## Replicate 1

| Attempt | Cell | Complete | Status | Finding items | False items | Ground-truth surface handled | Other items |
| --- | --- | --- | --- | --- | --- | --- | --- |
| att-11 | `high` r1 | yes (zero survivors on a data-integrity surface; clean-verdict batch: `clean verdict stands`) | **Approved (advisory)** | none | 0 | the lock-leak objection was raised as candidate `txn/lock-not-released-on-panic-if-recovered` (kind `concurrency`) and falsified on the absence of any `recover()` on the apply path — the register's reasoning exactly; the test's abandoned-lock/`s.Close()` concern raised and dropped | focused tests run once (package and `-run TestWriteTxnPanicWithoutApply`), pass |
| att-12 | `medium` r1 | yes (zero survivors; clean-verdict batch: `clean verdict stands`) | **Approved (advisory)** | none | 0 | same objection considered and falsified by a `recover()` search over `server/etcdserver`; the test's un-closed backend raised and dropped as "the unavoidable consequence of testing an invariant whose purpose is that the lock is never released before crash" | 1 observation (`computeFileHash` returns the raw digest bytes as a string: **accurate** at `txn_test.go:593`, but the cited evidence range `390-399` points at `TestCheckTxnAuth` — an evidence-location error, recorded separately). Focused tests run once (package and two `-run` filters), pass |

No false findings, no action errors, no questions. Both attempts ran the pinned skill's
clean-verdict batch and both verifiers upheld the acquittals.
