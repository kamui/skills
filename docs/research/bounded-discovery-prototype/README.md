# Bounded discovery prototype

Design handoff for [#146](https://github.com/kamui/skills/issues/146), part of the active
[#138](https://github.com/kamui/skills/issues/138) experiment. No reviewer, finder, selector,
or paid capability probe was dispatched for this handoff.

- Read [DESIGN.md](DESIGN.md) before implementing the adapter (#147), preparing targets
  (#148), or freezing the experiment (#149). It owns packet schemas, isolation, scheduling,
  stage records, fixtures, and terminal artifacts.
- Reuse [ledger.json](ledger.json) for every chargeable experiment operation across the epic.
  Its $150 total ceiling includes the $15 pre-freeze allowance; children get no new budget.
- Apply the [one-shot method](../code-review-one-shot-method.md) for scoring and accounting.
  #149 owns the final revision/configuration pins, numeric worker limits, and dispatch gate.

[handoff.json](handoff.json) records the completed design stage. Runtime and benchmark
readiness remain unestablished. #149 supplies metered toy probes. The paper fixtures test
routing and record identity only. They are neither new targets nor evidence of improved recall.

The executable #147 adapter is documented in [ADAPTER.md](ADAPTER.md). It supplies unpaid
fake-worker CLI checks and an explicit no-cell stop for an unprobed Claude runtime.
[Evidence](evidence/README.md) records the implementation checks and retained examples.
Runtime readiness and benchmark dispatch remain #149's gate.

Target preparation for #148 lives in [targets/](targets/README.md): the frozen selection criteria,
the sealed candidate inventory and registers, four per-slot manifests with packets, selected scopes,
mirror and setup recipes, access checks and metering. Hidden truth is committed only as ciphertext;
see [targets/sealed/README.md](targets/sealed/README.md).
