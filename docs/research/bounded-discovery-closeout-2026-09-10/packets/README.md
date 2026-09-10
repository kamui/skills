# Anonymous grading packets

Six packets, one for each pilot attempt that published a review, plus a
[no-packet manifest](no-packet-manifest.json) for the two attempts that published nothing. They are
[#152](https://github.com/kamui/skills/issues/152)'s inputs. Built by
[`../scripts/build_packets.py`](../scripts/build_packets.py) from the sealed pilot evidence, after
the [stop gate](../gate.json) established that every reviewer run had terminated.

## What a packet carries

Verbatim, because the grading is about the prose and nothing else: the published **status**, the
**whole review body**, and every **finding and observation** the attempt published structurally,
each with its trigger, claimed consequence, remedy and decisive evidence. `body_markdown` holds
every visible claim; `items` indexes the ones the attempt also emitted as structured records, and
is empty where it did not.

## What a packet does not carry

The position, the arm, the worker model, the replicate, the operational validity, the completion
and the cost. Those are the mapping #152 must not see while it forms rulings, and they live in
`redaction-map.json` inside the seal. Packet and item ids are random and are shuffled before
emission, so their order says nothing about schedule position.

## Masking, and what it does not achieve

Every value that names a target is replaced with a sequential token — the repository, its url, its
pull request, and each object id **at every length the prose abbreviates it to**, longest first, so
that masking a full id cannot leave a seven-character prefix of it behind. The tokens are
sequential, never digests: a hash over an enumerable secret is a lookup table for that secret, and
this experiment's own review proved it by inverting four such commitments. The slots are visited in
randomised order, so `<repository-01>` does not mean "the lowest-numbered slot".

**This is label masking, not guaranteed blinding.** Two limits are named rather than hidden:

- The prose keeps file paths, symbol names and the reviewer's own style. Any of those may suggest
  which arm wrote a packet.
- In this pilot only one arm published structured items beside its body, so whether `items` is
  populated correlates with that arm.

Treat any such inference as a guess, and freeze rulings before opening the mapping.

## Why the packets are sealed rather than committed in the clear

Masking the arm is achievable; masking the target is not, because the grading needs the file paths
and symbol names that name it. Publishing the pilot's six packets would therefore name the two
slots the pilot ran on — and the selection rule is public ("the adjudicated clean slot and the
lowest-numbered buggy slot, clean first"), so that pair identifies the clean slot outright.
[`seal.json`](seal.json) and [`SHA256SUMS`](SHA256SUMS) record the ciphertext and plaintext
digests. [`packet-index.json`](packet-index.json) is what may be public: random packet ids and the
digest of each masked packet, mapping to nothing published.

## Opening them

```sh
K=~/.config/bounded-discovery/issue-148/truth.key
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass file:"$K" \
  -in grading-packets.tar.gz.enc -out grading-packets.tar.gz
shasum -a 256 -c SHA256SUMS
tar -xzf grading-packets.tar.gz
```

A hash mismatch means the plaintext is not the sealed one; do not grade against it.

`grading-packets.json` is the grader's input. `redaction-map.json` is not: it holds the raw-to-mask
table, the packet-to-attempt mapping with arm, model, replicate, completion and cost, and the raw
payload digest for each packet. #152 opens it only after its rulings are frozen; #153 uses it to
restore the masked values at reveal.

One thing #152 must not do: grade this closeout's own outcomes. The packets are the pilot's
reviewers' claims, not the collectors'.
