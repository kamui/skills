# Review blind-73f628

### Item 1
Location: src/requests/adapters.py:94-95
Claim: Don't hand the shared preloaded SSLContext to client-cert connections. A process makes one verify=True request with a client certificate (`requests.get(url_a, cert=(certfile, keyfile))`, the documented mTLS usage) and, in the same process at any later point while the interpreter is alive, a verify=True request to a different, unrelated host with no client certificate (`requests.get(url_b)`).
Consequence: `_urllib3_request_context()` puts the same module-level `_preloaded_ssl_context` object into `pool_kwargs['ssl_context']` for every verify=True pool, regardless of client_cert. urllib3's `ssl_wrap_socket()` calls `context.load_cert_chain(certfile, keyfile)` on whatever ssl_context object a pool was built with, so loading url_a's client certificate mutates the same context object url_b's unrelated, no-client-cert pool also holds. url_b's connection then presents url_a's client certificate, silently leaking a TLS client-authentication credential to a host that should never receive it. Confirmed by tracing urllib3's connection/pool code and by an offline reproduction, independently re-executed by the verifier.
Fix: In `_urllib3_request_context()` (src/requests/adapters.py:94-95), only reuse `_preloaded_ssl_context` when `client_cert` is None; when a client certificate is supplied, do not hand out the shared context (e.g. let urllib3 build its own default per-pool context, or pass a fresh copy) so `load_cert_chain()` never mutates state shared with unrelated pools.

### Item 2
Location: (no file)
Claim: The default-CA-bundle SSLContext is now built and loaded at `import requests.adapters` time (module level) rather than lazily on the first verify=True request, so any failure loading the default bundle now surfaces at import instead of at first HTTPS call.
Consequence: src/requests/adapters.py:75-78; this was the behavior mm-matthias explicitly asked for in the PR's non-review conversation ("it happens on the first connection (vs. module init time). This creates noise in our live profiles.") and the module-level sharing was discussed for thread-safety in the same thread, so this is a deliberate, discussed tradeoff, not a candidate finding.
Fix: —
