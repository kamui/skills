# Evaluating four agentic code-review runs against a withdrawn API

**2026-09-03.** Analysis of the four runs in this directory against
[`microsoft/playwright#29698`](https://github.com/microsoft/playwright/pull/29698). Raw data is in
[v2](v2-run.md), [v2a](v2a-run.md), [v5](v5-run.md), [v5a](v5a-run.md); the side-by-side tables are
in [comparison-data.md](comparison-data.md); the pinned target, ground truth and controls are in
[README.md](README.md).

This is the program's first **single-cohort** comparison — one model, one harness, one packet, one
session — and the first **holdout** target for the patched prototypes v2a and v5a, which were
designed after their authors saw tests 1–3.

## Conclusion

On a small, readable, mostly-mechanical TypeScript API addition, all four prototypes produced a
competent review, agreed on a status, agreed on a headline blocking finding — and **all four missed
both of the things that actually went wrong with this pull request.** The one ground-truth item that
was mechanically checkable inside the diff, a stale generated file, separated them: three published
it and one found it, wrote it down, and argued itself out of reporting it.

Ranked on this target:

1. **v5a** — fewest findings (2), both real; the only run to avoid the false positive; the only run
   to route a genuinely uncertain claim to a question instead of publishing or dropping it; the only
   run to name the target's real design problem at all, even though it dropped it. Cheapest
   metered fan-out. Its restraint is the reason it scores well, and the same restraint is why it
   dropped the design problem.
2. **v5** — same architecture, one pass, lowest cost of the four, correct on GT-3 with the sharpest
   framing of any run. Loses to v5a on the false positive and on having no question channel to
   route the domain-matching doubt into, so it dropped it instead.
3. **v2a** — published GT-3, recovering a defect its own unpatched ancestor discarded. Costs the
   most of the four. Its Requirements axis returned a clean *Passed* on a pull request whose API
   was deleted 24 days later, and it flatly acquitted the domain-matching claim that upstream later
   partially conceded.
4. **v2** — most findings (4) and the only run to publish the domain-matching defect at
   `must-fix`, which upstream partially vindicated. But it is also the only run to miss GT-3, and
   it published the false positive. Highest finding count, lowest precision.

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

**A rate limit split the Panel-line runs.** v2 and v2a completed Find, were killed, and had Verify
and Publish executed by fresh orchestrators holding the same packet and the same verbatim finder
reports. The discontinuity sits where the architecture already imposes a context boundary, so the
substitute orchestrators were not information-poorer in any way that should matter — but this is a
real difference from v5 and v5a, which ran single-pass, and it is why their finder-phase costs are
carried forward from the first attempt.

**Ground truth here is softer than test 3's.** Test 3 had a production hang and a revert. Here, GT-1
and GT-2 are maintainer actions taken days and weeks later — an internal test-hygiene issue and an
API-shape reversal. Both are unambiguous facts about what upstream did. Neither is a crash.

## Ground truth, and what everyone missed

### GT-1: the tests hit the live internet

All eight tests in the new 231-line file destructure the `server` fixture and never use it, then
navigate to `https://www.example.com` and `https://www.example.org` and set cookies on those real
domains. Two days after merge, maintainer `mxschmitt` filed
[`#29795`](https://github.com/microsoft/playwright/issues/29795) — "[internal] remove-cookies should
not hit the network" — and it was fixed the same day.

**No run raised it.** This is the most uncomfortable result in the test, because it was not a
subtle inference: it is visible on the face of the file, the fixture sitting unused in every
signature is a static-analysis-grade smell, and three of the four runs had the WebKit flake on that
exact spec file quoted verbatim in their packet. Every run read the file in full. Every run wrote a
manifest row about it. v2a's row reads "Logic of each test… verified against the implementation and
found correct. **No defect.**"

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

**This is the most transferable finding of the round.** Maintainer approval is being treated as
terminal evidence that a design question is closed. It is not: it is evidence about one person's
judgment at one moment, and on unreleased API surface it is frequently provisional. A gate that
reads approval as closure will systematically miss exactly the class of defect where the approval
was the mistake — which, on new public API, is a common class. v2a's Requirements axis reached the
same destination by a different road, returning *Passed*, 7/7 requirements met, 0 questions, on a
pull request whose API was about to be deleted.

### GT-3: the generated types are stale — the discriminator

`packages/playwright-core/types/types.d.ts` is generated from `docs/src/api/*.md`.
`.github/workflows/infra.yml`'s `doc-and-lint` job runs `npm run lint` — which runs
`node utils/generate_types/` — on every pull request, then fails if the tree is dirty. The head's
final commit rewrote the md description and never regenerated the types, so the two disagree inside
the diff, four files apart, and the job would have been red.

**v2a, v5 and v5a published it. v2 did not — and v2 is the only run that explicitly examined it.**

v2's Code finder marked `types.d.ts` and `channels.ts` *ignored — generated artifact*, quoted both
conflicting sentences in the manifest row, and wrote:

> Any drift between this file and its source docs is caught there, not by manual review… That's
> exactly the class of thing the clean-tree check exists to catch, so it isn't reported as a
> candidate.

The reasoning is coherent and wrong in a specific way: it treats "a tool would catch this" as
equivalent to "this is caught," on a diff where the tool demonstrably had not caught it. The finder
had the evidence of the miss in its hands — the drift was right there — and deferred to the process
that produced it anyway.

The three runs that got it right all did so by treating the generated file as reviewable and
comparing it against its source. v2a used `addCookies`'s JSDoc as a **control**, establishing that
generated blocks normally match verbatim, then showing this one doesn't — a clean falsification
structure. v5 framed it most precisely, naming the mechanism: the last commit "edited the markdown
without regenerating types." v5a framed it as doc drift between two shipping surfaces.

That v2 → v2a recovery is the clearest evidence in this test that the Panel line's doc-sync patch
does something on holdout data. It is one observation.

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

The axis outcomes underneath it do carry information, and they disagree: on the same diff and the
same issue, v2 returned Requirements *Waiting for information* and v2a returned Requirements
*Passed*. That divergence between two runs of the same architecture, one patched, is worth more
attention than the identical top-line status.

## Unanimity is not accuracy

All four runs published the clear-then-re-add race as their headline blocking finding — v2 and v5a
at P1, v2a and v5 at P2. It is a real defect, well argued in all four, and both Skeptic-line
verifiers independently corrected the proposed remedy in the same way after establishing that
Firefox and WebKit expose no scoped delete primitive.

Upstream rewrote this exact function 24 days later and **kept the race.** `#30111`'s `clearCookies`
is still snapshot → `doClearCookies()` → re-add.

Meanwhile the item the four runs disagreed about most sharply — whether `filter.domain ===
cookie.domain` is too narrow — is the one upstream partially conceded, widening the filter fields to
`string | RegExp` and documenting `clearCookies({ domain: /.*my-origin\.com/ })`. The four
dispositions were: v2 published it at P1 `must-fix` with an RFC 6265 argument and got it confirmed;
v5a routed it to a published question naming the experiment that would settle it; v5 reframed it as
case-sensitivity and dropped it as "expected exact-match behavior"; v2a acquitted it as resting "on
an unstated assumption."

Two lessons. First, consensus across architectures measures shared priors, not correctness — the
unanimous finding is the one upstream declined to act on. Second, **v5a's question channel produced
the best-calibrated output of any run on this item**: it neither over-claimed like v2 nor buried the
doubt like v2a and v5, and it published the specific experiment that would resolve it. That is the
correct handling of a claim that static review genuinely cannot settle.

## The false positive

`since: v1.43` against a base of `1.42.0-next` looks like an off-by-one and is not; upstream kept
`v1.43` and `#30111`'s replacement options carry the same tag. **v2, v2a and v5 all published it at
P3. v5a alone dropped it**, and its reasoning is the point: it recorded the claim as "plausible,
ordinary release-boundary practice… not proven wrong," and declined to publish because it could not
be established, not because v5a knew the answer.

That is an evidentiary gate producing the right result on a claim the run could not resolve — the
same gate that, applied to maintainer approval in GT-2, produced the wrong one. The gate is not the
problem; what counts as terminal evidence is.

Three of four runs publishing the same wrong P3 also says something about the value of low-priority
findings: all three treated a version tag they could not verify as worth a reviewer's attention.

## Cost

This is the program's first clean cost comparison, and the architectures separate cleanly. The Panel
line spent 198k and 223k metered sub-agent tokens across three agents; the Skeptic line spent 36k
and 44k across one. The meters are not measuring the same thing — v5 and v5a do their primary review
in the unmetered top-level agent — but the *shape* difference is real: three reviewing agents against
one. Self-reported tool uses, which are on the same basis for all four, narrow the gap to 110/~123
against ~63/~100.

What the extra Panel-line spend bought on this target: v2 produced two extra findings, one of which
was right and one of which was wrong, plus two questions. v2a produced the same GT-3 hit that both
cheaper Skeptic runs also got, plus two extra observations, and a Requirements axis that returned
*Passed*. On this target the fan-out did not buy recall.

## What each prototype should take from this

**v2** — the generated-artifact acquittal is the finding. "A tool would catch this" is not a
disposition; it is a hypothesis that the diff in front of the reviewer falsifies. Any rule that lets
a finder mark a changed file *ignored* needs a carve-out for the case where the file's own content
contradicts its source.

**v2a** — the doc-sync patch works on holdout data; that is real and worth keeping. The exposure is
the Requirements axis returning a clean *Passed* on an API that was withdrawn, with no question
raised. An axis that can only return met/not-met/unverifiable against a one-paragraph issue will
return *Passed* on almost any competent implementation of a bad idea.

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

Single run per prototype on a single target. The Panel-line runs had a context discontinuity the
Skeptic-line runs did not. GT-1 and GT-2 are maintainer judgments, not crashes, and a reasonable
reviewer could have merged this pull request without raising either. The rankings above would move
on a second sample; the mechanism-level observations — the generated-artifact acquittal, the
approval-as-closure gate, the question channel's calibration, the four-way test-file miss — are the
parts most likely to replicate, and the parts worth acting on.
