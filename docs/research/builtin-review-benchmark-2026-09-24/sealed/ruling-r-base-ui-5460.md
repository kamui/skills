# Ruling: r-base-ui-5460

## Target

- Repository `mui/base-ui`, pull request #5460, "[field] Sync controlled value changes with field state". Author `atomiks`, who also merged it on 2026-08-13T11:23:20Z into `master` (merge commit `5c12af1accbad774f05ea51894966fa006f0d4d8`). Labels: `type: bug`, `component: field`. No linked issue (`closingIssuesReferences: []`). Licence MIT (`LICENSE`: "MIT License / Copyright (c) 2019 Material-UI SAS").
- Head `14d39e5d1ad6b7aca2fb067415dba09c6bea219b`. It is the only commit (`gh api pulls/5460/commits`). PR base `30b8ea2004fa999bed151204208676c6c0a9d261`. I computed the merge-base myself with `git merge-base 30b8ea20 14d39e5d` on a non-shallow clone: `30b8ea2004fa999bed151204208676c6c0a9d261`. The two agree.
- Manifest (`git diff --numstat 30b8ea20 14d39e5d`): 2 files, 223 changed lines.
  - `packages/react/src/field/control/FieldControl.test.tsx` +149 −6
  - `packages/react/src/field/control/FieldControl.tsx` +48 −20
- The PR promises (from its body):
  - `useValueChanged` owns the controlled path.
  - Programmatic changes update filled, dirty and validity.
  - The dirty baseline is serialized.
  - `details.cancel()` is honoured.
  - A value the consumer rejects or rewrites does not reach field state.
  - It accepts one extra render per keystroke in `onChange` mode.

## Verdict

2 material defects

## Defect register

### GT-r1: a controlled value normalized during blur discards the `onBlur` validation result

- **Where (head `14d39e5d`).** Everything below is in `packages/react/src/field/control/FieldControl.tsx`, in `FieldControl` (`Field.Control`), unless another file is named.
  - Lines 105–115 add `useValueChanged(serializedValue, () => { clearErrors(name); setDirty(…); setFilled(…); validation.change(serializedValue); })`.
  - `onBlur` at lines 161–167 calls `validation.commit(event.currentTarget.value)` when `validationMode === 'onBlur'`.
- **Callee** (`packages/react/src/field/root/useFieldValidation.ts` at head):
  - `change` (316–328) calls `commit(value, !validateOnChange)`. In `onBlur` mode that means `revalidate = true`.
  - `commit` increments `validationCommitIdRef` first (line 118).
  - In the revalidate branch (169–183), it returns when `state.valid !== false` (170). Otherwise, when `valueMissing` is false, it calls `publishAllValid(element, false)` (181) without running `validate`.
  - An in-flight async result is dropped when the commit id no longer matches (268–271).
  - `useValueChanged` (`packages/react/src/internals/useValueChanged.ts`) runs its callback in a layout effect whenever the value differs from the previous render.
- **Violated contract.**
  - `FieldRoot.tsx:291` JSDoc for `validationMode`: "`onBlur`: triggers validation when the control loses focus."
  - The PR scopes its new sync path to code-driven changes: "Setting the value from code, such as a clear button or a form library reset, updated the input text but not filled, dirty, or validity". Nothing in it promises that a blur-time rewrite cancels blur validation.
- **Trigger.**
  - Setup: `<Field.Root validationMode="onBlur" validate={v => String(v).includes('@') ? null : 'Invalid email'}>` with `<Field.Control value={value} onValueChange={setValue} onBlur={() => setValue(c => c.trim())} />` and `<Field.Error />`.
  - Action: type `"foo "`, then blur.
- **Consequence** (reproduced; see Reproduction):
  - **Sync validator.** The blur commit publishes "Invalid email". The trim changes `value`, and the layout effect calls `change('foo')`. That takes the revalidate path; the field is invalid and not `valueMissing`, so `publishAllValid` runs. The end state is `value="foo"`, no `aria-invalid` and no error text, and `validate('foo')` never runs. The user leaves an invalid field that reports valid, and the next blur will not happen.
  - **Async validator.** The blur commit's pending promise is retired by the commit-id bump in the `change` → `commit` call. That call returns at line 170 because `state.valid` is not `false` yet. Nothing is ever published for the blurred value.
  - **Not triggered without a rewrite.** The same field with no rewrite on blur (probe cases C and D) keeps its error at head. The defect needs the controlled value to change as a result of the blur.
