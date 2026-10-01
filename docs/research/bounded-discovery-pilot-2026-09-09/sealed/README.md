# Sealed pilot evidence

`pilot-evidence.tar.gz.enc` holds everything #150 produced that would disclose sealed truth: the full
per-cell artifacts, the rendered prompts, every transcript, each cell's review payload and research
report, arm C's freeze and discovery files, both invalidated attempts, and the reconciled ledger.

Two things force the seal. The per-cell records name their slot, and the ledger's **frozen attempt
IDs contain slot names** — and because the pilot's selection rule is public ("the adjudicated clean
slot and the lowest-numbered buggy slot, clean first"), naming the slots the six positions ran on
would disclose which slot holds the clean control. That is the same hidden truth #148 sealed and #153
reveals.

Encrypted with the key #148 generated, under the same parameters as #148's registers and #149's
schedule: `openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt`. [`SHA256SUMS`](SHA256SUMS) records
the SHA-256 of the compressed plaintext at the moment it was sealed; [`seal.json`](seal.json) records
the ciphertext digest, its size, which positions it covers and which invalidated attempts it retains.

## The reconciled ledger

The live ledger moved to `~/.config/bounded-discovery/issue-150/ledger.json` on the preparation
machine, so that #151 can keep appending to one chain while the committed copy of
`bounded-discovery-prototype/ledger.json` stays byte-unchanged through the pilot. Its SHA-256 at
delivery is

```
8470b46872339b3f7e44752b51f3c0993825a64ab1924bbb01ed1d48e025cabd
```

and a copy of it is inside this archive. `verify_freeze.py` passes against the committed ledger, whose
event prefix through `cap-freeze` is what the freeze rests on.

## What is deliberately not sealed

The public per-cell summaries in [`../cells/`](../cells/) carry the process and fidelity evidence:
dispositions, isolation verdicts, model-and-effort reports, mount counts, egress counts, costs and
residuals. They are built from a whitelist and then mechanically scanned, so a slot name, repository,
pull-request number or leak-set digest cannot reach them.

## Reveal

```sh
K=~/.config/bounded-discovery/issue-148/truth.key
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass file:"$K" \
  -in pilot-evidence.tar.gz.enc -out pilot-evidence.tar.gz
shasum -a 256 -c SHA256SUMS
tar -xzf pilot-evidence.tar.gz
```

A hash mismatch means the plaintext is not the sealed one; do not score against it. #152 opens this
once every reviewer run has stopped, and not before.
