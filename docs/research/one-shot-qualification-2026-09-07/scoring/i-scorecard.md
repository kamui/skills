# Scorecard — target `i` (psf/requests#6667)

Register: 2 material defects, GT-i1 (shared mutable process-wide `SSLContext` — (a) silently
discards subclass-configured `ssl_context` and (b) lets concurrent/sequential per-request
client-cert loading mutate shared OpenSSL state) and GT-i2 (CA-bundle loading moved from lazy
per-request to eager import-time execution).

Note on method: I did not try to determine which arm/run produced which blind file; I scored each
payload strictly against the register and against the source at `/tmp/qual137/transport-check/i`.
I noticed no reviewer-identifying text and did not go looking for any.

---

## blind-6fb580.md

**1. Recovered defect IDs**

- **GT-i1 (manifestation (b) only — shared-mutation/client-cert leak).** Quote: *"`_urllib3_request_context()` hands every verify=True request the same module-level singleton `_preloaded_ssl_context` ... urllib3 unconditionally calls `context.load_cert_chain(certfile, keyfile)` on whatever `ssl_context` it receives, so the first client-cert request permanently loads that identity into the shared context; every later verify=True connection ... reuses the identical mutated object and can present the leaked certificate."* This names the exact shared object, the exact mutating call, and a concrete cross-request consequence — enough specificity that a reader would act on the right underlying defect (a single shared, mutable `SSLContext`). Clears the specificity bar.

**2. Missed defect IDs**

- **GT-i2** (eager import-time CA-bundle loading). Not mentioned anywhere in this payload — no finding, no observation, no coverage caveat.
- **GT-i1 manifestation (a)** (subclass-configured `ssl_context` via `init_poolmanager` silently discarded even with no client cert involved) is not raised; see fix-sufficiency below.

**3. Fix sufficiency**

- GT-i1: **partial**. Quoted proposed change: *"stop treating `_preloaded_ssl_context` as the default whenever a client certificate is involved: key any preloaded context on the exact `client_cert` value, or build a fresh context per distinct `client_cert`, falling back to the shared cert-free singleton only when `client_cert` is None."* This resolves the client-cert mutation manifestation but explicitly keeps the shared singleton for the `client_cert is None` case — so a subclass's `init_poolmanager`-configured `ssl_context` would still be silently replaced by `_preloaded_ssl_context` whenever no client cert is in play. Manifestation (a) survives this fix, so it does not restore the full required corrective outcome.
- GT-i2: **absent** (no finding at all).

**4. Findings not in the register**

- None beyond the one finding. The coverage note about running `test_different_connection_pool_for_mtls_settings` and finding it fails only due to an expired fixture cert is a verification-process detail, not a published finding; I checked it against the register's own note (`Missing Authority Key Identifier` / test-cert staleness) and it's consistent — no register conflict.

**5. Action/severity errors**

- None. The one finding is correctly framed as a deterministic (not merely racy) steady-state defect and labeled P0/must-fix, which the demonstrated consequence (credential leak) supports.

**6. Questions, observations, hygiene items**

- None published in this payload (no Observations/Questions section).

**7. Derived status**

- "Changes Requested (advisory) — 1 must-fix finding." Coverage declared **complete** ("diff coverage: complete").

**8. False clean**

- No. (Not applicable — the review does report a material finding.)

**9. Duplicates**

- None; only one finding.

---

## blind-72fbb9.md

**1. Recovered defect IDs**

- **GT-i1 (manifestation (b)).** Quote: *"`_urllib3_request_context()` hands the same module-level `_preloaded_ssl_context` object to every `verify=True` pool. urllib3's `ssl_wrap_socket()` calls `context.load_cert_chain(certfile, keyfile)` on that shared object whenever a connection carries a client certificate, and nothing ever clears it. The later, cert-less request still presents the earlier request's client certificate to its own server — a deterministic, single-process credential leak, not merely a race."* Specific object, specific mutating call, concrete consequence — clears the bar.
- **GT-i2.** Quote: *"`src/requests/adapters.py` now calls `_preloaded_ssl_context.load_verify_locations(...)` unconditionally at module import time. `import requests` now raises `OSError`/`FileNotFoundError` and fails completely, even for callers using `verify=False`, a custom CA bundle string, or no HTTPS at all. At the merge-base this same check ran only lazily, inside `cert_verify()`, gated on an actual HTTPS request needing the default bundle."* Correctly names the mechanism (eager, unconditional, import-time) and the "was lazy before" contrast the register requires. Clears the bar.

**2. Missed defect IDs**

