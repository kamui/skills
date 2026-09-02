# Findings 5: v2a bundle-contract miss

## Verdict

The miss is systematic under the v2a run conditions, not an isolated sample. The original v2a
Requirements run and four fresh independent reruns all failed to raise or acquit
`skills/shortlist/references/search-bundle-format.md:208`. The unchanged rubric therefore scored
0/5 for considering the known obligation-kind drift.

The evidence does not isolate one of C1 through C5 as the cause. C3 is ruled out directly: a fresh
run with only the disposition-ledger output requirement removed still missed the item. C1, C4, and
C5 affect classification or reporting after a hypothesis exists; the transcript shows that this
hypothesis never existed. C2 and C6 do not apply to this target. The original v2 run used a
different model and harness, so the result proves a systematic v2a failure under the repeated run
conditions, not that one rubric edit alone caused the behavioral change.

## Replicates

All runs used the pinned target with head
`4349ff41ff4d134e09017662dd30420b80e8eb30`, base and merge-base
`ccd1842d742fd940b2afde4f903c7bdcb3a707eb`, the same issue and pull-request packet, Claude Sonnet
5 at high effort, an offline clone, and publication disabled.

| Run | Rubric | `search-bundle-format.md:208` | Result |
| --- | --- | --- | --- |
| Original v2a | `023baf7` | absent | missed |
| Fresh 2 | unchanged v2a | absent | missed |
| Fresh 3 | unchanged v2a | absent | missed |
| Fresh 4 | unchanged v2a | absent | missed |
| Fresh 5 | unchanged v2a | absent | missed |

The four fresh runs used 41 to 53 model turns and produced 26,199 to 40,019 output tokens including
thinking. Each returned a complete changed-file manifest. This was not early termination or a
smaller review pass.

One causal ablation removed only these two C3 paragraphs from `requirements-axis.md`:

- the requirement to return a disposition ledger;
- the compact four-field row format.

That run used 50 turns and 27,228 output tokens including thinking. It still returned zero
Requirements candidates and never mentioned `search-bundle-format.md`. C3's reporting cost is
therefore not implicated by this test.

## Transcript evidence

The recovered original Requirements-finder transcript contains 41 tool calls. It never searches
for `search-bundle-format.md`, `discovery branch`, or `safeguard`.

Its searches instead follow the freshness wording:

- `volatile` in `record-schemas.md`;
- `freshness expectation`, `freshness horizon`, and `freshness credibility` across the repository;
- volatile and freshness language in the Narrow and Research skill files.

The finder then opens `category-bundle-format.md`, whose name resembles
`search-bundle-format.md`, and acquits its volatile cache-reuse horizon as a different ADR 0004
mechanism. It never lists the sibling reference files or checks the Search bundle contract. The
trace does not show the finder claiming that both filenames name the same artifact. The supported
finding is narrower: its search converged on the adjacent file and stopped before inspecting the
relevant sibling.

The original v2 finder used the decisive repository-wide search
`grep -rn "discovery branch" skills docs CONTEXT.md tests`. That search finds the unchanged phrase
shared by every copy of the obligation-kind enumeration, including stale copies that omit the new
`Volatile-claim class` term. The v2a finder issued no equivalent search.

## Rubric and guidance review

The v2a and v2 Requirements briefs have the same three review steps. C1 adds action calibration,
C3 adds the disposition-ledger output, C4 sharpens question routing, and C5 adds observations.
None adds a completion criterion for checking peer copies of a changed vocabulary or normative
enumeration.

Base `docs/agents/domain.md` directs reviewers to root `CONTEXT.md`, relevant ADRs, and
`docs/design/use-scenario-catalog.md` when Research obligations or category profiles change. Base
`CONTEXT.md` contains the old obligation-kind phrase with `discovery branch` and `safeguard`, so it
could have supplied the decisive search seed. The v2a finder received and read that guidance but
still did not search the phrase. Guidance exposure did not prevent the miss, and no guidance file
points directly to `search-bundle-format.md`.

## Proximate cause

The Requirements brief allowed the finder to mark the category-profile and obligation-kind
requirements met after checking the changed canonical sites. It did not require a repository-wide
peer-contract search before that disposition. Searching the new term alone is insufficient because
a stale copy is defined by omitting that term.

The similar filename shaped the observed search path, but the missing completion criterion is the
actionable cause. It explains why a long, complete review could inspect an adjacent contract,
acquit it correctly, and still never encounter the stale Search bundle contract.

## Fix

`requirements-axis.md` now requires a paired peer-contract sweep before marking each affected
requirement met:

1. Search the whole repository for the new term.
2. Read the base contract and search for a distinctive phrase or member retained in the new
   version.
3. Inspect and ledger every live result, including files outside the changed-file manifest.

The unchanged-term search is the load-bearing half. It finds stale copies that a new-term search
cannot. The sweep ends only after every peer includes the new contract or the finder proves that it
governs a different mechanism.

Two validation runs against an earlier, weaker version of this fix found the Narrow drift but still
missed the bundle contract because they searched only new vocabulary. The final wording records
that failure and makes the base-phrase search a separate required action. The caller requested a
direct push before another model-backed validation round, so this final strengthened wording has
only static validation in this handoff.

## Recommendation

Keep C1 through C5. Record the 0/5 result as a systematic recall regression under v2a's run
conditions, with C3 ruled out rather than blamed. Retain the paired peer-contract sweep and include
this target in the next repeated-seed evaluation. The next evaluation should require the ledger to
name `search-bundle-format.md:208` as either a candidate or an acquittal; a generic complete review
does not count as a pass.
