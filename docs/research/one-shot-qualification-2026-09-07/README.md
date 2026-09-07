# One-shot qualification grid — repaired policy against the historical baseline (issue #137)

**Bundle for [#137](https://github.com/kamui/skills/issues/137), started 2026-09-07 UTC.** This is
the matched experiment the ticket authorizes: the repaired `code-review-publish` snapshot pinned by
[#136](../code-review-one-shot-baseline.md) against the unchanged historical control
`3ff624a0a8b57e7096d8ad8263ac64a3fb3ccd83`, on fresh execution-enabled targets, under one model,
one effort and one verifier configuration. It follows the
[one-shot evaluation method](../code-review-one-shot-method.md). Results and the screening verdict
are in [`evaluation.md`](evaluation.md); every cell's rows are in
[`comparison-data.md`](comparison-data.md); every attempt and every dollar are in
[`ledger.md`](ledger.md).

The bundle is dated by UTC. Work began on the evening of 2026-09-06 Pacific, which is 2026-09-07
UTC; every timestamp in this bundle is UTC.

This README is the preregistration. It is committed in two stages, each before the dispatch it
governs, and both stage commits are named below. Anything changed after its stage commit is a
dated deviation with the original text retained.

## 1. Freeze

### 1.1 Stage 1 — design, arms, thresholds, caps, adapter, and target criteria

**Committed before the first reviewer dispatch** (commit recorded in the ledger's dispatch record
of attempt `att-01`). No reviewer had been dispatched and no candidate-arm review output existed
when this stage was written: the only chargeable work before it was the configuration probe and
the target vetting recorded in [`ledger.md`](ledger.md) §Setup, none of which ran a review.

**Question.** Does the repaired integrated reviewer recover more useful material defects per
completed review than the historical current-skill baseline, while preserving precision and
acceptable cost?

**Arms.** One model, one effort, one packet per target, one dispatch template. The arms differ in
exactly one thing: which pinned skill tree the reviewer reads.

| Arm | Skill snapshot | Workflow identifier | Row label |
| --- | --- | --- | --- |
| candidate | `skills/code-review-publish` at commit `83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6`, tree `bea6be143582e75bada966ee85964623ef31f167` (the #136 repaired baseline) | `v5b-10` | `repaired` |
| control | `skills/code-review-publish` at commit `3ff624a0a8b57e7096d8ad8263ac64a3fb3ccd83`, tree `867cf3ff0d9f097259699be4f55aa147c98a3a5d` (unchanged historical baseline) | `v5b-1`, pre-#70 | `historical` |

Runs identify their snapshot **by tree hash, never by the `workflow` trailer**: #136 §3 records
that `v5b-1` names two different verification behaviours across the #70 window, so the trailer
cannot separate them. Each snapshot was taken with `git archive <commit> skills/code-review-publish`
and the extracted tree re-hashed with `git write-tree`; both re-hashes matched the pins above
(ledger S2). The two snapshot directories are named `snapshots/bea6be14/` and `snapshots/867cf3ff/`
so that the path a reviewer reads carries the pin and not an arm label.

**Pins.**

| | Value |
| --- | --- |
| Model | `claude-sonnet-5`, passed as `--model sonnet` on the root and `model: "sonnet"` on every `Agent` call; verified from every assistant line of every transcript before scoring |
| Effort | `high` on the primary and on every sub-agent, in both arms — the runtime's observed default for `claude-sonnet-5`, requested explicitly as `--effort high` and inherited by children (ledger S1) |
| Runtime | Claude Code `2.1.263` (headless `claude -p`), Darwin 27.0.0, Python 3.14.7, git 2.55.0, gh 2.98.0, Go 1.27.0 |
| Prices | Sonnet 5 list `$2/$10` per M tokens; cache write ×1.25 (5-minute tier) and ×2.0 (1-hour tier) as the transcripts report them; cache read ×0.1. `transcript_usage.py` prices each tier from the usage fields (#97) |
| Method | [`code-review-one-shot-method.md`](../code-review-one-shot-method.md) at the stage-1 commit |
| Packets | built with the shipped [`build_packet.py`](../tools/build_packet.py) (#184) at its merged commit, with the merge-time cutoff and its provenance validation, one packet per target shared byte-identically by both arms |

**Adapter: what is normalised, and what is not.** Both arms are versions of the same skill, so the
dispatch shape is shared and nothing is backported. Three things are supplied identically to both
arms and are recorded here as the adapter:

1. **Phase 1 is supplied as a packet.** Neither arm resolves the target over the network; the same
   packet file is the pinned input for both. Both arms' `SKILL.md` step 1 has the orchestrator-
   supplied-packet route, so this is transport, not policy.
2. **`subagent_type: "general-purpose"`.** Both arms' `references/verifier.md` say only "start an
   equivalent clean worker" (the sentence is byte-identical in the two trees). This harness's
   clean worker is the `general-purpose` agent, and the dispatch template names it for both arms.
   Effort is inherited, so both arms' verifiers run at `high` with no agent definition.
3. **Render-only completion.** The targets are merged, publication is disabled, and both arms stop
   at the rendered would-be review. `SKILL.md` step 5 of both trees specifies exactly that for a
   retrospective run.

Nothing else is normalised. In particular the control keeps its own `review_context.py`, which has
no `--path`, `--store`, `--chunk-bytes`, `--from` or `--chunk` options; the candidate keeps the
bounded-recovery options #133 added. That difference is part of the repaired release, not an
adapter — see the size criterion in §1.2 for how the grid avoids letting it decide the result by
accident.

**Configuration probe (ledger S1).** Headless `claude -p --model sonnet --effort high` sessions
with sub-agents: [`agent_effort.py`](../tools/agent_effort.py) reports `claude-sonnet-5` and
`high` on 100% of assistant lines of the root and of every child, with no agent definition — a
child inherits its parent's effort, which is what makes a single `--effort high` flag sufficient
for both arms here. (This is the same inheritance #124 had to work around when its arms differed;
here they do not.)

**Cells.** Twenty-four planned cells: six targets × two arms × two replicates. A replicate is a
fresh headless session and a fresh clone; the harness exposes no API seed, so replicates are
labelled by ordinal. Attempt IDs are `att-NN`, never reused. At most two replacement attempts
(26 attempts total).

**Order and concurrency.** A two-target paired **pilot** runs first — one buggy target and one
clean target, eight cells — and its valid rows count inside the 24. Matched pairs dispatch
together, at most two cells in flight, with the arm order alternated by replicate: replicate 1
dispatches `repaired` then `historical`, replicate 2 `historical` then `repaired`. A session-limit
notice stops new dispatch until its reported reset.

**Replacement policy.** An attempt is discarded and replaced inside the two-replacement cap when it
is stopped by a session-limit notice or harness error, when any transcript line shows a model other
than `claude-sonnet-5` or an effort other than `high`, when the clone was mutated or a leak SHA was
reachable, or when the reviewer read another cell's files. A reviewer that finishes but violates its
own contract is a **skill failure** and stays a valid attempt (scored, and completion judged under
the method). No resumed continuation is allowed: a stopped attempt leaves evidence only. A
substantive miss, a false finding or a timeout under the frozen conditions is a measured outcome
and is never replaced.

**Target criteria (frozen here; the targets themselves are stage 2).** Six pull requests, four with
independently adjudicated material defects and two adjudicated clean, chosen to span **cross-file
conformance outside the diff**, **changed-test correctness**, **concurrency/progress**, and an
**ordinary behavioural change**, with at least one clean control on a high-risk surface. Every
target must satisfy all of:

1. **Unused.** Not `hyperium/hyper#3952`, `hashicorp/raft#581`, `python/typeshed#9458`,
   `astral-sh/uv#4424`, `pola-rs/polars#24771`, `spf13/cobra#1938`, `kamui/cobra-holdout#9`,
   `tokio-rs/bytes#698`, `etcd-io/etcd#18749`, or any target of prototype tests 1–4
   (`microsoft/playwright#29698`, `#29811`, `#30111`, `redis/redis#15530`, `#15680`,
   `tokio-rs/tokio#7757`, `kamui/shortlist#66`, `kamui/skills#17`, `#18`, `#19`). Both #124's
   reservations and every holdout and earlier test target are excluded.
2. **Merged at least six months before the grid**, with its confirming fix, revert or report
   already existing, so ground truth is settled by the upstream project rather than by us.
3. **Small: at most about 200 changed lines across at most six files.**
4. **Packet-buildable at the merge-time cutoff.** `build_packet.py` must exit 0 with the default
   cutoff. A target whose pull-request body, review, thread comment, conversation comment or
   closing-issue comment was edited after the merge instant fails #184's provenance check and is
   rejected, because its historical text cannot be established.
5. **Context build under 24,000 bytes.** The unbounded
   `review_context.py --merge-base <mb> --head <head>` output must be at most 24,000 bytes and must
   be **byte-identical between the two arms**, checked mechanically before the freeze. This keeps
   the grid off the one path where the arms' tooling genuinely differs: above the harness's Bash
   output limit the candidate can recover the diff from its private store (#133) and the control
   cannot. Measuring that difference is a legitimate question, but it is not the recall question
   this ticket asks, and one truncated target across four cells would dominate the macro. Rejected
   candidates and their byte counts are recorded in §1.2.
6. **Offline-runnable focused tests**, provisioned before dispatch, with the same allowance written
   into the packet for both arms; or, where no such path exists, the same static-only constraint for
   both arms, stated honestly.
7. **Review trail readable through `gh`.** A repository that reviews on an external tool (for
   example Reviewable.io) is rejected: its packet would silently omit the review record.
8. **The defect is not the promised change.** At most one of the four buggy targets may be of the
   class #124 identified — where the defect *is* the observable contract change the pull request
   asked for — and if one is used it is labelled as such in its register and reported separately.

**Ground truth.** Each target's register is written by an independent adjudicator that works from
primary sources and never sees any reviewer output, is checked against the orchestrator's own
reading of the code, and is committed in stage 2 **before that target's first dispatch**. Registers
carry stable defect IDs, expected behaviour, demonstrated consequence, evidence, the required
corrective outcome, and — for clean targets — the ground-truth surface a correct review must not
assert as a defect. Preexisting hints are disclosed: where a human reviewer on the pull request
already gestured at the defect, the register says so, because that comment is in both arms' packets.
Unexpected plausible true findings go to blinded independent adjudication (arm, replicate and cost
labels removed) before any register change, and every attempt is rescored against a versioned
register.

**Scoring.** Method §4. Payloads are scored blind: each attempt's payload is copied under a random
token with the mapping sealed in `scoring/`, cell and attempt identifiers redacted, scored, then
unblinded. The screening rule, applied to the candidate (`repaired`) arm against the control
(`historical`) arm:

1. zero raw false findings across all candidate attempts, harness-invalid ones included;
2. no additional false-clean outcomes (count and rate, on the same buggy targets);
3. completion rate not worse;
4. macro material recall at least **+10 percentage points**, in both the attempt-level and the
   completed-only view;
5. matched median billed cost ratio (candidate cell all-attempt cost / control cell all-attempt
   cost, matched by target and replicate, median over complete pairs) **`<= 1.25`**.

A full positive screen needs all twenty-four cells validly completed and the frozen four-buggy /
two-clean mix to survive adjudication. Otherwise the report names the failing gate and the measured
baseline is retained. A result with zero false findings but unchanged low recall is not success;
questions and hygiene suggestions cannot meet the recall criterion.

**Verifier-batch presence.** For every attempt the bundle records which verification mode ran
(`none`, `candidate`, `clean-verdict`, `follow-up`) and whether every acquitted `concurrency`,
`invariant`, `security` or `bug` row on a high-risk surface was ever ruled on by a verifier. For
each arm the record names the source rule that did or did not require the ruling and any
rule-permitted omission, so a faithful policy miss is distinguished from a dispatch failure. The
two arms' trigger semantics are read from their own trees; the repaired pin's semantics are not
assumed of the control.

**Budget gate.** Projection at Sonnet 5 list prices from #124's measured medians on the same
headless shape (candidate arm: #124's `high` all-attempt median $2.88; control arm: conservatively
$3.30, since the historical line's holdout median was $3.62 and no headless observation of it
exists): 12 × $2.88 + 12 × $3.30 = $74.16 of cells; pre-freeze setup, probes, vetting and
adjudication $15.00; grading/closeout reserve $5.00; two replacements ≈ $6.20. **Projected ticket
total ≈ $100.** Spend cap = `min(1.5 × $100, $150)` = **$150** — the #96 absolute ceiling binds
here, not the multiplier, which leaves less headroom than #124 had and is why the pre-freeze
allowance is held to $15. Per-attempt outlier: no cell is stopped for cost, but a single attempt
metering past $9 (about 3× the projected cell median) is reported as an outlier; the cap binds on
the ticket total. The 1-hour cache tier appears in headless sessions and is priced at ×2.0 where
the transcripts report it. Assumptions: targets meet criterion 3; no paid tool or repro charges.
If the grid tracks above projection, dispatch stops at the cap and the report is incomplete rather
than extended.

### 1.2 Stage 2 — fresh targets, registers, packets

**Committed before the first reviewer dispatch, together with stage 1** (the grid had not started;
see the ledger's dispatch record of `att-01`). No reviewer output of any kind existed. The targets
came from four vetting hunts (ledger S3–S6, reports in [`hunts/`](hunts/)) and each register was
written by an independent adjudicator (ledger S8) that never saw a reviewer's output and was told
to treat the hunt's proposal as an unproven hypothesis.

| Target | Slot and shape | Pull request | Head / merge-base | Diff | Language, execution |
| --- | --- | --- | --- | --- | --- |
| (i) | buggy — **concurrency / shared mutable state** | [`psf/requests#6667`](https://github.com/psf/requests/pull/6667) "Avoid reloading root certificates to improve concurrent performance", merged 2024-05-15 | `4089f3dc65f783beaa53cc032958ab625440d0ac` / `8dd3b26bf59808de24fd654699f592abf6de581e` (= base) | 1 file, +28/−18 | Python; offline pytest in a pre-provisioned virtualenv |
| (j) | buggy — **cross-file obligation outside the diff** | [`trpc/trpc#5017`](https://github.com/trpc/trpc/pull/5017) "fix(server): inference fix for inputs with middleware", merged 2023-11-10 | `7dc04a7e94654dfad6ef1289dfe01a0a206fff3b` / `2abb2d5cd19740be37272dac6ad7fdd36244ae54` (= base) | 2 files, +57/−3 | TypeScript; offline `tsc` with dependencies pre-installed in the clone |
| (k) | buggy — **changed-test correctness** | [`graphql/graphql-js#1582`](https://github.com/graphql/graphql-js/pull/1582) "Enable Flow typings on errors tests + Fix typing for Error constructor", merged 2018-11-21 | `7e39a122eea9292eeffa6905ffdf8a60c5161cfd` / `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11` (= base) | 5 files, +48/−47 | JavaScript; offline mocha with dependencies pre-installed in the clone |
| (l) | buggy — **ordinary behavioural change** | [`bokeh/bokeh#9232`](https://github.com/bokeh/bokeh/pull/9232) "Fixed issue of Datepicker displaying the wrong date for users in UTC+…", merged 2019-10-03 | `36549bca3a63d581f7b68d08054a7813c1e6a499` / `ccb4bcb4c2b841d89b0e88303a97bf4604a5795f` (= base) | 2 files, +104/−2 | TypeScript; offline scratch `node` under the work directory |
| (m) | clean — **high-risk (concurrency)** | [`grpc/grpc-go#7390`](https://github.com/grpc/grpc-go/pull/7390) "grpc: hold ac.mu while calling resetTransport to prevent concurrent connection attempts", merged 2024-07-09, originating issue #7365 | `76ef33f44a600c3ed1a385979fd1dfbcade3fbb6` / `daab56344e612097fd50c46c433de5d9b6013837` (= base) | 1 file, +6/−7 | Go; offline `go test`/`go vet` with pre-downloaded module and build caches |
| (n) | clean — **ordinary risk** | [`BurntSushi/ripgrep#2957`](https://github.com/BurntSushi/ripgrep/pull/2957) "feat(completion): support sourcing zsh completion dynamically", merged 2024-12-31, originating issue #2956 | `855bfa6cdae4f4fe8762f892fc4957635397083e` / `79cbe89deb1151e703f4d91b19af9cdcc128b765` (= base) | 2 files, +29/−4 | Rust project, shell surface; offline scratch `zsh` under the work directory |

Every merge-base was recomputed locally and every one equals the pull request's recorded base.
The four buggy targets cover the four shapes the method asks for, and the two controls cover a
high-risk and an ordinary surface.

**Ground truth.** Sealed registers, committed here before the first dispatch and versioned
thereafter. Every defect below was ruled an **unintended error**, not the behaviour change its
pull request promised, so criterion 8's allowance for one promised-change target is unused and no
target is reported in that class.

| Target | `D_t` | Defect IDs and one-line claims |
| --- | --- | --- |
| (i) | **2** | **GT-i1** the single shared process-wide `SSLContext` silently discards an adapter's own `ssl_context` and exposes shared mutable OpenSSL state to concurrent per-request client-cert loading; **GT-i2** CA-bundle loading moves from lazy per-request to eager unconditional import time |
| (j) | **1** | **GT-j1** `Overwrite`'s new `extends object` gate drops inferred context/input properties when a middleware's params derive from an unconstrained generic type parameter, at call sites in two untouched files |
| (k) | **1** | **GT-k1** the changed test "creates new stack if original error has no stack" no longer exercises the no-stack fallback branch and cannot fail for the reason it exists |
| (l) | **1** | **GT-l1** `_unlocal_date`'s timezone correction is valid only for local-midnight input and shifts UTC-midnight `value`/`min_date`/`max_date` back one day for every user west of UTC |
| (m) | **0** | adjudicated clean; the ground-truth surface a correct review must not assert as a defect is the lock handed across the `go ac.resetTransportAndUnlock()` boundary |
| (n) | **0** | adjudicated clean; the ground-truth surface is the replacement of the unconditional `_rg "$@"` by the `funcstack`/`compdef` guard |

Each register also carries its reproduction log, its "not ground truth" list of plausible
objections that are **not** defects, its preexisting-hints section, and its leakage set.

**Preexisting hints, disclosed.** Both arms' packets carry the pull request's review record through
the cutoff, and on (i) that record already gestures at part of GT-i1: `sigmavirus24` wrote "I'm
pretty sure SSLContext is not itself thread safe … loading it at the module will likely cause
issues", and `nateprewitt` asked whether the context should be per-adapter rather than global.
Neither blocked the merge. On (j), (k), (l), (m) and (n) no participant raised the adjudicated
defect or the ground-truth surface. This is disclosed rather than removed: the hint is identical
for both arms.

**Packets.** Built with the shipped [`build_packet.py`](../tools/build_packet.py) (#184), one per
target, byte-identical across arms and replicates. SHA-256:

| Target | Cutoff | Omitted after cutoff | Packet SHA-256 |
| --- | --- | --- | --- |
| (i) | `2024-05-15T20:07:26Z` (merge) | 1 review, 11 conversation comments | `f217cd71acce435aa1062c52ba3997aa4b0777293c824da131353028a4cb96b4` |
| (j) | `2023-11-10T10:08:08Z` (merge) | none | `e7734dc35aeea6588f58ac65a0f1d1bcfbd2b2aaac0f5806cc2618d6f0347382` |
| (k) | `2018-11-21T14:33:19Z` (merge) | none | `6b5e1d3797ed3af4b34d01aa440dcf7540ea94c13b26cd3dca2bd4f0dd4d731b` |
| (l) | `2019-10-03T15:51:00Z` (**62 s before the merge — see the deviation below**) | 4 conversation, 2 issue comments | `5964e4ba6fb323734e75c868d22b3e5bbd35cb202f413637e0673399ad09b46d` |
| (m) | `2024-07-09T20:27:27Z` (merge) | none | `a003ca717a66aea689fe350a479454b02c92f32e9edd268504ba8a1d2a46a2f6` |
| (n) | `2024-12-31T13:23:13Z` (merge) | 2 conversation comments | `ac4ad8bf3c68466a8aca4e4debe1d3fd25a5f5130c8d6f35ef1aee23f390022b` |

**Target (l)'s earlier cutoff, and why it is not a loosening.** At the merge instant `build_packet.py`
refuses (l): a maintainer's conversation comment created 25 s *before* the merge was edited 73 s
*after* it, so #184's provenance rule cannot establish its historical text. Moving the cutoff back
62 s, to `2019-10-03T15:51:00Z`, is strictly **more** conservative than the merge instant — an
earlier cutoff can only remove material, never admit post-merge knowledge — so the guarantee the
rule exists for is over-satisfied rather than weakened. It costs the packet that comment (a note
about flaky CI), the author's thanks, and the post-merge chatter. It is applied identically to both
arms and is recorded here as a per-target cutoff, not as an exception to the rule.

**Rejected candidates, with the criterion each failed.** Recorded so the selection is auditable:

| Candidate | Criterion | Evidence |
| --- | --- | --- |
| `cockroachdb/pebble#5743` | 5 (context size) and 7 (review trail) | unbounded `review_context.py` output **41,976 bytes**, over the harness's Bash output limit — the one path where the arms' tooling genuinely differs, since only the candidate has #133's chunked recovery; and cockroachdb reviews on Reviewable.io, which `gh` does not return |
| `quic-go/quic-go#5220` | 4 (packet provenance) | `build_packet.py` exits 1: `conversation #1: lastEditedAt is after the cutoff; historical text unavailable` — the codecov bot edited its comment 44 s after the merge |
| `libuv/libuv#4400` | ground truth | vetted in #124's hunt as having no confirmed defect of its own |
| `etcd-io/etcd#17563` | statically visible | the defect was found by production-scale profiling, not by reading |
| `etcd-io/bbolt#1179`, `golang-jwt/jwt#456` | 2 / difficulty | too recent; too mechanical |

**Context-build size and arm identity, measured.** Criterion 5, checked mechanically on a fresh
clone of each mirror with both arms' `review_context.py`:

| Target | (i) | (j) | (k) | (l) | (m) | (n) |
| --- | --- | --- | --- | --- | --- | --- |
| Bytes | 22,095 | 3,620 | 18,831 | 7,374 | 6,305 | 13,253 |
| Arms byte-identical | yes | yes | yes | yes | yes | yes |

All six are under the 24,000-byte bound, and no target puts the grid on the bounded-recovery path.

**Mirrors and leakage checks.** One bare mirror per target holding only the head (`review-head`) and
the merge-base (the base branch). Negative `git cat-file -e` checks run on the mirror at
provisioning and again on **every** clone inside the runner, which aborts before dispatch on a hit:
(i) `9a40d127…`, `145b5399…`, `90fee087…`, `11d68c17…`; (j) `f27d50c7…`, `a2a14f0f…`, `de858987…`,
`afa9ad92…`; (k) `f0ae3f4c…`, `8d621b00…`, `25680d28…`; (l) `ec1e525c…`, `ec557b68…`, `16d3d0ef…`;
(m) `45d44a73…`; (n) `94305125…`. In every mirror the newest reachable commit date equals the head's
own date. Dependency caches were populated from the pinned heads only.

**Execution allowances** are in each packet's section 8 and are identical for both arms. Targets (j)
and (k) have their dependencies installed by the runner **before** dispatch, from an offline store
or cache; the runner then aborts the cell if that provisioning left the tracked tree dirty, so the
reviewer receives a clean checkout it is told not to modify. Provisioning and a representative
focused command, timed on this machine: (i) venv 9 s, `pytest -k "ssl or verify"` 2.7 s — one
failure present **at the merge-base too**, an OpenSSL/fixture-certificate mismatch, not introduced by
the change; (j) `pnpm install --offline` 19 s, `tsc --noEmit` 5 s; (k) `npm install --offline` 4 s,
`mocha` 2 s; (l) none beyond `node`; (m) `go mod download` 2 s, focused `go test` 3 s, `go vet` 1 s;
(n) none beyond `zsh`.

**Budget refinement.** All six diffs are small and the stage-1 projection is unchanged; the cap
stays **$150**. Pre-freeze spend is $26.38 against the $15 allowance — see the deviation in §3.

## 2. Preparation

**Per-cell mechanics.** `run_cell.sh <target> <bea6be14|867cf3ff> <replicate> <attempt>`
(experiment tooling, quoted in [`tooling.md`](tooling.md)): a fresh clone from the target's mirror
with the base branch forced to the merge-base and `review-head` checked out at the head; the
negative leak checks re-run on that clone, aborting before dispatch on a hit; optional post-clone
dependency provisioning from an offline store, followed by a check that the tracked tree is still
clean; the dispatch prompt rendered from one template with the cell's paths; the timing sidecar
created with `root_dispatched_at` immediately before the `claude -p` call; `payload_validated_at`
written by the reviewer itself right after its final successful `validate_review.py` run via
`mark_event.py`; `completed_at` written by the runner when the session returns with both the report
and the payload present (completion mode `render-only`). A non-zero exit or a missing file writes a
stop record outside the sidecar. `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` is exported for the cell
session, and the dispatch template requires `run_in_background: false` on every sub-agent, after the
S3 helper was killed by the runtime's 600-second background-wait ceiling.

Close-out (`close_cell.py`) scans `message.model` and the top-level `effort` on every line of the
root and of every child transcript, and meters with
`transcript_usage.py --prices 2,10 --report <run.md> --timing <timing.json>`. It reported zero
problems on all 24 attempts.

**Blind scoring.** After each target's four cells closed, `blind.py seal` copied their payloads
under random tokens with the mapping sealed, redacting the cell id, the attempt id, the snapshot
hash and the `workflow` trailer. An independent scorer, told to score each review on its own merits
and not to compare or identify them, produced the target's scorecard against the sealed register;
the mapping was revealed only afterwards. Scorecards and mappings are in [`scoring/`](scoring/).

## 3. What ran, deviations, and the decision

**Ran (2026-09-07, 04:52–09:54Z):** all twenty-four planned cells, all valid completed, **zero
replacements** of the two available, no session-limit notice, no stopped or discarded attempt. The
stage-1 and stage-2 freeze commit `588edce` (04:52:01Z) preceded att-01 (04:52:17Z). Order: the
paired pilot on (i) and (m), replicate 1 `repaired` then `historical` and replicate 2 the other way,
then (j), (l), (k), (n) the same way, two cells in flight throughout.

**Deviations, dated:**

1. **04:53Z — dispatch records for `att-01` and `att-02` were written to the ledger about a minute
   after their dispatch, not before it**, contrary to method §3. The freeze commit itself preceded
   both dispatches, and every subsequent dispatch record (att-03 onward) was written before its
   dispatch by `dispatch_record.sh`. The two rows say so on their face.
2. **04:52Z — the pre-freeze allowance was overrun by $11.38** ($26.38 spent against $15.00). Causes,
   both in the ledger: the S3 vetting hunt fanned out to background sub-agents, hit GitHub's
   30-per-minute code-search limit, stalled, and was killed by the runtime's 600-second
   background-wait ceiling, costing $3.29 for no report; and the S5 cross-file hunt cost $8.82, 4.6×
   the median of the other three. The ticket's $150 cap was not moved and was not exceeded — the
   grid closed at $109.48. The overrun is recorded, not absorbed.
3. **10:03Z — the frozen target mix changed from four buggy / two clean to five buggy / one clean.**
   One cell published a finding on the clean control (n) that the sealed register had not
   considered. Under method §4 it went to an independent adjudicator with the arm, replicate and
   cost labels removed, which ruled it **material**; `D_n` moved 0 → 1 and the register was versioned
   ([`n-ripgrep-2957/register.md`](n-ripgrep-2957/register.md) §"Register version 2",
   [`adjudication/nc1-ruling.md`](adjudication/nc1-ruling.md)). Every arm and attempt was rescored
   against version 2, and both the version-1 and version-2 scores are reported. Method §4 makes a
   changed target mix incompatible with a full positive screen, so this qualification is
   **incomplete** regardless of the numbers. The screen fails on quality gates under both truth
   sets, so the revision changes the margin, not the verdict.
4. **10:03Z — GT-n1 is of the "promised behaviour change" class** #124 identified. Criterion 8
   capped that class at one of the four *buggy* targets and it arrived instead by revision on a
   target frozen as clean, which the preregistration did not contemplate. It is reported separately
   in `evaluation.md` §5, including the screen recomputed with (n) excluded entirely.
5. **06:40Z — the order of the four non-pilot targets was chosen after the pilot**, on projected
   cost and shape coverage only, and recorded in the ledger before any of them was dispatched. Stage
   1 froze the pilot and the pairing rule but left this order open. No output from (j), (k), (l) or
   (n) existed when it was chosen.
6. **The orchestrator inspected the structure of two payloads** (`att-01`, `att-02` headers and
   section headings) as a validity check before scoring began. Scoring was done throughout by
   independent blind scorers on redacted copies; the orchestrator scored nothing.
7. No deviation from the preregistered thresholds, arms, pins, cells, replacement policy, scoring
   rule or caps.

**Decision.** The screen **fails** at gate 2 (false cleans 4 against 3) and gate 4 (macro material
recall 55.0% against 70.0%, fifteen points the wrong way against a +10-point threshold), while
passing gate 1 (zero false findings), gate 3 (12/12 completion in both arms) and gate 5 (matched
median billed cost ratio 1.057 against ≤ 1.25). **The measured baseline is retained**; see
[`evaluation.md`](evaluation.md). Nothing here argues for reverting to `v5b-1`: the historical arm's
advantage is two cells wide, and the repaired release carries mechanical guarantees the control does
not. What the grid establishes is that the accumulated policy changes between `v5b-1` and `v5b-10`
did not move measured material recall on fresh targets, and that the ceiling is set by gaps both
versions share — most visibly the cross-file target (j), which all four cells of both arms missed
while faithfully following their own rules. This result changes no verification semantics, so the
workflow identifier stays `v5b-10`.

## 4. Files

- `README.md` — preregistration (stages 1 and 2), preparation, what ran, deviations, decision
- `ledger.md` — caps, setup and probe entries, the attempt ledger with dispatch records and meter
  rows, close-out totals
- `comparison-data.md` — per-attempt verification, outcomes, recall by target, false cleans, billed
  usage, timing, matched pairs, verifier-batch presence
- `evaluation.md` — the screening rule applied, where the difference comes from, what both arms
  miss, limitations, decision
- `i-requests-6667/`, `j-trpc-5017/`, `k-graphql-js-1582/`, `l-bokeh-9232/`, `m-grpc-go-7390/`,
  `n-ripgrep-2957/` — per target: the packet both arms received, the sealed register (version 2 for
  (n)), and every attempt's payload, run report and timing sidecar
- `scoring/` — the six blind scorecards and their sealed token→attempt mappings
- `adjudication/nc1-ruling.md` — the post-grid blinded ruling that versioned (n)'s register
- `hunts/` — the four target-vetting reports
- `prompts/` — the cell dispatch template, the blind-scoring template, the ground-truth
  adjudicator template, the GT-n1 adjudication brief, and the four vetting-hunt prompts
- `tooling.md` — every experiment script, the packet-build invocations, and the context-build
  size and arm-identity check, quoted

The per-attempt run reports are the reviewers' own raw output and are committed unedited. A few of
them link to their `/tmp` working paths, which do not exist in the repository; those links are left
as the reviewers wrote them rather than rewritten, since the reports are evidence.
