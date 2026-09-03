# Comparison data — v2, v3, v4, v5 on `kamui/shortlist#66`

> **Promotion status:** “v5” is the historical prototype name used by this record. PR #17 promoted that workflow to `skills/code-review-publish` on `main`; new experiments should invoke `/code-review-publish` without the `-5` suffix.

**2026-09-01. Data only.** Every number here is measured or directly observed; the analysis is in
[`evaluation.md`](evaluation.md).

All four runs used the same model and harness — Claude Opus 5 (1M context) at High reasoning under
the Claude Code CLI — so the cost columns are directly comparable. See
[conditions held constant](README.md#conditions-held-constant).

## Cost and shape

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Agents spawned | 3 | 1 | 2 | 2 |
| **Sub-agent tokens** | **253,712** | **110,630** | **175,824** | **174,563** |
| — breakdown | 91,333 + 99,834 finders; 62,545 verifier | 110,630 reviewer | 128,616 reviewer; 47,208 verifier | 128,013 reviewer; 46,550 verifier |
| Tool uses | 118 | 49 | 78 | 64 |
| Wall clock (sub-agents) | ~851 s (finders parallel) | ~663 s | ~879 s | ~986 s |
| Verifier used? | yes, mandatory | no (frequent path) | yes, conditional threshold met | yes, one `must-fix` + one batched `consider` |
| Verifier share of tokens | 25% | — | 27% | 27% |

## Output

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Candidates raised | 6 (+1 passed-along) | 10 | 10 | 6 |
| Dropped before publication | 2 refuted, 1 merged | 9 dropped | 8 dropped in falsification, 0 refuted | 4 in falsification, 0 refuted |
| **Findings** | **4** | **1** | **2** | **2** |
| Blocking findings | 2 | 1 | 0 | 0 |
| Priority spread | P1, P1, P2, P2 | P2 | P2, P3 | P3, P3 |
| Questions | 0 | 0 | 0 to author; 1 to orchestrator | 0 |
| Coverage reported | complete | complete, fetch gap disclosed | incomplete → complete after recovery | complete |
| **Derived status** | Changes Requested (advisory) | Changes Requested (advisory) | **Approved (advisory)** | **Approved (advisory)** |

## Finding-level agreement

Twelve distinct items were considered by at least one run.

| Item | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Narrow skill's closed refresh list | **confirmed** P1 must-fix | **admitted** P2 blocking | **confirmed** P2 consider | **confirmed** P3 consider (verifier-downgraded from P2 must-fix) |
| `search-bundle-format.md:208` five-kind enumeration | **confirmed** P1 must-fix | dropped (gates 1/4) | **confirmed** P3 consider | **confirmed** P3 consider |
| `validate-completion.py` commerce-only volatile regex | **confirmed** P2 consider | dropped (gates 2/4/6) | not raised | not raised |
| Freshness expectation has no recording site | **confirmed** P2 consider | not raised (AC4 met) | dropped (gate 2, pre-existing at base) | not raised (AC4 met; `Observed` already required on every Evidence record) |
| `research-protocol.md` commerce branch excludes generalized claims | **refuted** | not raised | not raised | dropped (per-bundle-type Freshness split cannot fire) |
| Attestation test asserts complete on "incomplete" bundle | **refuted** (factually wrong) | dropped #5 | dropped #1 | acquitted pre-candidate by executing the validator |
| `PROJECT_BRIEF.md` / ADR 0017 stale seed lists | not raised | dropped #4 | dropped #3 | dropped (not lockstep peers at base) |
| `shortlist-research/SKILL.md:39` omits refine/mark-inapplicable | acquitted, not raised | dropped #3 | dropped #2 | not raised |
| Schema bump for widened enum | not raised | not raised | dropped #6 | no compatibility break found |
| `narrowing-protocol.md:68` cites "the ledger" in a commerce-shared section | not raised | not raised | not raised | dropped (gate 4) |
| Streaming fixture record 8's negative `Why it applies` | not raised | not raised | not raised | dropped (base fixture uses the identical idiom) |
| Freshness-attestation timing | not raised | not raised | not raised | not raised |

**All four confirmed the Narrow closed refresh list**, with four different calibrations: P1
`must-fix`, P2 blocking, P2 `consider`, and P3 `consider`.

**Three of four confirmed `search-bundle-format.md:208`** — v2 as P1 `must-fix`, v4 and v5 as P3
`consider`. Only v3 dropped it.

**Independently reached, same conclusion in all four:** every run killed the attestation-test
candidate, and all but v2 did so by executing the validator and finding the mutation is required
setup. V2 reached it through a verifier refutation of an out-of-axis observation one finder passed
along; v3 and v4 reached it inside falsification; v5 acquitted it before it became a candidate.

**Maximum disagreement:** `search-bundle-format.md:208` — v2 P1 blocking versus v3 dropping it
entirely, with v4 and v5 landing together at P3 non-blocking.

**Only v5 raised** the `narrowing-protocol.md:68` ledger-scope imprecision and the streaming
fixture's negative `Why it applies`; it dropped both.

## Requirement ledger comparison — issue #45, 10 criteria

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Met | 7 | 8 | 10 (3 flagged "met, with propagation gap") | 10 |
| Partial / not met | 3 (AC1, AC4, AC6) | 2 (AC5 protocol-only, AC6 partial) | 0 | 0 |
| Unverifiable | 0 | 0 | 0 | 0 |
| Scope creep found | 0 (explicit pass) | not separately reported | 0 (non-goals explicitly checked) | 0 (non-goal checked) |

All four verified AC10 by running both suites: 290 Python tests and 60 Node tests, green under a
modern Python runtime.

## Verifier behavior, where one ran

| | v2 | v4 | v5 |
| --- | --- | --- | --- |
| Input discipline | claims only, `support` withheld | claims only, `support` withheld | claim and raw citations only, `support` withheld |
| Candidates submitted | 7 | 2 | 2 (1 mandatory, 1 batched under the `consider` clause) |
| Verdicts | 4 confirmed, 2 refuted, 1 merge | 2 confirmed, 0 refuted, 0 merges | **2 confirmed**, 0 refuted, 0 merges |
| Corrections made | 2 triggers corrected, 1 refinement | 1 trigger basis corrected, 1 requirement citation reordered, **1 impact cut as "not establishable"** | 1 impact refined plus a missed lockstep commit supplied; **1 trigger example replaced and the record downgraded P2→P3, must-fix→consider, requirement→maintainability** |
| Priority moves | 0 | 0 (explicitly said *do not raise* F2) | 1 downgrade; 0 raises |
| Refutation evidence | quoted decisive line each time | n/a | n/a — nothing was refuted |
| Effect on derived status | none | none | **Changes Requested → Approved**, without erasing a finding |

## Distinguishing behaviors observed

- **v2** was the only run to produce a **cross-axis duplicate** and merge it (its Code and
  Requirements finders independently found the Narrow list from different angles; the verifier merged
  them keeping the Requirements frame). Its verifier was also the only one to refute anything.
- **v3** was the only run to cite **commit history as evidence for a finding** — `1450bc2`
  introduced the protocol line and the skill line together, establishing lockstep maintenance and
  making the omission drift rather than design. V5 later used the same commit plus `1c25a91` and
  `55e1f25` to establish a second, four-document lockstep set.
- **v4** was the only run to **stop and ask the orchestrator**, to distinguish a recoverable from an
  unrecoverable fetch in its status derivation, and to **flag an ambiguous policy call** (whether
  `SKILL.md` files are a "public/external contract" for its mandatory-verification threshold)
  instead of silently resolving it.
- **v5** was the only run whose verifier **downgraded a candidate across the blocking boundary
  rather than confirming or erasing it** — turning a provisional P2 `must-fix` into a published P3
  `consider`, which is what moved the run from `Changes Requested` to `Approved`. It was also the
  only run to route verification by action rather than artifact name, to use outcome-level
  representation to avoid requiring a new freshness field, and to acquit the attestation test before
  it ever became a candidate.
- All four **used base-branch state to acquit candidates**, not only to convict: v2 cleared a
  fixture's `Not applicable` seed and a suspected duplicate test block; v3 cleared `PROJECT_BRIEF`/ADR
  drift and the schema question; v4 cleared the freshness-expectation gap and the development-repo
  path citation; v5 cleared the ADR/`PROJECT_BRIEF` lists by proving they were never lockstep peers,
  and cleared the streaming fixture's negative disposition against the base fixture's own idiom.

## Publication decision

V4's output was published to PR #66 after the first three runs finished. V5 ran later and was not
published.
