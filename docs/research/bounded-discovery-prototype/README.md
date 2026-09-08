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

The design is ready for implementation; runtime and benchmark readiness remain unestablished.
[handoff.json](handoff.json) records this stage's disposition. #147 supplies fake-worker and
isolation checks; #149 supplies metered toy probes. The paper fixtures test routing and
record identity only. They are neither new targets nor evidence of improved recall.
