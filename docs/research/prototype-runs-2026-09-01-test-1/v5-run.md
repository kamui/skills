# v5 run — `code-review-publish-5` against `kamui/shortlist#66`

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-publish-5` ([PR #17](https://github.com/kamui/skills/pull/17), branch `t3code/prototype-code-review-publish-5`, workflow `v5-2`) |
| Architecture | 1 integrated reviewer + consequence-triggered batched fresh-context verifier |
| Agents spawned | 2 (verifier invoked) |
| Total sub-agent tokens | **174,563** — 128,013 reviewer; 46,550 verifier |
| Tool uses | **64** — 48 reviewer; 16 verifier |
| Wall clock (sub-agents) | ~986 s reviewer end-to-end, of which ~167 s was the verifier |
| Candidates raised | 6 |
| Candidates surviving primary falsification | 2 |
| Verifier verdicts | **2 confirmed** · 0 plausible · 0 refuted |
| Findings for publication | **2** — P3 `consider`, P3 `consider` |
| Questions | 0 |
| Coverage | **complete** |
| Derived status | **Approved (advisory)** |

## Exact would-be published review

Event: `COMMENT` (self-review; gating not authorized). One forge-native batch: the summary body plus
two inline line comments. Both findings have honest single-line anchors on changed lines, so no
`Unanchored findings` section was needed.

### Summary body

```markdown
**Approved (advisory)** — no blocking findings; 2 optional consistency findings.

**Intent:** Make the category profile a documented mechanism that seeds the applicability ledger with a new `Volatile-claim class` obligation kind, and generalize freshness from a fixed commerce list to any decision-relevant Volatile claim.

**Issue fit:** Complete — all ten acceptance criteria are met, including the deliberate exclusion of `check_freshness.py` and the four required fixture shapes.

**Coverage:** Complete merge-base diff reviewed; the ledger-vocabulary peer documents, the Narrow and Research stage skills, ADR 0017, and the base-branch guidance files were inspected. `python3 -m unittest discover -s tests` (290 passed) and `node --test "tests/*.ts"` (60 passed) were run at the reviewed head.

**Reviewed:** `4349ff41ff4d134e09017662dd30420b80e8eb30` against merge-base `ccd1842d742fd940b2afde4f903c7bdcb3a707eb`.

## Findings

- [P3] [consider] Add `Volatile-claim class` to the bundle contract's ledger list — anchor `skills/shortlist/references/research-protocol.md:295`; fix `skills/shortlist/references/search-bundle-format.md:208`
- [P3] [consider] Mirror the generalized refresh rule into the Narrow skill — anchor `skills/shortlist/references/narrowing-protocol.md:68`; fix `skills/shortlist-narrow/SKILL.md:46`

<!-- review-run head=4349ff41ff4d134e09017662dd30420b80e8eb30 base-ref=main base-sha=ccd1842d742fd940b2afde4f903c7bdcb3a707eb merge-base=ccd1842d742fd940b2afde4f903c7bdcb3a707eb workflow=v5-2 context=acd97af42ea631a55b5ebdceb73ccf76f319c55a2a7ab41fc3af71a7c25eebf3 issues=kamui/shortlist#45 coverage=complete -->
```

### Finding 1 — anchor `skills/shortlist/references/research-protocol.md:295`, side `RIGHT`

```markdown
**[P3] [consider] Add `Volatile-claim class` to the bundle contract's ledger list**

**Triggers when:** An agent reads `search-bundle-format.md` as the bundle contract before building or editing a generalized bundle's applicability ledger.

**Impact:** That file's ledger enumeration still stops at "safeguard, or other category-relevant work", so the four documents that carried one obligation vocabulary no longer agree — commits `1c25a91` and `55e1f25` each extended all four together. `OBLIGATION_KINDS` still accepts the new kind, so this is contract drift rather than a rejected record.

**Change:** In `skills/shortlist/references/search-bundle-format.md` line 208, add `Volatile-claim class` to that enumeration so the bundle contract matches `record-schemas.md` and `research-protocol.md`.

Closing this without action is a correct response.

<!-- finding id=shortlist/bundle-format-obligation-kind-drift head=4349ff41ff4d134e09017662dd30420b80e8eb30 priority=P3 action=consider blocking=false kind=maintainability fix=skills/shortlist/references/search-bundle-format.md:208 -->
```

### Finding 2 — anchor `skills/shortlist/references/narrowing-protocol.md:68`, side `RIGHT`

```markdown
**[P3] [consider] Mirror the generalized refresh rule into the Narrow skill**

