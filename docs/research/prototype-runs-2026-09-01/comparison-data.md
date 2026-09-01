# Comparison data — v2, v3, v4 on `kamui/shortlist#66`

**2026-09-01. Data only — no analysis.** Every number here is measured or directly observed.

## Cost and shape

| | v2 | v3 | v4 |
| --- | --- | --- | --- |
| Agents spawned | 3 | 1 | 2 |
| **Sub-agent tokens** | **253,712** | **110,630** | **175,824** |
| — breakdown | 91,333 + 99,834 finders; 62,545 verifier | 110,630 reviewer | 128,616 reviewer; 47,208 verifier |
| Tool uses | 118 | 49 | 78 |
| Wall clock (sub-agents) | ~851 s (finders parallel) | ~663 s | ~879 s |
| Verifier used? | yes, mandatory | no (frequent path) | yes, conditional threshold met |
| Verifier share of tokens | 25% | — | 27% |

## Output

| | v2 | v3 | v4 |
| --- | --- | --- | --- |
| Candidates raised | 6 (+1 passed-along) | 10 | 10 |
| Dropped before publication | 2 refuted, 1 merged | 9 dropped | 8 dropped in falsification, 0 refuted |
| **Findings** | **4** | **1** | **2** |
| Blocking findings | 2 | 1 | 0 |
| Priority spread | P1, P1, P2, P2 | P2 | P2, P3 |
| Questions | 0 | 0 | 0 to author; 1 to orchestrator |
| Coverage reported | complete | complete, fetch gap disclosed | incomplete → complete after recovery |
| **Derived status** | Changes Requested (advisory) | Changes Requested (advisory) | **Approved (advisory)** |

## Finding-level agreement

Nine distinct items were considered by at least one run.

| Item | v2 | v3 | v4 |
| --- | --- | --- | --- |
| Narrow skill's closed refresh list | **confirmed** P1 must-fix | **admitted** P2 blocking | **confirmed** P2 consider |
| `search-bundle-format.md:208` five-kind enumeration | **confirmed** P1 must-fix | dropped (gates 1/4) | **confirmed** P3 consider |
| `validate-completion.py` commerce-only volatile regex | **confirmed** P2 consider | dropped (gates 2/4/6) | not raised |
| Freshness expectation has no recording site | **confirmed** P2 consider | not raised (AC4 met) | dropped (gate 2, pre-existing at base) |
| `research-protocol.md` stock/delivery commerce branch | **refuted** | not raised | not raised |
| Attestation test asserts complete on "incomplete" bundle | **refuted** (factually wrong) | dropped #5 | dropped #1 |
| `PROJECT_BRIEF.md` / ADR 0017 stale seed lists | not raised | dropped #4 | dropped #3 |
| `shortlist-research/SKILL.md:39` omits refine/mark-inapplicable | acquitted, not raised | dropped #3 | dropped #2 |
| Schema bump for widened enum | not raised | not raised | dropped #6 |

**Unanimous:** only the Narrow closed refresh list — the sole item all three published. Its severity differs across all three runs (must-fix / blocking / non-blocking consider).

**Independently reached, same conclusion:** all three killed the attestation-test candidate by executing the validator and finding the mutation is required setup. v2 reached it through a verifier refutation of an out-of-axis observation one finder passed along; v3 and v4 reached it inside falsification.

**Maximum disagreement:** `search-bundle-format.md:208` — v2 P1 blocking, v3 dropped entirely, v4 P3 non-blocking with impact cut down by its verifier.

## Requirement ledger comparison — issue #45, 10 criteria

| | v2 | v3 | v4 |
| --- | --- | --- | --- |
| Met | 7 | 8 | 10 (3 flagged "met, with propagation gap") |
| Partial / not met | 3 (AC1, AC4, AC6) | 2 (AC5 protocol-only, AC6 partial) | 0 |
| Unverifiable | 0 | 0 | 0 |
| Scope creep found | 0 (explicit pass) | not separately reported | 0 (non-goals explicitly checked) |

All three verified AC10 by running both suites: 290 Python tests, 60 node tests, green.

## Verifier behavior, where one ran

| | v2 | v4 |
| --- | --- | --- |
| Input discipline | claims only, `support` withheld | claims only, `support` withheld |
| Verdicts | 4 confirmed, 2 refuted, 1 merge | 2 confirmed, 0 refuted, 0 merges |
| Corrections made | 2 triggers corrected, 1 refinement | 1 trigger basis corrected, 1 requirement citation reordered, **1 impact cut as "not establishable"** |
| Priority moves | 0 | 0 (explicitly said *do not raise* F2) |
| Refutation evidence | quoted decisive line each time | n/a |

## Distinguishing behaviors observed

- **v2** was the only run to produce a **cross-axis duplicate** and merge it (its Code and Requirements finders independently found the Narrow list from different angles; the verifier merged them keeping the Requirements frame). It was also the only run whose verifier **refuted anything**.
- **v3** was the only run to cite **commit history as evidence for a finding** — `1450bc2` introduced the protocol line and the skill line together, establishing lockstep maintenance and making the omission drift rather than design.
- **v4** was the only run to **stop and ask the orchestrator**, to distinguish a recoverable from an unrecoverable fetch in its status derivation, and to **flag an ambiguous policy call** (whether `SKILL.md` files are a "public/external contract" for its mandatory-verification threshold) instead of silently resolving it. It was also the only run to reach `Approved`.
- All three **used base-branch state to acquit candidates**, not only to convict: v2 cleared a fixture's `Not applicable` seed and a suspected duplicate test block; v3 cleared `PROJECT_BRIEF`/ADR drift and the schema question; v4 cleared the freshness-expectation gap and the development-repo path citation.

## Publication decision

One run's output was published to PR #66 after all three finished. See `publication-decision.md`.
