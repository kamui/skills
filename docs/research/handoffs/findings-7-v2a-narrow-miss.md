# Findings 7 — Why post-fix v2a missed the Narrow-skill closed-list item

Investigation of why `code-review-deep-publish` (v2a, pinned `5db5903`, handoff-5 fix `326ef6f`
included) never raised or acquitted `skills/shortlist-narrow/SKILL.md:46`'s closed Volatile-refresh
list in the 2026-09-02 run against target 1 (`kamui/shortlist#66`), on either axis. Per
`handoff-7-investigate-v2a-narrow-miss.md`. All definition-of-done items complete. Run date of all
replicates and diagnostics: 2026-09-02.

## Verdict

**A trigger-classification gap in the paired-peer-contract-sweep clause, exposed at Sonnet tier —
not sampling noise, not the clause's substance, and not the "only the first qualifying requirement"
scope defect the handoff hypothesized.** The clause (`requirements-axis.md:35`) fires only for
requirements the finder classifies as "chang[ing] a named vocabulary, enum, schema field, or
normative enumeration." In 4 of 5 Sonnet Requirements runs, the finder classified exactly one
change that way — the Kind enum (R1/AC1) — and marked R6/AC6 Met from the changed files alone,
never treating "closed normative list replaced by an open rule" as a qualifying contract change.
The sweep's substance is vindicated every time it fires: the one Sonnet replicate that classified
R6 as qualifying (rep3) and the Opus diagnostic both ran a base-phrase sweep (`restock` /
`price, stock, delivery`) and walked directly into `shortlist-narrow/SKILL.md:46`, raising it as
a finding. Combined score for the item across this round's unchanged-text Sonnet runs: **1/10**
(1/5 Requirements, 0/5 Code). "Unreliable at Sonnet tier for list-opening changes" is the precise
characterization — the handoff's own criterion ("if it appears in a meaningful fraction, say
'unreliable'") applies, but with the mechanism located, not guessed.

Hypothesis outcomes:

- **Two-vocabulary-changes-one-diff (scope) — does not hold as worded.** The diagnostic run with
  the clause reworded to "every requirement whose disposition depends on a qualifying change …
  not just the first one you identify" still missed the item (§4). The clause was already
  per-requirement in letter; the failure is in deciding *whether R6 qualifies at all*, one step
  earlier than the handoff's phrasing reaches.
- **Model tier — holds (n=1, mechanism-consistent).** The byte-identical prompt and skill text at
  Opus raised the item as P2 `consider`, via four explicit per-contract sweeps where Sonnet runs
  typically ran one (§5).
- **Sampling noise — ruled out as the primary story.** 1/10 is not a coin-flip miss, and the
  transcripts show *why* each run lands where it does.

## 1. Original-run transcript (handoff steps 4–5)

Both finders' transcripts survive
(`~/.claude/projects/-Users-jack--t3-worktrees-skills-t3code-93ea65fa/283cabb5-99db-496b-917b-9e231f34c173/subagents/`;
Requirements = `agent-a748adef1bbea2d9d.jsonl`, 50 tool calls; Code = `agent-a8c5a1b3001fb3e66.jsonl`,
29 tool calls).

**The Requirements finder applied the sweep-trigger test to exactly one requirement — its own
words.** Closing "Unfinished work" line: "…the peer-contract sweep was run for **the one
enum-touching requirement**…". It ran the fix's two legs for the Kind enum exactly as designed
(repo-wide `"Discovery branch"` and `"Source family|Candidate relationship|Safeguard"` greps,
tool calls 11–12), found `search-bundle-format.md:208`, produced F1 — and never ran any sweep for
R6.

**AC6 was marked Met with no consumer-file check (handoff step 5: confirmed).** The finder never
opened `narrowing-protocol.md` as a file; its R6 evidence was the diff hunk in the packet,
`research-protocol.md`'s Freshness section, `validate-completion.py`'s new "Freshness credibility"
attestation, and the passing suite — all real, all inside `skills/shortlist/`. Manifest row:
"`narrowing-protocol.md` — reviewed — `Volatile evidence` section generalization checked against
R5/R6." The string `shortlist-narrow` occurs nowhere in its tool calls or output.

**The near-miss: right pattern, wrong scope (tool call 47, event 125).** One search's pattern does
match the missed line:

```
grep -n -i "price and mandatory accessory|stock and delivery path|volatile" \
  skills/shortlist/references/*.md docs/adr/*.md docs/design/*.md PROJECT_BRIEF.md
```

