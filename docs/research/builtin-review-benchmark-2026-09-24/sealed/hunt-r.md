# Hunt (r): frontend component logic — buggy

Started 2026-09-24. Single-threaded. Clones under `scratch/`.

## Inventory (in order examined)

| # | Repo | PR | Merged | Lines / files | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 | Result |
|---|------|----|--------|---------------|----|----|----|----|----|----|----|----|----|-----|--------|
| 1 | mui/base-ui | #5460 | 2026-08-13T11:23:20Z | 223 (+197/−26) / 2 | pass (repo not listed) | pass (preferred window) | pass (numstat on full clone) | pass (exit 0, default cutoff = merge instant, 0 omissions) | pass (GitHub-native; no human reviews, 3 bot comments) | pass (pnpm install 35 s; focused vitest jsdom 1–2 s; fails at head, passes at merge-base and with fix) | pass (diff + `useFieldValidation.change/commit` + `useValueChanged`) | pass (PR promised syncing programmatic changes, not discarding blur validation) | pass (maintainer fix #5563, 1e208a97, 2026-08-25: "The blur half is a regression from #5460") | pass (MIT, public, MUI maintainers) | **PASS — recommended** |
| 2 | TanStack/form | #1893 (via fix #2240) | 2025-12-01T18:38:16Z | 195 (+149/−46) / 5 (gh counts) | pass | fallback window only (2025-12); preferred candidates exist | pass (gh counts) | not checked | — | — | — | — | fix #2240 says "Regression from #1893 (v1.27.0)" | — | not pursued (E2: preferred-window candidates found) |
| 3 | mui/base-ui | #5578 | 2026-08-27T05:43:35Z | 75 (+59/−16) / 7 | pass | pass | pass (numstat on full clone, merge-base 2b8af88e = PR base) | not checked | pass | not checked | pass | **doubtful**: the post-`focus()` caret write that clobbers a consumer `onFocus` selection is the mechanism the PR openly describes ("The helper sets the selection after `focus()` returns") | partial: follow-up fix #5619 (b7f6683c, 2026-09-02) says "Follow-up to #5578", not "regression"; first-focus clobbering also existed before | pass (MIT) | dropped (E8 weak, E9 attribution weak) |
| 4 | 47ng/nuqs | #1558 | 2026-08-20T08:18:55Z | 114 (+96/−18) / 2 (gh counts) | pass | pass | pass (gh counts) | not checked | pass | fail-risk: tests are `*.browser.test.tsx` (vitest browser mode) | — | — | **fail**: fix #1568 narrows #1558's recovery, but issue #1567 says the leak "was already there before #1558 and is untouched by it" | pass (MIT) | dropped (E9: defect predates the PR) |
| 5 | vuetifyjs/vuetify | #23023 | 2026-08-13T00:19:47Z | 24 (+21/−3) / 7 | pass (repo not listed) | pass (preferred window) | pass (numstat on full clone) | pass (exit 0, default cutoff = merge instant, 0 omissions) | pass (GitHub-native; 0 reviews, 0 comments) | pass (pnpm install with `CI=true HUSKY=0` 23 s; focused vitest jsdom 2–3 s; fails at head, passes at merge-base and with fix) | pass (diff + sibling `onMousedownMenuIcon` in same hunk + `VTextField` `mousedown:control` bubbling) | pass (PR promised input-click toggling, not a dead menu icon) | pass (fix #23200, c8b9d6a1, 2026-09-23, merged by the #23023 author J-Sek; issue #23197) | pass (MIT, public) | **PASS — alternate** |

Notes on the inventory:

