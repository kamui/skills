# Observations from running the pilot

Things the six cells established about the **frozen configuration itself**, separate from
anything about the arms. None of these is a result: no recall, cost-ratio or quality comparison
appears here, and the pilot's outcomes stay sealed until every reviewer run has stopped.

They are recorded because #151 runs eighteen more cells under the same configuration and should
not rediscover them, and because two of them add noise to figures the screening gates use.

## 1. The allow list refuses the command forms the execution notes suggest

The frozen `--allowedTools` list admits a shell command only when it matches an allow-listed
**prefix**. The per-target execution notes tell the cell to run, for example,

```
GOMODCACHE=/tmp/bd148/gomodcache GOCACHE=... GOFLAGS=-mod=mod GOPROXY=off go vet ./pkg/
```

which does not start with `go`, so `Bash(go:*)` does not match it and the call is denied. The same
is true of `env ... go vet`, of `cargo` with a `CARGO_HOME=...` prefix, and of every compound
`a && b` — the dispatch template already warns about the last of these.

**Observed, not inferred.** Every cell hit it. One arm C cell accumulated seven denials in a row
working through `GOMODCACHE=... go vet`, `go -C <clone> vet`, `export ...; go vet`,
`env ... go vet`, `GOPROXY=off go vet ./...` and `GOFLAGS=-mod=mod go vet` before the attempt
ended.

**It is friction, not a blocker.** Tests do run: every cell that completed executed its focused
commands successfully — `ok google.golang.org/grpc/...` and a 74-test `cargo test` — by routing
through the allow-listed interpreter, `python3 -c "...subprocess..."` or a small script written
into the work directory. Between 3,995 and 4,856 build-cache files were written per cell, and
every clone was verified clean afterwards, so the execution allowance was genuinely exercised
and the no-mutation rule held.

**Why it matters to the gates.** The turns spent discovering the workaround are charged to the
attempt, and how quickly a cell finds it varies. That is noise in billed cost and in elapsed
time, both of which the screen uses — the matched cost ratio directly. It falls on all three arms
alike, so it does not bias one arm, but it widens the spread.

**Not changed mid-grid.** Adding `Bash(env:*)` or a broader pattern would alter the execution
permissions every arm receives, which the preregistration fixes as identical across arms. Running
part of the grid under one allow list and part under another would be a worse defect than the
friction. #151 should inherit the list unchanged; a future frozen study should widen it.

## 2. A provider error costs the per-role cost split, through the frozen meter

When a session hits an API error the harness writes an assistant line whose `model` is
`<synthetic>`. `transcript_usage.py` drops that line, but `meter_split.py` counts it as a second
model and refuses the transcript as mixed-model — so an attempt that hits a 502 loses the per-role
split the method asks for, and falls back to the runtime self-report alone.

`meter_split.py` is pinned by digest in #149's manifest, so this runner does not edit it. It
filters the synthetic lines into copies, records how many it removed, and meters the copies. The
removed lines carry no usage, so no cost moves. One cell needed this; it recovered a split naming
both models.

## 3. A single-turn session may not flush its assistant lines

A container session that answers in one turn and exits immediately can leave a transcript with no
assistant line at all, which makes `agent_effort.py` unable to verify its model and effort and
leaves `meter_split.py` with no model to price. A multi-turn session flushes normally, and every
benchmark cell is many turns, so no cell is affected — but a short probe run against this harness
cannot be metered or fidelity-checked from its transcript, and should be metered from its result
envelope.

## 4. The reconciliation residual is real in every cell, and mostly explained

Every cell billed more than its transcripts account for, as #149's probes predicted. The residual
decomposes into the part the result envelope attributes to a model that never reached a transcript
— `claude-haiku-4-5-20251001`, between $0.0035 and $0.0040 per cell, larger than the probes'
$0.0013 because these sessions are larger — and a remainder. The remainder was $0.0000000 in one
cell and under a tenth of a cent in another; the one cell with a materially larger unexplained
remainder was the attempt a 502 cut off mid-stream, where the final request was billed but its
transcript record was truncated. Settlement charges the larger source in every case.
