# Review experiment data

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

**2026-09-03.** Raw outputs and metadata from a fourth controlled comparison of the code-review
prototypes, against a target chosen for a different reason from the first three. **Data only** — the
analysis lives in [`evaluation.md`](evaluation.md); the side-by-side metadata is in
[`comparison-data.md`](comparison-data.md). Earlier comparison sets:
[test 1](../prototype-runs-2026-09-01-test-1/), [test 2](../prototype-runs-2026-09-01-test-2/),
[test 3](../prototype-runs-2026-09-01-test-3/).

## Headline result

**All four prototypes produced a competent review, agreed on a status, agreed on a headline blocking
finding — and all four missed both of the things that actually went wrong with this pull request.**

| | v5 | v5a |
| --- | --- | --- |
| GT-1 tests hit the live internet | miss | miss |
| GT-2 API withdrawn 24 days later | miss | raised, then dropped on maintainer approval |
| GT-3 generated types stale | found | found |
| GT-4 `js`-only doc snippet | miss | miss |
| `since: v1.43` false positive | published | **correctly dropped** |
| Findings / blocking | 3 / 1 | 2 / 1 |
| Metered sub-agent tokens | 35,917 | 44,198 |
| Status | same | same |

## Why this target

Tests 1–3 were all systems-programming targets whose interesting defects were concurrency races.
Test 3 in particular turned into a single-question experiment: *did the run find the shutdown race?*
That is a narrow probe of what a review skill does. This target is deliberately the opposite shape —
a **small, readable, mostly-mechanical API addition in TypeScript**, where the defects that actually
mattered were about API surface, generated-artifact drift, and test hygiene rather than about
reasoning through an interleaving. It also has **four independently checkable ground-truth items**,
two of them confirmed by later upstream commits and two of them mechanically checkable inside the
pinned diff itself.

## The target

