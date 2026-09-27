# Scorecard: r-base-ui-5460, mapping v1

Register v1 (1bb5b63fb98b), rubric v1, scored at 2026-09-27T11:05:10Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 4a68510ae855184616b9963b03dc56ed00c1d7b528cbc405e740a11394fa0806; session 0da15c22-2a27-47d3-a55c-462400ea9fd8; read audit clean.

## att-001 (review-code-sonnet-high-isolated-control), blind-5fb8ce

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "No test in this diff exercises a controlled array `value`, though the PR body claims the fix also resolves array-value dirty tracking." This is an accurate test-coverage observation: the PR tests cover only the numeric case, and String(value) applies uniformly at FieldControl.tsx:86. It asserts no defect and no behavioural consequence, so it falls below the finding threshold.

## att-002 (review-code-sonnet-high-isolated-control), blind-9bda50

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery True; false clean False.

- item-0: `non-material`, fix n/a, priority error True, group none. Quote: "Controlled non-string values reach validate() as strings on submit ... validate receives the string \"5\" instead of the number 5 ... pass the raw controlled `value` (not `serializedValue`) as the third argument to useRegisterFieldControl". The fact is true: FieldControl.tsx:90-97 now registers serializedValue. The register lists this exact claim under non_defects: "Real observable change via registration.value, but blur/change/Enter paths already passed the DOM string at merge-base, validate is typed (value: unknown), and Form values come from the DOM either way; consistency, no demonstrated failure." Because validate logic that relies on the number type was already broken on the blur, change and Enter paths, the claimed material breakage is not a new defect. This is an accurate observation below the threshold, not a registered defect.

## att-003 (review-code-sonnet-high-isolated-lifecycle), blind-e798ca

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery True; false clean False.

- item-0: `false-finding`, fix n/a, priority error n/a, group none. Quote: "A controlled Field.Control's value prop transitions from a defined value to null ... the new useValueChanged callback's early return (if (serializedValue === undefined) return;) skips validation.change ... publishes a validation result for the old, no-longer-current value. This is the exact defect class the PR's own body says it fixes ... reintroduced". The register lists this as a non-defect: "useValueChanged skips serializedValue === undefined, so clearing a controlled value to undefined/null is ignored", which is outside the contract. null is not a valid value: FieldControlProps extends BaseUIComponentProps<'input'>, and React's input value type is string | number | readonly string[] | undefined. React itself treats value={null} as uncontrolled and warns about it. The claim of a regression ("reintroduced") is also unsupported. At merge-base (main) no path reacted to programmatic value changes, so a pending async result for the old value could publish on any programmatic change, and this diff makes the null case no worse. The material consequence is therefore not supported within the component's contract.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "array-valued controlled inputs ... is not exercised by any test in this diff; the String(value) normalization would apply the same fix, but this is untested." This is an accurate test-coverage observation that the item itself concedes is behaviourally fine. It is hygiene, below the threshold.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "reports double-digit percentage paint regressions in components this diff never touches ... this reads as benchmark noise rather than evidence of a product regression." This is an observation about the CI bot comment (packet section 6, comment 2) that asserts no defect. It is non-material.

## att-004 (review-code-sonnet-high-isolated-lifecycle), blind-0a74e9

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-r2`, fix partial, priority error False, group none. Quote: "Mount effect never clears data-filled when a Field.Control remounts empty ... mounting Field.Root > Field.Control key=\"a\" value=\"foo\" then swapping to Field.Control key=\"b\" value=\"\" leaves data-filled present at head, where the merge-base's version ... clears it." This is GT-r2 manifestation 1 (controlled remount empty, probe E), with the right mechanism: the mount effect at FieldControl.tsx:99-103 only sets filled true and dropped the merge-base valueProp === '' branch; useValueChanged does not fire on mount. Fix proposed: "setFilled(!!validation.inputRef.current?.value) unconditionally". That clears stale filled for the remount-empty case, but it still reads only the DOM value, so for a controlled value on render={<div />} (manifestation 2, probe G) inputRef.current.value is undefined and filled is set false instead of true. Required outcome is that mount-time filled reflect the controlled value prop independent of the rendered element, so the fix is partial.

## New candidates

None.