- Search trail: `gh search prs` full-text "regression introduced in #" / "fixes regression from #" (TypeScript, merged ≥ 2026-07-01), then per-repo `"regression in:body"` searches over 44 UI repositories (TanStack query/router/form/table/virtual, react-hook-form, radix, mantine, headlessui, react-spectrum, MUI material/base-ui, chakra, zag, ariakit, floating-ui, vueuse, reka-ui, bits-ui, react-router, swr, react-day-picker, heroui, element-plus, vuetify, quasar, nuqs, alibaba/hooks, conform, kobalte, and others). About 80 fix-PR bodies were scanned for an introducing-PR reference (`scratch/scan.sh`, `scratch/scan2.sh`). Only rows 1–5 named an introducing PR plausibly in scope, so only those are in the table.
- Row 2 (TanStack/form#1893) merged in the fallback window. Preferred-window candidates exist, so it was not pursued.
- Row 3: base-ui#5578's own description says "The helper sets the selection after `focus()` returns", and fix #5619 calls itself a "Follow-up to #5578", not a regression fix. Before #5578 the first focus already overwrote the selection. Dropped as an E8/E9 risk, not measured further.
- Row 4: nuqs issue #1567, whose reporter the maintainer credited, says "That path was already there before #1558 and is untouched by it".

## Recommendation

- **Primary: mui/base-ui#5460** (row 1, the first candidate in inventory order that passes E1–E10).
- **Alternate: vuetifyjs/vuetify#23023** (row 5).

---

### Primary: mui/base-ui#5460 — "[field] Sync controlled value changes with field state"

- **Author** `atomiks`, who also merged it (a maintainer: they merge base-ui PRs, including this one and #5563). **Merged** 2026-08-13T11:23:20Z into `master`. **Licence** MIT (`LICENSE`: "MIT License / Copyright (c) 2019 Material-UI SAS"; API `spdx_id: MIT`). Public.
- **Head** `14d39e5d1ad6b7aca2fb067415dba09c6bea219b` (the only commit; `pull/5460/head` resolves to it). **PR base SHA** `30b8ea2004fa999bed151204208676c6c0a9d261`. **Merge-base I computed** on a full clone (`git merge-base 30b8ea20 14d39e5d`, repository not shallow, 4884 commits on master) = `30b8ea2004fa999bed151204208676c6c0a9d261`. **They agree.** Merge commit `5c12af1accbad774f05ea51894966fa006f0d4d8`.
- **Manifest** (`git diff --numstat 30b8ea20 14d39e5d`): 223 changed lines in 2 files.
  - `packages/react/src/field/control/FieldControl.test.tsx`: +149 −6
  - `packages/react/src/field/control/FieldControl.tsx`: +48 −20
- **Originating issue:** none linked (`closingIssuesReferences` is empty). Labels are `type: bug` and `component: field`.
- **Review record up to the merge:** no reviews and no review threads (`reviews: []`; the REST `pulls/5460/comments` count is 0). There are 3 conversation comments, all from bots: `pkg-pr-new` (2026-08-10T13:18:26Z, preview install links), `code-infra-dashboard` (13:19:19Z, bundle size "+88B"), and `netlify` (13:20:31Z, deploy preview). **Nobody raised the defect.**
- **The defect:** `packages/react/src/field/control/FieldControl.tsx` at head, component `Field.Control`:
  - **Where.** Lines 105–115 add `useValueChanged(serializedValue, () => { clearErrors(name); setDirty(...); setFilled(...); validation.change(serializedValue); })` for the controlled path. The `onBlur` handler at 161–166 calls `validation.commit(event.currentTarget.value)` when `validationMode === 'onBlur'`.
  - **Callee** (`packages/react/src/field/root/useFieldValidation.ts` at head). `change` (316–326) calls `commit(value, !validateOnChange)`. In `onBlur` mode that is `commit(value, /*revalidate*/ true)`. `commit` bumps `validationCommitIdRef` (118). The revalidate branch (169–181) returns early when `state.valid !== false`. Otherwise, when `valueMissing` is false, it calls `publishAllValid(element, false)`.
  - **Contract.** `FieldRoot.tsx` JSDoc: "`onBlur`: triggers validation when the control loses focus." The PR scoped its own change to programmatic changes: "Setting the value from code, such as a clear button or a form library reset, updated the input text but not filled, dirty, or validity".
  - **Trigger.** `<Field.Root validationMode="onBlur" validate={v => String(v).includes('@') ? null : 'Invalid email'}>` wraps a controlled `<Field.Control value={value} onValueChange={setValue} onBlur={() => setValue(v => v.trim())} />` and `<Field.Error />`. Type `"foo "`, then blur.
  - **Consequence at head, sync validator.** The blur commit publishes "Invalid email". The trim then changes the `value` prop. The layout effect calls `change('foo')`, which takes the revalidate path; the field is invalid and not `valueMissing`, so `publishAllValid` clears the error. The field reports valid, has no `aria-invalid` and shows no error, and `validate('foo')` never runs.
  - **Consequence at head, async validator.** The blur commit's pending promise is retired by the id bump. The revalidate path returns at line 170 because `state.valid` is still `null`. Nothing is ever published.
  - **Before the PR** (merge-base) the blur error stayed visible, because nothing reacted to the prop change.
  - **Upstream confirmation.** mui/base-ui#5563, "[field][checkbox][switch] Fix controlled blur validation and stale filled state", author and merger `atomiks`, merged 2026-08-25T08:47:41Z, squash commit `1e208a97f0339b617e70dadbc4abda32b48ea063`. Verbatim: "Two field lifecycle fixes. The blur half is a regression from #5460; the filled half predates it." and "**Controlled blur normalization no longer discards validation.** With `validationMode="onBlur"`, a blur handler that normalizes the controlled value (e.g. `.trim()`) had its commit retired by the value's prop transition." The fix adds the regression tests "validates the final controlled value when it is normalized on blur" and "keeps the final async validation when a controlled value is normalized on blur" to `FieldControl.test.tsx`.
  - **Corrective outcome** any fix must restore: in `onBlur` mode, when a controlled consumer rewrites the value during blur, the field must end up showing the validation result for the settled value, sync or async. A prop transition must not silently drop or overwrite a blur-time validation with "valid". A reset back to the initial value may stay quiet, as upstream chose.
  - **Scope caution for the answer key.** #5563 also changes `filled` derivation, and #5460 removed the mount-effect branch `hasExternalValue && valueProp === '' → setFilled(false)`. The maintainer says "the filled half predates it", so filled-state findings should be neither credited nor penalised as this defect.
- **Tempting false positives:**
  1. *`String(value)` serialization mangles arrays and objects.* Intended. The PR explains that the DOM value is always a string, so the dirty baseline must be serialized: "The control now registers the serialized value, so the baseline and the comparison agree."
  2. *A controlled `onChange` returns before `setDirty`, `setFilled` and validation, so a controlled field never validates on change.* Wrong. The `useValueChanged` layout effect performs that work when the consumer echoes the value. The early return is the PR's stated design ("`useValueChanged` owns the controlled path, `onChange` owns the uncontrolled path").
  3. *An extra render per keystroke in `onChange` mode is a bug.* A documented trade-off, measured in the PR's performance table ("Moving the work into a layout effect costs one extra render per keystroke in `onChange` mode"). It is not a behavioural defect.
  4. *`details.isCanceled` now suppressing `clearErrors` and `validation.change` is a breaking change.* It is the promised fix: "`details.cancel()` in `onValueChange` now stops the internal handling."
  5. *`useValueChanged` skips `serializedValue === undefined`, so clearing a controlled value to `undefined` is ignored.* `value === undefined` means uncontrolled in this component (`isControlled = valueProp !== undefined`), so the uncontrolled path owns it.
- **Leak set** (a truncated mirror must exclude all of these):
  - Merge commit `5c12af1accbad774f05ea51894966fa006f0d4d8` and everything after it on `master`.
  - Fix squash `1e208a97f0339b617e70dadbc4abda32b48ea063`.
  - #5563 branch commits `d40b71710cf66ced70bf5fe8bc2c8bc14d48a4e4 4bcacb41be4d3e257bdef5216bba41cc7e89768f 2999b2cf499d6fe0edb0a9c217039394988251c9 38a5239c01c53af10723a29174e2e04d4479474f 1ab0996877a0bbf3caa67ff3b25ed7c055d634c1 a37e2badbfaad524ef2b447174a58c7910d34e38 3422dd07772aee03b6e15c1194c71661153b2771 51bc501f10c21d7bfb5b6d069dc13b5e686f9c37` (head).
  - Later commits on the changed paths: `3ab5747dd108ab9027f09689d7f46b2dfb6f9160` (#5486), `eabe0a9d9063e7d1b6e15c59cac497f33aa01b5b` (#5520), `18c8802667e88b81ada41ce6da2c3a6149ab457d` (#5512), `24a959817a78b931a97e7566b854e2478c9d8b91` (#5459), `5b495488d182c81a8a14a440d7a376517118f8ec` (#5605).
  - PR numbers whose content gives the answer away: **#5563**. The PR search for "5460" returned only #5460 and #5563.
- **Provisioning and test evidence** (clone `scratch/base-ui`; logs are in `scratch/`):
  - Provisioning:
    - `git clone https://github.com/mui/base-ui.git`: 4.9 s.
    - `git fetch origin pull/5460/head pull/5563/head`.
    - At head: `COREPACK_ENABLE_DOWNLOAD_PROMPT=0 corepack pnpm install --frozen-lockfile` (pnpm 11.17.0): exit 0, **35 s**. No browser download. The lockfile is unchanged between merge-base and head.
  - Focused test: `scratch/hunt-blur-normalize.test.tsx`. It has two cases, sync and async validators, each asserting that "Invalid email" is shown after trim-on-blur; the sync case also asserts `aria-invalid="true"`. It was copied into `packages/react/src/field/control/` only while running.
  - Command: `corepack pnpm exec cross-env TZ=UTC VITEST_ENV=jsdom vitest run --project @base-ui/react packages/react/src/field/control/hunt-blur-normalize.test.tsx`. Results:
    - **Head `14d39e5d`: exit 1, 2 s, 2 of 2 failed.** Sync: `expect(element).toHaveAttribute("aria-invalid", "true")` failed; the rendered input has `value="foo"` and no error. Async: `Unable to find an element with the text: Invalid email`.
    - **Merge-base `30b8ea20`: exit 0, 2 s, 2 of 2 passed.**
    - **Head plus the upstream `FieldControl.tsx` hunk from `1e208a97`** (`git apply`, clean): **exit 0, 1 s, 2 of 2 passed.**
    - Existing `FieldControl.test.tsx` at head: exit 0, 2 s, 26 passed and 1 skipped.
  - **Tracked tree stayed clean:** the fix hunk was reverted with `git checkout --`, the probe file was removed, and `git status --short --untracked-files=all` is empty. The clone is left detached at head.
- **E4:** `build_packet.py --repo mui/base-ui --pr 5460 --head 14d39e5d… --merge-base 30b8ea20… --base-sha 30b8ea20… --staging scratch/base-ui --target r --out scratch/packet-5460.md` → **exit 0**, 1 s. Cutoff is the default merge instant, 2026-08-13T11:23:20Z. Omitted after cutoff: reviews 0, thread comments 0, conversation 0, issue comments 0.
- **Confidence: high.**
  - The defect was reproduced by a focused jsdom test: red at head, green at merge-base and green with the upstream fix.
  - The maintainer's fix names #5460 and the mechanism verbatim.
  - The PR is small (2 files), and the mechanism is reachable in 1–2 hops (`useFieldValidation.change/commit`, `useValueChanged`).
  - Residual risks. (a) The PR has no human review, so there is no prior-review baseline. (b) The same fix also covers a pre-existing `filled` issue, so the answer key must scope to the blur half. (c) A reviewer needs to know that `onBlur` mode makes `change()` take the revalidate path, which is one hop into `useFieldValidation.ts`.

---

### Alternate: vuetifyjs/vuetify#23023 — "feat(VAutocomplete,VCombobox): add `close-on-input-click` prop"

- **Author and merger** `J-Sek`, a Vuetify maintainer: they merged both this PR and fix #23200. Org membership is not public, so the API returns `CONTRIBUTOR`. **Merged** 2026-08-13T00:19:47Z into `dev`. **Licence** MIT (`LICENSE.md`: "The MIT License (MIT) / Copyright (c) 2016-now Vuetify, LLC"; `package.json` `"license": "MIT"`; the GitHub API reports `NOASSERTION` only because of the `.md` filename). Public.
- **Head** `a47ab77f8e0cd2f51b1f4d94b165e0f9fcddf9e3` (one commit). **PR base SHA** `5eac66780411a9b3fe1bcff8b83b14bed6e18bb9`. **Merge-base I computed** on a full, non-blobless clone = `5eac66780411a9b3fe1bcff8b83b14bed6e18bb9`. **They agree.** Merge (squash) commit `5dfeb32d791371d138b89e07c627fc373d7704c8`.
- **Manifest:** 24 changed lines in 7 files.
  - `packages/api-generator/src/locale/en/VAutocomplete.json`: +1 −0
  - `packages/api-generator/src/locale/en/VCombobox.json`: +1 −0
  - `packages/docs/src/data/new-in.json`: +2 −0
  - `packages/docs/src/pages/en/blog/july-2026-update.md`: +1 −1
  - `packages/vuetify/src/components/VAutocomplete/VAutocomplete.tsx`: +2 −1
  - `packages/vuetify/src/components/VAutocomplete/__tests__/VAutocomplete.spec.browser.tsx`: +12 −0
  - `packages/vuetify/src/components/VCombobox/VCombobox.tsx`: +2 −1
- **Originating issue:** #23021, "[Feature Request] Please bring back v-menu closeOnClick", by `nxmndr`, 2026-07-21. The packet includes it. It asks for the feature and does not mention the defect.
- **Review record up to the merge:** 0 reviews, 0 threads and 0 conversation comments; the PR was self-merged. **Nobody raised the defect.**
- **The defect:**
  - **Where.** `VAutocomplete.tsx` 240–243 at head: `onMousedownControl` now runs `menu.value = props.closeOnInputClick ? !menu.value : true`. The same change is in `VCombobox.tsx` 294–297.
  - **Sibling.** `onMousedownMenuIcon` (VAutocomplete 245–252, VCombobox 299+) only calls `e.stopPropagation()` when `isFocused.value`, then unconditionally runs `menu.value = !menu.value`.
  - **Bubbling path.** The menu icon is rendered in VField's `append-inner` slot (`onMousedown={ onMousedownMenuIcon }`, VAutocomplete line 809). VTextField's `onControlMousedown` (VTextField 132–133 and 226) emits `mousedown:control`, which is wired to `onMousedownControl` (VAutocomplete 557). So an icon mousedown on an unfocused field bubbles to the control handler.
  - **Contract.** The prop description added by this PR: "Clicking the field while the menu is open closes it." The PR does not promise anything about the menu icon, and without the prop the icon opens a closed menu.
  - **Trigger.** Mount `<VAutocomplete items={['foo','bar']} closeOnInputClick />` (or `VCombobox`), unfocused and with the menu closed. Fire `mousedown` on `.v-autocomplete__menu-icon`.
  - **Consequence.** The icon handler toggles `false → true`. The event is not stopped because the field is unfocused, so it bubbles and the control handler toggles `true → false`. The last `update:menu` emission is `false`, so the menu never opens (a flash, in a browser with `open-on-focus`). Before the PR, the control handler set `true`.
  - **Upstream confirmation:**
    - Issue #23197, "[Bug Report][4.2.1] Menu flashing with openOnFocus and closeOnInputClick when using menu open button" (by `devtobi`, 2026-09-17; closed 2026-09-23).
    - Diagnosis comment by `modos`: "`onMousedownMenuIcon` toggles the menu, then the event bubbles to the parent, where `onMousedownControl` toggles it again because of `close-on-input-click`, causing the menu to flash."
    - Fix PR #23200, "fix(VAutocomplete/VCombobox): prevent menu icon from toggling twice", by `modos`, **merged by J-Sek** 2026-09-23T18:20:52Z, squash `c8b9d6a1819ff6f69ef1837445daba51fc78c243`. Verbatim: "When `open-on-focus` and `close-on-input-click` were used together, clicking the menu icon while the field was unfocused caused the menu to toggle twice." The fix moves `menu.value = !menu.value` inside the `if (isFocused.value)` branch of both components.
    - `git blame` at `5dfeb32d` attributes the control-side toggle line to J-Sek's #23023. The icon-side lines date from 2023 (Kael/Yuchao).
  - **Corrective outcome.** A single mousedown on the menu icon of an unfocused field with `close-on-input-click` must leave the menu open; it must not toggle twice. Input clicks while open must still close the menu.
  - **Caveat.** Upstream frames the bug as needing `open-on-focus`, a prop added two days later by #23126. My test shows the double toggle at #23023's head without `open-on-focus`: the menu simply never opens. The answer key should accept either framing.
- **Tempting false positives:**
  1. *The `closeOnInputClick` toggle makes an input click close a menu opened by `openOnFocus` on the same interaction.* `openOnFocus` does not exist at this head; it arrived in #23126 on 2026-08-15.
  2. *VSelect was not updated, so the feature is incomplete.* The PR markup exercises `v-select` with the prop, but VSelect is outside the diff. At most this is an unrequested-scope observation, not a defect in the changed logic.
  3. *The prop defaults to `false` via `Boolean`, which might break existing behaviour.* When the prop is `false` the expression reduces to `true`, which is the previous behaviour.
  4. *The browser spec only covers VAutocomplete, not VCombobox.* That is a test-coverage gap, not a behaviour defect.
- **Leak set:**
  - Merge commit `5dfeb32d791371d138b89e07c627fc373d7704c8` and later.
  - Fix `c8b9d6a1819ff6f69ef1837445daba51fc78c243`.
  - #23200 branch commits `7eec26362f13db0a349607b5d6bbb91391907c4f` and `25f117d57b318df2a0325c08d439a6ccea85ca99`.
  - Later commits on the changed paths (all after the merge; exclude them in any case): `44e789f18` (#23126, open-on-focus), `71d38a619` (#23008), `2614f431e` (#22895), `7a33ea9c2` (#23031), `aae8fc4cf`, `c87979562`, `d65e89e31`, `bb09f8b72` (#23108), `8d1d985e9` (#23193), `b6c9f5c9e` (#23063).
  - Issue and PR numbers that give the answer away: **#23197 and #23200**.
- **Provisioning and test evidence** (clone `scratch/vuetify`):
  - Clone: full `git clone`, 15 s.
  - First `corepack pnpm install --frozen-lockfile` at head: exit 128 after 9 s. The root `prepare` script runs `$CI || pnpm exec playwright install chromium` and failed with "Unbound variable CI".
  - Rerun with `CI=true HUSKY=0`, which skips the browser download and git hooks: **exit 0, 23 s** (pnpm 10.26.1).
  - Focused jsdom test: `scratch/hunt-menu-icon.spec.tsx`. It is parameterized over VAutocomplete and VCombobox with `closeOnInputClick` = false and true, stubs `ResizeObserver`, mounts with `@vue/test-utils`, fires `mousedown` on the menu icon, and expects the last `update:menu` to be `true`. It was copied into `packages/vuetify/src/components/VAutocomplete/__tests__/` only while running.
  - Command (in `packages/vuetify`): `CI=true corepack pnpm exec vitest run --project unit <spec>`. Results:
    - **Head `a47ab77f`: exit 1, 3 s.** The 2 `closeOnInputClick=true` cases failed with "expected false to be true"; the 2 `false` controls passed.
    - **Merge-base `5eac6678`: exit 0, 2 s, 4 of 4 passed.** The prop does not exist yet, so the old behaviour applies. The lockfile is identical.
    - **Head plus the `c8b9d6a1` component hunks** (`git apply`): **exit 0, 2 s, 4 of 4 passed.**
  - An earlier run without the `ResizeObserver` stub errored with `ResizeObserver is not defined`; that is a harness gap, not the defect.
  - **Tracked tree stayed clean:** the component files were restored with `git checkout --`, the probe was removed, and `git status` is empty.
- **E4:** `build_packet.py --repo vuetifyjs/vuetify --pr 23023 --head a47ab77f… --merge-base 5eac6678… --base-sha 5eac6678… --staging scratch/vuetify --target r --out scratch/packet-23023.md` → **exit 0**, 1 s. Cutoff is the default merge instant, 2026-08-13T00:19:47Z. Omitted after cutoff: all 0. It reported 1 linked issue.
- **Confidence: medium-high.**
  - The defect is crisp and was reproduced red, green and green, and the fix was accepted by a maintainer.
  - Weaker points:
    - The fix and the diagnosis were written by a contributor (`modos`) and accepted by the maintainer through the merge. Neither cites #23023 explicitly; attribution rests on `git blame` and on my test at head versus merge-base.
    - Upstream frames the trigger with `open-on-focus`, a later prop.
    - The logic change is only 2 lines per component, which makes it an easy target.

## Closest misses

- **47ng/nuqs#1558:** fails E9, because the reporter's issue #1567 says the leak predates #1558. It is also an E6 risk, because the reproductions are vitest browser-mode tests.
- **mui/base-ui#5578:** E8 and E9 are weak. The clobbering post-`focus()` write is the openly described mechanism, and follow-up #5619 does not call it a regression.
- **TanStack/form#1893:** credible regression (fix #2240: "Regression from #1893 (v1.27.0)"), but merged 2025-12-01, in the fallback window only.

## Session notes

- Commands and logs are in `scratch/`: `install-*.log`, `test-*.log`, `fix-*.patch`, `packet-*.md`.
- Search pacing: about 50 search API calls, each with a sleep of at least 2.2 s between them. No rate-limit responses were received.