**Triggers when:** The Narrow stage refreshes a generalized bundle whose ledger records a Volatile-claim class outside a fixed list, such as the `policy terms` class now named in `record-schemas.md` line 392.

**Impact:** `skills/shortlist-narrow/SKILL.md` line 46 still names a closed per-bundle-type list — price, stock, delivery, restock; access, cost, catalog, licensing, compatibility, support — with no policy-terms entry, so the stage skill contradicts the rule this line now states. Commit `1450bc2` wrote both texts in one commit.

**Change:** In `skills/shortlist-narrow/SKILL.md` line 46, replace the fixed list with the protocol's rule: refresh every applicable Volatile claim the category and the ledger identify, including a class Research added, keeping the prior observation in history.

Closing this without action is a correct response.

<!-- finding id=shortlist-narrow/volatile-refresh-fixed-list head=4349ff41ff4d134e09017662dd30420b80e8eb30 priority=P3 action=consider blocking=false kind=maintainability fix=skills/shortlist-narrow/SKILL.md:46 -->
```

### Context digest

Computed with the skill's own `scripts/context_fingerprint.py`:
`acd97af42ea631a55b5ebdceb73ccf76f319c55a2a7ab41fc3af71a7c25eebf3`.

Inputs: `pr` — the pinned title plus the PR body verbatim; `issues` — one entry, `kamui/shortlist#45`,
title and body verbatim, `comments: []`; `specs` — empty; `guidance` — the three base-branch
instruction files applied as repository rules, at base blob SHAs (`AGENTS.md`
`95782227f7e1d4f5c6909f3d6a9f52e07f9806eb`, `docs/agents/domain.md`
`b56c178259ddeceb4b611cf0f38b4fd93edd9a32`, `docs/agents/issue-tracker.md`
`0f2055d3f6a40c7cd29a88f2b12b5559c402ca57`). PR and issue bodies were sliced programmatically out of
the controlled brief rather than retyped.

## Requirement ledger — issue #45, 10 criteria

All ten private, all `met`; nothing was surfaced to the author.

| # | Verdict | Decisive evidence |
| --- | --- | --- |
| 1 | met | `research-protocol.md:289` — "a seed, not a closed checklist"; `CONTEXT.md:330-332` |
| 2 | met | `research-protocol.md:289` (profile derived from Candidate field and Use conditions); `research-protocol.md:291` ("never becomes executable routing, a required one-profile-per-scenario registry") |
| 3 | met | `record-schemas.md:394`; `research-protocol.md:295`; `CONTEXT.md:327`; completion still gated by `validate-completion.py:320-362` |
| 4 | met | `CONTEXT.md:294-296`; `research-protocol.md:406`; `record_schemas.py:336-343` makes `Observed` required on every Evidence record; `freshness-checker.md:3-5` |
| 5 | met | `record-schemas.md:392` names the exact class set; `research-protocol.md:406`; `narrowing-protocol.md:68` |
| 6 | met | `narrowing-protocol.md:68` ("not only a fixed commerce list"); `narrowing-protocol.md:70` (history preserved) |
| 7 | met | `research-protocol.md:47` — governing and regulatory material controls within its authority; declared/measured/observed roles kept distinct |
| 8 | met | `generalized-bundle-physical/ledger.md:83-91`; `generalized-bundle/current/coverage.md:57-63`; `generalized-bundle-streaming/ledger.md:53-62` and `:64-72` (`Origin: Research`) |
| 9 | met (non-goal preserved) | `check_freshness.py` and `freshness-checker.md` absent from the 9-file diff |
| 10 | met | 290 Python tests and 60 Node tests pass at the reviewed head |

## Risk checks

- **Authorization, sessions, tokens, public exposure** — no exposure. The only Python changes are a
  `frozenset` literal (`record_schemas.py:397`) and a static string tuple
  (`validate-completion.py:90-92`); no auth, request handling, or permission surface in the diff.
- **Secrets, cryptography, logging, sensitive data** — clean. The one new output is a fixed
  attestation string printed to stdout; no credentials, user data, or new logging of bundle content.
- **Paths, file serving, traversal, symlinks** — clean. The only new path is the repo-relative
  constant `STREAMING_LEDGER` (`tests/test_generalized_bundle.py:19`).
- **Migration, destructive operations, rollback, compatibility** — additive and backward-compatible.
  `validate-completion.py:303-307` errors only on a `Kind` *not* in the set, so widening
  `OBLIGATION_KINDS` cannot invalidate an existing ledger. `GENERALIZED_SCHEMA_VERSION`,
  `validate_bundle.py`, and `migrate_notebook.py` are untouched; confirmed empirically by the full
  suite passing on every commerce and generalized fixture.
