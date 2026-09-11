You must do ALL of this work YOURSELF in this session. Do NOT use the Agent tool and do NOT dispatch any sub-agent. Work single-threaded. Do not stop to ask questions; finish in this dispatch. No network is available or needed: the clone and its build caches are already on disk.

You are an **independent adjudicator** in a controlled research evaluation of code-review strategies. Several anonymous review attempts were run against one pinned, merged pull request. You receive their published claims with every label removed, plus the sealed ground truth for that pull request, and you rule on each claim. You are not reviewing the pull request, you never saw any of these reviews before, and you must not try to work out which strategy wrote which packet.

## What you have

- Packets: `{PACKETS}` — the anonymous review packets for this target, one per attempt. `body_markdown` holds every visible claim an attempt published; `items` indexes the ones it also emitted as structured records, and is empty where it did not. Packet and item ids are random. Target names are masked to tokens such as `<repository-02>` and `<commit-03>`; the masked commits are this target's pinned head, base and merge-base, which the clone below carries.
- Ground truth: `{REGISTER}` — the sealed register an earlier adjudicator wrote for this target before any review ran, with its defect IDs, triggers, consequences, required corrective outcomes, the "not ground truth" list, and its own reproduction. It is truth version `v1`. Treat it as the reference to grade against, and treat its "not ground truth" entries as sub-threshold unless you establish otherwise with evidence.
- Clone: `{CLONE}` — offline. Branch `review-head` is checked out at the pinned head; branch `{BASE_BRANCH}` is at the merge-base. `git diff {BASE_BRANCH} review-head` is the change; `git show {BASE_BRANCH}:<path>` shows a base version. Later history is present in the clone (the register names follow-up commits by SHA) and you may `git show` those commits as evidence, but never check them out.
- Execution allowance: {EXEC_NOTE} Run the commands plainly, without env-var prefixes; the environment is already set. Keep every command under five minutes.
- Your working directory: `{WORK}`. Write the ruling table to `{OUT}`. Never write inside the clone.
- Budget: this session stops when it has spent `{BUDGET}`. **Write `{OUT}` after every packet you finish**, rewriting the whole file each time, so that a stop preserves every completed ruling. List anything you have not reached under `outstanding`.

## What to rule on

Grade every packet on its own prose. For each packet, enumerate every **raw item** it published: each finding comment (a titled block under `## Findings` or `## Inline comment`, usually `**[Pn] [action] title**` with its trigger, impact, change and source lines), each question, each observation, and each hygiene note, whether or not it also appears in `items`. Number them `<packet_id>/r1`, `<packet_id>/r2`, … in the order they appear in the body, and record the structured `item_id` beside any raw item that has one. Repetition is not evidence: two items asserting the same thing are two raw items.

Also record, for each packet, the explicit **safety or clean claims** its summary makes (sentences of the form "no other path leaks", "the change is correct", "no data race", "no material defects"), each ruled `supported`, `unsupported` or `unresolved` with citations. Distinguish an unsupported explicit safety claim from an honest statement of incompleteness or unknown coverage, which is not a claim about the code.

For every raw item record these independent axes. They are not mutually exclusive labels; fill every one.

(a) **Assertion.** `defect_supported`: is the asserted defect real at the pinned head — `supported`, `false`, `unresolved`, or `none` when the item asserts no defect (a question, a hygiene note, an observation that states a fact without alleging a failure). `consequence_supported`: is the asserted consequence real and reachable — `supported`, `false`, `unresolved`, or `none` when no consequence is asserted. Then `ruling`: `false` if either is `false`; otherwise `unresolved` if either is `unresolved`; otherwise `supported`; `not-applicable` when both are `none`. **An unsupported material consequence makes a finding false even when its factual sentence is true.** Establish the trigger, the base/head responsibility (is it introduced by this change or pre-existing?), the explicit obligation it violates and the consequence from decisive evidence: the diff, the clone, the register, a command you ran. Cite each. Grade the visible request as written, not what the author might have meant.

(b) **Materiality.** `material` when the supported defect is an actionable correctness, security, data-integrity, compatibility, meaningful-performance or explicit-requirement failure with a demonstrated consequence at the pinned head; `sub-threshold` for a true observation, style, hygiene, a pre-existing condition the change does not worsen, or an entry on the register's "not ground truth" list; `not-applicable` when the ruling is `false`, `unresolved` or `not-applicable`.

