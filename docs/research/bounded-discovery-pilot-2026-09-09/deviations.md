# Deviations from the frozen inputs, dated

The preregistration's section 11 requires every departure from the freeze to be dated and recorded
rather than smoothed away. These are #150's. Numbering continues #149's list.

## 7. Cells run in a container, because host absence was unreachable (2026-09-09)

**Frozen control.** Preregistration section 5: the evaluator key and plaintexts, every other slot's
mirror, clone and staging clone, every other attempt's store and **every checkout of this repository**
are absent from the machine while a cell runs, checked before and after by
`check_cell_isolation.py`. Absence rather than confinement, because probe 7 showed an allow-listed
interpreter reads any path that exists and probe 2c showed a raw socket to an IP address bypasses the
egress proxy.

**What was observed.** The machine preparing this run holds 188 linked worktrees of this repository
plus its primary checkout, sharing a single object store that reaches `targets/README.md` — which
discloses the relationship between the two `nats-io/nats-server` slots — and the entire sealed bundle
at any commit. `~/.config/bounded-discovery/` holds the only plaintext registers and leak sets and a
`vault.tar.enc` encrypted under the key in that same directory, and no off-machine storage was
available to move it to. Deleting it would forfeit #152's and #153's ability to adjudicate at all.
The filesystem and git operations that would remove the checkouts were not available to the runner.

**What replaces it.** Each cell runs in a container built from a pinned image (`claude` 2.1.263, the
version the #149 probes measured, with the host's own `go 1.27.0` and `rustc 1.98.0` so the frozen
per-target execution notes stay true). The container mounts **only** the cell's own tree, at its
identical absolute path, and that target's private copy of the toolchain caches at the paths the
packet hardcodes. Nothing else from the host is mounted. `check_cell_isolation.py --phase
pre-dispatch` and `--phase post-dispatch` run **inside** the container against the host paths, and the
mount set is additionally asserted from `docker inspect` and retained with the cell.

**What this establishes and what it does not.** It establishes that the forbidden material was not
reachable through the cell's filesystem, which is the property the frozen control exists to secure,
and it is enforced by the kernel rather than by a flag the interpreter can walk around. It does
**not** establish unconditional absence: the material remains on the host, so the boundary is
conditional on the mount set being correct, where absence would have been unconditional. The mount
set is therefore recorded per cell as primary evidence rather than as a note. The preparation-phase
attestation over the clone's and mirror's complete object stores is unchanged and still runs on the
host while the evaluator material is present.

**Scope.** Every cell of the grid, not only the pilot, must run this way for the arms to stay
comparable. #151 inherits this deviation; a cell run under host absence and a cell run under container
mounts are not interchangeable within one comparison.

## 8. The container authenticates differently from the probes (2026-09-09)

The twelve capability probes ran as the host's own authenticated `claude` sessions. A container cannot
use the host's keychain credential, so cells authenticate with a separately provisioned token. Rates,
ceilings and metering are unchanged — `rates.json` is a rate card and `--max-budget-usd` behaves as
probe 4 measured — but the credential path differs from the sessions that established the runtime
controls, and an attempt's settlement is still taken from the larger of the runtime self-report and
the retained per-request records.

## 9. The execution allowance was re-measured on the container substrate (2026-09-09)

The per-target execution notes were provisioned and timed by #148 on macOS with warm caches, and the
concern going in was that a Linux container would start cold and push a focused command past the
frozen five-minute limit. **Measured, it does not.** Each pilot target's focused commands were re-run
inside the container and reproduced #148's host timings to within about a second, well inside the
five-minute per-command and ten-minute per-target allowances.

The per-command figures are **sealed rather than printed here**: a command names the package path of
the repository it runs against, and the set of targets the pilot exercised is exactly the pairing the
freeze seals. The table lives in the sealed archive alongside each cell's evidence, keyed by schedule
position, and #153 can read it at reveal.

The reason the concern did not materialise is that the expensive, platform-independent part of each
cache — the dependency source caches — carries over unchanged, while the build output each cell
produces for itself is the cheap part. A platform-specific build cache is useless in Linux and is
simply rebuilt inside the allowance. Every clone was verified clean after these runs, so the
execution notes' "nothing added to or changed in the clone" holds on this substrate too.

Provisioning therefore stays exactly what #148 recorded: the dependency caches, copied per cell so no
two cells share mutable state, and **not** the build output. Each cell pays its own test-binary build,
which is what its execution note describes. The earlier draft of this deviation asserted that cold
caches would lengthen the cells; that was a prediction, it was wrong, and the measurement replaces it.

What remains true is narrower: elapsed time is still this harness's, not the policy's production
timing — because verification runs in the foreground in every arm by choice, which preregistration
section 10 already records as an interpretation limit. Token cost is unaffected and every arm carries
the substrate equally, so no gate moves.

## 10. Attempts were claimed on the ledger after they ran, not before (2026-09-09)

`budget.py`'s `attempt_event` is the control that makes the attempt and replacement caps real: it
refuses a reused attempt ID, refuses a reused worker context ID, enforces the 27-attempt and
three-replacement limits and the concurrent-cell ceiling, and refuses a replacement whose predecessor
was not closed as documented invalidity. #150's issue text asks for exactly this — "atomically reserve
the complete next cell/worker bound".

The runner did not call it during the pilot. It reserved the dollar allowance, which is a different
control and enforces none of those things, so for the duration of the pilot those caps were bookkeeping
rather than enforcement. The defect was found in review, before publication.

Two corrections followed. The runner now claims the cell and its contexts through `attempt_event`
*before* the dollar reservation, so a reused ID or an unearned replacement stops a cell before it
spends, and `settle` closes the attempt with its disposition. And the pilot's eight attempts were
replayed into the chain in order, through the ledger's own checks, so #151 inherits enforcement rather
than an empty history.

The replay is honest about what it is: it does not pretend the checks were in force at dispatch time.
It did, however, change a reported fact. The handoff had recorded one replacement consumed, on the
judgment that position 1's refused launch measured nothing and so should not count. The ledger's rule
is that any second attempt at a cell is a replacement requiring a predecessor closed as invalid, and
the replay therefore counts **two of three**. The ledger's definition governs, and the narrative
judgment was wrong.
