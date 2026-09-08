# Target preparation for issue #148: four fresh targets and sealed ground truth

**Delivered 2026-09-08 (UTC) for [#148](https://github.com/kamui/skills/issues/148), part of the
[#138](https://github.com/kamui/skills/issues/138) epic.** This directory holds everything #149 needs
to freeze the experiment on four fresh pull-request targets: the criteria frozen before selection
([criteria.md](criteria.md)), the sealed candidate inventory and the public exclusion log
([exclusions.md](exclusions.md)), one manifest per slot with its common packet, selected scope, mirror
and clone recipes, execution allowance, setup results and access checks, the sealed registers, and
the metering of every charged helper. No reviewer, finder or verifier ran. The shared
[ledger](../ledger.json) carries every charged helper as a reservation followed by a settlement.

## What was prepared

| Slot | Pull request | Head / merge-base | Diff | Packet cutoff | Selected scope |
| --- | --- | --- | --- | --- | --- |
| slot-1 | [`clap-rs/clap#6212`](https://github.com/clap-rs/clap/pull/6212) "Fix value_terminator has no effect when it is the first argument", merged 2026-01-27 | `3604b1311` / `4ecbf54ac` | 2 files, +46/-0 | `2026-01-27T20:18:05Z` (merge instant (default); omitted: none) | S2: `clap_builder/src/parser/parser.rs` `Parser::parse` 130–144 |
| slot-2 | [`grpc/grpc-go#7417`](https://github.com/grpc/grpc-go/pull/7417) "xds/balancer/priority: Unlock mutex before returning", merged 2024-07-15 | `040de9b12` / `bdd707e64` | 1 file, +1/-0 | `2024-07-15T15:45:20Z` (merge instant (default); omitted: none) | S1: `xds/internal/balancer/priority/balancer.go` `run` 260–289 |
| slot-3 | [`nats-io/nats-server#6593`](https://github.com/nats-io/nats-server/pull/6593) "De-flake TestNRGTermDoesntRollBackToPtermOnCatchup", merged 2025-02-27 | `282d01c54` / `4791216cd` | 3 files, +34/-13 | `2025-02-27T17:07:22Z` (merge instant (default); omitted: none) | S1: `server/raft_chain_of_blocks_helpers_test.go` `RCOBStateMachine.applyEntry` 116–140 |
| slot-4 | [`nats-io/nats-server#7395`](https://github.com/nats-io/nats-server/pull/7395) "[FIXED] Mirror consumer data race", merged 2025-10-06 | `b81b039c3` / `78e2dacea` | 1 file, +2/-1 | `2025-10-06T11:29:49Z` (merge instant (default); omitted: none) | S1: `server/stream.go` `setupMirrorConsumer` 3146–3305 |

Slots are numbered by case-sensitive lexical order of `owner/repo#number` (criteria §4.4). The
manifests, packets and scopes carry no category, clean/buggy status, defect, leak SHA or later-fix
reference: that is all hidden truth, sealed under [sealed/](sealed/README.md) and revealed only after
every reviewer run has stopped. The four pull requests are now reserved for every later grid, in
addition to the reservation list in criteria §7.

## How the roles were kept apart

- **Curator** (the orchestrator session): hunted candidates from clone-history greps and forge
  searches, wrote each candidate's hypothesis, froze the inventory (commit `8e5fe3a`) and prepared
  mirrors, packets and provisioning. Its work is ordinary ticket work outside the measured
  experimental spend (design §6 convention), disclosed here.
- **Selector** (one fresh headless `claude-sonnet-5` / `high` session per target, tools `Read`,
  `Grep`, `Glob` only, no shell): received only `packet.md`, `diff.patch` and exported `head/` and
  `base/` trees, ran once, and its output is frozen as delivered. Every tool call is audited in
  `metering/selector-<label>/read-audit.txt`; none read outside its working directory. One frontier
  citation in slot-3's output characterizes a lock as a hazard, drawing on the pull request's own body
  text; it is frozen as delivered, and #149 should judge whether that sentence over-cues the finder. The selectors
  ran **before** the adjudicators, so no register existed anywhere on the machine during selection,
  and every plaintext of hidden truth (inventory, and for the two replacement runs the registers and
  hypotheses that already existed) was removed from disk for the duration (ciphertext and key
  remained; the sessions had no shell to decrypt with).
- **Adjudicator** (one fresh headless `claude-sonnet-5` / `high` session per target, with shell,
  `gh`, `git`, `go` and `cargo`): received the curator's hypothesis as an unproven claim plus the
  full staging clone, and wrote the register directly into evaluator-only storage. Registers were
  sealed as delivered; the curator did not edit them.

Model and effort were verified on every assistant line of every helper transcript with
`agent_effort.py` (`metering/*/effort.txt`).

## Deviations from the frozen criteria, dated

1. **Selector before adjudicator (2026-09-08T06:08Z).** Criteria §9 lists adjudication (step 5)
   before the selector (step 6). The selectors ran first so that no register existed on disk during
   selection. The order of the two steps does not change what either role may see; it removes a read
   surface. Original text retained in criteria.md.
2. **Selectors could not write files (06:08Z).** The selector sessions were given no `Write` tool, so
   the outputs the template asked for under `output/` were delivered in each session's final
   message instead. That message is saved verbatim as `selector-output.md`; `selection.json` is the
   fenced JSON block parsed from it; two sessions attempted a `Write` call that the tool policy
   refused (noted in their audits). The selection rule and inputs were unchanged.
3. **Frontier edges beyond two hops (06:12Z).** Two selectors supplied edges a third hop out or
   duplicating a symbol. `scope.json` keeps the first two hops as the frozen bound requires and lists
   the rest under `unavailable_under_bound`; nothing was reselected.
4. **Ledger events before the `--ticket` option (06:08Z).** `scripts/budget.py` hard-coded ticket
   147 on every event; the four selector reservations (`c7c482f4…` to `91533161…`) therefore say
   `ticket: 147`. The option was added and every later #148 event says 148. Events were not rewritten.
5. **Adapter tests decoupled from the live ledger (06:16Z).** `scripts/fixtures.py` and
   `scripts/test_adapter.py` copied the live `ledger.json` as their synthetic base, so the suite
   failed as soon as real reservations existed. They now start from the ledger's opening state
   (`opening_state`). The full adapter suite passes; see the pull request.
6. **Two replacements for one slot (06:28Z and 06:41Z).** For one of the four slots the independent adjudicators ruled the first two candidates in the sealed inventory order outside the shape that slot requires (criteria §3 E11), so the third candidate in that order fills it. Which slot, which shape and what each ruling found are hidden truth: the two excluded registers are sealed for audit (`sealed/excluded-*.enc`), the selector runs on the two excluded candidates are retained as discarded pre-freeze spend, and `exclusions.md` records the replacements without naming the slot or the reasons. The replacements followed the frozen order; no candidate was chosen after the fact.
7. **Internal spend target exceeded (06:52Z).** Criteria §8 aimed this ticket at $9.00 of the $15.00 pre-freeze subtotal; the two replacements brought the metered total to $9.90. The $15.00 subtotal was never at risk: every helper was reserved before launch and settled from its transcript, and the largest single session cost $1.41.
8. **Packet worker-model line (06:08Z, recorded after review).** Criteria §9.3 named
   `--subagent-model sonnet`. The packets were built with the literal value
   `<the model your dispatch names for that worker>` instead, so that the line the builder renders
   ("pass `model: "…"` explicitly on every call") does not pre-empt #149's choice: design §2 gives arms
   B and C a worker configuration different from A while every arm must receive byte-identical
   packets. The string is deliberate, not an unfilled placeholder; each manifest records it under
   `packet.subagent_model_line`. #149's dispatch template must name the model for each worker and
   state that this packet line means the dispatch's value. The packets are not rebuilt: the selectors
   ran on these bytes and the frozen scope hashes bind to them.
9. **Staging clone reuse for slot-2 (recorded after review).** The full bare clone of `grpc/grpc-go`
   used as the staging source for slot-2's mirror and packet manifest is the one made for the #137
   preparation on 2026-09-07 (`/tmp/qual137/staging/grpc-go.git`), refreshed with `git fetch` on
   2026-09-08. A staging clone is only a source of upstream objects; the truncated mirror holds two
   refs and passed its negative checks. The other three targets use clones made for this ticket.

## Cross-target hazard

Two targets live in `nats-io/nats-server`. The later one's history contains the confirming fix for
the earlier one's defect. Each target has its own truncated mirror, so neither mirror contains the
other's answer, but a reviewer of one that could read the other's clone or mirror would see it.
#149's isolation controls must keep the two targets' mirrors and clones mutually unreadable, or run
their cells with the other mirror unmounted. This is recorded in the sealed inventory as well.

## Budget

| Item | Sessions | Metered | Evidence |
| --- | --- | --- | --- |
| Scope selectors | 6 headless (four slots plus two replacement candidates), `--max-budget-usd 1.50` each | $3.76 | `metering/selector-*/usage.json`, ledger reservations and settlements |
| Adjudicators | 6 headless (four slots plus two replacement candidates), `--max-budget-usd 2.50` each | $6.13 | `metering/adjudicator-*/usage.json`, ledger reservations and settlements |
| Provisioning, mirrors, packets | no model cost | $0.00 | this README and the manifests |
| **Ticket total charged to the epic ledger** | | **$9.90** of the $15.00 pre-freeze subtotal (criteria §8 targeted at most $9.00) | [ledger.json](../ledger.json) |

All helper sessions were headless and wrote the one-hour cache tier, priced ×2.0 by
`transcript_usage.py` as the transcripts report it; `requests.jsonl` per helper reproduces each
`usage.json` total. Remaining pre-freeze allowance for #149's probes: $5.10.

## Files

- `criteria.md` — frozen roles, categories, E1–E11, selection rule, selector protocol, sealed storage,
  budget stop rule, per-target checklist (commit `285e4cf`, before any selection)
- `exclusions.md` — every examined-and-excluded candidate with the criterion it failed, no categories
- `sealed/` — ciphertext of the inventory, the four slot registers and leak sets, the two excluded
  candidates' registers and the slot map; `SHA256SUMS` of the plaintexts; the reveal procedure
- `slot-1/` … `slot-4/` — `manifest.json`, `packet.md`, `scope.json`, `selection.json`,
  `selector-output.md`
- `prompts/` — the selector and adjudicator templates (public; no truth)
- `metering/` — per-helper `usage.json`, `row.md`, `requests.jsonl`, `effort.txt`, `transcripts.txt`
  and, for selectors, `read-audit.txt`
- `tools/extract_requests.py` — the per-request extractor used for `requests.jsonl`

Working files on the preparation machine (not delivery): `/tmp/bd148/` (staging clones, mirrors,
packets, selector inputs, provisioning trees, logs, transcripts under `~/.claude/projects/-private-tmp-bd148-*`)
and the evaluator-only directory `~/.config/bounded-discovery/issue-148/` (key, plaintexts, hypotheses,
adjudicator prompts).

## Handoff to #149

[handoff.json](../handoff.json) records this stage as `ready` with the four slots assigned and
`dispatch_authorized: false`. #149 must: pin this directory's commit; re-bind each `scope.json`'s
`source_hash` to its `SourcePacket` ArtifactRef without changing the content; run the metered
capability probes inside the remaining pre-freeze allowance; establish reviewer-tool isolation
covering files, processes, history, network, other checkouts and the evaluator-only key directory;
and keep the two nats-server targets mutually unreadable. The registers stay sealed until #152/#153.
