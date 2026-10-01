# v5a run — `snapshot-path-omitted` against `kamui/shortlist#66`

**2026-09-02.** Data only. Not published to the PR. See
[`addendum-2026-09-02.md`](addendum-2026-09-02.md) for run conditions, model/harness, and the
dev-set caveat that applies to this run.

## Metadata

| | |
| --- | --- |
| Skill | `snapshot-path-omitted` ([PR #19](https://github.com/kamui/skills/pull/19), branch `snapshot-path-omitted`, pinned commit `c5f76df`, `workflow=v5a-1`) |
| Includes fix | `ff94971` "Require repo-wide peer-set search for drift candidates" (handoff 6's fix — the sync-drift paragraph now requires a repo-wide, case-insensitive peer-set sweep on both old wording and new vocabulary before comparing peers) |
| Architecture | 1 integrated reviewer + consequence-triggered fresh-context verifier |
| Agents spawned | 1 (verifier invoked — sole candidate proposed `must-fix`, which is mandatory) |
| Total tokens | **160,853** (harness-reported for this run as a whole; the primary reviewer itself cannot introspect its own token usage — see notes) |
| Tool uses | **64** |
| Wall clock | ~758 s (~12.6 min) — 00:24:37–00:37:15, includes the one foreground verifier dispatch |
| Candidates raised | 4 |
| Candidates surviving primary falsification | 1 |
| Verifier verdicts | 1 confirmed (independent-confirmed) · 0 plausible · 0 refuted |
| Findings for publication | **1** — P2 `must-fix`, blocking |
| Questions | 0 |
| Observations | 2 (cap is 3) |
| Coverage | complete (9/9 files; sibling-skill and cross-repo peer sweep performed; tests re-run read-only) |
| Derived status | **Changes Requested (advisory)** |

## Exact would-be published review

Event: `COMMENT` (self-review; gating not authorized). Retrospective mode — merged PR, publication
disabled by default and not separately authorized, applied explicitly rather than improvised.

### Summary body

```markdown
**Changes Requested (advisory)** — 1 must-fix finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Generalize Research-obligation seeding and Volatile-claim freshness past a fixed
commerce list, formalizing category profiles and a `Volatile-claim class` obligation kind (issue #45).

**Issue fit:** Partial — every acceptance criterion is implemented across the touched protocol,
schema, script, and fixture files, but the freshness generalization is incomplete:
`skills/shortlist-narrow/SKILL.md`'s own restated refresh checklist still names the pre-diff fixed
two-bucket list that `narrowing-protocol.md` just replaced.

**Coverage:** Complete merge-base diff reviewed (9 files). Sibling shortlist-narrow/-research/-start
skills, ADR 0017, freshness-checker.md/check_freshness.py, and use-scenario-catalog.md inspected for
consistency. `python3 -m unittest discover -s tests` re-run locally, read-only (290 passed); TS suite
not re-run as disproportionate to this diff's scope (no routing/locator/question-contract files
touched).

**Reviewed:** `4349ff4` against merge-base `ccd1842`.

## Findings

- [P2] [must-fix] Sync shortlist-narrow's refresh checklist with the generalized Volatile-claim rule — anchor `skills/shortlist/references/narrowing-protocol.md:68`; fix `skills/shortlist-narrow/SKILL.md:46`

## Observations

- ADR 0017 names four obligation categories while `record_schemas.py`'s `OBLIGATION_KINDS` now names
  six, including this change's new `Volatile-claim class`. Evidence:
  `docs/adr/0017-validate-applicable-research-obligations.md`, `record_schemas.py:399`.
- The mechanical offset-timestamp check in `bundle_date_errors` recognizes only commerce keywords
  such as price, stock, delivery, and restock, leaving generalized Volatile-claim vocabulary such as
  catalog or policy terms to the new judgment-only Freshness-credibility attestation instead of a
  mechanical check. Evidence: `validate-completion.py:2945`, `validate-completion.py:90`.

<!-- review-run head=4349ff41ff4d134e09017662dd30420b80e8eb30 base-ref=main base-sha=ccd1842d742fd940b2afde4f903c7bdcb3a707eb merge-base=ccd1842d742fd940b2afde4f903c7bdcb3a707eb workflow=v5a-1 context=6ba3ab62e26b15fd045b6492d6cecf5c726b623fe559686e0f7698de3d08099c issues=kamui/shortlist#45 coverage=complete -->
```

### Finding 1 — anchor `skills/shortlist/references/narrowing-protocol.md:68`, side `RIGHT`

```markdown
**[P2] [must-fix] Sync shortlist-narrow's refresh checklist with the generalized Volatile-claim rule**

**Triggers when:** An agent runs `$shortlist-narrow` on a generalized bundle whose applicability
ledger holds a Volatile-claim class obligation outside the six categories
`skills/shortlist-narrow/SKILL.md:46` names — for example, this PR's own new fixture record, "Ad-tier
feature and price-lock volatility," a Research-origin class the category profile did not anticipate.

**Impact:** Executing SKILL.md's own restated refresh step verbatim gives the agent no textual cue to
refresh that claim before handoff, reproducing the fixed-list assumption issue #45 asks this change
to remove.

**Change:** In `skills/shortlist-narrow/SKILL.md`'s Narrow-the-pool refresh step (line 46), replace
the closed two-list restatement with `narrowing-protocol.md:68`'s ledger-driven rule: refresh every
applicable Volatile-claim class the category and ledger identify, not only a fixed commerce or
generalized list.

**Source:** kamui/shortlist#45, acceptance criterion "Narrow ... does not assume that only commerce
facts can expire."

<!-- finding id=shortlist-narrow/volatile-evidence-fixed-list-drift head=4349ff41ff4d134e09017662dd30420b80e8eb30 priority=P2 action=must-fix blocking=true kind=requirement fix=skills/shortlist-narrow/SKILL.md:46 -->
```

### Context digest

Computed with `scripts/context_fingerprint.py`: `6ba3ab62e26b15fd045b6492d6cecf5c726b623fe559686e0f7698de3d08099c`.

**Determinism check (F1):** computed twice from independently-authored inputs, not just repeated
calls on the same bytes — once from a programmatically-built JSON input, once from a hand-authored
input with the `guidance` array reversed, top-level keys shuffled, and body text re-typed as literal
escaped strings. All three invocations produced the identical digest above, confirming the tool's
canonical-ordering normalization is genuinely order-independent, not merely stable across repeats.

**Guidance-membership judgment call:** included only root `AGENTS.md` and root `CONTEXT.md`.
Excluded `docs/agents/issue-tracker.md` (named excluded explicitly) and `docs/agents/domain.md` (not
itself named `AGENTS.md`/`CLAUDE.md`, and merely linked from `AGENTS.md` rather than independently
qualifying) — the reviewer's stated reading of the output contract's membership rules, applied
literally.

## This is the item the peer-set-sweep fix (handoff 6) was written to catch

The prior un-patched round of this exact skill on this exact target never opened, grepped, or listed
any `skills/shortlist-*` sibling directory and, as a direct result, missed this exact item. This run:

1. Listed all top-level directories (`find . -maxdepth 2 -type d`), surfacing
   `skills/shortlist-narrow`, `skills/shortlist-research`, `skills/shortlist-start` as siblings of
   `skills/shortlist`.
2. Listed every file in all three sibling directories.
3. Ran the peer-set sweep **repo-wide** (root `.`, not scoped to `skills/shortlist/`) and
   **case-insensitive** (`grep -rin`), against both the rule's old wording and its new vocabulary —
   `"price, stock, delivery"`, `"stock and delivery path"`, `"restock"`, and `"volatile"` — exactly as
   the fixed sync-drift paragraph requires. These four sweeps are what surfaced
   `skills/shortlist-narrow/SKILL.md:46` as a hit under both the old-wording ("restock") and
   new-vocabulary ("volatile") searches.
4. Ran a targeted follow-up (`grep -in "volatile\|freshness\|restock\|stale"` across
   `shortlist-research/SKILL.md`, `shortlist-start/SKILL.md`, `shortlist/SKILL.md`) to complete the
   peer set: zero hits in the first two, one non-stale hit in the third.
5. The verifier independently re-ran an equivalent check (`grep -rln -i volatile skills/`) from a
   fresh context and confirmed the same result rather than trusting the primary's sweep.

This explicitly avoids both traps the un-patched round fell into: **not** confined to
`skills/shortlist/`'s own directory (started at repo root), and **not** keyed to one exact phrase
(searched several component phrases of the old wording plus the new vocabulary term), case-insensitive
throughout. **On this specific check, the fix worked exactly as designed.**

## Falsified / dropped candidates (private disposition ledger)

| id | kind | claim | disposition | decisive evidence | why dropped |
| --- | --- | --- | --- | --- | --- |
| `validate-completion/obligation-kinds-hardcoded-elsewhere` | bug | Suspected a second hardcoded Kind enum in `validate-completion.py` now out of sync with `record_schemas.py` | refuted | `validate-completion.py:18-19` imports `OBLIGATION_KINDS`/`OBLIGATION_ORIGINS` directly — no second copy exists | no drift possible |
| `docs/adr-0017-obligation-kind-gap` | maintainability | ADR 0017 enumerates only 4 obligation categories, omitting `Safeguard` and `Volatile-claim class` | refuted as finding → routed to Observations | ADR already lacked `Safeguard` **before** this PR | ADR treated as historical record, not a living spec kept in lockstep |
| `validate-completion/volatile-regex-not-generalized` | bug | The offset-timestamp regex in `bundle_date_errors` matches only commerce keywords, missing generalized Volatile-claim vocabulary | refuted as finding → routed to Observations | New judgment-only "Freshness credibility" attestation explicitly labeled "not mechanically validated"; `check_freshness.py` (the actual refresh tool) already generalized | proportionate, precedented design choice — repo already handles open-ended judgment calls via attestations elsewhere |
| `context-md-volatile-claim-term-not-widened` | maintainability | `CONTEXT.md`'s `Volatile claim` glossary entry doesn't list the PR's added examples | refuted | Entry uses "such as" — explicitly non-exhaustive | no closed-list contradiction exists |

Private requirement ledger (10 ACs): 9 `met`, 1 `partial` (Narrow refresh — protocol-level fixed,
consumer-level (`shortlist-narrow/SKILL.md:46`) still stale — this is Finding 1).

## Files/commands consulted beyond the diff manifest (exhaustive)

Beyond the 9-file diff: `freshness-checker.md`, `check_freshness.py` (grepped), `category-bundle-format.md`
and `search-bundle-format.md` (grep hits inspected), `skills/shortlist-narrow/SKILL.md` (read in
full), `skills/shortlist-research/SKILL.md` and `skills/shortlist-start/SKILL.md` (grepped, zero
volatile/freshness hits), `skills/shortlist/SKILL.md` (grepped), `docs/adr/0017-*.md` (read in full),
`docs/adr/0007-*.md` (grep hits), `docs/design/use-scenario-catalog.md` and
`intake-criteria-and-ranked-narrowing.md` (grep hits), `PROJECT_BRIEF.md` (grep hits),
`research/model-comparison-2026-08-2{7,9}.md` (grep hits), `tests/test_freshness_checker.py`,
`tests/test_category_bundle.py`, `tests/test_validate_completion.py` (two ranges read in full),
sample category-bundle fixtures (grep hits). Git history: `git log --follow -p -- shortlist-narrow/SKILL.md`
and `git show 1450bc2315309b71a0b69defc6430ac9c3cfa6e5` — independently re-confirmed this commit
edited both `narrowing-protocol.md` and `shortlist-narrow/SKILL.md`'s Volatile-evidence wording
together, proving historical lockstep rather than intentional independence.

**One self-corrected process error, disclosed for completeness:** early in the run, a
`git checkout main -- .` intended to diff against base content instead staged `main`'s files into
the `review-head` working tree — a clone mutation against the run's own condition. Caught via
`git status` on the very next call and repaired with `git reset --hard HEAD` before any diff read,
test run, or finding was based on the mutated state. Reported for precision, not because it affected
any conclusion.

Tests: `python3 -m unittest discover -s tests -q` → 290 passed (read-only, clean status before/after).
Node/TS suite deliberately not re-run — the four `.ts` files cover locator/question/routing/
source-access contracts unrelated to this diff's subject; recorded as a reasoned coverage decision,
stated in the Coverage line, not an omission.

One sub-agent spawned: an `Explore`-type fresh-context verifier, given only the rubric-permitted
candidate-mode fields (`id/kind/priority/action/anchor/fix/title/claim/trigger/impact/change/
requirement_source/raw_citations`) with `support` and confidence explicitly withheld per
`verifier.md`.

## Mechanism checklist

- **G2 (Requirements gate scoping) — confirmed, cleanly.** The surviving finding is
  `kind=requirement` with a fix site (`shortlist-narrow/SKILL.md:46`) the diff never touches. Per
  rubric gate 2 ("never refutes a `kind=requirement` candidate... the missing implementation may
  live entirely in an unchanged... artifact"), it was admitted without any anchor/fix workaround —
  the anchor sits on the actual changed line stating the rule being drifted from, `fix` correctly
  points to the unchanged consumer.
- **N1 (Observations) — fired.** Two items landed in Observations (ADR-0017 gap; commerce-only
  offset-timestamp regex vs. the new judgment-only attestation), both accurate facts that failed
  admission on proven-consequence/established-intentional grounds.
- **N3 (Follow-up verifier round) — did not fire.** No candidate newly reached render eligibility
  after the initial verifier batch (one candidate, confirmed with no corrections, no re-opened
  dispositions). Correctly inert — nothing to collect.
- **N4 (`plausible`) — did not fire.** All four candidates resolved decisively (1 confirmed, 3
  refuted); none reached `plausible`, so no question arose from that path.
- **F1 (Contract determinism) — confirmed.** Digest identical across three invocations, two from
  independently-authored/reordered inputs (see above). `validate_review.py` returned 0 violations on
  the assembled payload; its own `--self-test` passed 30/30. Trailer's `fix=` matches the visible
  `Change`/fix text exactly.
- **F2 (Closed-PR / retrospective rule) — applied explicitly, not improvised.** Packet pins the PR
  MERGED with posting identity == author and grants no separate publication authorization, so the
  retrospective clause governs directly. Stated via the exact contract-mandated `**Mode:**` line as
  the summary's second line; skipped the pre-write head re-fetch and publication step per the
  contract's non-publishing-retrospective carve-out.

## Notes on the run

- Own token usage is not exposed to the primary reviewer mid-run; the 160,853-token /
  895,787 ms figures above come from the harness's outer usage wrapper for the whole background
  task, not a self-report — recorded here rather than guessed.
- No mandated fan-out beyond the one verifier: this skill's architecture is a single integrated
  reviewer, and the run followed that (no separate finder agents).
