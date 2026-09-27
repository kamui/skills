# Review blind-5fb8ce

### Item 1
Location: (no file)
Claim: No test in this diff exercises a controlled array `value`, though the PR body claims the fix also resolves array-value dirty tracking.
Consequence: FieldControl.tsx:34's `serializedValue = value == null ? undefined : String(value)` is applied uniformly regardless of value type, and the same mechanism is exercised only for a numeric `value` by FieldControl.test.tsx's "clears dirty state when a numeric controlled value returns to its initial value".
Fix: —
