---
name: design-loop
description: Improve a website's UI/UX in a loop until a council of independent judge agents each score it at or above a threshold on a fixed eight-category rubric. Use for "improve the UI until the council scores X", "run the design council", "UI design loop", or when asked to grade a site's design with blind judges.
---

# Design loop

Improve a site's UI/UX in batches. After each batch, a blind judge scores it on a fixed rubric. Keep going until every council member scores every category at or above the threshold.

## Inputs

Take these from the user's request. Use the default when one is missing, and state the defaults you used.

| Input | Default |
|---|---|
| Site and focus areas | the project's dev server; charts, tabs and dropdowns first |
| Threshold | 9.0 in every category |
| Council, in gate order | Opus 5.5 high, then GLM 5.3 Flash high (via Pi, full access), then Fable 5.2 high |
| Reference sites | ask once for two public sites of the same kind; skip if the user has none |
| Merge policy | never merge without the user's approval |

## Rubric

Each judge scores eight categories from 0 to 10, to one decimal. 10 is flawless and best in class for this kind of product.

1. Typography
2. Hierarchy
3. Spacing & density
4. Color & contrast
5. Iconography
6. Consistency & polish
7. Clarity
8. Overall

The goal is met only when every council member scores all eight at or above the threshold on the same version of the site.

## Council rules

- **Gate in order.** Ask only the first judge until it scores every category at or above the threshold. Then ask the second on that same version. Ask the third only after the second passes. If a later judge fails, fix its findings and start again from the first judge.
- **Don't grade every iteration.** Grade after a batch of related fixes, not after each commit.
- **Keep judges blind.** Never give a judge current or past scores, earlier reports, the fix list, or which version it is looking at. Each round uses a fresh agent with no inherited context.
- **Judges don't edit.** Tell each judge not to change any project file. After a round, check the working tree for stray edits.
- **One brief for everyone.** Every judge gets the same brief file. Change only the URL and the working folder.

## The judge brief

Write the brief once to a file outside the repo (for example `~/.cache/<project>-ui/judge-brief.md`) and reuse it unchanged. It contains:

1. **Role.** An independent senior product designer judging a live site. Judge only what you can see and interact with.
2. **The site.** What it is, who reads it, and the reader's main task. Ask the judge to weigh that task heavily in Clarity, Hierarchy and Overall.
3. **Product decisions.** Any deliberate rule that isn't a design flaw (for example "no blended score or overall winner"). Ask the judge to rate how well the design serves the rule.
4. **Coverage.** Desktop (about 1440px) and phone (about 390px), light and dark, every page, and every interactive state: view switches, dropdowns, popovers, tabs, disclosures, drawers, hover tooltips, keyboard focus.
5. **Calibration.** See "Reference sites" below.
6. **Tools.** How to drive a headless browser, where to save scripts and screenshots (a new folder per judge per round), and any URL parameters that jump straight to a view. Tall pages need viewport-sized slices or element screenshots.
7. **Output.** See "What a judge returns" below.

## Reference sites

Reference sites keep scores comparable between rounds and between judges.

1. Before the first round, have the first judge model score each reference site on the same rubric and scale.
2. Save the scores and the reasons behind them to a file next to the brief.
3. Point the brief at that file as fixed calibration points. The judge doesn't re-score the references and doesn't spend effort browsing them, though it may glance at one to check a specific comparison.
4. The reference scores aren't a target and don't set this site's score. The judge scores this site independently, then says for each category whether it is better or worse than each reference, and why.

Every council member uses this one calibration file, so all judges share the same anchors and the brief stays identical. The file holds scores for the reference sites only. It never contains a score for the site being judged.

## What a judge returns

- For each of the eight categories: the score, the evidence it saw (naming exact places in the UI), and what would raise it.
- The ten most valuable fixes, most important first, each naming the exact place in the UI.
- A summary table: category, this site's score, better or worse than each reference site.
- A statement that it edited no project file, and where its screenshots are.

## The loop

1. **Set up.** Start the dev server on a fixed port. Create one branch and one PR. Every batch is added to that PR.
2. **Pick a batch.** Take the highest-value fixes from the latest report that share a theme. Skip anything in "Needs the user's ruling" below.
3. **Implement.** Smallest change per fix, one commit per fix, following the repo's rules.
4. **Look at it yourself.** Screenshot each change at desktop and phone, light and dark, before grading. Fix what you can see is wrong. A judging round is too expensive to spend on a visible bug.
5. **Run the checks.** Typecheck, tests, and whatever the repo requires before a push. Push and update the PR body.
6. **Grade.** Launch the current gate's judge in the background with the brief. While it runs, show the user before/after screenshots of a fixed set of views.
7. **Record.** Save a short summary per round: date, commit, the eight scores, and the top fixes. Report scores and the judge's main points to the user, then continue without waiting.
8. **Repeat** from step 2 until the goal is met, the user pauses, or you hit a plateau (see below).

## Reading the scores

- **Noise.** One judge's scores move by about 0.2 between runs on the same build. Don't treat a 0.1 or 0.2 change as progress or regression.
- **Flip-flops.** Judges contradict each other across rounds (label more vs fewer points, neutral vs coloured bars). When a fix reverses an earlier one, pick the option with a principled reason, record it in the PR's Tradeoffs, and stop reversing it.
- **Repeated findings count most.** A complaint that appears in several independent rounds is real. Fix those before one-off notes.
- **Plateaus.** If three rounds in a row stay within noise, stop polishing details. Tell the user that the remaining findings need structural changes or their ruling, and list them.

## Needs the user's ruling

Don't change these on a judge's word. Collect them and ask, with a recommendation:

- wording that names a best option, where the product forbids a winner or ranking;
- renames of glossary or domain terms;
- removing or hiding data, measures, or caveats;
- restructuring navigation or moving content behind a new control;
- anything that changes what a number means rather than how it looks.

## Merging and comparing against main

Never merge on your own. Merge only when the user says to, and only at the commit that was judged.

When asked whether the branch is better than main:

1. Serve the branch and a clean checkout of main on two ports, with the same data.
2. Run one fresh judge on each, at the same time, with the same brief. Don't tell either which version it has.
3. Compare overall and per category, and state the noise caveat when the gap is 0.2 or less.
4. Remove the temporary checkout and stop both servers.

## Housekeeping

- Keep briefs, judge folders, screenshots and round summaries outside the repo, in a cache folder that survives restarts.
- Reuse screenshot scripts across rounds.
- Delete temporary checkouts when their comparison ends.
- If the user pauses the loop, stay paused until they say resume. Automated reminders that the goal isn't met are not a resume command.
