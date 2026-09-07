# Review payload — `psf/requests#6667` (i-867cf3ff-seed1-att-02)
Retrospective, non-publishing review. Rendered exactly as it would be posted as one
forge-native GitHub review (`event=COMMENT`, `commit_id=4089f3dc65f783beaa53cc032958ab625440d0ac`) if publication were authorized.

---

## Summary (review body)

**Changes Requested (advisory)** — 2 must-fix findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Avoid redundant `SSLContext.load_verify_locations()` calls when `verify=True`, by caching the default CA bundle in a module-level `SSLContext` reused across requests, to cut per-request TLS overhead under concurrent load.

**Issue fit:** No linked issue; the pull-request body is the only statement of intent (no formal acceptance criteria). Its stated primary goal — avoid reloading root certificates when `verify=True` and no custom CA is supplied — is achieved for that case, but the same caching mechanism creates a cross-request client-certificate leak when combined with `cert=` (see finding below) and moves a previously lazy CA-bundle failure to import time (see finding below).

**Coverage:** Complete merge-base diff reviewed (single file, `src/requests/adapters.py`, +28/−18); the installed urllib3 2.7.0 internals it depends on, and the repository's existing local-TLS test fixtures, were inspected; two focused, offline reproductions were run to confirm both findings.

**Reviewed:** `4089f3d` against merge-base `8dd3b26`.

## Findings

- [P1] [must-fix] Stop reusing the shared default SSLContext when a client certificate is set — anchor [`src/requests/adapters.py:94-102`](https://github.com/psf/requests/blob/4089f3dc65f783beaa53cc032958ab625440d0ac/src/requests/adapters.py?plain=1#L94-L102); fix [`src/requests/adapters.py:95`](https://github.com/psf/requests/blob/4089f3dc65f783beaa53cc032958ab625440d0ac/src/requests/adapters.py?plain=1#L95)
- [P2] [must-fix] Don't load the default CA bundle unconditionally at import time — anchor [`src/requests/adapters.py:75-78`](https://github.com/psf/requests/blob/4089f3dc65f783beaa53cc032958ab625440d0ac/src/requests/adapters.py?plain=1#L75-L78)

## Observations

- The shared `_preloaded_ssl_context`'s `verify_mode` is reassigned on every `verify=True` connection, not only its client-identity certificate, since urllib3's connection-establishment path applies `cert_reqs`-derived `verify_mode` to whichever context it receives. Evidence: `src/requests/adapters.py:298`, `urllib3/connection.py:901-937`.

<!-- review-run head=4089f3dc65f783beaa53cc032958ab625440d0ac base-ref=main base-sha=8dd3b26bf59808de24fd654699f592abf6de581e merge-base=8dd3b26bf59808de24fd654699f592abf6de581e workflow=v5b-1 context=9e80f1a16f93243a31dff067dd6ba49658a84f52b2a0216860c03ff210cf8621 issues=none coverage=complete -->

---

## Finding comment 1 — inline on `src/requests/adapters.py:94-102` (RIGHT)

**[P1] [must-fix] Stop reusing the shared default SSLContext when a client certificate is set**

**Triggers when:** In one process, one `verify=True` request supplies a client certificate
(`session.get(url_a, verify=True, cert=(certA, keyA))`), then another `verify=True` request to
any other host supplies no `cert=` at all.

**Impact:** `_urllib3_request_context()` hands the same module-level `_preloaded_ssl_context`
object to every `verify=True` pool. urllib3's `ssl_wrap_socket()` calls
`context.load_cert_chain(certfile, keyfile)` on that shared object whenever a connection carries
a client certificate, and nothing ever clears it. The later, cert-less request still presents the
earlier request's client certificate to its own server — a deterministic, single-process
credential leak, not merely a race.

**Change:** In `src/requests/adapters.py`, stop passing `_preloaded_ssl_context` as
`pool_kwargs["ssl_context"]` when `client_cert is not None`; build a context/pool_kwargs
combination scoped to that specific client certificate instead, so `load_cert_chain()` never
mutates state another request also reads.

<!-- finding id=adapters/shared-ssl-context-client-cert-leak head=4089f3dc65f783beaa53cc032958ab625440d0ac priority=P1 action=must-fix blocking=true kind=security fix=src/requests/adapters.py:95 -->

---

## Finding comment 2 — inline on `src/requests/adapters.py:75-78` (RIGHT)

**[P2] [must-fix] Don't load the default CA bundle unconditionally at import time**

**Triggers when:** The default CA bundle path (`certifi.where()`) is missing or unreadable in
the running environment — regardless of whether the caller ever verifies a certificate with it.

**Impact:** `src/requests/adapters.py` now calls `_preloaded_ssl_context.load_verify_locations(...)`
unconditionally at module import time. `import requests` now raises `OSError`/`FileNotFoundError`
and fails completely, even for callers using `verify=False`, a custom CA bundle string, or no
HTTPS at all. At the merge-base this same check ran only lazily, inside `cert_verify()`, gated on
an actual HTTPS request needing the default bundle.

**Change:** Defer creating and loading `_preloaded_ssl_context` until the first `verify=True`
HTTPS request actually needs it, so a broken default CA bundle only affects callers who verify
with it.

<!-- finding id=adapters/eager-default-ca-bundle-load-at-import head=4089f3dc65f783beaa53cc032958ab625440d0ac priority=P2 action=must-fix blocking=true kind=bug -->

