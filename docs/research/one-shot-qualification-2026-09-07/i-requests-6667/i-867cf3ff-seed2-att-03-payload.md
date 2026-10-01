# Review payload — `psf/requests#6667` (retrospective, publication disabled)

This is the review exactly as it would be published as one forge-native review
(`event=COMMENT`, since gating is not authorized and this is a third-party,
non-author, retrospective review of a merged PR). It was not posted anywhere;
this file is the render. It validated with zero violations under
`scripts/validate_review.py` (`workflow=v5b-1`) and its `--emit-batch` mode
produced a well-formed one-call GitHub review batch (summary + 2 line comments).

## Summary (review body)

**Changes Requested (advisory)** — 2 must-fix findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Avoid a redundant TLS root-certificate reload (`load_verify_locations()`) on every `verify=True` HTTPS request, to fix a concurrency-performance regression, by sharing one pre-loaded `SSLContext` across connections instead of loading the CA bundle per request.

**Issue fit:** No linked issue (`issues=none`); judged against the PR's own stated intent. The performance goal is met — the per-request reload is gone for the plain `verify=True` case — but the mechanism used to achieve it (a single shared, mutable `SSLContext`) is unsafe whenever a client certificate or a hostname-check override is also in play (Finding 1), and its eager construction at import time is a new failure mode of its own (Finding 2).

**Coverage:** Complete. The single changed file (`src/requests/adapters.py`) was reviewed in full via the merge-base diff (function-context expanded to the enclosing class); TLS/authorization, concurrency, and compatibility risk checks were exercised with evidence, including one independent verifier batch and one focused pytest selection per flag set. Three pre-existing test failures were confirmed identical against the merge-base and are unrelated to this diff.

**Reviewed:** `4089f3dc6` against merge-base `8dd3b26bf5`.

## Findings

- [P1] [must-fix] Stop sharing the preloaded SSLContext with client-certificate or hostname-override connections — anchor [`src/requests/adapters.py:94-95`](https://github.com/psf/requests/blob/4089f3dc65f783beaa53cc032958ab625440d0ac/src/requests/adapters.py?plain=1#L94-L95); fix [`src/requests/adapters.py:94-107`](https://github.com/psf/requests/blob/4089f3dc65f783beaa53cc032958ab625440d0ac/src/requests/adapters.py?plain=1#L94-L107)
- [P1] [must-fix] Don't load the default CA bundle eagerly at import time — anchor [`src/requests/adapters.py:75-78`](https://github.com/psf/requests/blob/4089f3dc65f783beaa53cc032958ab625440d0ac/src/requests/adapters.py?plain=1#L75-L78)

## Observations

- The directory-vs-file CA-path check is computed independently in both `_urllib3_request_context()` and `cert_verify()`, duplicating the same decision on every request. Evidence: `src/requests/adapters.py:96-99`, `src/requests/adapters.py:314-317`.

<!-- review-run head=4089f3dc65f783beaa53cc032958ab625440d0ac base-ref=main base-sha=8dd3b26bf59808de24fd654699f592abf6de581e merge-base=8dd3b26bf59808de24fd654699f592abf6de581e workflow=v5b-1 context=c0867eb8665714e98853874c7a66087e62cdd24962072b2681554acf99349763 issues=none coverage=complete -->

---

## Finding comments (rendered as they would post on their anchors)

### 1. `src/requests/adapters.py:94-95` (RIGHT)

**[P1] [must-fix] Stop sharing the preloaded SSLContext with client-certificate or hostname-override connections**

**Triggers when:** A session sends one HTTPS request with `verify=True` (the default) and a client certificate via `cert=`, then any later `verify=True` request — even without `cert=` — opens a new connection to a different host.

**Impact:** The shared, process-wide `_preloaded_ssl_context` created at import (`adapters.py:75-78`) is handed to every `verify=True` connection pool, including ones with a client certificate; urllib3's `ssl_wrap_socket()` calls `context.load_cert_chain()` on that same shared object, so the loaded certificate persists and gets presented to unrelated hosts afterward, and concurrent requests on different threads race on the same mutation. At the merge-base, `ssl_context` was never set for `verify=True`, so urllib3 built a private context per connection; this change removed that isolation.

**Change:** In `_urllib3_request_context()` (`adapters.py:94-107`), only pass `_preloaded_ssl_context` when the connection has no client certificate and no hostname-check override; otherwise build a private, connection-scoped `SSLContext` as before this change.

<!-- finding id=ssl-context-sharing/client-cert-mtls-leak head=4089f3dc65f783beaa53cc032958ab625440d0ac priority=P1 action=must-fix blocking=true kind=concurrency fix=src/requests/adapters.py:94-107 -->

### 2. `src/requests/adapters.py:75-78` (RIGHT)

**[P1] [must-fix] Don't load the default CA bundle eagerly at import time**

**Triggers when:** `DEFAULT_CA_BUNDLE_PATH` (certifi's bundle, or a distro/managed override of `requests.certs.where()` — a customization `certs.py`'s own docstring documents as supported) points at a path that is missing or unparseable when `adapters.py` is first imported.

**Impact:** `_preloaded_ssl_context.load_verify_locations(...)` (`adapters.py:75-78`) now runs unconditionally at `import requests` time, so a broken default bundle makes the bare import raise, breaking every caller in that process, including ones that only use `verify=False` or a custom CA bundle and never needed the default one. At the merge-base the same broken bundle only failed the specific `verify=True` request that used no override, inside `cert_verify()`'s existing `OSError` handling. Because the context is now built once, monkeypatching `DEFAULT_CA_BUNDLE_PATH` after import — a workaround that worked before — no longer has any effect either.

**Change:** Defer building and loading `_preloaded_ssl_context` until the first `verify=True` request that actually needs it, so import cannot fail merely because the default bundle is broken.

<!-- finding id=adapters/eager-ca-bundle-import-crash head=4089f3dc65f783beaa53cc032958ab625440d0ac priority=P1 action=must-fix blocking=true kind=bug -->

---

## Questions

None. Both survivors were fully resolvable from code, the installed dependency, and the review record; no candidate required a maintainer decision or a benchmark to settle.

## Would-be publication

Event: `COMMENT` (third-party review; gating not authorized; the target is merged so publication is disabled by default under a retrospective/audit review regardless). Commit: `4089f3dc65f783beaa53cc032958ab625440d0ac`. This payload validated with zero violations (`python3 scripts/validate_review.py`) and its `--emit-batch` render is the exact one-call GitHub review body that would have been submitted via `gh api --method POST repos/psf/requests/pulls/6667/reviews --input batch.json`, had publication been authorized. It was not submitted.
