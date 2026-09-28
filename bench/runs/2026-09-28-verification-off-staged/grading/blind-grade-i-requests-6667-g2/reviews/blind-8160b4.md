# Review blind-8160b4

### Item 1
Location: src/requests/adapters.py:94-95
Claim: Don't load a per-request client certificate onto the shared, process-wide SSL context. Any call anywhere in the process of `session.request(..., cert=(certfile, keyfile))` (or `cert=certfile`) with the default `verify=True`, together with any other `verify=True` request to a different host that does not itself pass `cert=`.
Consequence: `_urllib3_request_context()` hands out the single module-level `_preloaded_ssl_context` to every verify=True pool, cert or not. urllib3 calls `context.load_cert_chain(certfile, keyfile)` on whatever `ssl_context` it's given whenever `cert_file` is set, so one client-cert request permanently loads that certificate onto the shared object; every other verify=True connection in the process, to any host, then silently presents it too - a cross-host client-certificate leak, confirmed by a focused reproduction (fresh handshake with the shared context offers the cert; a same-built control context does not).
Fix: In `_urllib3_request_context()`, stop reusing `pool_kwargs["ssl_context"] = _preloaded_ssl_context` whenever `client_cert` is also set; build (or cache per client-cert-pair) a fresh SSLContext for that case instead, so a client certificate never gets loaded onto the shared default context.

### Item 2
Location: (no file)
Claim: `_preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))` now runs unconditionally at `requests.adapters` import time, whereas before this change the equivalent CA-bundle resolution only ran lazily, inside `cert_verify()`, the first time an HTTPS request with `verify=True` was actually made.
Consequence: src/requests/adapters.py:75-77.
Fix: —
