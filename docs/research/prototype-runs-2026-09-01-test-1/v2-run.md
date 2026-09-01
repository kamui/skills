# v2 run — `code-review-publish-2` against `kamui/shortlist#66`

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-publish-2` (PR #14, at commit `f42f708`) |
| Architecture | 2 axis finders in parallel → 1 mandatory fresh-context verifier |
| Agents spawned | 3 |
| **Total sub-agent tokens** | **253,712** |
| — Code finder | 91,333 (47 tool uses, 462 s) |
| — Requirements finder | 99,834 (35 tool uses, 527 s) |
| — Verifier | 62,545 (36 tool uses, 324 s) |
| Total tool uses | 118 |
| Wall clock (sub-agents) | ~851 s (finders parallel at 527 s, then verifier 324 s) |
| Candidates raised | 6 (+1 out-of-axis observation ruled on) |
| Verdicts | 4 confirmed · 0 plausible · 2 refuted · 1 merged |
| Findings for publication | **4** — 2 `must-fix`/P1, 2 `consider`/P2 |
| Questions | 0 |
| Coverage | complete (9/9 files, both finders) |
| Derived status | **Changes Requested (advisory)** |

## Findings

### F1 — `requirements/search-bundle-format/ledger-omits-volatile-claim-class` — must-fix / P1

- **anchor** `skills/shortlist/references/record-schemas.md:392`
- **fix** `skills/shortlist/references/search-bundle-format.md:208`

Issue #45 AC1 requires a category profile to seed "source families, audits, Candidate relationships, discovery branches, safeguards, **and Volatile-claim classes**". `record-schemas.md:392`, `research-protocol.md:295`, `CONTEXT.md:327`, and `record_schemas.py:397` each gained `Volatile-claim class`. `search-bundle-format.md:208` — the bundle contract every stage skill is told to read before editing a bundle — still enumerates five kinds:

> …one Research obligation record per applicable source family, audit, Candidate relationship, discovery branch, safeguard, or other category-relevant work…

Verifier: **confirmed**. `grep -rn "discovery branch" skills docs CONTEXT.md tests` shows this is the only live enumeration left at five kinds. Corroborated independent of the issue by the commit body itself, which says the kind lands "alongside source families, audits, relationships, discovery branches, and safeguards". Verifier correction to scope: `docs/adr/0017-*.md:7` also carries a stale four-kind list, but an ADR is an immutable historical record, not a contract, so it does not weaken the finding.

**Trigger:** a Coordinator seeding a generalized bundle's ledger from the bundle contract sees five kinds plus `Other`, so a profile's volatile classes get recorded as `Other` or omitted.

### F2 — `requirements/shortlist-narrow/fixed-volatile-refresh-list` — must-fix / P1

- **anchor** `skills/shortlist/references/narrowing-protocol.md:68`
- **fix** `skills/shortlist-narrow/SKILL.md:46`
- Absorbed `code/shortlist-narrow-skill/closed-volatile-class-list` (identical anchor and fix site; Requirements frame kept per the dedup rule)

`narrowing-protocol.md:68` opened the refresh list — "refresh every applicable Volatile claim… not only a fixed commerce list… A claim class a category profile did not anticipate is refreshed on the same terms as one it seeded." `shortlist-narrow/SKILL.md:46`, the Narrow stage's own inline step, is byte-identical to base and still closed:

> Refresh volatile evidence before the final handoff when it may have changed since research: price, stock, delivery, and restock facts in a commerce bundle; access, cost, catalog, licensing, compatibility, and support claims in a generalized bundle.

Verifier: **confirmed**, with a mitigation to carry into the comment — `shortlist-narrow/SKILL.md:12` does tell the agent to read the narrowing protocol, so the open rule is reachable. This is contradictory guidance rather than total omission, but line 46 is the instruction at the point of use and it is the one now wrong.

**Trigger:** the change's own fixture. `generalized-bundle-streaming/ledger.md:63-71` Record 7 is "Ad-tier feature and price-lock volatility", `Kind: Volatile-claim class`, `Origin: Research` — exactly the Research-origin class the enumeration cannot admit. A Narrow session refreshes price and stock, skips it, and hands off on a stale Volatile claim.

### F3 — `code/validate-completion/volatile-timestamp-gate-not-generalized` — consider / P2

- **anchor** `skills/shortlist/references/research-protocol.md:406`
- **fix** `skills/shortlist/scripts/validate-completion.py:2949`

`research-protocol.md:406` widened the timestamp obligation to generalized Volatile classes. The mechanical form at `validate-completion.py:2948-2955` was not widened:

```python
r"\b(?:price|stock|delivery|restock|availability|available|unavailable)\b",
```

Every alternative is commerce; none of `cost`, `access`, `catalog contents`, `policy terms`, `compatibility`, `release support` matches. At base the reference read "Timestamp price, stock, delivery, and restock observations" — exactly what the regex covers — so the divergence is introduced here. `check_freshness.py` `KIND_TARGETS` already carries the broad vocabulary, so the two scripts now disagree on what a Volatile claim is.

Verifier: **confirmed**, with a **corrected trigger** — the finder's flag was wrong. The fixture's `state.md` has `Current stage | Complete`, so `--require-complete` rejects it outright. The reproducible trigger is the plain run:

```
$ validate-completion.py <copy of generalized-bundle>
completion-ready Shortlist bundle
# edit E008's claim to say "price", change nothing else:
ERROR: volatile evidence E008 requires an offset-bearing timestamp
```

### F4 — `requirements/volatile-claim/freshness-expectation-unrecorded` — consider / P2

- **anchor** `skills/shortlist/references/research-protocol.md:406`
- **fix** `skills/shortlist/references/record-schemas.md:611`

Issue #45 AC4 has two halves — "an observation date **and category-appropriate freshness expectation**". Only the first is implemented. The Evidence schema at `record-schemas.md:603-612` is unchanged and carries Scope, Claim, Type, Source and URL, Observed, Notes or conflict. `grep -rni "freshness expectation"` returns exactly one line tree-wide, `CONTEXT.md:295`, with no schema field, protocol step, or validator behind it — while `narrowing-protocol.md:68` newly asks Narrow to judge "materially stale".

Verifier: **confirmed**, requirement corroborated in-repo at `CONTEXT.md:295` without needing the issue. **Trigger refinement:** `check_freshness.py` does supply a global `--horizon-days` defaulting to 7 — but that is one horizon for all claims, not a category-appropriate per-class expectation, and it does not reach the model's judgment.

## Refuted — dropped, never reaches the PR

**`requirements/research-protocol/stock-delivery-commerce-only`** (P3) — refuted as already handled. The generalized branch of the sentence ends "…or another decision-relevant claim Research identifies as Volatile in a generalized bundle", and the next sentence disclaims a fixed list. The stated trigger does not occur. The candidate conceded the behavior stays reachable, which concedes there is no defect.

**`code/tests/attestation-test-asserts-complete-on-incomplete-bundle`** (would have been P2) — refuted as factually wrong. Raised by the Requirements finder as an out-of-axis observation and ruled on anyway. `validate-completion.py:3089,3101-3109` make `Research status: In progress` / `Pool status: In progress` the *only* configuration `--require-complete` accepts; "completion-ready" means eligible to be declared complete, not already complete. The test is setting up the only legal input, and a pre-existing test uses identical setup.

## Notes on the run

- Both finders returned complete 9/9 manifests with per-file reasoning, and both **acquitted candidates using base-branch reading** — the Code finder cleared the streaming fixture's `Not applicable` commerce seed by finding `record-schemas.md:394` blesses it, and cleared a suspected duplicated test-setup block by running the validator and finding the rollback load-bearing.
- The Requirements finder restated all 10 criteria before reading the diff, sorted 7 met / 3 partial / 0 unverifiable, and found **zero scope creep**.
- The verifier's two refutations both quoted a decisive line, per the brief's asymmetry rule. It produced **zero `plausible` verdicts**, so v2's question path again did not fire.
- Verifier could not fetch issue #45 (the clone's `origin` is a local path), and said so, then corroborated each issue quote against in-repo evidence instead.
