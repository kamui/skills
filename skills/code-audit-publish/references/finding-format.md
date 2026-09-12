# The finding contract

Every finding is read twice: by a human deciding what matters, and by an agent deciding what to do. The two read the same text differently. A human treats severity as advice and applies judgment; an agent treats it as an instruction and does the work. Findings that serve only one reader fail the other — prose a human likes is unparseable, and a bare JSON blob is unreadable in a pull-request thread.

So each finding carries both renderings of the same judgment, and the low band states its permission in words rather than trusting a label to imply it.

## Vocabularies

**Axis** — `[Code]` or `[Requirements]`. `[Code]` is correctness, documented repository standards, and implementation quality. `[Requirements]` is missing, partial, or incorrect behavior against the originating spec, plus behavior the spec never asked for. A question carries no axis.

**Action** — what a reader does. Three values, closed:

| Action | The agent does | The human reads |
| --- | --- | --- |
| `must-fix` | make the change; the pull request should not merge until this is settled | blocking |
| `consider` | may make the change or close it unactioned; both are correct | optional |
| `question` | **change no code**; answer it, or say what would settle it | open question |

**Priority** — `P0`–`P3`, the human's triage order:

- `P0` — drop everything. Blocking release, operations, or major usage. Only for issues that hold under any input, with no assumptions.
- `P1` — urgent.
- `P2` — normal; worth fixing eventually.
- `P3` — low; nice to have.

Priority and action are separate judgments. Priority describes impact and urgency; action is a merge judgment, licensed by **demonstrated merge consequence** — what provably goes wrong if this merges unfixed — never by the severity label. `P0` is inherently `must-fix`; otherwise do not derive action from priority, fix size, or artifact type, and do not inflate priority to communicate action. In particular, `P1` does not mean blocking and `P2`/`P3` do not mean optional. Restatement drift — a second document carrying an older version of a rule whose canonical statement is correct — is `P2` when the stale document is executed as instructions and `P3` otherwise; it is never `P1` or `P0`.

The calibration: a proven correctness, security, or explicit-requirement gap on an authoritative execution path is `must-fix`, even when the edit is one line or documentary. A restatement of a rule in a second document is on an authoritative execution path only when **both** hold: the canonical rule is not linked or referenced from the stale text, so a reader following the stale text has no cue to the correct rule; **and** the stale text, followed literally, causes a concrete wrong action the canonical text forbids — name that action. When either fails, the drift is `consider`: the canonical behavior remains satisfied and merge does not depend on resolving it. A real doc-sync drift is usually this shape. The verifier may recalibrate action independently of priority, and a `plausible` verdict makes a candidate `question` at any priority.

Do not label everything `consider` and do not label nothing `consider`. The first is a review that blocks nothing; the second is a review where a nit stops a merge.

**Confidence** — implicit, never written. Publication is the assertion: a finding published as a finding was verified `confirmed`. `plausible` publishes as a question and `refuted` does not publish at all, so a confidence key in the trailer would never vary.

## Anchor and fix site

A finding has two locations and they are not always the same one. The forge constrains where a comment may attach — GitHub takes line comments only on lines the diff touches — but nothing constrains where the edit belongs.

- **`anchor`** — the `file:line` the comment attaches to. Must be a line the diff touches.
- **`fix`** — where the edit goes. Omitted when it is the anchor.

Choose the anchor in order, taking the first that applies:

1. The fix site is in the diff — anchor there. A finding about a whole file the diff adds or rewrites has no single line: it goes in the review body, still inside the review, because the batched review call takes line comments only (`publishing.md` § One review, one call).
2. Otherwise, the diff line that **makes the finding true**: the change that opened the gap, or that stranded code elsewhere.
3. Otherwise, the diff line that most directly **demonstrates** it — a test that looks like it covers the case and does not, a call site that breaks.
4. Otherwise the finding has no honest anchor, and it goes in the review body. Do not attach it to an unrelated line merely to make it a line comment.

