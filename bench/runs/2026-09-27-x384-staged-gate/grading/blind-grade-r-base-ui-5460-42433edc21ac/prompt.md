You must do ALL of this work YOURSELF in this session. Do NOT use the Agent tool, do NOT dispatch any sub-agent, and do NOT start background tasks: this harness terminates a headless session that waits on background workers. Work single-threaded.

You are grading code reviews of one pull request, target `r-base-ui-5460`, for a controlled benchmark. You are **blind**: each review is rendered uniformly under a random name, with every sign of which reviewer produced it removed. Do not try to guess or infer which reviewer wrote what. Grade each review on its own merits against the ground truth, and never let one review change the verdict you give another.

Do not stop to ask questions; finish in this dispatch.

## Your working directory

Every path below is relative to your working directory. Stay inside it: do not read, list or search anything outside it, including its parent directories and your home directory.

- `register.json`: the ground-truth register, authoritative.
- `rubric.md`: the scoring rubric whose vocabulary you apply.
- `packet.md`: the facts the reviewers were given about the pull request.
- `clone/`: an offline clone of the repository. Local branch `main` is the merge-base and `review-head`, which is checked out, is the head under review; the change is `main...review-head`.
- `clone-cache/`: the clone's restored dependency cache, and `clone-work/`, scratch space for focused checks.
- `reviews/`: the reviews to grade, listed below.

Registered defects: GT-r1, GT-r2.

## Execution allowance

The reviewers were given this allowance, and it is yours too.

Read the clone and the pinned skill. Focused commands may run only as the target allowance states, offline, with a five-minute limit per command. Put scratch files in the attempt work directory or its private temporary directory. Dependency-cache and artifact writes remain inside the attempt. Never change the clone or request access to another attempt or the host filesystem. Unavailable paths and connections stay unavailable; do not retry outside the sandbox. Focused test execution is permitted on this target, offline: dependencies are already installed in the clone (untracked and ignored; leave them alone). Run the existing jsdom unit tests with the clone's own binary from the clone root, for example `TZ=UTC VITEST_ENV=jsdom ./node_modules/.bin/vitest run --project @base-ui/react packages/react/src/field/control/FieldControl.test.tsx` (a few seconds). A scratch test can run from the work directory without touching the clone: in the work directory, link `<clone>/packages/react/node_modules` as `node_modules`, write a `vitest.config.mts` that exports a plain object with `test: { environment: 'jsdom', include: ['*.test.tsx'] }` and `resolve.alias` entries mapping `@base-ui/react/<name>` to `<clone>/packages/react/src/<name>/index.ts` and `@base-ui/utils/<name>` to `<clone>/packages/utils/src/<name>`, put the test beside it, and run `TZ=UTC <clone>/node_modules/.bin/vitest run --root <work directory>`; `@testing-library/react` resolves through the link. Five minutes per command, a selection at most once per flag set; nothing may be added to or changed in the clone, and no network call of any kind is available (pnpm and npx cannot reach a registry).

Unavailable: network; the registry (pnpm, npx); browsers, so the chromium test mode and anything settled by looking at rendered output

Here `<clone>` is `clone/`, `<cache>` is `clone-cache/` and the work directory is `clone-work/`, all in your working directory; from inside `clone/` they are `.`, `../clone-cache` and `../clone-work`.

## Reviews to grade

- `reviews/blind-3f410f.md`: 1 item
- `reviews/blind-903847.md`: 1 item

## Order of work

1. Read `register.json` in full first: every defect with its required corrective outcome, and `non_defects`, `preexisting_hints`, `limits` and `clean_basis`. The `non_defects` list is the plausible objections that are **not** material defects; `clean_basis`, when present, is why a clean target is clean.
2. Read `rubric.md` and `packet.md`.
3. Grade every item of every review, then write `verdicts.json`.

## Verdicts

Every rendered item (`### Item <n>`) gets exactly one `assignment`, whatever it looks like. Questions and observations are items too; they are usually `non-material`.

