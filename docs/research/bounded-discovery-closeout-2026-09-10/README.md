# Bounded discovery — closing out the stopped pilot

**Delivered 2026-09-10 (UTC).** This bundle is [#151](https://github.com/kamui/skills/issues/151),
the closeout stage of the [#138](https://github.com/kamui/skills/issues/138) epic. Its prerequisite
[#150](https://github.com/kamui/skills/issues/150) delivered `stopped-incomplete` in merged
[PR #197](https://github.com/kamui/skills/pull/197), and that handoff authorises closeout only.

**No experimental reviewer run was launched here, and none may be launched from this handoff.** The
eighteen unattempted grid cells stay unattempted. [`handoff.json`](handoff.json) carries
`dispatch_authorized: false`.

**Disposition: `closeout-delivered`, on an experiment that remains `stopped-incomplete`.** The
closeout is complete; the experiment is not, and this bundle does not pretend otherwise.

| Artifact | What it settles |
| --- | --- |
| [gate.json](gate.json) | that every reviewer run that ever started has terminated, recorded before anything sealed was opened |
| [seal-open.json](seal-open.json) | when the pilot evidence was decrypted, and against which digests |
| [fidelity-assessment.json](fidelity-assessment.json) | `pilot/actual-fidelity`: what is established for each of the eight attempts, and what was never retained |
| [reconciliation.json](reconciliation.json) | every charge in the epic against the single ledger, with five discrepancies and two retained bounds |
| [manifest.json](manifest.json) | all twenty-four planned cells, attempted and unattempted |
| [packets/](packets/) | #152's anonymous grading packets, sealed, plus the no-packet manifest |
| [handoff.json](handoff.json) | the stage record #152 reads |

## The gate, and why it comes first

Nothing may read the pilot's sealed outcomes until every reviewer run has stopped. That gate was
recorded at **2026-09-10T07:03:56Z** and committed on its own, thirty seconds before the seal was
opened at 07:04:26Z, so the ordering is in the history rather than asserted inside a later file.

Seven checks pass. No process outside this session's own ancestry names a cell container, the
coordinator or a cell workspace; no cell container is live; no attempt workspace survives anywhere
under the user's home; all eight attempts opened on the ledger are closed; no reservation is
outstanding; the eighty-event chain is unbroken; and nothing was appended after the last attempt
closed.

Two limits are stated rather than smoothed. The container runtime is not running, which establishes
that no cell is executing and nothing at all about how each one exited — the cells ran under
`docker run --rm`, so a terminated cell leaves nothing to list either way. And the gate names its
own cell root on its command line, so it excludes its own process ancestry by walking the parent
chain, and reports how many processes that excluded rather than matching itself.

The raw `ps` and `find` captures stay outside the repository: a command line can name a slot. Only
counts and digests reach [gate.json](gate.json).

## Historical fidelity: unresolved, with the missing evidence named

`pilot/actual-fidelity` has been blocked since PR #197 found that the coordinator fixes cannot
establish what the original attempts did. This assessment reads the eight attempts out of the seal
and **recomputes** every observable dimension rather than trusting the record each attempt wrote
about itself.

**Established, for all eight.** Every retained transcript verifies to the frozen model and effort
for its role — primary at `claude-sonnet-5`/`high` in every arm, verifiers and arm C's finder at
`claude-opus-5`/`high` where the arm calls for them. Every session opens with exactly one root user
message and carries no summary or compact record, so no context was inherited or resumed. Every
absence gate, preparation attestation and read audit passed, with no read outside the permitted
roots. And the frozen-input chain holds three links deep: the dispatch template against #149's pin,
each rendered prompt against the raw digest sealed beside it, and the same file against the HMAC
published in the public cell summary.

**Not established, and named rather than smoothed.**

- **The launch argv was never retained.** The requested `--model`, `--effort`, `--max-budget-usd`,
  `--restricted` and allow-list values cannot be read back for any attempt. What survives is
  indirect: the rendered dispatch prompt with its execution allowance, the permission denials the
  restricted layer actually produced, and a settled cost inside the frozen ceiling. That is not the
  same as establishing that every arm received identical allowances.
- **No per-role cost split exists.** Every transcript metered as `unassigned`, so primary, finder
  and verifier spend cannot be separated in an arm that runs one model — which is exactly arm A.
- **No per-command network judgment was recorded.** The read audit checked paths, not whether a
  command reached the network outside the proxy.
- **Position 4 dispatched no verifier and recorded no no-batch reason.** The pinned policy may
  legitimately dispatch none, but the design asks for the reason and it was not kept.

Under the frozen rule an unobservable setting is not a pass, so the six settled attempts carry
`unresolved`: **no violation was observed, and none is certified faithful either.** The two attempts
already closed as invalid stay invalid on their recorded basis — one launch refused before any model
request, one primary lost to a provider 502 before it wrote its arm C freeze artifact.

The budget stop at position 6 stays a measured result. It is not infrastructure invalidity and is
not replacement-eligible.

| Attempt | Arm | Validity | Completion | Settled (USD) |
| --- | --- | --- | --- | --- |
| position-01-attempt-1 | A | invalid | stopped-runtime | 0.0000000 |
| position-01-attempt-2 | A | unresolved | complete | 3.8595330 |
| position-02-attempt-1 | B | unresolved | complete | 3.8777270 |
| position-03-attempt-1 | C | invalid | stopped-runtime | 1.5838690 |
| position-03-attempt-2 | C | unresolved | complete | 7.0003047 |
| position-04-attempt-1 | A | unresolved | complete | 4.5304828 |
| position-05-attempt-1 | B | unresolved | complete | 6.3671277 |
| position-06-attempt-1 | C | unresolved | stopped-budget | 9.0040632 |

**What this does to the grading.** An unresolved attempt is not a valid completed outcome, so under
preregistration section 8 it counts as missing rather than present. #152 grades the claims these
attempts produced without treating any cell as a clean comparison member; #153 applies the
conservative limits that follow.

## The accounting

The eighty-event ledger reconciles exactly: **$10.9378407** pre-freeze, **$0.1527100** of shared
setup charged once to the epic, and **$36.2231074** across eight review attempts sum to the
**$47.3136581** the ledger header carries, with a zero difference. The frozen event prefix still
hashes to #149's pin and the chain is unbroken. Both discarded predecessors keep their cost in the
total, and the attempt that settled at zero is counted as a settlement rather than dropped.

Two conservative bounds are retained rather than resolved, **$0.082158** each: the cancelled #149
probe that may never have recorded a request, and the #150 launch-shape check whose transcript was
deleted before it could be metered. They come off the remaining allowance too — a session that may
yet be billed is not headroom.

Five discrepancies are recorded and **none is repaired**, because the chain is append-only and a
stage record that was true when it was written stays as delivered:

1. The ledger header's `attempts_dispatched` counter reads 0 against eight `attempt-open` events.
2. All sixteen attempt-lifecycle events were written within twenty-seven milliseconds of each
   other, half an hour after the last attempt settled. **The ledger's own refusals — a reused
   attempt id, the twenty-seven-attempt cap, a replacement whose predecessor was not closed as
   documented invalidity — therefore never gated a pilot dispatch.** The money events were
   contemporaneous; the lifecycle is a reconstruction.
3. The ledger digest #150's sealed README publishes is this same ledger truncated to the events
   before that backfill. That explains it without changing it: the sealed and live copies are
   byte-identical to each other.
4. One attempt carries an unexplained residual above one per cent of its settled cost, already
   settled at the larger source, so no charge is understated.
5. No attempt carries the per-role split settlement was asked to take from the transcripts.

**Could a repair fit?** Re-running the six unresolved cells would cost **$34.6392384** at measured
rates against **$92.5220259** available, so the money fits. It would need **six replacements against
the one that remains**. Preregistration section 6 governs that case — when required invalidation
exceeds the allowance, stop and close out the partial experiment — so this ticket closes out and
dispatches nothing. Raising the allowance is not this ticket's to do.

## The twenty-four-cell manifest

[manifest.json](manifest.json) carries every planned cell: six attempted in the pilot, eighteen
never dispatched. Each attempted row carries its attempts in order with the predecessor each
replacement replaced, the validity and its basis, the completion, the settled charge and whether it
reconciles against the ledger, whether the attempt produced claims, and what timing is available.
The eight attempts reconcile against the eight settlements on the ledger, well inside the
twenty-seven-attempt limit.

An unattempted cell's outputs are **unavailable and stay unavailable** — it counts as missing in the
screen, never as present. A stopped attempt reports root elapsed with its duration censored at the
stop, and no row converts a censored duration into completion.

Every row is keyed by **schedule position**. Naming the six attempted cells would disclose the pilot
pair; naming the eighteen unattempted ones would disclose it by elimination. Neither appears.

## The grading packets

Six packets and a two-attempt no-packet manifest, in [packets/](packets/), with their own
[README](packets/README.md). They keep every visible finding's prose, trigger, claimed consequence,
remedy, status and decisive evidence verbatim, and drop the position, arm, model, replicate,
validity, completion and cost into a sealed redaction map.

They are **sealed rather than published**, and the reason is worth stating plainly: masking the arm
is achievable, masking the target is not, because grading needs the file paths and symbol names that
name it. Publishing the pilot's packets would name the two slots it ran on, and the public selection
rule turns that pair into the clean slot. This is **label masking, not guaranteed blinding**, and
the packets say so — including the one structural tell that survives, that in this pilot only one
arm published structured items beside its body.

## What #151 changes about the previous stages: nothing

#150's bundle, its cell summaries, its sealed archive and the committed ledger are untouched. Its
`fidelity-review.json` still reads `blocked`, because it was true when it was written and that
finding's resolution is this bundle. The rule the pilot recorded for anyone publishing beside a
blind still holds and is applied throughout here: **a hash is only opaque when its input has real
entropy.** Every mask in the packets is a sequential token, never a digest.

## Scripts

Standard-library Python 3.9+, macOS and Linux, each with `--self-test`:

| Script | What it does |
| --- | --- |
| [closeout.py](scripts/closeout.py) | the stop gate, opening the seal behind it, the fidelity assessment, the reconciliation, the cell manifest, sealing and the handoff |
| [build_packets.py](scripts/build_packets.py) | the anonymous grading packets, their masking and their redaction map |

Every public artifact is scanned before it is written. The scan derives what must never appear —
each slot name, and each target's repository, url, pull request and object ids — from #149's frozen
manifest, and allows this repository's own public pins. Anything else that looks like an object id
is refused, because a whitelist of individually harmless fields is exactly what failed to catch the
digest leak the pilot found.

## Reproducing it

```sh
BUNDLE=docs/research/bounded-discovery-closeout-2026-09-10
FROZEN=docs/research/bounded-discovery-runs-2026-09-08/manifest.json
PILOT=docs/research/bounded-discovery-pilot-2026-09-09
LEDGER=~/.config/bounded-discovery/issue-150/ledger.json
WORK=~/.config/bounded-discovery/issue-151

python3 $BUNDLE/scripts/closeout.py gate --ledger $LEDGER \
  --cells-root /tmp/bd150/cells --raw-out $WORK/gate-raw-capture.json \
  --out $BUNDLE/gate.json
python3 $BUNDLE/scripts/closeout.py open-seal --gate $BUNDLE/gate.json \
  --seal $PILOT/sealed/seal.json --key ~/.config/bounded-discovery/issue-148/truth.key \
  --archive $PILOT/sealed/pilot-evidence.tar.gz.enc --into $WORK/evidence \
  --out $BUNDLE/seal-open.json
python3 $BUNDLE/scripts/closeout.py fidelity --gate $BUNDLE/gate.json \
  --evidence $WORK/evidence --manifest $FROZEN --bundle $PILOT \
  --salt $WORK/evidence/commitment-salt --out $BUNDLE/fidelity-assessment.json
python3 $BUNDLE/scripts/closeout.py reconcile --ledger $LEDGER --manifest $FROZEN \
  --evidence $WORK/evidence --fidelity $BUNDLE/fidelity-assessment.json \
  --bundle $PILOT --out $BUNDLE/reconciliation.json
python3 $BUNDLE/scripts/closeout.py manifest --fidelity $BUNDLE/fidelity-assessment.json \
  --reconciliation $BUNDLE/reconciliation.json --bundle $PILOT --frozen $FROZEN \
  --out $BUNDLE/manifest.json
python3 $BUNDLE/scripts/build_packets.py --evidence $WORK/evidence --frozen $FROZEN \
  --out-dir $WORK/packets
```

The packets are then sealed with `closeout.py seal` and the handoff written with
`closeout.py handoff`; the exact invocations are in the commits that added them. The extracted
evidence and the unsealed packets stay under `$WORK`, outside every checkout of this repository —
their paths, ledger and transcripts name slots.
