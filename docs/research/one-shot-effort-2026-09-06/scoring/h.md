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

## Replicate 2

| Attempt | Cell | Complete | Status | Finding items | False items | Ground-truth surface handled | Other items |
| --- | --- | --- | --- | --- | --- | --- | --- |
| att-13 | `medium` r2 | yes (one `consider` survivor, no mandatory trigger, so under the pinned skill no verifier batch was required) | **Approved (advisory)** | P3/consider/maintainability: close the leaked test backend (accurate; the register lists it as legitimate test hygiene at most `consider`) | 0 | lock objection considered and dropped on the same no-`recover()` reasoning | none |
| att-14 | `high` r2 | yes (same shape: one `consider` survivor, no verifier required) | **Approved (advisory)** | P3/consider/maintainability: close the backend explicitly in the test (accurate) | 0 | lock objection: risk-led check "for a panic-recovery wrapper (none found)"; every other `.Panic(` site checked for the end-before-panic pattern | 2 observations: a typo in the new test comment ("aply", verified at `txn_test.go:377`) and the raw-digest `computeFileHash` return (verified, correct pointer `:592`) |

## Etcd summary (four valid completed attempts, `D_h = 0`)

| Arm | Attempts | Status | False findings (raw) | Action errors | Verifier batches |
| --- | --- | --- | --- | --- | --- |
| `high` (control) | att-11, att-14 | Approved ×2 | 0 | 0 | 1 (att-11, clean-verdict) |
| `medium` (candidate) | att-12, att-13 | Approved ×2 | 0 | 0 | 1 (att-12, clean-verdict) |

Every attempt considered the register's tempting objection (the lock leak on a recovered panic)
and falsified it the way the register does. The only published finding in either arm is the
test's un-closed backend at `consider`, inside the register's allowance. In replicate 2 both arms
kept that `consider` survivor, which under the pinned skill removes the zero-survivor
clean-verdict batch on a data-integrity surface; replicate 1's attempts had zero survivors and
ran it. Same skill behavior in both arms.
