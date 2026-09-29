# v3 run — `snapshot-path-omitted` against `kamui/shortlist#66`

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `snapshot-path-omitted` (PR #13, branch `snapshot-path-omitted`) |
| Architecture | 1 integrated tool-using reviewer, self-falsification, no fan-out |
| Agents spawned | 1 |
| **Total sub-agent tokens** | **110,630** |
| Tool uses | 49 |
| Wall clock (sub-agent) | ~663 s (serial) |
| Candidates raised | 10 (1 admitted, 9 dropped) |
| Findings for publication | **1** — blocking, P2 |
| Questions | 0 |
| Coverage | complete for the manifest and risk checks; **one fetch gap disclosed** (PR body unreachable — clone `origin` is a local path) |
| Derived status | **Changes Requested (advisory)** |

Conditional verifier **not** invoked — the reviewer judged the change (9 files, +160/−6) not unusually large, coupled, or high-risk, which is the frequent path the skill specifies.

## Requirement ledger — issue #45, 10 criteria

| # | Verdict | Evidence cited |
| --- | --- | --- |
| 1 | met | `research-protocol.md:289` ("no obligation is required merely because a profile named it…"); `CONTEXT.md:330`; `record_schemas.py:397` |
| 2 | met | `research-protocol.md:289` derives from "the Candidate field's category, comparison level, and boundary, plus the Use conditions"; `:291` restates the non-goal; no router or registry added |
| 3 | met | `research-protocol.md:295`; `record-schemas.md:394`; validator gating untouched; streaming Record 8 is a seeded obligation marked `Not applicable` with a reason and clears terminal validation |
| 4 | **met (largely on base)** | `Observed` required per `record-schemas.md:611`; `check_freshness.py` detects generalized volatile kinds with "no additional schema marker required" (`freshness-checker.md:3-11`, base, from #44); this PR supplies per-category expectation via the `Volatile-claim class` obligation text |
| 5 | **met in protocol/schema, not on the executable Narrow path** | `record-schemas.md:392` lists all eight; `shortlist-narrow/SKILL.md:46` still closed → finding |
| 6 | **partially met** | `narrowing-protocol.md:68`/`:70` satisfy it; the operative Narrow skill contradicts it → finding |
| 7 | met | `research-protocol.md:47`, consistent with `CONTEXT.md`'s Declared/Measured/Observed definitions |
| 8 | met | physical Record 9; community-technology = pre-existing `generalized-bundle`; streaming Record 6 (catalog); streaming Record 7 (`Origin: Research`) |
| 9 | met (preserved) | `check_freshness.py`, `freshness_price_rules.json`, `freshness-checker.md`, `test_freshness_checker.py` all untouched; new rule explicitly judgment-only |
| 10 | met | `node --test` 60/60; `python3 -m unittest discover -s tests` 290 OK |

## Risk checks

- **Migrations / compatibility** — additive only; widening `OBLIGATION_KINDS` cannot invalidate an existing record; `search-bundle-format.md:78` anticipates later tickets deepening generalized behavior.
- **External contracts / version skew** — validator stdout gained one line; grepped every consumer, only `assertIn` in tests; `Kind` accept-set has exactly one definition and one consumer.
- **Secrets / sensitive data** — new fixture read in full; no URLs, credentials, or personal data.
- **Path handling** — `STREAMING_LEDGER` is a `ROOT`-relative read-only constant.
- **Authorization, retries/concurrency** — not applicable with basis; no auth, network, or stateful code in the diff.

## The one finding

```yaml
id: narrowing/volatile-refresh-closed-skill-list
path: skills/shortlist/references/narrowing-protocol.md
start_line: 68
end_line: 68
side: RIGHT
priority: P2
blocking: true
kind: requirement
title: Open the Narrow skill's volatile-refresh list alongside this protocol
trigger: >
  A generalized narrow run whose ledger holds a Volatile-claim class outside the
  skill's two fixed branches — this PR's own streaming fixture Record 7
  ("Ad-tier feature and price-lock volatility", Origin: Research), or a
  policy-terms class named in acceptance criterion 5.
impact: >
  skills/shortlist-narrow/SKILL.md:46 is the operative Narrow instruction and
  still directs a closed enumeration. It has no "another class" escape and omits
  policy terms entirely, so it contradicts this line's "not only a fixed commerce
  list". The pre-handoff refresh required by criterion 6 is not delivered on the
  path an agent actually executes.
evidence:
  - narrowing-protocol.md:68 replaces the fixed list with an open rule
  - shortlist-narrow/SKILL.md:46 retains the closed two-branch list (unchanged by this PR)
  - commit 1450bc2 introduced both sentences together, establishing lockstep maintenance
  - generalized-bundle-streaming/ledger.md Record 7 is a Research-added class the list does not cover
  - no test or eval covers the Narrow skill's refresh wording
requirement_source: issue-45/acceptance-criteria-5-and-6
requested_behavior: >
  Update the Narrow skill's refresh sentence to defer to the ledger's applicable
  Volatile-claim classes, keeping the commerce and generalized examples
  illustrative rather than exhaustive.
verification: passed
```

Note `priority: P2` with `blocking: true` — v3 treats priority and blocking as independent axes. Anchor verified against `git diff -U0` (`@@ -68 +68 @@`). The fix site is outside the diff and named in prose rather than used as the anchor.

Distinctive evidence this reviewer produced and the others did not: **commit `1450bc2` introduced both sentences together**, establishing that the protocol line and the skill line are maintained in lockstep — a history-based argument that the omission is drift rather than design.

## The nine dropped candidates

Recorded verbatim in substance, since this is the run's filtering data.

1. **`validate-completion.py:2948` volatile regex still commerce-only.** Dropped on gates 2, 4, 6: the regex predates the PR; every Evidence record already carries a required `Observed` date so "timestamp every Volatile-claim observation" is satisfied and there is no proven path to a wrong outcome, only lower sub-day precision a weeks-scale catalog claim does not need; and the same diff makes freshness credibility explicitly judgment-only, establishing non-mechanical treatment as deliberate. Criterion 9 also fences off freshness-checker work.
2. **`search-bundle-format.md:208` omits `Volatile-claim class`** while the PR updated the three peer docs, and commit `1c25a91` updated this exact sentence when it added `Safeguard`. Dropped on gates 1/4: the list is now open-ended ("or other category-relevant work") so it is incomplete rather than wrong; the sentence links inline to `record-schemas.md#research-obligation`; the instruction that actually drives seeding was updated. No observable wrong outcome.
3. **`shortlist-research/SKILL.md:39`** says "add obligations the field evidence reveals" without "refine, or mark inapplicable". Dropped on gates 1/7: an abstract deferral to the protocol, not a closed enumeration — "the exact distinction that makes candidate 3 fail where finding 1 passes."
4. **`PROJECT_BRIEF.md:85` and ADR 0017 seed lists** omit safeguards and Volatile-claim classes. Dropped on gates 2/8: both already diverged at base when `Safeguard` landed; an ADR is a historical record.
5. **New attestation test downgrades a complete fixture before asserting `--require-complete` returns 0.** Dropped after direct execution: the unmodified fixture fails with `--require-complete requires Current stage Research`, so the mutation is required setup.
6. **"Refine" has no fixture or test** while add and mark-inapplicable do. Dropped on gates 1/5: criterion 8 enumerates required fixtures and does not include one; a refinement leaves no distinguishable record shape since Kind and Origin are preserved by design.
7. **Streaming Record 8 records a commerce `Not applicable` entry.** Dropped: one entry is not "repeated", and base fixture Record 6 sets the precedent.
8. **Refinement may "sharpen its `Obligation` name", the identity key for duplicate detection.** Dropped on gate 4: speculative, no concrete trigger, and the validator would surface a resulting mismatch.
9. **Line length in the new test helper.** Dropped on gate 7: no lint config exists and CI runs only `npm test`.

## Overlap with the v2 run

Recorded as raw comparison data, without interpretation:

| Item | v2 | v3 |
| --- | --- | --- |
| Narrow skill closed refresh list | **confirmed**, P1, must-fix | **admitted**, P2, blocking — the one finding |
| `search-bundle-format.md:208` five-kind enumeration | **confirmed**, P1, must-fix | **dropped** (gates 1/4 — open-ended list, links to the enum, no observable wrong outcome) |
| `validate-completion.py` commerce-only volatile regex | **confirmed**, P2, consider | **dropped** (gates 2/4/6 — pre-existing regex, judgment-only treatment deliberate) |
| Freshness expectation has no recording site | **confirmed**, P2, consider | **not raised** (ledger criterion 4 marked met on the `Volatile-claim class` obligation text) |
| `research-protocol.md` stock/delivery commerce branch | **refuted** by verifier | **not raised** |
| Attestation test asserts complete on incomplete bundle | **refuted** by verifier (factually wrong) | **dropped** #5 (same reasoning, reached independently) |
| Streaming Record 8 `Not applicable` seed | acquitted by finder, never a candidate | **dropped** #7 (same reasoning) |
| `PROJECT_BRIEF.md` / ADR stale lists | not raised | **dropped** #4 |

## Notes on the run

- The reviewer **disclosed a fetch gap** rather than silently proceeding: the PR body was unreachable, so it substituted the commit message for the deliberateness test and noted that a strict rubric reading makes this one failed fetch, while stating it does not change the derived status.
- Base-branch reading did acquittal work again — dropped candidates 2, 4, and 5 each turned on base state or prior-commit history rather than the diff alone.
- Zero questions raised.
