# Holdout evaluation — results and verdicts (#60)

**2026-09-04.** The grid ran reduced, at the maintainer's direction, after its cost became clear
(see [What ran and what was cut](#what-ran-and-what-was-cut)). Every figure below is from the run
documents in this directory; per-run billed usage is in [`comparison-data.md`](comparison-data.md).
Ground truth, bands, and scoring rules are the ones committed in [`README.md`](README.md) before the
first cell; where a run produced something the ground truth did not anticipate, the adjudication is
stated here with its reasoning.

## Interpretation correction — 2026-09-05 (#131)

These results came from reviewers forbidden to execute target tests. `v5b-noverify` simulated
unavailable verification and withheld mandatory findings; its outcomes do not establish the
precision of a primary-only publication policy. Under the original [criterion 2](README.md#success-criteria),
0/2 reopenings is **not decidable**, because fewer than three occurrences exist. The `FAIL` label
below is preserved as the original interpretation; importing the effort arm's occurrence cannot
decide the baseline arm's criterion. The observed misses are unchanged.

The 2026-09-05 published-outcome restatement discussed under the lower-effort arm was post-result.
It records a policy deviation, not a preregistered success or new measurements. #124's new matched
experiment follows [the one-shot method](../code-review-one-shot-method.md). Original observations,
numbers, and both historical effort rulings remain below.

## Timing correction — 2026-09-05 (#130)

Historical `Wall` totals are **agent span sums**, adding each transcript's first-to-last
assistant span. Parent waits can include child work, so these are not end-to-end claims. The
old cost table's timing numbers remain historical agent spans; the lower-effort comparison's
old elapsed figures are primary assistant timestamp proxies. Exact root dispatch, final
validation, and final publication/result events were not recorded, so elapsed-to-payload and
elapsed-to-completion are unavailable. Nesting does not establish those boundaries. Preserve
the original numbers and billed rows; new measurements follow the
[timing sidecar instructions](README.md#metering-per-run) and compare the same completion mode.

## What ran and what was cut

| Arm | Planned | Ran | Note |
| --- | --- | --- | --- |
| `v5b` | 18 (six targets × 3) | 15 on (a)–(e); (f) one seed (first review, re-review, stale probe) | (f) seeds 2–3 cut |
| `v5b-effort-medium` (#68) | 6 | 6 valid ((b), (c) seeds 2–4); seeds 1 discarded | discards under the effort rule, see README |
| `v5b-noverify` (ablation) | 18 | 4 (seed 1 on (a)–(d)) | (e) and seeds 2–3 cut |
| Fable tier split | 6 | 0 | maintainer directed Sonnet-only; not measured |

Every run: `claude-sonnet-5` on every assistant line of every transcript, verified at close-out
(`comparison-data.md`, Model verification). The lower-effort arm's primaries at `medium`, every
verifier at `high`, verified the same way.

### (a) `hyperium/hyper#3952` — GT-a1, the hot loop

| Cell | GT-a1 | Status | Findings | False findings | False acquittals on the GT surface | Re-opened? | Band | Dimension 4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v5b seed 1 | **found** (steady-state mechanism named) | Changes Requested | P1 must-fix; P2 consider (CI never runs the new test) | 0 | 0 | n/a | in band | **invariant** — "gate the retry on whether this round actually buffered new output, not merely on `body_rx.is_some()`" |
| v5b seed 2 | found, closing-path projection only | Changes Requested | P1 must-fix (livelock when `close()` leaves `body_rx` set); two P2 consider on the test | 0 | 1 — verifier aside published as an observation: the new term is "provably unreachable during ordinary (non-closing) steady-state body streaming"; #3976 was steady-state | no | in band on status; the published claim is the shutdown projection | branch — "clear `self.body_rx` in `close()`, or force `wants_write_again` false whenever `is_closing`" |
| v5b seed 3 | **acquitted** | Approved | P3 consider (test watchdog never panics) | 0 | 1 — the verifier `refuted` the concurrency candidate and added "the diff is correct as merged" | no | **under** | none |
| v5b-noverify seed 1 | **acquitted** by the primary ("no third path… no bug found") | Approved | two P2 consider on the test | 0 | 1, unchecked (no verifier in this arm) | n/a | **under** | none |

Recall on GT-a1 for `v5b`: one `found`, one closing-path projection, one `acquitted`. Two of the three
`v5b` seeds carry a false acquittal on the ground-truth surface and neither was re-opened: in seed 2
the contradiction arrived as a verifier *aside* and was routed to `Observations` beside the very
finding it contradicts; in seed 3 the verifier corrected a real error in the primary's model of `?`
on `Poll<Result>` and then overshot into "no fix needed". The re-land's rule (flush readiness is not
write readiness) was named by no run; seed 1's progress-gated fix restores it by a different route
and is scored `invariant` under the README's rule. Cost: `v5b` median $4.43 billed, the most
expensive target; seed 3 alone ran 52 minutes with 144k thinking tokens and ended `Approved`.

### (b) `hashicorp/raft#581` — adjudicated clean

| Cell | Status | Findings | False findings | Acquittals checked | False acquittals | Re-opens | Band |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v5b seed 1 | Approved | 0 | 0 | 2 | 0 | 3 warranted, citation grounds (line pointers ~2,000 lines off); re-held | in band |
| v5b seed 2 | Approved | 0 | 0 | 2 | 0 | 0 | in band |
| v5b seed 3 | Approved | 0 | 0 | 2 | 0 | 0 | in band |
| v5b-effort-medium seed 2 | Approved | 0 | 0 | 4 | 0 | 0 | in band |
| v5b-effort-medium seed 3 | Approved | 0 | 0 | 6 | 0 | 0 | in band |
| v5b-effort-medium seed 4 | Approved | 0 | 0 | 3 | **1** (C2: "the timeout-text conflation pre-existed", contradicted by merge-base `raft.go:692-696`) | **1 warranted** (C2 re-opened by the zero-survivor batch, re-falsified, re-dropped on impact and intent) | in band |
| v5b-noverify seed 1 | Incomplete (batch withheld) | 0 | 0 | 3 | 0 | none | in band for the arm |

Zero false findings and zero false re-open rulings across seven cells; the zero-survivor clean-verdict
batch fired in every verified cell and returned `clean verdict stands` in five of six. The one false
acquittal on the ground-truth surface (effort seed 4) was re-opened by the batch, which is the
behavior criterion 2 asks for. Three of seven primaries mis-derived line numbers from tool output
and had them corrected by the verifier; none of those corrections changed a disposition.

### (c) `python/typeshed#9458` — GT-c1, the missing re-export

| Cell | GT-c1 | T-c2 | T-c3 | Other true omissions published | False | Status | Band |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v5b seed 1 | not raised | not raised | not raised | `can_read_destructive` (P2 must-fix) | 0 | Changes Requested | in band |
| v5b seed 2 | not raised | not raised | not raised | `can_read_destructive` (P2 must-fix); abstractmethod style item as P3 consider | 0 | Changes Requested | in band |
| v5b seed 3 | **found** (P2 must-fix) | **found** (P2 must-fix) | not raised | — | 0 | Changes Requested | in band |
| v5b-effort-medium seed 2 | not raised | not raised | not raised | `can_read_destructive` | 0 | Changes Requested | in band |
| v5b-effort-medium seed 3 | **found** (P2 must-fix) | not raised | not raised | `can_read_destructive`, `credential_provider` attribute, retry accessors on `RedisCluster` and on `Redis`/`ConnectionPool` | 0 | Changes Requested | in band |
| v5b-effort-medium seed 4 | not raised | not raised | not raised | `can_read_destructive` | 0 | Changes Requested | in band |
| v5b-noverify seed 1 | not raised | raised, withheld | not raised | `get_message` timeout (P3 consider); five must-fix omissions withheld | 0 | Incomplete | arm's rule followed |

### (d) `astral-sh/uv#4424` — GT-d1, the deferred naming

| Cell | GT-d1 | T-d2 | Other items | False items | Status | Band |
| --- | --- | --- | --- | --- | --- | --- |
| v5b seed 1 | raised (ledger row 9: "explicit deferral in the review record, nothing new to add") | dropped: traced `git show e783a799` and read it as the fix of a self-described incomplete revert | P3 consider (docs claim a download two commands never perform); 1 observation | 0 | Approved | under |
| v5b seed 2 | raised (checklist: "fired, resolved as non-issue") | observation | — | 0 | Approved | under |
| v5b seed 3 | raised (C9 dropped: "a subjective naming preference (gate 7)") | observation | 2 more observations | 0 | Approved | under |
| v5b-noverify seed 1 | raised ("would not meet the 'worth the author's time' bar") | dropped as deliberate | 1 observation (`value_enum` attribute) | 0 | Approved | under |

### (e) `pola-rs/polars#24771` — GT-e1, the benchmark question

| Cell | GT-e1 | T-e1 | Interval-sign item | Other | False findings | Band |
| --- | --- | --- | --- | --- | --- | --- |
| v5b seed 1 | not raised | P2 must-fix (over) | P1 must-fix | P3 consider (`ch as char`) | 0 | over |
| v5b seed 2 | raised (ledger `not-verifiable`, no question) | P1 must-fix (over) | P2 must-fix | P3 consider | 0 | over |
| v5b seed 3 | not raised | P2 must-fix (over) | P3 consider | none | 0 | over |

The question channel never fired: the benchmark claim was a ledger row once and a summary caveat
once, and a candidate never. Every seed instead published two true findings the ground truth had
placed lower: T-e1 at P1/P2 instead of P3, and an item the ground truth did not anticipate — the
rewrite consumes a leading sign before the interval-mode check, so `try_parse_interval("-1d")` now
returns a negative duration where the merge-base bailed with "signs are not currently supported in
interval strings". All three seeds traced the same base and head lines and three fresh-context
verifiers confirmed it; the enforcement it removes was generalized by the same author three days
earlier (#24737), and the PR body and tests never mention interval-mode signs. Adjudicated **true**,
a silent behavior change on the PR's own headline example string, in band at P3 either action;
seed 1's P1 is over. Zero false findings on this target.

### (f) `spf13/cobra#1938` — first review, re-review, stale-head probe

One seed, `v5b`, on `kamui/cobra-holdout#9`. This is the only target that published.

| Round | GT recall / classification | Published | False | Band |
| --- | --- | --- | --- | --- |
| first review at `R1` | GT-f1 **not raised**, GT-f2 **not raised**, GT-f3 **not raised** | one P3 `consider` (name the `TestGetEnvConfig` cases with `t.Run`), one observation | 0 | **under**: `Approved (advisory)` on a diff whose test is red |
| re-review at `R2` | the one prior item classified `fixed` against commit `9740ecead`; the ParseBool-ignored-error fact raised and acquitted as intentional (in band as `consider`, not published) | second review naming `97b7001…1107319`, one observation, one thread reply with `disposition=implemented` | 0 | in band |
| stale-head probe | full re-review done, validator clean, batch built; pre-write re-fetch saw `276cddd6…` against the reviewed `1107319c…` | **nothing** | — | correct |

The first review read `TestGetEnvConfig` to anchor its `t.Run` suggestion and never engaged the
`defer assertNoErr(t, os.Unsetenv(...))` lines that make four of five cases fail; the maintainer
saw it on the same head. The re-review path worked as the reference specifies: delta selection with
an unchanged merge-base (the `context` digest was byte-identical across rounds), widening of the
test file because the delta overlapped the prior anchor, commit-level classification, a `Prior
findings` section, a reply trailer, and the stale-head abort, confirmed from the forge: the pull
request carries exactly the two reviews and the one reply. Two gaps in the reference surfaced:
observations have no carry-forward vocabulary (the run handled it in prose), and the `ancestor` and
`merge-base-unchanged` tokens are never written down, only inferable.

## The lower-effort arm (#68)

Six valid cells, three per target, primaries at `medium` and verifiers at `high`, every one
verified from the transcripts. Controls are the `v5b` cells on the same targets.

| Target | Figure | `v5b` median (n=3) | `v5b-effort-medium` median (n=3) | Change |
| --- | --- | --- | --- | --- |
| (b) | billed $ | 3.04 | 1.93 | −37% |
| (b) | production-shaped $ | 2.90 | 1.80 | −38% |
| (b) | thinking tokens | 55,324 | 29,908 | −46% |
| (b) | output tokens | 99,844 | 70,552 | −29% |
| (b) | turns | 66 | 50 | −24% |
| (b) | tool calls | 73 | 49 | −33% |
| (c) | billed $ | 4.42 | 2.62 | −41% |
| (c) | production-shaped $ | 4.25 | 2.51 | −41% |
| (c) | thinking tokens | 47,841 | 17,736 | −63% |
| (c) | output tokens | 98,083 | 57,712 | −41% |
| (c) | turns | 97 | 81 | −16% |
| (c) | tool calls | 100 | 88 | −12% |
| (b) | primary wall | 0:20:40 | 0:16:03 | −22% |
| (b) | verifier wall | 0:04:37 | 0:05:45 | +25% |
| (b) | elapsed (historical primary-span proxy) | 0:20:40 | 0:16:03 | −22% |
| (c) | primary wall | 0:22:22 | 0:15:42 | −30% |
| (c) | verifier wall | 0:02:05 | 0:01:23 | −34% |
| (c) | elapsed (historical primary-span proxy) | 0:22:22 | 0:15:42 | −30% |

The per-sub-agent walls are the `Wall` figures from each run document's `transcript_usage.py`
block, also in `comparison-data.md`'s Effort verification table. The historical elapsed proxy was
taken at close-out from the transcripts' timestamps (first to last assistant line across the run's
two transcripts). In all twelve runs the verifier batch's span lies inside the primary's, since
every primary dispatched its verifier in the foreground and waited, so the proxy equals the
primary's wall and the summed `wall` in the `TOTAL` block counts that wait twice. The proxy does
not measure dispatch-to-completion. The verifier walls are not an
effort effect — every verifier ran at `high` in both arms — and the (b) increase is one batch of
21,989 thinking tokens on seed 4, the batch that re-opened the C2 acquittal.

**Against #68's estimate.** The ticket guessed, for a low-risk run, −20–40% output tokens, −10–25%
tool calls, and −2–5 minutes; and from the test-4 figures that a −50% thinking reduction would be
about −12% of billed cost and −25% of wall clock before any tool-call reduction. Measured, per
target median: output tokens −29% and −41%; tool calls −33% and −12%; primary-span proxy −4:37 and −6:40;
thinking −46% and −63%; billed −37% and −41%. The billed saving is about three times the guess
because the primary also made fewer requests (turns −24% and −16%), and each request it did not make
was a replay of the whole context, which is where most of a run's dollars go.

**Quality.** Dimension 2: no false finding in either arm on either target; one false acquittal in the
lower-effort arm ((b) seed 4, re-opened by the batch and resolved) against none in the controls.
Dimension 1: GT-c1 `found` once in each arm; the union of adjudicated-true items published on (c) is
the same class in both arms. **Adoption rule: not met**, on the letter of "no false acquittal that
the v5b cells on the same target and seed do not also show": the C2 acquittal in seed 4 has no
counterpart in any control. The re-open resolved it, so the *published* output was unaffected; the
rule as written counts the ledger, and the ledger differs. The cost effect stands on record: roughly
−40% billed dollars and −50% thinking tokens with no change in published outcome on these two
targets.

**Restated rule (2026-09-05, deviation recorded in the README).** At the maintainer's direction the
rule was restated after the runs to count published outcomes rather than ledger rows, and under that
restatement it is **met**: no false finding in six cells, no false acquittal survived to publication,
GT-c1 found once in each arm. The one ledger-level failure, quoted so the deviation is checkable:
the seed 4 primary dropped C2 as "matches stated intent, not contradicted" with the falsification
reason that the same error text "is the pre-existing convention used by the outer select's timeout
branch (raft.go:680-684, unchanged by this diff)"; the clean-verdict batch ruled `disposition C2
does not hold; re-open it`, because the merge-base's `doneCh`-success path (`raft.go:692-696` at
base) "never routed through that string at all"; the primary re-falsified C2 and dropped it on
impact and intent, publishing nothing. The pre-registered ruling stands beside this one. What the
restatement authorises is [#124](https://github.com/kamui/skills/issues/124): the measured shape
(primary at `medium`, every verifier at `high`, on every diff, not risk-surface tiering, which was
never measured and would put lower effort where the zero-survivor batch does not fire), with any
default change gated on three seeds of the arm on target (a), the reasoning-heavy target this arm
never ran.

**Disposition (#68).** Closed by the maintainer on 2026-09-05 with both rulings on record: under
the pre-registered rule, **not met**, on the ledger row above; under the restated rule, which counts
published outcomes (no false finding, no false acquittal surviving to publication, at most one lost
ground-truth item against the controls), **met**, with the C2 row and its re-open quoted above as
the deviation record. The harness passed effort per sub-agent as the README describes (the
not-testable clause did not apply), the six valid cells ran with effort verified on every assistant
line, and each run's record carries billed usage with thinking tokens, turns, tool calls, wall
clock, and effort as passed and as verified. What the restatement authorises is
[#124](https://github.com/kamui/skills/issues/124), the measured shape — primary at `medium` with
every verifier batch pinned at `high`, on every diff — rather than the risk-surface tiering #68
proposed, and not a default change: no skill text, agent definition, or harness default adopts lower
effort on the strength of these six cells, and #124 gates any default change on three seeds of the
arm on target (a). The cost table above is the evidence #124 cites.

Two behaviors were not effort-specific: three Skeptic-line primaries at `medium` and two at `high`
drafted a "verbatim verifier report" section before dispatching the verifier, caught it, and replaced
it (all disclosed); and three primaries at each effort mis-derived line numbers from tool display.

## The ablation (`v5b-noverify`)

Four cells, one each on (a)–(d). On (b) and (c) the arm did what the README predicted: it reached the
verification trigger and withheld, ending `Incomplete` with its must-fix candidates listed and
unpublished. On (a) and (d) it never reached a mandatory trigger and so behaved like `v5b`
without a verifier: on (a) that meant approving the hot loop on the primary's own exhaustive-sounding
trace, the miss a verifier had a chance to catch and, in `v5b` seed 3, did not.

## Cost

| Arm | Runs | Median billed ($) | Median production-shaped ($) | Median wall | #62 estimate |
| --- | --- | --- | --- | --- | --- |
| `v5b` | 18 (15 retrospective + the three (f) rounds) | 3.62 | 3.50 | ~25 min | ~1.8–2.3 |
| `v5b-effort-medium` | 6 | 2.33 | 2.23 | ~16 min | — |
| `v5b-noverify` | 4 | 2.75 | 2.66 | ~16 min | ~1.6–2.0 |

## What the ground truth did not anticipate

- **(a):** the failure mode was not "missed the anchor". All four cells read the same fifteen lines;
  the split was in tracing `Poll` propagation (`?` versus `ready!`), and the verifier both fixed that
  model (seed 3) and then produced the false "fix works" conclusion. A rule that treats a verifier
  aside contradicting a co-published finding as a re-open, not an observation, is the missing piece.
- **(c):** the un-anticipated `can_read_destructive` omission was published by seven of seven cells
  and GT-c1 by two; the upstream trees made the *diff-local* omissions visible and the *package-init*
  omission no more visible than before.
- **(d):** four of four cells did what gate 6 says (deferral marks the question open) and then found
  no rule under which an open naming preference becomes a publishable question. The rubric's
  question rule requires an outcome-changing fact; the deferred question is a preference. The
  playwright GT-2 pattern recurred with the reasoning fully written out.
- **(e):** the benchmark claim never became a candidate because it was never treated as a claim
  about the artifact. Every seed said, in the summary, that it did not re-verify the number, and
  stopped there.
