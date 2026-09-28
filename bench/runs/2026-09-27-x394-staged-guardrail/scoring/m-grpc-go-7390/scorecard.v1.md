# Scorecard: m-grpc-go-7390, mapping v1

Register v1 (5a40b59e0c38), rubric v1, scored at 2026-09-28T02:28:24Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 c50024109624eae0c2f48a7625b5d7d38fbda4f8e9108ad5376877fb970a727b; session 0abe801a-4f0d-4e99-9878-4d2d7e87b1fd; read audit clean.

## att-001 (review-code-sonnet-high-enforced-x394-trimmed), blind-280b8f

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "updateAddrs() spawns `go ac.resetTransportAndUnlock()` while still holding ac.mu ... an unusual pattern reviewers ... explicitly discussed and accepted via the function's name and doc comment rather than a compile- or runtime-enforced check." Fix: "—". Accurate: clone/clientconn.go:996 is `go ac.resetTransportAndUnlock()` with ac.mu held, and the doc comment at :1231-1233 states the contract. The item asserts no defect or consequence; it describes the handoff and notes the trade-off was accepted. The register lists both the lock handoff (non_defects[0]: sync.Mutex has no goroutine affinity) and the lack of enforcement (non_defects[1]) as non-defects, and the review does not claim otherwise. An accurate observation below the finding threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "resetTransportAndUnlock's early `acCtx.Err() != nil` return skips the connectivity.Connecting transition entirely; this pre-existing behavior (unchanged by this diff beyond the lock removal) was raised and explicitly dismissed by reviewers as immaterial." Accurate: clone/clientconn.go:1235-1239 returns after Unlock before the Connecting update at :1259, and `git diff main...review-head` shows the early-return body was not changed; only the leading `ac.mu.Lock()` was removed. The item itself says the behavior is pre-existing and immaterial and proposes no fix. A true, inconsequential remark, so it is non-material.

## New candidates

None.
