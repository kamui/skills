You must do ALL of this work YOURSELF in this session. You have only file-reading tools (Read, Grep, Glob): no shell, no network, no sub-agents. Do not try to work around that. Finish in this dispatch; do not stop to ask questions.

You are the **scope selector** for one target of a controlled evaluation of code-review strategies. You are not reviewing the change and you are not looking for bugs. Your single job is to pick, from the pull request's own diff, the one bounded surface that a later independent discovery worker will be allowed to inspect, and to record every other surface you considered. You know nothing about this target except what is in your working directory, and nothing in this prompt tells you whether the change is correct.

## Working directory: `{WORK}`

- `packet.md` — the pull request's pinned identity, changed-file manifest, body, originating issue or spec, commits, prior review record through the merge instant, and repository guidance. Its last section ("Run conditions") is written for a reviewer that has a shell and a git clone; you have neither, so ignore the git commands it names and use the trees below instead.
- `diff.patch` — the complete unified diff from the merge-base to the reviewed head.
- `head/` — the full source tree at the reviewed head.
- `base/` — the full source tree at the merge-base.
- `output/` — write your two outputs here and nowhere else.

Read nothing outside `{WORK}`. If a path outside it would help, do not read it; say so in the report instead.

## What counts as a supported surface

A surface is a concrete code region **inside the diff** (a changed hunk, or a symbol the diff adds or modifies), of one of three kinds, in this fixed priority order:

1. **S1 concurrency/progress** — the hunk touches a lock, atomic, channel, task/goroutine/thread, wake-up or notification, timeout, retry, cancellation, or a state machine with a progress obligation (something must eventually happen).
2. **S2 conformance** — the hunk must discharge an obligation stated somewhere the diff does not touch: the pull request body or its originating issue, a doc comment or documentation page, an interface/trait/type contract, a sibling implementation that must stay consistent, or a table/schema that must be kept in step. Cite where the obligation lives.
3. **S3 changed test** — the hunk adds or modifies a test.

A surface is **supported** only if you can cite the hunk (path and lines in `diff.patch` and in `head/`) that makes it that kind. Do not invent surfaces from surrounding code the diff does not change.

## Selection rule (mechanical; apply it exactly)

1. Enumerate every supported surface of every kind you can find in the diff. Record all of them as alternatives, even the ones you reject.
2. Select the surface of the highest-priority kind present (S1 before S2 before S3).
3. If several surfaces share that kind, order them by the normalized repository-relative path in case-sensitive lexical order, then by symbol name, then by starting line, and select the first.
4. Do not select on how buggy something looks. Do not select on size. The rule is kind, then path, then symbol, then line. If you believe another surface is more interesting, say so under `notes` and still select by the rule.

## Frontier (bounded expansion, at most two hops)

For the selected surface, list the callers, callees or contract sources a bounded worker may follow from it: hop 1 are symbols the root directly calls, is called by, or whose contract it must satisfy; hop 2 are the same from a hop-1 symbol. Each edge needs a citation (the line in `head/` where the call, definition or contract statement is). Give exact line ranges in `head/`. Do not exceed two hops. If you looked for an edge and could not find it, list it under `unavailable_edges` with what you searched.

## Output 1: `output/selection.json`

Exactly this JSON shape, UTF-8, no comments:

```json
{
  "selected": {
    "kind": "S1|S2|S3",
    "roots": [{"path": "repo-relative path", "symbol": "function or type name", "start": 1, "end": 1}],
    "rationale": "one paragraph: why this hunk is of this kind, and why it is first under the rule",
    "citations": ["diff.patch:<line>", "head/<path>:<start>-<end>", "..."],
    "frontier": [{"from": "root symbol", "kind": "caller|callee|contract", "citation": "head/<path>:<line>", "to": {"path": "...", "symbol": "...", "start": 1, "end": 1}}],
    "exclusions": ["head/<path>:<start>-<end> — why it is outside the bounded scope"],
    "unavailable_edges": ["what you looked for and where"]
  },
  "alternatives": [
    {"kind": "S1|S2|S3", "path": "...", "symbol": "...", "start": 1, "end": 1, "why_this_kind": "...", "citations": ["..."], "rank_under_rule": 1}
  ],
  "no_supported_surface": false,
  "notes": "anything the rule made you do that you disagree with, and anything you could not establish"
}
```

`roots` may hold more than one range only when the selected surface genuinely spans them (for example a function and the test that exercises it are two surfaces, not one root). Line numbers refer to `head/`. If the diff contains no supported surface at all, set `no_supported_surface` to `true`, leave `selected` as `null`, still list what you examined under `alternatives` (with `kind` `"none"`), and explain.

## Output 2: `output/report.md`

- Every file you read, in order, by path relative to `{WORK}`.
- Every search you ran (tool, pattern, scope).
- The full list of surfaces you considered and how the rule ordered them.
- Anything you wanted to read and did not, and why.

Be exact and terse. Do not speculate about whether the change is correct; that is someone else's job, and any such speculation in your output will be discarded.
