# Scorecard: r-base-ui-5460, mapping v1

Register v1 (1bb5b63fb98b), rubric v1, scored at 2026-09-27T07:10:27Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 0649e80041fed20421d1a9d7ef47c1372e46fd9cc32655ae5cf99aa9f8bb1c6e; session aeb9803b-9347-4970-9e20-8280e975a137; read audit clean.

## att-001 (review-code-sonnet-high), blind-d293ad

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "Controlled `Field.Control` inputs now render twice per keystroke instead of once when `validationMode=\"onChange\"` ... the PR discloses and accepts this cost". This is accurate and matches the PR body's performance table (packet §3) and the register non_defect ruling that the extra render is a 'Documented, measured trade-off ... not a behavioural defect.' The note that the onChange figure has no test is test-coverage hygiene. It identifies neither GT-r1 nor GT-r2, so it falls below the finding threshold.

## att-004 (review-code-sonnet-high), blind-1f9fe4

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery True; false clean False.

- item-0: `false-finding`, fix n/a, priority error n/a, group none. Quote: "Submit-time validate() now receives a stringified value for controlled non-string fields" ... "silently breaking type-sensitive validate logic ... This is a regression in a default, previously-working path". The underlying fact is true: clone/packages/react/src/field/control/FieldControl.tsx:86-97 now registers `serializedValue` (String(value)) with useRegisterFieldControl instead of the raw `value`. But this is exactly the register's non_defect 'Submit-time validation now passes the serialized string instead of the raw controlled value to validate', ruled 'Real observable change via registration.value, but blur/change/Enter paths already passed the DOM string at merge-base, validate is typed (value: unknown), and Form values come from the DOM either way; consistency, no demonstrated failure.' The item's material consequence (broken or throwing type-sensitive validators as a regression) is hypothetical: such a validator already received strings on every blur/change/Enter path at merge-base, so no failure is shown, only a type difference. It asserts a material regression the adjudication rejected, and it does not touch GT-r1 (blur-normalization dropping the validation result) or GT-r2 (mount-time filled from the controlled value).
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The extra render per keystroke in `onChange` validation mode ... reads as an accepted, documented trade-off rather than an undisclosed regression." This is accurate: the PR body's performance table discloses it, and the register lists 'One extra render per keystroke in onChange mode' as a documented trade-off, not a defect. It is an observation with no defect claimed, so it falls below the finding threshold.

## New candidates

None.
