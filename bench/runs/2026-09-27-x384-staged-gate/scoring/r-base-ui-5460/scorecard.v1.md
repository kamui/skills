# Scorecard: r-base-ui-5460, mapping v1

Register v1 (1bb5b63fb98b), rubric v1, scored at 2026-09-27T20:08:28Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 5c8e512bfb7e99d2378394dbfaeacd71539cc757ddb88415b676a1fec374bf76; session e59866be-8fd4-4441-94fa-4f714cb5ed7f; read audit clean.

## att-001 (review-code-sonnet-high-enforced-lifecycle), blind-3f410f

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "NumberFieldInput's useValueChanged callback only clears errors and revalidates; unlike FieldControl's combined callback it does not also call setDirty/setFilled, because NumberFieldRoot's setValue already applies those". Checked: NumberFieldInput.tsx:101-110 calls only clearErrors and validation.change; FieldControl.tsx:105-115 also calls setDirty/setFilled. NumberFieldRoot sets dirty in setValue (line 254) and filled via an effect on value (lines 120-121), so the claim is broadly accurate (filled comes from an effect rather than setValue). It is a comparative observation that asserts no defect or consequence in the PR, and touches neither the onBlur normalization problem (GT-r1) nor the mount-time filled problem (GT-r2). Below the finding threshold.

## att-002 (review-code-sonnet-high-enforced-lifecycle), blind-903847

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The PR's own CI performance-benchmark comment reports large regressions (e.g. Menu open +43.9%, Select open +28.5%, Dialog mount +23.0%) for interactions this two-file FieldControl diff does not touch, and a +88B (+0.02%) bundle-size delta." The figures match packet.md section 6, comment #2, verbatim. The item itself says the diff does not touch those interactions, so it does not attribute a behavioural regression to the PR. It is an accurate observation about CI noise and bundle size with no material consequence, and it is unrelated to GT-r1 or GT-r2.

## New candidates

None.
