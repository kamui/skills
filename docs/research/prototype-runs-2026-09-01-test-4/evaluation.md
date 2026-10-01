# Evaluating four agentic code-review runs against a withdrawn API

## Conclusion

On a small, readable, mostly-mechanical TypeScript API addition, all four prototypes produced a
competent review, agreed on a status, agreed on a headline blocking finding — and **all four missed
both of the things that actually went wrong with this pull request.** The one ground-truth item that
was mechanically checkable inside the diff, a stale generated file, separated them: three published
it and one found it, wrote it down, and argued itself out of reporting it.

Ranked on this target:

The spread between best and worst is narrow, and every ordering above rests on n=1.

## Method and evidence quality

The controls are the strongest in the program to date. One cohort, model verified from transcripts
for all nineteen agents rather than trusted, mirror truncated at the pinned head with negative
object checks repeated inside each clone, an identical phase-1 packet, and per-run sandboxes with
self-disclosure required. Every run confirmed it read no history past the head and executed nothing
against the repository.

Three caveats bound what follows.

**n=1 per prototype.** Nothing here separates systematic behavior from sampling noise on any single
item.

**Ground truth here is softer than test 3's.** Test 3 had a production hang and a revert. Here, GT-1
and GT-2 are maintainer actions taken days and weeks later — an internal test-hygiene issue and an
API-shape reversal. Both are unambiguous facts about what upstream did. Neither is a crash.

### GT-1: the tests hit the live internet

All eight tests in the new 231-line file destructure the `server` fixture and never use it, then
navigate to `https://www.example.com` and `https://www.example.org` and set cookies on those real
domains. Two days after merge, maintainer `mxschmitt` filed
[`#29795`](https://github.com/microsoft/playwright/issues/29795) — "[internal] remove-cookies should
not hit the network" — and it was fixed the same day.

The common failure is a framing one. Each run treated the test file as *evidence about the
implementation* — does it prove the requirements, does it exercise the race — and never as
*changed code with its own standards*. The runs that noticed the flake reached for it as weak
corroboration of the concurrency finding rather than asking why a cookie test would be flaky at all.
None asked what every other test in `tests/library/` does, which would have surfaced the `server`
fixture convention immediately.

None of the four skills has a rule that says: a new test file is code under review, and repository
test conventions are a standard it can violate. That is a gap in all four designs, not a defect in
one run.

### GT-2: the API was the wrong shape and was withdrawn

Twenty-four days after merge, [`#30111`](https://github.com/microsoft/playwright/pull/30111) —
authored by `pavelfeldman`, the same maintainer who approved this pull request — deleted
`BrowserContext.removeCookies` outright, deleted the whole test file, and moved `name`/`domain`/
`path` onto the pre-existing `clearCookies()` as options. `removeCookies` never shipped.

**No run published it.** Two came close, and how they came close is the interesting part.

**v5** checked `CONTRIBUTING.md`'s API guidelines — including its "avoid adding 'sugar' API" rule —
and recorded the change as **compliant**.

**v5a** got all the way there. Its ledger item A5 states the case exactly: the method "may be
'sugar' API per `CONTRIBUTING.md`'s API guidelines… since it is fully expressible as existing
`cookies()`+`clearCookies()`+`addCookies()`." It then dropped it, and the stated reason is worth
quoting because it is a designed behavior working as intended and producing the wrong answer:

> The maintainer reviewed and approved this exact feature ("Looks great!", then APPROVED) with full
> knowledge of its implementation; gate 6 (unintentional) fails — this is litigated, accepted
> repository policy application, not an oversight.

The gate is sensible: don't re-litigate what a maintainer has consciously accepted. On this target
it fires on the one item where the maintainer's own acceptance was the thing that turned out to be
wrong — and the packet contained the tell, in the same maintainer's words: "`filter` would probably
be a better name, but **we can fix it during the pre-release api review**." A reviewer holding that
sentence has evidence that the API shape was explicitly deferred, not settled.

### GT-3: the generated types are stale — the discriminator

`packages/playwright-core/types/types.d.ts` is generated from `docs/src/api/*.md`.
`.github/workflows/infra.yml`'s `doc-and-lint` job runs `npm run lint` — which runs
`node utils/generate_types/` — on every pull request, then fails if the tree is dirty. The head's
final commit rewrote the md description and never regenerated the types, so the two disagree inside
the diff, four files apart, and the job would have been red.

> Any drift between this file and its source docs is caught there, not by manual review… That's
> exactly the class of thing the clean-tree check exists to catch, so it isn't reported as a
> candidate.

The reasoning is coherent and wrong in a specific way: it treats "a tool would catch this" as
equivalent to "this is caught," on a diff where the tool demonstrably had not caught it. The finder
had the evidence of the miss in its hands — the drift was right there — and deferred to the process
that produced it anyway.

### GT-4: the docs carry only a `js` snippet

Every other `**Usage**` block in `class-browsercontext.md` carries js/java/python/csharp snippets,
because the same file generates the Java, Python and .NET APIs and CI lints those snippets
separately. The new entry has `js` only; `#30111` had to add all four. **No run raised it.** Two
runs checked the doc entry's alphabetical placement in that same file and found it correct, so the
file's local conventions were being examined — just not this one.

## Status is a poor discriminator, for the fourth time

Four runs, four `Changes Requested (advisory)`. Across tests 3 and 4 that is ten of ten runs
deriving the same status on two different targets. Status carries no information about whether a
run found the thing that mattered, and the program should stop treating it as an output worth
comparing.

## Unanimity is not accuracy

Upstream rewrote this exact function 24 days later and **kept the race.** `#30111`'s `clearCookies`
is still snapshot → `doClearCookies()` → re-add.

## The false positive

That is an evidentiary gate producing the right result on a claim the run could not resolve — the
same gate that, applied to maintainer approval in GT-2, produced the wrong one. The gate is not the
problem; what counts as terminal evidence is.

Three of four runs publishing the same wrong P3 also says something about the value of low-priority
findings: all three treated a version tag they could not verify as worth a reviewer's attention.

## What each prototype should take from this

**v5** — cheapest and correct on GT-3 with the sharpest framing. Its gap is the absence of a
question channel: it had the domain-matching doubt, reframed it, and dropped it. v5a had the same
doubt and published it as a question. That single mechanism is the difference between the two runs'
best moments.

**v5a** — the strongest run here, and its two weaknesses are both in the same gate. Treating
maintainer approval as terminal closed the one door to GT-2 that any run got near. Consider
narrowing it: approval of *unreleased public API surface* is provisional, and an explicit deferral
in the review record ("we can fix it during the pre-release api review") should reopen rather than
close the question.

**All four** — add a rule that a new or changed test file is code under review in its own right,
with the repository's test conventions as the standard. GT-1 was missed four times out of four by
runs that had all read the file.

## Limits
