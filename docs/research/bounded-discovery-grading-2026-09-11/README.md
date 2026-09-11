# Bounded discovery — independent grading before unblinding

**Delivered 2026-09-11 (UTC).** This bundle is [#152](https://github.com/kamui/skills/issues/152),
the grading stage of the [#138](https://github.com/kamui/skills/issues/138) epic. Its prerequisite
[#151](https://github.com/kamui/skills/issues/151) closed out the stopped pilot in merged
[PR #198](https://github.com/kamui/skills/pull/198) and sealed six anonymous grading packets plus a
two-attempt no-packet manifest. This stage grades those packets and nothing else.

**No reviewer run was launched here, and none may be launched from this handoff.** The eighteen
unattempted grid cells stay unattempted; [`handoff.json`](handoff.json) carries
`dispatch_authorized: false`. The experiment remains `stopped-incomplete`.

**The arm mapping was not opened.** The rulings were frozen and hashed
([`rulings-freeze.json`](rulings-freeze.json)) and sealed ([`sealed/`](sealed/)) with the redaction
map still closed. After the pull-request review disputed two rulings, the same adjudicators
re-examined them on the evidence and amended both; the amendments are a versioned layer over the
untouched frozen tables, frozen again as [`rulings-freeze-2.json`](rulings-freeze-2.json) and
sealed under [`sealed/amendment-1/`](sealed/amendment-1/), still with the map closed (see
*Amendments after review* below). #153 opens it. Nothing in this bundle names an arm, a model, a replicate, a
validity label or a cost of any attempt, and no ruling was joined to one.

| Artifact | What it settles |
| --- | --- |
| [rulings-public.json](rulings-public.json) | the anonymous ruling summary: per packet and per masked target, every axis as counts, raw against concept, with every unmasking cue listed |
| [rulings-freeze.json](rulings-freeze.json) | the digest of each full ruling table and of the derived scoring fields, recorded before the mapping was opened; untouched by the amendments |
| [rulings-freeze-2.json](rulings-freeze-2.json) | the current freeze: the same tables, the two amendments and the amended derived fields, recorded with the mapping still closed |
| [sealed/](sealed/) | the full ruling tables with their quotes, citations and basis, under #148's key; the plaintext digests are beside the ciphertext |
| [sealed/amendment-1/](sealed/amendment-1/) | the two amendments, the amended derived fields, the prompts and launch argv that produced them, the reproduction program and the full transcripts |
| [metering/](metering/) | each adjudicator session's cost, model, effort, freshness and read audit, and its retained launch argv |
| [prompts/adjudicator-template.md](prompts/adjudicator-template.md) | the adjudicator's instructions, public because they carry no truth |
| [handoff.json](handoff.json) | the stage record #153 reads |

## Independence, and what the adjudicator was given

Two fresh headless sessions, one per masked target, `claude-sonnet-5` at effort `high`, verified on
every assistant line of both transcripts ([`metering/`](metering/)). Neither had produced a review,
seen a comparative outcome, or read this repository. Each received exactly four things:

1. the packets for its target, split from #151's sealed `grading-packets.json` by
   [`grade.py split`](scripts/grade.py), carrying the packet id, status, body and structured items
   and nothing operational — the split file's digest of its source is recorded in it;
2. the sealed truth register for that target, byte-identical to the register #148 sealed on
   2026-09-08 (its digest matches the slot manifest's `register_plaintext_sha256`);
3. a clone pinned to the target's head and merge-base with the same branch shape the reviewers had,
   plus an offline build cache, so that a claim could be confirmed by running the focused test that
   would show it;
4. the [template](prompts/adjudicator-template.md), rendered with paths and the execution note.

What it did not receive, and could not reach: the redaction map, the closeout's fidelity
assessment, the manifest, the reconciliation, the ledger, the pilot's cell summaries, the other
target's material, and this repository. The session ran `--restricted` with only the clone and the
inputs directory added to its roots; [`grade.py audit`](scripts/grade.py) then classified every
path a tool call named against those roots from the transcript. Both audits are in
[`metering/`](metering/) and the result is stated under *Fidelity* below rather than assumed.

The adjudicator was told that the packets are label-masked, not blinded, and to record any cue it
noticed and then ignore it. It was **not** told the one cue the coordinator already knew — that in
this pilot only one arm published structured `items` beside its body — because telling it would
have been the discovery the ticket says to avoid. That cue is recorded by the coordinator in
[`rulings-public.json`](rulings-public.json) under `unmasking_cues`, as the packets' own README says
it must be.

The coordinator (the session that wrote this bundle) read the packets' structure to build the
inputs and wrote no ruling. It did read the two registers, which is what handing them over
requires. It did not open the redaction map. It saw one line of the live ledger while confirming
the grading reserve, which names a slot and an arm for one attempt; that is recorded here as a
limit on the coordinator's blindness, not the adjudicator's, and no ruling passed through the
coordinator's judgment.

## The axes

Every raw item an attempt published — each finding, question, observation and hygiene note in
its body, whether or not the attempt also emitted it structurally — was ruled on five independent
axes, per the method's section 4 and the ticket:

- **(a) assertion** — `defect_supported` and `consequence_supported`, each `supported`, `false`,
  `unresolved` or `none`, and the ruling that follows mechanically from the pair: `false` if either
  is false, otherwise `unresolved` if either is unresolved, otherwise `supported`. An unsupported
  material consequence makes a finding false even when its factual sentence is true;
- **(b) materiality** — `material` or `sub-threshold`, only for supported items;
- **(c) concept** — a register defect ID, or an adjudicator-defined false (`F`), sub-threshold
  (`N`) or unresolved (`U`) concept, shared across packets on the same target. Raw items are counted
  every time; a concept once per attempt. Two false duplicates are two raw false items and one false
  concept; two supported duplicates recover a material concept once;
- **(d) requested fix** — `sufficient`, `partial`, `absent` or `unresolved` against the register's
  required corrective outcome, only for supported material items; a partial fix recovers the concept
  and earns no sufficiency credit;
- **(e) priority and action errors** — booleans with a note each; a must-fix resting on a false or
  sub-threshold item is an action error even when a sentence in it is true.

Beside the items, each packet carries its explicit clean claim (a status of `Approved` is one,
whatever the body says), an honest-incomplete flag, and every explicit safety claim its summary
made, each ruled `supported`, `unsupported` or `unresolved` — so that an unsupported "no other path
leaks" is separated from an honest "coverage incomplete".

[`grade.py validate`](scripts/grade.py) refuses a table whose ruling does not follow from its two
supporting axes, whose supported material item names a concept that is neither a register defect
nor a confirmed revision, or whose packet is neither ruled nor listed as outstanding.
[`grade.py derive`](scripts/grade.py) is the only place the raw-versus-concept collapse happens;
its `--self-test` runs the mapping on the five cases the ticket names — a supported duplicate pair,
a false duplicate pair, a true fact with an invented impact, an insufficient fix, and an unresolved
claim — plus the recovered-but-Approved case the preregistration carries forward.

## Scripts

Standard-library Python 3.9+, macOS and Linux, one script with `--self-test`:

| Command | What it does |
| --- | --- |
| `grade.py split` | one packet file per masked target from the sealed packets, nothing operational |
| `grade.py render` | the adjudicator prompt from the template, refusing an unfilled placeholder |
| `grade.py validate` | the ruling table's shape and internal consistency |
| `grade.py derive` | the per-attempt fields `score_attempts.py` consumes, without arm, validity or cost |
| `grade.py freeze` / `--check` | the digests, and the proof a later copy is byte-identical |
| `grade.py publish` | the anonymous summary, scanned against #149's frozen manifest before it is written |
| `grade.py seal` | the full tables under #148's key |
| `grade.py audit` | model, effort, freshness and read audit of one adjudicator transcript |
| `grade.py meter` | one session's cost, charging the larger of transcript and self-report |
| `grade.py handoff` | the stage record, scanned the same way |

The public scan refuses every slot name, repository component, url, pinned object id and
pull-request reference derived from the frozen manifest, any other full object id, and — new here —
any source path, any slash path outside this repository's own roots, and any path under a home or
temporary directory, because a file path names the project as surely as its name does.

## What was graded

Six packets on two masked targets, `<target-A>` (three packets) and `<target-B>` (three packets),
plus the two attempts #151's no-packet manifest records as having published nothing: one refused
before any model request and one lost to a provider error before it published. Neither of those has
a claim to grade and neither is scored as clean; they stay in the closeout's manifest with their
cost. Every packet was ruled; nothing is outstanding.

The counts below are the public summary's. Per-item quotes, anchors, citations and reasoning are in
the sealed tables; defect IDs are renumbered per target (`D1`, `D2`) so that a register's own
lettering names nothing.

### `<target-A>` — register adjudicated clean, truth stays `v1`

| Packet | Status | Raw items | Findings | False findings | False non-finding items | Unresolved | Safety claims (unsupported) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `1d3416e2…` | Approved | 0 | 0 | 0 | 0 | 0 | 4 (0) |
| `c838196b…` | Approved | 1 observation | 0 | 0 | 0 (1 before amendment 1) | 0 | 2 (0) |
| `d34ed404…` | Approved | 1 observation | 0 | 0 | 0 | 0 | 2 (0) |

All three return Approved on an adjudicated clean target, which is the correct verdict; recall is
N/A on a clean target. One observation asserts a further consequence of the pre-fix defect. The
adjudicator first ruled it false, tracing the shutdown path at the pinned head; the pull-request
review disputed that with a concrete interleaving, and on re-examination the adjudicator found the
interleaving real, reproduced it with a standard-library program using the same primitives, and
amended the ruling to **supported and sub-threshold**: a true statement about the scope of the
pre-fix defect, already foreclosed by the change under review, filed as a non-blocking observation.
It is an observation, not a finding, and earns no recovery credit either way. The other observation
states a true coverage fact and asserts no defect. Every explicit safety claim in the
three summaries is supported; one packet misstates a test count, which the adjudicator recorded and did
not treat as a claim about the code.

### `<target-B>` — register adjudicated buggy with one defect, truth becomes `v2` with two

| Packet | Status | Raw items | Findings | Recovered | Sufficient fix | Partial fix | False findings | Unresolved | Action / priority errors | Unsupported safety claims |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `48d5db81…` | Changes Requested | 2 findings | 2 | D1, D2 | D2 (D1 before amendment 1) | D1 | 0 | 0 | 0 / 0 | 0 |
| `d5fbbc87…` | Changes Requested | 1 finding | 1 | D1, D2 | D2 | D1 | 0 | 0 | 0 / 0 | 0 |
| `8814c28e…` | Approved | 2 observations | 0 | — | — | — | 0 | 0 | 0 / 0 | **1** |

**A novel defect was confirmed and the register is versioned.** One packet asserted a second
defect the `v1` register does not carry, on the same added lines: a different input state under
which the change silently accepts what the merge-base rejected with an error. The adjudicator did not take the packet's word for it
and did not count the second packet that raises the same case as evidence. It appended a temporary
test to the clone, ran it at the pinned head and at the merge-base, saw the silent acceptance at
the head and the error at the base, restored the file, and recorded both commands with their
output; the transcript in the seal carries the raw test output. That is independent confirmation,
so `D2` enters the truth register as `v2` for this target and **every packet on the target is
scored against `v2`**, including the two that raised it and the one that did not. The target's
classification is unchanged — buggy stays buggy — so the frozen clean/buggy mix is not disturbed;
its defect count moves from one to two, which changes the recall denominator for every attempt on
it, and that is disclosed here rather than applied silently. `D1` is the register's original
defect, reproduced by the adjudicator at the pinned head with the register's own trigger.

Two packets recover both defects, and each earns sufficiency credit for `D2` only. One raises them
as two separate findings; its `D1` fix was first judged sufficient, and the pull-request review
pointed at a manifestation the request does not reach — the terminating positional being itself
the final one — which the adjudicator reproduced at the head and the merge-base and traced through
the guard that fires before the edited arm, amending that fix ruling to **partial**. The other
bundles both defects under one finding with one proposed fix that restores `D2`'s outcome and not
`D1`'s; the table records the bundled second concept explicitly, with its own fix ruling. A partial
fix recovers a concept and earns no full credit, so both packets recover two concepts and hold one
sufficiency credit each. The third packet returns Approved with zero findings on a target carrying a
material, maintainer-confirmed regression; its two observations are true and sub-threshold, and
its Approved line is an **unsupported explicit clean claim**. Under the preregistration's section
8 that status is false clean on a buggy target whatever else the packet says; the join is #153's.

Raw against concept, on this target: five raw items, three of them findings, recover two concepts
across two packets — four recovery credits from three findings, because one finding carries two —
and two sufficiency credits. Zero raw false findings, zero false concepts, zero unresolved rulings,
zero action or priority errors.

### Across both targets

| | Packets | Raw items | Raw findings | Raw false findings | False concepts (findings) | False non-finding items | Unresolved | Outstanding |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<target-A>` | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `<target-B>` | 3 | 5 | 3 | 0 | 0 | 0 | 0 | 0 |

No packet published a raw false finding. The screen's zero-false-finding gate is therefore not
tripped by any packet; whether any arm fails it is a join #153 makes, and whether any arm's recall
means anything on a grid with eighteen cells unattempted and three of eight attempts invalid is the
question #153 answers, not this bundle. **No comparison, no arm, no ranking appears here.**

## Unmasking cues

Seven cues are recorded and none is resolved. Six are the adjudicator's, one per packet except one
packet with two, kept verbatim in the sealed tables; the public summary lists only that a cue exists
and which packet it concerns, because a cue quotes the packet's prose:
they concern the presence or absence of an `items` array, phrasing that suggests a verification
step in the pipeline, and terminology in a status line. The seventh is the coordinator's, known
before grading and recorded rather than discovered: only one arm in this pilot published
structured `items` beside its body, and two of the six packets carry them. Blinding was not
perfect and this bundle does not claim it was; what it claims is that no cue was resolved, no
mapping was opened, and every ruling was frozen before either could be.

One further masking gap belongs to the packets rather than to this stage: the builder masked
repositories, urls, pull-request references and object ids, and left an issue number in one
packet's prose in the clear. It identifies the target, which the packets never hid, and says
nothing about the arm.

## Fidelity of the adjudicators

Both sessions verified on every assistant line to `claude-sonnet-5` at `high` — 81 lines on
`<target-A>`, 101 on `<target-B>` across every segment — with one root user message and no
summary or compact record, and no path outside the permitted roots named by any tool call
([`metering/`](metering/)); the audit classifies a file tool's path against the recorded roots
whether or not the file still exists, and reports a shell token that no longer resolves as
unresolved rather than inside (none occurred). The `<target-B>` session was resumed once, for
thirty seconds, to add one field to one item: the schema had allowed one concept per item and its
own basis already said that item covered two. The pre-resume table is sealed beside the final one;
the diff is that one field. Both sessions were resumed once more for the amendments below. The
mapping was closed throughout.

The `<target-B>` adjudicator temporarily appended tests to a file in the clone and switched its
branch to run one at the merge-base, then restored the file and returned to the pinned head; the
clone's tracked tree was clean and on the pinned head when the session ended and when this bundle
was written. That is inside what its execution note permitted, and it is recorded because the
preregistration's isolation rules for *reviewers* forbid tree mutation and an adjudicator is not
a reviewer.

Two limits on the coordinator's own blindness are named above rather than smoothed: it read both
registers, and it saw one ledger line naming a slot and an arm for one attempt.

## Cost

Charged to the epic ledger's protected grading and closeout reserve, phase `grading`, ticket 152,
as two reservations of $3.50 for the grading sessions and two of $1.50 for the amendment
sessions, each followed by its settlement ([`metering/ledger-events.json`](metering/ledger-events.json)):

| Session | Turns | Transcript at frozen rates | Runtime self-report | Charged |
| --- | --- | --- | --- | --- |
| `<target-A>` grading | 33 | | $0.7084362 | **$0.7084362** |
| `<target-A>` amendment 1 | 13 | | $0.5643804 | **$0.5643804** |
| `<target-B>` grading, with the 4-turn resume | 39 + 4 | | $1.1246248 | **$1.1246248** |
| `<target-B>` amendment 1 | 20 | | $0.6193592 | **$0.6193592** |
| `<target-A>` all segments | | $1.268829 | $1.2728166 | |
| `<target-B>` all segments | | $1.740020 | $1.7439840 | |
| **Total** | | | | **$3.0168006** |

Settled at the larger of the two figures, as the preregistration's settlement rule says; the
self-report exceeds the transcript by about $0.004 on each, the untranscripted small-model
request the probes identified. Headless sessions write the one-hour cache tier, priced ×2.0. The
ledger stands at **$50.3304587** actual with $0.164316 of retained uncertainty carried unchanged
from the closeout (this stage retains none of its own); **$6.9831994** of the $10.00 protected
reserve remains for #153's synthesis. No reservation is outstanding.

## Amendments after review

The pull-request review of this bundle, itself a fresh context without the arm mapping, disputed
two rulings with concrete arguments. Neither was accepted on authority: each argument was relayed
verbatim to the adjudicator that made the ruling, as an unproven claim to check against the code,
with the frozen table left read-only and the mapping still closed. Both adjudicators changed
their ruling on the evidence and wrote an amendment naming what the original missed:

- **`<target-A>`, one observation, false → supported and sub-threshold.** The original refutation
  assumed the shutdown path could never lose the contended resource to the worker it was racing;
  the code gives no such ordering guarantee, cancelling a deferred callback does not stop one that
  has already started, and a standard-library reproduction of the same primitives showed the
  interleaving five times out of five. The observation is true about the pre-fix defect's scope
  and non-material at the head.
- **`<target-B>`, one fix ruling, sufficient → partial.** The requested edit sits in an arm that a
  guard fires before, when the terminating positional is itself the final one. The adjudicator
  reproduced that case failing at the head and passing at the merge-base, so it is a manifestation
  of `D1`, and the request restores the other manifestations but not this one.

An amendment replaces whole item records by `item_ref` and may add concepts; `grade.py derive`
lays it over the frozen table and records what it applied. The frozen tables and
[`rulings-freeze.json`](rulings-freeze.json) are byte-unchanged and still verify;
[`rulings-freeze-2.json`](rulings-freeze-2.json) covers the tables, both amendments and the amended
derived fields together, and is the freeze #153 checks. The amendments, the prompts and launch argv
that produced them, the reproduction program and the full transcripts are sealed under
[`sealed/amendment-1/`](sealed/amendment-1/).

The same review found three defects in the script, all fixed with regression cases: recovery and
fix credit now come from supported material **findings** only, so a question, observation or
hygiene note ruled material is counted where it is and earns neither; `freeze --check` now requires
the supplied set to match the freeze record exactly, refusing an omitted or duplicated file, so an
incomplete verification cannot pass the gate; and the read audit now classifies a file tool's path
against the recorded roots regardless of whether the file still exists, reporting a shell token
that no longer resolves as unresolved rather than inside.

## What this bundle does not do

- It launches no reviewer run and authorises none; `dispatch_authorized` is `false`.
- It opens no redaction map and joins no arm, replicate, validity, completion or cost to a ruling.
- It sets no threshold, changes no default, names no winner and grades none of the closeout's
  own outcomes.
- It does not certify blinding; it lists the cues.

## For #153

Verify the freeze first: decrypt [`sealed/`](sealed/) and [`sealed/amendment-1/`](sealed/amendment-1/),
check each `SHA256SUMS`, then run `grade.py freeze --check` against
[`rulings-freeze-2.json`](rulings-freeze-2.json) with the two tables, the two amendments and
`derived-fields-amended-1.json`, and against [`rulings-freeze.json`](rulings-freeze.json) with the
tables and `derived-fields.json`. Then open #151's redaction map and join, per packet: arm,
replicate, completion and cost from the map; operational validity from the closeout's fidelity
assessment; and the per-attempt fields from the sealed `derived-fields-amended-1.json`, which are
in the shape `score_attempts.py` reads. Score against `v2` for
`<target-B>` and report the `v1` figures beside it. Treat the two no-packet attempts and every
unattempted cell as missing, never as clean.

## Reproducing it

```sh
BUNDLE=docs/research/bounded-discovery-grading-2026-09-11
FROZEN=docs/research/bounded-discovery-runs-2026-09-08/manifest.json
RATES=docs/research/bounded-discovery-runs-2026-09-08/rates.json
WORK=~/.config/bounded-discovery/issue-152      # outside every checkout: its paths name targets
PACKETS=~/.config/bounded-discovery/issue-151/packets/grading-packets.json   # opened per packets/README.md

python3 $BUNDLE/scripts/grade.py --self-test
python3 $BUNDLE/scripts/grade.py split --packets $PACKETS --out-dir $WORK/inputs
python3 $BUNDLE/scripts/grade.py render --template $BUNDLE/prompts/adjudicator-template.md \
  --target-ref '<target-B>' --packets $WORK/inputs/packets-target-B.json \
  --register $WORK/inputs/register-target-B.md --clone $WORK/clones/<clone> --base-branch master \
  --work $WORK/adjudication/target-B --out $WORK/adjudication/target-B/rulings.json \
  --exec-note '<the target's execution note>' --budget '$2.50' \
  --out-prompt $WORK/adjudication/target-B/prompt.md
# launch: each target's launch record under metering/ carries the exact argv with paths masked
python3 $BUNDLE/scripts/grade.py validate --rulings $WORK/final/rulings-target-B.json \
  --packets $WORK/inputs/packets-target-B.json
# rulings-target-[AB].json names the two final tables and nothing else: the sealed set also
# holds the pre-resume table for target-B, which rulings-target-*.json would pick up
python3 $BUNDLE/scripts/grade.py derive --rulings $WORK/final/rulings-target-[AB].json --out $WORK/final/derived-fields.json
python3 $BUNDLE/scripts/grade.py freeze --rulings $WORK/final/rulings-target-[AB].json \
  --derived $WORK/final/derived-fields.json --out $BUNDLE/rulings-freeze.json
# after the review: the amendments as a layer, and a second freeze over the whole set
python3 $BUNDLE/scripts/grade.py derive --rulings $WORK/final/rulings-target-[AB].json \
  --amendment $WORK/final/amendment-1-target-*.json --out $WORK/final/derived-fields-amended-1.json
python3 $BUNDLE/scripts/grade.py freeze --rulings $WORK/final/rulings-target-[AB].json \
  --amendment $WORK/final/amendment-1-target-*.json --derived $WORK/final/derived-fields-amended-1.json \
  --out $BUNDLE/rulings-freeze-2.json
python3 $BUNDLE/scripts/grade.py seal --key ~/.config/bounded-discovery/issue-148/truth.key \
  --out-dir $BUNDLE/sealed $WORK/final/*
# the public summary is published from the amended derived fields; the original derived file
# exists only to check the original freeze
python3 $BUNDLE/scripts/grade.py publish --derived $WORK/final/derived-fields-amended-1.json \
  --rulings $WORK/final/rulings-target-[AB].json --frozen $FROZEN --known-cue '…' --out $WORK/rulings-public.json
python3 -c 'import json,sys; a,b=[json.load(open(p)) for p in sys.argv[1:]]; a.pop("published_at"); b.pop("published_at"); sys.exit(a!=b)' \
  $WORK/rulings-public.json $BUNDLE/rulings-public.json   # exit 0: the reproduced counts match
python3 $BUNDLE/scripts/grade.py audit --transcript <session>.jsonl --root … --out …
python3 $BUNDLE/scripts/grade.py meter --transcript <session>.jsonl --envelope result.json \
  --rates $RATES --tools docs/research/tools --out …
python3 $BUNDLE/scripts/grade.py scan --frozen $FROZEN $BUNDLE/README.md $BUNDLE/*.json $BUNDLE/metering/*/*.json
```

The registers were handed over as byte-identical copies of the plaintexts #148 sealed; their
digests match each slot manifest's `register_plaintext_sha256`. The two clones were made fresh
from the public repositories and pinned to the frozen head and merge-base OIDs, with the same
branch shape the reviewers had; the offline registry, module and build caches were provisioned
before dispatch so that no adjudicator command needed the network.
