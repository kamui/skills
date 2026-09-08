# Bounded discovery runs — the frozen experiment

**2026-09-08 (UTC).** This bundle is the freeze gate of the
[#138](https://github.com/kamui/skills/issues/138) epic, delivered for
[#149](https://github.com/kamui/skills/issues/149). It fixes every value the grid is allowed to vary
before any reviewer, finder or verifier has run, and it records the metered capability probes that
establish the runtime controls the design depends on.

**Disposition: `ready`** ([handoff.json](handoff.json)).
[#150](https://github.com/kamui/skills/issues/150) runs the six-cell pilot,
[#151](https://github.com/kamui/skills/issues/151) the remaining eighteen. No benchmark cell has been
dispatched. The only model sessions charged here are the twelve probes; none of them reviewed a
target.

## Read in this order

- [preregistration.md](preregistration.md) — the frozen experiment: prerequisites, hypothesis, arms,
  the prospectively selected stronger worker, pins, probe results, isolation, cells and order,
  the budget and its ceilings, the screening rules, fidelity requirements, interpretation limits and
  dated deviations.
- [manifest.json](manifest.json) — the same thing machine-readable, with a digest for every file it
  names. `python3 scripts/verify_freeze.py` recomputes all of them plus the git pins, the
  scope-to-packet bindings and the ledger reconciliation.
- [dispatch-template.md](dispatch-template.md) — the exact launch commands and prompts for the
  primary, the arm C barrier and resume, and the finder.
- [probes/README.md](probes/README.md) — what each capability probe asked, what it observed, and what
  it cost.
- [handoff.json](handoff.json) — the stage record #150 reads.

## What the probes settled

| Established | Not established |
| --- | --- |
| a child worker really runs at a different model and effort when the definition is supplied at startup | that the stronger worker is stronger — that is the hypothesis |
| every worker context is fresh | |
| `--restricted` confines the file tools, including symlinks and Grep roots | that the shell is confined: an allow-listed interpreter reads any path that exists |
| an allow-list proxy blocks every forge fetch while the provider keeps working | that egress is closed: a raw socket to an IP address still connects |
| SIGTERM ends the session, its provider work and its continuations | |
| the dollar allowance stops a session, overshooting by at most one call | that any hard token control exists |
| two reservations against the same capacity admit exactly one | |
| the retained per-request records reproduce the runtime's own billed total | |
| the cell can write its payload and report — once `--allowedTools` names `Write` and `Edit` | |

The two "not established" rows are why the frozen isolation control is **absence** — the evaluator
key, the other slots' clones and mirrors, the other attempts' stores and every checkout of this
repository are off the machine while a cell runs, checked before and after by
`scripts/check_cell_isolation.py` — with a transcript and egress audit behind it that invalidates any
attempt which read or fetched outside its permitted roots.

## Scripts

Standard-library Python 3.9+, macOS and Linux, each with `--self-test`:

| Script | What it does |
| --- | --- |
| [verify_freeze.py](scripts/verify_freeze.py) | rechecks every pin, binding and ledger invariant in the manifest |
| [check_cell_isolation.py](scripts/check_cell_isolation.py) | the per-cell pre- and post-dispatch environment check |
| [egress_proxy.py](scripts/egress_proxy.py) | the allow-list egress proxy and its per-cell log |
| [meter_split.py](scripts/meter_split.py) | prices a mixed-model attempt per model and reconciles it against the runtime's figure |
| [score_attempts.py](scripts/score_attempts.py) | the frozen scoring and screen, with [eleven fixtures](scripts/scoring-fixtures.json) |
| [seal_schedule.py](scripts/seal_schedule.py) | resolved the pilot pair and the cell order from the sealed registers, and sealed them |

[scoring-example.md](scoring-example.md) renders one synthetic fixture so the scorecard's shape is visible without running anything.

## Sealed here

[sealed/schedule.json.enc](sealed/schedule.json.enc) is the resolved 24-cell order, encrypted under
#148's key because naming the pilot pair in the clear would narrow which slots are clean. Its
plaintext digest is in [sealed/SHA256SUMS](sealed/SHA256SUMS) and the reveal procedure is in
[sealed/README.md](sealed/README.md). Nothing else in this bundle is hidden.

## What this bundle does not contain

No result, no finding, no recall number and no claim about either arm. The tables in
`preregistration.md` are inputs and thresholds. The first outcome of this experiment will be #150's.