A finding about a guarantee this change removed settles its coordinates the same way as any other, and in the same order: the fix site is wherever the edit goes, and the ladder runs from there. Where the repair is to restore the protection the diff removed, the fix site is that changed line, rung 1 applies, and the finding carries no separate `fix` — `Change` still says what to restore. Where the removal is deliberate and the untouched consumer is what must adapt, the fix site is the consumer, rung 1 cannot apply, and rung 2 anchors the comment on the line that dropped the lock, the ordering, the ownership rule, or the validated invariant. Deciding the anchor first and calling the consumer the fix site because the anchor landed elsewhere inverts this, and sends the edit location to a line nobody needs to edit. What holds in both directions is what the anchor means: do not describe the consumer's line as one the diff touches, and do not re-attribute the finding to some nearer touched line, in order to manufacture an anchor — the anchor asserts that the diff changed that line, the forge will reject it where it did not, and a reader who follows it finds a claim the code does not make. A removed-guarantee finding with no diff line to attach to goes in the body like any other, with both coordinates in its prose.

Where the two differ, `Change` names the fix site in prose **and** the trailer carries it as `fix=`:

```markdown
**[Code] [consider] [P3] `CONTEXT.md` glossary still describes four obligation kinds**

`record-schemas.md:392` broadened the obligation vocabulary; the canonical glossary was not updated with it and still lists four.

**Triggers when**: a maintainer extending the ledger trusts the glossary and writes code or docs that contradict the enum.

**Change**: update the `Research obligation` entry at `CONTEXT.md:326-327` to carry all five kinds.

Closing this without action is a correct response.

<!-- finding id=code/record-schemas/stale-glossary axis=code action=consider priority=P3 fix=CONTEXT.md:326 head=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 -->
```

A human reads the prose and goes where it says. An agent that parsed only the anchor would edit the wrong line — so this is the one place where omitting a machine-readable field turns a helpful comment into a harmful one.

## Claim and support

A finder produces two things about every candidate, and only one of them crosses to the verifier.

- **`claim`** — a flat, falsifiable statement of what is wrong, with its citations: the quoted code, the quoted rule, the quoted requirement. Written to be checked, not to persuade.
- **`support`** — how the finder came to believe it: what it ran, what it read, what it remains unsure of.

The test for which is which: **the claim describes the artifact; the support describes the finder.** Anything that would read identically had a different finder found the same defect is claim. Anything in the first person, or that reports a process, is support.

Quoted lines from the repository and the spec are facts about the artifact, so they belong in the claim. The split withholds argument, not evidence.

`support` reaches neither the pull request nor the verifier. It exists so a finder has somewhere to put its uncertainty other than the finding itself, and so a run can be audited afterwards. A verifier told that the finder already demonstrated something believes it, and the step decays into agreement; re-deriving the claim from the code is the entire check.

The published comment's evidence paragraph is written from the `claim`.

## Finder candidate block

End the candidate material with exactly one fenced `candidates` block. Use one exact
`### Candidate` heading per candidate and these fields in this order; a zero-candidate report uses
`None.` as the block's entire content.

`````markdown
````candidates
### Candidate
id: code/file-slug/defect-slug
axis: Code
anchor: path/to/file.ext:123
fix: (same as anchor)
title: Short defect title
claim: Flat, falsifiable claim with evidence pointers.
support: Finder process, checks, and uncertainty.
trigger: Concrete input, state, or environment that produces the wrong outcome.
priority: P2
action: must-fix
````
`````

Use `Code` or `Requirements` for `axis`. Keep `fix` present and write `(same as anchor)` when it is
the anchor. The verifier-prompt builder carries every other field verbatim and removes `support`
mechanically, so load-bearing evidence belongs in `claim` and the concrete scenario belongs in
`trigger`.