- `defect:<id>`: the item recovers the registered defect `<id>`. It names the same underlying mechanism and required corrective outcome a reader would act on; a partial symptom that still leads there is a recovery. An item that only gestures at the right file or function without identifying the defect is not.
- `false-finding`: the item asserts a defect or consequence the evidence contradicts, or that lacks the support it needs after you check it. A fabricated material consequence attached to a true fact is a false finding. Being unhelpful is not being false.
- `non-material`: an accurate fact below the finding threshold: cleanup, hygiene, style, an observation, a question, or a true but inconsequential remark.
- `unresolved`: you cannot settle the item from the register, the packet and the clone. Say what would settle it; do not guess.

For each `defect:` item, `fix_sufficiency` is `sufficient` (restores the required outcome for every known manifestation), `partial` (some manifestations or symptoms only) or `absent` (no change proposed). Judge it from the whole item text: many reviews put the proposed change in the Consequence line and have no Fix line. Every other item has `n/a`.

A plausible, specific, material claim that is not in the register and that you cannot refute is `unresolved` with a `candidate` id, and gets an entry in `new_candidates`; these go to a separate adjudication. Several items, in one review or across reviews, that make the same new claim share one candidate.

`duplicate_group` joins items within one review that make the same underlying claim: give them the same short label (`g1`, `g2`, ...). Use `null` for an item with no duplicate in its review. Never group items across reviews.

Do not judge priority, ordering or the review's overall verdict; those are derived afterwards from the reviewers' own labels.

## Rules

- Quote before you judge. Every item's `notes` quote the words the verdict rests on, then give the reasoning: for a recovery, why it clears the bar and how the proposed change measures up; for a `false-finding`, the evidence that refutes it (file and line in `clone/`, or the register or packet passage); for `non-material`, why it is below the threshold; for `unresolved`, what would settle it.
- Check claims against `clone/` and `packet.md`. You may read anything in the clone, and run focused checks when they help, but only as the execution allowance above permits the reviewers: offline, with no package installs or fetches.
- Be strict about `false-finding`: say what refutes the claim.
- Do not reward a review for being longer, more confident or better formatted. Recovery and truth are what you are measuring.
- If you notice something that looks like an identifier of the reviewer, ignore it.
- Write `verdicts.json` in the working directory. Scratch files for a focused check go under `clone-work/`; create no other file.

## `verdicts.json`

Write exactly this shape, as JSON:

```json
{"reviews": {"blind-3f9a1c": {"items": {"1": {"assignment": "defect:GT-x1", "duplicate_group": null,
   "fix_sufficiency": "partial", "candidate": null, "notes": "..."}}}},
 "new_candidates": [{"id": "NC-1", "claim": "...", "evidence": "...", "confidence": "...", "would_settle": "...",
   "items": [{"review": "blind-3f9a1c", "item": 2}]}]}
```

- `reviews` has one key per review listed above, named exactly as its file is (without `.md`), and no other key.
- Each review's `items` has one key per rendered item, the strings `"1"` to `"n"` matching its `### Item <n>` headings; a review with no items has `"items": {}`.
- Each item has exactly the five fields `assignment`, `duplicate_group`, `fix_sufficiency`, `candidate` and `notes`.
- `assignment` is `defect:<id>` with `<id>` from `register.json`, or `false-finding`, `non-material` or `unresolved`.
- `fix_sufficiency` is `sufficient`, `partial` or `absent` on a `defect:` item and `n/a` on every other item.
- `candidate` is `null` except on an `unresolved` item that raises a new candidate, where it is that candidate's `id`.
- `notes` is never empty.
- `new_candidates` is a list, `[]` when there are none. Each entry has exactly `id` (`NC-1`, `NC-2`, ...), `claim`, `evidence` (what you checked and found), `confidence`, `would_settle`, and `items`: every item whose `candidate` names it, as `{"review": "<name>", "item": <n>}` with `<n>` a number, and no other item.