- **Retries, idempotency, partial failure, stale state, concurrency** — untouched.
  `check_freshness.py`, which owns the transient-failure and one-retry policy, is not in the diff;
  the 60 Node tests covering failed-route retry semantics pass.
- **External contracts, serialization, dependencies, version skew** — **two drift instances found**,
  both published as `consider`. The ledger `Kind` vocabulary is a cross-artifact contract: three of
  its four lockstep documents were updated and `search-bundle-format.md:208` was missed; the
  Volatile-refresh rule was generalized in the protocol but not in `shortlist-narrow/SKILL.md:46`.
  No dependency changes; `package.json` untouched.

## Manifest coverage

All 9 changed files were `reviewed`; none were ignored or unreviewed.

- `CONTEXT.md` — new `Category profile` term and widened `Research obligation`; matches the file's
  existing term idiom and conceptual grouping.
- `skills/shortlist/references/narrowing-protocol.md` — Volatile-evidence generalization; every base
  list item preserved, history preservation added. Finding 2's anchor.
- `skills/shortlist/references/record-schemas.md` — `Kind` enum plus the refinement paragraph;
  agrees with `record_schemas.py:397`.
- `skills/shortlist/references/research-protocol.md` — evidence-authority paragraph, `Category
  profiles` section, widened ledger seeding, generalized Freshness. Finding 1's anchor.
- `skills/shortlist/scripts/record_schemas.py` — one-line additive enum widening, purely permissive.
- `skills/shortlist/scripts/validate-completion.py` — one attestation appended to
  `JUDGMENT_ONLY_ATTESTATIONS`; no duplicate attestation list exists elsewhere, so no drift.
- Physical ledger fixture — record 9 is required, not decorative:
  `test_physical_product_ledger_covers_applicable_work` asserts `OBLIGATION_KINDS <= kinds`.
- Streaming ledger fixture — 8 records; record 6 profile-seeded and record 7 Research-origin
  Volatile-claim classes; record 8's `Not applicable` shape matches the base fixture's idiom.
- `tests/test_generalized_bundle.py` — two new tests; the attestation test's state mutation is
  required by the validator's own gate, verified by executing it.

## Candidates and dispositions

Six candidates raised; two survived primary falsification.

### Survived

**1. `shortlist/bundle-format-obligation-kind-drift`** — P3 `consider`, published.

Could not be disproven. The peers were compared at the merge-base, where
`search-bundle-format.md:208` carried the identical enumeration. The last two commits to touch the
shared vocabulary (`1c25a91`, `55e1f25`) each edited all four documents together, and `55e1f25`'s
message names `search-bundle-format.md` explicitly. Nothing prevents it — the file is simply behind.
Not intentional: the PR body's changed-document list silently omits it. The partial mitigation (the
sentence links `record-schemas.md`, and the list ends in the open "or other category-relevant work")
caps it at P3 `consider` rather than killing it.

**2. `shortlist-narrow/volatile-refresh-fixed-list`** — P3 `consider`, published.

Could not be disproven. `1450bc2` wrote `shortlist-narrow/SKILL.md:46` and the protocol's
Volatile-evidence paragraph in one commit with the same split; this PR generalized only the protocol.
`grep -c policy skills/shortlist-narrow/SKILL.md` returns `0`, making the omission of the
`policy terms` class decisive. The prevention attempt succeeded only partially:
`shortlist-narrow/SKILL.md:37` says "Follow the narrowing protocol:", which keeps canonical behavior
intact — that is what demoted it from `must-fix` to `consider`.

### Dropped

**3. `narrowing-protocol.md:68` cites "the ledger" in a section shared with commerce bundles that
have no applicability ledger.** Failed gate 4 (proven consequence). The applicability ledger exists
only in generalized bundles, but the same sentence supplies the full commonly-includes list inline
and says "what the category **and** the ledger identified", so a commerce Narrow still has complete
guidance. Imprecision with no observable wrong outcome.

**4. `research-protocol.md:406` keeps a per-bundle-type Freshness split, contradicting the PR body's
"rather than a hardcoded per-bundle-type list".** Falsified by unchanged surrounding code. The
hypothesis was untimestamped Volatile claims in a commerce bundle; `record_schemas.py:336-343` makes
`Observed` a **required** field on every Evidence record in both bundle forms, so every claim already
carries a date regardless of the Freshness prose. The mechanism cannot fire. The PR body overstates
slightly; that is not a code defect.

