# Pinned baseline for the repaired one-shot review skill

**Pinned 2026-09-06 for [#136](https://github.com/kamui/skills/issues/136).** This document
fixes the snapshot that [#137](https://github.com/kamui/skills/issues/137) measures against the
historical control, records the version audit that preceded the pin, and reports the mechanical
checks that passed on it. It is an acceptance record, not a result: every check below is a
property of the scripts and the output contract, and none of them is evidence about how many
material defects a review recovers. Recall belongs to #137 under the
[one-shot evaluation method](code-review-one-shot-method.md); the epic decision belongs to
[#71](https://github.com/kamui/skills/issues/71).

## 1. The pin

| | Repaired baseline | Historical control |
| --- | --- | --- |
| Commit | `83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6` | `3ff624a0a8b57e7096d8ad8263ac64a3fb3ccd83` |
| `skills/code-review-publish` tree | `bea6be143582e75bada966ee85964623ef31f167` | `867cf3ff0d9f097259699be4f55aa147c98a3a5d` |
| Workflow identifier | `v5b-10` | `v5b-1` (pre-#70; see §3) |
| Status | pinned here; later commits are a different snapshot | unchanged by this work |

Evaluation agents snapshot the pinned skill tree, never a moving branch. Take the snapshot by
commit, not by copying `main`:

```sh
git -C <clone> archive 83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6 skills/code-review-publish | tar -x -C <snapshot-dir>
git -C <clone> rev-parse 83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6:skills/code-review-publish   # must print bea6be14…
```

The tree hash is the check that matters. The commit SHA identifies where the snapshot came from;
the tree hash proves the snapshot is the reviewed one, and it stays valid if later commits touch
only documents outside the skill. The control is pinned the same way and is not modified here.

## 2. Merged change map, control to baseline

Everything in `skills/code-review-publish` between the two pins, newest first. Each entry is one
merged issue; the identifier column is what that issue left the workflow identifier at.

| Issue | Change | Identifier |
| --- | --- | --- |
| [#136](https://github.com/kamui/skills/issues/136) | The late bump this document's §3 explains; no rule change | `v5b-10` |
| [#135](https://github.com/kamui/skills/issues/135) | Decision rules consolidated to one owner each; bounded risk-led discovery | `v5b-9` |
| [#134](https://github.com/kamui/skills/issues/134) | A finding needs exactly one non-empty `Triggers when`, `Impact`, and `Change`, in order | `v5b-8` |
| [#133](https://github.com/kamui/skills/issues/133) | Bounded large-diff recovery: literal `--path`, a private store, chunked reads with a consumed/missing inventory | `v5b-7` (retained) |
| [#132](https://github.com/kamui/skills/issues/132) | Forge inputs persisted as one paginated packet with stable ids and edit timestamps | `v5b-7` |
| [#123](https://github.com/kamui/skills/issues/123) | Versioned conformance obligations enumerated into the ledger | `v5b-6` |
| [#122](https://github.com/kamui/skills/issues/122) | Changed tests inspected in execution order; focused checks executed once | `v5b-5` |
| [#121](https://github.com/kamui/skills/issues/121) | Claims ledger built from the pull-request text before compliance review | `v5b-4` |
| [#84](https://github.com/kamui/skills/issues/84) | Deleted-file anchors linked at the merge-base | `v5b-3` |
| [#119](https://github.com/kamui/skills/issues/119) | Scoped verifier safety rulings; post-refutation clean-verdict recheck | `v5b-2` |
| [#70](https://github.com/kamui/skills/issues/70) | Early dispatch of the candidate batch on low-risk surfaces (PR #125) | `v5b-1` (retained — the defect §3 repairs) |

`git diff --stat 3ff624a0a8b57e7096d8ad8263ac64a3fb3ccd83 83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6 -- skills/code-review-publish`
reports 14 files changed, 3691 insertions, 188 deletions, including two new scripts
(`forge_packet.py`, `test_forge_packet.py`) and two new references (`conformance.md`,
`verifier-concurrency.md`). #84's paired routine/audit repair is not in this snapshot: it stays
open behind #159, per its current scope.

## 3. Version audit and the late bump

The audit asked one question of every commit merged since `v5b-1`: did a change to admission,
verification, rendering, or state semantics reach `main` without an identifier increment? One
did.

**Issue #70 (PR #125, `f6ce7073149f7d2e02a0a4df234a213a1c43f02a`, merged 2026-09-05).** Its
change note recorded it as "a scheduling change, not a change to what is verified" and kept
`v5b-1`. Two of its clauses are rules the merge-base did not have. The single follow-up batch
acquired a trigger of its own — a ledger row that first becomes related to a batch survivor runs
it even when no late candidate exists, where before only a candidate newly reaching render
eligibility could start it. And which related rows the *initial* batch carries became a function
of when that batch was dispatched rather than of the finished falsification pass. Both decide
which acquittals get an independent ruling and how many verifier contexts a review spends, so
both are verification semantics under the output contract's own rule.

The increment cannot be inserted where it belonged: `v5b-2` through `v5b-9` are published
identifiers that `validate_review.py` and existing trailers already use, and renumbering them
would misdate every review carrying one. It is therefore taken forward as `v5b-10` in the pinned
commit. `DESIGN.md`'s issue #70 entry is corrected in place — it now names the change it made and
points at the issue #136 entry — rather than being rewritten as though the bump had happened
then.

**The intervening ambiguity the late bump does not repair.** `v5b-1` names two different
verification behaviors. On `main` the pre-#70 rules held until PR #125 merged and the post-#70
rules until PR #140 bumped `v5b-2` about half an hour later, but the window is not the problem.
The historical control is a pinned *pre-*#70 tree whose `validate_review.py` reports
`WORKFLOW = "v5b-1"`, and the holdout runs recorded under it carry a `v5b-1` trailer that a
post-#70 run would carry too. No `v5b-1` trailer separates them. **A matched comparison must
identify each run by the skill-tree commit SHA it ran from, and never by the workflow trailer
alone** — which is why §1 pins both arms by tree hash.

Two adjacent retentions were checked and confirmed rather than corrected. #133 changed the
tooling that fetches the diff and named one new instance of the existing omitted-patch rule, not
the rule itself, so `v5b-7` stands. #136 itself moves no admission, verification, rendering, or
state rule: a review run under `v5b-9` and one run under `v5b-10` follow identical instructions
apart from the identifier. The one live cost of the bump is that a review published under
`v5b-9` no longer suppresses a re-review under the duplicate-review shortcut — one identifier's
worth of re-reviews over the day `v5b-9` was current, failing in the safe direction.

Runtime references were searched for stale identifiers and are consistent at `v5b-10`:
`scripts/validate_review.py`'s `WORKFLOW`, `references/output-contract.md`'s versioning sentence
and example trailer, and `README.md`'s version history. `DESIGN.md` and the run documents under
`docs/research/` keep their earlier identifiers as history and were deliberately left alone.

## 4. Mechanical checks

Environment: Python 3.14.7, git 2.55.0, gh 2.98.0, Darwin 27.0.0. Run from
`skills/code-review-publish` at the pinned commit.

| Command | Exit | Result |
| --- | --- | --- |
| `python3 scripts/validate_review.py --self-test` | 0 | `self-test passed (105 cases, emit-batch included)` |
| `python3 scripts/test_context_fingerprint.py` | 0 | `10 case group(s) passed` |
| `python3 scripts/forge_packet.py --self-test` | 0 | `passed` |
| `python3 scripts/test_forge_packet.py` | 0 | `7 case group(s) passed` |
| `python3 scripts/review_context.py --self-test` | 0 | 11 named cases passed, including path selection, pinned diff prefixes, newline-only chunking, store round trip with byte-exact recovery, private store open, the bound charged against a build call's other sections, three delta cases, `--help` coverage, and `--chunk-bytes` refused without `--store` |

## 5. Fixture acceptance

These exercise the skill's own scripts on a real local range and a real read-only forge fetch.
Nothing was published. The range is PR #177: merge-base
`25e61a63445911082f1abf46b4d73bca015020a4`, head `913b26e5054ee6d3f94938a816c66b2f3830d3bf`,
prior head `24a3b0fd17bee4c2d0e26ded6b7f72b6b8ad8fb1`. `$DIR` is a `mktemp -d` directory and
`$STORE` is `$DIR/review-context-<head>.json`.

**First review, full packet.** The root query in `SKILL.md` step 1 saved to `forge-1.json`, then:

```sh
python3 scripts/forge_packet.py normalize $DIR/forge-1.json > $DIR/packet.json
```

Exit 0; `complete: true`, `gaps: []`, and per-connection coverage complete for
`closingIssuesReferences` (1/1), `reviews` (2/2), `reviewThreads` (1/1), `comments` (1/1), and
the comment connections of issue `kamui/skills#123` and thread `PRRT_kwDOUHcsF86fmoL4`.

**A truncated connection is named, not silently dropped.** The saved page was edited to report
`hasNextPage: true` and `totalCount: 5` on `reviews` with no continuation page. `normalize`
printed `forge_packet: gap: reviews: 2 of 5 items fetched; continuation missing or failed`, and
the packet carried `complete: false` with that gap.

**Digest.** `echo -n "" | python3 scripts/context_fingerprint.py --packet $DIR/packet.json`
printed `6f100ce6d920f398f58081bfaf4098fb0f7588b4b335f7854c09b54731b48038`, identical on a second
run.

**Chunk recovery.** The unbounded build printed 140,164 bytes, above this harness's tool-output
limit. The bounded build

```sh
python3 scripts/review_context.py --merge-base <mb> --head <head> --store $STORE
```

printed 7,414 bytes and wrote a 145,464-byte store, withholding 133,941 bytes of diff across 9
chunks against the 16,991 bytes its other sections left of the 24,000-byte bound, with
`diff coverage: incomplete (0/9 chunks consumed)`. Reading each chunk back with
`--from $STORE --path <path> --chunk <k>` — nine reads across six files — moved the inventory to
`diff coverage: complete (9/9 chunks consumed)`, and the chunk byte counts sum to exactly the
133,941 bytes withheld. Byte-exact reconstruction of the persisted diff is pinned by the
script's own store round-trip self-test rather than re-derived here.

**Re-review.** The same build with `--base-ref main --prior-head <prior>` produced
`delta-conditions` (`ancestor: yes`, `merge-base-unchanged: no`, `prior-head-reachable: yes`), a
one-file `delta-manifest`, the corresponding `delta-diff`, and one `delta-overlap` row pairing
the delta range against the full-diff range that contains it.

**Required fields.** The contract's example review, assembled as a payload with

```sh
python3 -c 'import sys, json; sys.path.insert(0, "scripts"); import validate_review as v; json.dump(v.valid_payload(), sys.stdout)' > $DIR/payload.json
```

validates at exit 0 and carries `workflow=v5b-10`. Removing the `**Impact:**` field from its
first finding fails at exit 1 — the #134 rule holding on the pinned tree:

```
items[0]: finding-fields: a finding states `**Impact:**` once; it is missing (a label inside a code block or code span is example text and does not count)
```

**Unsupported verifier evidence.** Only one part of this rule is mechanical: a fact published in
`Observations`, a verifier aside included, must carry its pointer. Stripping the `Evidence:`
sentence from the payload's observation fails at exit 1:

```
items[2]: observation-form: an observation ends with one `Evidence:` pointer
```

The rest of the rule is reviewer judgment the validator never sees — uncited safety prose cannot narrow a
confirmed finding, a `refuted` verdict with basis `unresolved` is an unsettled claim rather than
evidence of safety, and `verification: independent-confirmed` lives in the private record. Those
are checked on paper in `DESIGN.md`'s "Paper regression checks", and no check in this document
is evidence that a model applies them.

## 6. Non-publishing payload, validation, and batch emission

The acceptance check #136 asks for, run end to end with no external write:

```sh
python3 scripts/validate_review.py --render   < $DIR/payload.json   # exit 0, 2 fragments
python3 scripts/validate_review.py            < $DIR/payload.json   # exit 0, no violations
python3 scripts/validate_review.py --emit-batch < $DIR/payload.json > $DIR/batch.json  # exit 0
```

`--render` printed one `anchor …; fix …` fragment per rendered item, both as commit-pinned blob
links at the run head. The emitted batch is `{commit_id, event, body, comments}` with
`event: COMMENT`, `commit_id` equal to the trailer's head, a 1,340-byte body, and one line-
anchored comment (`src/payments.ts:42`, side `RIGHT`); the file-anchored question produced no
comment, as the contract specifies. Emission is refused on an invalid payload: the missing-
`Impact` variant exits 1 and emits no batch. The publisher stays advisory — `SKILL.md` step 6
re-fetches the head and writes only when publication is authorized, and none of this ran.

## 7. Outstanding limitations

- **`v5b-1` is ambiguous** across the #70 window (§3). Identify runs by tree hash.
- **Mechanical acceptance is not recall.** Nothing here says the pinned skill finds more
  material defects than the control. #137 measures that; #138 evaluates its frozen prototype
  comparison separately and does not wait for #137. **Measured 2026-09-07 (#137,
  [bundle](one-shot-qualification-2026-09-07/README.md)): it does not.** Across 24 cells on six
  fresh targets the pinned snapshot recovered fewer material defects per completed review than
  this control (macro 55.0% against 70.0%) and returned more false cleans (4 against 3), with
  zero false findings in either arm, equal completion, and matched median billed cost 1.057.
  The screen fails and the baseline is retained; this is a recall result and says nothing about
  the mechanical guarantees recorded above, which the control does not carry.
- **The forge write is untested.** Coverage stops at batch emission. No test exercises the
  actual review submission, the stale-head guard, or the malformed-comment repair path in
  `references/output-contract.md`'s publication invariants; those are observed only in live runs.
- **One interpreter.** The scripts declare Python 3.9+ and were run here only on 3.14.7, on
  macOS. Linux and older 3.x are unverified in this record.
- **`--emit-batch` writes its violations to stdout.** Redirecting a failing call leaves the
  violation text where a batch would be, so a caller must gate on the exit status, as `SKILL.md`
  step 6 does.
- **The digest does not cover prior review state.** `context_fingerprint.py` hashes the packet's
  `pr` and `issues` sections, so the truncated-`reviews` packet in §5 produced the same digest as
  the complete one. Packet `gaps` is what carries that loss, and the re-review reference reads it
  from there.
- **The build call's unchunked sections can spend the whole bound.** `manifest`, `ranges`,
  `history`, the delta sections, and the inventory scale with file count and are not chunked; on
  a wide range they leave nothing for the diff, as the issue #133 change note records. The
  7,414-byte figure in §5 also moves with the store path length, since the withheld notice quotes
  it.
- **#84's paired routine/audit repair is not in this snapshot**, per §2.
