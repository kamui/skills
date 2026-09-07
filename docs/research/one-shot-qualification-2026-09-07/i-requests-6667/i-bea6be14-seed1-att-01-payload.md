# Review payload — psf/requests#6667 (as it would be published)

Posting identity: `kamui`. Event: `COMMENT` (retrospective review of a merged pull request; publication disabled — rendered, not posted).

## Review summary (submitted as the review body)

**Changes Requested (advisory)** — 2 must-fix findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Avoid a redundant per-request `load_verify_locations()` call for `verify=True` HTTPS requests, by preloading the default CA bundle into one shared SSLContext and reusing it for every default-verified connection, fixing a documented concurrent-performance regression.

**Issue fit:** No originating issue; ledger built from the pull-request title and body. Met: eliminating the redundant `load_verify_locations()` call for the common `verify=True` case (pr-title, pr-body); server-certificate verification semantics (`CERT_REQUIRED`/`CERT_NONE`) unchanged for both `verify=True` and `verify=False` (pr-body). Non-goal honored: the change does not attempt to eliminate the default-bundle load entirely (pr-body).

**Coverage:** Complete merge-base diff reviewed (1 file, `src/requests/adapters.py`, +28/-18). No test function was added or changed by this diff, so the Changed tests section's execution requirement is vacuous; a lack of any existing test over the changed functions is recorded as an observation below rather than as an executed-and-passed check. Two focused, ad hoc, fully offline reproductions were run once each (no network) via the pre-provisioned pytest virtualenv to settle the two findings below; both were independently re-run with identical results by a fresh-context verifier, which additionally re-ran and held three related, non-survivor candidates it was given for acquittal review.

**Reviewed:** `4089f3dc6` against merge-base `8dd3b26bf`.

## Findings

- [P1] [must-fix] Don't load the default CA bundle unconditionally at import time — anchor [`src/requests/adapters.py:75-78`](https://github.com/psf/requests/blob/4089f3dc65f783beaa53cc032958ab625440d0ac/src/requests/adapters.py?plain=1#L75-L78)
- [P1] [must-fix] Don't hand the shared preloaded SSLContext to a connection that also supplies a client certificate — anchor [`src/requests/adapters.py:94-95`](https://github.com/psf/requests/blob/4089f3dc65f783beaa53cc032958ab625440d0ac/src/requests/adapters.py?plain=1#L94-L95)

## Observations

- `tests/test_adapters.py`, the only test file covering this module, exercises none of `_urllib3_request_context()`, `cert_verify()`, or `_preloaded_ssl_context`. Evidence: `tests/test_adapters.py`.

<!-- review-run head=4089f3dc65f783beaa53cc032958ab625440d0ac base-ref=main base-sha=8dd3b26bf59808de24fd654699f592abf6de581e merge-base=8dd3b26bf59808de24fd654699f592abf6de581e workflow=v5b-10 context=9e80f1a16f93243a31dff067dd6ba49658a84f52b2a0216860c03ff210cf8621 issues=none coverage=complete -->

## Inline comment — `src/requests/adapters.py:75-78 (RIGHT)`

**[P1] [must-fix] Don't load the default CA bundle unconditionally at import time**

**Triggers when:** The default certifi bundle path is unreadable or missing at process start (a corrupted or incompatible certifi install, a broken shim, a frozen/zipped distribution whose bundle failed to extract, or a sandboxed filesystem) in a process that never sends a `verify=True` request against the default trust store (it always uses `verify=False` or always supplies its own CA bundle).

**Impact:** The bare `import requests` statement now raises an uncaught `FileNotFoundError`/`SSLError` before any application code runs, crashing every program that imports requests. At the merge-base, `load_verify_locations()` for the default bundle only ran lazily inside `cert_verify()`, so this class of failure only affected processes that actually sent a verified HTTPS request.

**Change:** In `src/requests/adapters.py`, don't call `load_verify_locations()` unconditionally at import time; build `_preloaded_ssl_context` lazily on first `verify=True` use, or wrap the module-level call so a load failure is deferred and reported the same way `cert_verify()` already reports it (a clear `OSError` naming the invalid path) instead of aborting import.

<!-- finding id=adapters/import-time-cert-load-crash head=4089f3dc65f783beaa53cc032958ab625440d0ac priority=P1 action=must-fix blocking=true kind=bug -->

## Inline comment — `src/requests/adapters.py:94-95 (RIGHT)`

**[P1] [must-fix] Don't hand the shared preloaded SSLContext to a connection that also supplies a client certificate**

**Triggers when:** Any single `verify=True` request anywhere in the process supplies a client certificate via the documented `cert=` parameter (`Session.request(..., cert=(...))` or `HTTPAdapter.send(..., cert=(...))`).

**Impact:** `_urllib3_request_context()` hands the same process-wide `_preloaded_ssl_context` object to urllib3 for every `verify=True` request, with or without a client certificate. urllib3's `ssl_wrap_socket()` then calls `context.load_cert_chain(certfile, keyfile)` on that exact shared object. `ssl.SSLContext` has no API to unload a certificate chain, so every later `verify=True` connection to any host, including ones that never asked for a client certificate, presents that certificate for the rest of the process's life. This is a steady-state defect, not a race-only one: it reproduces sequentially, with no concurrent threads required, and matches the exact hazard an OpenSSL/CPython maintainer described in this PR's own review thread ("changing ... mTLS certs can lead to surprising behavior ... unrelated to threads"), which the PR addressed only by renaming the object, not by isolating client-certificate use.

**Change:** In `_urllib3_request_context` (`src/requests/adapters.py`), don't reuse `_preloaded_ssl_context` when `client_cert` is not `None`; build a private `SSLContext` for that combination instead (optionally cached per client-cert identity, with the cache's own read/create-if-absent path synchronized so concurrent requests for the same identity cannot race to build divergent contexts).

<!-- finding id=adapters/shared-ssl-context-cert-chain-leak head=4089f3dc65f783beaa53cc032958ab625440d0ac priority=P1 action=must-fix blocking=true kind=concurrency -->
