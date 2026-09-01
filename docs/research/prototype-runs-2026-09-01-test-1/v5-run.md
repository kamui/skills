# v5 run — `code-review-publish-5` against `kamui/shortlist#66`

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-publish-5` ([PR #17](https://github.com/kamui/skills/pull/17), branch `t3code/prototype-code-review-publish-5`, workflow `v5-2`) |
| Architecture | 1 integrated reviewer + consequence-triggered batched fresh-context verifier |
| Agents spawned | 2 (verifier invoked) |
| Total sub-agent tokens | unavailable from this harness run |
| Tool uses | **41** — 36 primary (33 shell-orchestration, 3 collaboration) + 5 verifier orchestration calls |
| Wall clock | unavailable; no end-to-end timer was started |
| Candidates raised | 4 |
| Candidates surviving primary falsification | 1 |
| Verifier verdicts | 0 confirmed · 0 plausible · **1 refuted** |
| Findings for publication | **0** |
| Questions | 0 |
| Coverage | **complete** |
| Derived status | **Approved (advisory)** — no findings |

## Exact would-be published review

Event: `COMMENT`. No finding or question comments.

```markdown
**Approved (advisory)** — no findings.

**Intent:** Seed open category profiles into the generalized Research ledger and make Volatile-claim freshness category- and ledger-driven.

**Issue fit:** Met — category profiles derive from the recorded Candidate field and Use conditions without turning the scenario catalog into routing; Research can add, refine, or mark seeded obligations inapplicable with reasons; `Volatile-claim class` is formalized for seeded and field-discovered work; freshness and source-authority guidance now cover generalized claims.

**Coverage:** Complete merge-base diff reviewed across all 9 changed files; applicable base guidance, ADRs, domain design, stage entrypoints, schema consumers, validator paths, fixtures, and the repository test suites were inspected. The physical, community-technology, and streaming coverage satisfies the requested cross-category cases. No qualifying findings or open questions survived falsification and required independent verification.

**Reviewed:** `4349ff4` against merge-base `ccd1842`.

<!-- review-run head=4349ff41ff4d134e09017662dd30420b80e8eb30 base-ref=main base-sha=ccd1842d742fd940b2afde4f903c7bdcb3a707eb merge-base=ccd1842d742fd940b2afde4f903c7bdcb3a707eb workflow=v5-2 context=acd97af42ea631a55b5ebdceb73ccf76f319c55a2a7ab41fc3af71a7c25eebf3 issues=kamui/shortlist#45 coverage=complete -->
```

## Requirement ledger — issue #45, 10 criteria

| # | Verdict | Decisive evidence |
| --- | --- | --- |
| 1 | met | `research-protocol.md:287-295`; `record-schemas.md:380-394`; `record_schemas.py:390-403` |
| 2 | met | `research-protocol.md:289-291`; `CONTEXT.md:330-332` |
| 3 | met | `research-protocol.md:295`; `record-schemas.md:394`; validator terminal checks |
| 4 | met | `research-protocol.md:404-413`; Evidence `Observed`; ledger-class semantics at `record-schemas.md:392` |
| 5 | met | `record-schemas.md:392`; `research-protocol.md:406`; `narrowing-protocol.md:68` |
| 6 | met | `narrowing-protocol.md:68-70`; the Narrow skill requires reading and following that protocol |
| 7 | met | `research-protocol.md:39-47` |
| 8 | met | physical and streaming ledgers; existing generalized community fixture; `test_generalized_bundle.py:503-542` |
| 9 | met (non-goal preserved) | no non-LLM freshness-checker file changed |
| 10 | met | 60 Node tests and 290 Python tests pass under available modern runtimes |

## Risk checks

- **Authorization, sessions, tokens, public exposure** — not applicable; no such behavior changed.
- **Secrets, cryptography, logging, sensitive data** — not applicable.
- **Paths, file serving, traversal, symlinks** — not applicable.
- **Migration, destructive operations, rollback** — no migration or destructive behavior; the enum change is additive.
- **Compatibility and serialization** — additive Kind enum, parser consumers, fixtures, and schema documentation inspected; no break found.
- **Retries, idempotency, partial failure, concurrency** — no runtime write/retry behavior changed.
- **Stale state and freshness** — Research, Narrow, validator attestations, entrypoints, and history-preservation path inspected.
- **Dependencies and version skew** — no dependency change. System Python 3.9 fails on pre-existing `zip(strict=...)`; a modern Python passes all tests.

## Manifest coverage

All 9 changed files were `reviewed`; none were ignored or unreviewed:

- `CONTEXT.md` — glossary alignment.
- `skills/shortlist/references/narrowing-protocol.md` — ledger-driven refresh and history preservation.
- `skills/shortlist/references/record-schemas.md` — Kind enum and refinement/inapplicability semantics.
- `skills/shortlist/references/research-protocol.md` — profiles, authority, ledger lifecycle, freshness.
- `skills/shortlist/scripts/record_schemas.py` — additive enum and consumers.
- `skills/shortlist/scripts/validate-completion.py` — judgment-only attestation behavior.
- Physical ledger fixture — parsed and validated.
- Streaming ledger fixture — profile-seeded, Research-added, and inapplicable cases.
- `tests/test_generalized_bundle.py` — new and surrounding contract tests.

## Candidates and dispositions

### 1. Narrow entrypoint's fixed refresh list

Stable id: `shortlist-narrow/ledger-defined-volatile-refresh`.

The primary admitted this as a P2 `must-fix`: the changed ledger-driven Narrowing protocol was not propagated to `skills/shortlist-narrow/SKILL.md:46`, whose older fixed examples name price/stock and access/delivery. This was the only survivor and therefore triggered mandatory independent verification.

The fresh verifier **refuted** it:

```yaml
id: shortlist-narrow/ledger-defined-volatile-refresh
verdict: refuted
justification: >
  The Narrow entrypoint requires reading and following the narrowing protocol.
  That protocol expressly requires every applicable ledger-defined Volatile
  class, including Research-added classes. The older list in SKILL.md is a
  summary without “only” language and does not override the protocol.
