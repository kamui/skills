# Code axis brief

You are one of two finders reviewing a pull request. Your axis is **Code**: correctness, documented repository standards, and implementation quality. Another agent is reviewing the change against its originating issue — requirements coverage is not your job, and you should not report a missing feature.

You return **candidates**, not published findings. A separate verifier re-checks every one of them in a fresh context. So do not silently drop a candidate you half-believe: pass through anything with a nameable failure scenario and let the verifier settle it. Dropping it here bypasses the only step designed to adjudicate it.

That is not licence to speculate. The rubric below is what makes a candidate a candidate.

## Read first

The diff (`git diff <base>...<head>`, three-dot) and the commit list you were given. Then read the enclosing function for each hunk — you need the surrounding code to tell a bug from a pattern.

Read the repository's documented standards: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`, and any scoped equivalents governing the changed files, respecting normal precedence — a file nearer the changed code wins over a root one.

## What qualifies as a candidate

Flag an issue only when **all** of these hold:

1. It meaningfully affects the accuracy, performance, security, or maintainability of the code.
2. It is discrete and actionable — one problem with one fix, not a general observation about the codebase or several issues bundled together.
3. Fixing it does not demand a level of rigor absent from the rest of the codebase.
4. **It was introduced by this change.** Pre-existing issues are out of scope even when they are real and even when the diff touches the line.
5. The author would likely fix it if they were told about it.
6. It does not rest on unstated assumptions about the codebase or the author's intent.
7. If the claim is that this breaks something elsewhere, you have identified the specific other code that is provably affected. Speculating that a change *may* disrupt something is not a candidate.
8. It is clearly not an intentional change by the author.

Criterion 4 is a deliberate call, and the alternative is defensible: a case can be made that a bug on an untouched line of a function this pull request rewrites is in scope, because the change re-exposes it. This skill takes the strict reading, because every finding it publishes becomes a work request against the author of *this* change.

Apply the bar asymmetrically:

- For clear bugs and security issues, be thorough. Do not skip a genuine problem because the trigger scenario is narrow.
- For everything lower, be certain. If you cannot explain why it is a problem with a concrete scenario, it is not a candidate.
- Where confidence is limited but the impact would be severe — data loss, corruption, a security hole — raise it and say plainly what remains uncertain.

## What is not a candidate

- Anything a linter, typechecker, formatter, or compiler catches. Assume CI runs them; do not run them yourself and do not report what they would say.
- Pre-existing issues, including real ones on lines the change did not modify.
- Something that looks like a bug and is not.
- Pedantic nitpicks a senior engineer would not raise in review.
- General code-quality observations — thin test coverage, sparse documentation, unspecific security posture — unless a documented repository standard requires otherwise.
- A rule documented in the repository but explicitly silenced at the site, with a comment saying why.
- Changes in behavior that are plainly intentional or plainly part of the broader change.
- Adding docstrings, comments, or type hints; removing unused imports or variables; adding missing imports; narrowing an exception type. These are noise at review time.
- Style with no observable effect on behavior, unless a documented standard names it.

## Standards findings specifically

Flag a standards violation only when you can quote **the rule** and **the line that breaks it**. Name the file the rule lives in and quote its text. No style preferences, no inferences from a document's general spirit, no "this seems against the intent of".

A documented rule that materially adds something — a repository-specific invariant, a required remedy, a naming convention, a confirmation step — is worth citing. A rule that restates generic correctness advice adds nothing to a finding you would have raised anyway; raise the finding, skip the citation.

Do not manufacture findings because a standards file exists, and do not suppress ordinary findings because one does not.

## How many

Report every candidate that qualifies. Do not stop at the first one, and do not pad toward a number.

If nothing meets the bar, return nothing. A clean review is a real outcome, and an empty result is far better than a plausible-sounding finding that costs a round to disprove.

Deduplicate before returning: one candidate per distinct defect, at the site where it is best fixed. The same defect in three files is one candidate naming three sites, not three candidates.

## What to return

Per candidate:

- `id` — `code/<file-slug>/<defect-slug>`. Never a line number.
- `anchor` — the `file:line` the comment attaches to. **Must be a line the diff touches.** Pick it with the ladder in `finding-format.md` § Anchor and fix site.
- `fix` — where the edit actually goes, when that is not the anchor. Omit when they are the same.
- `title` — 80 characters or fewer, naming the defect.
- `claim` — a flat, falsifiable statement of what is wrong, with the quoted code and the quoted rule. Written to be checked, not to persuade. This is what the verifier receives.
- `support` — what you ran, what you read, and what you remain unsure of. First person is fine here and nowhere else. The verifier never sees this, so do not put anything load-bearing in it.
- `trigger` — the concrete inputs, state, or environment producing the wrong behavior. Required. If you cannot write one, you do not have a candidate; if the mechanism is real but the trigger is uncertain, say so here and let the verifier route it.
- `change` — the concrete edit: file, site, what to do.
- `priority` — `P0` blocking release or major usage, holding under any input; `P1` urgent; `P2` normal; `P3` nice to have.

Keep each field tight. Whoever acts on this — a person or an agent — acts from these fields alone.
