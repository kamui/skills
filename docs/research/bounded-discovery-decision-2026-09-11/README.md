# Bounded discovery — the decision on the stopped pilot

**Delivered 2026-09-11 (UTC).** This bundle is [#153](https://github.com/kamui/skills/issues/153),
the decision stage of the [#138](https://github.com/kamui/skills/issues/138) epic. Its
prerequisite [#152](https://github.com/kamui/skills/issues/152) delivered the independent grading
in merged [PR #200](https://github.com/kamui/skills/pull/200), with the rulings frozen and sealed
before the arm mapping was opened.

**Decision: `inconclusive`, for B against A and for C against A**, under the frozen screen and
against both the graded truth and the registers as frozen. No arm is rejected: the grading ruled
zero raw false findings in every packet. No positive screen is reachable: eighteen of twenty-four
cells were never attempted, two of the three buggy targets have no attempt, and no attempt is a
valid completed outcome. **No confirmation study is recommended or authorised, no default changes,
nothing runs from this handoff.** [`evaluation.md`](evaluation.md) is the argument;
[`comparison-data.md`](comparison-data.md) is the data.

| Artifact | What it settles |
| --- | --- |
| [reveal.json](reveal.json) | the per-member digests of #151's sealed packet archive, read from the decrypted archive only after it hashed to the digest #151 published, so both packet files have a sealed digest to be checked against without the key |
| [verification.json](verification.json) | every revealed plaintext against the digest its stage sealed; both #152 freeze records with their exact file sets; both packet files against the sealed archive's member digests and the packet set against the public index, nothing missing or duplicated; the ledger's chain and totals |
| [revealed/](revealed/) | the sealed truth, schedule, packets, redaction map and ruling tables, opened after the freezes verified |
| [comparison.json](comparison.json) | the join: every attempt with its arm, target, validity, completion, cost by role, timing and per-attempt scoring fields |
| [grid-v2.json](grid-v2.json), [grid-v1.json](grid-v1.json) | the frozen scorer's input, against graded truth and against the registers as frozen |
| [scorecard-v2.md](scorecard-v2.md), [scorecard-v1.md](scorecard-v1.md) | the pinned `score_attempts.py`'s own output, unedited (JSON beside each) |
| [comparison-data.md](comparison-data.md) | per-attempt rows with raw items, concepts claimed, duplicate and bundled concept counts, per-target recall, screens, matched cost, spend by role, elapsed time, where each defect was found or lost |
| [loss-stages.json](loss-stages.json) | the coordinator's stage judgments per attempt and defect, with evidence pointers into the sealed records |
| [evaluation.md](evaluation.md) | the screening verdicts, what was measured, the limits, and what would change the conclusion |
| [decision.json](decision.json) | the decision record: outcome, per-criterion verdicts, blockers, what would change it |
| [handoff.json](handoff.json) | the stage record that closes the epic's measurement |

## Order of operations

1. **Verify before opening anything.** Both of #152's freeze records were checked with the exact
   file set each names — first at PR #200's review round against the grading stage's working
   copies, before this stage read the redaction map, and again here against the revealed copies
   before the join — and #151's packets against the public packet index
   ([`verification.json`](verification.json) records the digests; the grading handoff records that
   the map was never opened during grading).
2. **Reveal.** Every `.enc` under #148's `targets/sealed/`, #149's sealed schedule, #151's sealed
   packets and #152's two sealed archives were decrypted under #148's key and each plaintext
   checked against its `SHA256SUMS` or seal record. #151 published its packet archive's digest and
   not its members', so `decide.py reveal` records the two members' digests from the archive once
   it has hashed as sealed ([`reveal.json`](reveal.json)); `verify` checks the revealed packet
   files against that record and the packet set against the public index, refusing a missing,
   extra or duplicated packet or a changed redaction-map row. The member digests are trusted from
   the reveal step, which is the one step that needs the key: `verify` checks that the record names
   the archive #151 sealed and cannot re-derive the members without it, so anyone holding the key
   re-runs `reveal` and compares. The plaintexts the decision reads are committed
   verbatim under [`revealed/`](revealed/): the four registers and leak sets, the inventory, the two
   excluded registers, the slot map, the schedule, the grading packets and redaction map, the two
   ruling tables (and the pre-resume table beside the final one), both amendments and both derived
   field sets. Prompts, launch records, result envelopes and transcripts stay in the seals; their
   digests are public in the seal records.
3. **Join.** `decide.py join` keys everything by attempt: the arm, target and replicate from the
   schedule and the redaction map (cross-checked against each other and against #151's manifest);
   operational validity from the fidelity assessment (the map deliberately carries none); completion,
   cost and elapsed time from the manifest and reconciliation, including the per-role split; and the
   per-attempt scoring fields from the sealed `derived-fields-amended-1.json`; the duplicate-concept
   and bundled-item counts come from the revealed ruling tables' item-to-concept mapping with the
   amendments laid over by item reference, cross-checked against the derived fields. Truth for the two
   attempted slots comes from the derived fields (register status, `v1` ids, ids after grading) and
   for the two unattempted slots from their registers; the join refuses any disagreement.
4. **Score.** The pinned `score_attempts.py`, its digest checked against the frozen manifest, over
   the `v2` grid and the `v1` grid. Its output is committed unedited.
5. **Compare and decide.** The comparison tables, the loss-stage record, the evaluation and the
   decision record. The decision is read off the scorer's verdicts and nothing else.

## What the grid shows, in one paragraph

One replicate on two targets. On the clean target every arm returned Approved with zero findings
and C's finder claims were correctly rejected at admission. On the buggy target the control
returned Approved with zero findings — never raising either defect, with no verifier by policy —
while both candidate arms recovered both defects with a sufficient fix for one and a partial fix for
the other, C's first-defect recovery being the pilot's one finder-origin material recovery. The B
attempt is invalid on protocol grounds and the C attempt stopped at the budget ceiling, so neither
recovery is admissible. Matched cost medians over the two pairs: B/A 1.205, C/A 2.106, C/B 1.814.
None of this is a comparison the frozen design can support; it is one row.

## Truth after grading

| Slot | Target | Status | `v1` | After grading |
| --- | --- | --- | --- | --- |
| slot-1 | `clap-rs/clap#6212` | buggy | GT-p1 | GT-p1, GT-p2 (`v2`, confirmed by the adjudicator at head and merge-base) |
| slot-2 | `grpc/grpc-go#7417` | clean | — | — |
| slot-3 | `nats-io/nats-server#6593` | buggy | GT-r1 | GT-r1, never attempted |
| slot-4 | `nats-io/nats-server#7395` | buggy | GT-s1 | GT-s1, never attempted |

The frozen mix — three buggy, one clean — is unchanged. The four pull requests stay reserved; they
are revealed now and cannot be reused blind.

## Cost

Nothing was charged to this ticket. The ledger stands where #152 settled it: $50.3304587 actual,
$0.164316 retained uncertainty, no reservation outstanding, eighty-eight events in an unbroken chain;
$6.9831994 of the $10.00 protected grading and closeout reserve is unused and $99.5052253 remains
under the $150.00 cap after uncertainty. The design's `stop` operation was never implemented in
`budget.py`, so the ledger is left as it is and this bundle is the closing record. The fresh-context
review of this bundle before publishing is ordinary ticket work outside the measured spend, as every
stage's reviews have been.

| Column | USD |
| --- | --- |
| Pre-freeze: targets and probes | 10.9378407 |
| Shared setup and selection, charged once | 0.1527100 |
| Eight review attempts, discards included | 36.2231074 |
| Charged grading (#152) | 3.0168006 |
| This decision (#153) | 0 |
| Retained uncertainty | 0.164316 |
| **Ledger actual** | **50.3304587** |

## What this bundle does not do

- It launches no cell and authorises none; `dispatch_authorized` is `false`.
- It names no winner, sets no threshold, changes no default and recommends no confirmation study.
- It does not certify any attempt faithful: the fidelity assessment's `unresolved` and `invalid`
  verdicts are joined as they stand.
- It does not edit a frozen ruling, a freeze record, the ledger or any earlier stage's artifact.

## Scripts

Standard-library Python 3.9+, macOS and Linux, with `--self-test` (52 checks, including CLI exit
codes through `subprocess`):

| Command | What it does |
| --- | --- |
| `decide.py reveal` | the per-member digests of #151's packet archive, refusing an archive that does not hash as sealed or lacks a member |
| `decide.py verify` | every revealed plaintext against its sealed digest, the two freeze records with exact file sets, both packet files against the reveal record and the packet set against the public index, the ledger chain |
| `decide.py join` | the per-attempt join and the two scorer grids, refusing any disagreement between the schedule, the map, the manifest, the assessment and the derived fields |
| `decide.py score` | the pinned scorer over a grid, refusing a scorer whose digest is not the frozen one |
| `decide.py compare` | `comparison-data.md` from the join, the scorecards and the loss-stage record, whose vocabulary it validates |
| `decide.py handoff` | `decision.json` and `handoff.json`, refusing to decide over an unverified reveal |
| `decide.py scan` | authored public files against home and temporary paths |

The revealed plaintexts are exempt from the scan, deliberately: they are committed byte-for-byte so
that their digests prove them the sealed bytes, and some of them (the registers, the ruling tables)
name the working directories the evaluator used, as every earlier stage's README already does.

## Reproducing it

```sh
BUNDLE=docs/research/bounded-discovery-decision-2026-09-11
FROZEN=docs/research/bounded-discovery-runs-2026-09-08
CLOSEOUT=docs/research/bounded-discovery-closeout-2026-09-10
GRADING=docs/research/bounded-discovery-grading-2026-09-11
TARGETS=docs/research/bounded-discovery-prototype/targets
LEDGER=~/.config/bounded-discovery/issue-150/ledger.json         # the live ledger; optional
EVIDENCE=~/.config/bounded-discovery/issue-151/evidence           # the decrypted pilot evidence; optional, for the timing sidecars

python3 $BUNDLE/scripts/decide.py --self-test
# reveal: each sealed README's own procedure, under #148's key; the plaintexts under revealed/ are the result
python3 $BUNDLE/scripts/decide.py reveal --archive <decrypted grading-packets.tar.gz> \
  --sums $CLOSEOUT/packets/SHA256SUMS --out $BUNDLE/reveal.json      # needs the key; the record is committed
python3 $BUNDLE/scripts/decide.py verify --bundle $BUNDLE --targets-sums $TARGETS/sealed/SHA256SUMS \
  --schedule-sums $FROZEN/sealed/SHA256SUMS --packets-dir $CLOSEOUT/packets --reveal $BUNDLE/reveal.json \
  --grading-dir $GRADING --ledger $LEDGER --out $BUNDLE/verification.json
python3 $BUNDLE/scripts/decide.py join --bundle $BUNDLE --closeout-dir $CLOSEOUT --frozen $FROZEN/manifest.json \
  --evidence $EVIDENCE --loss-stages $BUNDLE/loss-stages.json --grading-usd 3.0168006 --out-dir $BUNDLE
for v in v2 v1; do
  python3 $BUNDLE/scripts/decide.py score --scorer $FROZEN/scripts/score_attempts.py --frozen $FROZEN/manifest.json \
    --grid $BUNDLE/grid-$v.json --out-json $BUNDLE/scorecard-$v.json --out-md $BUNDLE/scorecard-$v.md
done
python3 $BUNDLE/scripts/decide.py compare --comparison $BUNDLE/comparison.json --scorecard-v2 $BUNDLE/scorecard-v2.json \
  --scorecard-v1 $BUNDLE/scorecard-v1.json --loss-stages $BUNDLE/loss-stages.json --out $BUNDLE/comparison-data.md
python3 $BUNDLE/scripts/decide.py handoff --comparison $BUNDLE/comparison.json --scorecard-v2 $BUNDLE/scorecard-v2.json \
  --scorecard-v1 $BUNDLE/scorecard-v1.json --verification $BUNDLE/verification.json \
  --loss-stages $BUNDLE/loss-stages.json --out-decision $BUNDLE/decision.json --out-handoff $BUNDLE/handoff.json
python3 $BUNDLE/scripts/decide.py scan $BUNDLE/README.md $BUNDLE/evaluation.md $BUNDLE/comparison-data.md \
  $BUNDLE/*.json $BUNDLE/scorecard-*.md
```

Without `--evidence` the timing columns read `n/a`; without `--ledger` the handoff carries no
ledger figures. Everything else reproduces from the repository alone once the plaintexts are
revealed, and the reveal itself is checked by `verify`.
