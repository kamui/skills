You must do ALL of this work YOURSELF in this session. Do NOT use the Agent tool, do NOT dispatch any sub-agent, and do NOT start background tasks. Work single-threaded.

You are an independent adjudicator ruling on claims about one merged pull request that its ground-truth register does not cover. You are deliberately not told who raised them, how many reviewers raised them, what tool or configuration produced them, or what any reviewer said beyond each claim. Do not try to find out, and do not let any guess about their source affect your rulings. Do not stop to ask questions; finish in this dispatch.

## The change under review

`{REPO}#{PR}`, "{TITLE}", merged {MERGED_AT}. Head `{HEAD}`, merge-base `{MERGE_BASE}` (base branch `{BASE_BRANCH}`).

Your working directory holds:

- `register.json`: the target's ground-truth register, version {REGISTER_VERSION}. Its `defects` are the material defects already established, with their required corrective outcomes; its `non_defects` are plausible objections already ruled not material.
- `rubric.md`: the scoring rubric, whose definitions you apply.
- `clone/`: an offline clone with `main` at the merge-base and `review-head` checked out, with `clone-cache/` (its dependency cache) and `clone-work/` (scratch space) beside it. The execution allowance below says how to run things in it.

You may also use the network, `gh` and `git` to read the upstream repository and its history, including everything after the merge: later commits, issues, pull requests, reverts and releases. Stay inside your working directory otherwise; read nothing else on this machine.

## Execution allowance

{ALLOWANCE}

## The claims

Each claim was raised during scoring and could not be refuted from the register and the clone. The notes under each are a scorer's, unverified: treat every part as a hypothesis.

{CLAIMS}

## What to decide, for each claim separately

1. **Is it true at the head?** Reproduce it or refute it yourself, with the exact commands and output, and check the merge-base too.
2. **Was it introduced by this pull request?**
3. **Is it already in the register?** Compare it with each `defects` entry (same underlying mechanism and required corrective outcome) and each `non_defects` entry.
4. **Is it material?** A material defect is an actionable correctness, security, data-integrity, compatibility, meaningful-performance or explicit-requirement failure with a demonstrated consequence (`rubric.md`). Say what triggers it, what breaks, and what evidence demonstrates the consequence: a downstream report, a revert, a regression test, or your own reproduction.
5. **Counter-arguments.** Give the strongest case against your ruling and say why you do or do not accept it.

## Output

Write `rulings.json` in your working directory, exactly this shape:

```json
{"rulings": [{"candidate": "NC-1", "ruling": "material", "duplicate_of": null, "classification": null,
  "defect": {"title": "...", "trigger": "...", "consequence": "...", "evidence": "...", "required_outcome": "...",
             "manifestations": ["..."]},
  "reasoning": "..."}]}
```

- `ruling` is one of:
  - `material`: a new material defect. Fill `defect` in full; `required_outcome` is stated as an outcome any sufficient fix must restore, not as one patch.
  - `duplicate`: the same defect as a register entry. Set `duplicate_of` to its id.
  - `not-material`: set `classification` to `true-sub-threshold` (an accurate fact below the bar) or `false` (contradicted or unsupported), and add it as a `non_defect` in `reasoning`'s terms.
  - `unresolved`: say in `reasoning` exactly what would settle it.
- `defect` is null unless the ruling is `material`; `duplicate_of` is null unless it is `duplicate`; `classification` is null unless it is `not-material`.
- `reasoning` quotes the evidence each ruling rests on.

Also write `rulings.md`: the same rulings in prose, with the commands you ran and their output.

Be willing to rule either way. A wrong ruling in either direction corrupts a measurement, so decide on the evidence you gathered, not on how a claim is phrased.