**5. Streaming fixture record 8's `Why it applies` explains why the obligation does *not* apply.**
Failed gate 2 (introduced here). The base fixture
`tests/fixtures/generalized-bundle/current/coverage.md:57-63` uses the identical pattern — same
obligation name, same Kind/Origin, same negative `Why it applies`. The new record faithfully copies
the repository's established idiom.

**6. ADR 0017 and `PROJECT_BRIEF.md:85` were not updated for the widened vocabulary.** Failed gate 2
and the propagation test. Both already lacked `safeguard` at the merge-base — `55e1f25` deliberately
left them alone while updating the other four documents. They are demonstrably *not* lockstep peers,
so this is pre-existing and intentional, not worsened here.

### Deduplication

The two survivors target different files, different shared rules, and different fix sites, so they
were not merged. The verifier independently returned no duplicate groups.

## Fresh-verifier discipline

The threshold fired on `shortlist-narrow/volatile-refresh-fixed-list`, proposed as `must-fix`.
`shortlist/bundle-format-obligation-kind-drift` was added to the same batch under the
`consider`-inclusion clause: its proof spans four documents and two commits, and independent
reconstruction could plausibly change its action.

Exactly one batched verifier ran in a fresh isolated context with no inherited conversation. It
received the repository name; the pinned head, base ref, base SHA, and merge-base; the exact diff
command; issue coordinate `kamui/shortlist#45` with its verbatim acceptance criteria; base-branch
rule coordinates; relevant verbatim PR-body excerpts; and for each candidate its `id`, `kind`,
`priority`, `action`, `blocking`, `anchor`, `fix`, `title`, `claim`, `trigger`, `impact`, `change`,
`requirement_source`, and raw code citations. The primary's `support`, confidence, reasoning,
conclusion, and falsification narrative were withheld; citations were passed bare. It generated no
new candidates and made no writes.

| id | Verdict | Corrections returned | Primary's disposition |
| --- | --- | --- | --- |
| `shortlist/bundle-format-obligation-kind-drift` | **confirmed** | Refine `impact`: the catch-all clause and `OBLIGATION_KINDS` keep the kind writable, so the harm is vocabulary drift, not a rejected record. No change to anchor, fix, change, priority, or action | Accepted, and folded into the published `Impact`. The verifier also supplied a fact the primary had missed — `1c25a91` extended the same peer set — which the primary independently re-verified (`git show 1c25a91 --stat`) before citing both commits |
| `shortlist-narrow/volatile-refresh-fixed-list` | **confirmed**, with downgrades | Trigger example wrong: the streaming fixture's ad-tier/price-lock and regional-catalog records fall inside the skill's existing terms; use `policy terms` from `record-schemas.md:392` instead. `kind` requirement→maintainability; `priority` P2→P3; `action` must-fix→consider; `blocking` true→false; drop `requirement_source` because AC 6 is satisfied at `narrowing-protocol.md:68` | Accepted after validating each correction against the diff. The primary confirmed `SKILL.md:37` and `SKILL.md:12` defer to the protocol, so canonical behavior is intact and the rubric's `consider` clause applies, and confirmed `grep -c policy` = 0 makes the corrected trigger decisive |

Both survivors are `verification: independent-confirmed`. The primary noted one contestable point in
the verifier's reasoning — `check_freshness.py:106-107` treats `catalog` and `plan-feature` as
distinct kinds, so calling ad-tier features "catalog" is arguable — but accepted the correction
anyway, because the example was not clean either way.

**The downgrade is why this review's status is `Approved (advisory)` rather than
`Changes Requested`.** The verifier materially changed the outcome without erasing the finding.

## Checks

- Head, base, merge-base, and the nine-file manifest matched the controlled brief exactly.
- `python3 -m unittest discover -s tests` — **290 passed**, 22.2 s.
- `node --test "tests/*.ts"` — **60 passed**, 0 failed, 1.08 s.
- `python3 skills/shortlist/scripts/validate-completion.py --require-complete tests/fixtures/generalized-bundle`
  — exit 1, `ERROR: --require-complete requires Current stage Research`, which explains and justifies
  the new test's state mutation.
- `git log -L '/^## Volatile evidence/,/^## Completion/'` on `narrowing-protocol.md` — `1450bc2`, `30fdbfb`.
- `git log -S "restock facts in a commerce bundle" -- shortlist-narrow/SKILL.md narrowing-protocol.md`
  — `1450bc2` alone, proving the lockstep pair.
- `git log -S "discovery branch, safeguard"` over the four vocabulary documents — `55e1f25`, `1c25a91`.
- `git show 55e1f25 --stat` — touches all four vocabulary documents; message names
  `search-bundle-format.md`. `git show 1c25a91 --stat` — same peer set.
