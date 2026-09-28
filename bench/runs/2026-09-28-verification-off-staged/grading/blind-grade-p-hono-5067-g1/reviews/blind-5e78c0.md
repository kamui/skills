# Review blind-5e78c0

### Item 1
Location: (no file)
Claim: `parseFormData` in src/utils/body.ts now reads the whole body via `arrayBuffer()` and re-parses it through `bufferToFormData()` instead of calling the platform `Request.formData()` directly, matching the pattern `src/validator/validator.ts`'s `form` branch already used before this change.
Consequence: src/utils/body.ts:126-132; src/validator/validator.ts:119-121.
Fix: —
