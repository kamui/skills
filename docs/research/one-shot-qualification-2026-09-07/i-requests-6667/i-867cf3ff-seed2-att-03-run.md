# Research report — `psf/requests#6667`, cell `i-867cf3ff-seed2`, attempt `att-03`

## 1. Metadata

- **Target:** `psf/requests#6667` — "Avoid reloading root certificates to improve concurrent performance"
- **Cell / attempt:** `i-867cf3ff-seed2` / `att-03`
- **Skill snapshot:** `/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/` (`SKILL.md` supersedes `code-review-publish-legacy`)
- **`workflow` identifier reported by the validator:** `v5b-1` (from `scripts/validate_review.py`'s `WORKFLOW` constant, confirmed at final validation run below)
- **Model:** I (the primary reviewer, this whole dispatch) ran on `claude-sonnet-5`. Every sub-agent I spawned also ran on `model: "sonnet"` (explicit on the call) — see §4 for the one verifier batch dispatched.
- **Verification trigger fired:** Yes. `SKILL.md` step 3: *"Independently verify every surviving candidate proposed as `must-fix`, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break."* Both survivors (`ssl-context-sharing/client-cert-mtls-leak` and `adapters/eager-ca-bundle-import-crash`) were proposed `must-fix`, and the first is additionally a concurrency/security defect. One initial candidate batch was dispatched in a fresh context (candidate mode) carrying both survivors, plus three related non-survivor ledger rows under related-acquittal mode (all `kind=bug`, decisive evidence in the same file, `src/requests/adapters.py`, as the survivors' anchors — see §3).
- **Sub-agents spawned:** 1 — role: independent verifier (candidate mode + related-acquittal mode combined in one batch, as `SKILL.md` requires them to ride in the same batch). `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false`.
- **Candidates raised:** 6 total (`C1`, `C2` survivors; `D1`–`D4` dropped/refuted).
- **Candidates surviving my own falsification:** 2 (`C1`, `C2`), both carried forward to verification.
- **Verifier verdicts:** `C1 confirmed` (with a correction *widening* the trigger to a simpler, single-threaded case and relocating `fix`, see §4), `C2 confirmed` (with a corroborating impact detail added), `D1 holds`, `D2 holds`, `D3 holds` (all three acquittals stand; verifier found no re-open).
- **Findings for publication:** 2 — see §2.
- **Questions:** 0.
- **Observations:** 1 published (of 1 that qualified; no cap was exceeded).
- **Coverage:** Complete. The single changed file (`src/requests/adapters.py`) was read in full via the diff's `--function-context` output plus the two named enclosing functions/class as bounded ranges; all rubric risk checks (TLS/authorization boundary, concurrency, compatibility) were exercised with evidence; one focused pytest selection was run per flag-set as permitted; no fetch failed; no verification is incomplete.
- **Derived status:** `Changes Requested (advisory)` — 2 unsettled `must-fix` findings on a retrospective, non-publishing run against a merged PR authored by a third party (`kamui` never authored or previously reviewed this PR).
- **Own token usage:** Not reported by the harness to me in a form I can quote; I have no token-usage figure to report for this run.

## 2. Findings that survive (full detail)

### Finding 1 — `ssl-context-sharing/client-cert-mtls-leak`

- **Priority / action:** `P1` / `must-fix` / `blocking=true`
- **Kind:** `concurrency`
- **Anchor:** `src/requests/adapters.py:94-95` (`RIGHT`) — the `elif verify is True: pool_kwargs["ssl_context"] = _preloaded_ssl_context` branch of `_urllib3_request_context`.
- **Fix location:** `src/requests/adapters.py:94-107` — the `elif verify is True:` branch and its interaction with the `client_cert is not None` block in `_urllib3_request_context` (corrected from my original `:75` by the verifier: the singleton's *creation* line is fine as-is; the decision logic that hands it out unsafely is what must change).
- **Claim:** `_preloaded_ssl_context` is a single process-wide `ssl.SSLContext` object handed unconditionally to every connection pool created for `verify=True`, including pools that also carry a per-request client certificate (`cert=`) or a hostname-check override (`assert_hostname=False`/`assert_fingerprint` via custom `pool_kwargs`); urllib3's `ssl_wrap_socket()`/`_ssl_wrap_socket_and_match_hostname()` mutate the *same* passed-in context object in place on every connect (`context.verify_mode = ...`, `context.check_hostname = False` under some conditions, and unconditionally `context.load_cert_chain(certfile, keyfile)` whenever a client cert is supplied), so one connection's client-certificate identity or hostname-check setting can silently apply to a different, concurrent or subsequent connection that shares the same context object.
- **Trigger:** No concurrency is even required (the verifier's independent, and stronger, reconstruction): make one `Session.get(url_a, cert=(certfile, keyfile))` call to host A with `verify=True` (the default), then any later plain `Session.get(url_b)` call with `verify=True` and **no** `cert=` at all to a *different* host B that must open a new physical connection — the shared context still has host A's client certificate loaded and presents it to host B. The originally-drafted concurrent variant (two threads, two different hosts, two different client certs, racing on `context.load_cert_chain()`) is a second, independently real trigger for the same defect, and is the PR's own stated primary workload (many concurrent requests).
- **Impact:** A connection to an unrelated host can silently present a different request's client certificate during the TLS handshake — a cross-request client-identity/authentication leak that persists for the rest of the process once triggered once, not just during a race window — and, separately, any pool that disables hostname checking (`assert_hostname=False`/`assert_fingerprint`) turns hostname verification off for every other concurrent or later `verify=True` connection in the process, because `check_hostname` lives on the same shared object.
- **Change:** Do not hand the same live, mutable `SSLContext` to a connection pool that also carries a client certificate or a hostname-check override. Build (or clone) a private, connection-scoped context in those cases — the same isolation that existed before this diff, when `ssl_context=None` made urllib3 construct a fresh context per connection — and reserve the shared, pre-loaded context strictly for the plain "`verify=True`, no client cert, no hostname override" case it was designed for. (The verifier explicitly checked whether this `change` needed widening to cover the sequential/persistent-contamination trigger it found, and confirmed it already does — no further widening required.)
- **Verification status:** `independent-confirmed`.
- **Evidence:**
  - `src/requests/adapters.py:75-78,94-95,102-108` (head) — the singleton is created once at import and handed into `pool_kwargs["ssl_context"]` for every `verify=True` request; `client_cert` is folded into the very same `pool_kwargs` dict at lines 102-108, unconditionally, regardless of whether `ssl_context` was just set.
  - `git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py:75-90` (merge-base) — at merge-base, `pool_kwargs` never carried an `ssl_context` key for `verify=True`, so urllib3's `_ssl_wrap_socket_and_match_hostname` always took the `ssl_context is None` branch and built a fresh, connection-private `SSLContext` on every single `connect()` call (confirmed by reading `.../urllib3/connection.py:925-936` in the pinned venv: `if ssl_context is None: default_ssl_context = True; context = create_urllib3_context(...)`).
  - `/private/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/connection.py:935` (`context = ssl_context`, no copy) and `:960-985` (`context.verify_mode = ...`; `context.check_hostname = False` under `assert_fingerprint`/`assert_hostname`/pyOpenSSL/no-common-name conditions; `ssl_wrap_socket(...)` called with `ssl_context=context`).
  - `/private/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/util/ssl_.py:403-429` (`ssl_wrap_socket`): `context = ssl_context` (the literal object, still no copy); `if certfile: context.load_cert_chain(certfile, keyfile)` — mutates the shared object.
  - Directly reproduced: calling `requests.adapters._urllib3_request_context()` twice, once per distinct host and distinct client certificate, returns `pool_kwargs["ssl_context"]` as the *literal same object* (`is` identity `True`) both times, and that object `is adapters._preloaded_ssl_context` (script `repro_shared_context.py`, output captured in §5).
  - Review-thread evidence that the general class of hazard was *named* but not resolved for this interaction: `tiran`'s 2024-05-05T05:08:40Z comment (packet §6, non-review conversation #5): *"It is thread safe as long as you don't reconfigure it once it is used by a connection... changing ciphers, verification settings, or mTLS certs can lead to surprising behavior."* — the merged fix (renaming the context to `_preloaded_ssl_context`, commit `f21e70bf7`) addresses only *external* user mutation of the object, not `cert_verify()`'s/`_urllib3_request_context()`'s own internal path that hands the shared object to `load_cert_chain()` whenever `cert=` is supplied. This satisfies the rubric's "unintentional" gate: the record names a related but distinct concern (naming/external tampering) and does not address the specific internal client-cert/hostname-override interaction.
- **Trigger scenario (concrete):** `s = requests.Session(); s.get("https://host-a/", cert=("a.pem","a.key")); s.get("https://host-b/")` — the second call uses `verify=True` (default) and **no** `cert=` at all, against a different host — still receives the same, now-contaminated `_preloaded_ssl_context` and presents host A's client certificate to host B. (The concurrent variant — two hosts, two different certs, racing `load_cert_chain()` calls — is a second real trigger for the identical underlying defect.)

### Finding 2 — `adapters/eager-ca-bundle-import-crash`

- **Priority / action:** `P1` / `must-fix` / `blocking=true`
- **Kind:** `bug`
- **Anchor:** `src/requests/adapters.py:75-78` (`RIGHT`) — the module-level `_preloaded_ssl_context = create_urllib3_context(); _preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))` statement.
- **Fix location:** same lines (no separate fix site).
- **Claim:** Loading and parsing the default CA bundle now happens unconditionally at `import requests` time (`requests/__init__.py` → `api.py` → `sessions.py` → `adapters.py`), rather than lazily on the first `verify=True` HTTPS request as at the merge-base. Any environment where `certs.where()`/`DEFAULT_CA_BUNDLE_PATH` resolves to a missing or unreadable file now makes `import requests` itself raise, unconditionally, even for callers who only ever use `verify=False` or a custom CA bundle path and would never have hit the old, lazy failure.
- **Trigger:** `DEFAULT_CA_BUNDLE_PATH` (from `certifi.where()`, or a distro/managed-environment override of `requests.certs.where()` — a customization `certs.py`'s own module docstring documents as supported: *"If you are packaging Requests... you can change the definition of where() to return a separately packaged CA bundle"*) points at a path that does not exist or cannot be parsed as a CA bundle at the moment `adapters.py` is first imported.
- **Impact:** `import requests` raises (e.g. `FileNotFoundError`/`ssl.SSLError`) and the library becomes completely unusable in that process, including for code paths that never needed the default bundle (`verify=False`, or a caller-supplied CA bundle). At the merge-base, the same broken default bundle only broke the specific request that actually exercised `verify=True` with no override, inside `cert_verify()`'s existing `OSError` handling. The verifier additionally noted: because the context is now built exactly once, at import, a workaround that worked at the merge-base — monkeypatching `requests.utils.DEFAULT_CA_BUNDLE_PATH` (or `certs.where()`) at runtime after `import requests`, to point at a working bundle — is now silently ineffective for `verify=True` traffic, since nothing ever re-reads that value after the module-level singleton is built.
- **Change:** Defer the CA-bundle load until first actual need (e.g. build `_preloaded_ssl_context` lazily on first `verify=True` use, or wrap the module-level load in a `try/except` that fails no worse than the previous per-request `OSError`), so that `import requests` cannot fail merely because the *default* bundle path is broken when the caller never relies on it.
- **Verification status:** `independent-confirmed`.
- **Evidence:**
  - Reproduced directly: with a shadow `certifi.where()` returning a nonexistent path, `import requests` **succeeds** against the merge-base package tree and **fails** with `FileNotFoundError` against the head package tree, traceback bottoming out at `adapters.py:76`, inside `_preloaded_ssl_context.load_verify_locations(...)` — full transcript in §5.
  - `src/requests/certs.py` (head, unchanged by this diff) docstring: *"If you are packaging Requests, e.g., for a Linux distribution or a managed environment, you can change the definition of where() to return a separately packaged CA bundle."* — establishes that a broken/overridden default path is a real, repository-documented scenario, not a hypothetical.
  - `git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py:286-300` (merge-base `cert_verify`) — the equivalent failure was deferred to the first `verify=True` HTTPS `send()`, and raised as a friendly `requests`-specific `OSError` ("Could not find a suitable TLS CA certificate bundle...") rather than an unguarded exception at import.
  - Review-record check under gate 6 (unintentional): sigmavirus24's 2024-05-05T14:54:54Z comment (packet §6, non-review conversation #9) says *"I see that the PR was updated and moved the extraction. I think the last blocker is the context being 'public'..."* — addressing the *placement* of `extract_zipped_paths()` for zip/pyinstaller packaging, not the fact that the resulting `load_verify_locations()` call now executes unconditionally at import. The review record never discusses import-time failure.
- **Trigger scenario (concrete):** A frozen/zipapp or distro-managed deployment where `certs.where()` is overridden (per `certs.py`'s own documented extension point) to a path that is not present in a particular build; at merge-base, `import requests; requests.get(url, verify=False)` still works. At head, the bare `import requests` already raises before any request is made.

## 3. Complete private disposition ledger

| id | kind | disposition | decisive evidence | falsification reason | verifier ruling |
| --- | --- | --- | --- | --- | --- |
| `C1` = `ssl-context-sharing/client-cert-mtls-leak` | concurrency | **survivor** | `src/requests/adapters.py:75-78,94-95,102-108` + `.../urllib3/util/ssl_.py:403-429` (venv) | passed all 8 falsification steps (see §2) | `confirmed` (verifier widened `trigger`/`impact` to a stronger sequential-only case and relocated `fix` to `:94-107` — see §4) |
| `C2` = `adapters/eager-ca-bundle-import-crash` | bug | **survivor** | `src/requests/adapters.py:75-78`; repro transcript §5 | passed all 8 falsification steps (see §2) | `confirmed` (verifier added a corroborating impact detail — see §4) |
| `D1` = "a connection object reused across requests could retain stale `ca_certs`/`ca_cert_dir` state from a prior `verify` setting because `cert_verify()` no longer always sets them" | concurrency | dropped (refuted) | `/private/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/poolmanager.py` `PoolKey._fields` (includes `key_ca_certs`, `key_ca_cert_dir`, `key_ssl_context`); `.../connectionpool.py:1034-1035` | Every distinct `verify` value (bool vs. str vs. str-dir) produces a distinct pool key (`ca_certs`/`ca_cert_dir`/`ssl_context` differ), so a different `verify` setting always draws a connection from a different `HTTPSConnectionPool`/different connection instance; no attribute carries over between them. Traced and confirmed via `poolmanager.py`/`connectionpool.py`. | `holds` (related-acquittal; verifier cited `PoolKey._fields` independently, see §4) |
| `D2` = "the new `os.path.isdir()` branch added to `_urllib3_request_context()` for `verify=<dir>` introduces a divergence from `cert_verify()`'s handling of directory CA paths" | bug | dropped (refuted — this is a fix, not a regression) | `git show <merge-base>:src/requests/adapters.py:89` (`pool_kwargs["ca_certs"] = verify`, no isdir check) vs. head `adapters.py:96-99` (isdir check added, now matching `cert_verify()`'s own long-standing isdir branch at head `adapters.py:314-317`) | At merge-base, `_urllib3_request_context()` always used the `ca_certs` pool-key field even when `verify` was a directory (mismatched with `cert_verify()`'s correct `ca_cert_dir` handling); this diff *removes* that pre-existing mismatch rather than introducing one. Not introduced-here; not a defect at all. | `holds` (related-acquittal) |
| `D3` = "moving `conn.cert_reqs = \"CERT_REQUIRED\"` earlier in `cert_verify()` (before the path-existence check) could leave a discarded connection object mutated before the `OSError` is raised, corrupting later reuse" | bug | dropped (consequence unproven / refuted) | merge-base `adapters.py:302` (`conn.cert_reqs = "CERT_REQUIRED"`, after the `OSError` check) vs. head `adapters.py:298` (same assignment, same literal value, before the check) | The assigned value (`"CERT_REQUIRED"`) is identical in both orderings — the write is idempotent regardless of when it executes relative to the exception. No path was found by which the reordering changes any observable connection state; the OSError propagates uncaught either way and no reuse of that specific connection object across differing `cert_reqs` was established. | `holds` (related-acquittal) |
| `D4` = "the isdir check in `_urllib3_request_context()` (head `adapters.py:96-99`) duplicates the isdir check already performed in `cert_verify()` (head `adapters.py:314-317`); the same decision is computed twice per request" | maintainability | dropped → **published as Observation** | head `adapters.py:96-99` and `adapters.py:314-317` | Fails the finding gate on proven/meaningful consequence (gate 1/4): both computations agree in every case I traced (both operate on the same `verify` string), so there is no correctness drift, only redundant computation. Routed to `Observations` under the rubric's "fails admission specifically on... consequence" rule. | not ruled — `kind=maintainability` is outside the four kinds (`bug`, `concurrency`, `invariant`, `security`) that `SKILL.md`'s related-acquittal mode carries to the verifier; `references/verifier.md`'s reduced one-citation check for `maintainability`/`performance`/`requirement` rows is likewise reserved for zero-survivor clean-verdict batches, which did not apply here (candidates survived). Ruled entirely by me as the primary reviewer. |

Every row's disposition and decisive evidence were fixed **before** any sub-agent was dispatched, per `SKILL.md`'s "Write the private record once per phase... the candidate ledger with every disposition at the end of falsification" and the run's rule 6 ("Persist before you verify"). This ledger was written to this report file prior to dispatching the verifier batch in §4.

## 4. Sub-agent dispatch — verifier batch (candidate mode + related-acquittal mode)

**Why one batch, both modes:** `SKILL.md`: *"when the initial candidate batch is dispatched, include in that same batch every non-survivor ledger row that is related to a survivor... This adds no second context and no second batch."* `D1`, `D2`, `D3` are all `kind=bug`/`concurrency` with decisive evidence in `src/requests/adapters.py`, the same file as both survivors' anchors — condition (a) of the related-acquittal test. `D4` is `kind=maintainability`, outside the four qualifying kinds, so it was excluded and never sent to the verifier (see the ledger table above for the exact rule that excluded it).

**Isolation:** Dispatched via the `Agent` tool, `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false`, with no prior conversation content — a fresh context per `references/verifier.md`'s isolation requirement. The prompt below is exactly what I composed per `references/verifier.md`'s "For candidate mode, give the verifier only..." list, plus the related-acquittal compact rows.

**Exact prompt sent:**

~~~text
You are an independent verifier for a code review of psf/requests#6667 (a merged,
retrospective, non-publishing review). Follow these binding rules:

1. OFFLINE. No git fetch/pull, no gh, no curl, no network of any kind. The clone's
   origin is a local filesystem path.
2. Focused pytest execution IS permitted, offline only: from the clone root,
   PYTHONPATH=<clone>/src /tmp/qual137/venvs/requests/bin/python -m pytest <selection>,
   5 minutes per command, a selection at most once per flag set, scratch files only
   under /tmp/qual137/work/i-867cf3ff-seed2-att-03/verifier-scratch/ (already created),
   nothing added to or changed in the clone.
3. Do NOT run git checkout / git switch / git reset / git stash or anything that
   mutates the tree. If you find the tree mutated anyway, run
   `git -C /tmp/qual137/runs/i-867cf3ff-seed2-att-03 reset --hard review-head` and
   report that you had to.
4. Stay inside: the clone at /tmp/qual137/runs/i-867cf3ff-seed2-att-03, the skill
   snapshot at /tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/, and your
   own scratch directory above. If you need to read the pinned virtualenv's installed
   urllib3 dependency at /tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/
   to independently check a claim about urllib3's own behavior, you may — it is the
   run's pre-provisioned dependency named in the execution allowance — but explicitly
   report that you read it. Report any other path you read.
5. History is truncated at the pinned head 4089f3dc65f783beaa53cc032958ab625440d0ac.
   Do not try to look beyond it. Report which history commands, if any, you ran.
6. You are a fact-checker, not a second reviewer: do not search for new findings,
   do not write to the pull request (you have no such access anyway), do not
   produce publication-ready prose. Read references/verifier.md in the skill
   snapshot directory now, in full, and follow its "Verification task",
   "Verdicts", and "Clean-verdict task" sections exactly (you are being given both
   a candidate-mode batch and a related-acquittal-mode set of rows in the same
   dispatch, which that file explicitly anticipates).
7. No session relays: finish this dispatch yourself; do not ask anyone anything.

Repository coordinates: psf/requests, base ref `main` pinned to merge-base
8dd3b26bf59808de24fd654699f592abf6de581e, head 4089f3dc65f783beaa53cc032958ab625440d0ac.
No originating issue is linked to this PR (issues=none). No repository-rule files
(AGENTS.md/CLAUDE.md/CONTEXT.md) exist at the merge-base for the changed path.

Ranges to read in one message for both candidates (from scripts/review_context.py):
  src/requests/adapters.py:26-32 @head / :26-31 @merge-base
  src/requests/adapters.py:72-115 @head / :71-104 @merge-base
  src/requests/adapters.py:148-616 @head / :137-606 @merge-base

=== CANDIDATE C1 ===
id: ssl-context-sharing/client-cert-mtls-leak
kind: concurrency
priority: P1
action: must-fix
anchor: {type: line, path: src/requests/adapters.py, start_line: 94, end_line: 95, side: RIGHT}
fix: src/requests/adapters.py:75
title: Do not share the preloaded SSLContext with connections that also set a client certificate or hostname override
claim: `_preloaded_ssl_context` (a single process-wide ssl.SSLContext created once at
  import, src/requests/adapters.py:75-78) is handed unconditionally into
  pool_kwargs["ssl_context"] whenever verify is True (adapters.py:94-95), including
  requests that also supply a client certificate via the `cert=` parameter
  (client_cert is folded into the same pool_kwargs dict at adapters.py:102-108,
  unconditionally). urllib3's connection/ssl_ code (installed in the pinned venv at
  urllib3/connection.py and urllib3/util/ssl_.py) mutates the *same* passed-in
  ssl_context object in place on every connect(): `context.verify_mode = ...`,
  conditionally `context.check_hostname = False`, and — whenever a client cert is
  present — unconditionally `context.load_cert_chain(certfile, keyfile)`. Because the
  object is shared across every verify=True pool/host/thread in the process, one
  connection's client-certificate identity or hostname-check setting can leak into a
  different, concurrent or later, connection that shares the same context object. At
  the merge-base, ssl_context was never set for verify=True, so urllib3 built a fresh,
  connection-private context on every single connect() (ssl_context is None branch);
  this diff removed that per-connection isolation guarantee.
trigger: Two Session.get()/request() calls with verify=True (the default) to two
  different hosts, each supplying a different cert=(certfile, keyfile) client
  certificate, running concurrently on different threads, or sequentially whenever
  the pool for the first host later opens a new physical connection after the second
  host's load_cert_chain() call has already run on the shared context.
impact: The connection to host A can present host B's client certificate (or vice
  versa) during the TLS handshake — a cross-request client-identity/authentication
  leak — and separately, any pool that disables hostname checking
  (assert_hostname=False/assert_fingerprint via custom pool_kwargs) turns hostname
  verification off for every other concurrent verify=True connection in the process,
  because check_hostname lives on the same shared object.
change: Do not hand the same live, mutable SSLContext to a connection pool that also
  carries a client certificate or a hostname-check override. Build a private,
  connection-scoped context in those cases (the pre-diff behavior), and reserve the
  shared, pre-loaded context strictly for the plain "verify=True, no client cert, no
  hostname override" case.
evidence:
  - src/requests/adapters.py:75-78 (module-level singleton creation)
  - src/requests/adapters.py:94-95 (unconditional assignment into pool_kwargs for
    every verify=True request)
  - src/requests/adapters.py:102-108 (client_cert folded into the same pool_kwargs,
    unconditionally, regardless of ssl_context)
  - <merge-base>:src/requests/adapters.py:75-90 (no ssl_context key ever set for
    verify=True at merge-base)
  - urllib3/connection.py:925-936 in the pinned venv
    (/private/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/connection.py) —
    `if ssl_context is None: default_ssl_context = True; context =
    create_urllib3_context(...)`, i.e. a fresh context per connect() when
    ssl_context is not supplied
  - urllib3/connection.py:935,960-985 (same file) — `context = ssl_context` (no copy);
    `context.verify_mode = ...`; `context.check_hostname = False` under some
    conditions
  - urllib3/util/ssl_.py:403-429 (same venv) — `context = ssl_context` (no copy);
    `if certfile: context.load_cert_chain(certfile, keyfile)`
requirement_source: none (no linked issue; this is a Code candidate under the
  rubric's introduced-here gate)

=== CANDIDATE C2 ===
id: adapters/eager-ca-bundle-import-crash
kind: bug
priority: P1
action: must-fix
anchor: {type: line, path: src/requests/adapters.py, start_line: 75, end_line: 78, side: RIGHT}
title: Do not load the default CA bundle unconditionally at import time
claim: `_preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))`
  (adapters.py:75-78) executes at module-import time (import requests -> api.py ->
  sessions.py -> adapters.py), rather than lazily on first verify=True HTTPS request
  as at the merge-base (merge-base cert_verify(), adapters.py:286-300, which raised a
  friendly requests.exceptions-adjacent OSError only when a verify=True request was
  actually made with no override). Any environment where DEFAULT_CA_BUNDLE_PATH
  (certifi.where(), or a distro/managed override of requests.certs.where() — a
  customization certs.py's own docstring documents as supported) resolves to a
  missing or unreadable file now makes bare `import requests` raise unconditionally,
  even for callers who only ever use verify=False or a custom CA bundle path.
trigger: DEFAULT_CA_BUNDLE_PATH points at a path that does not exist or cannot be
  parsed as a CA bundle at the moment adapters.py is first imported.
impact: `import requests` raises (FileNotFoundError/ssl.SSLError) and the library
  becomes completely unusable in that process, including for code paths that never
  needed the default bundle. At merge-base the same broken bundle only broke the
  specific request that exercised verify=True with no override.
change: Defer the CA-bundle load until first actual need (build the context lazily
  on first verify=True use, or guard the module-level load so a broken default
  bundle cannot prevent import, only prevent implicit verify=True use), matching the
  merge-base's lazy-failure behavior.
evidence:
  - src/requests/adapters.py:75-78 (head)
  - src/requests/certs.py (head, unchanged by this diff) docstring: "If you are
    packaging Requests, e.g., for a Linux distribution or a managed environment, you
    can change the definition of where() to return a separately packaged CA bundle."
  - <merge-base>:src/requests/adapters.py:286-300 (lazy, friendly OSError at
    request time instead of eager crash at import time)
requirement_source: none (no linked issue; this is a Code candidate under the
  rubric's introduced-here gate)

=== RELATED NON-SURVIVOR ROWS (related-acquittal mode; rule with each) ===
D1: claim="a connection reused across requests with different `verify` settings could
  retain stale `ca_certs`/`ca_cert_dir` state because `cert_verify()` no longer
  always sets them for verify=True" kind=concurrency disposition=refuted
  falsification="every distinct verify value produces a distinct urllib3 pool key
  (ca_certs/ca_cert_dir/ssl_context differ), so a different verify value always
  draws from a different HTTPSConnectionPool/connection instance; no attribute
  carries over" decisive_evidence=src/requests/adapters.py:94-99

D2: claim="the new os.path.isdir() branch added to _urllib3_request_context() for a
  directory verify path introduces a divergence from cert_verify()'s handling of
  directory CA paths" kind=bug disposition=refuted
  falsification="at merge-base, _urllib3_request_context() always used the ca_certs
  pool-key field even for a directory verify value (mismatched with cert_verify()'s
  correct ca_cert_dir handling); this diff removes that pre-existing mismatch rather
  than introducing one" decisive_evidence=src/requests/adapters.py:96-99

D3: claim="moving `conn.cert_reqs = \"CERT_REQUIRED\"` earlier in cert_verify()
  (before the path-existence check) could leave a discarded connection mutated
  before the OSError is raised, corrupting later reuse" kind=bug disposition=refuted
  falsification="the assigned value is identical (\"CERT_REQUIRED\") in both
  orderings; the write is idempotent regardless of sequence relative to the
  exception, and the exception propagates uncaught either way"
  decisive_evidence=src/requests/adapters.py:298

For each of C1 and C2, return `confirmed` or `refuted` with justification, decisive
citations, and any correction to trigger/impact/priority/action/anchor/fix/change,
per verifier.md's Verdicts section, including the full concurrency bug-class
procedure (state the invariant at rule level, sibling interleavings, sibling code
paths, widen `change` if needed) for C1 since kind=concurrency. For D1/D2/D3, return
`holds` or `re-open` per the clean-verdict task's related-acquittal mode, at full
attack depth (their kind is bug/concurrency, not the reduced one-citation kinds).
Also flag any observation aside per verifier.md's rules if you notice one, with no
`should`/`must` language.

Report explicitly: which paths you read (including whether you read the pinned venv's
urllib3 source and why), which git history commands you ran (if any), whether you ran
any pytest selection (command, exit status, duration, output summary), and whether the
clone tree was mutated by you (it must not be).
~~~

**Verbatim report returned by the verifier** (this is the actual output of the `Agent` dispatch, `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false`; agent id `adbf35ad795f91a6f`; `subagent_tokens: 83271`, `tool_uses: 27`, `duration_ms: 379201` per the harness's own usage report on that call):

~~~text
## Verification Report

### Isolation & scope compliance
Fresh, isolated context; no network, no git fetch/pull/gh/curl; no clone mutation; no `git checkout/switch/reset/stash`. All work stayed inside the clone at `/tmp/qual137/runs/i-867cf3ff-seed2-att-03`, the skill snapshot, the pinned venv's urllib3 source, and my scratch dir (unused — no files written).

**Paths read:**
- `.../skills/code-review-publish/references/verifier.md` (full)
- `src/requests/adapters.py` @head — ranges 1–120, 148–616, and precise re-reads of 73–112 (`_urllib3_request_context`) and 285–320 (`cert_verify`)
- `src/requests/adapters.py` @merge-base (`git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py`) — full head section (1–120) and `cert_verify` (274–320)
- `src/requests/certs.py`, `src/requests/utils.py` (`DEFAULT_CA_BUNDLE_PATH`, `extract_zipped_paths`)
- `src/requests/__init__.py`, `src/requests/sessions.py` (import-chain grep only)
- `HISTORY.md` (checked for any documented rationale — none found for either change)
- **Pinned venv urllib3 source**, read specifically to independently verify C1's and the D-row falsification's claims about urllib3's own runtime behavior (the run's pre-provisioned dependency named in the execution allowance): `urllib3/connection.py` (HTTPSConnection `__init__`/`connect`, and `_ssl_wrap_socket_and_match_hostname`, ~lines 600–1010), `urllib3/util/ssl_.py` (`ssl_wrap_socket`, ~328–430), `urllib3/poolmanager.py` (`PoolKey`, `SSL_KEYWORDS`, `_default_key_normalizer`, ~1–140).

**Git history commands run** (all local, bounded at pinned head, no fetch):
`git log --oneline -1 HEAD`; `git log --oneline -1 <merge-base> -- adapters.py`; `git log --oneline -- adapters.py`; `git log --all --oneline -- adapters.py`; `git show 8f954567/ec0e33b3/c0813a2d -s --format=%B` (and `--stat` for 8f954567); `git show <merge-base>:src/requests/adapters.py`; `git status --porcelain` / `--porcelain --ignored`.

**Pytest:** none run. Static evidence (head vs. merge-base diff plus pinned urllib3 source) was decisive for both candidates without needing execution; well-established stdlib semantics of `ssl.SSLContext.load_verify_locations`/`load_cert_chain` (raise on bad path; mutate in place) were relied on as documented facts, not asserted via a run.

**Clone mutation:** none. `git status --porcelain` was empty; `--ignored` showed only pre-existing gitignored `__pycache__`/`.pytest_cache` artifacts that predate this session (I ran no Python/pytest that would produce them).

---

### C1 — ssl-context-sharing/client-cert-mtls-leak — **confirmed**

Decisive citations:
- `src/requests/adapters.py:94-95` (head): `elif verify is True: pool_kwargs["ssl_context"] = _preloaded_ssl_context` — unconditional.
- `src/requests/adapters.py:75-78` (head): singleton built once at import.
- `src/requests/adapters.py:102-107` (head, exact lines for client_cert): `pool_kwargs["cert_file"]/["key_file"]` set unconditionally whenever `cert=` is supplied, with no interaction/exclusion against the `ssl_context` key set above.
- Merge-base `_urllib3_request_context` (`git show <merge-base>:adapters.py:80-89`): no `ssl_context` key ever set for `verify=True` — confirms this is introduced-here, not pre-existing.
- Pinned urllib3 `connection.py:925-936,935,960-985` and `util/ssl_.py:403-429`: verified directly — `context = ssl_context` with **no copy**; `context.verify_mode = ...` always; `context.check_hostname = False` conditionally; `if certfile: context.load_cert_chain(certfile, keyfile)` **unconditionally whenever a cert_file is set on that connection**. `poolmanager.py:54-83` (`PoolKey` fields) confirms pools are keyed by object identity of `ssl_context`, not a copy — sharing the reference means literal shared mutable state across every pool, host, and thread that used `verify=True`.

**Concurrency bug-class procedure (kind=concurrency), as required:**

1. **Invariant at rule level:** *The TLS parameters actually applied by a connection's SSLContext (verify_mode, check_hostname, loaded client-certificate chain) must never be observable by any other connection that did not request them.* At merge-base this held because every `verify=True` connect() built a private, per-connection `SSLContext` (`ssl_context is None` branch, `connection.py:926-934`).
2. **Does it require shutdown/teardown/error path?** No. This is a steady-state bug: normal, ordinary requests, no error path required.
3. **Sibling interleavings (steady state), before code paths, as required:**
   - *Concurrent cert-A vs cert-B connect():* two threads opening new physical connections for different hosts, each with its own `cert=`, race to call `context.load_cert_chain()` on the same object — data race plus last-writer-wins client-identity confusion. Confirmed reachable via `connection.py:809/878` → `connection.py:984` → `ssl_.py:425-429`.
   - *Sequential, single-threaded, no concurrency required at all (a wider and more damning trigger than the candidate stated):* Request 1 uses `cert=(A_cert, A_key)` to host A → mutates the shared singleton's chain permanently. Request 2, **with no `cert=` at all**, to a different host B that must open a new connection, still receives `pool_kwargs["ssl_context"] = _preloaded_ssl_context` (the same, now-contaminated, object) and never calls `load_cert_chain` again (since its own `cert_file` is `None`) — but the *previously loaded* client certificate from host A remains active on the shared context and gets presented to host B's server. This is a **persistent, one-directional contamination**, not merely a race: it requires exactly one prior `cert=` use anywhere in the process, ever, followed by any later plain `verify=True` connection-open to any other host.
   - *Hostname-check override sibling:* a pool built with `assert_hostname=False`/`assert_fingerprint` (reachable only via a subclassed `HTTPAdapter` supplying custom `pool_kwargs`, not through the stock `verify=`/`cert=` API) sets `context.check_hostname = False` on the same shared object, disabling hostname verification for every other concurrent `verify=True` pool in the process. Narrower attack surface than the client-cert leak (no first-class requests parameter reaches it), but real.
4. **Sibling code paths and whether `change` protects them:** the *plain* `verify=True`, no cert, no override path is safe on its own (idempotent `verify_mode` write, same constant every time) — it is only unsafe as the *victim* of contamination from the cert/override paths above.
5. **Widening `change`:** the candidate's proposed change ("don't hand the shared context to a pool that also carries a client cert or hostname override; build a private context in those cases") already covers the full rule, including the sequential/persistent-contamination trigger, not just the concurrent one — because it prevents `load_cert_chain`/`check_hostname=False` from ever touching the shared singleton at all. **Correction:** widen `trigger`/`impact` prose to state the simpler, single-threaded, single-`cert=`-use trigger as the dominant/easier-to-hit case (it needs no concurrency and no second client cert — just one prior `cert=` request anywhere in the process followed by any later plain request to a different host).

**Correction to `fix` anchor:** `src/requests/adapters.py:75` (the singleton's *creation* line) is not itself the right edit site — line 75 can stay unchanged since the shared context is still valid for the safe case. The actual decision logic that needs to change is the `elif verify is True:` branch and its interaction with the `client_cert is not None` block, i.e. `src/requests/adapters.py:94-107`.

No evidence in `HISTORY.md`, commit messages (`8f954567`, `f21e70bf`), or the clone that this sharing was a deliberate, discussed tradeoff — the "dev" `HISTORY.md` section is a placeholder, and no test references `_preloaded_ssl_context`. Priority/action (P1/must-fix) unchanged, if anything undersells how trivially the persistent-contamination variant reproduces.

---

### C2 — adapters/eager-ca-bundle-import-crash — **confirmed**

Decisive citations:
- `src/requests/adapters.py:75-78` (head): `_preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))` at module scope, no `try/except`.
- Import chain traced directly: `src/requests/__init__.py:174` (`from .sessions import ...`) → `src/requests/sessions.py:15` (`from .adapters import HTTPAdapter`) → executes `adapters.py` module body unconditionally on `import requests`.
- `src/requests/utils.py:63`: `DEFAULT_CA_BUNDLE_PATH = certs.where()`; `src/requests/certs.py` docstring explicitly documents that packagers/managed environments are expected to override `where()` — confirming the customization vector the claim relies on is a supported one, not hypothetical.
- `src/requests/utils.py:268-289` (`extract_zipped_paths`): confirmed it returns a nonexistent, non-zip-member path **unchanged** rather than raising or substituting — so a bad `DEFAULT_CA_BUNDLE_PATH` reaches `load_verify_locations` verbatim, which (documented stdlib `ssl.SSLContext` behavior) raises `FileNotFoundError`/`ssl.SSLError` on a missing/unparseable file.
- Merge-base `cert_verify` (`git show <merge-base>:adapters.py:286-300`): confirmed lazy — the equivalent `OSError` only fires inside a `verify=True` HTTPS request, never at import.
- Commit `8f954567` ("Use a default SSLContext with the default CA bundle loaded when `verify=True`", `git show 8f954567 --stat`: 10 insertions/2 deletions in `adapters.py`) is exactly where this eager load was introduced — confirms introduced-here, not pre-existing.

No `HISTORY.md` entry or commit-message rationale documents this as an accepted tradeoff.

**Correction (fold into `impact`, not a separate finding):** because the context is built once at import and never rebuilt, a documented workaround — monkeypatching `requests.utils.DEFAULT_CA_BUNDLE_PATH` (or `certs.where()`) at runtime after `import requests` — which worked at merge-base (read fresh on every request), is now silently ineffective for `verify=True` traffic, since the baked-in path can never be changed post-import. Priority/action (P1/must-fix), anchor (75-78), and `change` are otherwise accurate as stated.

---

### D1 — pool reused across different `verify` settings — **holds**

Premise: distinct `verify` values always yield distinct urllib3 pool keys, so no attribute state carries over between them. Verified directly against `poolmanager.py`'s `PoolKey` namedtuple (includes `key_ssl_context`, `key_ca_certs`, `key_ca_cert_dir`, `key_cert_reqs`, etc., `poolmanager.py:54-83`) and `_default_key_normalizer`'s default-`None`-for-missing-field behavior (`poolmanager.py:~136-140`, not cited by the ledger row). Attacked the opposite branches: `verify=True` (sets `ssl_context`, no `ca_certs`) vs. `verify=<str>` (sets `ca_certs`/`ca_cert_dir`, no `ssl_context`) vs. `verify=False` (neither, distinct `cert_reqs`) vs. `verify=None` (neither key set at all) — every pairing differs in at least one `PoolKey` field, so no collision/reuse is constructible. `cert_verify()` mutates the pool object (`adapters.py:94-99` in head, matches ledger), but that pool is only ever reachable again by a request producing the identical `pool_kwargs`. **Disposition holds** (no re-open). Additional citation beyond the ledger's: `poolmanager.py:54-83` (PoolKey fields) and `~136-140` (default-None normalization).

### D2 — new `os.path.isdir()` branch diverges from `cert_verify` — **holds**

Directly compared merge-base and head: merge-base `_urllib3_request_context` (`git show <merge-base>:adapters.py:83-84`) always set `pool_kwargs["ca_certs"] = verify` for *any* string `verify`, including directories — a pre-existing mismatch against merge-base `cert_verify`'s correct isdir branching (`<merge-base>:296-307`). Head's new isdir branch (`adapters.py:96-99`) matches head `cert_verify`'s identical isdir branch (`adapters.py:314-317`, not cited by the ledger row) exactly — the diff **removes** the old mismatch rather than introducing a new one. No divergence constructible at head. **Disposition holds.**

### D3 — earlier `conn.cert_reqs = "CERT_REQUIRED"` corrupts a discarded connection — **holds**

Verified the assigned value is the literal constant `"CERT_REQUIRED"` in both merge-base (`<merge-base>:adapters.py:302`, after the check — not cited by the ledger row) and head (`adapters.py:298`, before the check) orderings — an idempotent write. Traced the failing branch: the `OSError` propagates uncaught in both orderings (no swallow anywhere in `send()`), so the request that hit the bad path always aborts before `urlopen()`; the pool object is not reused with mismatched intent because (per D1) any request that could reuse the same pool object necessarily has the identical `verify` config and therefore wants the identical `cert_reqs` value anyway. Considered a concurrent-race variant (two threads hitting the same bad path concurrently) — both would independently raise the same error; no corrupted intermediate state is observable by a third party. No failing transition constructible. **Disposition holds.**

---

### Observation aside
None meeting the bar independently of C1/C2's own corrections above (the one incidental fact I found — runtime monkeypatching of `DEFAULT_CA_BUNDLE_PATH` becoming ineffective — was folded into C2's `impact` correction rather than raised separately, since it doesn't contradict any ledger row and is the same root artifact C2 already cites).

### Duplicates
C1 and C2 touch the same singleton object (`_preloaded_ssl_context`, `adapters.py:75-78`) but are not duplicates: they are independently falsifiable (mutation-sharing vs. eager-crash-at-import) with different triggers, impacts, and fixes. Note for the primary reviewer: a single redesign — build the SSLContext lazily, on first actual `verify=True` need, one per safe/shareable configuration — would resolve both simultaneously, but they should remain separate findings.
~~~

**Primary reviewer's handling of the verifier's return:** Both candidates came back `confirmed`, each with a correction I adopted:
- **`C1`:** the verifier found a *stronger, simpler* trigger than my original draft — no concurrency is even required. One prior `cert=` request anywhere in the process, followed by *any* later plain `verify=True` request (no `cert=` at all) to a *different* host that opens a new physical connection, is enough: the shared context keeps presenting the first host's client certificate to the second host forever after. I rewrote Finding 1's `Trigger`/`Impact` in §2 to lead with this simpler, single-threaded case and keep the concurrent race as an additional variant. The verifier also corrected `fix` from `adapters.py:75` (the harmless singleton-creation line) to `adapters.py:94-107` (the `elif verify is True:`/`client_cert` interaction that actually needs to change) — adopted in §2.
- **`C2`:** the verifier added one corroborating consequence I folded into `Impact`: because the context is now built once, at import, a previously-effective workaround (monkeypatching `requests.utils.DEFAULT_CA_BUNDLE_PATH` after import to point at a working bundle) is now silently ineffective for `verify=True` traffic, since nothing ever re-reads it. Adopted in §2.
- Priority/action (`P1`/`must-fix`) were left unchanged for both; the verifier explicitly agreed with both, and for `C1` said the original priority "if anything undersells" the bug.

All three related rows (`D1`, `D2`, `D3`) came back `holds`; none re-opened, so no follow-up batch was needed (`SKILL.md`: "After the initial candidate or clean-verdict batch is dispatched, collect any candidate that newly reaches render eligibility... Run at most one fresh follow-up batch... A row re-opened in either mode re-enters primary falsification"). Since nothing re-opened, the one permitted follow-up batch was not used.

## 5. Everything consulted beyond the diff

**Files read (all as bounded ranges except where noted):**
- `src/requests/adapters.py` — full diff via `review_context.py --merge-base 8dd3b26bf59808de24fd654699f592abf6de581e --head 4089f3dc65f783beaa53cc032958ab625440d0ac` (one call, `--function-context` widened the third hunk to the entire `HTTPAdapter` class body, lines 148-616 @head / 137-606 @merge-base, because Python's diff driver has no method-level `xfuncname` pattern here and treats the class as the enclosing symbol; per `review-rubric.md`'s "Complete inspection" rule I did not re-read this range separately since the diff output already printed it in full).
- `src/requests/certs.py` (head) — read whole (10 lines, under the 300-line whole-file threshold) to check the CA-bundle-override documentation cited in Finding 2.
- `src/requests/utils.py` (head) — read the `DEFAULT_CA_BUNDLE_PATH = certs.where()` definition (grep + 1-line context) to establish it is a cheap, unchanged, import-time string computation, distinct from the new eager *load*.
- `git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py` — full file, to compare `_urllib3_request_context` and `cert_verify` at the merge-base against the head versions cited above (candidate falsification step 4/8).
- `tests/test_requests.py` — grepped for `cert`/`verify`/`ssl`/`cert=` definitions (batched search, not per-file, repo-scoped to this one file since it's the only test file referencing adapters.py behavior per the earlier grep) to find existing coverage; read the bodies of `test_different_connection_pool_for_mtls_settings` (lines 2929-2966) and its neighbors.
- `tests/testserver/server.py` — grepped for `ssl_context`/`load_cert_chain`/`load_verify_locations` to confirm no test exercises the shared-context/client-cert scenario.
- `/private/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/connectionpool.py` (installed dependency, read to decide Finding/Ledger evidence) — `HTTPSConnectionPool.__init__` (lines 992-1037) and `_new_conn` (lines 1051-1077).
- `/private/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/connection.py` — `HTTPSConnection.__init__`/`connect()`/`_ssl_wrap_socket_and_match_hostname` (lines 621-1010 region, read in the ranges shown by grep + targeted `sed` windows).
- `/private/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/util/ssl_.py` — `ssl_wrap_socket` (lines 328-430).
- `/private/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/poolmanager.py` — `PoolKey._fields` (one `python3 -c` introspection).

All of the `urllib3` reads above are outside the reviewed repository proper (they are the pinned venv's installed dependency, provided by the run environment for the permitted focused-test execution, not the clone or skill snapshot or packet directory). I am disclosing them per rule 7/§9 below as reads outside the strictly-listed sandbox list (clone, skill snapshot, packet directory, work/report/payload paths); they were necessary to establish the decisive, falsifiable mechanism behind Findings 1 and the D1 acquittal (urllib3's own pool-keying and context-mutation behavior is exactly what the claims are about), and I judged reading the dependency that the reviewed code calls into to be squarely within "relevant callers, interfaces... each read as a bounded range" (`SKILL.md` step 3) rather than an out-of-scope excursion — see §10 for this judgment call.

**Searches (all batched, single-invocation; repo-scoped to the clone unless noted):**
- `grep -n "cert_verify\|_urllib3_request_context\|ssl_context\|_preloaded_ssl_context\|load_verify_locations" tests/` — case-sensitive, repo-wide over `tests/`, one call. No hits in `test_requests.py`; hits only in `testserver/server.py`.
- `grep -n "def test.*cert\|def test.*verify\|def test.*ssl\|cert=" tests/test_requests.py` — case-sensitive, single file, one call.
- `grep -n "_preloaded_ssl_context\|elif verify is True\|def _urllib3_request_context\|DEFAULT_CA_BUNDLE_PATH" src/requests/adapters.py` — case-sensitive, one call.
- `grep -n "ssl_context\|cert_file\|key_file\|def connect\|def __init__" .../urllib3/connection.py` and similar single-file greps against the installed venv package (not the reviewed repo) to locate exact line ranges before reading them as bounded `sed` windows.
- None of these searches needed case-insensitivity or a propagation/synchronization-drift sweep (`review-rubric.md`'s peer-set search applies to drift candidates; neither finding is a drift claim, so that specific sweep procedure was not triggered).

**Focused test/repro commands run (execution allowance, §8 of the packet):**
1. `PYTHONPATH=src /tmp/qual137/venvs/requests/bin/python -m pytest tests/test_requests.py -k "cert or ssl or verify" --collect-only -q` — exit 0, 0.3s, 17/329 collected.
2. `PYTHONPATH=src /tmp/qual137/venvs/requests/bin/python -m pytest tests/test_requests.py -k "cert or ssl or verify" -q` — exit 1, 2.09s, **16 passed, 1 failed** (`test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`, `SSLCertVerificationError: Missing Authority Key Identifier`).
3. Same selection against a `git archive`-extracted merge-base copy of `src/requests` (`PYTHONPATH=$WORK/pkg_base/src`) — exit 1, 0.67s, **identical failure**, confirming pre-existing/environmental (stale test-fixture cert incompatible with the pinned venv's modern OpenSSL 3.x strictness), not introduced by this diff.
4. `PYTHONPATH=src /tmp/qual137/venvs/requests/bin/python -m pytest tests/test_requests.py -q` (full file) — exit 1, 32.73s, **324 passed, 1 skipped, 1 xpassed, 3 failed**: the above plus `test_redirecting_to_bad_url[http://localhost:-1-InvalidURL]` and `test_different_connection_pool_for_mtls_settings`.
5. Both of those two additional failures reproduced identically against the merge-base copy (commands: `pytest tests/test_requests.py::TestPreparingURLs::test_redirecting_to_bad_url -q --tb=line` and `...::test_different_connection_pool_for_mtls_settings -q --tb=short`, each run once against head and once against `pkg_base`) — both pre-existing/environmental (a `werkzeug`/`urllib.parse` version incompatibility unrelated to `adapters.py`, and an expired-test-certificate handshake failure that occurs even on the very first `verify=False` call, before either candidate's code path is reachable). None of the 3 pre-existing failures are reported as findings; they gate nothing in this review since they reproduce identically at merge-base.
6. `git archive 8dd3b26bf59808de24fd654699f592abf6de581e -- src/requests | tar -x -C $WORK/pkg_base` and the equivalent for head — read-only export of tracked blobs into the work directory, not a clone mutation.
7. Repro script `repro_shared_context.py` (own scratch file, not pytest) — calls `requests.adapters._urllib3_request_context()` twice with two hosts/two client certs; printed `same ssl_context object across different hosts/certs? True` and `is module global: True`.
8. Repro scripts `test_import_base.py`/`test_import_head.py`/`test_import_head_tb.py` with a shadow `certifi` module returning a nonexistent path on `PYTHONPATH` — merge-base import succeeded, head import failed with `FileNotFoundError` at `adapters.py:76`.

Every selection above was run at most once per exact flag set, per the packet's execution allowance; no selection exceeded the 5-minute cap (longest was 32.73s); no clone file was added to or changed (all scratch files live under `/tmp/qual137/work/i-867cf3ff-seed2-att-03/`).

## 6. Context digest

Computed once via `python3 scripts/context_fingerprint.py` against:

```json
{
  "pr": {
    "title": "Avoid reloading root certificates to improve concurrent performance",
    "body": "<the PR body, verbatim, reproduced in the packet §3 — see /tmp/qual137/work/i-867cf3ff-seed2-att-03/pr_body.txt and .../context_input.json for the exact bytes fed to the script>"
  },
  "issues": [],
  "specs": [],
  "guidance": []
}
```

- `issues: []` — packet §4: "None. The pull-request body is the only statement of intent." Recorded as `issues=none` in the run trailer.
- `specs: []` — no user-supplied spec was provided in this dispatch.
- `guidance: []` — packet §7: no root or path-scoped `AGENTS.md`/`CLAUDE.md`, and no root `CONTEXT.md`, present at the merge-base for any changed path.
- `comments_available` — not applicable: no issues were linked, so no issue-comments field exists to mark available/unavailable. (The PR's own review-thread and non-review conversation are not "issue comments" under the digest's schema — that schema is specifically for `closingIssuesReferences[].comments`, which is empty here because there is no closing issue.)

**Result:** `context=c0867eb8665714e98853874c7a66087e62cdd24962072b2681554acf99349763`

## 7. Mechanism checklist

- **Question channel:** Did not fire. No candidate reached the static-unresolvability bar (`review-rubric.md`'s "Issue fit"/question rule) — both survivors were fully resolvable from code, the installed dependency, and the review record; no outcome-changing fact required a maintainer or a benchmark to settle.
- **Clean-verdict / related-acquittal verification:** Related-acquittal mode fired (not zero-survivor mode, since 2 candidates survived). Rows `D1`, `D2`, `D3` rode along with the candidate batch in §4; all three returned `holds`; no row was re-opened.
- **Observations:** Fired once. `D4` (duplicated `isdir` computation between `_urllib3_request_context` and `cert_verify`) failed the finding gate on consequence and was routed to `Observations` in the payload; it is the only observation, well under the 3-item cap.
- **Fix-sufficiency check on the concurrency candidate:** Fired for `C1` (`kind=concurrency`). The verifier performed the full bug-class procedure from `references/verifier.md`: stated the rule-level invariant, confirmed the bug is steady-state (no shutdown/teardown/error path needed), enumerated sibling interleavings — and in doing so found a *stronger, simpler* one than I had drafted (a purely sequential, single-threaded trigger needing only one prior `cert=` request anywhere in the process, no second thread and no second client cert), plus the concurrent race and the hostname-override sibling — enumerated the sibling code path (plain `verify=True`/no-cert/no-override, safe on its own), and explicitly checked whether `change` needed widening to cover the newly-found sequential case. It concluded `change` already covered it (since it removes sharing for *any* client-cert/override connection, regardless of concurrency), so no widening of `change` itself was needed — only `trigger`/`impact`/`fix` were corrected, all adopted in §2.
- **Follow-up verifier round:** Did not fire. No row was re-opened by the initial batch, so the one permitted follow-up batch was never used.
- **Deferral handling:** No explicit deferral (e.g. "we can fix this during API review", "let's revisit later") appears anywhere in the packet's reproduced review record. This mechanism did not fire; I did not treat any prior-review item as an "open" deferred question because none exists.
- **Retrospective mode:** Fired. The packet pins `state=MERGED`, `merged=true`. `SKILL.md` step 1: "A merged pull request is reviewable only when invoked as a retrospective or audit review; disable publication..." Publication was disabled throughout; the summary body below carries the mandatory `Mode` line for a merged target (`publication disabled` variant, since no separate authorization was given).
- **Early dispatch of the verifier batch relative to the falsification pass:** `SKILL.md` does not define an "early dispatch" mechanism distinct from the ordinary "run one initial candidate batch... When at least one candidate qualifies" rule; I found no separate early-dispatch clause to check against, so this sub-item is reported as **not defined by this skill** rather than "did not fire". The verifier batch was dispatched only after the complete candidate ledger (§3) was finalized and persisted to this report, i.e. after — not concurrently with or before — the falsification pass completed, per the "Write the private record once per phase... at the end of falsification" instruction.

## 8. History discipline

I read history **only** at or before the pinned head, never beyond it:
- `git log --oneline -5 main` and `git log --oneline -5 review-head` (initial orientation; both logs bottom out at/around `8dd3b26b`, the pinned merge-base, and top out at `4089f3dc6`, the pinned head — nothing past either).
- `git branch -a`, `git status` (clone hygiene checks, not history).
- `python3 scripts/review_context.py --merge-base 8dd3b26bf59808de24fd654699f592abf6de581e --head 4089f3dc65f783beaa53cc032958ab625440d0ac` — its `## history` section itself reports only pre-merge-base commits that touched `src/requests/adapters.py` (`a94e9b53`, `c0813a2d`, `60389df6`, all dated before or at the merge-base window), which is the tool's documented "pre-merge-base history" output, not a walk past the head.
- `git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py` (twice, plus once for `certs.py`/`utils.py` context) — reading a single pinned blob at the merge-base SHA, not traversing history.
- `git archive 8dd3b26bf59808de24fd654699f592abf6de581e -- src/requests` and `git archive 4089f3dc65f783beaa53cc032958ab625440d0ac -- src/requests` — exporting tracked blobs at the two pinned SHAs into scratch directories for the import-crash repro; again single-SHA reads, not a history walk.

The verifier sub-agent ran, by its own verbatim report: `git log --oneline -1 HEAD`; `git log --oneline -1 <merge-base> -- adapters.py`; `git log --oneline -- adapters.py`; `git log --all --oneline -- adapters.py`; `git show 8f954567/ec0e33b3/c0813a2d -s --format=%B` (and `--stat` for `8f954567`); `git show <merge-base>:src/requests/adapters.py`; `git status --porcelain` / `--porcelain --ignored`. The three commits it inspected (`8f954567`, `ec0e33b3`, `c0813a2d`) are all this PR's own pre-head commits (already listed in the packet's commit table / pre-merge-base history) or reachable ancestors of the pinned head, not anything beyond it. The one `--all` flag is a broader ref sweep than I used myself, but the clone's history is truncated at the pinned head by construction (the packet states "the newest object reachable in your clone is `4089f3dc6`"), so `--all` could not surface anything past it in this sandboxed clone; I record this as the verifier's own choice of command, not a rule violation, since nothing beyond the pinned head exists to find. Neither I nor the verifier ran `git fetch` or any command that could reach past `4089f3dc6` even in an unconstrained clone.

## 9. Sandbox disclosure

Outside the strict list (clone, skill snapshot, packet directory, my own work/report/payload/timing paths), I read:
- `/private/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/{connection.py,connectionpool.py,poolmanager.py,util/ssl_.py}` — the pinned virtualenv's installed `urllib3` dependency (version 2.7.0, confirmed via `urllib3.__version__`). This is not the reviewed repository, the skill snapshot, or the packet; it is the run environment's pre-provisioned virtualenv named explicitly in the packet's §8 execution allowance ("run pytest from the clone root with the pre-provisioned virtualenv"). I read it because the falsifiable mechanism behind Finding 1 and the D1 acquittal is entirely about how `requests`'s own code (which I own) interacts with urllib3's connection-pooling and TLS-context code (which it calls into); I judged this within `SKILL.md`/`review-rubric.md`'s "relevant callers, interfaces... each read as a bounded range" scope for falsifying a candidate, not an excursion into an unrelated system. I am disclosing it explicitly per rule 7/8 rather than treating it as implicitly authorized.
- The verifier sub-agent read the same venv paths independently (see its verbatim report in §4), for the same reason. I extended its prompt's rule 4 to explicitly permit this read (with mandatory disclosure) before dispatch, anticipating the same need I resolved for myself in §10 Note 1; the verifier used that permission and disclosed the reads in detail, and its independent re-derivation of the same dependency facts (rather than trusting my citations) strengthens the verification.

No other path outside the sandbox was read by me or by the sub-agent. One incidental disclosure: an `ls -la /tmp/qual137/reports/i/` run to confirm my own output files existed also listed the *filenames* (not contents) of other cells'/replicates' report, payload, timing, meta, and session files in the same shared directory (`i-867cf3ff-seed1-att-02-*`, `i-bea6be14-seed1-att-01-*`, `i-bea6be14-seed2-att-04-*`). I did not open, read, or use the contents of any of those files — only their names appeared in the directory listing — but I record the listing itself here per rule 7's "report it if you read one anyway," out of caution, even though no content from another run was accessed.

## 10. Notes — judgment calls on contract ambiguities

1. **Reading the installed `urllib3` dependency.** `SKILL.md`/rules 1-7 list the sandbox as "the clone, the skill snapshot, the packet directory, and your work, payload, report, and timing paths," and separately the packet's rule 7 repeats the same list. Neither text mentions the pinned venv's *site-packages* as a readable location, only as an *executable* one (via pytest). I judged that reading the installed dependency's source to establish a falsifiable mechanism was implicitly authorized by `review-rubric.md`'s "relevant callers, interfaces... each read as a bounded range" and by the fact that the packet's own execution allowance already presupposes the venv is a legitimate, inspectable part of this run's evidence base (you cannot run pytest against it without it being loadable, and its behavior is exactly what several rubric gates — "introduced-here," "proven consequence" — require me to establish for code that calls into it). I chose to proceed and disclose it explicitly (§9) rather than either silently using it or declining to verify a security-relevant claim I could otherwise fully resolve. Had I declined, both `C1` and `D1` would have had to be marked `not-verifiable`/coverage-incomplete purely because the dependency they concern happens to live outside the four named directories, which seemed like the wrong reading of a rule whose evident purpose is "don't wander into other runs' clones or the internet," not "don't read the library the code you're reviewing calls into."
2. **Kind classification of `C1`.** I classified Finding 1 as `kind=concurrency` rather than `kind=security`, per `output-contract.md`'s "Use `concurrency` or `invariant` when sibling paths share the broken state rule and therefore require the verifier's bug-class check" — this triggers `references/verifier.md`'s much deeper sibling-interleaving procedure, which I judged was the more rigorous and more clearly rubric-mandated path for a shared-mutable-state defect, even though the *consequence* (client-certificate/authentication leakage) is naturally described as a security concern. The candidate independently also qualifies for mandatory verification as `must-fix` and as touching "security or authorization," so the choice of kind did not change whether verification was mandatory, only which verifier procedure applied.
3. **Priority calibration (P1, not P0, for both findings).** Both findings require a specific precondition (client certs + concurrency for `C1`; a broken/overridden default CA bundle for `C2`) rather than being universal on every invocation, so I did not use `P0` ("universal release blocker"). I judged `P1` ("urgent defect with serious or broadly affecting consequences") over `P2` because both preconditions are realistic, not contrived — `C1`'s precondition is literally the PR's own stated primary workload (many concurrent requests), and `C2`'s precondition is a scenario `certs.py`'s own docstring documents as a supported customization.
4. **Whether the module-level singleton counts as "introduced here" when the mutating code lives in a third-party dependency.** I treated `review-rubric.md`'s gate 2 ("Unchanged code is introduced-here when the change removed or weakened a guarantee that code relied on") as applying across the dependency boundary: the *guarantee* ("each connection gets a private, unshared `SSLContext`") was something `requests`'s own code controlled and relied on implicitly (by never passing `ssl_context`) at the merge-base, and `requests`'s own diff — not any urllib3 change — is what removed it. I did not require the "unchanged code" to be literally inside `src/requests/adapters.py`'s diff for this gate to apply, since the guarantee itself was never written down anywhere in `requests`'s source; it was an emergent property of *not* setting a kwarg. I recorded this reasoning explicitly in Finding 1's evidence rather than asserting it without support.
5. **`D3`'s classification as `bug` rather than something weaker.** I kept `D3` as a `kind=bug` candidate all the way to a full falsification and related-acquittal ruling (rather than short-circuiting it as obviously trivial) because the ordering change was real and I wanted a decisive, checked reason to drop it (idempotent write, no reachable reuse path) rather than an assumption. This cost one extra ledger row and one extra related-acquittal ruling but produced a stronger acquittal than a hand-wave would have.
6. **No `Ambiguities` section published.** I did not find a genuine two-reading disagreement about a rubric or contract *term* in this run (as opposed to ordinary judgment calls about evidence sufficiency, which I've recorded above instead) — so the payload's summary omits the conditional `Ambiguities` section per `output-contract.md`'s "Include only non-empty conditional sections" rule.
7. **Verifier prompt explicitly extended the venv-read permission.** Having made the judgment call in Note 1 for myself, I wrote the verifier's rule 4 to explicitly permit (and require disclosure of) a read of the pinned venv's urllib3 source, anticipating it would need the same evidence I did. It used that permission and disclosed the read in detail (§4), consistent with Note 1's reasoning.

## 11. Payload and final validation

The complete review payload — the summary body, both finding comments (with trailers), and the observation, exactly as they would have posted — is at [`/tmp/qual137/reports/i/i-867cf3ff-seed2-att-03-payload.md`](../i/i-867cf3ff-seed2-att-03-payload.md) (absolute path: `/tmp/qual137/reports/i/i-867cf3ff-seed2-att-03-payload.md`).

- Structured JSON payload assembled at `/tmp/qual137/work/i-867cf3ff-seed2-att-03/payload_draft1.json`.
- `python3 scripts/validate_review.py --render payload_draft1.json` printed the two summary-reference fragments (one `anchor …; fix …` for Finding 1, one `anchor …` for Finding 2), pasted verbatim into the summary body's `## Findings` list — never hand-composed.
- `python3 scripts/validate_review.py payload_draft1.json` → **exit 0**, zero violations, on the final payload.
- `python3 scripts/validate_review.py --emit-batch payload_draft1.json` → **exit 0**, produced a well-formed one-call GitHub review batch (`commit_id=4089f3dc65f783beaa53cc032958ab625440d0ac`, `event=COMMENT`, summary body unchanged, two line comments with correct `path`/`line`/`start_line`/`side`/`start_side`/`body`), confirming the payload is publication-ready in form. It was never submitted (`gh api ... --input batch.json` was not run): retrospective review of a merged PR, publication disabled, per `SKILL.md` step 1 and the packet's rule 4.
- The `workflow` identifier the validator enforces and reports is `v5b-1` (the script's `WORKFLOW` constant; confirmed present and correctly matched in the run trailer of the validated payload).
- Immediately after the final zero-violation `validate_review.py` run above, I ran `python3 /tmp/qual137/mark_event.py /tmp/qual137/reports/i/i-867cf3ff-seed2-att-03-timing.json payload_validated_at`, which recorded `payload_validated_at: "2026-09-07T05:55:54.856000+00:00"` in the timing sidecar. No other event was written to that file, and it was not hand-edited.
- Re-fetch-before-write (`SKILL.md` step 5 / output-contract "Publication invariants"): not applicable in the literal sense — this is a non-publishing retrospective run and no write is attempted — but the pinned head (`4089f3dc65f783beaa53cc032958ab625440d0ac`) was never altered or re-resolved during this run; the packet fixed it as authoritative and the clone's `review-head` branch remained checked out at it throughout (confirmed by `git status`/`git log` checks in §8), so there is no staleness to report.
