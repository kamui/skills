# Preregistration: bounded independent discovery against stronger verification

**Frozen 2026-09-08 (UTC) for [#149](https://github.com/kamui/skills/issues/149), the freeze gate of
the [#138](https://github.com/kamui/skills/issues/138) epic.** This document and its
[manifest](manifest.json) fix everything the grid is allowed to vary, before any reviewer, finder or
verifier has run. Nothing here reports a result: the only model sessions charged to this ticket are
the thirteen capability probes in [`probes/`](probes/), none of which reviewed a target.

Disposition: **ready**, recorded in [handoff.json](handoff.json). [#150](https://github.com/kamui/skills/issues/150)
runs the six-cell pilot and [#151](https://github.com/kamui/skills/issues/151) the remaining
eighteen. A closed prerequisite is not dispatch authorization; this commit is.

Read alongside it: the [method](../code-review-one-shot-method.md) (scoring and accounting),
the [design](../bounded-discovery-prototype/DESIGN.md) (schemas and transitions), the
[adapter](../bounded-discovery-prototype/ADAPTER.md) (executable mechanics) and
[target preparation](../bounded-discovery-prototype/targets/README.md) (the four slots).
Where this document and one of those disagree about an experiment value, this one governs;
where it disagrees about a schema or a scoring definition, they do.

## 1. Prerequisite dispositions

Every blocker is closed **and** delivered something usable, which is the condition #149 was told to
check rather than assume:

| Ticket | Disposition read | What this freeze consumes |
| --- | --- | --- |
| [#146](https://github.com/kamui/skills/issues/146) | design delivered, `ready` | schemas, transitions, arm invariants, the $150/$15 ledger |
| [#147](https://github.com/kamui/skills/issues/147) | adapter delivered with a `stopped-runtime` no-cell entry point | the executable adapter, budget lock, and the probe list this ticket had to run |
| [#148](https://github.com/kamui/skills/issues/148) | four targets `ready`, `dispatch_authorized: false` | packets, selected scopes, mirrors, sealed truth, $9.895998 of sunk pre-freeze spend |
| [#136](https://github.com/kamui/skills/issues/136) | repaired policy pinned | `83bc170e…`, skill tree `bea6be14…`, workflow `v5b-10` |
| [#130](https://github.com/kamui/skills/issues/130) | timing schema shipped | the `completion_mode` / dispatch / validated / completed sidecar |
| [#96](https://github.com/kamui/skills/issues/96), [#97](https://github.com/kamui/skills/issues/97) | shipped | discard accounting and explicit cache-tier pricing |

#147's runtime disposition was a stop: it inventoried the runtime from local help output and left
every effective control unprobed. Section 4 is the work that clears it. Nothing in #147's fake-worker
evidence is treated here as evidence about a real worker.

## 2. Hypothesis and arms

**Does bounding an independent discovery worker and deferring initial verification until its claims
are admitted recover more material defects than spending the same verification budget on a stronger
verifier alone, without adding false findings and without exceeding a 1.25 matched cost ratio?**

| Arm | Primary | Verification | Finder |
| --- | --- | --- | --- |
| A | #136 policy, `claude-sonnet-5` / `high` | the policy's own conditional fresh verification, `claude-sonnet-5` / `high` | none |
| B | identical | identical policy and triggers, workers at `claude-opus-5` / `high` | none |
| C | identical | identical to B, deferred until the discovery barrier | one bounded finder at `claude-opus-5` / `high` |

"Same configuration" for the workers means the same model and the same effort: B's and C's verifiers
are byte-identical definitions apart from nothing at all, and C's finder names the same model and
effort. The finder's *tools* are deliberately narrower — `Read`, `Grep` and `Glob`, no shell and no
sub-agent — because a bounded discovery pass over a selected scope is the treatment, and because it
must never verify. A verifier keeps the shell so it can check evidence outside the finder's frontier,
in every arm alike.

Every arm receives the byte-identical source packet, the same primary policy, prompt, model, effort,
execution permissions, session shape, cache accounting and whole-review ceiling. Coordinator
instructions differ only where C's finder, barrier and admission sequence require it. C's primary
conversation necessarily diverges after it receives discoveries; that is the treatment, not a
confound to be denied. C against B is reported as the discovery-and-timing contrast with identical
verifiers, and is not itself a gate.

### The stronger worker, chosen prospectively

`claude-opus-5` at effort `high`, against the control's `claude-sonnet-5` at effort `high`.

*Actually distinct.* Probe 1 requested the two configurations in one session and observed them:
`claude-sonnet-5`/`high` on all four root assistant lines, `claude-opus-5`/`high` on both child
lines ([`probes/p1-settings/effort.txt`](probes/p1-settings/effort.txt)). Probe 5 repeated it inside
the exact `--restricted` cell configuration. A per-call field or a definition created mid-session
does not establish a child setting; a definition supplied at startup does, and that is what the
dispatch template uses.

*Why it is the hypothesis.* [`tier-split-evaluation-arm.md`](../tier-split-evaluation-arm.md)
treats Opus 5 as the higher tier and Sonnet 5 as the cheaper one, and prices them at $5/$25 and
$2/$10 per million tokens; its arm A is "the configuration the current evidence describes", with
Opus verification. PR #183 measured *effort* inside one model and did not qualify medium for
adoption, which is why effort is held at `high` in every context here and the treatment moves the
model tier instead.

*What it is not.* No measurement in this repository compares these two models as review verifiers on
a common target set. "Stronger" is a treatment hypothesis. If B does not beat A, the honest reading
is that this configuration change did not help on these targets — not that the tier ordering is
wrong. The retained common primary follows #124's decision (`high` primary, `high` baseline
verifiers, in the measured Claude/Sonnet runtime); no other runtime inherits it, and none is used.

## 3. Pins

Exact artifacts, not a moving `main`. [`manifest.json`](manifest.json) carries the digest of every
file named here; [`scripts/verify_freeze.py`](scripts/verify_freeze.py) recomputes all of them, the
git pins, the scope bindings and the ledger reconciliation, and exits non-zero on any drift. Run it
before each dispatch.

- **Policy under test (common to A, B and C):** commit `83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6`,
  skill tree `bea6be143582e75bada966ee85964623ef31f167`, workflow `v5b-10`, extracted with
  `git archive` into the cell's snapshot directory. Cells never read a checkout.
- **Method, design, adapter, prototype scripts, research helpers, freeze tools, rate card:** pinned
  by digest in the manifest.
- **Targets:** the four #148 slots with their packets, selected scopes, slot manifests, sealed
  registers, mirror refs, clone recipes and per-target execution notes. Repository, PR, base ref,
  base OID, merge-base OID, head OID and cutoff are pinned per slot.
- **Repository state read for this freeze:** `cfde565d8b27237b7c378a474e8008d27ac25bfe`.

The ledger is the one input deliberately **not** pinned by file digest. Every cell appends a
reservation and a settlement to it, so a digest pin would fail the next cell's own gate on ordinary
progress. What is pinned is its event **prefix** — the chain through the `cap-freeze` event, which is
the history the freeze rests on. Everything after it is checked as behaviour: unbroken chain,
snapshot reconciling to the events, the frozen cap and protected reserve unchanged, the closed
pre-freeze subtotal unmoved, and room still left under the cap.

### The scope-to-packet binding

#148 handed over each `scope.json` with `source_hash` set to the bare digest of that slot's
`packet.md` and a note that #149 must bind it to the SourcePacket `ArtifactRef`. The binding is
recorded in the manifest — each slot carries the packet as a full `{uri, sha256, access}` reference
and asserts the equality — rather than by editing `scope.json`. Editing it would change its digest,
which is pinned in that slot's `manifest.json` and again in #148's `handoff.json`, so a one-field
edit would invalidate two frozen artifacts to record something a check can verify.
`verify_freeze.py` recomputes `sha256(packet.md) == scope.source_hash` for all four slots on every
run; all four hold at this commit. The adapter's own check (`scope["source_hash"] ==
config["source"]["sha256"]`) is the same equality, so no dispatch can proceed without it.

## 4. Runtime capability: what the probes established

Thirteen headless sessions, $1.0418428 charged and $0.082158 retained as uncertainty, all inside
#146's $15.00 pre-freeze subtotal. Every one is metered, model-and-effort verified and committed under
[`probes/`](probes/); [`probes/README.md`](probes/README.md) has the detail. Freshness was checked
mechanically rather than asked of the model: each session's transcript opens with exactly one user
message — the probe prompt — and carries no summary or resume record
([`probes/freshness.json`](probes/freshness.json)).

| Control | Status | Evidence |
| --- | --- | --- |
| distinct child model and effort | **enforced** | probes 1, 5 |
| fresh context per worker | **enforced** | `freshness.json` |
| finder file confinement | **enforced** | probe 2a: out-of-root reads, an absolute path, a symlink resolving outside the root and an out-of-root Grep all denied; no network tool exists in the session |
| primary/verifier file-tool confinement | **enforced** | probe 5: an out-of-root `Read` denied, naming the permitted roots |
| unlisted shell commands | **enforced** | probe 6: `curl` denied automatically, because a `--print` session with `--permission-prompts none` has no approval surface |
| network by host name | **enforced** | probe 2c: `api.github.com` and `raw.githubusercontent.com` refused and logged by the egress proxy while the provider was allowed and the session ran normally |
| cancellation and provider termination | **enforced** | probe 3: SIGTERM at 25 s, exit 124, no payload, no surviving process, transcript unchanged 25 s later |
| bounded request allowance | **enforced, with one call of overshoot** | probe 4: `--max-budget-usd 0.05` stopped the session with `subtype: error_max_budget_usd` after spending $0.067136 |
| atomic budget contention | **enforced** | probe 3: of two operations against the same remaining capacity, one was admitted and the second exited 1 with no event written |
| billed totals from retained usage | **enforced** | `meter_split.py` reproduces the runtime self-report from the per-request records for every session that produced one: five to within $0.0000005, and six about $0.0013 low each — an untranscripted `claude-haiku-4-5-20251001` request whose cost matches each gap exactly ([`probes/reconciliation.json`](probes/reconciliation.json)) |
| the cell can write its payload, report and script output | **enforced, and it needs the allow list** | probes 8 and 9: under `--restricted` with `--permission-prompts none` the write tools are denied outright unless `--allowedTools` names them — while an allow-listed `python3` writes freely — and naming `Write` and `Edit` restores writes inside the roots while still refusing one outside |
| background verification | **supported, and deliberately not used** | probe 10: the primary dispatched a verifier with `run_in_background: true`, ran a shell command while it was still going, and collected its result from the completion notification. The frozen rule is foreground anyway; section 10 says why |
| **shell filesystem reach** | **audited, not enforced** | probe 7: with `Bash(python3:*)` allow-listed, `python3 -c "print(open(...).read())"` read a canary outside every permitted root, and so did a `subprocess` call. An allow-listed `cat` was blocked; an interpreter is not. |
| **raw-socket egress** | **audited, not enforced** | probes 2c and 6: a direct TCP connection to an IP address on port 443 succeeds through an allow-listed `python3` |

A reviewer primary needs `python3` (the policy's own `validate_review.py`) and `go`/`cargo` (the
per-target execution allowance), so an interpreter cannot be removed from the allow list. The two
audited rows are therefore real and are handled by section 5 rather than described away.

## 5. Isolation: absence, not confinement

Probe 2b ran a session configured exactly like #137's grid runner. It read the primary store, another
attempt's store, the evaluator truth directory and another target's mirror directory, and it reached
`api.github.com` with HTTP 200. Probe 7 showed that tightening to `--restricted` with a Bash allow
list does not close the interpreter path. The control that actually holds is that **the material is
not on the machine while a cell runs**.

**Two phases, because one moment cannot satisfy both controls.** The leak-set check has to read the
sealed leak set, and the absence gate requires that same evaluator storage to be gone — so
[`scripts/check_cell_isolation.py`](scripts/check_cell_isolation.py) runs first in a `preparation`
phase, while the evaluator material is still present, and emits an **attestation**: the clone head,
base and merge-base, the mirror's refs, a digest of every object each repository holds — referenced
or not, alternates followed — the SHA-256 of the leak-set *file*, and how many objects it examined
and how many hit. HEAD and refs alone would not bind it: an object can arrive in a store without
moving either, which is precisely the leaked evidence the leak-set check rules absent. It carries no SHA *from* the set, so it crosses into the dispatch window
without carrying truth with it. The file digest names which set was checked; nothing during the
dispatch window can compare it, because the file is deliberately gone by then, but #152 and #153 can
once the sealed material returns — which is what makes the attestation auditable rather than merely
asserted.

**Mandatory before every dispatch, and again after the cell stops**, once the evaluator material is
removed. The script writes a dated record and exits non-zero unless all of the following hold:

1. every forbidden path is absent: `~/.config/bounded-discovery/` (the key, the plaintext registers,
   the leak sets and the decrypted schedule), every other slot's mirror, clone and staging clone,
   every other attempt's store, and every checkout of this repository, which contains this
   preregistration, the design and `targets/README.md` — the last of which discloses that one of the
   two `nats-io/nats-server` slots holds the confirming fix for the other's defect, and so would leak
   truth about that slot to a reviewer reading it;
2. the permitted roots exist and contain no forbidden path;
3. the clone is at the pinned head, its base branch at the pinned merge-base, and its tracked tree is
   clean;
4. the preparation attestation covers these exact object stores — same head, same refs, the same
   digest over every object in the clone and in the mirror, and no alternate store in either — and
   records a non-empty leak set, with a file digest and zero hits. No evaluator file is read in this
   phase, and none needs to be;
5. the egress proxy is listening and refuses a host that is not on its allow list.

#148's sealed README made moving the key off the machine an alternative. Here it is mandatory. The
committed ciphertext may stay: without the key it is inert.

**Audited, and invalidating.** Every cell runs behind
[`scripts/egress_proxy.py`](scripts/egress_proxy.py) with only `.anthropic.com:443` allowed and every
attempt logged. After the cell stops, its transcripts are scanned for paths read and commands run. A
read outside the permitted roots, or any network use that does not appear in the egress log, makes
that attempt **invalid on protocol grounds** and replacement-eligible under the three-replacement
allowance. It is not scored as a substantive result.

**One cell at a time.** The design permits two concurrent cells and the adapter still enforces that
ceiling, but the frozen schedule never uses it: two live cells on one machine are readable by each
other through the same interpreter path. This costs wall-clock time and nothing else.

## 6. Cells, order and replacement

Twenty-four planned cells: four slots × A/B/C × two fresh replicates. Cell IDs are
`<slot>-<arm>-replicate-<n>`; attempt IDs are `issue-138-<cell_id>-attempt-<n>` and are never
recycled — the ledger refuses a reused one. A replicate is a fresh independent context and clone,
not a reproducible sample: the runtime exposes no API seed, so a replicate is an ordinal.

**Order.** The rule is frozen here; the resolved order is sealed. Pilot = the adjudicated clean slot
and the lowest-numbered buggy slot, replicate 1, arms A/B/C per slot with the clean slot first. Then
replicate 1 of the remaining slots and all of replicate 2, slots in numeric order, arms A/B/C within
a slot. Every A/B/C triple is contiguous, so a budget or runtime stop leaves whole triples — the unit
the matched cost ratio and per-target recall both need.

The resolved list is sealed because naming the pilot pair in the clear would tell any reader which
two slots hold the clean target, and therefore which two do not.
[`scripts/seal_schedule.py`](scripts/seal_schedule.py) read only each register's `Verdict` line,
checked every register against #148's `SHA256SUMS` first, and wrote
[`sealed/schedule.json.enc`](sealed/schedule.json.enc) under #148's key. Its plaintext digest is
`598584e4976e52fbecd24fa3d92190b9d431337ed07a9adb2df8fd6f68dd6a1b`, recorded in
[`sealed/SHA256SUMS`](sealed/SHA256SUMS); #150 and #151 decrypt it with the reveal procedure in
[`sealed/README.md`](sealed/README.md). #150 owns the six `pilot` cells, #151 the eighteen `grid`
cells. Pilot outcomes stay sealed for quality comparison until every reviewer run has stopped.

**Replacement.** Three replacements maximum, 27 attempts maximum across the epic — enough for one
affected triplet. This prospectively overrides the general method's older two-replacement rule for
#138 only; historical experiments keep theirs. A replacement is earned only by documented
infrastructure or input invalidity, and it invalidates exactly the comparison cells that change
affected; unrelated faithful cells stand. A valid substantive miss, a false finding and a skill
timeout are results, not rerun opportunities. If required invalidation exceeds the allowance, stop
and close out the partial experiment.

## 7. One enforceable budget

Sunk spend is reconciled first, not written off. #146 and #147 charged nothing; #148 charged
$9.895998 for six selectors and six adjudicators; this ticket's probes charged $1.0418428 and retain
$0.082158 of uncertainty for one request the cancelled probe may never have recorded. Pre-freeze
actual is **$10.9378407** of the $15.00 subtotal. The cap was frozen against a $135.99 projection
before probes 8 and 9 ran; deviation 5 records why the recomputed $136.0527 leaves it unchanged.

Every figure is shown to four decimal places and computed from the unrounded inputs, so the column
adds up as printed. The per-arm means are themselves rounded for display: recombining $3.4200,
$3.7413 and $5.6294 by hand gives $102.3256 for the 24 cells rather than the $102.3254 below, because
B's unrounded value is $3.74125 and rounds up while C's $5.629430 rounds down. Two hundredths of a
cent changes nothing here, and the gate uses the unrounded numbers throughout.

| Line | Amount | Basis |
| --- | --- | --- |
| Sunk pre-freeze, including probes | $10.9378 | the ledger |
| Retained uncertainty | $0.0822 | the cancelled probe's largest observed request |
| 24 cells | $102.3254 | 8 × ($3.4200 A + $3.7413 B + $5.6294 C) |
| Three-replacement allowance | $12.7907 | 3 × the $4.2636 mean cell |
| Grading and closeout reserve | $10.0000 | #152's blind adjudication and per-target scoring plus #153's synthesis |
| **Projected full experimental cost** | **$136.1361** | |
| **Frozen cap** | **$150.00** | `min(1.5 × 136.1361, 150)` |
| Headroom | $13.8639 | 9.2% of the cap |

The per-cell figures come from measured runs at the dated rates in [`rates.json`](rates.json), not
from a guess. A is the mean attempt cost of the twelve `bea6be14` cells in
[`one-shot-qualification-2026-09-07/metering/cells/`](../one-shot-qualification-2026-09-07/metering/cells/)
— the same #136 policy, same runtime, same session shape: $3.4200, of which the verifier children
were $0.2142. B reprices those children at Opus's 2.5× ratio. C adds a finder priced from the six
#148 selector sessions ($0.6270 mean at Sonnet, the closest available analogue: a fresh bounded
read-only session over one of these packets) at the same ratio, plus ten per cent of the primary for
admission and falsification of finder claims. The grading line scales #137's per-target scorers by
this grid's six attempts per target and adds blind adjudication and synthesis.

**The headroom is thin and the risk is stated, not smoothed.** Measured cells under this policy
ranged $2.02 to $6.78 — a 3.3× spread. At the observed maximum throughout, 24 cells would exceed the
cap. The `min(1.5 × projected, $150)` formula gives no real contingency here because the $150 ceiling
binds; what protects the experiment instead is the ledger's atomic reservation, which refuses the
first dispatch that cannot fit, and the contiguous-triple order, which makes a mid-grid stop leave an
interpretable partial grid rather than a ragged one. This is a `stopped-budget` risk that is accepted
prospectively, not a design that shrinks if money runs short.

**Numeric ceilings**, equal across A, B and C:

| Ceiling | Value | How it is held |
| --- | --- | --- |
| whole-review dollars per attempt | $9.00 | `--max-budget-usd`, plus a ledger reservation of the remaining allowance before every dispatch |
| one-call headroom | $1.00 | added to every reservation, because probe 4 shows the allowance is checked after a call completes |
| whole-review billed tokens per attempt | 30,000,000 | audited against the retained per-request records |
| root wall clock per attempt | 5400 s | `timeout`, counted **once from the root dispatch instant** — in arm C the resumed phase gets only what is left, and the barrier wait and the finder's run fall inside the same window |
| model requests per attempt | 400 | audited |
| shell commands per attempt | 120 | audited |
| per focused command | 300 s | the per-target execution note |
| provisioning per target | 600 s | the method's default |
| **finder sublimit** | $2.00, 1800 s, 4,000,000 tokens, 80 requests | `--max-budget-usd` on the finder session; **charged inside C's $9.00, never in addition** |

$9.00 is 2.6× the mean A cell and 1.28× the most expensive cell ever measured under this policy. A
cell that needs more stops as `stopped-budget` and is reported as an incomplete attempt, in every
arm alike. The runtime has no hard token control, so the token, request and command ceilings are
audited after the fact and an overrun is recorded rather than prevented; the dollar allowance is the
enforced one. Billed tokens are uncached input + cache write by tier + cache read + output; output
already includes thinking and is counted once, and `transcript_usage.py` deduplicates streamed
records of a single request by taking the maximum of each counter. There are no paid tool charges.

**Settlement.** Settle from the runtime self-report and from the retained per-request records; when
they differ, charge the larger and record the difference as a reconciliation residual. Every cell
will have one, and it has a name: six of the probes billed about $0.0013 more than their transcripts
account for, and in each case the result envelope's `modelUsage` carries a
`claude-haiku-4-5-20251001` entry whose cost equals that gap to the last digit. The runtime bills a
small Haiku request it never writes to the transcript. Meter a cell from both sources — the
transcripts for the per-role split, the result envelope for what they never saw — rather than
treating the difference as noise. An attempt
that produced no self-report settles from its transcript and retains one further request at the
largest observed per-request cost as uncertainty — exactly what probe 3 did. Review consumption,
one-off setup and selection, and charged grading are reported in separate columns; shared setup is
charged once to the epic, never once per arm and never omitted. Any production-shaped amortization is
a separate estimate and never replaces billed spend. Matched cost compares billed cells from this
grid; #137's absolute dollars are not transplanted.

## 8. Prospective screening

Applied by [`scripts/score_attempts.py`](scripts/score_attempts.py), which consumes explicit
adjudicated fields only — target status and defect IDs, and per attempt its validity, completion,
published status, clean claim, recovered and sufficiently-fixed defect IDs, false-finding counts and
billed cost. It never infers materiality or a clean verdict from prose; #152 makes those judgments
and this does the arithmetic. Definitions are the method's section 4, unchanged.

Screen B against A, and C against A, separately. Every criterion must hold:

1. **zero** raw false finding items in the candidate arm, invalid attempts included;
2. no worse false-clean count **and** no worse false-clean rate;
3. no worse completion;
4. macro material recall: at least a 20% relative gain with a positive absolute gain, in **both** the
   all-attempt and the completed-only view; where the control's macro recall is 0, the gate is +10
   percentage points instead;
5. median matched billed cell-cost ratio ≤ 1.25, cells matched by target and replicate, each cell
   charged all of its attempts including discarded predecessors.

Reported alongside, as decision evidence rather than gates: sufficient-outcome recall `S/D`,
aggregate fix sufficiency `S/R`, unjustified action errors, priority errors, and zero-recovery
attempts that did not claim clean.

Unresolved material truth, a planned cell without a **valid completed** outcome — attempted but
invalid or unfinished counts as missing, not as present — or a changed clean/buggy target mix blocks
a positive screen and forces `inconclusive`. One thing outranks those blockers: a supported raw false
finding **rejects** the arm outright, even when unrelated cells are unavailable, because a false
finding is decisive on its own evidence and does not need the rest of the grid to be interpretable.
The blockers are still reported in that case; the verdict is `fail`, not `inconclusive`. A partial
run reports what it measured rather than collapsing into a global inconclusive.

**False clean is frozen independently of recovery credit, reviewer priority or action, and fix
sufficiency.** An attempt on an adjudicated buggy target that explicitly returns Approved / clean /
no material defects is false clean — even if it recovered the defect, even if it reported it as a
`consider`, even if it also declared operational incompleteness. Both recorded signals carry it: a
published `status` of `Approved` *is* an explicit clean return, so it counts whatever the
`clean_claim` field says, and an attempt recorded with one and not the other is refused as
contradictory input rather than scored. Status is validated against the output contract's four
values, so a typo cannot quietly become "not Approved". The first frozen scoring check is
exactly that case, a synthetic attempt that recovers `D1` with a sufficient fix and publishes
Approved: it scores recall 0.5 **and** false clean 1. Eleven checks in
[`scripts/scoring-fixtures.json`](scripts/scoring-fixtures.json) run under
`python3 scripts/score_attempts.py --self-test`; every one is synthetic and none is evidence about
any arm. The recovered-but-Approved case carries forward to #152.

A complete positive screen recommends a **fresh confirmation study** against the then-current
integrated policy. Four targets and two replicates cannot support an equivalence claim or a
promotion. A supported false finding can reject an arm even when unrelated cells are unavailable, and
a partial run is reported as what it measured rather than forced into a global inconclusive.

## 9. Fidelity requirements

- **Model and effort** are verified with `agent_effort.py` on every assistant line of every
  transcript — root, finder, initial verifier, follow-up verifier and every continuation — with
  `--expect-model` and `--expect-effort` for that role. A mismatch or an unobservable setting is a
  fidelity failure and invalidates the attempt; it is never relabelled as an equivalent treatment,
  and no provider or model is substituted silently.
- **Cache accounting** is identical in every arm. Headless cells write the one-hour tier, priced
  ×2.0, with the five-minute tier ×1.25 and reads ×0.1, as `transcript_usage.py` reports them.
  Because a C cell mixes models, each transcript is priced at its own model's rate and the groups
  summed — that is all [`scripts/meter_split.py`](scripts/meter_split.py) does, by calling the two
  pinned helpers rather than copying their parsers. It refuses a transcript that mixes models.
- **Batch modes, no-batch reasons, row coverage and stage records** are the design's, frozen by
  pinning DESIGN.md's digest. A and B may legitimately dispatch no verifier under the pinned rules;
  those outcomes and their costs are counted, not forced into a batch and not excluded as substantive
  misses.
- **Timing** uses #130's sidecar unchanged: `completion_mode` `render-only`, `root_dispatched_at`,
  `payload_validated_at`, `completed_at`, with a stopped attempt's `stopped_at` in its Attempt record
  outside the sidecar and its duration reported as censored. Worker spans are recorded separately and
  never replace root elapsed.
- **The common policy stays #136** in all three arms, including its permitted omissions. #185 and
  #186 landed after the snapshot; they are recorded as limits on applicability, and a current-policy
  comparison requires its own frozen study.

## 10. Interpretation limits carried into this freeze

- **#137's corrected comparison** ([comparison data](https://github.com/kamui/skills/blob/bdd1c4a36ba9d4bb0890a66b9579203bc9f3ea19/docs/research/one-shot-qualification-2026-09-07/comparison-data.md),
  [metering handoff](https://github.com/kamui/skills/blob/bdd1c4a36ba9d4bb0890a66b9579203bc9f3ea19/docs/research/one-shot-qualification-2026-09-07/ledger.md),
  decision in #71) is a negative screen on a changed target mix. It is carried here as an
  interpretation limit only. Corrected reporting is not a new experiment and does not alter the
  common policy.
- **PR #183** did not qualify medium effort for adoption: cost ratio 0.94 against ≤ 0.80, with its
  recall advantage confined to known Hyper. Effort is `high` everywhere here as a result.
- **slot-3's selector output** characterises a lock as a hazard, drawing on that pull request's own
  body text. #148 flagged it for this gate. It is kept as delivered — reselecting after seeing it
  would be worse than the cue — and recorded as a possible over-cue of C's finder on that slot. Read
  slot-3's C cells with that in mind.
- **The packets' worker-model line** is the literal string
  `<the model your dispatch names for that worker>`, deliberately, so that every arm receives
  byte-identical packets. [`dispatch-template.md`](dispatch-template.md) names the model for each
  worker and says that this packet line means the dispatch's value.
- **Verification runs in the foreground in every arm, by choice.** Probe 10 established that this
  runtime does support background sub-agents, so the constraint is the experiment's, not the
  harness's. Token cost is unaffected and every arm carries it equally, so no gate moves. Elapsed
  time does move: an A or B attempt serialises its verifier where the pinned policy's #70 early
  dispatch would have let it overlap the primary's remaining low-risk work. Read the arms' elapsed
  distributions as this harness's timing, not as the policy's production timing, and do not read C's
  relative wall clock as evidence that deferring verification is cheaper in time.
- **Nothing here establishes that `claude-opus-5` verifies better than `claude-sonnet-5`.** That is
  the hypothesis under test.

## 11. Deviations from the frozen inputs, dated

1. **The scope-to-packet binding is recorded in the manifest rather than written into
   `scope.json` (2026-09-08).** Reason and verification in section 3. #148's artifacts are unchanged
   and their digests still hold.
2. **Concurrency is frozen at one cell although the design permits two (2026-09-08).** Reason in
   section 5. The adapter's two-cell ceiling is unchanged.
3. **`budget.py` gained a `cap-freeze` operation (2026-09-08).** DESIGN's `BudgetEvent` vocabulary
   already contained it; #147 implemented only `reserve` and `settle`, so #149 had no way to record
   the gate it owns. The operation sets the frozen cap and the protected reserve exactly once,
   refuses a cap below the sunk spend or above the ceiling, refuses a cap that cannot also hold the
   reserve, and refuses a second freeze. Covered by
   `test_adapter.py::AdapterTests::test_cap_freeze_gates_the_review_phase`.
4. **Arm C's primary runs as two invocations of one session (2026-09-08).** The barrier needs the
   primary to freeze before it sees any finder claim, and a `--print` session cannot be handed a
   second message mid-run. Phase 1 ends with the freeze artifact written and hashed; the coordinator
   verifies both freezes, terminates the finder, and resumes the same session with the compact
   claims. A and B run as one invocation. The extra process boundary is part of C's treatment.

5. **Probes 8 and 9 ran after the `cap-freeze` event (2026-09-08).** The gate was recorded against a
   $135.99 projection; then probes 8 and 9 found that the cell configuration as written could not
   write its own payload, and fixed it. They are pre-freeze spend inside the same $15.00 subtotal and
   they raise the projection to $136.1361, together with probe 10, which answered the review's open
   question about background verification. It still fits the $150.00 cap, with $13.8639 of headroom.
   The `cap-freeze` event is left exactly as written — it was true when it was recorded, and the
   ledger's event chain is append-only — and the cap it set is unchanged, because `1.5 × 136.1361`
   still exceeds $150.00. Section 7's table carries the recomputed figures.
6. **Two earlier stage records now quote stale digests (2026-09-08).** #147's
   `implementation-handoff.json` records `ADAPTER.md` and `ledger.json` as they were when it
   delivered, and #148's `handoff.json` records `ledger.json` as it was when *it* delivered. The
   ledger is a living shared artifact by design — every chargeable operation across the epic appends
   to it — and `ADAPTER.md` gained a dated pointer to the probe results plus a correction to its
   "$0 incurred" sentence and its `budget.py` row. Both stage records are left exactly as delivered:
   they are true about the moment they describe, and this bundle carries the current digests.

## 12. What #150 does next

Decrypt the sealed schedule, take its six `pilot` cells in order, and for each: run
`verify_freeze.py`, prepare the cell environment and run `check_cell_isolation.py --phase
pre-dispatch`, reserve the attempt on the ledger, dispatch per
[`dispatch-template.md`](dispatch-template.md), then re-check isolation, meter with `meter_split.py`,
verify model and effort, settle, and archive the attempt's artifacts. Stop on any non-zero exit and
read the handoff rather than dispatching again. Keep the pilot's outcomes sealed until every reviewer
run has stopped.