The first two phrases are base-`narrowing-protocol.md` wording — a base-phrase search of exactly
the right kind — but it was issued in service of the R1/AC5 sweep ("another potential live peer of
the AC5 enumeration", event 123) and directory-scoped. The identical pattern run repo-wide hits
`skills/shortlist-narrow/SKILL.md:46` (verified in the pinned clone). Because the sweep mandate
("search the whole repository") was not in force for R6, the finder fell back to the directory-scope
habit findings-6 documented as v5a's trap shape (a).

**Decisive terms never tried at the right scope (handoff step 4: answered).** Across 50 calls:
"materially stale" and "price, stock" — never searched; volatile-family terms — searched three
times, each either file-scoped, directory-scoped, or keyed to new vocabulary the stale consumer by
definition lacks. So: the mandated sweep **never fired** for R6, and the one incidental search that
could have compensated was mis-scoped. ("Never attempted" for the sweep, "engaged and stopped
short" for the incidental search — both of the handoff's step-4 shapes, layered.)

**The Code finder never left the changed skill's neighborhood.** All 29 calls confined to
`skills/shortlist/`, `docs/`, `tests/`, `CONTEXT.md`. It read head `narrowing-protocol.md` in full
— saw the new open rule — and checked no consumer.

## 2. Replicates (handoff step 1) — n=5 per axis, Sonnet 5, byte-identical packet

Fresh clone copies per replicate (verified clean, branches at pinned SHAs before copying), prompts
byte-identical to the originating dispatch except the clone path; outcomes measured from each
replicate's own transcript (tool-call inspection), not self-report.

### Requirements axis

| Run | Narrow item (`SKILL.md:46`) | `search-bundle-format.md:208` | Touched any `shortlist-*` sibling? |
| --- | --- | --- | --- |
| original | **absent** | raised (P3 consider) | no (0/50) |
| rep2 | **absent** | raised (P2 consider) | once — `shortlist-research/SKILL.md`, as a Kind-enum peer only |
| rep3 | **RAISED — P1 must-fix** | raised (P1 must-fix) | yes (8 calls incl. reading `shortlist-narrow/SKILL.md:1-50` and diffing its base blob) |
| rep4 | **absent** | raised (P2 consider) | no (0/63) |
| rep5 | **absent** | **absent** | no (0/44) |

**1/5 raised; 4/5 absent from the ledger entirely (not acquitted).** Every miss shows the same
shape: sweep run for the Kind enum only; R6 marked Met citing `narrowing-protocol.md`'s own
changed text (plus attestation and tests). rep3's success path is the mechanism in positive: it
stated "all three [R1/R6/R8] touch the Kind/Origin enum or the Volatile-claim vocabulary," swept
the surviving phrase `restock`, followed it into `shortlist-narrow/SKILL.md`, and confirmed the
peer was in lockstep at base.

Two sharpening observations:

- **rep5's repo-wide grep returned the missed line and the finder did not act on it.** Its event-24
  search (`grep -n -i "volatile" -r --include="*.md" --include="*.py" .`) returned
  `skills/shortlist-narrow/SKILL.md:46` verbatim in an 18 KB result. No follow-up ever touched the
  file. In-context evidence does not rescue the miss when the finder has no sweep obligation
  attached to R6 — it was reading those results for Kind-enum/new-vocabulary purposes.
- **rep5 also missed the fix's own target item** (`search-bundle-format.md:208`): its sweep legs
  found ADR 0017 and PROJECT_BRIEF but not the bundle contract. The handoff-5 fix is 4/5 on its own
  target at Sonnet tier this round, not 5/5 — same Sonnet-variance family findings-6 flagged for
  v5a (3/6 zero-finding runs).

### Code axis

| Run | Narrow item | `search-bundle-format.md:208` | Touched any `shortlist-*` sibling? |
| --- | --- | --- | --- |
| original | absent | absent (0 candidates) | no |
| repC2 | absent | raised (P3) | no |
| repC3 | absent | raised (P3) | no |
| repC4 | absent | absent (0 candidates) | no |
| repC5 | absent | absent (0 candidates) | no |

**0/5.** No Code run ever listed `skills/` or searched a sibling directory. The two that found the
bundle item did so via repo-wide *enum-phrase* greps ("safeguard, or other category-relevant
work"), which the Narrow skill's text does not contain — findings-6's single-phrase-keying trap
shape (b), reproduced on this axis. The Code brief has no sweep clause at all; original v2's
Code-axis catch of this item (absorbed into v2 F2) is not reproducible at Sonnet tier.

## 3. AC6-on-weak-evidence check (handoff step 5)

Confirmed, across runs: every Requirements run that missed the item marked R6/AC6 **Met** on
evidence drawn exclusively from diff-touched files (`narrowing-protocol.md`'s rewritten section,
`research-protocol.md`'s Freshness section, the attestation, the suite). None widened to the file
the rule is restated in. This is the proximate mechanism the handoff predicted — with the
refinement that it is caused by the sweep-trigger classification upstream, not by a missing
per-requirement obligation in the clause's letter.

## 4. Two-vocabulary-changes-one-diff diagnostic (handoff step 2) — does not hold as worded

One Sonnet run (diagA) with only two edits: the sweep paragraph's opening reworded to "For every
requirement … decide whether its disposition depends on any change in the diff to a named
vocabulary, enum, schema field, or normative enumeration. A diff may contain more than one
qualifying change; apply this test to each requirement independently — completing the sweep for
one requirement does not discharge it for any other," and the dispatch prompt's paraphrase aligned
("…every such requirement, not just the first one you identify").

Result: **item still absent.** The reworded finder found the bundle item (P2), even grepped the
four sibling `SKILL.md` files for citations of `search-bundle-format` — citing
`shortlist-narrow/SKILL.md:12` as liveness evidence for its F1, 34 lines above the missed line —
and still marked R6 Met from `narrowing-protocol.md:67-71` alone. It classified one qualifying
change in the diff. So the cost handoff 5's fix imposed is **not** "sweeps only the first
qualifying requirement"; it is that the trigger's category list reads as *membership changes to a
surviving list* (add/rename a term) and does not read on *retiring a closed list in favor of an
open rule* — which is what the R6 change is, and which is precisely the case where the stale peer
still carries the old closed list. n=1 caveat applies, but the diagnostic was designed to make the
item resurface if scope were the defect, and it did not.

## 5. Model-tier diagnostic (handoff step 3) — holds

One Opus run (diagB), prompt and skill text byte-identical to the originating run. Result: **item
raised** (`requirements/narrow-skill/volatile-refresh-list-still-closed`, P2 `consider`, anchored
`narrowing-protocol.md:68`, fix `shortlist-narrow/SKILL.md:46`). The transcript shows the
qualitative difference, not just the outcome: Opus identified **four** sweep-qualifying
requirements (R1, R3, R5, R6) and ran a distinct paired sweep per contract — "Sweep 2 —
Volatile-class enumeration (new open clause; surviving phrase `price, stock, delivery, and
restock`)" is verbatim the classification every missing Sonnet run failed to make. It also ran
early repo-wide case-insensitive `Volatile` greps, grepped all four sibling `SKILL.md`s for
volatile/refresh terms, read `shortlist-narrow/SKILL.md` in full, and correctly acquitted
`category-bundle-format.md:96` (handoff 5's confusable file) as a different mechanism. Same
finding-6 caveat: n=1 cannot separate "Opus is reliable here" from "Opus got a good draw," and
cannot separate tier from the trigger-wording gap — but it is direct evidence that the identical
text executes at the intended scope on the higher tier, matching findings-6 §5's pattern for v5a.

(Opus also raised two additional candidates the program hasn't tracked — a "category-appropriate
freshness expectation" gap it priced P1 `must-fix`, and the new attestation as Research-stage/
Narrow-stage tense mismatch scope creep. Not this handoff's question; noted for the record since
they bear on any future cross-tier calibration comparison.)

## 6. Is the paired-sweep clause implicated?

Yes — but as an under-specified **trigger**, not as substance and not as scope-per-requirement:

- Substance: validated again. All three runs where the sweep fired for a contract (original run's
  Kind sweep; rep3's two sweeps; Opus's four) found every stale peer of that contract.
- Scope ("each requirement"): the letter is already per-requirement, and making it emphatic
  (diagA) changed nothing.
- Trigger: "decide whether it changes a named vocabulary, enum, schema field, or normative
  enumeration" is answered "no" for R6 by most Sonnet runs, because the R6 change *removes* the
  closed enumeration rather than editing its membership. A finder reading the trigger narrowly has
  no obligation left that would ever reach `shortlist-narrow/SKILL.md`.

Was the miss *caused by* the handoff-5 fix (a regression), or merely *not prevented* by it? The
pre-fix Sonnet baseline for this specific item is thin: the pre-fix originating run found it (1/1,
P1 must-fix, verifier-confirmed), and findings-5 records that both interim weaker-fix validation
runs found it (2/2) while missing the bundle item — but the four pre-fix findings-5 replicates'
Narrow-item outcomes were never recorded (that investigation scored only the bundle item). So
3/3 recorded pre-fix/interim runs found it vs. 1/6 post-fix (original + 5 unchanged-text
Requirements runs incl. this handoff's). That is consistent with the final fix wording *anchoring*
the finder on the enum-shaped change — satisfy the sweep there, close the books — but with n=3
recorded on the pre-fix side, "the fix caused it" cannot be claimed cleanly; "the fix's trigger
wording fails to capture list-opening changes, and Sonnet-tier execution does not compensate" is
what the evidence supports.

## 7. Recommendation

**Propose a specific rubric fix; do not apply it under this handoff.** This is not a trivially
unambiguous wording bug by the handoff's own criterion: diagA proves that one plausible rewording
does nothing, so any candidate wording needs its own model-backed validation round (the same
lesson findings-5 recorded when its first fix draft failed 2/2). Exact edit to validate, in
`skills/code-review-deep-publish/references/requirements-axis.md`, first sentence of the sweep
paragraph (line 35 at `5db5903`):

> Before marking each requirement `Met`, decide whether any change it depends on touches a named
> vocabulary, enum, schema field, or normative enumeration — **including a change that opens,
> generalizes, or replaces a closed list with an open rule; the stale copy is then the one still
> carrying the retired closed list, so take the base-phrase leg's search term from that closed
> list.** A diff may contain more than one such contract; run the sweep separately for each.

The bolded clause is the load-bearing addition (it names the exact classification every missing
run got wrong, and tells the finder what the base-phrase leg means when the list didn't survive);
the last sentence folds in diagA's per-contract emphasis, which is cheap to keep even though it was
insufficient alone. Validation bar, per findings-5's precedent: replicates must show the ledger
naming `shortlist-narrow/SKILL.md:46` as candidate or acquittal — a generic complete review does
not count — *and* must re-confirm the bundle item still surfaces (guard against trading one item
for the other). Also worth stating in DESIGN.md when this lands: the Code axis has no sweep
mechanism and went 0/5 on this item; recall for consumer-drift currently rides entirely on the
Requirements axis at Sonnet tier.

Separately, re-endorse findings-6's open flag: a repeated-seeds evaluation across model tiers is
the only way to price how much of this family is tier execution vs. rubric text. Two skills have
now shown the identical signature (correct clause, under-scoped execution at Sonnet, resolved by
explicit instruction or by Opus).

## 8. Go/no-go on handoff-3's targets 2 and 3

**Go, with one condition on interpretation; hold only if the operator wants single-run recall
claims.** The miss is now characterized: it is item-class-specific (list-opening consumer drift),
mechanism-located, and does not indicate the packet, clones, or orchestration are broken — the
fix's own target mechanism works when it fires, and C1–C5/pole checks in the run doc remain valid.
Targets 2 and 3 can resume under the existing dev-set caveat **provided** no single Sonnet run's
found/missed result is treated as a mechanism verdict — this round showed material single-run
variance in both directions (Narrow item 1/5; even the handoff-5 target item 4/5 Requirements,
2/5 Code). Where a target has a known planted/expected item, score it over ≥3 replicates or note
n=1 explicitly. If the program would rather not carry that caveat, land and validate the trigger
fix first — that is the only ordering in which waiting buys anything.

## 9. Location of this report

Kept at `/tmp/handoff3/investigation-handoffs/findings-7-v2a-narrow-miss.md` per handoff 6's
convention: the core finding is execution behavior under a specific model tier plus an unvalidated
fix proposal, not a settled repo fact. **Promotion recommendation:** if/when the §7 trigger fix is
adopted, promote the evidence with it exactly as `326ef6f` did for findings-5 (fix commit +
DESIGN.md change note + findings file under `docs/research/handoffs/`) — the replicate tables in
§2 are the justification a future reader of that commit will want.

## 10. Method notes, deviations, and other issues encountered

- Replicate prompts byte-identical to the originating dispatch except the clone path
  (`diff` verified after reversing the substitution); fresh clone copy per replicate; guidance
  staging and skill files shared read-only (diagA's reworded axis copy excepted).
- Delivery deviation: replicates received the prompt via "read this file and follow it as your
  task prompt" rather than inline. Content byte-identical; only the first tool call differs.
- Models: Sonnet (default effort) for replicates and diagA, matching the originating round per the
  addendum; Opus for diagB. Note a records inconsistency worth fixing somewhere: findings-5 says
  its replicates ran "Sonnet 5 at high effort" while the addendum pins the originating round at
  default effort — the program's Sonnet baselines are not all at one effort setting.
- The uncommitted run docs this handoff depends on (`v2a-run.md`, `v5a-run.md`,
  `addendum-2026-09-02.md`) exist only in two worktrees (`t3code-93ea65fa`, current, and
  `t3code-3099c1ab`, stale — their `v2a-run.md` copies differ). Evidence for four handoffs now
  rides on uncommitted files; recommend committing `t3code-93ea65fa`'s copies.
- Minor: `v2a-run.md` reports the Requirements finder at 50 tool uses (harness-counted, correct);
  the finder self-reported "approximately 39."
- Replicate artifacts preserved: `/tmp/handoff7/` (per-run clones, prompts, diagA's reworded
  skill copy, `analyze.py`); replicate transcripts under
  `~/.claude/projects/-Users-jack--t3-worktrees-skills-t3code-2b054563/8150d938-c543-45d3-9edf-ecfd00557998/subagents/`.

## Definition of done

- [x] ≥5 Requirements-finder replicates recorded (5, plus 5 Code-finder replicates the handoff's
      step 1 parenthetically requested) — §2
- [x] Two-vocabulary hypothesis tested via reworded-paragraph run; result: does not hold as
      worded — §4
- [x] Model-tier hypothesis tested via Opus run; result: holds, mechanism-consistent — §5
- [x] Transcripts checked for decisive search terms and the AC6-without-consumer-check question;
      both answered — §1, §3
- [x] Verdict stated: trigger-classification gap in the paired-sweep clause, Sonnet-tier-exposed;
      noise ruled out — §Verdict
- [x] Go/no-go on targets 2–3: go with replicate-scored recall, hold only for single-run recall
      claims — §8
- [x] Report written at the required location, with promotion recommendation — §9

## Fix validation

The recommended fix was implemented in two rounds. The first stated the rule declaratively — the
Requirements trigger sentence extended to name list-opening changes, and a new Code-axis
"Sync drift from a changed rule" section describing the paired sweep. It scored 0 of 3 on each
axis. One Requirements run read the extended trigger and still wrote "the only contract this diff
opens/generalizes," naming the Kind enum; a second acquitted the Narrow item on a misreading; a
third demoted the bundle item to an observation. The Code runs did sweep, but keyed their
old-wording legs to whole base sentences ("Timestamp price, stock, delivery, and restock") or to
the wrong contract, and matched nothing.

The second round restructured both briefs around an artifact rather than a classification rule.
Requirements now opens Step 2 with a changed-contract scan whose output — per contract, the two
search terms and every live peer with its disposition — is a required part of the report. The
Code section enumerates qualifying contracts before sweeping any of them, and both briefs require
the old-wording leg to be keyed to a short distinctive fragment, never a whole sentence. This
mirrors what the two runs that ever found the item unprompted did on their own: the passing
Requirements replicate and the Opus diagnostic both began by listing the diff's qualifying
contracts explicitly.

Second-round results, same pinned target, Sonnet 5, offline clone, publication disabled:

| Run | Axis | `shortlist-narrow/SKILL.md:46` | `search-bundle-format.md:208` |
| --- | --- | --- | --- |
| fixR4 | Requirements | candidate `P1` | candidate `P1` |
| fixR5 | Requirements | candidate `P2` | candidate `P1` |
| fixR6 | Requirements | candidate `P1` | candidate `P1` |
| fixC4 | Code | acquitted on a false premise | candidate `P3` |
| fixC5 | Code | candidate `P3` | candidate `P2` |
| fixC6 | Code | never engaged | candidate `P2` |

The Requirements axis moved from 1 of 5 to 3 of 3, and all three runs produced the contract list
as an artifact, naming both changed contracts and acquitting the ADR and brief peers on the
record. The Code axis moved from 0 of 5 to 1 of 3 raised plus 1 of 3 engaged. Its two failure
modes are both still live: fixC4 swept the consumer file and then acquitted it by asserting,
falsely, that an earlier pull request had already generalized it, and fixC6 collapsed its contract
list back onto the enum and never issued an old-wording search for the refresh rule at all. The
Code axis should be re-scored in the next repeated-seed evaluation.

A third live drift on this target surfaced during validation and is not tracked by any prior
round: `skills/shortlist/scripts/validate-completion.py:2948` still gates the offset-timestamp
requirement on the retired commerce wordlist
(`\b(?:price|stock|delivery|restock|availability|available|unavailable)\b`), and
`bundle_date_errors` is called unconditionally at line 3726. One Code run confirmed it by
execution: a generalized-bundle evidence record whose claim names "catalog" passes the validator
without an offset-bearing timestamp, while the same record reworded to name "price" fails.
