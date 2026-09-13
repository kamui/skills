# Routine-review diagnosis: collection plan

Recorded before inspecting selected review outcomes for [issue #216](https://github.com/kamui/skills/issues/216).

- Cutoff: **2026-09-13T07:47:31Z**. Window: **2026-08-14T07:47:31Z through cutoff**, inclusive.
- Shipped repository policy: `374635be7f4e62f6eb9c797530bf6bf091a9d3a1` (`origin/main`, verified against GitHub). Latest commit touching `skills/code-review-publish`: `afcdbd86bb328d5071153d65a22ea1fa3f5e7433`. Workflow: **v5b-15**, as recorded in the runtime output contract and validator. A target's source head is not a policy commit.
- Sources to search: tracked repository filenames and research indexes; GitHub `kamui/skills` issue/PR metadata updated since 2026-08-14; review-run identity trailers in their review/comment records; explicitly linked routine-review artifacts. Exclude experimental cells, paper replays, implementation-only local reviews, audit reviews, and reserved blind targets from the routine sample. Do not open sealed truth or investigate active reserved targets.
- Selection: enumerate identifiable routine-review runs with timestamps in the window, sort descending by submission time, break ties by qualified repository, PR number and review/comment ID, and take at most **20 runs**. Separate re-reviews count as runs; duplicate representations of one publication do not. Do not filter by verdict, allegation, later fix, or availability of a private trace. Unknown workflow provenance remains unknown; workflow declarations alone do not prove an exact installed policy commit.
- Inspect selected outcomes only after fixing the list. Retain supported misses, non-defects and unresolved allegations separately from runs. Establish a miss at its reviewed head and legitimate scope using existing evidence; missing publication alone never establishes discovery loss. Stop at the bound or an insufficient current-release sample, without initiating new review sessions or widening into a study.
- Reservation check: use #173/#174/#175 and #199/#207 status and non-truth inventory information before following target evidence. Defer ambiguous reservations. Existing research files surfaced incidentally by initial broad text searches are historical context only, not sample selection; record any exposed target identities in the consumed-material register.

## Frozen run selection

The first 20 trailer-bearing publications in descending submission order are below. No outcome was used to choose them. All are native review objects on `kamui/skills`; the other 77 identified trailer records are outside the selected 20. Eligibility of linked artifacts and reservations is checked separately.

| Run | PR / review | Submitted (UTC) | Declared workflow |
| --- | --- | --- | --- |
| R01 | [#215 / 5189692717](https://github.com/kamui/skills/pull/215#pullrequestreview-5189692717) | 2026-09-13T05:41:27Z | v5b-14 |
| R02 | [#214 / 5189597506](https://github.com/kamui/skills/pull/214#pullrequestreview-5189597506) | 2026-09-13T05:04:26Z | v5b-13 |
| R03 | [#213 / 5189241215](https://github.com/kamui/skills/pull/213#pullrequestreview-5189241215) | 2026-09-13T02:53:21Z | v5b-13 |
| R04 | [#212 / 5188844112](https://github.com/kamui/skills/pull/212#pullrequestreview-5188844112) | 2026-09-13T00:50:22Z | v5b-13 |
| R05 | [#212 / 5188676934](https://github.com/kamui/skills/pull/212#pullrequestreview-5188676934) | 2026-09-13T00:08:03Z | v5b-13 |
| R06 | [#211 / 5188336914](https://github.com/kamui/skills/pull/211#pullrequestreview-5188336914) | 2026-09-12T22:32:16Z | v5b-13 |
| R07 | [#211 / 5188061385](https://github.com/kamui/skills/pull/211#pullrequestreview-5188061385) | 2026-09-12T21:04:46Z | v5b-13 |
| R08 | [#210 / 5187741370](https://github.com/kamui/skills/pull/210#pullrequestreview-5187741370) | 2026-09-12T19:33:44Z | v5b-13 |
| R09 | [#209 / 5186003127](https://github.com/kamui/skills/pull/209#pullrequestreview-5186003127) | 2026-09-12T09:28:49Z | v5b-13 |
| R10 | [#208 / 5185964042](https://github.com/kamui/skills/pull/208#pullrequestreview-5185964042) | 2026-09-12T09:11:26Z | v5b-13 |
| R11 | [#206 / 5185648851](https://github.com/kamui/skills/pull/206#pullrequestreview-5185648851) | 2026-09-12T06:43:57Z | v5b-13 |
| R12 | [#206 / 5185478523](https://github.com/kamui/skills/pull/206#pullrequestreview-5185478523) | 2026-09-12T05:47:16Z | v5b-13 |
| R13 | [#205 / 5185178651](https://github.com/kamui/skills/pull/205#pullrequestreview-5185178651) | 2026-09-12T04:25:47Z | v5b-13 |
| R14 | [#204 / 5185029515](https://github.com/kamui/skills/pull/204#pullrequestreview-5185029515) | 2026-09-12T03:30:47Z | v5b-12 |
| R15 | [#203 / 5185003569](https://github.com/kamui/skills/pull/203#pullrequestreview-5185003569) | 2026-09-12T03:20:55Z | v5b-12 |
| R16 | [#201 / 5184681198](https://github.com/kamui/skills/pull/201#pullrequestreview-5184681198) | 2026-09-12T01:45:26Z | v5b-12 |
| R17 | [#201 / 5182728464](https://github.com/kamui/skills/pull/201#pullrequestreview-5182728464) | 2026-09-11T19:35:08Z | v5b-12 |
| R18 | [#200 / 5175922172](https://github.com/kamui/skills/pull/200#pullrequestreview-5175922172) | 2026-09-11T07:16:36Z | v5b-12 |
| R19 | [#200 / 5175408147](https://github.com/kamui/skills/pull/200#pullrequestreview-5175408147) | 2026-09-11T05:58:31Z | v5b-12 |
| R20 | [#198 / 5170526713](https://github.com/kamui/skills/pull/198#pullrequestreview-5170526713) | 2026-09-10T17:52:31Z | v5b-12 |
