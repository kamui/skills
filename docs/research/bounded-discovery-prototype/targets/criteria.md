# Target preparation for issue #148: frozen criteria, roles and procedure

**Frozen 2026-09-08 (UTC) before any candidate was selected, adjudicated or scope-selected.**
This file is committed first; the candidate inventory is frozen (sealed) second; the selector
runs third. Anything changed after this commit is a dated deviation with the original text
retained. Authority: [#148](https://github.com/kamui/skills/issues/148), the
[design](../DESIGN.md) §2 (common preparation and the scope selector), the
[one-shot method](../../code-review-one-shot-method.md) §2 (identical inputs, isolated execution)
and the [#137 preregistration](../../one-shot-qualification-2026-09-07/README.md) §1.1 target
criteria, which these criteria extend. "Today" for every freshness computation is
**2026-09-08**; six months before it is **2026-03-08**.

## 1. Roles and what each may know

| Role | Context | Knows truth | Charged | Output |
| --- | --- | --- | --- | --- |
| Curator | this orchestrator session | yes: hunts candidates, reads later fixes, writes the hypothesis for each candidate | no: ordinary ticket work, outside measured experimental spend by the [design](../DESIGN.md) §6 convention (disclosed here, not asserted free) | sealed candidate inventory, exclusion log, mirrors, packets, manifests |
| Adjudicator | one fresh `claude-sonnet-5` helper per chosen candidate, in-session `Agent` with `model: "sonnet"` set explicitly, single-threaded, no sub-agents | receives the curator's hypothesis as an **unproven** claim plus full history; may run tests and read later fixes | yes: reserved and settled on the shared [ledger](../ledger.json) under `pre-freeze` | sealed defect register (or clean ruling), leak set, plausible non-defects, preexisting hints |
| Selector | one fresh **headless** `claude -p --model sonnet --effort high` session per chosen target, single-threaded, offline, read-only tools | **nothing** beyond the common packet, the offline clone and the diff: no truth, no category label, no later fixes, no curator narrative, no other target | yes: reserved and settled under `pre-freeze` | `scope.json` (SelectedScope) plus its report; kept even when it misses |
| Reviewer | none in this ticket | — | — | — |

One agent that has read the answer cannot become blind by omitting it from its next prompt, so
the selector is always a new root context with only its own prompt file, and the adjudicator
is a fresh sub-agent that has not seen the selector or any reviewer. The curator never writes
into a selector prompt anything but the prompt template and the target's public coordinates.

## 2. Sample

Four fresh merged pull requests, one per category, purposively sampled (a mechanism pilot, not
a prevalence estimate):

| Category | Required shape |
| --- | --- |
| C1 concurrency/progress defect | a material defect in a concurrency, cancellation, wake-up, ordering, timeout, retry or liveness mechanism the diff touches |
| C2 conformance omission | the change fails to discharge an obligation stated outside its own hunks: an issue/spec requirement, a documented contract, a caller's or sibling implementation's invariant, a schema/table/type that must stay in step |
| C3 changed-test behavioral defect | a test the diff adds or substantively changes is materially wrong: asserts the wrong thing, cannot fail for the reason it exists, exercises a different path than it names, or is flaky by construction |
| C4 clean control | no material defect, adjudicated with evidence, on at least one of the three surfaces above so that the selector has something to select |

At most one buggy target may be of the "promised contract change" shape #124 identified (the
defect is the observable behaviour the pull request itself asked for); if one is, its sealed
register labels it so and #153 reports it separately. It is a target characteristic, not a
failure-stage claim.

## 3. Objective eligibility criteria (predeclared)

Every candidate is checked against all of E1–E10 mechanically by the curator and E11 by the
adjudicator. A failure names the criterion in the exclusion log. Only these failures can exclude
or replace a candidate; **a selector miss never can** (design §2).

- **E1 Unused.** Not on the reservation list in §7.
- **E2 Settled.** `mergedAt` on or before `2026-03-08T00:00:00Z`. For a buggy candidate the
  upstream confirmation (fix, revert, regression test or issue naming the mechanism) must already
  exist and predate this freeze. For the clean control the six-month window is the cleanliness
  window.
- **E3 Small.** At most 200 changed lines (additions plus deletions from
  `git diff --numstat <merge-base> <head>`) across at most 6 files.
- **E4 Packet-buildable.** `docs/research/tools/build_packet.py` (#184) exits 0 with the default
  merge-instant cutoff. If it refuses only because a record was edited after the merge, one
  earlier cutoff may be used, at the latest instant that passes, provided it drops comments only
  and never a review submission; the per-target cutoff is recorded and applies identically to
  every arm (the #137 target (l) precedent). Any other refusal excludes the candidate.
- **E5 Trail readable through `gh`.** GitHub-native reviews, threads and comments; repositories
  reviewing on Reviewable, Gerrit or a mailing list are excluded.
- **E6 Safe reproducibility.** Focused offline commands of at most five minutes each after at most
  ten minutes of network provisioning per target, no credentials, services or destructive
  external effects; otherwise a static-only allowance stated identically for all arms. A
  provisioning failure excludes the candidate only when neither route is available.
- **E7 Supported surface.** The diff contains at least one surface the selector can select,
  checked from the file list and hunks: (S1) concurrency/progress: locks, atomics, channels,
  tasks/goroutines/threads, wake-ups, timeouts, retries, cancellation, state machines with a
  progress obligation; (S2) conformance: an obligation stated in the PR text, its issue, a doc,
  a type/interface contract, a sibling implementation or a table the change must keep in step;
  (S3) changed test: a test file added or modified. The surface found is recorded per candidate.
- **E8 Statically visible.** The defect (or, for the control, the tempting-but-false surface) is
  reachable by reading the diff plus at most two caller/callee/contract hops; telemetry-only or
  fuzzing-only defects are excluded.
- **E9 Independently confirmed.** Buggy: the upstream record identifies this defect and its
  mechanism, with SHAs. Clean: `git log` over every changed path from the merge to this freeze,
  plus issue and pull-request searches for the changed symbols, find no fix, revert or report.
- **E10 Public and permissive.** Public repository, OSI-approved license, real maintainers.
- **E11 Adjudicated.** The fresh adjudicator confirms at least one material defect in the stated
  category (buggy) or rules the change clean with evidence (control), with stable defect IDs,
  trigger, demonstrated consequence and required corrective outcome. An adjudicator that refutes
  the hypothesis excludes the candidate under this criterion.

## 4. Selection rule

1. The curator hunts candidates per category and records **every** candidate examined, in the
   order examined, with its E1–E10 results, into the inventory. The inventory is then sealed
   (§6) and its hash committed **before** any adjudicator or selector runs.
2. Within each category, the first candidate in inventory order that passes E1–E10 is sent to
   adjudication. If E11 fails, the next in order is sent. A candidate whose adjudication passes is
   the category's target.
3. A target is replaced before dispatch only for a predeclared objective failure discovered
   later (E1–E11), never because the selector selected another surface or missed the defect.
   Every replacement is logged with the criterion.
4. **Slot numbers hide category.** After the four targets are fixed they are ordered by
   case-sensitive lexical order of `owner/repo#number` and named `slot-1` … `slot-4`. The public
   manifests carry no category, clean/buggy status, defect, leak SHA or later-fix reference.

## 5. Scope selector protocol

- One run per target, after the packet and clone are frozen, from the committed prompt template
  in `prompts/selector-template.md` with only the target's public coordinates and paths filled.
- Model `claude-sonnet-5`, effort `high`, headless session (`claude -p --session-id <uuid>
  --model sonnet --effort high`) so the transcript proves the model and effort on every
  assistant line with `agent_effort.py`. Tools: read-only (`Read`, `Grep`, `Glob`, `Bash` limited
  by prompt to `git diff`/`git show`/`git log` on the offline clone and `ls`/`cat`). The clone
  is a disposable checkout from the truncated mirror with no network remote.
- Inputs: the packet (`packet.md`), the clone, and the diff. Nothing else exists under its working
  directory. Recorded before the run: SHA-256 of the prompt file, the packet, the diff bytes, and
  the clone's head tree OID; after the run: SHA-256 of the output, transcript path, metered cost.
- Output: a `SelectedScope` per design §3 with `selection_mode: model-assisted`, the supported
  alternatives it found, the selected surface under the fixed order **S1 concurrency/progress,
  then S2 conformance, then S3 changed test**, ties broken by normalized repository-relative
  path (case-sensitive lexical), then symbol, then line; roots as `{path, symbol, start, end}`;
  a frontier of at most two cited hops; exclusions.
- The output is frozen as delivered. If it is structurally unparseable (not the schema), one
  re-run with the identical prompt is permitted and both transcripts are kept; a parseable
  selection is never re-run, whatever it selects. A miss is part of the measured strategy.

## 6. Sealed truth and evaluator-only storage

Repository commit visibility is not assumed safe for reviewers with filesystem access, so hidden
truth is never committed in clear:

- Hidden artifacts: the candidate inventory (it names categories), each target's register, leak
  set (post-merge SHAs and issue/PR numbers), plausible non-defects, preexisting hints, curator
  hunt notes, the category-to-slot mapping.
- Each hidden file is encrypted with `openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt` under
  one random 256-bit key generated for this ticket; the ciphertext is committed under
  `sealed/`, and `sealed/SHA256SUMS` commits the SHA-256 of every plaintext so the freeze is
  provable at reveal time. The key and a plaintext copy live only in the evaluator-only
  directory `~/.config/bounded-discovery/issue-148/` (mode 0700), outside the repository and
  outside every reviewer clone, packet directory and `/tmp` working root.
- Reveal: after every reviewer run has stopped, #153 decrypts with the key, checks
  `SHA256SUMS`, and joins. The reveal procedure is in `sealed/README.md`.
- Residual read surface, disclosed: the key file is on the same machine. Before any reviewer
  dispatch #149 must either move the key off the reachable filesystem or demonstrate with its
  isolation probes that reviewer tools cannot read `~/.config`. A leak detected later
  invalidates the affected comparisons; this file does not claim enforcement.

## 7. Reservation list (E1)

Excluded as used or reserved by earlier grids: `kamui/shortlist#66`, `redis/redis#15530`,
`redis/redis#15680`, `tokio-rs/tokio#7757`, `microsoft/playwright#29698`, `#29811`, `#30111`,
`kamui/skills#17`, `#18`, `#19` (prototype tests 1–4); `hyperium/hyper#3952`,
`hashicorp/raft#581`, `python/typeshed#9458`, `astral-sh/uv#4424`, `pola-rs/polars#24771`,
`spf13/cobra#1938`, `kamui/cobra-holdout#9` (holdout); `tokio-rs/bytes#698`,
`etcd-io/etcd#18749` (#124); `psf/requests#6667`, `trpc/trpc#5017`, `graphql/graphql-js#1582`,
`bokeh/bokeh#9232`, `grpc/grpc-go#7390`, `BurntSushi/ripgrep#2957` (#137). Previously rejected
candidates are re-examined against E1–E10 rather than inherited: `cockroachdb/pebble#5743`
(E5), `quic-go/quic-go#5220` (E4), `libuv/libuv#4400` (E9), `etcd-io/etcd#17563` (E8),
`etcd-io/bbolt#1179` (E2). Repositories are excluded only at the pull-request level; a different
pull request in a used repository is eligible, and the exclusion log says when one was taken.
The four targets chosen here join this list for every later grid.

## 8. Budget and stop rule

All charged helpers (adjudicators, selectors) reserve on the shared ledger with
`scripts/budget.py … reserve --phase pre-freeze` before launch, using a conservative upper bound
(adjudicator $2.50, selector $1.50, from #137's helper medians with headroom), and settle the
metered cost from `transcript_usage.py` afterwards. The $15.00 cumulative pre-freeze subtotal is
shared with #149's capability probes, so this ticket targets at most $9.00 of it. If a required
helper cannot be reserved inside the subtotal, the remaining categories are delivered as an
unavailable-target manifest with the reason and spend, and the handoff records a
`stopped-budget` disposition for those slots instead of overspending or silently downgrading.
Every helper's transcript is metered to `metering/`.

## 9. Per-target preparation checklist

For each chosen target, in this order, with results recorded in `slot-N/manifest.json` and
`slot-N/setup.md`:

1. Pin repository, pull request, base ref, PR-recorded base OID, head OID, locally computed
   merge-base (from a full staging clone), merged-at instant, review identity (`kamui`, a third
   party, event `COMMENT`, retrospective, render-only).
2. Build the truncated mirror: a bare repository holding only `review-head` at the head and the
   base branch at the merge-base; negative `git cat-file -e` for every SHA in the sealed leak set
   on the mirror and again on every clone; newest reachable commit date equal to the head's.
3. Build the packet with `build_packet.py` (`--experiment-label "issue #138 bounded discovery"
   --subagent-model sonnet`, the target's execution note, default merge cutoff unless E4's
   earlier-cutoff rule applies); record the cutoff, what was omitted (stdout only) and the
   packet SHA-256.
4. Provision dependencies offline where practical (ten-minute allowance); run one focused
   base and head command; record commands, exit status, duration, tree cleanliness. Setup
   results are recorded without adjudicator hints: the public setup log names the command and
   its outcome, never the defect.
5. Adjudicate (fresh helper), seal the register and leak set, commit the ciphertext and hash.
6. Run the selector once; freeze `scope.json` and its hashes.
7. Write the manifest: source packet identity, packet and scope hashes, mirror recipe, access
   checks, execution allowance, provisioning results, original truth version (`v1`, sealed hash).

Preinstalled dependency material is checked for answer leakage (no post-merge version of the
target's own package in any cache).
