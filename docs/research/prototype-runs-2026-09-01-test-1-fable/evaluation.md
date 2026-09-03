# Evaluating the Fable post-C9 v2a run on `kamui/shortlist#66`

**2026-09-02.** This evaluates one `code-review-deep-publish` run under
`claude-fable-5-1`. It is not an architecture tournament. Its value is narrower: it records how the
post-C9 panel behaved on the same target used for the Sonnet before/after and exposes meaningful
run/model sensitivity.

Sources: [README](README.md), [run record](v2a-run.md),
[comparison data](comparison-data.md), and the shared
[conditions/addendum](../prototype-runs-2026-09-01-test-1/addendum-2026-09-02.md).

## Conclusion

**The Fable run is strong evidence that C9's search mechanism can work, useful evidence of broader
recall, and weak evidence about architecture quality or cost.** Its Requirements finder recorded
the changed contracts first and used the closed-list-to-open-rule sweep to find the Narrow peer,
the bundle peer, the Research-skill wording, and the commerce-only validator regex. A fresh verifier
confirmed all four findings and converted the ambiguous AC4 claim into a question rather than a
blocker.

The later Sonnet post-C9 run proves the Narrow recall recovery did not require a model change: it
found the same central peer on the same configured model as the pre-C9 miss. That leaves this Fable
record with a different purpose. It found the validator regex and AC4 question that Sonnet missed,
while Sonnet made the Narrow drift blocking and Fable did not. The difference is material evidence
that one run per model/skill is not a stable estimate of recall or calibration.

The run should not be used for cost ranking. A rate limit killed an orchestrator and one finder,
the completed roles ran serially, and the reported 249,628 tokens exclude substantial wasted work.

## Method and limitations

The target identity matches the main test-1 corpus: head `4349ff41`, merge-base `ccd1842d`, nine
changed files, issue #45, and no prior review state. The clone was truncated so no later review or
commit was reachable. Every completed reviewing role used `claude-fable-5-1` at default reasoning.

Two variables prevent a clean pre/post inference from the original 2026-09-02 pair: the skill
changed from pre-C9 to post-C9 and the model changed from Sonnet to Fable. The later Sonnet rerun
removes that confound for C9. This run also remains development-set evidence because the skill was
designed after the target's earlier results were known.

The execution was interrupted. The saved prompts remained byte-identical, the clone stayed clean,
and verifier `support` withholding was checked mechanically, so the finding evidence remains usable.
The timing and token totals do not represent the intended parallel architecture.

## Finding quality

The run's four findings occupy two bands.

The central synchronization drifts are well supported:

- `search-bundle-format.md:208` omits a formal Kind that peer documents and code added;
- `shortlist-narrow/SKILL.md:46` restates a closed refresh list after the protocol made it
  ledger-driven; and
- `shortlist-research/SKILL.md:39` says only “add” after the protocol added refine and
  mark-inapplicable operations.

All are real textual inconsistencies. The first two have historical lockstep evidence and both
finders reached them. Non-blocking action is proportionate because canonical schema/protocol paths
remain correct. P3 would also have been defensible for the Research wording.

The validator regex is more consequential but less simple. It still recognizes only commerce
terms when deciding whether evidence needs an offset-bearing timestamp, so generalized claims with
bare dates can pass where price claims fail. The verifier reconstructed that asymmetry. The new
Freshness attestation is deliberately judgment-only, which makes “missing enforcement” a policy
choice rather than an automatic blocker. P2 `consider` is reasonable.

This was not the first record of that regex: v2 already published the same line and mechanism. The
independent rediscovery still strengthens confidence that the asymmetry is real.

## The AC4 question

The Requirements finder proposed that no record can carry a category-appropriate freshness
expectation. The verifier separated two claims:

- no _defined structured carrier_ exists — supported; and
- there is nowhere to record an expectation — overstated, because free-text fields exist.

It also rejected using the separate freshness checker's seven-day horizon as decisive evidence,
because that work is outside this issue. `Plausible` → question is exactly the right verdict shape.
It preserves a specification ambiguity without inventing a field or blocking on one interpretation.

This is the clearest positive result unique to the Fable run. The Sonnet post-C9 run did not raise
the matter, and the original runs split between finding, dropping, and declaring the criterion met.

## What C9 demonstrated

The changed-contract inventory did more than add prose to the prompt. Its row for the retired fixed
freshness list forced an old-fragment search across the repository. That search surfaced both the
Narrow skill and the validator regex. Both axes independently found the two originally tracked
documentation peers; the Requirements axis alone found the code-level enforcement peer.

That is concrete mechanism evidence. It also identifies a weakness: the Code axis's sync-drift
pass remained shallower than the Requirements pass. On this target the expensive duplicate finder
did not provide duplicate coverage of the most code-like drift.

## Model sensitivity

The Fable and Sonnet post-C9 runs agree that the bundle, Narrow, and Research restatements are stale.
They disagree in two ways that matter:

1. Fable found an additional validator asymmetry and raised a specification question; Sonnet
   missed both.
2. Fable rated the Narrow item `consider`; Sonnet's verifier retained `must-fix` and changed the
   status to Changes Requested.

This does not establish that Fable is the better reviewer. It is one target and one sample, with an
interrupted Fable execution. It establishes that both recall and action can move when the model/run
changes even after the skill and inputs are pinned.

## Verdict

Retain this run in the corpus. It supplies:

- an auditable example of C9 producing the intended repo-wide search;
- an independent reconstruction of the validator asymmetry;
- the target's only verifier-produced `plausible` question; and
- direct evidence that single-run absence is weak.

Do not use it to attribute the C9 fix by itself, compare cost with the Sonnet or original cohorts,
or rank Fable above Sonnet. Those claims require repeated, model-matched runs. The practical design
lesson is to keep the changed-contract inventory and question conversion, mechanically enforce the
ledger format, and verify high-consequence acquittals as well as surviving candidates.
