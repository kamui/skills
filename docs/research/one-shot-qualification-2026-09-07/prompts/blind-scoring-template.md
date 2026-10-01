You must do ALL of this work YOURSELF in this session. Do NOT use the Agent tool and do NOT dispatch any sub-agent: this harness terminates a headless session that waits on background workers. Work single-threaded.

You are scoring code reviews for a controlled evaluation. You are **blind**: the reviews below have had every identifier of which reviewer produced them redacted, and you must not try to guess or infer it. Score each one on its own merits against the ground truth, and never let a comparison between reviews change a score you already justified.

Write your scorecard to `{OUT}`. Do not stop to ask questions; finish in this dispatch.

## Inputs

- **Ground-truth register** (authoritative): `{REGISTER}`. Read it in full first. It defines the material defects `{DEFECT_IDS}` on this target, the required corrective outcome for each, the plausible objections that are **not** material defects, and, for a clean target, the surface a correct review must not assert as a defect.
- **The reviews to score**, each a rendered review payload exactly as it would have been published:
{PAYLOADS}
- **The target's own source**, if you want to check a claim yourself: a clone is at `{CLONE}`, with the reviewed head checked out as `review-head` and the base branch pinned at the merge-base. It is offline. You may read anything in it. You may also read the packet the reviewers were given: `{PACKET}`.

## Definitions you must apply exactly

- A **material defect** is an actionable correctness, security, data-integrity, compatibility, meaningful-performance or explicit-requirement failure with a demonstrated consequence. Only the register's `GT-` entries count. Nothing else on this target is a material defect unless you newly adjudicate it as one under "New candidates" below.
- A review **recovers** a defect when its published findings state that defect's claim with enough specificity that a reader would act on the right thing. Partial symptoms count as recovery if they identify the same underlying defect and would lead to the same required corrective outcome. A finding that merely gestures at the right file or function without identifying the defect does **not** recover it.
- **Fix sufficiency**: for each recovered defect, classify the review's proposed change as `sufficient` (restores the required outcome for all known manifestations), `partial` (addresses some manifestations or symptoms only), `absent` (no fix proposed), or `unresolved`.
- A **false finding** is a published finding whose asserted defect or consequence is contradicted by the evidence or lacks the support it claims, after you check it. Being unhelpful is not the same as being false. A true fact that demands an unjustified blocking action is an **action error**, not a false finding — record it separately.
- **False clean**: the review explicitly returns Approved / no material defects on a target that has at least one material defect. An honest statement of incompleteness or uncertainty is not false clean.
- Questions, hygiene suggestions, observations and style notes **cannot** recover a defect. Score them in their own columns.

## For each review, report

1. **Recovered defect IDs** and, for each, the exact quoted sentence(s) that recover it, plus your reasoning for why it clears the specificity bar.
2. **Missed defect IDs.**
3. **Fix sufficiency** per recovered defect, with the quoted proposed change.
4. **Findings that are not in the register**: for each, quote it and classify as `true but not material` (a real fact below the material bar), `false finding` (contradicted or unsupported — say what contradicts it), or `new candidate` (a plausible, specific, material claim not in the register that you cannot refute). Check each against the source before classifying. Be strict about `false finding`: quote the evidence that refutes it.
5. **Action/severity errors**: a true finding given a priority or required action the evidence does not support.
6. **Questions, observations, hygiene items**: count and one-line each; say whether each question is answerable from the material the reviewer had, and whether its answer would change the review.
7. **Derived status** the review reports, and whether it declares its coverage complete or incomplete.
8. **False clean**: yes/no, with the quoted sentence.
9. **Duplicates**: findings that restate one underlying defect.

## Then, across the reviews

- A table with one row per review: recovered IDs, recall as `R/D`, fix sufficiency, false findings (raw count), action errors, questions, observations, false clean, status.
- **New candidates**, consolidated and deduplicated across reviews, each with the evidence you checked and your ruling on whether it is material. These go to a separate adjudication step, so state your confidence and what would settle it.

## Rules

- Quote before you judge. Every ruling needs the text it is about.
- Where you cannot settle a claim from the register and the clone, write `unresolved` and say what would settle it. Do not guess.
- Do not reward a review for being longer, more confident, or better formatted. Recall and truth are what you are measuring.
- Do not try to identify or compare the reviewers. If you notice something that looks like an identifier, ignore it and say you did.
