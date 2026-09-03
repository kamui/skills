# v2a run — `code-review-deep-publish` against `kamui/shortlist#66`

**2026-09-02, second run (post-C9).** Data only. Not published to the PR. See
[`addendum-2026-09-02.md`](../prototype-runs-2026-09-01-test-1/addendum-2026-09-02.md) for run conditions, model/harness, and the
dev-set caveat that applies to this run. The earlier same-day run under the pre-C9 skill is kept as
[`v2a-run-pre-c9.md`](../prototype-runs-2026-09-01-test-1/v2a-run-pre-c9.md); this run supersedes it.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-deep-publish` (research nickname **v2a**, "Panel line"; [PR #18](https://github.com/kamui/skills/pull/18), branch `t3code/prototype-code-review-publish-2a`, pinned commit `87c68a9`) |
| Includes fixes | `326ef6f` "Require paired peer-contract sweeps" (handoff 5) **and** `940aa2c` "Sweep every changed contract, on both axes" (DESIGN.md §C9, merged via PR #38 as `87c68a9`): the Requirements axis must write a changed-contract list before sorting requirements, run a paired repo-wide case-insensitive sweep per contract, return the list, and may not mark a requirement `Met` while a live stale peer exists; the Code axis gains a "Sync drift from a changed rule" section |
| Architecture | 2 axis finders in parallel (Code, Requirements) → 1 mandatory fresh-context verifier |
| Model | `claude-fable-5-1` on every agent (orchestrator, both finders, verifier), verified from the harness's sub-agent transcripts. **Run 1 ran on `claude-sonnet-5`**, so this run is not model-matched to the one it supersedes — see the addendum's regression watch |
| Agents spawned | 5 (1 orchestrator, killed; 3 finder attempts, 1 killed; 1 verifier) — see "How this run was executed" |
| **Sub-agent tokens, completed path** | **249,628** |
| — Code finder | 75,860 (25 tool uses, 270,814 ms / ~4.51 min) |
| — Requirements finder (attempt 2) | 105,117 (29 tool uses, 475,720 ms / ~7.93 min) |
| — Verifier | 68,651 (20 tool uses, 241,479 ms / ~4.02 min) |
| Tool uses (completed path) | 74 |
| Wall clock (completed path) | ~988 s, but **not** the parallel shape v2a normally has: the Code finder ran in the first attempt, the Requirements finder ran alone in the second, and the verifier followed |
| Wasted by the rate-limit kill | orchestrator sub-agent: 139,895 tokens / 20 tool uses / ~595 s through phase 1 and finder dispatch, then further uncaptured work until the 429; Requirements finder attempt 1: ~22 tool uses of investigation, no report, tokens not captured. Neither figure is in the totals above |
| Candidates raised | 8 — Requirements 5, Code 3 |
| Verdicts | 7 confirmed · 1 plausible · 0 refuted · 3 merged (each Code candidate into its Requirements twin) |
| Findings for publication | **4** — P2 `consider` ×3, P3 `consider` ×1 |
| Questions | 1 (the `plausible` candidate, on AC4) |
| Coverage | complete (9/9 files, both finders) |
| Requirements counts | met 8 · not met 4 · unverifiable 0 |
| Axis outcomes | Requirements: `Waiting for information` (open question on AC4; 4 findings) · Code: `Findings` (3 candidates, all merged into Requirements) |
| Derived status | **Needs Information** (no `must-fix`; one open question whose answer could change the verdict). `COMMENT` natively |

## Findings

All four are the Requirements-axis survivors after the verifier merged each Code candidate into its
Requirements twin (Requirements frame kept per `verify.md`'s dedup rule). Priority kept at the higher
of each pair.

### F1 — `requirements/validator-volatile-detection-commerce-list` — consider / P2

- **anchor** `skills/shortlist/references/research-protocol.md:406`
- **fix** `skills/shortlist/scripts/validate-completion.py:2949`

The diff's Freshness rule says the applicable Volatile classes "follow the category and the ledger
rather than a fixed commerce list", but the validator's offset-bearing-timestamp rule still selects
"volatile evidence" with the base regex
`\b(?:price|stock|delivery|restock|availability|available|unavailable)\b`. A generalized bundle's
catalog, cost, license, or release-support claim with a bare `YYYY-MM-DD` passes `--require-complete`
while the identical omission on a price claim is rejected.

Verifier: **confirmed**. Regex unchanged from base; `bundle_date_errors` is called unconditionally
with no generalized branch (`validate-completion.py:3726`); the community-technology fixture's E003
passes with `Observed: 2026-08-28` while the bundle is completion-ready. Nuance recorded for the
comment: the protocol line says "Timestamp every Volatile-claim observation" and a bare date is a
timestamp, so this is an enforcement inconsistency between commerce and generalized classes rather
than a literal breach of the new text. P2 / `consider` kept.

**This is the third drift DESIGN.md §C9 tracked** (found by the fix author's own validation runs,
never by any prior prototype run on this target). This run is the first prototype run to raise it.
Only the Requirements axis did; see the Code-axis ledger note below.

### F2 — `requirements/search-bundle-format-stale-kind-list` — consider / P2

- **anchor** `skills/shortlist/references/record-schemas.md:392`
- **fix** `skills/shortlist/references/search-bundle-format.md:208`
- merged in: `code/search-bundle-format/stale-obligation-kind-list` (Code, P3)

The obligation `Kind` enumeration gained `Volatile-claim class` in four places; the bundle contract's
parallel sentence still lists five kinds. Verifier: **confirmed**, quoting the stale line; both
finders' lockstep-history claims (`1c25a91`, `55e1f25` touched all three files together) verified.
P2 / `consider` kept.

### F3 — `requirements/narrow-skill-fixed-refresh-list` — consider / P2

- **anchor** `skills/shortlist/references/narrowing-protocol.md:68`
- **fix** `skills/shortlist-narrow/SKILL.md:46`
- merged in: `code/shortlist-narrow-skill/closed-volatile-lists` (Code, P3)

`narrowing-protocol.md:68` replaced its two closed per-bundle refresh lists with an open,
ledger-driven rule; the Narrow stage skill's own instruction still carries the closed pair with no
ledger reference. Verifier: **confirmed**; trigger verified against the streaming fixture's
Research-origin "Ad-tier feature and price-lock volatility" record, which falls outside the skill's
list. P2 / `consider` kept, with the note that the skill links and says to follow the protocol, so
this is paraphrase drift rather than a broken execution path. The verifier suggests carrying the Code
candidate's rewrite wording into the published comment.

**This is the item the pre-C9 run missed entirely** (see `v2a-run-pre-c9.md`). Both axes raised it
this run.

### F4 — `requirements/research-skill-omits-refine-and-inapplicable` — consider / P3

- **anchor** `skills/shortlist/references/research-protocol.md:295`
- **fix** `skills/shortlist-research/SKILL.md:39`
- merged in: `code/shortlist-research-skill/add-only-ledger-rule` (Code, P3)

The protocol now lets field evidence "add, refine, or mark inapplicable a seeded obligation ...
always with a recorded reason"; the Research stage skill still restates the add-only rule.
Verifier: **confirmed**, quoting the byte-identical-to-base line. P3 / `consider` kept. Both finders
flagged this as the weakest of their sync-drift candidates; the verifier confirmed it anyway rather
than downgrading to an observation, since the stale line is real and has one fix site.

## Open question

### Q1 — from `requirements/volatile-evidence-freshness-expectation` (proposed P1 must-fix)

AC4 reads "Evidence can mark any decision-relevant claim as Volatile with an observation date and
category-appropriate freshness expectation." The Evidence record at head has no Volatile marker and
no freshness-expectation field; the diff adds none, and the word "expectation" does not occur in it.
The finder proposed this as P1 `must-fix`.

Verifier: **plausible**, not confirmed. The factual core holds, but whether AC4 demands a structured
carrier or is satisfied by the prose the new `Volatile-claim class` obligations record in
`Why it applies` is a spec-interpretation question the code cannot settle. Two corrections: "nowhere
to say how old is too old" is too strong (free-text fields exist; what is missing is a *defined*
carrier), and the freshness checker's uniform 7-day horizon belongs to the issue AC9 excludes, so it
cannot license a merge consequence here. Publishes as a question; action `must-fix` → `question`;
priority moot. What would settle it: the issue author confirming whether AC4 intends an explicit
per-class expectation.

This is the question that holds the derived status at `Needs Information`. It is new to this
program: the pre-C9 run acquitted the same hypothesis as "pre-existing, unaffected" at the finder,
and none of the original v2–v5 runs raised it.

## Changed-contract list (Requirements finder, returned per the C9 rule)

Reproduced from the finder's report. Seven contracts, each with its paired new-term and
old-fragment sweep and every live peer dispositioned:

| # | Contract | New-term search | Old-fragment search | Live peers and disposition |
| --- | --- | --- | --- | --- |
| 1 | Obligation `Kind` enum: five kinds + `Other` → adds `Volatile-claim class` | `volatile-claim class` (ci) | `discovery branch, safeguard` / `"Safeguard"` (ci) | Updated: `CONTEXT.md:327`, `record-schemas.md:392`, `research-protocol.md:295`, `record_schemas.py:397`. **Stale: `search-bundle-format.md:208`**. Historical/acquitted: `docs/adr/0017:7`, `PROJECT_BRIEF.md:85` |
| 2 | Obligation lifecycle: "field evidence may add" → "add, refine, or mark inapplicable, with a recorded reason" | `add, refine` / `mark inapplicable` (ci) | `field evidence may add` / `add obligations` (ci) | Updated: `CONTEXT.md:327`, `research-protocol.md:295`, `record-schemas.md:394`. **Partial peer: `shortlist-research/SKILL.md:39`**. Historical: `docs/adr/0017:7` |
| 3 | Freshness timestamp scope: closed "price, stock, delivery, and restock" → ledger-driven open rule | `materially stale` / `identif(y\|ied) as volatile` / `freshness credibility` (ci) | `price, stock, delivery` / `timestamp price` (ci) | Updated: `research-protocol.md:406`, `narrowing-protocol.md:68`. **Stale: `shortlist-narrow/SKILL.md:46`**. **Stale: `validate-completion.py:2948-2951`**. Already generalized / different mechanism: `research-protocol.md:67`, `category-bundle-format.md:96`, `freshness-checker.md:6-8`, `check_freshness.py:37+`, `docs/adr/0007:13`, `docs/design/intake-criteria-and-ranked-narrowing.md:60`, `research/model-comparison-2026-08-27.md:115` |
| 4 | Narrow "Volatile evidence" rule: commerce/generalized closed lists → open rule | as 3 | `mandatory accessory cost` / `announced restock` (ci) | Only `narrowing-protocol.md:68` carried it (updated); related stale peer is row 3's `shortlist-narrow/SKILL.md:46` |
| 5 | Source-authority rule: manufacturer/retailer roles → Candidate relationship + governing material | `within its authority` / `governing (and\|or) regulatory` (ci) | `manufacturer pages` / `declared evidence` (ci) | New: `research-protocol.md:47`; commerce roles retained at `:41-45`. Consistent: `intake-criteria-and-ranked-narrowing.md:60`, `record-schemas.md:332`. No stale peer |
| 6 | `JUDGMENT_ONLY_ATTESTATIONS` gains "Freshness credibility" | `freshness credibility` (ci) | `saturation credibility` (ci) | Only `validate-completion.py:79-91`; tests assert the header only. No stale peer |
| 7 | New glossary term `Category profile` | `category profile` (ci) | n/a (new) | All uses consistent; ADR 0017 / `PROJECT_BRIEF.md:85` narrower seed sets are historical |

Row 3 is the one that matters for the regression watch: the closed-list → open-rule change (the
shape C9 added to the contract definition explicitly) was written down as a contract, swept on the
old fragment `price, stock, delivery`, and surfaced both `shortlist-narrow/SKILL.md:46` and the
validator regex in one sweep.

The Code axis has no separate changed-contract list; its equivalent is the sync-drift block of its
ledger (rows 1–2 candidates plus the acquittals reproduced below).

## The three known items, per finder

| Item | Requirements finder | Code finder | Verifier |
| --- | --- | --- | --- |
| (a) `search-bundle-format.md:208` five-kind enumeration | candidate C3, P2 consider | candidate 1, P3 consider | confirmed; merged → F2 |
| (b) `shortlist-narrow/SKILL.md:46` closed refresh list | candidate C4, P2 consider | candidate 2, P3 consider | confirmed; merged → F3 |
| (c) `validate-completion.py:2949` retired-term regex | candidate C2, P2 consider | **not raised and not acquitted** — the nearest ledger rows are "Other scripts hard-code the obligation kinds separately from `OBLIGATION_KINDS`" (grepped `Safeguard`/`Discovery branch` in `scripts/`, acquitted) and "`freshness-checker.md` commerce-kind list conflicts with open rule" (acquitted, checker out of scope); neither touches the timestamp regex | confirmed → F1 |

Recall on the two originally-known drifts: **2 of 2, on both axes.** On the third: 1 of 2 axes.

## Disposition ledgers (both finders, complete)

### Requirements axis (5 candidates, 29 rows)

| Claim | Falsification route | Decisive evidence | Disposition |
| --- | --- | --- | --- |
| AC4's "category-appropriate freshness expectation" has no carrier in any record | find a schema field or fixture recording one | `record-schemas.md:604-612`; `check_freshness.py:33` uniform horizon | candidate |
| Validator's volatile-timestamp rule still commerce-only | check the regex was generalized | `validate-completion.py:2948-2951` unchanged | candidate |
| `search-bundle-format.md` ledger description omits Volatile-claim class | read the line | `search-bundle-format.md:208` | candidate |
| Narrow SKILL keeps closed refresh lists | read the line | `skills/shortlist-narrow/SKILL.md:46` | candidate |
| Research SKILL omits refine / mark-inapplicable | read the line | `skills/shortlist-research/SKILL.md:39` | candidate |
| AC1 profile may seed all six kinds, not a closed checklist | find text making it closed | `research-protocol.md:289` "not a closed checklist" | acquitted (met at protocol; peer in C3) |
| AC2 profile from Candidate field/Use conditions; catalog not routing | find routing/registry language | `research-protocol.md:289-291` | acquitted (met) |
| AC3 refine/mark-inapplicable with reason, ledger rules apply | find missing rule | `record-schemas.md:394`; `research-protocol.md:295` | acquitted (met at protocol; peer in C5) |
| AC5 Volatile class list is open | find closed wording | `record-schemas.md:392` "such as"; `narrowing-protocol.md:68` "another decision-relevant class" | acquitted (met) |
| AC6 refresh materially stale, preserve history, not commerce-only | find a commerce-only assumption | `narrowing-protocol.md:68-70` | acquitted (met at protocol; peer in C4) |
| AC7 governing material controls within authority; three evidence roles distinct | find contradiction | `research-protocol.md:47` | acquitted (met) |
| AC8 community-technology fixture exists | inspect fixture category | `tests/fixtures/generalized-bundle/current/intake.md:11`; `coverage.md:68-69` | acquitted (met) |
| AC8 streaming-like catalog claim + Research-added class | inspect fixture | `generalized-bundle-streaming/ledger.md:56-79` Records 6-7; `test_generalized_bundle.py:520-541` | acquitted (met) |
| AC8 physical-product profile fixture | inspect fixture | `generalized-bundle-physical/ledger.md:82-90` Record 9 | acquitted (met) |
| AC9 freshness checker untouched | diff manifest | `check_freshness.py`/`freshness-checker.md` absent from `--name-status` | acquitted (met) |
| AC10 suites pass | run suites | 290 Python OK; 60 Node pass | acquitted (met) |
| ADR 0017 / PROJECT_BRIEF list narrower seed sets | is ADR a live rule? | `docs/adr/0017:7`; `PROJECT_BRIEF.md:85`; decision records, not protocols | observation |
| `research-protocol.md:67` cached-claims list closed? | read wording | ":67 or similarly volatile claims" | acquitted |
| `category-bundle-format.md:96` `volatile` row closed? | read wording / mechanism | ":96 and similar observations", category-bundle reuse | acquitted (different mechanism) |
| `docs/adr/0007:7` fixed list stale | read ADR | `:13` already broadens to Volatile claims | acquitted |
| `docs/design/intake-criteria…:60` stale | read | already generalized | acquitted |
| `skills/shortlist/SKILL.md:27` "volatile facts" closed | read | generic wording | acquitted |
| Attestation-list tests break on new tuple entry | read tests | `test_validate_completion.py:289,986` header-only assertions | acquitted |
| "Freshness credibility" attestation is scope creep | is it needed by a requirement? | implements AC6 via existing judgment-only pattern | acquitted |
| `Category profile` glossary term is scope creep | is it needed? | `docs/agents/domain.md` glossary rule; term used by new protocol section | acquitted |
| Evidence-source paragraph is scope creep | maps to AC7 | `research-protocol.md:47` | acquitted |
| Streaming fixture is a bare ledger, not an evidence-level catalog claim | inspect | `generalized-bundle-streaming/ledger.md` only | observation |
| New attestation undocumented in any protocol | grep "Saturation credibility" | only `validate-completion.py:88-91` | observation |
| Kind/Origin enums enforced on completion path | read validator | `validate-completion.py:303-312` | acquitted |

Requirements finder's counts: **met 8 (R0a, R0b, R2, R5, R7, R8, R9, R10) · not met 4 (R4 partial
via C1/C2; R1, R3, R6 each satisfied at the canonical protocol but carrying a live stale peer, per
the C9 no-`Met`-while-a-peer-is-stale rule) · unverifiable 0.**

### Code axis (3 candidates, 22 rows)

| Claim | Falsification route | Decisive evidence | Disposition |
| --- | --- | --- | --- |
| `search-bundle-format.md` kind list stale after enum grew | compare base peers + commit history | `search-bundle-format.md:208`; `git show --stat 1c25a91` | candidate |
| `shortlist-narrow/SKILL.md` keeps closed volatile lists the protocol opened | compare base protocol wording + `git log -S` | `shortlist-narrow/SKILL.md:46`; `1450bc2` | candidate |
| `shortlist-research/SKILL.md` restates add-only ledger rule | compare protocol + `git log -S` | `shortlist-research/SKILL.md:39`; `1450bc2` | candidate (weakest) |
| Other scripts hard-code the obligation kinds separately from `OBLIGATION_KINDS` | grep `Safeguard`/`Discovery branch` in `scripts/` | only `record_schemas.py:397`; `validate-completion.py:298` imports the enum | acquitted |
| Generalized bundle template lists kinds and is stale | grep template | `assets/search-bundle-generalized/current/coverage.md:3` has heading only | acquitted |
| ADR 0017 / `PROJECT_BRIEF.md:85` kind lists are stale peers | compare to base list | both already lacked `safeguard` at base — not lockstep | acquitted |
| `docs/adr/0007` restates old freshness list | read ADR | `0007:13` already says list was broadened — historical | acquitted |
| `freshness-checker.md` commerce-kind list conflicts with open rule | read lines 3-7 | `freshness-checker.md:6-7` already adds category-applicable vocabulary; checker out of scope | acquitted |
| `intake-criteria-and-ranked-narrowing.md:60` conflicts with new freshness rule | read line | states the same open rule | acquitted |
| ADR conflict from extending profiles to Volatile classes | read ADR 0017 | ADR 0017:7 is extended, not contradicted | acquitted |
| `test_completion_attestations_cover_freshness_credibility` passes vacuously | run suite; check stage gate | `validate-completion.py:3089` would error if stage unchanged; 290/290 | acquitted |
| Streaming fixture record 8 `Evidence or research task: none` fails terminal check | read `research_obligation_terminal_errors` | `validate-completion.py:335-338` `continue`s on `not applicable`; test passes | acquitted |
| New freshness test duplicates existing attestation tests | read `test_validate_completion.py:289,986` | new test adds the `Freshness credibility:` assertion; not a defect | acquitted |
| `shortlist/SKILL.md:27` volatile-facts mention stale | read line | generic wording, no list | acquitted |
| (8 further acquittals on attestation wording, fixture citation IDs, duplicate obligation names, `Kind == "Source family"` special-casing, and the attestation "before handoff" ambiguity — see the finder report; the last two became observations) | | | acquitted / observation |

Code finder's observations: the "Freshness credibility" attestation says "refreshed before handoff"
but is printed only under `Current stage Research` (`validate-completion.py:90`, `:3089`), and the
repo uses "handoff" for both the Research→Narrow and the final Narrow handoff; and the streaming
fixture's record at `ledger.md:77` fills `Why it applies` with why the obligation does *not* apply,
which the validator accepts as non-empty.

### Verifier's additions

No new candidates. Five observations (a real publish keeps three): `CONTEXT.md:295` already promises
a "freshness expectation" no schema field carries; `category-bundle-format.md:88`'s freshness
horizons are a cache-reuse table, not a per-claim expectation; `freshness-checker.md:5`'s
"no additional schema marker is required" is the design choice Q1 is in tension with; the new
attestation test duplicates another test's setup and asserts only a substring; the Node suite was not
run by the verifier (it was run by both finders: 60 pass).

## How this run was executed (deviation from the pre-C9 run's shape)

- **Attempt 1 (orchestrated).** The session dispatched one orchestrator sub-agent with the same
  dispatch shape as the pre-C9 run (pinned skill commit updated to `87c68a9`; an added clone-hygiene
  clause). It completed phase 1 (tests 290/60 pass, tree untouched), built the shared finder prompt,
  and spawned both finders. The Code finder completed and its report was captured. The Requirements
  finder ran ~22 investigation tool calls (both legs of the sweeps, the relevant files, the validator
  around line 2948) and was then killed, along with the orchestrator, by the harness's session rate
  limit (HTTP 429, "session limit resets 10am America/New_York"). No verifier ran.
- **Attempt 2 (session-driven).** After the limit reset, the session extracted the orchestrator's
  exact Requirements-finder prompt from the killed finder's transcript (verified to contain no
  pointer to any known item) and re-dispatched it verbatim as a fresh sub-agent. It then built the
  verifier prompt programmatically from both finder reports — stripping every `support` line (checked
  mechanically: zero `support` fields in the dispatched prompt file) and passing the eight claims
  verbatim — and dispatched the verifier as a fresh sub-agent. Dedup, axis outcomes, and the status
  derivation were done by the session per `verify.md` / `publishing.md`.
- **What this changes.** Orchestrator-role work (verifier dispatch, compile) was done by the session
  rather than a sub-agent, so there is no single orchestrator token figure; the finders did not run
  in parallel; and the Code finder's inputs came from attempt 1's orchestrator while the Requirements
  finder's came from the session — but the prompt text was byte-identical (extracted, not
  re-authored). Neither finder nor the verifier saw any state from the killed attempt or from this
  research program's docs. Clone remained clean at `4349ff41` throughout, checked before and after
  each dispatch.
- **Guidance membership** is the same explicit call as the pre-C9 run (`AGENTS.md`,
  `docs/agents/domain.md`, base `CONTEXT.md`; `issue-tracker.md` excluded), inherited verbatim
  through the extracted prompt.

## Mechanism checklist

- **C1 (Calibration) — recall preserved, calibration correct on the drifts, status held by a
  question.** Both known doc-sync drifts were found, on both axes, and landed P2 `consider`
  (non-blocking, verifier-confirmed). The third drift (validator regex) was found on the
  Requirements axis and confirmed P2 `consider`. None of the four findings gates. The derived
  status is `Needs Information` rather than `Approved (advisory)` because of Q1, a `plausible`
  requirements candidate on AC4 that publishes as a question — which is the ladder working as
  written (a question never ages into approval), not a drift being over-rated. Whether Q1 is a good
  question is a separate call: the finder proposed it as P1 `must-fix`; the verifier declined to
  confirm it and named the spec ambiguity that would settle it.
- **C3 (Disposition ledger) — confirmed.** 29-row Requirements ledger and 22-row Code ledger, both
  with tried-to-convict acquittals, plus the seven-row changed-contract table.
- **C5 (Observations) — confirmed.** 5 Requirements + 2 Code + 5 verifier observation-shaped items
  stayed out of the verdict list; a real publish would keep 3.
- **C9 (Changed-contract sweep) — demonstrated.** The Requirements finder returned the
  changed-contract list first, with paired searches per row; row 3 (closed list → open rule) is the
  contract shape C9 added explicitly, and its old-fragment sweep is what surfaced both
  `shortlist-narrow/SKILL.md:46` and the validator regex. The Code axis's new sync-drift section
  produced candidates for both originally-known drifts but not the validator regex, matching
  DESIGN.md §C9's own note that the Code axis is the weaker of the two on this.
- **Pole intact — confirmed, with the execution deviation above.** Both finders ran to completion
  (Requirements on its second attempt); all 8 candidates received exactly one verifier verdict;
  `support` was withheld from the verifier, checked mechanically on the dispatched prompt file.
- **C2 (no-issue rule) and C4 (question-routing) — not applicable, as expected.** Issue #45 exists;
  no candidate landed in the "cannot tell from the code" bucket. Q1 reached the verifier as a defect
  claim and became a question by verdict, which is the `plausible` path, not C4's finder-side
  routing.
