# Comparison data — v2, v3, v4, v5 on `kamui/shortlist#66`

**2026-09-01. Data only — no analysis.** Every number here is measured or directly observed.

## Cost and shape

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Agents spawned | 3 | 1 | 2 | 2 |
| **Sub-agent tokens** | **253,712** | **110,630** | **175,824** | unavailable |
| — breakdown | 91,333 + 99,834 finders; 62,545 verifier | 110,630 reviewer | 128,616 reviewer; 47,208 verifier | unavailable |
| Tool uses | 118 | 49 | 78 | 41 |
| Wall clock (sub-agents) | ~851 s (finders parallel) | ~663 s | ~879 s | unavailable |
| Verifier used? | yes, mandatory | no (frequent path) | yes, conditional threshold met | yes, one `must-fix` survivor |
| Verifier share of tokens | 25% | — | 27% | unavailable |

## Output

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Candidates raised | 6 (+1 passed-along) | 10 | 10 | 4 |
| Dropped before publication | 2 refuted, 1 merged | 9 dropped | 8 dropped in falsification, 0 refuted | 3 in falsification, 1 refuted |
| **Findings** | **4** | **1** | **2** | **0** |
| Blocking findings | 2 | 1 | 0 | 0 |
| Priority spread | P1, P1, P2, P2 | P2 | P2, P3 | — |
| Questions | 0 | 0 | 0 to author; 1 to orchestrator | 0 |
| Coverage reported | complete | complete, fetch gap disclosed | incomplete → complete after recovery | complete |
| **Derived status** | Changes Requested (advisory) | Changes Requested (advisory) | **Approved (advisory)** | **Approved (advisory), no findings** |

## Finding-level agreement

Ten distinct items were considered by at least one run.

| Item | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Narrow skill's closed refresh list | **confirmed** P1 must-fix | **admitted** P2 blocking | **confirmed** P2 consider | primary P2 must-fix, then **refuted** |
| `search-bundle-format.md:208` five-kind enumeration | **confirmed** P1 must-fix | dropped (gates 1/4) | **confirmed** P3 consider | dropped (open wording + linked schema) |
| `validate-completion.py` commerce-only volatile regex | **confirmed** P2 consider | dropped (gates 2/4/6) | not raised | not raised |
| Freshness expectation has no recording site | **confirmed** P2 consider | not raised (AC4 met) | dropped (gate 2, pre-existing at base) | dropped (outcome met; representation unprescribed) |
| `research-protocol.md` stock/delivery commerce branch | **refuted** | not raised | not raised | not raised |
| Attestation test asserts complete on "incomplete" bundle | **refuted** (factually wrong) | dropped #5 | dropped #1 | not raised |
| Freshness-attestation timing | not raised | not raised | not raised | dropped (judgment-only; no prohibited timing) |
| `PROJECT_BRIEF.md` / ADR 0017 stale seed lists | not raised | dropped #4 | dropped #3 | not raised |
| `shortlist-research/SKILL.md:39` omits refine/mark-inapplicable | acquitted, not raised | dropped #3 | dropped #2 | not raised |
| Schema bump for widened enum | not raised | not raised | dropped #6 | no compatibility break found |

**All four considered the Narrow closed refresh list.** V2-v4 published it with three different action/severity calibrations; v5's primary proposed P2 `must-fix`, but its fresh verifier refuted it, leaving no finding.

**Independently reached, same conclusion among v2-v4:** all three killed the attestation-test candidate by executing the validator and finding the mutation is required setup. V2 reached it through a verifier refutation of an out-of-axis observation one finder passed along; v3 and v4 reached it inside falsification. V5 raised a different attestation-timing candidate and dropped it.

**Maximum disagreement:** `search-bundle-format.md:208` — v2 P1 blocking, v3 dropped entirely, v4 P3 non-blocking with impact cut down by its verifier, and v5 dropped because the prose is open-ended and links the complete formal schema.

## Requirement ledger comparison — issue #45, 10 criteria

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Met | 7 | 8 | 10 (3 flagged "met, with propagation gap") | 10 |
| Partial / not met | 3 (AC1, AC4, AC6) | 2 (AC5 protocol-only, AC6 partial) | 0 | 0 |
| Unverifiable | 0 | 0 | 0 | 0 |
| Scope creep found | 0 (explicit pass) | not separately reported | 0 (non-goals explicitly checked) | 0 (non-goal checked) |

All four verified AC10 by running both suites: 290 Python tests and 60 Node tests, green under a modern Python runtime.

## Verifier behavior, where one ran

| | v2 | v4 | v5 |
| --- | --- | --- | --- |
| Input discipline | claims only, `support` withheld | claims only, `support` withheld | claim and raw citations only, `support` withheld |
| Verdicts | 4 confirmed, 2 refuted, 1 merge | 2 confirmed, 0 refuted, 0 merges | 0 confirmed, **1 refuted** |
| Corrections made | 2 triggers corrected, 1 refinement | 1 trigger basis corrected, 1 requirement citation reordered, **1 impact cut as "not establishable"** | sole survivor dropped; action reframed as optional wording synchronization |
| Priority moves | 0 | 0 (explicitly said *do not raise* F2) | candidate removed |
| Refutation evidence | quoted decisive line each time | n/a | cited the entrypoint's protocol requirement and broader protocol text |

## Distinguishing behaviors observed

- **v2** was the only run to produce a **cross-axis duplicate** and merge it (its Code and Requirements finders independently found the Narrow list from different angles; the verifier merged them keeping the Requirements frame). Its verifier refuted two candidates; v5's later verifier refuted one.
- **v3** was the only run to cite **commit history as evidence for a finding** — `1450bc2` introduced the protocol line and the skill line together, establishing lockstep maintenance and making the omission drift rather than design.
- **v4** was the only run to **stop and ask the orchestrator**, to distinguish a recoverable from an unrecoverable fetch in its status derivation, and to **flag an ambiguous policy call** (whether `SKILL.md` files are a "public/external contract" for its mandatory-verification threshold) instead of silently resolving it. Among v2-v4, it was the only run to reach `Approved`.
- **v5** was the only run whose verifier **refuted its sole survivor**, turning a provisional P2 `must-fix` into a clean approval. It also explicitly used outcome-level representation to avoid requiring a new freshness field and routed verification by action rather than the artifact name.
- All four **used base-branch state to acquit candidates**, not only to convict: v2 cleared a fixture's `Not applicable` seed and a suspected duplicate test block; v3 cleared `PROJECT_BRIEF`/ADR drift and the schema question; v4 cleared the freshness-expectation gap and the development-repo path citation; v5 used the base entrypoint/protocol relationship and schema links to drop its two synchronization candidates.

## Publication decision

V4's output was published to PR #66 after the first three runs finished. V5 ran later and was not published. See `publication-decision.md`.
