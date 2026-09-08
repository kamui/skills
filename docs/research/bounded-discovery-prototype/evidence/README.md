# Adapter evidence

Issue #147 delivered the synthetic adapter and a no-cell stop for unsupported Claude dispatch.
No paid worker, selector or benchmark cell ran. The shared experiment ledger remains unchanged.

- [checks.txt](checks.txt) records the adapter CLI suite, research helper checks and Python 3.9
  syntax validation. The suite includes all 23 named transition fixtures, A/B/C omission
  variants, concurrent budget contention, cap/freshness failures and actual canary reads.
- [index.json](index.json) indexes nine retained invocations in
  [fake-artifacts.tar.gz](fake-artifacts.tar.gz). Eight are completed synthetic C invocations,
  including incomplete mandatory-coverage output. The ninth is a no-cell Claude runtime stop
  against the real shared ledger, with zero incurred spend and 24 unattempted slots.
- [runtime-inventory.json](runtime-inventory.json), [claude-version.txt](claude-version.txt)
  and [claude-help.txt](claude-help.txt) retain the uncharged local capability inventory.
  Effective real-worker settings, isolation and cancellation remain unprobed.
- [outcome-fixtures.json](outcome-fixtures.json) preserves separate evaluator-side recovery
  and sufficient-outcome examples. The adapter does not grade claims or consume these outcomes.
- [implementation-handoff.json](implementation-handoff.json) identifies the delivered
  implementation and the runtime limitation for the downstream gate.

The archive preserves exact config/scenario, common input bytes, scripted responses, request
inputs/transcripts/meters, freezes, stage records, canary reads, timing, coverage, ledger,
rendered payloads and stop/handoff manifests. Each run's file manifest records SHA-256 hashes.
The pinned validator export is immutable test input from Git, not a maintained publisher fork.

Extract the archive to inspect it. ArtifactRefs preserve the original absolute fixture paths
as provenance. To locate retained bytes, replace the fixture-root prefix recorded in
`index.json` with the extracted `artifacts` directory. Do not edit hashed artifacts.
References to research helpers and historical reports resolve to tracked repository files.
For a fresh executable replay, generate a new fixture using [ADAPTER.md](../ADAPTER.md).

The canary result proves the finite fake read tool's access checks. It does not prove OS
confinement for Claude or arbitrary repository commands. #149 must establish actual controls
using the documented metered toy probes or propagate a terminal runtime stop.