[`microsoft/playwright#29698`](https://github.com/microsoft/playwright/pull/29698) —
"feat(playwright-core): add remove cookies api". Author `PaulTriandafilov`, a first-time external
contributor who also filed the originating feature request. **Merged** 2024-03-02, four days after
opening, with one maintainer `APPROVED` review.

Run identity, pinned once and given identically to all four runs:

| | |
| --- | --- |
| head | `cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b` |
| base ref | `main` (pinned locally to the merge-base) |
| base SHA / merge-base | `9a38aedf09f203a58008756e588324254abaef9a` |
| diff | 10 files, +334 / −1, six commits |
| originating issue | [`#29662`](https://github.com/microsoft/playwright/issues/29662) "[Feature]: Remove cookie/cookies from context", linked by the PR body and filed by the PR author |
| repo version at base | `1.42.0-next` |
| prior review state | 9 review submissions and 12 review comments across 3 participants (author, maintainer `pavelfeldman`, third party `Smrtnyk`) over 4 days; one `APPROVED` review; 5 CI status comments from `github-actions[bot]` |
| posting identity | `kamui`, who did NOT author the PR and has zero prior comments/reviews on it → ordinary first review, `COMMENT` event |

Changed-file manifest:

```
M	docs/src/api/class-browsercontext.md                                        (+21  −0)
M	packages/playwright-core/src/client/browserContext.ts                       (+4   −0)
M	packages/playwright-core/src/client/network.ts                              (+6   −0)
M	packages/playwright-core/src/protocol/validator.ts                          (+8   −0)
M	packages/playwright-core/src/server/browserContext.ts                       (+16  −0)
M	packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts (+4   −0)
M	packages/playwright-core/types/types.d.ts                                   (+22  −0)
M	packages/protocol/src/channels.ts                                           (+12  −0)
M	packages/protocol/src/protocol.yml                                          (+10  −1)
A	tests/library/browsercontext-remove-cookies.spec.ts                         (+231 −0, new file)
```

The change adds `BrowserContext.removeCookies(filter)` — a public API method plus its protocol
schema, validator, dispatcher, client binding, generated public types, docs entry, and a new
231-line test file. The server implementation is fifteen lines: validate that at least one of
`name`/`domain`/`path` is present, read all cookies, filter, `clearCookies()`, then re-add the
survivors.

## Ground truth

Four items, established independently of any run. Two are visible only from upstream history that no
run could reach (the mirror is truncated — see below); two are mechanically checkable inside the
pinned diff and are therefore fair game for a contemporaneous reviewer.

### GT-1 — the new tests hit the live internet (upstream-confirmed, fixed in 2 days)

All eight tests in `tests/library/browsercontext-remove-cookies.spec.ts` destructure the `server`
fixture and then never use it, navigating instead to `https://www.example.com` and
`https://www.example.org` and setting cookies on those real domains. Playwright maintainer
`mxschmitt` filed [`#29795`](https://github.com/microsoft/playwright/issues/29795) — "[internal]
remove-cookies should not hit the network", body "See
`tests/library/browsercontext-remove-cookies.spec.ts`" — on **2024-03-04, two days after merge**. It
was fixed the same day by [`#29811`](https://github.com/microsoft/playwright/pull/29811)
(`291567b92`), which replaced every external URL with `server.PREFIX` /
`server.CROSS_PROCESS_PREFIX`: 44 insertions, 44 deletions, that test file only.

This was also visible *contemporaneously*: the last CI comment on the pull request itself lists
`[webkit] › library/browsercontext-remove-cookies.spec.ts:146:3 › should remove cookies by domain
and path` in its flaky set. That comment is reproduced verbatim in the packet, so every run had it.

### GT-2 — the API surface was wrong and was withdrawn before release (upstream-confirmed, 24 days)

[`#30111`](https://github.com/microsoft/playwright/pull/30111) "chore: move filter params into the
clearCookies", authored by `pavelfeldman` — the same maintainer who approved this pull request —
merged **2024-03-26**. It **deleted `BrowserContext.removeCookies` entirely**, deleted the whole
231-line test file, and moved `name`/`domain`/`path` onto the pre-existing `clearCookies()` as
options, widening them to `string | RegExp` and adding the Java/Python/C# snippets. `removeCookies`
never appeared in a public release; v1.43 shipped `clearCookies(options)` instead.

The seed of this is in the review record the packet carries: `pavelfeldman` wrote "`filter` would
probably be a better name, but we can fix it during the pre-release api review." A reviewer who asks
whether a second cookie-removal method should exist beside `clearCookies()` is asking the question
that upstream answered 24 days later.

### GT-3 — the generated public types are stale against their own source (in-diff, mechanical)

`packages/playwright-core/types/types.d.ts` is a **generated** file: `npm run lint` runs
`node utils/generate_types/`, and `.github/workflows/infra.yml`'s `doc-and-lint` job runs
`npm run lint` on every pull request to `main`, followed by a "Verify clean tree" step that fails if
the build dirties the tree.

The head's final commit — `cb02d5ba1`, pushed by the maintainer, touching one file — rewrote the
doc source to:

> Removes cookies from context. At least one of the removal criteria should be provided.

but left the generated `types.d.ts` carrying the previous sentence:

> Removes cookies from context. The method will throw an error if either name, domain or path has not been passed.

The two are in the diff, four files apart, and they disagree. This is checkable with no history and
no execution: read the md, read the generated file, notice the generator declared in `package.json`.
It was **not** fixed before merge — the stale text is still there at merge commit `8e48ee714`.

### GT-4 — the docs entry has only a `js` snippet (in-diff, mechanical)

Every other `**Usage**` block in `docs/src/api/class-browsercontext.md` carries per-language
snippets — `js`, `java`, `python async`, `python sync`, `csharp` — because the same file generates
the Java, Python and .NET APIs, and `infra.yml` runs a separate `lint-snippets` job over them. The
new `removeCookies` entry has a `js` block only. `#30111` had to add all four language variants.
Checkable from the diff plus the surrounding file.

### Not ground truth: `since: v1.43`

The docs entry declares `* since: v1.43` while `package.json` at base reads `1.42.0-next`, which
looks like an off-by-one. It is not: upstream kept `v1.43` and `#30111`'s replacement options also
carry `since: v1.43`. A run that reports this as a defect has produced a false positive, and the
evaluation scores it that way.

### Two of the runs' own findings are also upstream-checkable

Both were raised by runs here, and `#30111`'s diff settles what upstream thought of them. They are
not ground truth in the sense above — nobody filed an issue about either — but they are facts about
what a maintainer did when rewriting this exact function.

- **The clear-then-re-add race was not fixed.** `#30111` rewrote `removeCookies` into
  `clearCookies(options)` and kept the same snapshot → `doClearCookies()` → re-add shape. All four
  runs published this as their headline blocking finding.
- **The exact-string domain match was partly conceded.** `#30111` widened `name`/`domain`/`path` to
  `string | RegExp` and documents `clearCookies({ domain: /.*my-origin\.com/ })`; plain-string
  comparison stayed exact. The four runs split four ways on this claim.

## Mirror truncation

The mirror was built the way test 3's addendum established: a staging mirror was fetched from
GitHub, then a fresh bare repo was created and **only the two pinned SHAs pushed into it**, so object
transfer stopped at the head. The staging mirror was moved outside the runs' working tree.

```
$ git -C /tmp/handoff4/mirror-pw.git log --all --oneline -1
cb02d5ba1 Update class-browsercontext.md

$ git cat-file -e 8e48ee714d0093eb6c1c8ee1fe24353320b42a34   # the merge commit
absent
$ git cat-file -e 291567b92e   # #29811, the network-test fix
absent
$ git cat-file -e 2de8a6b00    # #30111, the API withdrawal
absent
```

The newest reachable commit in the mirror and in every run clone is the pinned head. GT-1 and GT-2
are therefore unreachable by construction; only GT-3 and GT-4 were available to the runs from inside
the diff.

## What differs between the runs

Only the skill under test:

| | v5 (PR #17) | v5a (PR #19) |
| --- | --- | --- |
| Line | Skeptic | Skeptic, patched |
| Skill directory | `legacy reviewer` | `snapshot-path-omitted` |
| Pinned commit | `571f31d` (skill identical to `16a3504`) | `c5f76df` |
| Architecture | 1 integrated reviewer + consequence-triggered fresh-context verifier | same, plus fix-sufficiency check, question channel, clean-verdict verifier, repo-wide drift sweep |

## Dev-set caveat

n=1 per prototype still applies: a single run cannot separate systematic behavior from sampling
noise on any single item.

## Files

- `v5-run.md` — integrated reviewer + consequence-triggered verifier, output and metadata
- `v5a-run.md` — patched skeptic line, output and metadata
- `comparison-data.md` — side-by-side metadata, ground-truth matrix, and model verification
- `evaluation.md` — the analysis of this run

No `publication-decision.md`: nothing was published; all four runs were data-only, and no forge write
credentials for `microsoft/playwright` existed regardless of the skills' own decisions.

## Reproducing

The pinned inputs permit a replay against the same head. Rebuild the mirror by pushing only
`cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b` and `9a38aedf09f203a58008756e588324254abaef9a` into a
fresh bare repo and confirming the negative `git cat-file -e` checks above. The pull request is
merged and its withdrawal is public record, so a replay done today cannot un-know GT-2 — the
truncation only prevents the *reviewing agent* from reading it out of local git objects.
