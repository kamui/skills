# Isolated review experiments: recovery and stop decisions

The read audit disqualifies attempts that cross the experiment's filesystem or
network boundaries. An invalid attempt still costs money, but cannot satisfy a
quality threshold. It does not by itself show that the candidate instruction is
better or worse.

| Issue | Valid / attempted | Decision | Reviews and grading |
| --- | ---: | --- | ---: |
| [#381](2026-09-26-x381-action/README.md) | 1/3 | Reject: valid ripgrep review missed GT-n1 | $9.687408 |
| [#384](2026-09-26-x384-lifecycle/README.md) | 0/4 | Inconclusive: four invalid cells exceed two replacements | $13.027116 |
| [#385](2026-09-26-x385-remedy-completeness/README.md) | 3/5 | Reject: valid Hono review missed GT-p1 | $14.602178 |

Total spend is **$37.316702**, including invalid attempts and blind grading. No
additional review was purchased during recovery. These are partial, stopped
screens under the [frozen protocol](../../docs/research/builtin-review-benchmark-2026-09-24/README.md#13-preregistered-follow-up-isolated-a-changes-2026-09-25),
not completed matrices or evidence of a performance improvement.

## Audit repair and recovered outputs

The audit incorrectly treated an explicit local `git clone` as network access.
The correction recognizes filesystem sources with local-copy options; remote
sources, unknown options and expandable sources remain disallowed. The independent
path audit still applies. Replaying that classification over all 83 historical
baseline audits changed none. Baseline files were not rewritten.

The initial correction removed #381's false network violation. Review then found
that quoted paths could bypass filesystem checking. The repaired parser keeps
spaces and separators inside path operands and checks complete absolute paths.
Its replay also exposes previously missed `find /` scans in #381's Requests and
#384's soba attempts. Both are invalid. Eight attempts are invalid in total: seven
crossed filesystem boundaries, and #384's gRPC attempt ran `go version` without
offline toolchain settings. That command can select and fetch a toolchain, so it
remains prohibited under the frozen execution rules.

Three completed CLI outputs lacked wrapper finalization after their terminal jobs
ended. Their native results, frozen skill trees and usage traces were recovered;
two are invalid and #385's final soba review is valid. Missing elapsed-to-payload
events remain missing. CLI durations are preserved separately and are not inserted
into that metric. Recovery grading completed in detached tmux sessions.

The [initial audit ledger](2026-09-27-audit-recovery.json) and
[complete-path replay](2026-09-27-quoted-path-audit.json) record both stages and
their disposition changes. Each run keeps original filed records in
`audit-revisions/before-local-clone-fix/`, recovered-output details in
`attempts/*/recovery.json`, and blind mappings and scorecards in `scoring/`.
The two later invalidations preserve the intervening records under
`audit-revisions/before-quoted-path-fix/`. Current scores are v2 for #381/#384 and
v1 for #385; all reproduce from their saved inputs apart from the computation
timestamp. Earlier scores remain preserved. Raw transcripts stay outside the
repository.

## Closure work

The #381 and #385 misses prevent full recall retention even if every remaining
planned replicate succeeds. Their added action and completeness sentences are
removed, with the former design entries retained in history. The shared runtime
limit stays at 74,000 bytes because retained instructions still occupy 73,341 bytes.

#384 stays open: at most seven valid cells fit within its eleven-attempt cap after
four invalid cells, short of the nine required. No cap is extended. A future run
needs a fresh preregistration and spending decision after fixing execution within
the allowed roots and offline environment. These runs do not complete #380's
combined and unseen-target adoption gate.
