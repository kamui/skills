# Bounded discovery adapter

This delivers the executable prototype for [#147](https://github.com/kamui/skills/issues/147).
The supported runtime is a finite synthetic worker with read tools. The Claude entry point
returns an immutable no-cell runtime stop. It does not issue provider requests.

Fake runs check scheduling, packet construction, IDs, file-tool access and accounting.
They do not establish discovery quality, stronger-worker settings or Claude isolation.
[DESIGN.md](DESIGN.md) remains the schema and policy authority. The comparison policy is
commit `83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6`, tree
`bea6be143582e75bada966ee85964623ef31f167`. Later production repairs stay outside these fixtures.

## Run and inspect

Run from this directory with Python 3.9 or newer on macOS or Linux:

```sh
python3 scripts/fixtures.py --out /tmp/discovery-example --case duplicate --arm C
python3 scripts/adapter.py --config /tmp/discovery-example/config.json \
  --scenario /tmp/discovery-example/scenario.json --out /tmp/discovery-example/run
python3 scripts/adapter.py --config /tmp/discovery-example/config.json \
  --scenario /tmp/discovery-example/scenario.json --out /tmp/discovery-example/no-cell \
  --runtime claude
python3 scripts/test_adapter.py
```

Use a new destination for each fixture and invocation. The first adapter call exits 0.
The Claude call exits 1 with a `stopped-runtime` handoff and all 24 cells unattempted.
Content violations and delivered stops exit 1 with a reason on stdout. Unreadable input or a
failed helper exits 2 with the command or path on stderr. Stop the step on either nonzero
exit and inspect `handoff.json`. A stop does not authorize another benchmark attempt.
Unreadable config/scenario or an existing destination fails before artifact creation.

The fake ledger is a disposable copy marked `synthetic: true`. Its arithmetic is synthetic
usage, not experimental spend. Fake work against the real epic ledger is refused.
The real [ledger.json](ledger.json) remains at $0 incurred and $0 reserved.
Ordinary implementation work is outside measured experiment costs.

## Files and interfaces

| File | Responsibility |
| --- | --- |
| `scripts/adapter.py` | One cell's transitions, concurrent C discovery, structural checks, compact packets, retained transcripts, stop and closeout |
| `scripts/fake_worker.py` | Trusted synthetic responses and finite read tools; no model, shell, network or arbitrary code tool |
| `scripts/budget.py` | Shared POSIX lock, reservations/settlements, protected reserve, attempt/context/replacement registration |
| `scripts/fixtures.py` | Disposable common inputs, explicit paper judgments, canaries and synthetic responses |
| `scripts/test_adapter.py` | CLI checks of transitions, failures, isolation, budgets and evidence records |

The adapter calls the baseline's `scripts/validate_review.py --emit-batch` by pinned path.
Fixtures export that exact Git blob into disposable inputs. The adapter compares its bytes
against the pin before executing it. There is no forked publisher. It saves `rendered.json`
without a forge write. The existing `../tools/transcript_usage.py` and `../tools/agent_effort.py`
run by path with captured hashes. Their parsers are not copied.

The adapter requires complete request records before freezing a report because the existing
helpers can skip malformed lines or accept empty transcripts. It retains malformed bytes
and their unsettled allowance instead of turning a partial report into an empty clean ledger.

## Executable config

`fixtures.py` produces a complete example. UTF-8 JSON uses `bounded-discovery-v1`.
Each ArtifactRef has exactly `uri`, `sha256` and `access`. SHA-256 covers stored bytes.
URIs are local paths under explicit permitted file/directory roots. Source/target access is
`reviewer-common`. Output is a new directory outside input roots. The adapter owns distinct
role stores; callers cannot alias worker output stores.

| Config fields | Required checks |
| --- | --- |
| `experiment_id`, `attempt_id`, `cell_id`, `arm`, `replicate` | Nonrecycled attempt ID; A/B/C; replicate 1 or 2; membership in 24 unique ordered cells |
| `predecessor`, `replacement_ordinal`, `replacement_evidence` when replacing | Latest same-cell invalid predecessor and explicit protocol/input evidence; no replacement for a substantive result or timeout |
| `policy_commit`, `skill_tree`, `method`, `design`, `prototype`, `prototype_files` | #136 OIDs; hashed method/design; all executed adapter/budget/fake-worker files match their pins |
| `source`, `target`, `scope` | Common-preparation provenance; source identity including boolean `merged`; matching target OIDs; source-bound scope |
| `primary_task`, `primary_config` | One common primary task and model/effort/permissions config |
| `workers`, `verifier_tasks`, `verifier_task` | A/B/C settings; equal B/C settings and verifier task refs |
| `finder_config`, `finder_task` | Only C; config equals B's worker config |
| `contexts` | Primary, initial verifier, follow-up verifier, plus finder for C; distinct safe IDs; no reuse across ledger attempts |
| `clone_root`, `permitted_input_roots`, `isolation` | Existing permitted clone; disjoint input/output; fake work requires `finite-fake-tools` |
| `helpers`, `ledger` | Hashed baseline validator and research helpers; shared ledger path |
| `ordered_cells`, `session_shape`, `cache_policy`, `completion_mode` | Explicit controls; render-only required |
| `limits` | Positive attempt/request/headroom dollars, root/worker/finder seconds, request/command counts, whole-attempt/finder/per-request token allowances |
| `rates` | Input/output USD per million, cache-write/read multipliers, observation time and evidence |

SourcePacket carries repository/PR, canonical URL, state/merged, posting/review identities,
base ref/OIDs, cutoff, permitted history and common text. It references PR/spec/rules,
diff/manifest/ranges, dependencies and execution policy. Provenance explicitly records
complete common preparation without arm output. The synthetic builder does not prepare
real targets; #148 owns their packets and independent selection evidence.

SelectedScope carries ID, source hash, selection mode/context, supported alternatives,
rationale/citations, timestamp, roots, frontier, maximum hops and exclusions. Roots and
destinations name path, symbol and inclusive lines. Frontier edges name a known predecessor,
caller/callee/contract kind, citation and destination. Paths cannot escape the clone; ranges
are ordered; at most two expansion hops are allowed. Finder reads fit selected ranges.
Primary and verifier reads may inspect the entire permitted clone.

Synthetic settings, task text and rates are mechanism-test placeholders. Passing fake
validation is not a #149 preregistration, proof of provenance or proof of effective settings.

## Worker records and transitions

The scenario maps roles to phases. Primary phases are `discovery`, C's `admission`,
`reconcile` and `final`. Finder has only `discovery`; verifiers have only `verification`.
Unknown workers, a third verifier and finder verification/restart phases fail.

A response has `report` and optional `tools`, `observed`, `usage`, `delay_seconds`,
`missing` or `malformed` fault injection. `requests` can supply sequential continuation
responses. Every request gets an ID, saved input/transcript, usage meter and effort report.
Responses are trusted fixture data visible to the synthetic process, not real-worker prompts.

Reports declare `complete`. Discovery also declares `pass_complete`; primary declares
`manifest_complete` and `first_falsification_complete`. A complete final provider record is
necessary to freeze. A freeze records context, phase, input/output hashes and coordinator time.
Later primary phases create new artifacts.

C runs primary/finder subprocesses concurrently, waits for both freezes and finder termination,
then records cross-feed and sends compact claims/citations to primary admission. A/B use the
discovery report as their first admission ledger and can verify before remaining reconciliation.
Empty C discovery creates no extra baseline trigger.

Admission/reconciliation/final reports carry claims and rows. Claims preserve local/canonical
IDs, explicit origin, source IDs/freezes, model dedup decision, compact claim fields, raw
citations, inspected evidence, admission/original text, verification requirements and
publication dispositions. Rejected concerns also retain safety premise, asserted scope and
disposition evidence. The model decides semantic identity, eligibility and truth.

Evidence availability is `inspected`, `not-inspected`, `unavailable` or `unknown`.
`not-inspected` needs an explicit complete-access-trace assertion. Missing narration stays
unknown. Whether an assertion or safety premise is supported remains a model/evaluator judgment.
High-risk rows carry kind, surface, premise/scope, inspected/disposition evidence, trigger
decisions, required/received batches, rulings and fidelity classification.

Stage snapshots preserve primary reports. `coverage.json` separately joins IDs to actual
batch receipts, returned rulings and gaps, so a declared empty receipt list cannot hide a batch.
An initial/follow-up decision either requests a mode with candidate/row IDs and baseline
evidence, or supplies phase/clause, survivors, trigger booleans, affected IDs and a no-batch
reason. Required IDs cannot be labeled policy-permitted omissions. Missing dispatch and
missing ruling are distinct. Related-only work cannot independently trigger an initial batch.

Verifier packets exclude origin endorsements, dedup narratives, private support and full
discovery reports. Candidate verdicts remain `confirmed`/`refuted`; row rulings remain
`holds`/`re-open`. Refutations retain their baseline basis; unresolved needs a settling fact.
Each ruling needs scope and evidence. Scripts never decide whether a ruling is true.

Final records preserve pending work at the two-batch cap. A required rendered claim needs
the latest confirmation for the same compact claim bytes. Changed/reopened claims cannot
reuse old confirmation. Publication records match payload finding IDs. Mandatory gaps cannot
become complete coverage. The pinned validator checks and renders the would-be payload.

## Access boundary and audited limitations

Finder tools actually attempt the allowed range, an excluded same-file range, primary-private,
other-attempt and hidden-truth canaries, and a symlink to hidden truth. Only the allowed range
succeeds. Shell requests receive `tool unavailable`. Verifier tools can read the excluded range.

This boundary belongs to the finite fake read tool. The trusted Python process retains the
OS user's ambient privileges. It is not an OS sandbox for arbitrary Python, repository tests
or Claude with shell/network access. Prompt omissions, directory names and `--add-dir` do not
establish independence. Real isolation must cover files, tools/processes, history, network,
inherited descriptors and other checkouts before a faithful run.

## Accounting and terminal artifacts

`budget.py` locks a stable sibling lockfile and atomically replaces a reconciled snapshot.
Events append IDs and previous-event links without rewriting old events. Actual spend,
outstanding reservations/uncertainty, protected closeout reserve and the new allowance must
fit the frozen/absolute cap. Pre-freeze cannot exceed $15; the absolute cap cannot exceed $150.
Before configuration freeze, pre-freeze reservations use the total ceiling when the frozen
cap is null and zero protected reserve when that reserve is null. Other phases require both
values to be set. Settlement uses the reservation's recorded phase, including for probes.

Each request reserves a conservative token-priced allowance plus one-call/cancellation
headroom before launch. Concurrent requests cannot share money or token capacity. Worker
requests charge the same attempt ceiling directly, without a second whole-attempt reservation.
Settlement uses the meter's lower bound as known cost and retains upper-minus-lower uncertainty.
Incomplete streams/timeouts retain their unproven reservation. No repeated or over-bound
settlement is accepted. Missing usage is not refunded.

Grading/closeout reservations transfer protected capacity atomically instead of counting it
twice. Zero-cost attempt-open/close events enforce unique contexts, at most two concurrent
cells, 27 attempts and three replacements.

Deadlines include remaining root and worker-phase time. Peer failure cancels later dispatch
and continuations; running fake peers are killed and reaped. The fake has no descendant-process
tool. These checks do not establish provider cancellation or hard token controls. Real dispatch
needs an enforceable conservative request allowance or demonstrated hard token controls.
Closeout preserves the first worker failure's disposition and reason. A peer's cancellation
record names that failure; only an expired deadline records a timeout.

`timing.json` uses #130's unchanged four fields: `completion_mode`, `root_dispatched_at`,
`payload_validated_at` and `completed_at`. Stop time remains in Attempt/Handoff. The shared
usage helper consumes the sidecar for `usage.json`. Worker spans never replace root elapsed.
`meter-status.json` marks censored stops, retained allowances and fake zero-cost read tools.

Every invocation delivers config/scenario, request inputs/transcripts/meters, freezes, events,
stages, coverage, Attempt, ledger snapshot, timing, Handoff and a SHA-256 manifest. Stops also
write `stop.json`, preserve available unadmitted discoveries and list unattempted cells.
No payload is needed. Exclusive creation prevents another invocation from overwriting artifacts.

`outcome-join.json` is evaluator-only and leaves recovery/sufficiency unset.
[outcome-fixtures.json](evidence/outcome-fixtures.json) separately preserves DESIGN fixture R.
Neither historical truth nor this join enters worker packets. #150/#151 can propagate a
no-dispatch closeout and #152 can grade available claims without successful grid payloads.

## Minimal #149 capability probes

[runtime-inventory.json](evidence/runtime-inventory.json) retains uncharged local version/help
evidence. Claude Code is 2.1.263. Its help advertises `--agents`, `--effort`,
`--max-budget-usd` and restricted tool controls. These do not establish effective child
settings, independence or exact token enforcement.

Reuse PR #183's startup-definition observation as a hypothesis. Before paid toy calls,
reconcile the shared ledger and reserve a positive allowance with one-call headroom and
closeout capacity inside the existing $15 pre-freeze subtotal. No child gets a new budget.

1. Start one tiny session with the intended verifier definition supplied at startup. Request
   distinct primary/child settings. Retain every request and run `agent_effort.py` with explicit
   expectations across all records. Record requested/observed model/effort and unavailable or
   mismatched states. Per-call fields or mid-session definitions are not sufficient evidence.
2. In disposable isolated clones, prove freshness and attempt primary, other-attempt, truth,
   symlink, absolute-path, history and network canaries through actual enabled worker tools.
   Prompt-only checks or unexplained trace gaps fail readiness.
3. Try two operations against shared capacity where only one fits, then cancel the allowed
   operation. Verify process/provider termination and settle all continuations against retained
   usage and dated actual rates. Leave unknown usage reserved.
4. Reproduce role/root totals from transcripts and #130 timing. Demonstrate a bounded request
   allowance if hard token controls are unavailable.

Stronger-worker selection remains #149's prospective choice. A failed probe produces a stop
with evidence and incurred spend. This ticket authorizes no paid grid, default promotion or
model-quality conclusion.