- **Introduced by this PR.**
  - At merge-base `30b8ea20`, a prop change reached no validation path: only the mount effect keyed on `valueProp`, and it touched only `filled`. The blur error stays visible there (probe A and B pass at merge-base).
  - Upstream agrees. #5563 (`1e208a97`, by `atomiks`): "The blur half is a regression from #5460" and "With `validationMode="onBlur"`, a blur handler that normalizes the controlled value (e.g. `.trim()`) had its commit retired by the value's prop transition."
- **Promised behaviour or unintended error:** unintended. The PR never mentions blur. Its stated goal is syncing programmatic changes, and it does not intend to revoke a blur verdict.
- **Required corrective outcome.**
  - In `onBlur` mode, when a controlled consumer rewrites the value as part of blur handling, the field must end up publishing the validator's result for the settled value. This applies to both sync and async validators.
  - A prop transition must not overwrite that result with "valid" without validating, and must not silently retire it.
  - A stale async result for the pre-normalization value must not overwrite the settled value's result.
  - A rewrite back to the initial value may stay quiet (upstream's choice).
  - Restoring merge-base behaviour, where the blur verdict for `"foo "` is kept but `"foo"` is never validated, is only **partial**. Probe case H shows why: when normalization makes the value valid, merge-base shows a stale error.
- **Evidence.**
  - My probe: cases A and B are red at head, green at merge-base, and green at head plus the upstream hunk. Applying only the `onBlur` hunk of the upstream patch also turns them green.
  - Upstream fix `1e208a97` (#5563) adds three regression tests to `FieldControl.test.tsx`:
    - "validates the final controlled value when it is normalized on blur"
    - "keeps the final async validation when a controlled value is normalized on blur"
    - "does not validate when a controlled value is reset to the initial value on blur"
- **Scoring guidance.** A finding recovers GT-r1 when it identifies the mechanism in `onBlur` mode: the `useValueChanged` → `validation.change` → revalidate path, or equivalently a controlled prop transition after blur, clears or retires the blur-time validation. The finding does not need to use the word "trim". Any blur-driven rewrite counts: normalization, formatting or masking.

### GT-r2: on mount, a controlled `Field.Control` no longer derives `filled` from its `value` prop

- **Where (head `14d39e5d`).** `FieldControl.tsx`, `FieldControl`, lines 99–103: `useIsoLayoutEffect(() => { if (validation.inputRef.current?.value) setFilled(true); }, [validation.inputRef, setFilled])`.
  - This replaced the merge-base effect: `hasExternalValue = valueProp != null; if (inputRef.current?.value || (hasExternalValue && valueProp !== '')) setFilled(true); else if (hasExternalValue && valueProp === '') setFilled(false);` with deps `[…, valueProp]`.
  - The new `useValueChanged` (105–115) does not run on mount. So the head effect is now the only mount-time source of `filled`: it reads only the DOM and can only set `true`.
- **Violated contract.** The documented Field state: "`data-filled` … Present when the field is filled" (`docs/src/app/(docs)/react/components/field/types.md:38`, repeated for each part).
- **Trigger** (two manifestations):
  1. **Remounting empty.** A controlled `Field.Control` that is remounted with an empty value inside the same `Field.Root`. Example: `<Field.Control key={String(empty)} value={empty ? '' : 'value'} onValueChange={() => {}} />`, then flip `empty`.
  2. **Non-input element.** A controlled `Field.Control` rendered as an element with no DOM `.value`: `<Field.Control value="value" onValueChange={() => {}} render={<div />} />`.
- **Consequence** (reproduced):
  1. **Remounting empty.** Field.Root keeps `data-filled` while the control is empty (a stale `true`).
  2. **Non-input element.** Field.Root lacks `data-filled` while the control holds `"value"`.
  - Both pass at merge-base and fail at head. Styling keyed on `data-filled`, such as floating labels, is wrong.
- **Introduced by this PR: yes, for these two manifestations.** This contradicts the vetting claim and the maintainer's summary in #5563, "the filled half predates it":
  - The **uncontrolled** remount case (probe F) does fail at merge-base too, so it predates #5460. It is excluded from GT-r2.
  - The **controlled** cases E and G pass at merge-base and fail at head. The removed `hasExternalValue` branches were what made them pass.
  - The #5563 regression tests "clears filled state when a controlled control remounts empty" and "sets filled state from a controlled value on a custom element" pin exactly these cases.
- **Promised behaviour or unintended error:** unintended. The PR's own test "does not set filled state on mount for an empty controlled value" only covers a fresh `Field.Root`. Its body calls the remaining mount effect "the mount-time DOM read that its uncontrolled mode requires". It gives no reason for dropping controlled-value derivation at mount.
- **Required corrective outcome.** At mount, `filled` must reflect a controlled `Field.Control`'s current `value` prop, whether `true` or `false`. This must hold regardless of the rendered element and of the state left by a previous control in the same `Field.Root`.
- **Evidence.**
  - My probe: cases E and G are red at head, green at merge-base, and green at head plus only the upstream `filled` hunks of `1e208a97`. Those hunks derive `filled` from `serializedValue ?? inputRef.value` in a layout effect keyed on `serializedValue`.
  - The upstream regression tests in #5563, named above.
- **Severity note.** GT-r2 is narrower and lower-impact than GT-r1: it affects a styling and state attribute, and only under a remount or a custom element. It is still a demonstrated regression of documented state.

## Reproduction

All runs happened in my own clone, at `work/base-ui`, cloned from `hunts/r/scratch/base-ui`.

**Install.** `COREPACK_ENABLE_DOWNLOAD_PROMPT=0 corepack pnpm install --frozen-lockfile --store-dir work/.pnpm-store`, with the XDG cache, data and state directories inside `work/`. pnpm 11.17.0: exit 0, 29 s. `pnpm-lock.yaml` is identical at merge-base and head (`git diff --quiet`).

**Probe.** `work/adj-probe.test.tsx`, run by `work/run-probe.sh`. The script copies the probe into `packages/react/src/field/control/`, runs it with the command below, and deletes it afterwards:

```
corepack pnpm exec cross-env TZ=UTC VITEST_ENV=jsdom vitest run --project @base-ui/react packages/react/src/field/control/adj-probe.test.tsx
```

| Case | Head `14d39e5d` | Merge-base `30b8ea20` | Head + full upstream `FieldControl.tsx` hunk (`1e208a97`) | Head + blur hunk only | Head + filled hunks only |
| --- | --- | --- | --- | --- | --- |
| A: sync, trim on blur keeps the error | **fail** (`aria-invalid` null) | pass | pass | pass | fail |
| B: async, trim on blur publishes the error | **fail** ("Unable to find … Invalid email") | pass | pass | pass | fail |
| C: blur without a value change (control) | pass | pass | pass | pass | pass |
| D: no consumer `onBlur` (control) | pass | pass | pass | pass | pass |
| E: controlled remount empty clears `data-filled` | **fail** | pass | pass | fail | pass |
| F: uncontrolled remount empty (pre-existing) | fail | **fail** | pass | fail | pass |
| G: controlled value on `render={<div/>}` sets `data-filled` | **fail** | pass | pass | fail | pass |
| H: normalization that makes the value valid ends valid | pass (by accident: cleared without validating) | **fail** (stale error) | pass | (not run) | (not run) |
| Exit and duration | exit 1, 1.8–2.0 s | exit 1 (F, H), 1.7 s | exit 0, 1.7–1.8 s | exit 1, 1.8 s | exit 1, 1.8 s |

Logs are `work/probe-{head,base,headfix,blurfix,filledfix,head2,base2,headfix2}.log`. The patches are `work/upstream-fix-fieldcontrol.patch`, `work/fix-blur-only.patch` and `work/fix-filled-only.patch`. Each patch was applied with `git apply` and reverted with `git checkout --`.

**Existing suites.** `vitest run --project @base-ui/react packages/react/src/field`:
- Head: exit 0, 3.4 s, 240 passed and 9 skipped.
- Merge-base: exit 0, 3.3 s, 233 passed and 9 skipped.
- Logs: `work/suite-field-*.log`.

The existing tests do not cover either defect.

**Tracked tree.** Clean afterwards: `git status --short --untracked-files=all` is empty, and the clone is detached at head.

**Checks on the vetting claim.**
- **Confirmed:** SHAs, merge-base, numstat, authorship and merge time, licence, empty review record, #5563 quotes, fix commit and branch commits, cited line numbers (±2 lines), and the sync and async mechanisms.
- **Minor inaccuracies:**
  - The scratch clone is not bare: `git rev-parse --is-bare-repository` prints `false`.
  - "4884 commits on master" is the count at current `origin/master`, not at merge-base (4672).
- **Material correction.** The claim's "Scope caution" treats all filled-state findings as pre-existing, following the maintainer. My reproduction shows the controlled `Field.Control` filled regressions (E, G) were introduced by #5460. They are registered as GT-r2. Only the uncontrolled case F predates it.

## Not ground truth

1. **`String(value)` serialization breaks arrays and objects.** Intended. The DOM value is always a string, and the PR says "The control now registers the serialized value, so the baseline and the comparison agree." The PR's test for a numeric value returning to its initial value covers it.
2. **The controlled `onChange` returns before `setDirty`, `setFilled` and validation, so controlled fields never validate on change.** False. `useValueChanged` performs that work when the consumer echoes the value. The PR states the design: "`useValueChanged` owns the controlled path, `onChange` owns the uncontrolled path". The PR test "validates once when a controlled value is changed by the user" covers it.
3. **An extra render per keystroke in `onChange` mode is a bug.** It is a documented and measured trade-off (the PR's performance table), and it matches Number Field. It is not a behavioural defect.
4. **`details.isCanceled` now suppressing `clearErrors` and `validation.change` is a breaking change.** It is the promised fix: "`details.cancel()` in `onValueChange` now stops the internal handling."
5. **`useValueChanged` ignores `serializedValue === undefined`, so clearing a controlled value to `undefined` is lost.** In this component `value === undefined` means uncontrolled (`isControlled = valueProp !== undefined`, line 83). `null` is serialized to `undefined` the same way. Switching between controlled and uncontrolled is outside the contract.
6. **A value the consumer rejects or rewrites (on change) never reaches field state.** Promised ("matching Combobox, Number Field and OTP Field").
7. **Programmatic value changes now call `clearErrors(name)`, clearing Form-level `errors` for that field.** Promised ("a resolved error stayed visible"). Before the PR, the same happened on every user keystroke.
8. **Programmatic changes in `onChange` mode now run validation (for example when a form library populates values).** Promised: the PR's goal is that programmatic changes update validity. No demonstrated harm.
9. **Submit-time validation now passes the serialized string (`"5"`) to `validate` instead of the raw controlled value (`5`).** This is real: `useFieldControlRegistration.validate` commits `registration.value`. But the blur, change and Enter paths already passed the DOM string at merge-base, `validate` is typed `(value: unknown, …)`, and Form values come from `getValue` (the DOM) either way. The change makes the paths consistent. No failure is demonstrated.
10. **The React #9023 `defaultPrevented` workaround no longer guards the controlled path.** The controlled path no longer depends on the DOM change event, so the workaround does not apply. No failure is demonstrated.
11. **In `onBlur` mode, a programmatic change at rest (not during blur) clears a prior error without re-validating until the next blur or submit.** On its own this is the existing revalidate design, which user typing already follows, and upstream kept it for non-blur transitions. A finding that ties this mechanism to the blur-time result being dropped counts as GT-r1. A demand to fully re-validate every programmatic change at rest is not ground truth.
12. **Stale `data-filled` after an uncontrolled `Field.Control` remounts empty.** Real, but it predates this PR (probe F fails at merge-base). Neither credit nor penalise it as a defect of #5460.
13. **Checkbox, Switch or CheckboxGroup filled-state issues fixed in #5563.** They are outside this diff and predate it.
14. **The "renders once per keystroke" test counts renders and is brittle.** Test hygiene, not material.
15. **`useValueChanged` running in a layout effect causes a flash or tearing.** Hypothetical. The existing sibling controls use the same pattern, and nothing is demonstrated.

## Preexisting hints

Before the merge instant, the review record has no reviews, no review threads (REST `pulls/5460/comments` count is 0), and three conversation comments, all from bots:
- `pkg-pr-new`, 2026-08-10T13:18:26Z: preview install links.
- `code-infra-dashboard`, 13:19:19Z: bundle size "+88B".
- `netlify`, 13:20:31Z: deploy preview.

None mentions blur, validation, filled or any tempting surface. The PR body itself names the "one extra render per keystroke" trade-off and the `details.cancel()` change. That makes non-defects 3 and 4 visible to every reviewer as intended behaviour.

## Leakage

A truncated mirror must exclude the following.

- **Merge and after.** Merge commit `5c12af1accbad774f05ea51894966fa006f0d4d8` and every later commit on `master` (current tip at adjudication is `e29ae4c3178716071eccc02688f65fab76836d6d`).
- **Fix.**
  - Squash `1e208a97f0339b617e70dadbc4abda32b48ea063` (#5563).
  - #5563 branch commits: `d40b71710cf66ced70bf5fe8bc2c8bc14d48a4e4`, `4bcacb41be4d3e257bdef5216bba41cc7e89768f`, `2999b2cf499d6fe0edb0a9c217039394988251c9`, `38a5239c01c53af10723a29174e2e04d4479474f`, `1ab0996877a0bbf3caa67ff3b25ed7c055d634c1`, `a37e2badbfaad524ef2b447174a58c7910d34e38`, `3422dd07772aee03b6e15c1194c71661153b2771`, `51bc501f10c21d7bfb5b6d069dc13b5e686f9c37` (head).
- **Later commits on the changed paths.** `3ab5747dd108ab9027f09689d7f46b2dfb6f9160` (#5486), `eabe0a9d9063e7d1b6e15c59cac497f33aa01b5b` (#5520), `18c8802667e88b81ada41ce6da2c3a6149ab457d` (#5512), `24a959817a78b931a97e7566b854e2478c9d8b91` (#5459), `5b495488d182c81a8a14a440d7a376517118f8ec` (#5605).
- **Later commits on the callee `useFieldValidation.ts`.** `feadc929d05d117ba45d7230a11734a8cd692701` (#5600, changes the async in-flight validity semantics) and `3cb844bb0a772fb6621b4279308ca39a324a5a9c` (#5248).
- **Pull requests.**
  - **#5563**: its title and body name the regression and both mechanisms.
  - #5600: same callee; does not name #5460, but changes async-validation semantics near GT-r1.
  - A search for "5460" in PRs finds only #5460 and #5563. The same search in issues finds nothing.
- **Local refs to hide.** The scratch clone carries refs `pr-5563` and `pr-5578`. `pr-5578` is an unrelated number-field branch but is post-merge. The scratch hunt artefacts (`hunt-blur-normalize.test.tsx`, `fix-fieldcontrol.patch`, `packet-5460.md` notes) and this `work/` directory must stay out of reviewer reach.

## Confidence and limits

- **GT-r1: high.**
  - Reproduced red at head and green at merge-base, sync and async.
  - Fixed by the upstream blur hunk alone.
  - Named explicitly by the maintainer as a regression from #5460.
  - Controls C and D show that the trigger requires a blur-driven rewrite.
- **GT-r2: high that it is a regression and real; moderate on how much it matters.**
  - Reproduced red at head and green at merge-base for both controlled manifestations, and fixed by the upstream filled hunks alone.
  - Its triggers are narrow (remount inside a persistent `Field.Root`; a non-input `render` element), and the consequence is a wrong `data-filled` attribute.
  - It contradicts the maintainer's own "the filled half predates it". I rely on the direct reproduction; the maintainer's phrase is accurate for the uncontrolled, Checkbox and Switch parts.
- **Environment.** jsdom only; no browser run. The mechanisms are pure React state and effect ordering plus `ValidityState` for `valueMissing`, and jsdom implements both. I don't expect the result to differ in a browser, but that is unverified.
- **Timing.** The probes use `act` plus microtask flushing. I did not test async normalization after blur (for example a `setTimeout` in the blur handler). Upstream says it is "still not covered" even after the fix, so it is not part of the required outcome.
- **No human review baseline.** The PR had no human reviewer, so there is no prior-review comparison.
