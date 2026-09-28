# Review blind-f97b84

### Item 1
Location: src/requests/adapters.py:75-78
Claim: Defer the CA-bundle preload instead of running it at import. `import requests` now unconditionally runs `_preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))` at module load, before any request is made or any `verify` value is known.
Consequence: If the default CA bundle (`certifi.where()`) is missing, stripped, or unreadable, the bare import now raises an unhandled `FileNotFoundError` and crashes the whole process — even programs that only ever pass `verify=False` or an explicit CA path and never touch the default bundle. Reproduced directly: with a broken bundle path, `import requests` succeeds at the merge-base (the check was lazy, inside `cert_verify()`, only for a default-bundle verified request, and raised a clear `requests`-style `OSError`) but fails at head.
Fix: Move the `create_urllib3_context()`/`load_verify_locations()` pair behind a function invoked only from the `verify is True` branch of `_urllib3_request_context` (e.g. cache it with `functools.lru_cache`), so the load stays lazy and any failure still reaches only default-bundle-verified callers with the previous clear error.

### Item 2
Location: (no file)
Claim: urllib3 2.8.0's `_ssl_wrap_socket_and_match_hostname` runs `context.verify_mode = resolve_cert_reqs(cert_reqs)` on every connect, including for the shared `_preloaded_ssl_context`; this looked like the reconfiguration hazard tiran warned about in review, but it always writes the same `CERT_REQUIRED` value back (the shared context is only ever used on the `verify=True` path), so it is a redundant write, not an observed defect.
Consequence: urllib3/connection.py:1040-1042 (installed 2.8.0); src/requests/adapters.py:91-99 only reaches the `_preloaded_ssl_context` branch when `verify is True`, which always pairs with `cert_reqs="CERT_REQUIRED"`.
Fix: —