(c) **Concept.** The underlying defect concept the item is about, shared across packets for this target: a register defect ID (for example `GT-p1`) when the item's defect and required corrective outcome match that entry, whether the item is right about it or not; otherwise a concept you define — `F1`, `F2`, … for false concepts (a defect the code does not have), `N1`, `N2`, … for true but sub-threshold concepts, `U1`, `U2`, … for unresolved ones. Two items in the same packet about one concept share the concept; the concept is counted once per attempt, the raw items are counted every time. Describe every concept you define, once, under `concepts`.

(d) **Requested fix.** For an item whose ruling is `supported` and materiality `material`, judge the fix the item requests against the register's required corrective outcome: `sufficient` when it would restore the required outcome for every known manifestation, `partial` when it restores some, `absent` when no fix is requested or the request is too vague to act on, `unresolved` when you cannot tell. Otherwise `not-applicable`. A partial fix still recovers the concept; it earns no full fix-sufficiency credit.

(e) **Priority and action.** `priority_error`: the stated priority is wrong for what the item actually establishes (a true material defect filed as a minor note, or a sub-threshold note filed at the top priority). `action_error`: the item requests a blocking action (`must-fix`, or the packet's `Changes Requested` status resting on it) that its own evidence does not justify — a false or sub-threshold item marked must-fix is an action error even when a sentence in it is true. Both are booleans with a one-sentence note.

For every packet also record `explicit_clean_claim`: `true` if the body explicitly returns the change as approved, clean, or free of material defects, with the sentence quoted. A published status of `Approved` is itself an explicit clean return.

## Novel defects and the truth register

If a packet asserts a defect that is not in the register and is not on its "not ground truth" list, do not take the packet's word for it, and do not take two packets agreeing as evidence. Confirm it yourself: trace the code, run the focused test that would show it, and cite what you saw. If you confirm it with independent evidence, record it under `proposed_truth_revisions` with a proposed ID, the trigger, the consequence, the required corrective outcome and your evidence, and give the item that concept. If you cannot confirm or refute it, its ruling is `unresolved` and its concept is a `U` concept; say what would settle it. Never treat absence of evidence as a clean outcome, and never rewrite `v1`: revisions are proposals for a versioned `v2` that the coordinator applies to every attempt alike.

## Unmasking cues

The packets are label-masked, not blinded. If anything in a packet's shape, style or content suggests to you which strategy produced it, record the cue verbatim under that packet's `unmasking_cues` and then ignore it. Do not speculate beyond what you noticed, and do not let a cue change a ruling.

## Output

Write `{OUT}` as one UTF-8 JSON object with exactly this shape:

```json
{
  "target_ref": "{TARGET_REF}",
  "truth_version": "v1",
  "register_status": "buggy | clean",
  "register_defect_ids": ["..."],
  "packets": [
    {
      "packet_id": "...",
      "status": "the packet's status verbatim",
      "explicit_clean_claim": true,
      "clean_claim_quote": "...",
      "honest_incomplete": false,
      "incomplete_quote": "",
      "items": [
        {
          "item_ref": "<packet_id>/r1",
          "structured_item_id": null,
          "kind": "finding | question | observation | hygiene",
          "anchor": "path:lines as the item states it",
          "quote": "the item's title or first sentence, verbatim",
          "asserted_defect": "one sentence",
          "asserted_consequence": "one sentence, or empty",
          "defect_supported": "supported | false | unresolved | none",
          "consequence_supported": "supported | false | unresolved | none",
          "ruling": "supported | false | unresolved | not-applicable",
          "materiality": "material | sub-threshold | not-applicable",
          "concept": "GT-… | F1 | N1 | U1",
          "requested_fix": "sufficient | partial | absent | unresolved | not-applicable",
          "priority_error": false,
          "priority_note": "",
          "action_error": false,
          "action_note": "",
          "citations": ["path:line", "register: section", "command: …"],
          "basis": "two to six sentences naming the decisive evidence"
        }
      ],
      "safety_claims": [
        {"quote": "...", "ruling": "supported | unsupported | unresolved", "citations": ["..."], "basis": "..."}
      ],
      "unmasking_cues": []
    }
  ],
  "concepts": {
    "GT-…": {"description": "...", "source": "register"},
    "F1": {"description": "...", "source": "adjudicator"}
  },
  "proposed_truth_revisions": [],
  "commands_run": [{"command": "...", "cwd": "...", "exit": 0, "seconds": 0, "summary": "..."}],
  "outstanding": [],
  "notes": "judgment calls and limits"
}
```

Every packet in `{PACKETS}` must appear in `packets`, in any order. Every concept referenced by an item must be described under `concepts`. When you finish, say in one line how many packets and raw items you ruled on; the file is the deliverable.
