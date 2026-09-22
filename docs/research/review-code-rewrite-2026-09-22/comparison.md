# Comparison manifest: baseline pin and matched cases

Drafted for [#329](https://github.com/kamui/skills/issues/329) and run by [#333](https://github.com/kamui/skills/issues/333). **This ticket launches no review.** The file holds reviewer inputs and run conditions only. Expected outcomes are in [expected-outcomes.md](expected-outcomes.md), which no working reviewer receives.

## Baseline pin

| | |
| --- | --- |
| Skill tree | `7387c169c9b5b23c5c679efb7110c9c07fc3f7f3` (`main`, PR #327 merged) |
| Workflow | `v5b-22` |
| Local record | `implementation-gate-record/1`, `implementation-gate-addendum/1` |
| Verifier modes | `candidate-only`, `complete-ledger`, `related-acquittal` |

Instruction size at the pin: word counts from `wc -w`. They cover instructions only, not code, evidence, or tool output.

| Load | Words |
| --- | --- |
| `SKILL.md` plus 15 runtime references | 22,046 |
| The four always-loaded files (`SKILL.md` 3,827, `review-rubric.md` 3,778, `review-record.md` 1,434, `rendering.md` 1,384) | 10,423 |
| Local review with changed tests and verification, primary load (the #328 figure) | 15,087 |
| Separate verifier context: `verifier.md` 2,219, `verifier-return.md` 531, and the `changed-tests.md` slice | ≥ 3,445 |
| `build_verifier_prompt.py --example` brief (candidate-only, one candidate, records included) | 4,476 |
| Helper text loaded at the baseline: `compose_review.py --example --profile implementation-gate` 444, `review_context.py --help` 324 | 768 |
| Draft entrypoint ([SKILL.draft.md](SKILL.draft.md)), body only | 1,134 |

The draft figure is the entrypoint alone. Measure the treatment's full load after #332, the same way, before any run.

## Arms

- **Baseline:** the skill tree at the pin above.
- **Treatment:** the skill tree after #330 to #332 activate the rewrite. Its full commit is pinned in #333 before the first attempt and never changed mid-screen.

Everything outside the skill tree matches between the arms.

## Matched conditions

- **Model and effort.** Primary and verifier run on the same model and effort in both arms. The default is `claude-sonnet-5` at `high`, as in the #137 grid. The owner may choose another pair before freezing, but both arms use it. Confirm per attempt from transcripts with `docs/research/tools/agent_effort.py`.
- **Harness.** One Claude Code version, headless. Sub-agents run with `run_in_background: false`, and `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` is set, as in #137.
- **Evidence access.** The same frozen packet, truncated mirror, and offline caches per case. No network access.
  - External historical cases (C1–C6) forbid builds and tests, as in their original runs.
  - kamui/skills cases (C7–C10) allow focused tests under `changed-tests.md`'s default bounds.
- **Inputs.** Identical caller inputs per case, as listed below. Reviewers never receive expected outcomes, prior scorecards, or this study's goal.
- **Order.** For each case, a seeded coin (`sha256("329-" + case id)`, lowest bit) decides which arm runs first. At most two attempts are in flight.
- **Usage capture.** Authoritative transcript usage per root and worker, captured with `docs/research/tools/transcript_usage.py`. Also capture `run-events.jsonl` and `run_events.py summarize` from both arms.

## Bounds

- **Attempts.** One baseline/treatment pair per case: 10 cases, 20 attempts. At most two replacement attempts, each a full pair member for a stopped or invalid run, for a hard maximum of 22. Failed and stopped attempts are counted and retained.
- **Spend.** Stop any attempt at $15 of authoritative usage. The screen's ceiling is $250, replacements included. Reaching a limit stops the screen, and the report is `inconclusive` for every case not yet paired.
- **Missing data.** A missing usage record, a missing transcript, or an unconfirmed model/effort makes that attempt invalid for cost comparison. It may still be scored for quality.

## Cases

"PR packet" means a frozen phase-1 packet supplied as the orchestrator input, with the target's prior review state as it stood at the pinned head.

| Id | Target | Head | Merge-base | Caller inputs | Categories |
| --- | --- | --- | --- | --- | --- |
| C1 | `redis/redis#15680` | `c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61` | `065d397030712fe216e795720ae0affd3211212c` | `one-shot`, `publishable`, PR packet (no issue; the prior approval and LGTM packet from [test-2](../prototype-runs-2026-09-01-test-2/README.md)) | historical recovery; high-risk safety premise (failover); buggy |
| C2 | `clap-rs/clap#6212` | `3604b13117cbb652c10bb44b228b300d543dcc80` | `4ecbf54ac314b6cd9a84d7e48350b71f6bd4c7ac` | `one-shot`, `publishable`, PR packet from [#138 slot-1](../bounded-discovery-prototype/targets/slot-1/) | ordinary parser false-clean risk; buggy |
| C3 | `trpc/trpc#5017` | `7dc04a7e94654dfad6ef1289dfe01a0a206fff3b` | `2abb2d5cd19740be37272dac6ad7fdd36244ae54` | `one-shot`, `publishable`, PR packet from [#137 (j)](../one-shot-qualification-2026-09-07/) | hygiene feedback beside a dismissed behavioral concern; buggy |
| C4 | `python/typeshed#9458` | `55dfb451101480275ae05f2f08d1a899a691a77d` | `8365b1aaefd46d506ca0dfe73e9721da2d03c566` | `one-shot`, `publishable`, PR packet with its originating issue, from the [holdout (c)](../prototype-runs-holdout/README.md) | unchanged-code requirement omission; buggy |
| C5 | `tokio-rs/bytes#698` | `7052d2454a2370ab9583f63711df89f3bd7bec83` | `ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401` | `one-shot`, `publishable`, the [recorded packet](../one-shot-effort-2026-09-06/g-bytes-698/packet.md); released 1.6.0 source at `ce8d8a0a029c0d296ade752ecc8c3e1ce9eee47f` in the mirror | released compatibility; mandatory verification; buggy |
| C6 | `grpc/grpc-go#7390` | `76ef33f44a600c3ed1a385979fd1dfbcade3fbb6` | `daab56344e612097fd50c46c433de5d9b6013837` | `one-shot`, `publishable`, PR packet from [#137 (m)](../one-shot-qualification-2026-09-07/) | clean high-risk control (concurrency); safety premise; clean |
| C7 | `kamui/skills#320` | `1956058ea055937ed812b1ea893a783521a2cda0` | `c7a7afca3cb1164c256eb44ae814ecf581352c40` | `one-shot`, `publishable`, PR packet frozen with no prior review state | fresh sample; buggy |
| C8 | `kamui/skills#325` | `0ea287f0c07fda09b9d063612353dcef37f38063` | `160d1201bed57d96de6fc8b1ae657bd098aa2de6` | `one-shot`, `publishable`, PR packet frozen with no prior review state | fresh sample; clean control |
| C9 | `kamui/skills` range `f738ad656890ae6f0021d6aa37cd1ff63ff4aaa5..6cac10d9a9f00a10437df9b8d4fc7c901563f428`, then continuation to `884f322ba607628fa6b36e3ff96e761befc554c9` | as stated | `f738ad656890ae6f0021d6aa37cd1ff63ff4aaa5` | `one-shot`, `implementation-gate`, specs `kamui/skills#279`, `#294`, `#295`; for the continuation, the reported fixed id from phase 1 and a check-evidence packet written at freeze | continuation; cross-version transition; buggy then fixed |
| C10 | C9's continuation with exhausted verification | a synthetic commit on `884f322…`, built at freeze | `f738ad656890ae6f0021d6aa37cd1ff63ff4aaa5` | As C9's continuation, but the supplied record reports both batches spent | exhausted verification; incomplete outcome |

### Case construction notes

- **C1.** Reuse test-2's truncated mirror and packet unchanged. This is the historical recovery in [evaluation.md](../prototype-runs-2026-09-01-test-2-fable/evaluation.md). There the v5a prototype found the defect through a clean-verdict verifier's aside plus a follow-up batch; no run at the baseline pin has been made.
- **C2.** This is #202's parser evidence. It is outside the named high-risk areas, so the treatment runs no safety-premise check here unless the primary finds a mandatory candidate. The case measures the recall tradeoff the epic accepts.
- **C7 and C8.** Freeze each packet from the forge as it stood before the first review on the pinned head. Exclude the published review and every later comment, so that neither arm sees the historical outcome.
- **C9.**
  - **Phase 1** reviews the range with the arm's own `implementation-gate`.
  - **Phase 2** continues from that arm's own record under `implement-publish`'s continuation procedure.
  - **Cross-version run.** One extra continuation reuses the *baseline's* phase-1 record, a version-1 chain, and continues it under the treatment. It is scored only for transition correctness, and it counts as one of C9's attempts only if it replaces the treatment's own continuation. Otherwise it is one of the two replacements.
- **C10.** At freeze, build one synthetic commit on `884f322…` that changes only `skills/implement-publish/SKILL.md` line 64, from "Attempt each write once; on an ambiguous result read the target before a single retry, then report the failure rather than writing again." to "On an ambiguous write result, retry the write until it succeeds." Seed a copy of each arm's C9 phase-1 record whose verification accounting shows both batches spent (`follow_up_spent: true` in version 1; both `allowance` flags true in version 2), and report C9's must-fix id as fixed. Record the construction in the freeze commit. Reviewers receive only the record, the delta from `6cac10d…` to the synthetic head, the fixed-id report, and the check-evidence packet.

## Scoring

Scoring follows #297's discipline. An independent adjudicator scores each attempt against expected-outcomes.md without seeing arm labels. The adjudicator records:

- recovery of each known blocker;
- false clean (`Approved` or `Needs Information` on a case with an unrecovered material defect);
- unsupported blockers;
- false `coverage=complete`;
- contract breaks (payload validation, trailer grammar, record or addendum schema, allowance reset);
- verification tasks and batches dispatched;
- elapsed time and authoritative cost.

The epic's acceptance section says which losses must be investigated before the rewrite is accepted: known-blocker losses, unsupported blockers, false complete coverage, and broken contracts.
