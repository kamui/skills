# Sealed candidate inventory for issue #148 (evaluator-only; frozen before adjudication and selection)

Frozen 2026-09-08 (UTC) by the curator under `targets/criteria.md` (commit `285e4cf26bc093cb861e57e6d31988a1f30373de`).
This file names categories and hypotheses, so it is hidden truth until every reviewer run has stopped.
Order within a category is the order in which the candidate's pull request was first looked up by the
curator (git clone log grep, then `gh api`), not a ranking. "First eligible" is the first row passing
E1–E10 mechanically; E11 is the adjudicator's independent ruling, which may exclude it and advance the order.

Reservation and freshness: today 2026-09-08; E2 threshold 2026-03-08T00:00:00Z. Sizes are
`git diff --numstat <merge-base> <head>` from full staging clones.

## C1 concurrency/progress defect

| # | Candidate | mergedAt | size | E1–E10 | Hypothesis (curator) | Confirmation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `nats-io/nats-server#7395` "[FIXED] Mirror consumer data race" head `b81b039c38afe724534ef6a1b9df490c5cdfaca4`, base = merge-base `78e2dacea262180ba6e39974aedca59529c9d17b`, base ref `main` | 2025-10-06T11:29:49Z | 1 file, +2/−1 (3) | **pass** (E4 built at merge cutoff, nothing omitted, nothing edited after merge; E7 S1) | The fix captures `mirrorWg := &mirror.wg` at the top of `setupMirrorConsumer` and waits on it inside the retry goroutine; the mirror config can be removed (e.g. leader change) between capture and `Wait`, so the data race it claims to fix persists and the goroutine waits on a stale mirror's WaitGroup. | `#7716` (2026-01-12) "Follow-up to #7395, since Antithesis still manages to reproduce the data race … capture it in the goroutine itself which allows to check the mirror config hasn't been removed" |
| 2 | `hyperium/h2#661` "Avoid spurious wakeups when stream capacity is not available" head `1f6464eea574bf956e606581e70b8e46223b0389`, merge-base = base `73bea23e9b6967cc9699918b8965e0fd87e8ae53` | 2023-02-20T22:55:05Z | 4 files, +111/−33 (144) | pass (E4 built; E7 S1) | Claims to fix #628 (`poll_capacity` returning `Ready(Some(0))`) by only setting `send_capacity_inc` when effective capacity increases; a WINDOW_UPDATE followed by a SETTINGS decrease in the same poll still yields `Ready(Ok(0))`, so the progress bug it promises to remove survives. | `#898` (2026-05-12) "poll_capacity must not return Ready(Some(Ok(0))) … WINDOW_UPDATE and SETTINGS decrease in the same poll can cancel each other out"; `#897` (2026-05-01) missed wakeup on `set_reset` |
| 3 | `hyperium/h2#596` "Make SendStream::poll_capacity never return Ok(Some(0))" head `b0470fd839b7251f25f5603142742b506fad6c67`, merge-base = base `b949d6ef998ce3a8bd805a03352b55985cf2fb0b` | 2022-01-19T18:49:54Z | 5 files, +85/−19 (104) | pass (E4 built; E7 S1) | Promises `poll_capacity` never returns `Ok(Some(0))`; issue #628 (2022-07-28) reproduces exactly that after this change; #661 says "the previous attempt on the fix has addressed only a part of the problem". | `#628`, `#661` |
| 4 | `prometheus/prometheus#15141` "Fix MemPostings.Add and MemPostings.Get data race" | 2024-10-11 | 3 files, +78/−12 (90) | E1–E3 pass; E4 not built; category fit doubtful (the confirmed defect is a memory-allocation blow-up, not a concurrency/progress failure) | Reverted by `#15316` (2024-11-03): "Memory allocation goes so high in Prombench that the system is unusable". | not examined further (below the first eligible) |
| 5 | `grpc/grpc-go#8369` xdsclient delay resource cache deletion | 2025-07-24 | 6 files, +268/−21 | **E3 fail** | reverted by #8527 for a race | — |
| 6 | `grpc/grpc-go#8342` otel retry attempts | 2025-09-10 | 4 files, +335/−278 | **E3 fail** | reverted by #8571 (flaky test) | — |
| 7 | `nats-io/nats-server#7387` filestore lost tombstones | 2025-11-13 | 3 files, +336/−17 | **E3 fail** | #7560 "data race introduced in #7387" | — |
| 8 | `tokio-rs/tokio` timer-sharding series | — | series | **E9 fail** | #7226 reverts a multi-PR series for a performance regression; no single introducing PR is named | — |
| 9 | `aio-libs/aiohttp#12119` server hang on chunk mismatch | 2026-02-22 | 3 files, +40/−0 | **E9 fail** | it is the fix of a pre-existing parser hang, not an introducing change | — |
| 10 | `nats-io/nats.go#1949` | 2025-10-10 | 6 files, +284/−7 | **E3 fail**; no introducing PR named | — | — |
| 11 | `redis/redis-py#3654` | 2025-05-26 | 3 files, +19/−6 | **E9 fail** (no introducing PR identified) | — | — |
| 12 | `libuv/libuv#4400` | 2024-07-29 | — | **E9 fail** (#124 hunt: no confirmed defect of its own) | — | — |
| 13 | `cockroachdb/pebble#5743` | — | — | **E5 fail** (Reviewable) | — | — |
| 14 | `quic-go/quic-go#5220` | — | — | **E4 fail** (codecov comment edited 44 s after merge; #137 record) | — | — |
| 15 | `etcd-io/etcd#17563` | — | — | **E8 fail** (found by production profiling) | — | — |

First eligible: **row 1, `nats-io/nats-server#7395`**. Next in order if E11 fails: row 2, then row 3.

## C2 conformance omission

| # | Candidate | mergedAt | size | E1–E10 | Hypothesis (curator) | Confirmation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `scrapy/scrapy#6993` "Fix override behavior in getwithbase()" | 2026-02-06T20:17:56Z | 2 files, +139/−5 | **E4 fail**: the codecov conversation comment created 2025-08-07T10:04:38Z was edited 2026-02-06T20:18:53Z, 57 s after the merge; the three review submissions (2026-02-04T18:47:46Z, 2026-02-04T19:59:32Z, 2026-02-06T20:17:30Z) all postdate the comment, so no earlier cutoff can drop the comment without dropping a review submission | `getwithbase()` normalizes every `_BASE` key with `load_object`, breaking format-keyed settings such as `FEED_EXPORTERS_BASE` (`csv.gz` → NameError) defined in the untouched `default_settings.py` | `#7426`, `#7449` (2026-04-22) |
| 2 | `clap-rs/clap#6212` "Fix value_terminator has no effect when it is the first argument" head `3604b13117cbb652c10bb44b228b300d543dcc80`, merge-base `4ecbf54ac314b6cd9a84d7e48350b71f6bd4c7ac` (PR-recorded base `b9009a76d1f2d62ba6af168bcef12ad7272626ca` is not an ancestor of the head), base ref `master` | 2026-01-27T20:18:05Z | 2 files, +46/−0 (46) | **pass** (E4 built at merge cutoff, nothing omitted; E7 S2 (`value_terminator`/`last` documented contract in untouched builder/arg docs) and S3 (test file changed)) | The new parser branch that lets a leading `value_terminator` fall through to positional handling breaks the documented interaction of `value_terminator` with `last(true)` / trailing positionals defined outside the diff; the change satisfies its own new test but not the existing contract. | `#6243` "fix(parser): Resolve regression with value_terminator/last" (merged 2026-02-03, commit `af904ae2` on master 2026-02-02 plus test commits `36eb896e`, `24cbf689`, `9d17332f`, `c98855a6`, `ccba5f5a`) |
| 3 | `grpc/grpc-go#8278` "grpc: Fix cardinality violations in non-server streaming RPCs" | 2025-06-11 | 2 files, +116/−6 (122) | E1–E3 pass; E4 not built; category fit plausible (documented `RecvMsg` contract of returning `io.EOF` on repeated calls) | reverted (commit `20bd1e7d`), rolled forward with changes by `#8523` (2025-08-26) "Restore the existing behavior to return io.EOF on repeated RecvMsg() calls" | not examined further |

First eligible: **row 2, `clap-rs/clap#6212`**. Next in order if E11 fails: row 3 (after building its packet).

## C3 changed-test behavioral defect

| # | Candidate | mergedAt | size | E1–E10 | Hypothesis (curator) | Confirmation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `psf/black#3931` "Use inline flags for test cases" (via #3939 "Fix test that was not being run") | 2023-10-09 | 132 files | **E3 fail** | — | — |
| 2 | `pytest-dev/pytest` commit `118cb3d3b` (2020) "Fix test_config: wrong assertions" | 2020-01-16 | — | **E9 fail** (a lint/cleanup commit; no confirmed defect and no introducing PR) | — | — |
| 3 | `graphql/graphql-js#3760` (via #3816) | 2023-01 | — | **E9 fail** (#3816 states the test behaves as desired; no defect) | — | — |
| 4 | `tokio-rs/tokio#964` (via #1197 "Fix lock test to actually test the inner lock value") | 2019-04-18 | 7 files, +256/−3 | **E3 fail** | — | — |
| 5 | `python-attrs/attrs` commit `b337f5b` (2016, via `649b273` "Make tests for simple-class actually run") | 2016-08-15 | 7 files, +137/−128 | **E3 fail** | — | — |
| 6 | `vercel/next.js` css-chunking test (via #96725 "fix missing await") | — | — | culprit not identified; not examined further | — | — |
| 7 | `python/cpython#30637` (via #96475 "_FlagTests were never run") | 2022-01-17 | 14 files, +2104/−2038 | **E3 fail** | — | — |
| 8 | `traefik/traefik` (via #10244 "unit tests were never run on cmd package") | — | — | **E9 fail** (the fix changes build configuration; no introducing test change identified) | — | — |
| 9 | `nats-io/nats-server#4045` (via #6266 "De-flake TestNRGSimple … was not actually testing anything") | 2023-04-13 | 5 files, +344/−14 | **E3 fail** (`TestNRGSimple` and `proposeDelta` originate here) | — | — |
| 10 | `nats-io/nats-server#4861` "Add low-level unit test for simple Raft election" | 2023-12-07 | 3 files, +94/−4 | **E9 fail**: examined as the `TestNRGSimple` origin by mistake; it adds `TestNRGSimpleElection`, for which no upstream defect confirmation exists | — | — |
| 11 | `nats-io/nats-server#6593` "De-flake TestNRGTermDoesntRollBackToPtermOnCatchup" head `282d01c5466d7694a098112a012097aa3a5dfaf1`, base = merge-base `4791216cdc896f127a9a2420edd42dcaf7e3b428`, base ref `main` | 2025-02-27T17:07:22Z | 3 test files, +34/−13 (47) | **pass** (E4 built at merge cutoff, nothing omitted; E7 S3 (test files changed) and S1 (test-side locking)) | The change to the Raft test helpers' locking (`lockAll`/`unlockAll` and the chain-of-blocks helpers) makes the chain-of-blocks tests race: a snapshot can contain new data with an old applied index, so the tests fail intermittently by construction; `leaderChange` is also called without the lock. | `#6623` (2025-03-10) "Partially reverts #6593 … the test became flaky due to the locking changes, since it introduced a race condition where snapshots could contain new data but with an old applied index … Also the lock was not held in `leaderChange`. (This was purely a test issue)" |
| 12 | `boutproject/BOUT-dev` (#137 hunt) | 2019 | 7 files, 300 lines | **E3 fail** (inherited) | — | — |
| 13 | `kubernetes/kubernetes` dual-stack test (#137 hunt, fixed by #137119) | — | — | not examined further (repository size; #137 hunt disqualified it) | — | — |

First eligible: **row 11, `nats-io/nats-server#6593`**. No further eligible candidate is recorded; if E11 fails, this category is delivered as an unavailable-target manifest unless a new hunt is run inside the budget.

## C4 clean control on a supported surface

| # | Candidate | mergedAt | size | E1–E10 | Hypothesis (curator) | Cleanliness evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `grpc/grpc-go#8519` "transport: ensure header mutex is held while copying trailers in handler_server" head `31a6f265a0` (full OID in the manifest), merge-base `0ebea3ebca8720be615d2c2e270a2c55ebd0b818` (PR-recorded base `fa0d658320…` is a later master pointer), base ref `master`, closing issue #8514 | 2025-08-21T06:50:13Z | 2 files, +99/−7 (106) | **pass** (E4 built at merge cutoff, nothing omitted; E7 S1 (header mutex around trailer copy) and S3 (test added)) | Clean: the added `hdrMu` hold around the trailer copy is correct; tempting objections (lock ordering, holding the mutex across `WriteStatus`, test determinism) are false. | #137 hunt (2026-09-07) found no fix/revert; curator re-check 2026-09-08: later commits on the two files (#8624, #8630, #8639, #9136, #9331) are refactors/unrelated; no commit or PR mentions #8519/#8514 as a defect |
| 2 | `golang-jwt/jwt#456` "Add WithNotBeforeRequired parser option" head `734a9292dbc587d5f0e7086af8e622d3541af21c`, merge-base = base `ce52acb322f4166c6f50543398a4b85993dd02fc` | 2025-08-07T06:01:43Z | 3 files, +81/−2 (83) | pass (E4 built; E7 S3 and S2 (RFC 7519 `nbf` optional contract)) | Clean per #124 hunt; surface is claim validation, not concurrency | #124 hunt: no later fix; not re-checked |
| 3 | `grpc/grpc-go#7417` "xds/balancer/priority: Unlock mutex before returning" | 2024-07-15 | 1 file, +1/−0 | E4 not built; one-line diff | clean per #137 hunt (medium confidence) | not examined further |
| 4 | `mvdan/sh#934` "expand: avoid panics on division by zero" | 2022-10-21 | 6 files, +94/−50 | E4 not built; ordinary surface with changed tests (S3) | clean per #137 hunt | not examined further |

First eligible: **row 1, `grpc/grpc-go#8519`**. Next in order if E11 fails: row 2.

## Cross-target hazard recorded at freeze

Two first-eligible candidates live in `nats-io/nats-server`. The C1 target's head (2025-10-06) is reachable
from a history that contains `#6623` (2025-03-10), the confirming fix for the C3 target. Each target gets
its own truncated mirror, so neither mirror contains the other's answer, but a reviewer of the C3 target
that could read the C1 target's clone would see the fix. #149's isolation controls must keep the two
targets' mirrors and clones mutually unreadable, or run their cells at different times with the other
mirror unmounted. This is a target characteristic, recorded here, not a change to the selection rule.
