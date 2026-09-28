# Review blind-1b8884

### Item 1
Location: src/requests/adapters.py:75-78
Claim: Don't let a missing CA bundle crash `import requests`. `adapters.py:75-78` builds `_preloaded_ssl_context` from `DEFAULT_CA_BUNDLE_PATH` unconditionally at module import. Patching `certifi.where()` to a missing path and running `import requests` reproduces an immediate `FileNotFoundError`.
Consequence: Every `import requests` now fails whenever the default CA bundle is missing or unreadable — even for callers who never verify TLS. At the merge-base the same lookup ran only inside `cert_verify()`, so it fired solely for a verified HTTPS request and raised a controlled `OSError` there instead.
Fix: Build `_preloaded_ssl_context` lazily on first `verify=True` use, or wrap its construction in the same failure handling `cert_verify()` applied, so a broken default bundle fails only a verified request, not `import requests` itself.

### Item 2
Location: (no file)
Claim: `_urllib3_request_context`'s new `os.path.isdir(verify)` check duplicates the `os.path.isdir(cert_loc)` check `cert_verify()` still performs for the same path, exactly as the PR author notes in the PR body.
Consequence: src/requests/adapters.py, `_urllib3_request_context` and `cert_verify`.
Fix: —

### Item 3
Location: (no file)
Claim: A third local test, `test_different_connection_pool_for_mtls_settings`, also fails beyond the two failures the run policy names, but its failing assertion exercises the unchanged `verify=False`/mutual-TLS code path, byte-identical at base and head, so it is unrelated to this diff.
Consequence: pytest run of `tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_mtls_settings` at the reviewed head; `git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py`.
Fix: —
