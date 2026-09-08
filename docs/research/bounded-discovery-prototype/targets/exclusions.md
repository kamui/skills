# Reservation and exclusion log for issue #148 (public)

Every candidate the curator examined and did not select, with the objective criterion it failed
(`targets/criteria.md` §3). Category labels, hypotheses and confirmations are in the sealed
inventory (`sealed/inventory.md.enc`, SHA-256 in `sealed/SHA256SUMS`) and are withheld here so this
file reveals nothing about which selected target is buggy or clean, or of which shape. The four
selected targets are named in `README.md` and are reserved for every later grid.

| Candidate | Failed criterion | Evidence |
| --- | --- | --- |
| `scrapy/scrapy#6993` | E4 packet provenance | a bot conversation comment created 2025-08-07T10:04:38Z was edited 2026-02-06T20:18:53Z, 57 s after the merge; all three review submissions postdate that comment, so no earlier cutoff can drop it without dropping a review |
| `grpc/grpc-go#8519` | E11 adjudication | the independent adjudicator's ruling did not match the shape its slot required (sealed register `sealed/excluded-grpc-go-8519-register.md.enc`); reserved rather than reused |
| `golang-jwt/jwt#456` | E11 adjudication | the independent adjudicator's ruling did not match the shape its slot required (sealed register `sealed/excluded-jwt-456-register.md.enc`); reserved rather than reused |
| `grpc/grpc-go#8369` | E3 size | 6 files, +268/−21 |
| `grpc/grpc-go#8342` | E3 size | 4 files, +335/−278 |
| `nats-io/nats-server#7387` | E3 size | 3 files, +336/−17 |
| `nats-io/nats-server#4045` | E3 size | 5 files, +344/−14 |
| `nats-io/nats-server#4861` | E9 confirmation | no upstream confirmation of a defect in this change; it was examined because of a misattributed test name |
| `nats-io/nats.go#1949` | E3 size | 6 files, +284/−7 |
| `psf/black#3931` | E3 size | 132 files |
| `tokio-rs/tokio#964` | E3 size | 7 files, +256/−3 |
| `tokio-rs/tokio` timer-sharding series | E9 confirmation | `#7226` reverts a multi-PR series; no single introducing pull request is named |
| `python/cpython#30637` | E3 size | 14 files, +2104/−2038 |
| `python-attrs/attrs` commit `b337f5b` (2016) | E3 size | 7 files, +137/−128 |
| `pytest-dev/pytest` commit `118cb3d3b` (2020) | E9 confirmation | cleanup commit; no confirmed defect |
| `graphql/graphql-js#3760` | E9 confirmation | the later change (`#3816`) states the test behaves as desired |
| `traefik/traefik` (via `#10244`) | E9 confirmation | the fix changes build configuration; no introducing change identified |
| `vercel/next.js` (via `#96725`) | not examined further | introducing change not identified |
| `aio-libs/aiohttp#12119` | E9 confirmation | a fix of a pre-existing behaviour, not an introducing change |
| `redis/redis-py#3654` | E9 confirmation | no introducing change identified |
| `libuv/libuv#4400` | E9 confirmation | #124 hunt: no confirmed defect of its own |
| `cockroachdb/pebble#5743` | E5 review trail | Reviewable.io |
| `quic-go/quic-go#5220` | E4 packet provenance | #137 record: bot comment edited 44 s after merge |
| `etcd-io/etcd#17563` | E8 static visibility | found by production profiling |
| `etcd-io/bbolt#1179` | E2 freshness | merged 2026-04-07 |
| `boutproject/BOUT-dev` (2019) | E3 size | #137 hunt: 7 files, 300 lines |
| `kubernetes/kubernetes` (via `#137119`) | not examined further | #137 hunt disqualified it |

Candidates that passed E1–E10 but sit below the first eligible candidate of their category were not
adjudicated; they are named in the sealed inventory and stay available to a later grid unless they are
promoted here by a replacement. Replacements, if any, are appended below with the criterion that
triggered them.

## Replacements

Two E11 exclusions above triggered replacements inside one slot; each time the next candidate in the
sealed inventory order for that slot was taken, after its packet passed E4. The slot is not named here,
because the trail of which candidates were rejected would otherwise hint at that slot's shape; the
sealed inventory records the full sequence with timestamps.

| When (UTC) | Replaced candidate | Criterion | Disposition of the replacement |
| --- | --- | --- | --- |
| 2026-09-08T06:28Z | `grpc/grpc-go#8519` | E11 | next candidate in order taken; its adjudication concluded 06:41Z |
| 2026-09-08T06:41Z | `golang-jwt/jwt#456` | E11 | next candidate in order taken; its packet passed E4 at the merge cutoff and its adjudication concluded 06:52Z |