- `grep -c policy skills/shortlist-narrow/SKILL.md` — `0`.
- `grep -rni "attestation" --include="*.md"` — no duplicated attestation list, so no drift from the
  `validate-completion.py` change.
- `context_fingerprint.py` — `acd97af4…`.
- Final `git status --porcelain` empty; head still `4349ff41…`.
- No live GitHub state was read, and nothing was published or modified.

One `grep` returned exit 1 on zero matches in `skills/shortlist-start/SKILL.md`; the empty result was
itself the answer and neighbouring greps in the same call succeeded, so it is a resolved operation,
not a coverage gap.

## Run conditions and observed ambiguity

The run used `/tmp/run-v5b` at the same pinned snapshot and the same phase-1 PR/issue inputs as
v2-v4. Publication was disabled and controlled prior-review state was `none`, even though v4 had
since been published live. The primary did not inspect earlier prototype outputs.

Because publication was withheld, `SKILL.md` §5's mandatory pre-write head re-fetch and §6's
post-publication read-back were structurally unreachable. Every other phase ran as written; the
reviewed head was confirmed stable locally instead.

Six concrete skill defects were reported:

1. **`consider` permission-sentence placement is underdetermined.** `output-contract.md` says to
   append the exact sentence after `Change`, but the template also places `Source` after `Change`.
   With both present the order is undefined. The run placed the sentence last.
2. **`guidance` membership for the `context` digest is undefined.** The contract says each entry has
   `path` and `blob_sha` but never says which files qualify — root instruction files, path-scoped
   files, `CONTEXT.md`, referenced ADRs, or design docs. This determines digest stability and
   therefore §2's duplicate-review comparison. Two reviewers can compute different digests from
   identical inputs.
3. **Trailer SHA width is unspecified.** Every example abbreviates, but §5's stale-head comparison
   and §2's continuity check both want unambiguous identity. The run used full 40-character SHAs.
4. **The line-anchor summary coordinate contradicts its own example.** The contract mandates
   `path:start-end`, but the worked example writes `src/payments.ts:42` for a single line.
5. **The `consider`-inclusion clause for the verifier batch is circular in one direction** — it asks
   the reviewer to predict the verifier's effect before running it. The reverse case that occurred
   here is uncovered: verification *downgraded* a `must-fix` below the mandatory threshold, and the
   text does not say whether such a candidate keeps `independent-confirmed`.
6. **No tie-break for which peer document to anchor when drift spans several changed files.**
   Finding 1 is provable from three changed lines; the rubric says "smallest honest changed range"
   without a rule for choosing among equally honest candidates.

## Overlap with v2, v3, and v4

Raw data, no interpretation.

| Item | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Narrow skill closed refresh list | confirmed, P1, **must-fix** | admitted, P2, **blocking** | confirmed, P2, **consider** | primary P2 must-fix → verifier-downgraded, **P3 consider** |
| `search-bundle-format.md:208` five-kind list | confirmed, P1, **must-fix** | dropped (gates 1/4) | confirmed, P3, **consider**, impact cut by verifier | confirmed, **P3 consider**, impact refined by verifier |
| `validate-completion.py` commerce-only regex | confirmed, P2, consider | dropped (gates 2/4/6) | not raised | not raised |
| Freshness expectation unrecorded | confirmed, P2, consider | not raised (AC4 met) | dropped (pre-existing at base) | not raised (AC4 met; `Observed` already required) |
| `research-protocol.md` commerce branch | refuted by verifier | not raised | not raised | **dropped** (per-bundle-type Freshness split cannot fire) |
| Attestation test | refuted by verifier | dropped #5 | dropped #1 | acquitted pre-candidate by executing the validator |
| `PROJECT_BRIEF.md` / ADR stale lists | not raised | dropped #4 | dropped #3 | **dropped** (not lockstep peers at base) |
| `shortlist-research/SKILL.md:39` | acquitted by finder, not raised | dropped #3 | dropped #2 | not raised |
| Schema bump for widened enum | not raised | not raised | dropped #6 | no compatibility break found |
| `narrowing-protocol.md:68` "the ledger" in a commerce-shared section | not raised | not raised | not raised | **dropped** (gate 4) |
| Streaming fixture record 8 negative `Why it applies` | not raised | not raised | not raised | **dropped** (base idiom) |
| **Derived status** | Changes Requested (advisory) | Changes Requested (advisory) | Approved (advisory) | **Approved (advisory)** |
