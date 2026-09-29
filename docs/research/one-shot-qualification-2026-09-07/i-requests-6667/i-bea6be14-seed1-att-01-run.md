# Research report — target (i) psf/requests#6667, cell i-bea6be14-seed1, attempt att-01

Written incrementally per the dispatch's "persist before you verify" rule: this file is updated in
stages as each phase of the skill completes, before any verifier is dispatched, and again as each
verifier report arrives.

## 1. Metadata

- **Target:** `psf/requests#6667` — "Avoid reloading root certificates to improve concurrent performance"
- **Cell / attempt:** `i-bea6be14-seed1` / `att-01`
- **Skill snapshot:** `/tmp/qual137/snapshots/bea6be14/snapshot-path-omitted/`
- **`workflow` identifier** (from `scripts/validate_review.py`'s `WORKFLOW` constant): `v5b-10`
- **Model:** this reviewer ran on `claude-sonnet-5` (Sonnet 5) throughout, in this same context, per the
  dispatch's binding instruction that the reviewer itself is never delegated. Every sub-agent dispatched
  (the one verifier batch, §7 below) was launched via the `Agent` tool with `subagent_type:
  "general-purpose"`, `model: "sonnet"` (Sonnet 5), `run_in_background: false`, exactly as required.
- **Verification trigger fired:** yes. SKILL.md step 3: *"Independently verify every surviving candidate
  proposed as `must-fix`, plus every candidate involving security or authorization, data loss or
  corruption, destructive migration, or an externally observable compatibility break."* Both survivors
  (CAND-01, CAND-02) are proposed `must-fix`; CAND-02 is additionally a security candidate and CAND-01 is
  additionally an externally observable compatibility break (a previously-succeeding `import requests`
  now raises). One initial candidate batch was dispatched (no zero-survivor and no follow-up batch was
  needed — see §7 Mechanism checklist).
- **Sub-agents spawned:** 1 — role: independent verifier (candidate + related-acquittal mode, one
  combined batch), `subagent_type: "general-purpose"`, model `sonnet`. No clean-verdict batch was needed
  (survivors existed) and no follow-up batch was needed (see §7).
- **Candidates raised:** 5 (CAND-01 through CAND-05, plus one hygiene fact routed as an observation,
  CAND-06, which was never a candidate under the finding gates).
- **Candidates surviving primary falsification:** 2 (CAND-01, CAND-02), both `must-fix`, both
  independently confirmed by the verifier.
- **Verifier verdicts:** CAND-01 `confirmed` (correction: none), CAND-02 `confirmed` (correction: none,
  concurrency bug-class widening applied — see §7); related-acquittal rulings: CAND-03 `holds`, CAND-04
  `holds`, CAND-05 `holds`.
- **Findings for publication:** 2, both `[P1] [must-fix]`.
- **Questions:** 0.
- **Observations:** 1 (test-coverage hygiene fact; below the 3-item cap).
- **Coverage:** complete — the entire (and only) changed file, `src/requests/adapters.py`, was read in
  full via the diff's function-context output (single chunk, `consumed`, `diff coverage: complete`); the
  targeted risk checks below are all evidence-backed; no packet gap, no failed fetch (this is a
  packet-only offline run so there was nothing further to fetch), no unresolved evidence-affecting tool
  failure.
- **Derived status:** `Changes Requested (advisory)` — two unsettled `must-fix` findings; event
  `COMMENT` (publication disabled; retrospective mode; `kamui` never had gating authorization in any
  case).
- **Token usage:** the harness surfaced to me does not report a running token-usage counter to the
  assistant in this environment, so I cannot state my own consumption; noting that per the report
  instructions rather than fabricating a number.

## 2. Pinned run identity (from the packet, used verbatim, not re-resolved)

| | |
| --- | --- |
| Repository | `psf/requests`, `summary.repository_url = https://github.com/psf/requests` |
| PR | #6667, author `agubelu` |
| Head SHA | `4089f3dc65f783beaa53cc032958ab625440d0ac` |
| Base ref | `main` |
| Base SHA / merge-base | `8dd3b26bf59808de24fd654699f592abf6de581e` (identical; confirmed locally with
  `git merge-base main review-head` — see §8) |
| `state` / `merged` | `MERGED` / `true` (merged 2024-05-15T20:07:26Z) |
| Originating issue(s) | none (`issues=none`); ledger built from PR title+body alone |
| Posting identity | `kamui`, third party, no prior comments/reviews → first review, not a re-review;
  `references/re-review.md` was not read (SKILL.md step 1: that reference loads only "when step 1 finds
  prior state from the posting identity", which it did not) |
| Mode | Retrospective review of a merged pull request; publication disabled (this run's binding
  condition #4, consistent with the Boundaries section of SKILL.md) |

## 3. Manifest

```
M src/requests/adapters.py +28 -18 new=no lines=616
```

One file changed. Built via `python3 scripts/review_context.py --merge-base 8dd3b26bf59808de24fd654699f592abf6de581e --head 4089f3dc65f783beaa53cc032958ab625440d0ac --store <private-store>` (exit 0), read once. The private store lives at
`/var/folders/tj/sr3wvlgs0v9608r9tjwmtnk40000gn/T/tmp.iey3sI62rH/review-context-4089f3dc65f783beaa53cc032958ab625440d0ac.json`,
created via `mktemp -d` outside the working tree, as the skill requires. The build call's own diff output
was already complete (one chunk, `consumed`, `diff coverage: complete (1/1 chunks consumed)`), so no
`--from` re-read was ever needed and the diff was never rebuilt or re-read per file.

`ranges` from the same call (the enclosing symbols the diff's function-context already printed, so none
needed a separate bounded read):

```
src/requests/adapters.py:26-32 @head / :26-31 @merge-base   (import block)
src/requests/adapters.py:72-115 @head / :71-104 @merge-base (module-level context + _urllib3_request_context)
src/requests/adapters.py:148-616 @head / :137-606 @merge-base (HTTPAdapter class, including cert_verify)
```

`history` (pre-merge-base history of the file, printed by the same call, read but not needed to decide
any candidate — the merge-base vs. head diff was sufficient for every gate-2 determination):

```
src/requests/adapters.py: a94e9b53 2024-03-13 Add local TLS server
src/requests/adapters.py: c0813a2d 2024-03-03 Use TLS settings in selecting connection pool
src/requests/adapters.py: 60389df6 2024-02-21 Trim excess leading path separators
```

Coverage: `src/requests/adapters.py` is `reviewed` in full (every hunk plus its full enclosing-function
context, i.e. essentially the entire 616-line file was inspected as printed by the store build). No other
file changed. Coverage is **complete**.

## 4. Issue fit ledger

No originating issue (`issues=none`); the ledger is built from the PR title and body alone, per SKILL.md
step 1 and the rubric's Issue fit section.

| # | Source coordinate | Class | Row | Disposition | Evidence |
| - | - | - | - | - | - |
| R1 | `pr-title` | acceptance requirement | "Avoid reloading root certificates" — eliminate the redundant per-request `load_verify_locations()` call urllib3 triggers when a connection's `ca_certs`/`ca_cert_dir` are set, for the common `verify=True` case | **met** | `src/requests/adapters.py:94-95` (`_urllib3_request_context` hands a pre-loaded `ssl_context` for `verify is True`) and `:304` (`cert_verify` no longer sets `ca_certs`/`ca_cert_dir` when `verify is True`) |
| R2 | `pr-body/"there is no need to trigger a call to load_verify_locations() again"` | acceptance requirement (restates R1) | same outcome as R1 | **met** | same evidence as R1 |
| R3 | `pr-body/"verify=True and verify=False still behave as expected"` | acceptance requirement | server-certificate verification semantics (`CERT_REQUIRED` vs. `CERT_NONE`) must be unchanged | **met** | `adapters.py:91-101` sets `cert_reqs` correctly on both branches; `adapters.py:297,318-321` mirrors it in `cert_verify` |
| R4 | `pr-body/"It isn't possible to skip loading root CA certificates entirely"` | explicit non-goal | the change does not attempt to eliminate the default-bundle load entirely | **met** (non-goal honored — trivially, since the change still loads the bundle once) | `adapters.py:75-78` |
| — | `pr-body/"~1.2s ... ~0.5s"` benchmark numbers | supporting assertion (not an acceptance requirement) | author's local timing measurement | not a ledger row (supporting assertion, uncontradicted); no network access to reproduce against `badssl.com` as the PR body suggests, and no reproduction is required since it is not an acceptance criterion | — |

Row R3's "met" disposition is about the *stated* acceptance criterion (server-certificate verification
outcome for the current request). It does **not** cover an unstated side effect — the shared context
persisting a *client* certificate across unrelated future requests — which the PR text never discusses in
any form; that is a separate defect (CAND-02 below), not a contradiction of R3, and is judged purely
under the ordinary gates, not the Issue-fit ledger.

No versioned-artifact conformance applies (`references/conformance.md` was not read — no issue, PR text,
or repository convention names a tracked stub/binding/schema/generated-source artifact this change must
conform to).

No explicit deferral of a *design, naming, or API-shape* decision remains open in the review record: the
one design deferral present (renaming the shared context to be "private by convention", non-review
conversation comment 9 in the packet) was explicitly resolved by commit 3 (`f21e70bf7`, "Rename default
SSLContext to make it private by convention"), which is already part of the reviewed head. The author's
closing-paragraph remark ("I'm not sure that setting `conn.ca_certs`... is even still needed... the logic
could be moved to `_urllib3_request_context()`") is an author musing about a possible future refactor, not
a design/naming/API-shape deferral in the SKILL.md step-1 sense (it does not concern what the surface
should look like), and no candidate in this run treats it as an open acceptance question.

## 5. Repository guidance (packet §7, verified applicable at merge-base)

No root or path-scoped `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` exists at the merge-base (packet table, all
"no"). No repository-rule findings are possible; none were raised.

## 6. Complete private candidate ledger

Every candidate raised during falsification, in the order considered. `disposition` is my own primary
judgment before verification; `survivor` rows also carry the verifier's independent verdict once returned
(§7). Kind, evidence and falsification are as specified in the rubric's Private finding record.

### CAND-01 — survivor, `must-fix`

```yaml
id: adapters/import-time-cert-load-crash
anchor: {type: line, path: src/requests/adapters.py, start_line: 75, end_line: 78, side: RIGHT}
priority: P1
action: must-fix
blocking: true
kind: bug
title: Don't load the default CA bundle unconditionally at import time
claim: >
  src/requests/adapters.py now calls create_urllib3_context() and
  _preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))
  unconditionally at module import time, with no exception handling, whereas at the merge-base
  load_verify_locations() for the default bundle was only ever invoked lazily inside cert_verify(),
  guarded, when an actual verify=True HTTPS request was sent.
trigger: >
  The default certifi bundle path returned by DEFAULT_CA_BUNDLE_PATH is unreadable or missing at
  process start (corrupted/incompatible certifi install, a broken shim, a frozen/zipped distribution
  whose bundle failed to extract, or a sandboxed filesystem) in a process that never intends to use the
  default trust store (always verify=False, or always a custom CA bundle/dir).
impact: >
  The bare `import requests` statement raises an uncaught FileNotFoundError/SSLError before any
  application code runs, crashing every program that imports requests — including ones that would never
  have hit the failure at the merge-base, because they never send a verify=True request against the
  default trust store.
evidence:
  - src/requests/adapters.py:75-78 (new, unconditional, unguarded module-level load)
  - src/requests/adapters.py:297-312 (merge-base-equivalent guarded, lazy call site, still present for
    the non-default-bundle string case, proving the guard/laziness pattern was the established norm)
support:
  inspected:
    - base-branch cert_verify() at git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py
    - urllib3 2.7.0 ssl_wrap_socket()/connection.py to rule out any implicit exception handling downstream
  checks:
    - reproduced empirically both ways (below); base import survives, head import crashes
  uncertainty: none
change: >
  In src/requests/adapters.py, don't call load_verify_locations() unconditionally at import time; either
  build _preloaded_ssl_context lazily on first verify=True use, or wrap the module-level call so a load
  failure is deferred/reported the same way cert_verify() already reports it (a clear OSError naming the
  invalid path), instead of aborting import.
verification: independent-confirmed
disposition: survivor
falsification: >
  No unchanged guard prevents this: the module-level call sits at top level with no try/except, runs
  before any HTTPAdapter is even constructed, and the failure mode was reproduced directly (see below).
```

**Reproduction (offline, via the permitted focused-pytest execution allowance):**

- `PYTHONPATH=/tmp/qual137/runs/i-bea6be14-seed1-att-01/src /tmp/qual137/venvs/requests/bin/python -m pytest /tmp/qual137/work/i-bea6be14-seed1-att-01/repro_import_time_crash_test.py -v -s`
  — exit 0 (test passed, i.e. the crash was reproduced as asserted), duration 0.14s. The test shadows
  `certifi` with a fake module returning a nonexistent bundle path and spawns a subprocess
  (`sys.executable -c "import requests"`) against the reviewed head's `src/`; the subprocess's traceback,
  captured verbatim, shows the failure originating exactly at the new module-level line:
  ```
  File ".../src/requests/adapters.py", line 76, in <module>
      _preloaded_ssl_context.load_verify_locations(
  FileNotFoundError: [Errno 2] No such file or directory
  ```
- `PYTHONPATH=/tmp/qual137/runs/i-bea6be14-seed1-att-01/src /tmp/qual137/venvs/requests/bin/python -m pytest /tmp/qual137/work/i-bea6be14-seed1-att-01/repro_base_import_ok_test.py -v -s`
  — exit 0 (test passed), duration 0.15s. Same fake-`certifi` condition against a read-only extraction of
  the merge-base tree (`git archive 8dd3b26bf59808de24fd654699f592abf6de581e -- src/requests`, extracted
  under my own work directory, no clone mutation): `import requests` succeeds and prints `IMPORT_OK`.

This pair of runs is the gate-2 "introduced here" guarantee test the rubric's Falsify section requires:
the base-branch guarantee ("import requests never touches the TLS trust store") is cited by direct
reproduction, and the head-branch code that no longer provides it is cited by direct reproduction and
traceback line number.

### CAND-02 — survivor, `must-fix`

```yaml
id: adapters/shared-ssl-context-cert-chain-leak
anchor: {type: line, path: src/requests/adapters.py, start_line: 94, end_line: 95, side: RIGHT}
priority: P1
action: must-fix
blocking: true
kind: concurrency
title: Don't hand the shared module-level SSLContext to a connection that also supplies a client certificate
claim: >
  _urllib3_request_context() (src/requests/adapters.py:94-95) hands the single, process-wide, module-level
  _preloaded_ssl_context object to urllib3 as pool_kwargs["ssl_context"] for every verify=True request,
  unconditionally, even when the same call also supplies a client certificate via pool_kwargs["cert_file"]/
  ["key_file"] (adapters.py:102-109, fed from HTTPAdapter.cert_verify()'s cert handling at :323-329).
  urllib3's ssl_.ssl_wrap_socket() then calls context.load_cert_chain(certfile, keyfile) on that exact
  shared object whenever certfile is truthy (confirmed by reading the installed urllib3 2.7.0 source,
  urllib3/util/ssl_.py).
trigger: >
  Any single verify=True request anywhere in the process supplies a client certificate via the
  documented `cert=` parameter (Session.request(..., cert=(...)) or HTTPAdapter.send(..., cert=(...))).
impact: >
  Because ssl.SSLContext exposes no API to unload a previously loaded certificate chain, and because
  _preloaded_ssl_context is a single literal object shared by every HTTPAdapter/connection pool in the
  process for the remainder of its life, every subsequent verify=True connection to ANY host — including
  hosts and threads that never requested a client certificate — will present that first request's client
  certificate for as long as the process runs. This is a client-credential/identity leak to unrelated
  servers, and it is exactly the "mTLS certs" hazard the PR's own review record raised and never actually
  closed: Christian Heimes (`tiran`), an OpenSSL/CPython core maintainer, wrote in this PR's own
  conversation (packet §6, non-review comment 5): "It is thread safe as long as you don't reconfigure it
  once it is used by a connection. Adding new certs to the internal trust store is fine, but changing
  ciphers, verification settings, or mTLS certs can lead to surprising behavior. The problem is unrelated
  to threads and can even occur in a single-threaded program." The merged PR's only response to that
  thread was to rename the context with a leading underscore ("private by convention", commit 3) — a
  naming change that does nothing to stop requests' own code from feeding a client certificate into that
  same shared object via the ordinary, unchanged `cert=` code path.
evidence:
  - src/requests/adapters.py:94-95 (unconditional shared-context assignment for verify=True)
  - src/requests/adapters.py:102-109 (client_cert handling in the same function, no interaction with the
    ssl_context branch above)
  - src/requests/adapters.py:323-329 (cert_verify sets conn.cert_file/key_file unconditionally, regardless
    of verify)
  - urllib3/util/ssl_.py ssl_wrap_socket(): `if certfile: context.load_cert_chain(certfile, keyfile)`
    against the exact context object handed in as ssl_context (installed venv, urllib3 2.7.0; the call
    shape predates 2.7.0 and is not new to that version)
support:
  inspected:
    - urllib3 2.7.0 connection.py (_ssl_wrap_socket_and_match_hostname, HTTPSConnection.connect) to
      confirm self.cert_file/self.ssl_context both flow into the same ssl_wrap_socket() call
    - sessions.py merge_environment_settings (verify env-var override) to rule out that path as a
      confound — it correctly bypasses the shared-context branch when REQUESTS_CA_BUNDLE/CURL_CA_BUNDLE
      is set, so is not itself a source of the leak
  checks:
    - reproduced empirically (below): the shared object identity persists across unrelated requests, and
      a directly-loaded cert chain on that object is visible to a later, unrelated call
  uncertainty: >
    the broader "does concurrent identical-value mutation of context.verify_mode / set_alpn_protocols
    from multiple threads ever itself cause an observable failure" question was traced but not proven
    within available offline legwork (see CAND-05-adjacent note below); the claim here rests only on the
    concretely reproduced, deterministic, sequential client-certificate persistence, which requires no
    race to manifest.
change: >
  In _urllib3_request_context (src/requests/adapters.py), don't reuse the shared _preloaded_ssl_context
  when client_cert is not None; build (and if warranted, cache per client-cert pair) a private SSLContext
  for that combination instead, so a client certificate never persists onto the object handed to
  unrelated connections.
verification: independent-confirmed
disposition: survivor
falsification: >
  No unchanged guard prevents this: _urllib3_request_context's elif chain assigns ssl_context based only
  on `verify`, never checks client_cert; cert_verify() sets conn.cert_file/key_file unconditionally
  whenever `cert` is truthy, independent of `verify`. Reproduced directly (below).
```

**Reproduction (offline, via the permitted focused-pytest execution allowance):**

- `PYTHONPATH=/tmp/qual137/runs/i-bea6be14-seed1-att-01/src /tmp/qual137/venvs/requests/bin/python -m pytest /tmp/qual137/work/i-bea6be14-seed1-att-01/repro_shared_context_test.py -v`
  — exit 0, both tests passed, duration 0.13s.
  `test_shared_context_is_singleton_regardless_of_client_cert` proves `_urllib3_request_context()` returns
  the literal same `_preloaded_ssl_context` object whether or not `client_cert` is supplied.
  `test_client_cert_loaded_into_shared_context_leaks_to_future_requests` uses the repository's own mTLS
  test fixture (`tests/certs/mtls/client/client.{pem,key}`), performs the exact mutation urllib3 performs
  (`context.load_cert_chain(...)`) on the object requests handed it for one request, then shows a second,
  unrelated request to a different host with no client cert of its own receives back the identical,
  now-cert-loaded context object.

No network access was used or needed for either test; both operate purely on the Python objects requests
and the standard `ssl` module expose, without opening a socket.

### CAND-03 — dropped (related to survivors CAND-01/CAND-02)

```yaml
id: adapters/http-scheme-unaware-pool-kwargs
kind: bug
claim: >
  _urllib3_request_context() builds ssl_context/cert_reqs/ca_certs pool_kwargs without checking whether
  the request's scheme is actually "https", so a plain-HTTP request with verify=True still gets an
  ssl_context (etc.) entry in pool_kwargs passed to a plain HTTPConnectionPool.
disposition: dropped (pre-existing; no consequence)
falsification: >
  Pre-existing at gate 2: the merge-base version had the identical scheme-unawareness for
  pool_kwargs["ca_certs"] (git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py).
  Also empirically harmless: PoolManager.connection_from_host() with scheme="http" and pool_kwargs
  containing ssl_context/cert_reqs returns a normal HTTPConnectionPool with no exception (verified via a
  small in-process call against the installed urllib3 2.7.0; not a network call).
evidence: src/requests/adapters.py:91-101
```

### CAND-04 — dropped (related to survivors CAND-01/CAND-02)

```yaml
id: adapters/ca-cert-dir-branch-in-request-context
kind: bug
claim: >
  _urllib3_request_context() now distinguishes os.path.isdir(verify) to choose ca_certs vs. ca_cert_dir,
  a behavior the merge-base version of this function did not have (it always set ca_certs for any string
  verify value).
disposition: dropped (established intentional, gate 6)
falsification: >
  The author's own review-thread comment (packet §6, thread comment 2, on commit ec0e33b33) explicitly
  announces this exact change as deliberate and as bringing _urllib3_request_context() into line with
  cert_verify()'s pre-existing isdir handling ("I also changed _urllib3_request_context() slightly to
  handle the case where verify is a path to a dir instead of a single file... I believe this is now fully
  redundant with the corresponding logic in cert_verify()."). Gate 6 fails: established intentional by the
  review record.
evidence: src/requests/adapters.py:96-100
```

### CAND-05 — dropped (related to survivors CAND-01/CAND-02)

```yaml
id: adapters/pooled-connection-stale-cert-attrs
kind: bug
claim: >
  When verify=True, cert_verify() no longer sets conn.ca_certs/conn.ca_cert_dir at all (it only sets
  conn.cert_reqs); if the same pooled connection object were later reused for a different verify value,
  it might retain stale ca_certs/ca_cert_dir from an earlier use.
disposition: dropped (pre-existing pool/connection semantics; consequence unproven)
falsification: >
  cert_verify() runs on every send() before urlopen() and always sets the attribute that governs the
  branch actually taken (cert_reqs, and ca_certs/ca_cert_dir when verify is not True); this reuse pattern
  and urllib3's own pool-keying (which pool/connection object services a given request) are unchanged by
  this diff and pre-date it. Available static legwork (reading _get_connection, cert_verify, and urllib3's
  connection pool key computation) did not establish a concrete broken trigger distinguishing head from
  merge-base behavior; pursuing this further would require reconstructing urllib3's internal pool-key
  computation across versions, disproportionate to a candidate with no established consequence. Routed as
  dropped (consequence unproven) rather than as an observation, since it never reached a stable fact to
  observe.
evidence: src/requests/adapters.py:297-321
```

### Considered, never raised as a candidate

- **Concurrent identical-value mutation of the shared context** (`context.verify_mode = ...` and
  `context.set_alpn_protocols(...)`, both called by urllib3's `ssl_wrap_socket()`/
  `_ssl_wrap_socket_and_match_hostname()` on *every* verify=True connection, always with the same value,
  from potentially many threads at once): traced through `urllib3/connection.py` and
  `urllib3/util/ssl_.py`, but no concrete, provable observable-impact reproduction could be constructed
  offline (unlike CAND-02's client-certificate case, which is deterministic and reproducible without any
  race). Not raised as a separate candidate; recorded here rather than silently dropped, per the rubric's
  falsify-and-drop discipline, and folded into CAND-02's `uncertainty` field as the aggravating mechanism
  that motivated verifying CAND-02 at `kind=concurrency` depth rather than `kind=security` depth alone.
- **`Session.merge_environment_settings()` interaction** (`REQUESTS_CA_BUNDLE`/`CURL_CA_BUNDLE` env vars):
  read `src/requests/sessions.py:750-779` as a targeted risk-led-discovery read (risk: "external contracts
  ... version skew" / "secrets, cryptography"); confirmed the env-var override still turns `verify=True`
  into a string *before* `_urllib3_request_context()` ever sees it, so the shared-context fast path is
  correctly bypassed whenever an env var is set. No candidate raised; recorded as a risk-led-discovery
  read, not a ledger row, per the rubric's Complete inspection section.

### CAND-06 — observation (never a candidate under the finding gates)

Not a falsifiable defect claim; routed directly to the Observations channel because it fails admission on
"meaningful/proven consequence" alone (a hygiene fact, not a proven defect) — see §9 for the published
text.

## 7. Sub-agent dispatch — independent verifier (1 of 1, foreground, model `sonnet`)

Dispatched via the `Agent` tool with `subagent_type: "general-purpose"`, `model: "sonnet"`,
`run_in_background: false`, exactly one combined batch carrying both survivors (CAND-01, CAND-02,
candidate mode) plus the three related non-survivor rows (CAND-03/04/05, related-acquittal mode), per
SKILL.md step 3's related-acquittal rule ("include in that same batch every non-survivor ledger row that
is related to a survivor" — here every dropped `kind=bug` row in the single changed file qualifies under
clause (a), same file as a survivor's anchor/fix). This is the run's **only** batch: no zero-survivor
clean-verdict batch was needed (there were survivors), and no follow-up batch was needed (the verifier
confirmed both candidates with no correction that changed a mandatory claim, and held all three related
rows — nothing newly render-eligible or newly related arose after dispatch). Dispatched **after** the
complete primary falsification pass finished (not early): the diff touches a security/cryptography
surface (shared TLS context, client-certificate handling), which SKILL.md step 3 explicitly names as a
reason **not** to dispatch early ("do not dispatch early when the diff touches ... a security or
authorization boundary — on those surfaces, dispatch after the complete pass"). The complete diff had
already been read once (§3), the manifest was finished, every mandatory-verification candidate (both
survivors) had completed primary falsification, and the three related rows had already reached their
final primary disposition, all before the dispatch below.

### 7.1 Exact prompt given

<details>
<summary>Full verifier prompt (click to expand — reproduced verbatim as sent)</summary>

You are an INDEPENDENT VERIFIER for a code review. You are not a second reviewer: you do not search for new findings. You fact-check the supplied candidate records against the actual repository. Follow exactly the procedure in the two reference files quoted in full below (`verifier.md` and `verifier-concurrency.md` from the `legacy reviewer` skill). Do not consult any other review skill or methodology.

## Binding rules for this dispatch (apply to you, the verifier, exactly as given)

1. This is a retrospective, offline review of a merged, real pull request (`psf/requests#6667`). No network access exists or is permitted: no `git fetch`/`pull`, no `gh`, no `curl`, no web fetch of any kind. You do not need any of these — everything you need is below or in the local clone.
2. **Clone hygiene:** the repository clone is at `/tmp/qual137/runs/i-bea6be14-seed1-att-01`. Do NOT run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the working tree or history. Read-only git commands (`git show`, `git log`, `git diff`, `git archive`, `git merge-base`) are fine. If you ever discover the tree was mutated, run `git -C /tmp/qual137/runs/i-bea6be14-seed1-att-01 reset --hard review-head` and say so prominently in your report.
3. **Execution allowance:** focused test execution IS permitted, offline: run pytest from the clone root using the pre-provisioned virtualenv, as `PYTHONPATH=/tmp/qual137/runs/i-bea6be14-seed1-att-01/src /tmp/qual137/venvs/requests/bin/python -m pytest <selection>`. Five minutes per command max. A given selection (file + flags) at most once. Any new scratch file you create must live under `/tmp/qual137/work/i-bea6be14-seed1-att-01/` (you may also read, and re-run via pytest, the existing scratch repro files already there — do not modify them). Never add or change anything inside the clone itself. No production service, no credentials, no destructive external effect.
4. **Sandbox:** you may read/execute only within: the clone (`/tmp/qual137/runs/i-bea6be14-seed1-att-01`), the skill snapshot (`/tmp/qual137/snapshots/bea6be14/snapshot-path-omitted/`), and the work directory (`/tmp/qual137/work/i-bea6be14-seed1-att-01/`). Do not read any other path (no other run's clone, report, or payload). If you accidentally read anything outside this list, disclose it plainly in your report.
5. This is a one-shot dispatch. Do not ask anyone anything. If some input is genuinely missing, say so explicitly in your report as an incomplete/unresolved item rather than guessing.
6. You never write to, edit, or publish anything about the pull request. You produce only the structured verdicts this task asks for, returned as your final report text.
7. Do not inherit or infer the primary reviewer's reasoning beyond what is explicitly given to you below — decide independently from the cited code and evidence.

## Pinned coordinates

- Repository: `psf/requests`, cloned at `/tmp/qual137/runs/i-bea6be14-seed1-att-01`.
- Head SHA: `4089f3dc65f783beaa53cc032958ab625440d0ac` (checked out on local branch `review-head`).
- Base ref: `main`; merge-base / base SHA: `8dd3b26bf59808de24fd654699f592abf6de581e` (local branch `main` is pinned there).
- Diff: 1 file, `src/requests/adapters.py`, +28/-18.
- No originating issue (`issues=none`); no candidate below cites a `pr-title`/`pr-body` requirement coordinate, so the formal Issue-fit ledger is not part of your task. However, two candidates' `claim`/`impact` text references specific statements made in the PR's own review conversation as evidence about author/maintainer intent (gate 6, "unintentional"); the exact verbatim excerpts you need for that check are quoted below so you do not need any issue tracker access.
- `urllib3` installed in the venv: version 2.7.0, at `/private/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3` (also importable from the venv's Python — this is the version to read/execute against; the PR's `pyproject.toml` constraint is `urllib3>=1.21.1,<3`, so 2.7.0 is a valid in-range version).

## `ranges` from the review-context tool (for your one-message read of the diff regions)

```
src/requests/adapters.py:26-32 @head / :26-31 @merge-base   (import block)
src/requests/adapters.py:72-115 @head / :71-104 @merge-base (module-level context + _urllib3_request_context)
src/requests/adapters.py:148-616 @head / :137-606 @merge-base (HTTPAdapter class, including cert_verify)
```

Read these at head directly from the file (`src/requests/adapters.py`) and at merge-base via
`git -C /tmp/qual137/runs/i-bea6be14-seed1-att-01 show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py`.

## Verbatim PR review-conversation excerpts (for the gate-6 "unintentional" check on CAND-02)

From the PR's review thread (on commit `ec0e33b33`, later superseded by the reviewed head):

> **sigmavirus24:** This is actually critical behavior you're removing
>
> **agubelu:** Thanks for the catch, I had to adapt the patch quite a bit from what we're using right now and that inconsistency slipped by. I pushed a change to explicitly use `DEFAULT_CA_BUNDLE_PATH` when `verify=True`. This is done by creating a module-level `SSLContext` with that bundle already loaded, and instructing the connection pool to use that context when no custom bundle is specified. [...] I also changed `_urllib3_request_context()` slightly to handle the case where `verify` is a path to a dir instead to a single file, as we should set `ca_cert_dir` instead of `ca_certs` in that case.

From the PR's non-review conversation, on the thread-safety of the shared `SSLContext`:

> **sigmavirus24:** Even still, I'm pretty sure SSLContext is not itself thread safe but I need to find a reference for that so loading it at the module will likely cause issues
>
> **tiran** (Christian Heimes, CPython core / OpenSSL contributor): `SSLContext` is designed to be shared and used for multiple connections. It is thread safe as long as you don't reconfigure it once it is used by a connection. Adding new certs to the internal trust store is fine, but changing ciphers, verification settings, or mTLS certs can lead to surprising behavior. The problem is unrelated to threads and can even occur in a single-threaded program.
>
> **sigmavirus24:** Ah, I see that the PR was updated and moved the extraction. I think the last blocker is the context being "public" in how it is named. [...] Either way, if we rename the default I'm in favor of merging this.
>
> **agubelu:** Thanks for the follow-up @sigmavirus24. I renamed the default context as requested, please let me know if you'd like any further changes.

Commit 3 on the reviewed head (`f21e70bf7`, "Rename default SSLContext to make it private by convention")
is exactly and only that renaming (module-level `ssl_context` → `_preloaded_ssl_context`, a leading
underscore). No commit changes how the shared context interacts with a client certificate (`cert=`
parameter), and no participant in the review conversation discusses that interaction.

---

## Candidates to verify (candidate mode)

### Candidate CAND-01

```yaml
id: adapters/import-time-cert-load-crash
anchor: {type: line, path: src/requests/adapters.py, start_line: 75, end_line: 78, side: RIGHT}
fix: (same location)
priority: P1
action: must-fix
blocking: true
kind: bug
title: Don't load the default CA bundle unconditionally at import time
claim: >
  src/requests/adapters.py now calls create_urllib3_context() and
  _preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))
  unconditionally at module import time, with no exception handling, whereas at the merge-base
  load_verify_locations() for the default bundle was only ever invoked lazily inside cert_verify(),
  guarded, when an actual verify=True HTTPS request was sent.
trigger: >
  The default certifi bundle path returned by DEFAULT_CA_BUNDLE_PATH is unreadable or missing at
  process start (corrupted/incompatible certifi install, a broken shim, a frozen/zipped distribution
  whose bundle failed to extract, or a sandboxed filesystem) in a process that never intends to use the
  default trust store (always verify=False, or always a custom CA bundle/dir).
impact: >
  The bare `import requests` statement raises an uncaught FileNotFoundError/SSLError before any
  application code runs, crashing every program that imports requests — including ones that would never
  have hit the failure at the merge-base, because they never send a verify=True request against the
  default trust store.
change: >
  In src/requests/adapters.py, don't call load_verify_locations() unconditionally at import time; either
  build _preloaded_ssl_context lazily on first verify=True use, or wrap the module-level call so a load
  failure is deferred/reported the same way cert_verify() already reports it (a clear OSError naming the
  invalid path), instead of aborting import.
raw code citations:
  - src/requests/adapters.py:75-78 (head, unconditional unguarded module-level load)
  - src/requests/adapters.py:297-312 (head, the surviving guarded/lazy call site for the non-default-bundle
    string case)
```

Recorded focused-check evidence from the primary reviewer (a citation, not an interpretation — please
independently re-run both, or construct your own equivalent probe, rather than only trusting this):

- Command: `PYTHONPATH=/tmp/qual137/runs/i-bea6be14-seed1-att-01/src /tmp/qual137/venvs/requests/bin/python -m pytest /tmp/qual137/work/i-bea6be14-seed1-att-01/repro_import_time_crash_test.py -v -s`
  Head: `4089f3dc65f783beaa53cc032958ab625440d0ac`. Exit status: 0 (both the test and the outcome it
  asserts — an import crash — passed). Decisive output line: `FileNotFoundError: [Errno 2] No such file or
  directory` raised from `src/requests/adapters.py`, line 76, inside `<module>`, with no HTTPS request
  ever attempted.
- Command: `PYTHONPATH=/tmp/qual137/runs/i-bea6be14-seed1-att-01/src /tmp/qual137/venvs/requests/bin/python -m pytest /tmp/qual137/work/i-bea6be14-seed1-att-01/repro_base_import_ok_test.py -v -s`
  Head: merge-base tree extracted read-only via `git archive 8dd3b26bf59808de24fd654699f592abf6de581e` into
  `/tmp/qual137/work/i-bea6be14-seed1-att-01/base_src/`. Exit status: 0. Decisive output: `import requests`
  succeeds and prints `IMPORT_OK` under the identical broken-bundle condition.

### Candidate CAND-02

```yaml
id: adapters/shared-ssl-context-cert-chain-leak
anchor: {type: line, path: src/requests/adapters.py, start_line: 94, end_line: 95, side: RIGHT}
fix: (same location)
priority: P1
action: must-fix
blocking: true
kind: concurrency
title: Don't hand the shared module-level SSLContext to a connection that also supplies a client certificate
claim: >
  _urllib3_request_context() (src/requests/adapters.py:94-95) hands the single, process-wide, module-level
  _preloaded_ssl_context object to urllib3 as pool_kwargs["ssl_context"] for every verify=True request,
  unconditionally, even when the same call also supplies a client certificate via pool_kwargs["cert_file"]/
  ["key_file"] (adapters.py:102-109, fed from HTTPAdapter.cert_verify()'s cert handling at :323-329).
  urllib3's ssl_.ssl_wrap_socket() then calls context.load_cert_chain(certfile, keyfile) on that exact
  shared object whenever certfile is truthy.
trigger: >
  Any single verify=True request anywhere in the process supplies a client certificate via the documented
  `cert=` parameter (`Session.request(..., cert=(...))` or `HTTPAdapter.send(..., cert=(...))`).
impact: >
  Because ssl.SSLContext exposes no API to unload a previously loaded certificate chain, and because
  _preloaded_ssl_context is a single literal object shared by every HTTPAdapter/connection pool in the
  process for the remainder of its life, every subsequent verify=True connection to ANY host — including
  hosts and threads that never requested a client certificate — will present that first request's client
  certificate for as long as the process runs. This is a client-credential/identity leak to unrelated
  servers.
change: >
  In _urllib3_request_context (src/requests/adapters.py), don't reuse the shared _preloaded_ssl_context
  when client_cert is not None; build (and if warranted, cache per client-cert pair) a private SSLContext
  for that combination instead, so a client certificate never persists onto the object handed to unrelated
  connections.
raw code citations:
  - src/requests/adapters.py:94-95 (unconditional shared-context assignment for verify=True)
  - src/requests/adapters.py:102-109 (client_cert handling, same function, no interaction with the
    ssl_context branch)
  - src/requests/adapters.py:323-329 (cert_verify sets conn.cert_file/key_file unconditionally, regardless
    of verify)
  - installed urllib3 2.7.0, src/urllib3/util/ssl_.py, function ssl_wrap_socket(): the line
    `if certfile: context.load_cert_chain(certfile, keyfile)`, called against the exact object passed in
    as `ssl_context` (see also connection.py `_ssl_wrap_socket_and_match_hostname`: `context = ssl_context`
    when `ssl_context is not None`, and `HTTPSConnection.connect()` passing `cert_file=self.cert_file,
    key_file=self.key_file, ..., ssl_context=self.ssl_context` into that same function)
```

Because this candidate's `kind` is `concurrency`, apply `verifier-concurrency.md`'s bug-class check to it
in full if you confirm it (full text quoted below).

Recorded focused-check evidence from the primary reviewer (citation, not interpretation — please
independently re-run, or construct your own equivalent probe):

- Command: `PYTHONPATH=/tmp/qual137/runs/i-bea6be14-seed1-att-01/src /tmp/qual137/venvs/requests/bin/python -m pytest /tmp/qual137/work/i-bea6be14-seed1-att-01/repro_shared_context_test.py -v`
  Head: `4089f3dc65f783beaa53cc032958ab625440d0ac`. Exit status: 0, both tests passed.
  `test_shared_context_is_singleton_regardless_of_client_cert`: proves `_urllib3_request_context()` returns
  the literal same `_preloaded_ssl_context` object whether or not `client_cert` is supplied.
  `test_client_cert_loaded_into_shared_context_leaks_to_future_requests`: uses the repository's own mTLS
  test fixture (`tests/certs/mtls/client/client.{pem,key}`), performs the exact mutation urllib3 performs
  (`context.load_cert_chain(...)`) on the object requests handed it for one request, then shows a second,
  unrelated request (different host, no client cert of its own) receives back the identical, now-cert-
  loaded context object. No network access used.

## Related non-survivor ledger rows (related-acquittal mode — rule on these too, `holds`/`re-open`, at the depth `verifier.md`'s clean-verdict task sets for each `kind`)

```yaml
- id: adapters/http-scheme-unaware-pool-kwargs
  kind: bug
  claim: "_urllib3_request_context() builds ssl_context/cert_reqs/ca_certs pool_kwargs without checking whether the request's scheme is https, so a plain-HTTP request with verify=True still gets an ssl_context entry in pool_kwargs passed to a plain HTTPConnectionPool."
  disposition: dropped (pre-existing; no consequence)
  falsification: "Pre-existing at gate 2 (merge-base had identical scheme-unawareness for ca_certs); empirically harmless (PoolManager.connection_from_host with scheme=http and an ssl_context/cert_reqs pool_kwargs returns a normal HTTPConnectionPool, no exception)."
  evidence: src/requests/adapters.py:91-101

- id: adapters/ca-cert-dir-branch-in-request-context
  kind: bug
  claim: "_urllib3_request_context() now distinguishes os.path.isdir(verify) to choose ca_certs vs. ca_cert_dir, a behavior the merge-base version of this function did not have."
  disposition: dropped (established intentional, gate 6)
  falsification: "Author's own review-thread comment (quoted above) explicitly announces this exact change as deliberate, matching cert_verify()'s pre-existing isdir handling."
  evidence: src/requests/adapters.py:96-100

- id: adapters/pooled-connection-stale-cert-attrs
  kind: bug
  claim: "When verify=True, cert_verify() no longer sets conn.ca_certs/conn.ca_cert_dir at all (only conn.cert_reqs); if the same pooled connection object were later reused for a different verify value it might retain stale ca_certs/ca_cert_dir from an earlier use."
  disposition: dropped (pre-existing pool/connection semantics; consequence unproven)
  falsification: "cert_verify() runs on every send() before urlopen() and always sets the attribute governing the branch actually taken; this reuse pattern and urllib3's pool-keying are unchanged by this diff and pre-date it; no concrete broken trigger was established distinguishing head from merge-base behavior."
  evidence: src/requests/adapters.py:297-321
```

*(the full text of `verifier.md` and `verifier-concurrency.md` followed verbatim in the actual dispatch,
identical to the copies quoted in §0 of this report / read directly from the skill snapshot; omitted here
a second time to avoid duplicating the entire reference text three times in this report — see "What to
return" instructions which followed, identical in substance to verifier.md's own Verdicts/Clean-verdict
sections)*

</details>

### 7.2 Verbatim report returned

<details open>
<summary>Full verifier response (verbatim)</summary>

Clone is clean, still on `review-head` at the pinned SHA. No mutation occurred. Final verdicts below.

## CAND-01: `adapters/import-time-cert-load-crash`

**Verdict: confirmed**

- Basis: trigger, impact, and "introduced-here" all independently re-verified.
- Gate 2 (introduced here): at merge-base (`8dd3b26bf5...`), `load_verify_locations()` for the default bundle only ran lazily inside `cert_verify()`, guarded by `os.path.exists(cert_loc)` → clear `OSError` (merge-base `adapters.py:275-295`, quoted in my read). At head, `src/requests/adapters.py:75-78` calls `_preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))` unconditionally at module scope, with no try/except. `git log` on this file shows this was introduced by commit `8f954567` ("Use a default SSLContext with the default CA bundle loaded when `verify=True`").
- Independently re-ran both cited pytest commands, verbatim as specified: both passed with the exact decisive output cited (`FileNotFoundError` at `adapters.py:76` during `<module>` import for the head repro; clean `IMPORT_OK` for the merge-base repro under identical broken-bundle conditions). No network access used; matches recorded evidence.
- Gate 5 (intentional?): the quoted review excerpt has agubelu explicitly describing "creating a module-level SSLContext with that bundle already loaded" — this establishes the *design choice* to load eagerly at module scope as reviewed/intentional. However, the review record never discusses failure handling for a missing/unreadable bundle, i.e., it does not address that this makes `import requests` itself crash uncaught for processes that never use the default trust store. Per the gate-5 rule ("establishes intent only for what the review record explicitly addresses"), the crash-on-failure behavior is not established as intentional — only the general "eager, preloaded" mechanism is.
- No basis for `refuted` applies (not contradicted, not prevented by a guard, not intentional as to the crash specifically, not pre-existing — merge-base did not have this exposure, and impact is proven by direct execution, not merely unresolved).

Correction: none needed to trigger/impact/priority/action/anchor/fix/change — all verified accurate as stated. One nuance to add to `claim`/gate-5 framing: note explicitly that the *general* design (eager module-level load) was reviewed and intentional; only the *unguarded-failure* aspect is unaddressed and thus not shielded by intent.

## CAND-02: `adapters/shared-ssl-context-cert-chain-leak`

**Verdict: confirmed**

- Gate 2 (introduced here): merge-base `_urllib3_request_context()` had no `ssl_context` branch at all (`if isinstance(verify, str): pool_kwargs["ca_certs"] = verify`); head introduces `elif verify is True: pool_kwargs["ssl_context"] = _preloaded_ssl_context` at `adapters.py:94-95`. Traced to the same commit `8f954567` as CAND-01.
- Independently re-ran the cited pytest command; both tests passed as recorded.
- Independently traced the full urllib3 2.7.0 plumbing beyond what was cited, confirming the mechanism precisely:
  - `connectionpool.py:1030-1031` (`HTTPSConnectionPool.__init__` stores `self.cert_file`/`self.key_file`/`ssl_context` from `pool_kwargs`) and `:1080-1085` (`_new_conn` passes `cert_file=self.cert_file, key_file=self.key_file, ...` into each new `HTTPSConnection`).
  - `connection.py:935` (`_ssl_wrap_socket_and_match_hostname`: `context = ssl_context` — no copy — when `ssl_context is not None`).
  - `ssl_.py:427` (`ssl_wrap_socket`: `if certfile: context.load_cert_chain(certfile, keyfile)`), mutating the exact shared object in place.
  - `poolmanager.py:56-89` (`PoolKey` includes `key_cert_file`/`key_key_file` but **also** `key_ssl_context` as a literal-object field) — confirms a with-cert request and a without-cert request to different hosts get *different* connection pools (different `PoolKey` due to differing cert_file/key_file) but the identical `_preloaded_ssl_context` object reference, so the mutation performed by one pool's connection is visible to the other pool's connections.
- Gate 5 (intentional?): per the task's supplied excerpts, the renaming commit (`f21e70bf7`) is the only place the shared-context "publicness" was addressed, and no participant discusses the cert_file/key_file interaction. Not established as intentional.
- No `refuted` basis applies.

### Concurrency bug-class analysis (verifier-concurrency.md)

1. **Invariant at rule level**: "The client TLS certificate chain presented during any single connection's handshake must equal exactly the client certificate that connection's own request specified (or none) — no connection may present a certificate chain loaded on behalf of a different request." At merge-base this held structurally: no `SSLContext` object was shared across requests/pools at all (each pool's TLS state lived in per-pool `ca_certs`/`cert_reqs`/`cert_file` scalars, not a shared mutable object), so there was no cross-request channel for this invariant to break through. At head, the invariant depends entirely on `_preloaded_ssl_context` never being mutated by one request in a way visible to another — but no lock, no copy, and no per-request isolation protects it.

2. **Shutdown vs. steady state**: No shutdown/teardown/error path is required. The failing interleaving is two ordinary, successful requests in normal steady-state operation (request A with `cert=`, then request B without, to any host). Traced end-to-end above (adapters.py:94-109 → connectionpool.py:1030-1085 → connection.py:935 → ssl_.py:427) to a **fails** verdict: after A's handshake, `_preloaded_ssl_context` permanently carries A's loaded chain, and any later verify=True connection anywhere in the process — including B, which requested no client cert — is handed that same mutated object. This is confirmed as a real steady-state defect, not merely a shutdown-path curiosity. (Note: per the maintainer testimony quoted in the prompt itself — tiran: "The problem is unrelated to threads and can even occur in a single-threaded program" — this leak's core manifestation doesn't even require concurrent threads, only sequential reuse of the module-level singleton across requests. The `kind: concurrency` label is defensible because true multi-threaded use compounds it, but the base defect is a shared-mutable-global-state bug that fires even single-threaded.)

3. **Sibling interleavings** (actor pairs touching `_preloaded_ssl_context`):
   - *Request-with-cert (A) vs. later request-without-cert (B), sequential or concurrent, any host*: **fails** — demonstrated by trace and by the independently re-run test.
   - *Request-with-cert-A vs. concurrent request-with-cert-B (different credentials, different hosts, truly concurrent threads)*: **fails**, and worse-shaped — `context.load_cert_chain()` is called by two threads on the identical object with different arguments; final state is a data race (last write wins, or per tiran's testimony, "surprising behavior" from reconfiguring a context already in use by a live connection). I did not execute a live-thread reproduction of this specific sub-case (only the sequential/attribute-identity leak was executed); I flag this narrower point as inferred from code + the quoted maintainer testimony, not independently execution-confirmed.
   - *Module import (creation of the singleton) vs. first request*: **holds** — Python's import machinery guarantees the module executes to completion, including lines 75-78/session construction, before any importer's code can call `_urllib3_request_context`; no race here.
   - *Concurrent request-without-cert vs. request-without-cert*: **holds** — neither mutates the shared context (no `load_cert_chain` call), so no interference regardless of concurrency.

4. **Sibling code paths governed by the rule**: both the direct path (`adapters.py:400-402`, `self.poolmanager.connection_from_host`) and the proxy path (`adapters.py:394-397`, `proxy_manager.connection_from_host`) consume the identical `pool_kwargs` produced by the single `_urllib3_request_context()` call at `adapters.py:383`. Both are equally exposed; neither is currently protected.

5. **Widening `change`**: the candidate's proposed fix — stop handing out the shared context when `client_cert is not None`, build/cache a private `SSLContext` per client-cert identity instead — already operates inside `_urllib3_request_context()`, so it automatically covers both sibling code paths (direct and proxied) without further widening. It also resolves the producer/producer race in step 3 (each distinct cert pair gets its own context object, so two concurrent client-cert requests no longer contend on one object). One necessary refinement the candidate doesn't state: if a cache keyed by client-cert pair is added, that cache's own read/create-if-absent operation needs its own lock/synchronization to avoid two threads racing to build two different context objects for the same identity or a lost-update on cache population — this is a needed addition to the proposed `change`, not a widening of the rule itself.

No correction needed to `trigger`/`impact`/`priority`/`action`/`anchor`/`fix` — all verified accurate. `change` should be extended with the cache-synchronization note above.

## Related ledger rows (related-acquittal mode, `kind: bug`, full 5-step attack applied)

**`adapters/http-scheme-unaware-pool-kwargs` — holds**
- Premise: scheme-unawareness is pre-existing and empirically harmless.
- Opposite-branch trace: confirmed both merge-base and head build `ssl_context`/`ca_certs`/`cert_reqs` into `pool_kwargs` without checking scheme (pre-existing, matches). Traced the actual urllib3 mechanism (not cited by the ledger row itself): `poolmanager.py` `_new_pool()` — `if scheme == "http": for kw in SSL_KEYWORDS: request_context.pop(kw, None)` — urllib3 itself strips every SSL-related kwarg (including `ssl_context`, `cert_reqs`, `ca_certs`) before constructing a plain `HTTPConnectionPool` for scheme `http`. This makes the harmlessness decisive rather than merely asserted.
- Decisive new citation: `urllib3/poolmanager.py` `_new_pool()`, the `SSL_KEYWORDS` stripping loop (not cited by the ledger row).
- Ruling: **holds**.

**`adapters/ca-cert-dir-branch-in-request-context` — holds**
- Premise: the isdir branch is a deliberate, reviewed change matching `cert_verify()`'s pre-existing handling.
- Opposite-branch check: confirmed via `git show 8f954567 -- src/requests/adapters.py` that this exact commit ("Use a default SSLContext with the default CA bundle loaded when `verify=True`") introduces both the `ssl_context` sharing *and* the `isdir(verify)` → `ca_cert_dir` branch in the same diff hunk, and confirmed `cert_verify()` already had identical isdir handling at merge-base (unchanged across the PR). This lines up exactly with the quoted author statement ("I also changed `_urllib3_request_context()` slightly to handle the case where verify is a path to a dir...").
- Decisive new citation: `git show 8f954567:src/requests/adapters.py` diff hunk (commit-level evidence, not cited by the ledger row, which only cited the head line range).
- Ruling: **holds**.

**`adapters/pooled-connection-stale-cert-attrs` — holds**
- Premise: `cert_verify()` mutates a pool object whose identity (urllib3 `PoolKey`) is itself derived from the same TLS settings it sets, so no stale cross-`verify`-value attribute reuse on the same object is possible.
- Opposite-branch trace: if the same pooled object survived a change from e.g. `verify="/custom.pem"` to `verify=True` for the same host, stale `ca_certs` could linger since the head `verify=True` branch never clears `conn.ca_certs`/`conn.ca_cert_dir` (unlike the `else` branch, which explicitly nulls them). Checked whether this reuse is actually possible: `urllib3/poolmanager.py` `PoolKey` (lines defining `key_ca_certs`, `key_cert_reqs`, `key_ca_cert_dir`, `key_ssl_context`) includes exactly the fields that differ between a string-`verify` request and a `verify=True` request. A change in `verify` therefore always produces a different `PoolKey`, so `connection_from_host` returns a distinct pool object rather than the one with stale attributes — the failing state transition is impossible to construct.
- Decisive new citation: `urllib3/poolmanager.py` `PoolKey` field list (not cited by the ledger row, which only cited `adapters.py:297-321`).
- Ruling: **holds**.

**Batch conclusion for the related rows: clean verdict stands** (all three rows independently re-attacked and hold, each backed by at least one citation the ledger row itself did not supply).

## Duplicate-id merge groups

None. CAND-01 (import-time crash) and CAND-02 (shared-context cert leak) address disjoint lines/behaviors and neither overlaps any of the three related rows.

## Observation (non-actionable, sub-threshold)

While tracing the urllib3 handshake path for CAND-02, I noticed `connection.py`'s `_ssl_wrap_socket_and_match_hostname` also does `context.verify_mode = resolve_cert_reqs(cert_reqs)` on the shared `ssl_context` object on every single connection, not just `load_cert_chain`. Currently this is a no-op in practice since `cert_reqs` is always `"CERT_REQUIRED"` when `verify is True` (the only path that hands out the shared context), so no observed divergence results today. Flagging only as an incidental fact; it does not contradict or extend either candidate's verdict and requires no action.

## Sandbox/hygiene disclosure

All reads and executions stayed within the three permitted roots (clone, skill snapshot area was not needed since the two reference docs were supplied inline, work directory). No path outside the allowlist was read. Git state on `review-head` remains clean and unmutated at the pinned SHA `4089f3dc65f783beaa53cc032958ab625440d0ac`; no destructive or mutating git commands were run.

</details>

### 7.3 Reconciliation

Both survivors: `confirmed`, no correction to `trigger`/`impact`/`priority`/`action`/`anchor`/`fix`.
CAND-02's `change` is extended per the verifier's concurrency-bug-class widening: the private-context
fix must itself be built/cached under its own synchronization (a lock around read/create-if-absent) so
two threads building a context for the same client-cert identity at once cannot race — folded into the
rendered finding's `Change` field below. All three related rows: `holds`; ledger unchanged. No row was
re-opened, so no re-falsification and no follow-up batch was needed or dispatched. Zero-survivor
eligibility never applied (two survivors existed throughout). The single non-actionable observation the
verifier surfaced (shared-context `verify_mode` reassignment, currently a no-op) is recorded here as part
of the verifier's return and is not promoted to a finding or to the summary's `Observations` section: it
neither contradicts a supplied row nor independently meets the finding gates (no proven consequence today
— the value written is always identical), and the rubric routes a verifier aside exactly this way ("A
verifier aside becomes a finding only through full primary admission and whatever verification SKILL.md
step 3 then requires" — this fact was never independently admitted by the primary under the ordinary
gates, so it stays in this private record only).

## 8. Validation, rendering, and the would-be publication

- **Payload:** `/tmp/qual137/work/i-bea6be14-seed1-att-01/payload.json`, assembled per
  `scripts/validate_review.py`'s documented input schema (2 findings + 1 observation; no questions).
- **Render step:** `python3 scripts/validate_review.py --render payload.json` — first attempt exited 1
  (`trailer-sha: --render needs a run trailer whose head is a full 40-hex SHA when repository_url is
  present`) because I initially left `summary.body` as a placeholder with no trailer; fixed by adding a
  `summary.trailer` field, then `--render` exited 0 and printed the two `anchor ...` fragments, pasted
  verbatim into the finished `summary.body` (see payload.json for the final trailer, now embedded in the
  body as the contract expects; the separate `summary.trailer` key was removed once the body carried it).
- **Validate step:** `python3 scripts/validate_review.py payload.json` — exit 0, zero violations. Timing
  sidecar event `payload_validated_at` was recorded immediately after, via `python3 mark_event.py
  /tmp/qual137/reports/i/i-bea6be14-seed1-att-01-timing.json payload_validated_at`, per this dispatch's
  binding rule.
- **Emit-batch step:** `python3 scripts/validate_review.py --emit-batch payload.json > batch.json` — exit
  0, produced the forge-native one-call review body (`commit_id=4089f3dc65f783beaa53cc032958ab625440d0ac`,
  `event=COMMENT`, `body=<summary>`, two line `comments`, one per finding, each carrying the finding's
  markdown plus trailer). This batch was **never submitted**: per this run's binding condition #4 and the
  Boundaries section of SKILL.md ("retrospective review of a merged pull request is non-publishing by
  default" and this run's publication is not separately authorized), the run stops at rendering. No `gh
  api` call, no write of any kind, was made.
- **Immediately-before-write head re-check:** the output contract's publication invariant ("re-fetch the
  head immediately before writing; a stale or unreadable head aborts all publication") does not apply
  literally here since there is no write to precede — SKILL.md step 6 says non-publishing retrospective
  mode "skip[s] the write and report[s] the complete would-be review instead." I nonetheless confirmed the
  locally pinned head is unchanged and the tree is clean immediately before finalizing this report:
  `git -C /tmp/qual137/runs/i-bea6be14-seed1-att-01 rev-parse review-head` → `4089f3dc65f783beaa53cc032958ab625440d0ac`
  (matches the pinned head exactly); `git status --porcelain` → empty (clean tree, no mutation by me or by
  the verifier sub-agent); `git rev-parse main` → `8dd3b26bf59808de24fd654699f592abf6de581e` (merge-base
  branch also untouched).
- **Review payload deliverable:** `/tmp/qual137/reports/i/i-bea6be14-seed1-att-01-payload.md` — the
  summary body (with the `Mode` line) and both finding comments with their trailers, reconstructed from
  `batch.json`/`payload.json` with nothing else added, as the review would have posted had publication
  been authorized.

## 9. Derived status

Per the output-contract's Status section: `Changes Requested` because two `must-fix` findings are
unsettled (both independently confirmed, neither corrected away). No unanswered outcome-changing question
exists, so `Needs Information` does not apply; coverage is complete, so `Incomplete` does not apply.
Authorization: `kamui` (posting identity) has no gating authorization on this run (third-party retrospective
review), so the forge event is `COMMENT` regardless of status, and the visible status carries `(advisory)`:
**`Changes Requested (advisory)`**.

## 10. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
| --- | --- | --- |
| Question channel | Did not fire | No candidate reached the static-unresolvability bar (rubric's Issue fit / Uncertainty routing sections). Both survivors were fully decidable by static tracing plus offline reproduction; nothing needed a maintainer/measurement answer. §4, §6. |
| Clean-verdict verification (zero-survivor or related-acquittal) | **Related-acquittal mode fired**; zero-survivor mode did not (there were survivors throughout). | §7: the single verifier batch carried CAND-03/04/05 as related non-survivor rows alongside the two candidates, per SKILL.md's related-acquittal rule (same file as a survivor's anchor). All three ruled `holds`; batch conclusion "clean verdict stands" for that sub-set. No re-open. |
| Observations | Fired | One observation published (test-coverage hygiene fact, CAND-06), well under the 3-item cap. §6, §9, payload. |
| Fix-sufficiency check on a concurrency/invariant candidate | Fired | CAND-02 is `kind=concurrency`; the verifier applied the full `verifier-concurrency.md` 5-step bug-class check (invariant at rule level, steady-state trace, sibling interleavings, sibling code paths, widened `change`) and returned one widening correction (cache synchronization), folded into the rendered finding's `Change` field. §7.2, §7.3. |
| Follow-up verifier round | Did not fire | Zero corrections changed a mandatory claim, zero rows were re-opened, and no new candidate became render-eligible after the initial batch. SKILL.md step 3's follow-up batch is spent only when one of those conditions holds; none did, so the one-initial-batch outcome stands and no second batch was dispatched. §7.3. |
| Deferral handling | One explicit deferral found in the review record (renaming the shared context, "the last blocker is the context being 'public'") | Checked against gate 6 for CAND-02 and found it was **resolved** in-record (commit `f21e70bf7`), not open; the author's separate closing remark about possibly moving `cert_verify()`'s logic was judged not a design/naming/API-shape deferral and was not promoted to an open question. §4 (Issue fit ledger, closing paragraph), §6 (Considered, never raised). |
| Retrospective mode | Fired | Publication disabled throughout; `Mode:` line rendered in the summary body per the output contract's mandatory rule for `merged: true`. §2, §8, payload. |
| Early verifier dispatch | **Did not fire — dispatched after the complete pass**, per SKILL.md step 3's exception. | The diff touches a security/cryptography surface (shared TLS context + client-certificate handling), which the skill explicitly excludes from early dispatch ("do not dispatch early when the diff touches ... a security or authorization boundary"). Dispatch happened only after the complete diff read (§3), the finished manifest, and complete primary falsification of every mandatory-verification candidate and every related row (§6, §7 opening paragraph). |

## 11. History discipline

I did not read any repository history beyond the pinned head. History commands run, all read-only and all
confined to the merge-base↔head range or explicit single-commit lookups already reachable from the pinned
head:

- `git status`, `git log --oneline -5 main` / `-5 review-head`, and `git merge-base main review-head` — to
  confirm the packet's pinned identity locally (§2), not to look beyond the head; the newest object touched
  was `4089f3dc6`, the pinned head itself, matching packet binding condition #3.
- `git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py` and
  `git archive 8dd3b26bf59808de24fd654699f592abf6de581e -- src/requests` — merge-base-only reads, used for
  the base-branch guarantee tests (gate 2) and the base-import reproduction. Never touched anything past
  the merge-base other than the pinned head itself.
- The verifier sub-agent additionally ran `git log`/`git show` against specific commits already listed in
  the packet's commit table (`8f954567`, `f21e70bf7`), all of which sit strictly between the merge-base and
  the pinned head — no history beyond the pinned head was read by it either, per its own hygiene
  disclosure (§7.2, "Sandbox/hygiene disclosure").
- `review_context.py`'s own `history` section (pre-merge-base commit list for the changed file, §3) was
  printed by the context-build call and read, but never used to decide any candidate (noted explicitly in
  §3); it is history *before* the merge-base, which the tool prints by design and which the packet does not
  forbid (only history *after* the pinned head is forbidden, per binding condition #3, and none was read).

No `git fetch`, `git pull`, `gh`, `curl`, or web fetch of any kind was performed, by me or by the verifier.

## 12. Sandbox disclosure

No path outside the authorized set was read by me: the clone
(`/tmp/qual137/runs/i-bea6be14-seed1-att-01`), the skill snapshot
(`/tmp/qual137/snapshots/bea6be14/snapshot-path-omitted/`), the packet directory
(`/tmp/qual137/packets/i/`), my own work directory (`/tmp/qual137/work/i-bea6be14-seed1-att-01/`), my own
report/payload/timing paths under `/tmp/qual137/reports/i/i-bea6be14-seed1-att-01-*`, and one incidental
`ls` of the shared `/tmp/qual137/reports/i/` directory (to locate my own timing sidecar), which surfaced
the *filenames* of another attempt's report/timing/session files
(`i-867cf3ff-seed1-att-02-{session.txt,timing.json}`) in a directory listing — I did not open, read, or
otherwise use the contents of any of those files, and I disclose the filename exposure here per rule 7,
even though no content from another run was read. The verifier sub-agent reported no path outside its own
authorized set (§7.2).

## 13. Notes — judgment calls on ambiguities in the skill's contract

1. **Context digest without a `forge-packet/1` file.** SKILL.md step 1 and the output contract describe
   computing `context` via `context_fingerprint.py --packet packet.json`, where `packet.json` is
   `forge_packet.py normalize`'s output over saved GraphQL page files. This cell supplies no raw GraphQL
   pages (offline, no network, phase 1 already resolved by the orchestrator into `packet.md`), so no such
   `packet.json` could be produced. I used the output contract's own documented fallback instead: "On a
   forge without that packet, supply `pr`, `issues`, `specs`, and `guidance` directly from the exact
   reviewed inputs" — i.e. `context_fingerprint.py <input.json>` (no `--packet` flag) with `pr.title`/
   `pr.body` taken verbatim from the packet's §3, `issues: []` (`issues=none`), `specs: []` (none
   supplied), `guidance: []` (packet §7: no guidance files present at merge-base). I treat this as the
   correct reading of "supply ... directly from the exact reviewed inputs" for a cell whose "forge" is a
   pre-resolved packet rather than a live API, not as a deviation from the contract. Resulting digest:
   `9e80f1a16f93243a31dff067dd6ba49658a84f52b2a0216860c03ff210cf8621` (computed once, per SKILL.md step 3's
   "Compute the `context` digest once, from the packet").
2. **Kind classification for CAND-02.** The candidate's headline, decisively reproduced consequence
   (client-certificate persistence/leak across unrelated requests) is a security consequence provable
   without any concurrent execution. I classified it `kind=concurrency` rather than `kind=security`
   specifically so that `verifier-concurrency.md`'s deeper bug-class check (sibling interleavings, steady-
   state trace, rule-level widening) would apply, on the view that the rubric's own instruction — "Use
   `concurrency` or `invariant` when sibling paths share the broken state rule and therefore require the
   verifier's bug-class check" — is about which check the defect *needs*, not only about whether true
   thread races are the sole failure mode. The verifier's own analysis (§7.2) validated this choice: it
   both confirmed the sequential/deterministic manifestation I had already proven and identified an
   additional, not-independently-executed, genuinely concurrent sub-case (two threads racing
   `load_cert_chain()` with different certificates) that the deeper check was positioned to surface.
   I recorded this reasoning explicitly rather than silently picking a kind label.
3. **Whether the author's closing-paragraph remark is a "design, naming, or API-shape" deferral.**
   SKILL.md step 1 requires recording "every explicit deferral of a design, naming, or API-shape decision"
   as an open question rather than accepted. The PR author's remark about possibly moving
   `cert_verify()`'s remaining logic into `_urllib3_request_context()` reads as an implementation-location
   musing, not a decision about what a surface's design, name, or API shape should be. I judged it out of
   scope for that specific step-1 rule and did not promote it to an open question; §4 and §6 record the
   reasoning so a different reviewer's contrary judgment is checkable against the same evidence.
4. **Anchor/fix collapse.** Both survivors' natural "fix" location is the same span as their anchor (the
   defect and its repair both live in the same few lines of `_urllib3_request_context`/module scope). Per
   the output contract ("Omit `fix` when it is the anchor"), I omitted the `fix` field on both findings
   rather than repeating the anchor coordinate as a redundant `fix`.
5. **Related-acquittal scope.** SKILL.md's related-acquittal rule includes a row when its evidence pointer
   is "in the same file as a survivor's anchor or fix" — since this diff is entirely confined to one file,
   this reading sweeps in every `bug`/`concurrency`/`invariant`/`security`-kind dropped candidate in the
   file, not just ones near the survivors' specific lines. I applied the rule literally as written (all
   three dropped `kind=bug` rows qualified) rather than narrowing it to "same function" or "same hunk",
   since the text says "file", not a smaller unit, and a single-file diff is the case where that literal
   reading is least likely to be an oversight in the rule's drafting (a large multi-file diff would show
   the same-file criterion doing real, non-trivial narrowing work).
6. **No Changed-tests obligation.** The diff adds or changes zero test functions (only `adapters.py`
   changed). The rubric's "Changed tests" section (execution, tracing, per-case obligations) is therefore
   vacuous by scope, not "unavailable" in the sense of a missing toolchain — I recorded this distinction
   explicitly in the summary body's Coverage line so a reader cannot mistake "no changed test" for "test
   skipped."
7. **Re-review reference not read.** SKILL.md step 1 gates `references/re-review.md` behind "step 1 finds
   prior state from the posting identity." The packet states plainly that `kamui` has no prior comments or
   reviews on this PR, so I treated this as a first review and did not load that reference at all — noted
   explicitly here since its non-use is itself a judgment call worth recording, not merely an omission.
8. **`conformance.md` not read.** No issue, PR text, or repository convention in this run names a tracked
   versioned artifact (stub, binding, schema, generated source) that this change must conform to, so the
   reference's loading condition in SKILL.md step 2 never fired; recorded in §4.

## 14. Deliverables

- Review payload (would-be publication): [`i-bea6be14-seed1-att-01-payload.md`](i-bea6be14-seed1-att-01-payload.md)
- This research report: `i-bea6be14-seed1-att-01-run.md` (this file)
- Timing sidecar: `i-bea6be14-seed1-att-01-timing.json` (`payload_validated_at` recorded post-validation,
  per binding rule; no other event written)
- Scratch work (all under my own work directory, nothing added to or changed in the clone):
  `payload.json`, `batch.json`, `context_output.md`, `fingerprint_input.json`, `pr_body_extracted.txt`,
  `store_dir.txt`, `repro_shared_context_test.py`, `repro_import_time_crash_test.py`,
  `repro_base_import_ok_test.py`, `base_adapters.py`, `base_src/` (read-only merge-base tree extraction via
  `git archive`).

