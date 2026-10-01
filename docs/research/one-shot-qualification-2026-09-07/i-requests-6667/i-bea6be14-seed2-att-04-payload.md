**Changes Requested (advisory)** — 1 must-fix finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Eliminate the per-connection `load_verify_locations()` call urllib3 makes for `verify=True` requests, by reusing one preloaded default `SSLContext`, to fix a reported concurrent-performance regression.

**Issue fit:** No originating issue; the ledger is built from the pull-request title and body. Met — the module-level preloaded `SSLContext` (`adapters.py:75-95`) replaces the per-connection `load_verify_locations()` call for `verify=True`, matching the PR's stated goal. Partial — the PR body's own claim that "`verify=True` and `verify=False` still behave as expected" (tested manually against `https://invalid.badssl.com`) holds for the tested server-verification scenario, but not once a client certificate is supplied together with `verify=True`; see the finding below.

**Coverage:** Complete merge-base diff reviewed (1 file, `src/requests/adapters.py`, function-context chunks fully consumed, `diff coverage: complete`); the unchanged urllib3 `ssl_wrap_socket`/`HTTPSConnection` contract this change depends on was inspected as the interface the change must still satisfy. This diff changes no test file, so the rubric's Changed-tests section created no execution obligation; one pre-existing, unrelated test (`test_different_connection_pool_for_mtls_settings`) was run once ad hoc while falsifying the finding below and failed only because its `tests/certs/mtls/client/client.pem` fixture expired 2026-03-13, unrelated to this diff.

**Reviewed:** `4089f3dc65f783beaa53cc032958ab625440d0ac` against merge-base `8dd3b26bf59808de24fd654699f592abf6de581e`.

## Findings

- [P0] [must-fix] Shared default SSLContext lets a client certificate leak into unrelated requests — anchor [`src/requests/adapters.py:94-95`](https://github.com/psf/requests/blob/4089f3dc65f783beaa53cc032958ab625440d0ac/src/requests/adapters.py?plain=1#L94-L95); fix [`src/requests/adapters.py:94-109`](https://github.com/psf/requests/blob/4089f3dc65f783beaa53cc032958ab625440d0ac/src/requests/adapters.py?plain=1#L94-L109)

<!-- review-run head=4089f3dc65f783beaa53cc032958ab625440d0ac base-ref=main base-sha=8dd3b26bf59808de24fd654699f592abf6de581e merge-base=8dd3b26bf59808de24fd654699f592abf6de581e workflow=v5b-10 context=9e80f1a16f93243a31dff067dd6ba49658a84f52b2a0216860c03ff210cf8621 issues=none coverage=complete -->

---

### Inline comment on `src/requests/adapters.py:94-95` (`RIGHT`)

**[P0] [must-fix] Shared default SSLContext lets a client certificate leak into unrelated requests**

**Triggers when:** Any request is made with the default verify=True and a client certificate (cert=(certfile, keyfile)), followed by any other verify=True request in the same process, even single-threaded and sequential, to an unrelated host with no cert= argument at all.

**Impact:** _urllib3_request_context() hands every verify=True request the same module-level singleton _preloaded_ssl_context (adapters.py:75,94-95) and routes cert_file/key_file into the same pool_kwargs dict when a client cert is supplied (adapters.py:102-109, unchanged since the merge-base). urllib3 unconditionally calls context.load_cert_chain(certfile, keyfile) on whatever ssl_context it receives, so the first client-cert request permanently loads that identity into the shared context; every later verify=True connection, proxied or direct, to any host, reuses the identical mutated object and can present the leaked certificate. This is a steady-state defect, not a race: it reproduces deterministically with no concurrency at all. At the merge-base no ssl_context was ever passed for verify=True, so urllib3 built a fresh, connection-private context per pool instead.

**Change:** In _urllib3_request_context(), at both the direct-pool and proxy call sites that consume the same pool_kwargs, stop treating _preloaded_ssl_context as the default whenever a client certificate is involved: key any preloaded context on the exact client_cert value, or build a fresh context per distinct client_cert, falling back to the shared cert-free singleton only when client_cert is None. Locking or re-serializing access does not fix this: the shared object's identity is the defect, and it leaks even under fully serialized, single-threaded access.

<!-- finding id=adapters/shared-ssl-context-client-cert-leak head=4089f3dc65f783beaa53cc032958ab625440d0ac priority=P0 action=must-fix blocking=true kind=invariant fix=src/requests/adapters.py:94-109 -->
