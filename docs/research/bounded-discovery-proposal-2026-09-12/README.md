# Bounded discovery — the proposed specification for a future study

**Status: `proposed`, awaiting qualification.** Nothing here is frozen, qualified or authorized to
dispatch, and merging it makes it none of those. No target is selected, no probe is run, no seal is
opened, no ledger is appended to and no historical artifact is changed.

This bundle is the specification deliverable of
[#207](https://github.com/kamui/skills/issues/207), the freeze gate a future bounded-discovery study
would have to pass. #207 is **blocked by [#199](https://github.com/kamui/skills/issues/199)**, which
stays open: #199 closes when #207's probes meet its ten requirements on the runtime and the targets a
study actually dispatches with — not when tooling lands and not because this document exists.

**A study may never be ticketed.** [#153](https://github.com/kamui/skills/issues/153) decided the
[#138](https://github.com/kamui/skills/issues/138) epic `inconclusive` for both candidate arms and
recommended no confirmation study. This bundle answers what such a study would have to look like
before anyone has to answer it under time pressure. It is not the decision to run one.

| File | What it holds |
| --- | --- |
| [SPECIFICATION.md](SPECIFICATION.md) | the proposal: hypothesis, arm invariants, model and effort candidates, evidence boundaries, the ten #199 requirements with their controls and tests, budget method, screening and stop rules, the evidence a freeze would need, every proposed change to the closed design with its justification, and the unknowns |
| [probes.md](probes.md) | the probe catalogue: twenty-seven probes, what each must establish, what refuses it, and which need paid model sessions. **None has been run.** |
| [readiness.json](readiness.json) | the same requirements in machine-readable form: status, controls, tests, probes, the evidence still required, and the open questions |
| [scripts/check_spec.py](scripts/check_spec.py) | checks that record against the repository it names, and refuses a status that claims a requirement is established |

## Where the rest of it lives

- The **prospective tooling** the requirements point at is
  [`bounded-discovery-readiness-2026-09-12/`](../bounded-discovery-readiness-2026-09-12/README.md)
  (PRs #205 and #206): launch retention, per-role settlement, the mechanical sandbox rule, the
  recorded-root shutdown gate, the uniform payload contract, the per-command network judgment and the
  ledger's terminal `stop`. Every one is exercised by synthetic tests only.
- The **closed grid** it proposes to succeed is the [#149 preregistration](../bounded-discovery-runs-2026-09-08/preregistration.md),
  the [#151 closeout](../bounded-discovery-closeout-2026-09-10/README.md) and the
  [#153 decision](../bounded-discovery-decision-2026-09-11/README.md). All three are unchanged by this
  bundle and are cited as history, never as current capability.

## Checking it

Standard-library Python 3.9+ on macOS or Linux. Unpaid, offline, and reading only this repository:

```sh
python3 scripts/check_spec.py             # the committed record against this repository
python3 scripts/check_spec.py --self-test # 16 CLI tests over synthetic records
```

`check_spec.py` refuses a control or test path that no longer exists, a test name a file no longer
defines, a `#199` gap that is missing or duplicated, a probe either list has drifted on, an
unresolved row that records no open question, and any status asserting that a requirement is
established, frozen, qualified or authorized. It checks the record's integrity. **It establishes
nothing about a runtime, a target or a blind, and a clean exit is not readiness.**

## What has to happen before anything runs

1. **A decision that a study is warranted at all.** #153 recommended none, and #207 records that entry
   condition. Everything below waits on it.
2. **Runtime requalification** — [`probes.md`](probes.md) group A, over a pinned runtime inventory.
   An unsupported or unobservable control stops the study.
3. **Fresh targets** — #148's criteria applied to new candidates, with the reservation set extended by
   the four revealed #138 targets, the two excluded registers and every pull request the revealed
   candidate inventory names.
4. **A budget** computed from requalified rates. No cap, ceiling or allowance is chosen here.
5. **A freeze** meeting [SPECIFICATION.md section 11](SPECIFICATION.md), ending in a recorded dispatch
   authorization. This bundle is not that authorization and cannot become one by being merged.
