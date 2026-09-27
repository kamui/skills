# Review blind-0a74e9

### Item 1
Location: packages/react/src/field/control/FieldControl.tsx:99-103
Claim: Mount effect never clears data-filled when a Field.Control remounts empty. A Field.Root stays mounted while its Field.Control child is swapped for a different control instance (a different `key`, or a conditionally rendered different control) whose initial value is empty, after the previous control instance had left the field filled.
Consequence: `data-filled` (and the `filled` field of Field.Root's public state) stays stuck `true` on the new, empty control. Reproduced directly: mounting `Field.Root` > `Field.Control key="a" value="foo"` then swapping to `Field.Control key="b" value=""` leaves `data-filled` present at head, where the merge-base's version of the same file clears it. `filled` is documented public field state (`FieldRootState.filled`, "Whether the field has a value"), so this is user-visible, e.g. through floating-label or empty-state styling driven by `data-filled`.
Fix: Make the mount-time effect symmetric so it also clears `filled` to `false` when the current DOM value is empty, matching the effect it replaced (`else if (hasExternalValue && valueProp === '') setFilled(false)`), e.g. `setFilled(!!validation.inputRef.current?.value)` unconditionally instead of only inside the truthy branch.
