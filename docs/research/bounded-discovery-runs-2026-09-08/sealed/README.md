# Sealed schedule

The resolved 24-cell order, including which two slots the six-cell pilot runs on, is committed here
only as ciphertext. Naming the pilot pair in the clear would tell any reader which two slots hold the
adjudicated clean target, and therefore which two do not — the same hidden truth #148 sealed.

`schedule.json.enc` is encrypted with the key #148 generated for its registers, under the same
parameters: `openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt`. `SHA256SUMS` records the SHA-256
of the plaintext at the moment it was sealed. The plaintext lives in
`~/.config/bounded-discovery/issue-149/` on the preparation machine (mode 0600) and moves off the
machine with the key for every dispatch window, as the preregistration's isolation section requires.

It was produced by [`../scripts/seal_schedule.py`](../scripts/seal_schedule.py), which verified each
register against #148's `SHA256SUMS`, read only its one-line `Verdict` section, and printed nothing
but hashes and counts.

## Contents of the plaintext

`rule` (the frozen selection rule, also stated in the clear in the preregistration), `pilot_slots`,
`ordered_cells` (24 entries with `position`, `cell_id`, `target_slot`, `arm`, `replicate`, `block`
and the owning ticket), and `register_sums`. No category, defect, leak SHA or verdict.

## Reveal

```sh
K=~/.config/bounded-discovery/issue-148/truth.key
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass file:"$K" \
  -in schedule.json.enc -out schedule.json
shasum -a 256 -c SHA256SUMS
```

#150 and #151 decrypt it to dispatch. A hash mismatch means the plaintext is not the sealed one; do
not dispatch against it.
