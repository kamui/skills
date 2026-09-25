# Sealed evaluator-only material for the fresh targets

The hunt reports and adjudication rulings for targets (o)–(r) name each defect, its trigger and the
later fix, so they are committed only as ciphertext until the first run is scored (design §5). Each
target's register is sealed beside its `target.json` in the same way, as
`bench/targets/<id>/register.v1.json.enc`, with its plaintext hash in that `target.json`'s `sealed`
block.

Every file here was written by [`bench/tools/seal.py`](../../../../bench/tools/seal.py):
`openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt` under one random 256-bit key at
`~/.config/bench/seal.key` on the preparation machine (mode 0600, directory 0700), outside the
repository and every attempt directory. `SHA256SUMS` records the SHA-256 of each plaintext at the
moment it was sealed. The plaintexts also stay in `~/.t3/bench-cache/sealed/` on that machine.

| File | What it is |
| --- | --- |
| `hunt-<slot>.md.enc` | the vetting hunt's report: every candidate examined in order with its E1–E10 results, the recommendation, the proposed defect or clean case, the leak set and the hunt's own test runs |
| `ruling-<target>.md.enc` | the independent adjudicator's ruling, the prose form of the sealed register |

A reviewer that reads anything outside its attempt directory is harness-invalid under the read
audit, and the key is outside every attempt directory. A separate Unix user would make the key
unreachable rather than detectable; that control is not in place (README §3).

## Reveal (after every reviewer attempt has been filed)

Done 2026-09-25 after the run was scored: the plaintexts now sit beside their ciphertexts, each
matching `SHA256SUMS`, and each fresh target's `register.v1.json` beside its `.enc`.

```sh
cd docs/research/builtin-review-benchmark-2026-09-24/sealed
for f in *.enc; do
  python3 ../../../../bench/tools/seal.py open "$f" "${f%.enc}" \
    --sha256 "$(awk -v n="${f%.enc}" '$2 == n {print $1}' SHA256SUMS)"
done
```

`seal.py open` writes a plaintext only when its hash matches, and a failed `open` leaves any file
already at that path untouched. A mismatch means decryption did not produce the sealed plaintext, so
nothing is written: check the key and `SHA256SUMS` before scoring.
