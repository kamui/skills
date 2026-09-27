# Review blind-e798ca

### Item 1
Location: packages/react/src/field/control/FieldControl.tsx:105-115
Claim: Controlled sync path skips validation invalidation when the value becomes null/undefined. A controlled `Field.Control`'s `value` prop transitions from a defined value to `null` (the only reachable variant; an `undefined` value flips the field to uncontrolled in the same render, per `isControlled = valueProp !== undefined`) while an earlier async or debounced `validate()` call for the previous value is still pending.
Consequence: `serializedValue` collapses to `undefined` for a `null` value, so the new `useValueChanged` callback's early return (`if (serializedValue === undefined) return;`) skips `validation.change`. `validationCommitIdRef.current` is therefore never incremented for this transition, so the earlier in-flight `commit()`'s stale-id check (`useFieldValidation.ts:269`) still matches when its promise resolves, and `setValidityData` publishes a validation result for the old, no-longer-current value. This is the exact defect class the PR's own body says it fixes ("a pending async validator for the old value could still publish"), reintroduced for this one transition by the very guard this diff adds; dirty/filled also never update for it. Confirmed by an independent fresh-context verifier, which also traced that no other effect in FieldRoot.tsx invalidates validation for this transition.
Fix: Don't let the controlled sync path exit before invalidating/re-running validation when the value serializes to `undefined`; for example normalize with `serializedValue ?? ''` before the comparisons and the `validation.change` call, the way the dirty check already does, instead of returning early.

### Item 2
Location: (no file)
Claim: The PR body's claim that array-valued controlled inputs failed the dirty-baseline comparison "by reference" the same way numeric values did is not exercised by any test in this diff; the `String(value)` normalization would apply the same fix, but this is untested.
Consequence: packages/react/src/field/control/FieldControl.tsx:86; pr-body/"Array values failed the same way by reference".
Fix: —

### Item 3
Location: (no file)
Claim: The supplied `code-infra-dashboard` CI comment reports double-digit percentage paint regressions in components this diff never touches (Menu, Select, Dialog, Combobox); with no plausible causal path from a two-file Field.Control change, this reads as benchmark noise rather than evidence of a product regression.
Consequence: packet section 6, comment 2 (code-infra-dashboard, 2026-08-10T13:19:19Z): "Menu open (500 items) | 84.59 ms 🔺+25.80 ms (+43.9%)".
Fix: —
