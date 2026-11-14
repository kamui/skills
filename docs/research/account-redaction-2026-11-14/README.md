# Account redaction, 2026-11-14

This repository was re-created from a rewritten history. Research transcripts and probe records under `docs/research/` recorded the account and the machines that produced them: Claude Code writes the signed-in account's email address into every session, and shell output and saved tool reports named the machines. This record says what was replaced, where, and how to check it.

It follows the [redaction of `kamui/code-review-bench`](https://github.com/kamui/code-review-bench/tree/main/docs/research/account-redaction-2026-11-13) of 2026-11-13 and applies the same rules, with one more machine name. The earlier repository is kept as the private archive `kamui/skills-archive`. [The owner's words](authorization.md) are saved beside this record.

## What was replaced

| Identifier | Replacement | Files at the tip |
| --- | --- | --- |
| The account's email address | `[redacted-email]` | 22 |
| The names of the two machines that ran most of the work | `host-01` and `host-02` | 20 |
| The local hostname of a third machine | `host-03.local` | 1 |

The same check looked for the Anthropic organization id, the Codex account ids and the Codex plan type. None of them occurred in this repository. The first two machine names have stand-ins of the same length. The third name occurred once, as a `.local` hostname in the `uname` output of `docs/research/bounded-discovery-qualification-2026-09-12/probes/P00-runtime-inventory/versions.txt`. Every blob, at every nesting level, and every commit was searched for other hostname uses of it, after `@`, before a shell prompt, in a hostname field and in `uname` output. There were none. The owner's home directory path was not replaced, by the owner's decision.

At the tip, 40 tracked files changed. They are 23 compressed transcripts (`.jsonl.gz`), 14 `.jsonl` files and 2 `.json` files under `docs/research/review-code-artifact-savings-2026-09-22` (34), `docs/research/review-code-rewrite-2026-09-22` (4) and `docs/research/review-code-one-record-2026-09-24` (1), and the `versions.txt` file above. The skills held no identifier. The `skills/` tree is byte-identical, and so is the tree id of every skill folder.

## Git history

The history was rewritten with `git filter-repo`, using a mailmap, message replacements, and a blob callback that substitutes the redacted bytes.

- 42 blobs changed across the history: the 40 above and two earlier versions of `docs/research/review-code-rewrite-2026-09-22/acceptance/C8-*/transcript.jsonl.gz`.
- Two commits named the account's email address as author and committer. They now name the owner's public address. Neither was on `main`.
- 23 commit messages lost a `Co-Authored-By: Claude` trailer. No commit message held an identifier.
- 23 commit messages cite an abbreviated commit id that `git filter-repo` replaced with the new id. Three cited ids name commits that exist only in the archive, and those were left as they were.
- `git filter-repo` removed the signatures of the 235 commits that GitHub had signed when merging. A rewritten commit cannot keep a valid signature.
- 1,062 of the 1,068 carried commits have a new id. [`commit-map.v1.txt`](commit-map.v1.txt) lists each earlier id with its new one. [`dropped-commits.v1.txt`](dropped-commits.v1.txt) lists the 40 earlier commits that only pull request refs reached and that no kept ref reaches. They remain in the archive.
- `main` is the only branch. Pull request refs do not exist in this repository.
- The first rewritten commits are `eea2e2c5d67633103e5619c74eac484cc3fd2c35`, the rewrite of the merge of #1, and `282608877518533e61382253ba353db3718428b7`, the rewrite of the commit that initialized the public repository. Every ref in this repository descends from one of them, and neither exists in the earlier history.

Three tags keep the pull request heads whose commits and skill trees `kamui/code-review-bench` cites:

| Tag | Earlier head | Keeps reachable |
| --- | --- | --- |
| `provenance/pr-397-head` | `136dbc7897e2` (#397) | 24 cited commits, among them the only one no other tag reaches |
| `provenance/pr-407-head` | `ca4ed67a77c5` (#407) | 32 cited commits, and the only commit that carries skill tree `6e6c654707` |
| `provenance/pr-413-head` | `6440ebe7353f` (#413) | 38 cited commits, six of them reached by no other tag |

Between them the tags reach all 39 commits of this repository that the benchmark's run manifests cite, and a commit that carries each of the skill trees `5e12864b52`, `6862d993a1`, `6e6c654707` and `c3c53da538`. A tree id is a hash of the tree's content, and these trees held no identifier, so all four ids are unchanged. The benchmark also pins tree `59e7df1b15` for this skill. That tree was never in this repository: it is `5e12864b52` with the benchmark's `bench/runs/2026-09-28-verification-off-staged/candidate.patch` applied. [`pinned-commits.v1.json`](pinned-commits.v1.json) gives each cited commit's new id, the tags that reach it and where the benchmark cites it, and the same for each tree.

The benchmark's frozen manifests keep the earlier commit ids. Look up the new id in `commit-map.v1.txt` or `pinned-commits.v1.json`.

One commit after the rewrite recomputed the records at the tip that pin a redacted file by hash:

- the 23 `.sha256` sidecars that name the hash of a redacted transcript's decompressed content. The three other sidecars name transcripts that held no identifier and did not change;
- `versions_capture_sha256` in `docs/research/bounded-discovery-qualification-2026-09-12/probes/P00-runtime-inventory/inventory.json`, which names the hash of `versions.txt`. No record pins `inventory.json` by its hash in turn.

These records in earlier commits and in the three tags still name the hashes of the earlier content.

## Issues and pull requests

GitHub numbers issues and pull requests in one sequence, and commits, research notes and the benchmark cite those numbers. An issue was created at every number from 1 to 471, in order, before anything else:

- 186 issues were created again with their title, body, labels, comments and state: 170 closed as completed, 15 open, and #394, closed as not planned;
- 241 pull request numbers are closed issues with the pull request's title and description, the date it merged or closed and, where the merge commit survives, its new id. 240 pull requests were merged. #407 was closed without merging and is kept because a tag is named after it;
- 44 numbers are unused. The owner chose not to carry over the issues closed as not planned and the pull requests closed without merging. That leaves out 40 issues and 4 pull requests. #394 was kept because the benchmark, files in this repository and the #407 stub cite it. Each unused number was created to hold its place and then deleted.

87 of the 127 sub-issue links were created again. The other 40 have a parent or a child among the unused numbers.

The same replacements were applied to this text, and commit ids in it were mapped to the new ones. Every date on GitHub is now the day of the re-creation; the original dates are in the text. The pull requests themselves, with their diffs, reviews and 165 comments, and the 18 comments on issues that were not carried over, are in the archive.

## Verification

Run on the rewritten repository before publication, with no network:

| Check | Result |
| --- | --- |
| A second redaction pass over every git object | 0 objects would change |
| The same pass over a fresh clone's working tree at `main` and at each tag | 0 files would change |
| The third machine name in a hostname form, in any blob, commit, path or ref | 0 |
| Commit authors and committers naming the account's email address | 0 |
| `main`'s tree against the earlier tip | differs in the 40 redacted files, the 24 repinned records and this folder only; same modes |
| Every `.sha256` sidecar at the tip against its transcript | 26 match |
| `versions_capture_sha256` against `versions.txt` | matches |
| The four skill trees above | present, ids unchanged |
| The 39 cited commits | each maps to a commit that a tag reaches |

## Limits

- The check finds the literal values, the Codex fields, the first two machine names in lower case and the third in the forms above. It does not find an identifier written in a form nobody anticipated.
- 41 blobs in `sealed/` folders are encrypted archives (25 at the tip). Their contents could not be searched, and they are unchanged byte for byte.
- The home path remains, as described above.
