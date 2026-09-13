# Isolated verification and verdict accounting — issue #160

Acceptance record for [#160](https://github.com/kamui/skills/issues/160), part of
[#156](https://github.com/kamui/skills/issues/156). The pre-change rule text is pinned at
`4a0f652` (`v2b-3`); the implementation advances `code-audit-publish` to `v2b-4`.

**What this is.** Five acceptance cases from the issue. Four of them turn on mechanics — what the
scripts accept, refuse, emit, and withhold — and those are CLI fixtures with asserted exit codes in
the scripts' own test runners; this document says which fixture carries each case so the claim can
be re-run. The fifth turns on policy — what happens when no isolated worker exists — and that is an
instruction replay: the rule text traced by hand, before and after, to show which sentence withholds
the output.

**What this is not.** No reviewer was run against a pull request on either revision. The fixtures
establish that the packet and the return are shaped and accounted as specified; they say nothing
about whether an isolated verifier confirms or refutes better than an inheriting one, and the
isolation replay is not evidence that any harness actually provides `fork_turns=none` or its
equivalent — that is checked per harness at run time, and a harness that cannot provide it takes
the incomplete path below. The release claims no recall, precision, or runtime-performance gain.

## The rule change being traced

| Owner | `v2b-3` | `v2b-4` |
| --- | --- | --- |
| `SKILL.md` step 3 | "Spawn one sub-agent with a fresh context" and use the builder's output as the prompt. "If the verifier runs and returns nothing, that is a clean review, not a failure." | A genuinely non-inheriting worker, `fork_turns=none` or equivalent, or verification is incomplete and every candidate is withheld. The builder writes an accounting packet; `account_verifier_return.py` checks the return against it before any verdict is read; one shape-only repair handed the prior return to preserve; a zero-record return is a failure; an intentionally empty input — nothing to verify on any round — takes the explicit clean-review path. |
| `references/verify.md` | Verifier receives the claim, the repository, and suite results; returns per-candidate verdicts and per-row rulings in prose. | Gains § Isolation; receives `kind`, `trigger`, `impact`, `change`; returns exactly one record per supplied id in fenced `verdicts` and `rulings` blocks, with a merged candidate carrying its survivor's verdict. |
| `references/finding-format.md` § Finder candidate block | Ten fields: `id`, `axis`, `anchor`, `fix`, `title`, `claim`, `support`, `trigger`, `priority`, `action`. | Thirteen fields, adding `kind`, `impact`, `change`; axis-prefixed unique ids; ledger rows carry a per-run id and a kind. |
| Both axis briefs § Report tail | Four-field ledger row: claim, route, evidence, disposition. | Six-field row: `<axis>-<n>`, kind, claim, route, evidence, disposition. The old row is refused by count with the old grammar named. |
| `scripts/build_verifier_prompt.py` | Parses ten fields and four-field rows; withholds `support`. | Parses thirteen fields and six-field rows; refuses duplicate ids and the old shapes; writes `--packet`; accepts `--prior`. |
| `scripts/validate_finder_report.py` | Checks ledger, manifest, counts. | Also checks the candidates block through the builder's parser, and the row id and kind. |
| `scripts/account_verifier_return.py` | — | New. |

## Case 1 — two candidates and one related row return all three records

**Fixture.** `account_verifier_return.py --self-test`, case "all records present": a packet with
`code/browser-context/remove-cookies-race`, `requirements/release-notes/missing-flag`, and the
related row `code-2`; a return whose `verdicts` block carries one `confirmed` and one `refuted |
contradiction` and whose `rulings` block carries `code-2 | holds | packages/browserContext.ts:538`.

**Expected.** Exit 0, and stdout lists the three normalized records. The `holds` cites a line other
than the row's own evidence (`packages/browserContext.ts:540-544`), which the script requires.

**`v2b-3`.** No accounting existed; the orchestrator read the prose and matched verdicts to
candidates by hand.

## Case 2 — absence is never approval

Each is a fixture in the same self-test, and each exits 1 with the violation named:

| Return | Fixture | Violation |
| --- | --- | --- |
| No fenced blocks at all | "empty response" | `verdicts:0: missing verdicts block`, then one `missing verdict` per candidate id and one `missing ruling` per row id |
| `verdicts` block reading `None.` | "zero-record blocks are a failure" | `verdicts:0: empty block: zero records for a packet of 2 verdict(s); absence is not a verdict` |
| Last candidate's row omitted | "missing last id" | `verdicts:0: missing verdict: requirements/release-notes/missing-flag has no record` |
| A candidate ruled twice | "duplicate id" | `verdicts:2: duplicate verdict: … appears 2 times` |
| A verdict on an id not in the packet | "unknown id" | `verdicts:1: unexpected id: … is not a verdict the verifier was given` |
| `probably` in the verdict column | "malformed verdict" | `verdicts:1: verdict: <id>: 'probably' is not one of confirmed, plausible, refuted` |
| `refuted` with prose where a basis belongs | "refuted without a basis token" | `verdicts:2: basis: <id>: … is not one of the five refutation bases` |
| `holds` citing only the row's own evidence | "holds citing the row's own evidence" | `rulings:1: evidence: code-2: a holds ruling cites …, the row's own evidence` |

The "violations leave the other ids accounted" fixture checks the partial-use rule: with the
Requirements verdict missing, the script's closing `accounted:` line carries the confirmed Code
verdict and the related ruling, its `withheld:` line carries the missing id, and the two lines
partition the packet, so after the one repair fails the orchestrator withholds exactly the withheld
line. The "malformed confirmed basis lands in withheld" and "malformed duplicate beside a valid row
is withheld" fixtures check that a record whose id is recoverable but whose shape is not conforming
lands on the withheld line rather than passing as accounted. The empty-packet fixture
checks the other boundary: a packet with no candidates and no rows exits 2 naming the clean-review
path, because such a run never dispatched a verifier and has no return to account for.

**`v2b-3`.** The empty return was a clean review by rule text; the missing-last-id and duplicate
cases had no mechanical check and depended on the orchestrator noticing.

## Case 3 — no isolation capability (instruction replay)

**Scenario.** A harness whose sub-agent primitive always inherits the parent conversation, or one
with no sub-agent primitive at all. Two candidates exist.

**`v2b-3`.** "Spawn one sub-agent with a fresh context" was the whole instruction. The prompt
builder withholds `support`, which the text presented as the mechanism ("it withholds every
`support` field mechanically"), so an orchestrator on an inheriting harness could dispatch the
stripped prompt to a worker that had already read both finder reports, receive verdicts, and
publish them as verified. Nothing in the text refused that.

**`v2b-4`.** `SKILL.md` step 3: "Where the runtime cannot provide that isolation, do not run the
brief in this context and do not imitate independence: mandatory verification is incomplete, every
candidate is withheld, the run publishes no `confirmed` finding, and the summary and run report
state that verification could not be isolated." `verify.md` § Isolation says the same from the
worker's side. `publishing.md` § Status names the coverage line, `verification not isolated`, and
the ladder yields `Incomplete` at step 2. Questions and observations, which never pass through the
verifier, still publish; both candidates are withheld and named in the run report.

**What this shows and does not show.** The rule text now withholds the output; that is all a paper
trace can establish. Whether a given harness provides a non-inheriting worker is a runtime fact this
document does not measure, and no claim is made that isolated verification performed better on any
target.

## Case 4 — support never reaches the worker; citations and the repair do

**Fixture.** `test_build_verifier_prompt.py`, normal invocation. The Code candidate's `support`
reads "I am certain of this; I traced it twice and the finder before me clearly proved it." The test
asserts that none of "I am certain", "traced it twice", "clearly proved", or the Requirements
finder's "Searched the notes" appears in the emitted prompt, that no `support:` label survives, and
that the `claim` (with its quoted coordinate), `trigger`, `impact`, and both candidates' `change`
lines do. A second fixture ("leaked") injects an indented `support:` line into a claim and asserts
the builder refuses the prompt rather than emitting it.

**`v2b-3`.** `support` was already withheld; `impact` and `change` did not exist in the block, so
the requested repair did not reach the verifier at all.

## Case 5 — the same claim on both axes keeps two ids

**Fixture.** `test_build_verifier_prompt.py`, "twin claims": the Requirements candidate's `claim` is
replaced with the Code candidate's, byte for byte. The test asserts exit 0, two rendered candidate
sections, and a packet listing `code/browser-context/remove-cookies-race` and
`requirements/release-notes/missing-flag` as two candidates. Deduplication remains the verifier's
ruling in its merge list; the merged candidate still owes its own verdict row, carrying the
survivor's verdict (`verify.md` § What to return).

The companion refusals — a duplicate id within a report, a candidate whose id carries the other
axis's prefix, a candidate whose `axis` field contradicts its report, and a prior finding whose id
duplicates a live candidate — are fixtures in the same runner, each asserting exit 1 and the message.

## Old shapes are refused, not misread

Not an acceptance case in the issue, but the mechanism it asked for. `test_build_verifier_prompt.py`
asserts that a ten-field candidate (no `kind`, `impact`, `change`) exits 1 with "is missing kind
before anchor", and that a four-field ledger row exits 1 with "has 4 fields, expected 6 … (the
four-field row grammar has no id or kind)". `validate_finder_report.py --self-test` asserts the same
two refusals through the validator, so a finder still writing `v2b-3` reports is sent back once for
the same review in shape at step 2, before the builder runs.

## Limits

- The fixtures are hand-built to exercise one rule each and carry no distributional claim about
  real verifier returns.
- Case 3 is a trace of rule text. It does not establish that any harness provides the isolation, and
  it is not runtime performance evidence for isolated verification.
- The `holds` citation check compares normalized location strings for equality only: a ruling that
  cites a different line inside the row's own range passes it, as the rule intends, and a ruling
  that restates the row's evidence with different whitespace is caught. It does not read the code.
- Prior findings on a re-review enter the packet through `--prior`, whose grammar requires the
  orchestrator to restate each prior finding as a candidate section, including a `kind` the earlier
  trailer never carried; that restatement is a judgment this document does not test.
