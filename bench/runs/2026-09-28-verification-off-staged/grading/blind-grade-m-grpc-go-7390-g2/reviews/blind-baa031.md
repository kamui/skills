# Review blind-baa031

### Item 1
Location: (no file)
Claim: No new test was added or changed by this diff; the fix's correctness rests on the pre-existing (previously ~0.4% flaky) `Test/AuthorityRevive` integration test and the author's manual reruns, rather than a new deterministic unit test targeting the connect/updateAddrs race directly.
Consequence: The changed-file manifest shows only `clientconn.go` (+6/-7); `git log` for the range shows no test file touched. Reviewer independently reran `Test/AuthorityRevive` 20x under `-race` at the reviewed head with 0 failures.
Fix: —

### Item 2
Location: (no file)
Claim: Commit `6214c9dd1`'s message, "Make callers of resetBackoff() lock the mutex", does not describe its content: the commit changes the `connect()`/`updateAddrs()`/`resetTransport` locking handoff and does not touch the `resetBackoff` channel.
Consequence: `git log -p daab5634..76ef33f4 -- clientconn.go`, commit `6214c9dd1cd421727852b03cafceac7c9e9eb973`.
Fix: —
