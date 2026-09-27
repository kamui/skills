# Scorecard: i-requests-6667, mapping v1

Register v2 (af11241069d2), rubric v1, scored at 2026-09-27T07:10:14Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 d0beaae98a265be05177b6f4f94aec6f936d4ef470366a4c67f3915ea71cca0c; session 9f897b2c-e3ff-46ab-969a-e3c076856587; read audit clean.

## att-001 (review-code-sonnet-high), blind-e4730e

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i1`, fix partial, priority error False, group none. Quote: "`_urllib3_request_context()` puts the module-level singleton `_preloaded_ssl_context` into `pool_kwargs['ssl_context']` for every `verify=True` connection, and urllib3's `ssl_wrap_socket()` calls `context.load_cert_chain(certfile, keyfile)` directly on whatever `ssl_context` object it is given ... loading one connection's client certificate onto it can leak into, race with, or overwrite another connection's handshake." This is GT-i1's shared-mutation manifestation with the exact mechanism the register gives (clone/src/requests/adapters.py:75-78 and 94-95 at head; urllib3 ssl_wrap_socket load_cert_chain), so it is a recovery. Fix: "change `elif verify is True:` to `elif verify is True and client_cert is None:`". That keeps cert= requests off the shared context, which confines in-place mutation, but it leaves the other manifestation untouched: a subclass's init_poolmanager ssl_context is still overridden by the preloaded context for every verify=True request with no cert. So the fix only partly meets the required outcome.
- item-1: `defect:GT-i2`, fix partial, priority error False, group none. Quote: "The module now calls `_preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))` unconditionally at import time ... At the merge-base, the equivalent CA-bundle existence check ran lazily inside `cert_verify()` ... the new eager module-level call raises a raw, unhandled `FileNotFoundError`/`ssl.SSLError` at `import requests` time." This names GT-i2's mechanism, CA-bundle loading moved from lazy per-request execution to eager import-time execution, and its manifestation that `import requests` itself fails even when no HTTPS request is made (the same class of failure as #6764's PermissionError). The facts check out: adapters.py:75-78 at head, and the diff shows cert_verify now checks the path only `if verify is not True`. Fix: "try/except around it, and reproduce the historical friendly OSError lazily". That stops the import crash, but the extraction and load_verify_locations still run unconditionally at import, so the import-time cost regression remains and the required outcome (the work is triggered by use, not import) is not met. Partial.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "Neither this PR nor the existing suite adds a test exercising `verify=True` together with a client certificate (`cert=`) ... `test_different_connection_pool_for_mtls_settings` only exercises `verify=False` plus `cert=`." This is an observation about missing test coverage. It proposes no fix and asserts no defect of its own; the defect it points at is already covered by Item 1. It is below the finding threshold.

## New candidates

None.
