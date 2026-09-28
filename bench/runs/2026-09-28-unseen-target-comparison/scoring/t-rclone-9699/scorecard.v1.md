# Scorecard: t-rclone-9699, mapping v1

Register v1 (405740094c70), rubric v1, scored at 2026-09-28T21:14:43Z.

Adjudicator: headless Claude Code 2.1.284, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 efbea21238e560ef55bdb2622dab44f8f27c6f3a1d75494142155bf0f44ec7d0; session 97c93e69-cd9f-45b8-8c9a-810582c85bdf; read audit clean.

## att-001 (review-code-sonnet-high-enforced-x394-control), blind-62d112

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

(no items)

## att-002 (review-code-sonnet-high-enforced-verification-off), blind-91a3b1

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "the new admitMu also now covers the pre-existing `fs.Debugf(b.f, ...)` call, so a slow `Stringer.String()` ... would hold admission (and block Shutdown) longer ... no concrete instance is shown to matter." True (batcher.go:273 Debugf between Lock at 267 and Unlock at 281) but the item itself shows no concrete impact; register non_defect 'fs.Debugf runs while admitMu is held' is ruled true and inconsequential.

## att-003 (review-code-sonnet-high-enforced-verification-off), blind-695d14

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "select on `<-b.closed` with a 100ms timeout can never observe a closed channel, because Shutdown blocks on `admitMu` until the blocked `Commit` goroutine releases it ... a no-op wait that does not affect the test's correctness." Correct at head: the Commit goroutine holds admitMu (batcher.go:267) while blocked in blockingStringer.String() via fs.Debugf, and Shutdown takes admitMu (line 243) before close(b.closed), so the <-b.closed branch cannot fire before release; the 100ms timeout always elapses. The item itself says it does not affect correctness (and the branch is meaningful at base, where it lets the marker be queued). Test hygiene observation, below threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "Holding `admitMu` across each `Commit` call's send ... fully serializes concurrent admissions ... though `commitLoop` keeps draining independently of the mutex so no deadlock is introduced." Accurate observation with no material consequence claimed; register non_defects rule the lock-across-send deadlock and serialisation/throughput objections not defects (critical section is a non-blocking select, Debugf and one buffered send; sync wait is after Unlock).

## att-004 (review-code-sonnet-high-enforced-x394-control), blind-747de2

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "`Commit`'s admission critical section now spans its debug-log call and the send on `b.in`, so concurrent `Commit` calls (and `Shutdown`) fully serialize on `admitMu` ... unmeasured, and ... runs show no timeout regression." True fact (batcher.go:267-281) with no demonstrated consequence; the item concedes it is unmeasured. Register non_defects: serialisation does not defeat batching, and Debugf under the lock is inconsequential. Observation only.

## att-005 (review-code-sonnet-high-enforced-x394-control), blind-4f31f7

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "toggling the process-global `fs.Config.LogLevel` ... an effective, deterministic way to hit the race window, but coupled to `fs.Debugf`'s current global-config fallback". Accurate: the test mutates ci from fs.GetConfig(context.Background()), which returns globalConfig (fs/config.go:793-802). This is a test-design coupling remark, not a product defect; register non_defects rule that the global LogLevel mutation is not a defect (race -count=5 passes, test not parallel). Test hygiene, below threshold.

## att-006 (review-code-sonnet-high-enforced-verification-off), blind-120d0b

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "Commit admission is now fully serialized through `admitMu`, including while a send to the buffered `b.in` channel is blocked ... the commit loop ... keeps draining `b.in` independently, so this bounds latency without risking deadlock." Accurate description (batcher.go:267-281 holds admitMu across the send; commitLoop never takes admitMu). It asserts no material consequence and itself concludes no deadlock. Register non_defects rule both the deadlock and the serialisation/throughput objections not defects. Observation only.

## New candidates

None.
