You must do ALL of this work YOURSELF in this session. Do NOT use the Agent tool, do NOT dispatch any sub-agent, and do NOT start background tasks: this harness terminates a headless session that waits on background workers. Work single-threaded.

You are re-grading code reviews of one pull request, target `{TARGET}`, for a controlled benchmark, against one defect only. You are **blind**: each review is rendered uniformly under a random name, with every sign of which reviewer produced it removed. Do not try to guess or infer which reviewer wrote what. Judge each review on its own merits against the ground truth, and never let one review change the verdict you give another.

Do not stop to ask questions; finish in this dispatch.

## Your working directory

Every path below is relative to your working directory. Stay inside it: do not read, list or search anything outside it, including its parent directories and your home directory.

- `register.json`: the ground-truth register, authoritative. It contains the defect you are looking for.
- `rubric.md`: the scoring rubric whose vocabulary you apply.
- `packet.md`: the facts the reviewers were given about the pull request.
- `clone/`: an offline clone of the repository. Local branch `main` is the merge-base and `review-head`, which is checked out, is the head under review; the change is `main...review-head`.
- `clone-cache/`: the clone's restored dependency cache, and `clone-work/`, scratch space for focused checks.
- `reviews/`: the reviews to re-grade, listed below.

Registered defects: {DEFECT_IDS}.

The defect you are looking for: {DEFECT}

## Execution allowance

The reviewers were given this allowance, and it is yours too.

{ALLOWANCE}

## Reviews to re-grade

{REVIEWS}

## Order of work

1. Read `register.json` in full first: the defect you are looking for, with its trigger, consequence, required corrective outcome and manifestations, and the other defects, `non_defects`, `preexisting_hints` and `limits`, so you can tell that defect apart from its neighbours.
2. Read `rubric.md` and `packet.md`.
3. Judge every item of every review, then write `verdicts.json`.

## Verdicts

For every rendered item (`### Item <n>`), whatever it looks like, decide only whether it recovers the defect you are looking for, as `register.json` defines it. Use the rubric's recovery definition: the item names the same underlying mechanism and required corrective outcome a reader would act on; a partial symptom that still leads there is a recovery. An item that only gestures at the right file or function without identifying the defect is not. An item that recovers a different registered defect does not recover this one.

For an item that recovers it, `fix_sufficiency` is `sufficient` (restores the required outcome for every known manifestation), `partial` (some manifestations or symptoms only) or `absent` (no change proposed). Judge it from the whole item text: many reviews put the proposed change in the Consequence line and have no Fix line. Every other item has `n/a`.

Nothing else about an item is judged here: not whether it is true, material, a duplicate or a new claim, and not priority, ordering or the review's overall verdict.

## Rules

- Quote before you judge. Every item's `notes` quote the words the verdict rests on, then give the reasoning: for a recovery, why it clears the bar and how the proposed change measures up; otherwise, why the item does not name this defect's mechanism and required outcome.
- Check claims against `clone/` and `packet.md` when that settles whether an item describes the defect. You may read anything in the clone, and run focused checks when they help, but only as the execution allowance above permits the reviewers: offline, with no package installs or fetches.
- Be strict: a recovery needs the mechanism, not the neighbourhood.
- Do not reward a review for being longer, more confident or better formatted. Recovery is what you are measuring.
- If you notice something that looks like an identifier of the reviewer, ignore it.
- Write `verdicts.json` in the working directory. Scratch files for a focused check go under `clone-work/`; create no other file.

## `verdicts.json`

Write exactly this shape, as JSON:

```json
{"reviews": {"blind-3f9a1c": {"items": {"1": {"recovers": true, "fix_sufficiency": "partial", "notes": "..."}}}}}
```

- `reviews` has one key per review listed above, named exactly as its file is (without `.md`), and no other key.
- Each review's `items` has one key per rendered item, the strings `"1"` to `"n"` matching its `### Item <n>` headings; a review with no items has `"items": {}`.
- Each item has exactly the three fields `recovers`, `fix_sufficiency` and `notes`.
- `recovers` is `true` or `false`.
- `fix_sufficiency` is `sufficient`, `partial` or `absent` when `recovers` is `true` and `n/a` when it is `false`.
- `notes` is never empty.