- **GT-i1 manifestation (a)** (silent override discard when no client cert is involved) — not raised as a separate concern; see fix sufficiency.

**3. Fix sufficiency**

- GT-i1: **partial**. Quoted change: *"stop passing `_preloaded_ssl_context` as `pool_kwargs["ssl_context"]` when `client_cert is not None`; build a context/pool_kwargs combination scoped to that specific client certificate instead, so `load_cert_chain()` never mutates state another request also reads."* Same gap as above — leaves the `client_cert is None` override-discard path untouched.
- GT-i2: **sufficient**. Quoted change: *"Defer creating and loading `_preloaded_ssl_context` until the first `verify=True` HTTPS request actually needs it, so a broken default CA bundle only affects callers who verify with it."* This restores lazy per-request behavior, addressing both the crash-on-broken-bundle manifestation (#6764-type) and the import-time wall-clock regression (#6790-type) in one stroke — matches the register's required corrective outcome exactly.

**4. Findings not in the register**

- Observation: *"The shared `_preloaded_ssl_context`'s `verify_mode` is reassigned on every `verify=True` connection, not only its client-identity certificate, since urllib3's connection-establishment path applies `cert_reqs`-derived `verify_mode` to whichever context it receives. Evidence: `src/requests/adapters.py:298`, `urllib3/connection.py:901-937`."* I verified this against the installed urllib3 2.7.0 source: `_ssl_wrap_socket_and_match_hostname()` does unconditionally execute `context.verify_mode = resolve_cert_reqs(cert_reqs)` on whatever context it's handed. **Classification: true but not material.** Because `_preloaded_ssl_context` is only ever handed out on the `verify is True` branch, `cert_reqs` is always `"CERT_REQUIRED"` there, so the reassignment is idempotent — it doesn't change behavior across requests and has no demonstrated consequence. Correctly presented only as an observation, not a finding with impact/fix, so no over-claim.

**5. Action/severity errors**

- None found.

**6. Questions, observations, hygiene items**

- 1 observation (verify_mode reassignment, above) — answerable from the material at hand (urllib3 source was inspected), and its answer (idempotent, no consequence) is already reflected in it being an observation rather than a finding, so it would not change the review if resolved further.
- 0 questions.

**7. Derived status**

- "Changes Requested (advisory) — 2 must-fix findings." Coverage declared **complete** (installed urllib3 2.7.0 internals and test fixtures inspected; two reproductions run).

**8. False clean**

- No.

**9. Duplicates**

- None; the two findings map to two distinct register defects.

---

## blind-c3e120.md

**1. Recovered defect IDs**

- **GT-i2.** Quote: *"The bare `import requests` statement now raises an uncaught `FileNotFoundError`/`SSLError` before any application code runs, crashing every program that imports requests. At the merge-base, `load_verify_locations()` for the default bundle only ran lazily inside `cert_verify()`, so this class of failure only affected processes that actually sent a verified HTTPS request."* Correct mechanism and correct contrast with merge-base behavior.
- **GT-i1 (manifestation (b)).** Quote: *"`_urllib3_request_context()` hands the same process-wide `_preloaded_ssl_context` object to urllib3 for every `verify=True` request, with or without a client certificate. urllib3's `ssl_wrap_socket()` then calls `context.load_cert_chain(certfile, keyfile)` on that exact shared object. `ssl.SSLContext` has no API to unload a certificate chain, so every later `verify=True` connection to any host, including ones that never asked for a client certificate, presents that certificate for the rest of the process's life."* Adds the correct, verifiable detail that `SSLContext` has no chain-unload API, strengthening the permanence claim. Clears the bar.

**2. Missed defect IDs**

- **GT-i1 manifestation (a)** — not raised; see fix sufficiency.

**3. Fix sufficiency**

- GT-i2: **sufficient** (with a caveat). Quoted change: *"don't call `load_verify_locations()` unconditionally at import time; build `_preloaded_ssl_context` lazily on first `verify=True` use, or wrap the module-level call so a load failure is deferred and reported the same way `cert_verify()` already reports it (a clear `OSError` naming the invalid path) instead of aborting import."* The first alternative (lazy build) fully restores the required outcome (no import-time filesystem I/O, no import-time regression). The second alternative offered ("wrap the module-level call ... instead of aborting import") would only suppress the crash without removing the eager `load_verify_locations()` call itself, so it would **not** address the import-time wall-clock regression manifestation (#6790-type) — that half of the "or" is only a partial fix. Since the primary clause is sufficient, I score this **sufficient** overall but flag the ambiguity: a reader could implement only the weaker alternative and still leave GT-i2's performance manifestation unresolved.
- GT-i1: **partial**. Quoted change: *"don't reuse `_preloaded_ssl_context` when `client_cert is not None`; build a private `SSLContext` for that combination instead (optionally cached per client-cert identity, with the cache's own read/create-if-absent path synchronized so concurrent requests for the same identity cannot race to build divergent contexts)."* Same gap: leaves the no-client-cert override-discard path (manifestation (a)) unaddressed. Notably, this is the only reviewed fix that also proactively addresses a *secondary* race (concurrent construction of the per-cert-identity context), which is good but doesn't change the (a)-manifestation gap.

**4. Findings not in the register**

- Observation: *"`tests/test_adapters.py`, the only test file covering this module, exercises none of `_urllib3_request_context()`, `cert_verify()`, or `_preloaded_ssl_context`. Evidence: `tests/test_adapters.py`."* I checked this against the register, which independently states: *"No test in the repository at either revision exercises the `_preloaded_ssl_context` injection path or a custom `init_poolmanager(ssl_context=...)` adapter."* **Classification: true but not material** (a real gap, explicitly called a hygiene/coverage observation, not asserted as a standalone defect).

**5. Action/severity errors**

- None found.

**6. Questions, observations, hygiene items**

- 1 observation (test-coverage gap, above) — answerable directly from the repo (it was), and doesn't itself change the review's verdict.
- 0 questions. The summary mentions a "fresh-context verifier" that "re-ran and held three related, non-survivor candidates ... for acquittal review," but does not disclose what those three candidates were, so I cannot check whether any of them was manifestation (a) of GT-i1 or something else; this is a transparency gap in the payload, not a question I can resolve from the material given.

**7. Derived status**

- "Changes Requested (advisory) — 2 must-fix findings." Coverage declared **complete**, with an explicit independent-verifier re-run step described.

**8. False clean**

- No.

**9. Duplicates**

- None; two findings map to two distinct register defects.

---

## blind-d6ef2b.md

**1. Recovered defect IDs**

- **GT-i1 (manifestation (b)), with one unsupported embellishment (see below).** Quote: *"The shared, process-wide `_preloaded_ssl_context` created at import (`adapters.py:75-78`) is handed to every `verify=True` connection pool, including ones with a client certificate; urllib3's `ssl_wrap_socket()` calls `context.load_cert_chain()` on that same shared object, so the loaded certificate persists and gets presented to unrelated hosts afterward ... At the merge-base, `ssl_context` was never set for `verify=True`, so urllib3 built a private context per connection; this change removed that isolation."* This core claim is specific and correct, and clears the bar.
- **GT-i2.** Quote: *"`_preloaded_ssl_context.load_verify_locations(...)` (`adapters.py:75-78`) now runs unconditionally at `import requests` time, so a broken default bundle makes the bare import raise, breaking every caller in that process, including ones that only use `verify=False` or a custom CA bundle and never needed the default one. At the merge-base the same broken bundle only failed the specific `verify=True` request that used no override, inside `cert_verify()`'s existing `OSError` handling."* Correct mechanism and correct merge-base contrast.

**2. Missed defect IDs**

- **GT-i1 manifestation (a)** — not raised as its own concern; see fix sufficiency.

**3. Fix sufficiency**

- GT-i1: **partial**. Quoted change: *"In `_urllib3_request_context()` (`adapters.py:94-107`), only pass `_preloaded_ssl_context` when the connection has no client certificate and no hostname-check override; otherwise build a private, connection-scoped `SSLContext` as before this change."* As with the other three reviews, this still hands `_preloaded_ssl_context` to any `verify=True` connection with no client cert — leaving a subclass's `init_poolmanager`-configured `ssl_context` silently discarded in that case. Manifestation (a) is unaddressed.
- GT-i2: **sufficient**. Quoted change: *"Defer building and loading `_preloaded_ssl_context` until the first `verify=True` request that actually needs it, so import cannot fail merely because the default bundle is broken."* Fully restores lazy per-request behavior; addresses both the crash and the import-time-cost manifestations.

**4. Findings not in the register**

- Embedded in Finding 1's title and remediation is a "hostname-override" trigger condition: *"Stop sharing the preloaded SSLContext with client-certificate **or hostname-override** connections"* and *"only pass `_preloaded_ssl_context` when the connection has no client certificate and **no hostname-check override**."* I searched the diff and the whole `src/requests` tree for any hostname-override mechanism (`assert_hostname`, `check_hostname`, `server_hostname`) reachable from `adapters.py`; there is none — `_urllib3_request_context()`/`cert_verify()` never set or expose any such per-request override. **Classification: false, as an embedded sub-claim.** It doesn't invalidate the finding's core, well-evidenced client-cert-leak claim (which I still count as recovering GT-i1), but the "hostname-override" half of the trigger/remediation is unsupported by any evidence in the source and should not be relied on as stated.
- Observation: *"The directory-vs-file CA-path check is computed independently in both `_urllib3_request_context()` and `cert_verify()`, duplicating the same decision on every request. Evidence: `src/requests/adapters.py:96-99`, `src/requests/adapters.py:314-317`."* I verified this against both the head and merge-base source: at merge-base, `_urllib3_request_context()` had no `os.path.isdir()` branch at all (`pool_kwargs["ca_certs"] = verify` unconditionally); the PR itself introduces the duplicate isdir check that already existed in `cert_verify()`. **Classification: true but not material** — a real, PR-introduced duplication, but purely a style/DRY observation with no demonstrated behavioral consequence; consistent with the register treating unrelated style gaps as sub-material.

**5. Action/severity errors**

- None found beyond the embedded false sub-claim noted above (which is a truth/support problem, not a severity/action mismatch — the P1/must-fix framing of the real client-cert-leak claim is well supported).

**6. Questions, observations, hygiene items**

- 1 observation (duplicated isdir check, above).
- 0 questions, explicitly: *"None. Both survivors were fully resolvable from code, the installed dependency, and the review record; no candidate required a maintainer decision or a benchmark to settle."* This is answerable-from-material and consistent with the payload's own reproduction claims.

**7. Derived status**

- "Changes Requested (advisory) — 2 must-fix findings." Coverage declared **complete**, citing an independent verifier batch and pytest runs, with three pre-existing test failures noted as confirmed-identical-at-merge-base (consistent with the register's own note about the stale mTLS/test-cert fixture).

**8. False clean**

- No.

**9. Duplicates**

- None; two findings map to two distinct register defects.

---

## Cross-review table

| Review | Recovered IDs | Recall (R/D) | Fix sufficiency | False findings (raw) | Action errors | Questions | Observations | False clean | Status |
|---|---|---|---|---|---|---|---|---|---|
| blind-6fb580 | GT-i1 (partial: manifestation (b) only) | 1/2 | GT-i1: partial; GT-i2: absent | 0 | 0 | 0 | 0 | No | Changes Requested — 1 must-fix |
| blind-72fbb9 | GT-i1 (partial), GT-i2 | 2/2 | GT-i1: partial; GT-i2: sufficient | 0 | 0 | 0 | 1 (true, not material) | No | Changes Requested — 2 must-fix |
| blind-c3e120 | GT-i1 (partial), GT-i2 | 2/2 | GT-i1: partial; GT-i2: sufficient (one of two offered fix options is only partial) | 0 | 0 | 0 | 1 (true, not material) | No | Changes Requested — 2 must-fix |
| blind-d6ef2b | GT-i1 (partial, with 1 unsupported embedded sub-claim), GT-i2 | 2/2 | GT-i1: partial; GT-i2: sufficient | 0 standalone (1 unsupported sub-claim embedded in a true finding) | 0 | 0 | 1 (true, not material) | No | Changes Requested — 2 must-fix |

Notes on the table:
- "Recall" counts a defect as recovered if any manifestation is stated with the required specificity, per the instructions; all four reviews clear that bar for GT-i1 via the client-cert-mutation manifestation only. None of the four raises GT-i1's other manifestation (silent discard of a subclass's `init_poolmanager`-configured `ssl_context` when no client cert is involved), so GT-i1's fix sufficiency is **partial in every review that found it** — this is a shared gap, not something that differentiates the four.
- I did not compare the reviews' overall quality against one another beyond what the rubric asks for (recall, truth, fix sufficiency); I did not weigh length, formatting, or confidence.

## New candidates (consolidated across reviews)

None. Every observation/finding raised across the four reviews that is not a register `GT-` entry was, on inspection, either (a) a verified true fact with no demonstrated material consequence (test-coverage gap; `verify_mode` reassignment idempotence; duplicated isdir-check logic), or (b) a specific sub-claim I could refute directly from the source (the "hostname-override" trigger in blind-d6ef2b's Finding 1, for which no such mechanism exists anywhere in `src/requests/adapters.py` or the rest of `src/requests`). No review proposed a plausible, specific, material claim outside GT-i1/GT-i2 that I was unable to settle — nothing here needs to go to further adjudication.
