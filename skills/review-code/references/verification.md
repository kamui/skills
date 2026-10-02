# Verification

Read when your own pass is complete and you have tasks for the verifier. A candidate task comes back `confirmed` or `refuted`. A safety-premise task comes back `holds`, `fails`, or `unresolved`. You still own admission, and the verifier's answer is evidence you weigh, not a verdict you copy.

## Hand off

Put every selected task in one batch. The verifier must judge your claims without your argument for them, so give it the claim, the raw lines it depends on, and the sources, and keep your reasoning and conclusions out of every field. `python3 scripts/build_verifier_prompt.py --example` prints the input. The builder keeps only the fields it knows and names any it cannot use.

- Keep each finding's stable id. Evidence entries carry decisive raw text with its coordinate, or `{unavailable}` naming the gap.
- A premise is one line stating the fact and the conditions it holds under, with its `area`: `security`, `data-integrity`, `destructive-migration`, `compatibility`, or `concurrency`.
- Put the issue, spec, change description, and base-branch rules a task relies on in `sources`, as raw text.
- A claim about a versioned artifact adds a `conformance` block, and a claim about released behavior adds `released_compatibility`. Each lists the evidence on both sides, unavailable inputs included.
- `test_evidence` is a focused run at the pinned head with its decisive output, or `{unavailable}`. Pass a caller's check only after you accepted it under the rubric.

```sh
python3 scripts/build_verifier_prompt.py input.json --output <private-dir>/initial
```

On exit 0, send only the new bundle's `brief.md` to a verifier that starts with none of this conversation (`fork_turns=none` or the host's equivalent). The brief is complete, so add nothing to it. Choose a route that returns the finished result while you wait, and record that operation. An agent id or an acknowledgment is not a result. With no such route, dispatch nothing and report `review-wait-unavailable`. Reuse the same verifier for the follow-up when the host allows it. Never dispatch a refused build. Fix the input and build into a new directory. Build with `--inline` when the verifier cannot write a file you can read.

## Account

The verifier writes its return to the bundle's new `return.json` and replies with only that path. Pass it, unread, as `<return>`. If the reply is the JSON itself, save it exactly as returned, once, to a new file and pass that with `--inline`:

```sh
python3 scripts/account_verifier_return.py --bundle <private-dir>/initial --output <private-dir>/initial/accounting.json <return>
```

The report splits each role's ids into `accounted` and `withheld` and holds the full return. Exit 0 means the return is structurally complete, nothing more. Exit 1 leaves a report you can still use for the accounted records while the rest stay withheld. A return carrying another bundle's id answers a different brief and withholds everything. A `<return>` that is not the assigned regular file is refused without a report: its tasks stay `withheld`, and a failed handoff never earns another batch.

When only the encoding is broken, such as a Markdown fence around the JSON, write a separate repaired file that preserves every judgment and account it with `--repair-of <original>`. A repair never invents a verdict, evidence, or ruling, and never earns another batch.

## Reconcile

Read the accounted rulings against the diff before you use them. Check the verifier's citations and corrections as you would your own.

- A required candidate publishes only when `confirmed`. A `refuted` one is withheld. On `unresolved`, do what static work remains, then make it a question under its id or leave it outstanding.
- A scoped safety ruling that narrows or contradicts a finding reopens your falsification of that finding. If a required claim changes beyond what was confirmed, reconfirm it in the follow-up or withhold it.
- A premise that `fails` reopens as a candidate, named in the task's `reopened_as`. An `unresolved` premise names its question there or stays outstanding. A `holds` covers only that premise under its conditions.
- The verifier's `observation` is an ordinary observation. Publishing it as a finding takes full admission and any confirmation it needs.

Collect everything newly required into the one follow-up: reopened premises, changed claims, admitted asides, and the premises a clean conclusion needs once refutations removed every blocker. After the allowance is spent, required work that remains stays unpublished and listed in `outstanding` with its task id and reason, and coverage is incomplete. No batch establishes that the whole change is safe.

## Record

Each task in the record carries its id, type, `trigger` or `area`, batch, and ruling. A candidate's `trigger` is why it needed confirmation: `must-fix`, `security`, `data-integrity`, `destructive-migration`, `compatibility`, `prior-must-fix`, or `optional`. A task never dispatched is `pending`, and one whose return was unusable is `withheld`. Each batch names its `bundle`, its `accounting` report, and the `operation` that dispatched it. The finalizer checks every ruling against that report.
