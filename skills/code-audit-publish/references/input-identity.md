# Reviewed inputs and duplicate identity

Read with step 1 on every run. The forge packet is the reviewed evidence, the context digest identifies intent and guidance, and the later-state check accounts for discussions and undated thread state. PR lifecycle (`state` and `merged`) is also pinned in the run trailer: an open-target review cannot suppress a subsequent explicit merged-target retrospective. None is publication authority.

## Fingerprint membership

Run `python3 scripts/context_fingerprint.py --packet packet.json context-inputs.json` from this skill's root. The JSON file has `specs` and `guidance`; `pr` and `issues` come exclusively from the packet's `fingerprint` section. Use the same normalized PR and issue records in both finder handovers and prior-state reading, including every relevant issue, not just closing references.

The digest contains exactly:

- PR title and body.
- Each reviewed issue's coordinate, title and body, plus all obtained comments' numeric id, author, created/updated timestamps and verbatim body. `comments_available: false` with no comments denotes an unavailable discussion; `comments_complete: false` beside obtained comments denotes truncation. The packet emits those markers. A genuinely available empty list has neither marker. Keep the corresponding gaps in coverage; a digest of partial evidence never makes it complete.
- Every caller-supplied or explicitly resolved non-issue spec actually used for intent, with its URL/coordinate as `identity` and exact text as `text`. Include an external spec's discussion as separate spec entries keyed by stable source/comment identity, with verbatim body and retained author/created/updated metadata serialized in the text. Keep unavailable or truncated source slices in coverage; never replace them with invented requirements. Inline text may omit identity: the helper derives `inline:<sha256-of-text>`. With no issues, supplied specs still govern alongside the PR's claims and non-goals.
- Applicable tracked **base-branch** guidance, each represented by repository-relative `path` and full `blob_sha`: exactly the `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md` and `CODING_STANDARDS.md` files emitted by `build_shared_block.py` for ancestors of changed paths (both rename paths). Add each further tracked base guidance file actually consulted through one of those files' normative pointers, with its base blob id. Resolve such pointers only when applicable to the reviewed paths/task. Carry those additional contents and provenance to each affected finder/verifier as well. Exclude head versions, guidance for unrelated scopes, non-normative linked material, and runtime instructions. Issue/spec text belongs in its own field; record a design document used as intent under `specs`, not guidance. Freeze the final membership in `context-inputs.json`.

This retains the audit's existing guidance discovery, rather than adopting the routine skill's narrower file membership. Blob ids refer to exact contents, including whitespace. Read them from the shared block's provenance or `git rev-parse <base-sha>:<path>`; never substitute the working tree. If more applicable guidance is read during discovery or verification, add its identity and recompute the final digest.

Normalization is mechanical: null strings become empty strings, null arrays become empty arrays; strings otherwise retain their exact UTF-8 contents. Numeric comment ids, including decimal strings with leading zeroes, become canonical decimal strings; booleans are invalid ids. Sort issue comments by numeric id, issues by UTF-8 coordinate, specs by UTF-8 identity/text, and guidance by UTF-8 path/blob id, with canonical JSON tie breaks for equal issue/comment keys. Input list order and object key order do not matter; duplicate entries remain entries, so assemble each source once (the packet deduplicates forge page boundaries by stable ids). Serialize with sorted object keys, no whitespace, literal Unicode and no NaN; hash those UTF-8 bytes with SHA-256. See the packaged helper and its CLI fixtures. Normalization imports no sibling skill.

## Duplicate gate

After computing the reviewed inputs, select a candidate prior review from the posting identity and run:

```sh
python3 scripts/review_identity.py packet.json --review <numeric-review-id> --author <login> --merge-base <full-sha> --inputs context-inputs.json
```

Exit 0 means its single trailer matches `workflow=v2b-5`, the full head/base/merge-base, explicit PR `state` and boolean `merged`, encoded base ref, sorted issue membership and freshly computed full 64-hex `context`, both prior coverage and current packet coverage are complete, and no later-state line exists. Report that existing review only when there is also no newly discovered eligible material and no additional input/coverage gap outside the packet. Exit 1 prints why this is a review to perform, not a duplicate to skip. Exit 2 is unreadable/malformed input: report the output and stop the step. This helper validates duplicate identity only; final payload validation is a separate contract.

`python3 scripts/forge_packet.py later-state packet.json --review <id>` is the underlying check. It retains later PR/issue edits, reviews, PR comments and inline replies, including human prose without trailers. Only the candidate review's original submission and original line comments are excluded; later edits to that output still count. A reply belongs to later state even when its `review_id` equals the candidate's. Relevant evidence changes must be assessed even when status and head stay unchanged. The helper conservatively treats every reported later item as defeating suppression; it never decides relevance from words or trailer presence.

Thread resolution has no edit timestamp. Every resolved thread and every thread predating the candidate that has no later comment produces a `thread-state` line, because it may have been resolved or reopened since. Unknown resolution state and absent/malformed timestamps cannot establish silence either: treat them as incomplete evidence. This audit deliberately takes a new assessment on any such line; there is no model override that converts incomplete evidence into an exact duplicate.

Historical workflows and trailers without a digest remain readable for stable finding ids, replies, verdicts and the round cap. They never suppress a new `v2b-5` review. Keep both prior findings and ledgers through the same-head re-review; revisit a conclusion when its evidence changed. Publish new eligible findings in the new batch and act on standing findings in their original threads, regardless of aggregate status equality.

## Coverage and freshness

Every missing source or connection slice is retained in the run record and summary, with what it could change. Inspect the packet's per-connection counts, cursors and gaps; `complete: false` prevents complete review coverage and duplicate suppression even when known findings may still publish. Explicit source failures also retain the source URL/coordinate and requested cursor in the fetch ledger; a bare failed filename is not the recovery request.

Before writes, step 4 makes a separate complete freshness collection in its own directory. Compare normalized records, not response page order, filenames, connection cursor placement or generated bookkeeping. Any evidence-affecting failure or difference requires reassessment. Recheck external spec sources too. The explicit state/merged publication rules apply to both the reviewed packet and the fresh one: missing state never grants authority, and a merged retrospective target requires separate explicit publication authority. Identity eligibility and an advisory status do not grant that authority.
