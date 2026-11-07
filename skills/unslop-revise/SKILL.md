---
name: unslop-revise
description: Run unslop on text, then fix any statement in the result that is wrong, ambiguous, or unsupported. Use for /unslop-revise.
---

# Unslop revise

If the `unslop` skill is not installed, stop and report `missing-dependency: unslop`.

1. Run `unslop` on the user's text.
2. Revise that result. Check each claim against the original text and anything you can verify, such as code, files, or sources. Fix any statement that is wrong, rewrite any a reader could take two ways, and cut any the original doesn't support. Keep unslop's rules while you revise.
3. Return only the revised text.
