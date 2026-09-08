# Sealed evaluator-only artifacts

Hidden truth for the four #148 targets is committed here only as ciphertext, so that a reviewer with
filesystem access to this repository cannot read it (criteria §6). Every file is encrypted with
`openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt` under one random 256-bit key generated for
this ticket. `SHA256SUMS` records the SHA-256 of each plaintext at the moment it was sealed, so the
freeze is provable at reveal time without trusting the ciphertext's mtime.

Plaintexts and the key live in `~/.config/bounded-discovery/issue-148/` on the preparation machine
(mode 0700). That directory, the key file and any decrypted copy must be outside every reviewer read
surface; #149's isolation probes must show reviewer tools cannot read `~/.config`, or the key must be
moved off the machine before dispatch.

## Contents

| File | What it is | Sealed at |
| --- | --- | --- |
| `inventory.md.enc` | the frozen candidate inventory: every candidate examined per category, in examination order, with E1–E10 results, hypotheses, confirmations and the first-eligible choice | inventory freeze commit |
| `<slot>-register.md.enc` | that slot's adjudicated register (defect IDs, trigger, consequence, corrective outcome, plausible non-defects, preexisting hints, leak set, category) | that slot's adjudication commit |
| `slots.json.enc` | the slot-to-category mapping and truth version | after the four targets are fixed |

## Reveal (after every reviewer run has stopped)

```sh
K=~/.config/bounded-discovery/issue-148/truth.key
for f in *.enc; do openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass file:"$K" -in "$f" -out "${f%.enc}"; done
shasum -a 256 -c SHA256SUMS
```

A hash mismatch means the plaintext is not the sealed one; do not score against it.
