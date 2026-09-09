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
frozen five-minute limit. **Measured, it does not.** The container reproduces #148's host timings:

| Command | #148 on the host | This container |
| --- | --- | --- |
| `go vet ./xds/internal/balancer/priority/` | exit 0, 7 s | exit 0, 7 s |
| `go test -count=1 -run 'Test/' ./xds/...priority/` | exit 0, 4 s | exit 0, 4 s (`ok`, 1.995 s) |
| `cargo test --offline --locked --test builder multiple_values` | exit 0, 74 passed, ~30 s build | exit 0, 74 passed, 28 s |

The reason is that the expensive, platform-independent part of each cache — the Go module cache and
the Cargo registry — carries over unchanged, while the build output each cell produces for itself is
the cheap part. The macOS `GOCACHE` is useless in Linux and is simply rebuilt inside the allowance.
Both clones were verified clean after these runs, so the execution note's "nothing added to or
changed in the clone" holds on this substrate too.

Provisioning therefore stays exactly what #148 recorded: the module and registry caches, copied
per cell so no two cells share mutable state, and **not** the build output. Each cell pays its own
~30 s test-binary build, which is what its execution note describes. The earlier draft of this
deviation asserted that cold caches would lengthen the cells; that was a prediction, it was wrong, and
it is replaced by the measurement above.

What remains true is narrower: elapsed time is still this harness's, not the policy's production
timing — because verification runs in the foreground in every arm by choice, which preregistration
section 10 already records as an interpretation limit. Token cost is unaffected and every arm carries
the substrate equally, so no gate moves.