Each field appears once, and the order above is the grammar rather than a house style. A column-zero
line that begins with one of these ten labels is always a field line, and it must name the next field
still expected; the builder refuses a candidate whose column-zero label is out of order or repeated,
because it cannot tell a quoted `support: enabled` from the candidate's own routing and will not
guess. Every other line continues the field above it and is carried through verbatim, so a `claim`
quoting configuration or code that begins with a field label indents that line — `  priority: high`
reaches the verifier as written, while `priority: high` at column zero is refused. Write `anchor`,
`fix`, and every ledger row's evidence as one whole repository-relative `path:line` coordinate (or,
for a `fix` that names a file, the bare path), optionally in backticks; a path may contain spaces,
because the builder reads the whole field as the coordinate rather than picking a path out of prose.
It relates a ledger row to a candidate by whole file identity, so `foo.py` and `src/foo.py` are two
different files and neither stands in for the other.

## Shape

A finding comment:

```markdown
**[Code] [must-fix] [P1] `parseOrder` swallows the validation error on the retry path**

`src/order.ts:47` — the catch added at line 47 returns the order unchanged when `validate()` throws, so a retried order that fails validation reaches the caller as if it had passed.

**Triggers when**: an order fails validation on a retry attempt — the caller receives an unvalidated order and no error.

**Change**: rethrow inside the catch at `src/order.ts:47`, or attach the validation failure to the returned result.

<!-- finding id=code/order-ts/swallowed-validation-error axis=code action=must-fix priority=P1 head=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 -->
```

Four parts, and each one serves a specific reader:

1. **The tag line.** Axis, action, priority, then a title of at most 80 characters, imperative or declarative, naming the defect rather than the area. A human scans it; an agent parses it. It is redundant with the trailer on purpose — the trailer is authoritative, the tag line is what a human sees.
2. **The evidence.** Written from the `claim`: `file:line` and what the code actually does. Cite the documented rule or the originating requirement where one applies, quoting it. One paragraph. Quote at most three lines of code — a diff the reader already has does not need reproducing.
3. **`Triggers when`.** The concrete inputs, state, or environment that produce the wrong behavior. This is the field an agent uses to check its own fix, so "could be wrong under some conditions" is not an answer. A finding that cannot name its trigger is a `question`, not a finding.
4. **`Change`.** The concrete edit. A human can work a fix out from the diagnosis; an agent handed only a diagnosis invents one. Name the file, the site, and what to do there. Where the fix is a literal replacement, give it as a fenced ```suggestion``` block with exact whitespace — and only then, because a suggestion block that does not apply cleanly is worse than prose.

Nothing above the trailer but these parts, and the evidence stays one paragraph — where it wants a second, that is usually two findings, or argument that belongs in `support`.

A `consider` finding adds one line before the trailer, verbatim:

> Closing this without action is a correct response.

Without it, an agent does the work anyway and the priority machinery upstream buys nothing.

A question:

```markdown
**[Question] Is the 30s timeout at `src/fetch.ts:88` deliberate?**

`src/fetch.ts:88` sets 30s where every other caller uses 5s. The issue is silent on timeouts and the history shows no rationale. If it is deliberate, a comment saying why would stop the next reader changing it.

**Change no code for this.** Answer it, or say what would settle it.

<!-- finding id=question/fetch-ts/timeout-30s action=question head=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 -->
```

## The trailer

An HTML comment: invisible rendered, present in the raw body via `gh api`. It is the machine-authoritative copy of the tag line — where the two disagree, a reader should trust the trailer, so do not let them disagree.

```
<!-- finding id=<id> axis=<code|requirements> action=<must-fix|consider> priority=<P0-P3> fix=<file:line> head=<full 40-hex sha> -->
```

`fix` is present only when the edit belongs somewhere other than the line the comment sits on. The anchor itself needs no key — the forge already reports the comment's `path` and `original_line`. A question's trailer carries only `id`, `action=question`, and `head`: no axis, no priority, no fix.

Reply, verdict, and ID correlation rules are in [`publishing.md`](publishing.md).
