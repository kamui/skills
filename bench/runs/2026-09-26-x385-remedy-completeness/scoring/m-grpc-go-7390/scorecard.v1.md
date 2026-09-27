# Scorecard: m-grpc-go-7390, mapping v1

Register v1 (5a40b59e0c38), rubric v1, scored at 2026-09-27T07:11:42Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 cd780daecfe66f9b61e20f60bf0053a6163e1eb15bacb577d61526844ba8dbf8; session 7f256aa0-9165-409c-8506-5e4ebe084b26; read audit clean.

## att-004 (review-code-sonnet-high), blind-03fd8e

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "now briefly blocks the `updateAddrs` goroutine on `ac.mu` until the spawned goroutine reaches `ac.mu.Unlock()`" ... "Verified deadlock-free ... and exercised by a passing `-race` test." Fix: "—". At head clientconn.go updateAddrs defers ac.transport.GracefulClose() (whose onClose locks ac.mu) and then runs `go ac.resetTransportAndUnlock()` still holding ac.mu, so the deferred close can wait until the spawned goroutine releases the lock after updateConnectivityState(Connecting) (clientconn.go ~1262). That is accurate. The item itself says it is deadlock-free and proposes no change. The register lists the lock handoff (non_defects[0]) and the longer critical section (non_defects[4]) as intended, not defects. An accurate observation with no material consequence.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The second commit's message, 'Make callers of resetBackoff() lock the mutex,' does not describe its actual diff ... no functional effect on the merged diff." Confirmed: `git show 6214c9dd` renames resetTransport to resetTransportAndUnlock and moves the Lock/Unlock to the callers, but it never touches resetBackoff. This is commit-message hygiene on an intermediate commit and has no effect on the code, so it is below the finding threshold.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "Prior reviewer discussion about mechanically enforcing the new caller-holds-ac.mu contract ... was explicitly settled by the merging maintainer in favor of the function name plus doc comment". This restates the disclosed, accepted trade-off (register non_defects[1] and the preexisting_hints about purnesh42H and dfawley). The doc comment is present at head ('ac.mu must be held by the caller, and this function will guarantee it is released'). It is an observation that asserts no defect.

## New candidates

None.
