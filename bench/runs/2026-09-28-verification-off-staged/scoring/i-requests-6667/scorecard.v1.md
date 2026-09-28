# Scorecard: i-requests-6667, mapping v1

Register v2 (af11241069d2), rubric v1, scored at 2026-09-28T07:06:16Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 de1e2dd406085c9ce538d2f8cb7762c45984eccd1105c202851e9531963ff9c8; session 489b6800-8a69-4df2-8cb0-e768232225c0; read audit clean.

## att-003 (review-code-sonnet-high-enforced-verification-off), blind-b155bc

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i1`, fix partial, priority error False, group none. Quote: "_urllib3_request_context (adapters.py:95) hands that connection the single module-level _preloaded_ssl_context; urllib3 (2.8.0) then calls context.load_cert_chain() directly on it, with no copy, permanently embedding the client cert in the shared singleton. Every later verify=True connection to any host then presents that same client identity". This is GT-i1's shared-mutation manifestation: at head adapters.py:94-95 injects the module-level context for verify=True, and urllib3's ssl_wrap_socket calls load_cert_chain on the supplied context. The register gives the same mechanism ("a client certificate supplied on one thread is loaded into the context every other thread is handshaking with"). The cross-host identity consequence follows from OpenSSL context-level cert state, so it is a recovery. Fix: "set conn.ssl_context = None before assigning conn.cert_file/conn.key_file" in cert_verify. That targets only the cert= manifestation, not the discarded init_poolmanager ssl_context override. It is also ineffective as written: on urllib3 2.8.0 the per-request ssl_context lives in pool.conn_kw and is passed through **self.conn_kw in HTTPSConnectionPool._new_conn (urllib3/connectionpool.py:1098-1115), and the pool has no ssl_context attribute for the assignment to clear. Partial.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "No test in the suite exercises _urllib3_request_context or _preloaded_ssl_context directly". Verified: a grep of clone/tests finds no matches. This is a true test-coverage observation with no defect or consequence of its own, so it is below the finding threshold.

## att-004 (review-code-sonnet-high-enforced-x394-control), blind-335d69

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i3`, fix partial, priority error False, group none. Quote: "A subclass overrides send() to call the older, still-public self.get_connection(url, proxies) ... then calls self.cert_verify(conn, url, True, cert)" / "The resulting pool has cert_reqs='CERT_REQUIRED' but ca_certs=None ... urllib3's ssl_wrap_socket() then falls back to ssl.SSLContext.load_default_certs() (the OS trust store) instead of requests' pinned certifi bundle". This is exactly GT-i3's manifestation (b): at head cert_verify (clone/src/requests/adapters.py:297-317) sets only cert_reqs for verify=True and no longer sets conn.ca_certs to the certifi bundle, so pools from get_connection() verify against the OS store. Mechanism and required outcome (restore certifi for verify=True in cert_verify) match, so it is a recovery. Fix: "when verify is True, also set ... conn.ssl_context = _preloaded_ssl_context". This is partial at best. On urllib3 2.8.0 HTTPSConnectionPool has no ssl_context attribute: _new_conn (urllib3/connectionpool.py:1076-1115) builds connections from self.ca_certs etc. plus **self.conn_kw, so an assignment to pool.ssl_context is ignored. The fix also does not cover the HTTPS-proxy leg or reset a stale ca_certs left by an earlier verify=<path>. And if it did take effect, pairing a stale ca_certs with the shared context would make urllib3 load_verify_locations into the global context, which makes GT-i1 worse.

## New candidates

None.
