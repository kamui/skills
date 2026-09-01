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

Action derives from priority, so one judgment produces both: `P0`/`P1` → `must-fix`, `P2`/`P3` → `consider`. The one override is the verifier: a `plausible` candidate becomes `question` at any priority.

Do not label everything `consider` and do not label nothing `consider`. The first is a review that blocks nothing; the second is a review where a nit stops a merge.

**Confidence** — `confirmed` only. A finding published as a finding has been confirmed. `plausible` findings publish as questions, `refuted` ones do not publish at all.

## Shape

A finding comment:

```markdown
**[Code] [must-fix] [P1] `parseOrder` swallows the validation error on the retry path**

`src/order.ts:47` — the catch added at line 47 returns the order unchanged when `validate()` throws, so a retried order that fails validation reaches the caller as if it had passed.

**Triggers when**: an order fails validation on a retry attempt — the caller receives an unvalidated order and no error.

**Change**: rethrow inside the catch at `src/order.ts:47`, or attach the validation failure to the returned result.

<!-- finding id=code/order-ts/swallowed-validation-error axis=code action=must-fix priority=P1 confidence=confirmed head=a1b2c3d -->
```

Four parts, and each one serves a specific reader:

1. **The tag line.** Axis, action, priority, then a title of at most 80 characters, imperative or declarative, naming the defect rather than the area. A human scans it; an agent parses it. It is redundant with the trailer on purpose — the trailer is authoritative, the tag line is what a human sees.
2. **The evidence.** `file:line` and what the code actually does. Cite the documented rule or the originating requirement where one applies, quoting it. One paragraph. Quote at most three lines of code — a diff the reader already has does not need reproducing.
3. **`Triggers when`.** The concrete inputs, state, or environment that produce the wrong behavior. This is the field an agent uses to check its own fix, so "could be wrong under some conditions" is not an answer. A finding that cannot name its trigger is a `question`, not a finding.
4. **`Change`.** The concrete edit. A human can work a fix out from the diagnosis; an agent handed only a diagnosis invents one. Name the file, the site, and what to do there. Where the fix is a literal replacement, give it as a fenced ```suggestion``` block with exact whitespace — and only then, because a suggestion block that does not apply cleanly is worse than prose.

Six lines or fewer above the trailer.

A `consider` finding adds one line before the trailer, verbatim:

> Closing this without action is a correct response.

Without it, an agent does the work anyway and the priority machinery upstream buys nothing.

A question:

```markdown
**[Question] Is the 30s timeout at `src/fetch.ts:88` deliberate?**

`src/fetch.ts:88` sets 30s where every other caller uses 5s. The issue is silent on timeouts and the history shows no rationale. If it is deliberate, a comment saying why would stop the next reader changing it.

**Change no code for this.** Answer it, or say what would settle it.

<!-- finding id=question/fetch-ts/timeout-30s action=question head=a1b2c3d -->
```

## The trailer

An HTML comment: invisible rendered, present in the raw body via `gh api`. It is the machine-authoritative copy of the tag line — where the two disagree, a reader should trust the trailer, so do not let them disagree.

```
<!-- finding id=<id> axis=<code|requirements> action=<must-fix|consider> priority=<P0-P3> confidence=confirmed head=<short sha> -->
```

`id` slugs the axis, the file, and the finding — `code/order-ts/swallowed-validation-error`. **Never a line number**: lines drift between rounds and the id has to survive that. One finding against the same code keeps one id across every round, which is what lets a re-review correlate it to its thread and verdict it rather than posting it again.

A candidate the verifier ruled `plausible` publishes as a question and takes a `question/...` id, not the axis id it was proposed under. If a later round confirms it, it becomes a finding under its own axis id and the question resolves as answered. The two ids stay distinct on purpose: the record then shows a question that turned out to expose a defect, rather than a finding that silently changed shape between rounds.

A responding agent replies with a matching trailer:

```
<!-- reply to=<finding id> disposition=<implemented|already-addressed|answered|declined|needs-info|blocked> head=<short sha> -->
```

and a re-review writes its verdict on the thread:

```
<!-- verdict on=<finding id> verdict=<fixed|accepted|obsolete|not-fixed> head=<short sha> -->
```

`fixed` names the finding's fate, not the reply's credibility — a finding that still stands is `not-fixed`. `accepted` is how a decline you agree with gets closed.

## Humans without trailers

A finding or reply written by a person carries no trailer. Read it as prose, infer what it means, and treat it exactly as any other item. Never skip something for lacking a trailer, and never write a trailer on a person's behalf. The trailers speed up the agent path; they do not gate it.