decisive_citations:
  - skills/shortlist-narrow/SKILL.md:12
  - skills/shortlist-narrow/SKILL.md:37
  - skills/shortlist/references/narrowing-protocol.md:68-70
  - skills/shortlist/references/record-schemas.md:392
  - kamui/shortlist#45 acceptance criterion 6
correction:
  action: Drop; wording synchronization would be optional, not must-fix.
duplicate_groups: []
```

The primary accepted the correction and dropped the finding.

### 2. Dedicated Volatile marker or expectation field

Dropped during primary falsification. The issue permits outcome-level representation; the ledger class, semantic claim classification, dated Evidence, and category judgment plausibly satisfy it without prescribing a new field.

### 3. Bundle-contract Kind list

Dropped. `search-bundle-format.md` ends its list with open “other category-relevant work” wording and links the formal record schema containing `Volatile-claim class`.

### 4. Freshness-attestation timing

Dropped. `Freshness credibility` is explicitly judgment-only, and the issue does not prohibit checking it during Research completion.

## Fresh-verifier discipline

Exactly one verifier ran with `fork_turns=none`. It received the repository and pinned SHAs, issue and base-rule coordinates, candidate claim and raw citations, anchor `narrowing-protocol.md:68`, proposed fix `shortlist-narrow/SKILL.md:46`, trigger, impact, action, and requested outcome. Primary support, confidence, reasoning, and conclusion were withheld. It generated no new candidates and made no writes.

The verifier used 5 orchestration calls containing 21 shell-command invocations. Their cumulative
reported tool wall time was approximately 1.6 seconds; end-to-end verifier time was unavailable.

## Checks

- Head, base, merge-base, and nine-file manifest matched the controlled brief.
- `git diff --check` passed.
- `node --test "tests/*.ts"` — 60 passed.
- System Python 3.9.6 — 290 executed, 129 failures and 11 errors from the repository's pre-existing newer-Python requirements, chiefly `zip(strict=...)`; recovered as environment skew.
- `/opt/homebrew/bin/python3` 3.14.7 — 290 passed.
- Final worktree status clean.
- No live GitHub state was read, and nothing was published or modified.

## Run conditions and observed ambiguity

The run used `/tmp/run-v5` at the same pinned snapshot and the same phase-1 PR/issue inputs as v2-v4. Publication was disabled and controlled prior-review state was `none`, even though v4 had since been published live. The primary did not inspect earlier prototype outputs.

The only reported ambiguity was fingerprint input classification: the contract does not precisely distinguish repository domain evidence as `guidance` versus `specs`. The run treated applicable base rule files as guidance, issue #45 as the sole spec source, and ADR/design files as inspected repository evidence pinned by the base SHA. No concrete runtime skill defect was reported.

Before this controlled run, an independent synthetic forward test exposed an undefined file-level-comment route. V5 was patched to use a first-class file anchor and to place its complete prose in the same GitHub review body when the documented batch endpoint cannot express file subjects; a targeted re-check passed. That rendering change is why this run uses `workflow=v5-2`.

## Overlap with v2, v3, and v4

Raw data, no interpretation.

| Item | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Narrow skill closed refresh list | confirmed, P1, **must-fix** | admitted, P2, **blocking** | confirmed, P2, **consider / non-blocking** | primary P2 must-fix, then **refuted and dropped** |
| `search-bundle-format.md:208` five-kind list | confirmed, P1, **must-fix** | dropped (gates 1/4) | confirmed, P3, **consider**, impact cut by verifier | **dropped** (open wording + linked formal schema) |
| `validate-completion.py` commerce-only regex | confirmed, P2, consider | dropped (gates 2/4/6) | not raised | not raised |
| Freshness expectation unrecorded | confirmed, P2, consider | not raised (AC4 met) | dropped (pre-existing at base) | **dropped** (outcome satisfied; representation not prescribed) |
| `research-protocol.md` stock/delivery branch | refuted by verifier | not raised | not raised | not raised |
| Attestation test | refuted by verifier | dropped #5 | dropped #1 | not raised; a distinct timing candidate was dropped |
| `PROJECT_BRIEF.md` / ADR stale lists | not raised | dropped #4 | dropped #3 | not raised |
| `shortlist-research/SKILL.md:39` | acquitted by finder, not raised | dropped #3 | dropped #2 | not raised |
| Schema bump for widened enum | not raised | not raised | dropped #6 | no compatibility break found |
| **Derived status** | Changes Requested (advisory) | Changes Requested (advisory) | Approved (advisory) | **Approved (advisory), no findings** |
