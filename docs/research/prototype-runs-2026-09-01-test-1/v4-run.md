# v4 run — `snapshot-path-omitted` against `kamui/shortlist#66`

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `snapshot-path-omitted` (PR #16, branch `snapshot-path-omitted`) |
| Architecture | 1 integrated reviewer + conditional batched fresh-context verifier |
| Agents spawned | 2 (verifier invoked) |
| **Total sub-agent tokens** | **175,824** |
| — Primary reviewer | 128,616 (61 tool uses, 689 s) |
| — Verifier | 47,208 (17 tool uses, 190 s) |
| Total tool uses | 78 |
| Wall clock (sub-agents) | ~879 s (serial) |
| Candidates surviving primary falsification | 2 (8 dropped) |
| Verdicts | 2 confirmed · 0 plausible · 0 refuted · 0 merged |
| Findings for publication | **2** — both `consider`, P2 and P3, `blocking: false` |
| Questions | 0 for the author; **1 for the orchestrator** (see below) |
| Coverage | **incomplete → complete after recovery** |
| Derived status | **Approved (advisory)** with 2 `consider` findings |

## The orchestrator question — a distinguishing event

The primary reviewer stopped at an **unrecoverable-by-it** fetch: the clone's `origin` is a local path, so `gh` could not read the PR #66 body. Rather than proceed silently or ask the author, it:

- marked coverage **`incomplete`** and derived a provisional status of **`Incomplete`**, citing its own rule ("a failed fetch … makes coverage incomplete; a recovered operation does not");
- stated what the missing input could change — gate 6, deliberateness, on both candidates — and that if the body declared skill-entrypoint synchronization deferred to #46, **both candidates drop**;
- addressed the question to the orchestrator, explicitly *not* the author, because repository evidence could not supply it;
- offered to re-run falsification on both records without re-reviewing the diff.

The orchestrator had the body from phase 1 and supplied it to the verifier for the gate-6 check. That made the fetch **recovered**, so coverage reached `complete` and the status moved from `Incomplete` to `Approved (advisory)`.

The reviewer also flagged a genuinely ambiguous call rather than deciding it silently: whether `SKILL.md` files constitute a "public/external contract" for mandatory-verification purposes. Under the repo-specific reading (distributed skill files *are* the product's contract with consumers) both candidates trip the mandatory threshold; under the narrower wire/API reading neither does. It recommended verifying both, on the grounds that the contract question was close and one cheap pass resolved it.

## Requirement ledger — issue #45, 10 criteria

| # | Verdict | Note |
| --- | --- | --- |
| 1 | met, with propagation gap | → F2 (`search-bundle-format.md:208`) |
| 2 | met (non-goal preserved) | verified no executable coupling: `grep use-scenario-catalog` over `*.py`/`*.ts`/`*.json` → zero hits; `routing.json` and `test_routing_contract.ts` untouched |
| 3 | met | completion still mechanically gated at `validate-completion.py:320-360` |
| 4 | met (by prose + ledger class, not a new field) | absence of a freshness-expectation field predates the change; AC9 fences the checker |
| 5 | met, with propagation gap | → F1 |
| 6 | met, with propagation gap | → F1. "Materially stale" mirrors the issue's own wording, so issue-sanctioned, not a regression |
| 7 | met | `research-protocol.md:47-48` consistent with base `CONTEXT.md:299-307` |
| 8 | met | all four fixture cases located |
| 9 | met (non-goal preserved) | manifest touches none of the three freshness-checker files |
| 10 | met | `node --test` 60/60; `unittest` 290 OK; `.github/workflows/test.yml` runs exactly those two |

Explicitly checked and reported: neither non-goal criterion (2, 9) implemented the thing it forbade.

## Risk checks

- **Migrations / compatibility** — clean. Ran `validate-completion.py --require-complete` against a mutated copy of `generalized-bundle` → rc 0. Forward skew exists but matches the precedent `55e1f25` set by adding `Other` without a schema bump.
- **Stale state / partial failure** — clean. Nothing executable changed; `freshness-checker.md:3-10` already detects the generalized vocabulary, so the doc change does not outrun the tool.
- **External contracts / version skew** — one documentary gap → F2. `validate-completion.py:18` imports `OBLIGATION_KINDS`, so the enum has a single definition and no code list drifted.
- **ADR conflict check** (required by base `docs/agents/domain.md`) — clean. ADR 0017's list is an extension not a contradiction; ADR 0007 already records the 0015–0017 broadening.
- **Not applicable, with reason** — authorization/sessions/tokens; secrets/crypto/logging; path traversal/symlinks.

### F1 — `shortlist-narrow/volatile-refresh-list-closed` — consider / P2 / blocking: false

- **anchor** `skills/shortlist/references/narrowing-protocol.md:68` (RIGHT) · **fix** `skills/shortlist-narrow/SKILL.md:46`

**Claim:** the narrowing protocol now drives pre-handoff refresh from whichever claims the category and ledger identify as Volatile, but `shortlist-narrow/SKILL.md:46` still instructs the Narrow stage with a closed enumeration omitting policy terms, release support, and any Volatile-claim class Research adds.

Verifier: **confirmed**, with base-state proof the divergence was introduced here — base `narrowing-protocol.md` carried a two-branch fixed list that matched the SKILL text, so the two were in sync before the change. `grep -rn -i "volatile\|restock\|refresh" skills/*/SKILL.md` confirms line 46 is the only refresh instruction in any SKILL.md, so the fix site is uniquely correct.

**Verifier corrections:**
- **trigger** — the "Working files" argument was *overstated as the mechanism*. `SKILL.md:35-46` opens "Follow the narrowing protocol:", so an agent that read the protocol does have the open rule in context. The defect is the SKILL's own narrower restatement standing beside it at the refresh step, not the agent never seeing the protocol. Survives either way, restated on the conflicting-restatement basis.
- **requirement citation** — lead with AC5 ("or another evidenced class"), which line 46 straightforwardly violates. AC6 is secondary: line 46 does list non-commerce facts, so it does not literally "assume that only commerce facts can expire."
- priority, action, anchor, fix, change: unchanged.

Impact established with no mechanical backstop: the new `Freshness credibility` attestation sits in `JUDGMENT_ONLY_ATTESTATIONS`, printed under "Judgment-only attestations (not mechanically validated)", and no test asserts SKILL/protocol consistency — so the gap is silent.

### F2 — `search-bundle-format/obligation-kind-enumeration` — consider / P3 / blocking: false

- **anchor** `skills/shortlist/references/research-protocol.md:295` (RIGHT) · **fix** `skills/shortlist/references/search-bundle-format.md:208`

**Claim:** `Volatile-claim class` was added to the enumeration in `research-protocol.md:295`, `record-schemas.md:392`, `CONTEXT.md:327` and `record_schemas.py:397`, but the identical enumeration in the bundle contract at `search-bundle-format.md:208` was left unchanged.

Verifier: **confirmed**. `git show ccd1842` proves `search-bundle-format.md:208` and `research-protocol.md:287` carried word-for-word the same list at base, so the divergence is introduced here. Trigger verified against `tests/test_locator_contract.ts:77-81`, which asserts every stage skill references the shared contract.

**Verifier correction — impact overstated and cut down:** two unchanged facts cap it. The contract sentence links inline to `record-schemas.md#research-obligation`, which does enumerate the kind; and seeding is governed by `research-protocol.md:295`, which `shortlist-research/SKILL.md:16` requires before live category research. So "a reconnaissance pass driven from it can omit Volatile-claim class obligations entirely" **is not establishable**. Restated as: the bundle contract now understates the ledger's obligation vocabulary and contradicts three synchronized copies — contract inconsistency in a normative document, not a demonstrated omission. P3 explicitly kept and the verifier said *do not raise it* given the corrected impact.

Both findings' deliberateness check used the PR body the orchestrator supplied: it enumerates the files it updated and declares only `check_freshness.py` out of scope, so neither omission is declared intentional. Prior art `55e1f25` updated all four documents in one commit when the Kind vocabulary last changed.

## The eight dropped candidates

1. **Attestation test looks vacuous/inverted** — disproven by execution: unmutated fixture → rc 1 `--require-complete requires Current stage Research`; mutated → rc 0. The mutation is required setup; the test is a real regression guard.
2. **`shortlist-research/SKILL.md:39`** omits "refine, or mark inapplicable" — gates 1/7: a compressed step summary enumerating no kinds, not contradicted; no lockstep precedent for that line.
3. **`PROJECT_BRIEF.md:85` and ADR 0017** omit the kind — gate 2: both already omitted `safeguard` at base, so pre-existing drift not materially worsened.
4. **Community-technology fixture carries no Volatile-claim class** — gates 4/5: AC8 requires a community-technology *profile*, which that fixture is; it does not require that fixture to carry the class.
5. **`narrowing-protocol.md:68` adds a "materially stale" gate**, narrowing prior unconditional behavior — gate 6: AC6 uses that exact phrasing, so issue-sanctioned.
6. **Widening `OBLIGATION_KINDS` without a schema bump** — gates 2/8: backward compatible, verified against existing fixtures; `55e1f25` set the precedent; a bump would exceed the repo's evident rigor.
7. **New section cites a development-repo path from a distributed skill reference** — gates 1/5: explicitly qualified "in the development repository" and cited only to say the catalog is *not* the mechanism — a deliberate non-reference.
8. **No freshness-expectation record field despite `CONTEXT.md:295`** — gate 2: that sentence is present at base `ccd1842` and predates the change; AC9 fences the checker work.
