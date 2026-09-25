# Scorecard: i-requests-6667, mapping v1

Register v1 (78510f37a5a8), rubric v1, scored at 2026-09-25T20:49:28Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 4829aeaf4926cc5fe9d32ac8f4551bb33c44ec13958cd5941a952ccdf8ccfe1b; session 4aa1d91a-4041-40c6-a13e-d6d80c15d4e7; read audit clean.

## att-001 (claude-builtin-sonnet-high), blind-366dc4

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i1`, fix absent, priority error n/a, group none. Quotes: 'A single process-wide SSLContext is shared ... and urllib3 mutates it, including loading client certificates into it' / 'urllib3's ssl_wrap_socket calls context.load_cert_chain(...) on that shared context'. GT-i1 shared-mutation manifestation. No corrective change proposed: absent.
- item-1: `defect:GT-i2`, fix absent, priority error n/a, group none. Quotes: 'The default CA bundle is now loaded at import time, so a missing or unreadable bundle breaks import requests' / 'adds tens to hundreds of ms of startup cost ... even if they never make an HTTPS request'. GT-i2 mechanism with both import-failure and import-cost consequences. No change proposed: absent.
- item-2: `unresolved`, fix n/a, priority error n/a, group none. NC-1: Quotes: 'The default bundle path is frozen at import time, so runtime overrides of DEFAULT_CA_BUNDLE_PATH and certifi updates are silently ignored.' Merge-base cert_verify read DEFAULT_CA_BUNDLE_PATH per request; head builds once at adapters.py:75-78. Not in register; materiality needs adjudication.
- item-3: `non-material`, fix n/a, priority error n/a, group none. Quotes: 'The guard that verify=True has a usable CA bundle was removed' / 'Callers who caught or tested for that OSError see different behavior.' True, but the missing-bundle case now fails at import (item 2); the error-type change alone is below threshold.
- item-4: `non-material`, fix n/a, priority error n/a, group none. Quotes: 'verify=1 or verify=Path(...) fails both is True and isinstance(verify, str), so _urllib3_request_context sets neither' / 'The str type check in the pool context was already there'. At the merge-base _urllib3_request_context also set nothing for non-str truthy verify and cert_verify set conn.ca_certs=verify, so behaviour for these inputs is unchanged; pre-existing, as the item concedes. Not a defect of this change.
- item-5: `non-material`, fix n/a, priority error n/a, group none. Quotes: 'The isdir/ca_certs vs ca_cert_dir logic is duplicated in _urllib3_request_context and cert_verify'. Accurate maintainability remark (adapters.py:96-100, 314-317), no consequence.
- item-6: `non-material`, fix n/a, priority error n/a, group none. Quotes: 'Custom CA bundles (verify=str) and proxy or session-per-host pools still trigger load_verify_locations ... so the perf fix is partial.' Accurate scope observation, no regression.

## att-002 (codex-default), blind-576ff8

Verdict 'patch is incorrect'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i1`, fix partial, priority error False, group blind-576ff8:g1. Quotes: 'With verify=True and cert=..., urllib3 calls load_cert_chain() on this shared context' / 'Keep client-certificate contexts isolated rather than sharing the default context with them.' GT-i1 shared-mutation manifestation. Fix isolates cert contexts only; adapter override manifestation not addressed: partial.
- item-1: `defect:GT-i1`, fix partial, priority error False, group blind-576ff8:g1. Quotes: 'When an adapter supplies an ssl_context through init_poolmanager(), this per-request value overrides it: urllib3's _merge_pool_kwargs() gives request kwargs precedence' / 'Only select the preloaded context when the manager has no explicit context.' GT-i1 override manifestation. Fix is the #6716-style partial fix; shared mutation under cert= remains: partial.
- item-2: `non-material`, fix n/a, priority error False, group none. Quotes: 'On Python installations without the optional ssl module ... eagerly calling create_urllib3_context() raises during import requests.' Register non_defects: a real edge case later fixed by #6724 but out of scope for the pinned diff and not a material defect here.

## att-018 (review-code-sonnet-high), blind-970cab

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i1`, fix partial, priority error False, group none. Quotes: 'urllib3's ssl_wrap_socket calls load_cert_chain on the shared module-level context, so the client certificate stays loaded' / 'Fix: ... pass _preloaded_ssl_context only when client_cert is None'. GT-i1 shared-mutation manifestation with a concrete fix, but the init_poolmanager override manifestation is untouched: partial.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quotes: 'test_different_connection_pool_for_mtls_settings ... fails identically at the merge-base and the head with a certificate-expired error'. A test-environment observation, not a defect of the change.

## att-019 (claude-builtin-opus-high), blind-2a1665

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i1`, fix absent, priority error False, group blind-2a1665:g1. Quotes: 'client certificates passed via cert= get loaded into this shared context' / 'urllib3's ssl_wrap_socket runs context.load_cert_chain(certfile, keyfile) on the shared context'. Same mechanism as GT-i1's shared-mutation manifestation (adapters.py:94-95 injects _preloaded_ssl_context; urllib3 util/ssl_.py:431 load_cert_chain on the passed context). Item text proposes no change: absent.
- item-1: `defect:GT-i1`, fix absent, priority error False, group blind-2a1665:g1. Quotes: 'Adding ssl_context to the per-request pool_kwargs overrides any ssl_context a subclass set in init_poolmanager, because urllib3's _merge_pool_kwargs lets request-level values win'. Exactly GT-i1's override manifestation. No corrective change proposed: absent.
- item-2: `defect:GT-i2`, fix absent, priority error False, group blind-2a1665:g2. Quotes: 'The SSL context is built and CA bundle loaded unconditionally at import time' / 'load_verify_locations raises FileNotFoundError at import, instead of the old lazy OSError that only fired on an actual verify=True HTTPS request'. Identifies GT-i2's mechanism (adapters.py:75-78 runs at import) with an import-failure consequence analogous to #6764. The no-ssl half is a register non-defect but does not cancel the recovery. No change proposed: absent.
- item-3: `unresolved`, fix n/a, priority error n/a, group none. NC-2: Quotes: 'When verify=True, cert_verify no longer sets conn.ca_certs, so TLS to an HTTPS proxy (tunnel mode) now uses the OS trust store instead of certifi.' Checked urllib3 connection.py:962-968 (_connect_tls_proxy non-forwarding branch passes ssl_context=None, ca_certs=self.ca_certs) and connection.py:1061-1068 (load_default_certs when no CA given); head cert_verify (adapters.py:297-317) no longer sets ca_certs for verify=True while the merge-base did. Mechanism supported, not in register, not refuted: new candidate.
- item-4: `unresolved`, fix n/a, priority error n/a, group none. NC-1: Quotes: 'The trust store is frozen at import time, so trust-store changes made after import requests have no effect on verify=True requests' (truststore/pyopenssl injection after import, DEFAULT_CA_BUNDLE_PATH patching, bundle file replacement). At merge-base cert_verify re-read DEFAULT_CA_BUNDLE_PATH and urllib3 built a fresh context per pool; at head the context is built once at adapters.py:75-78. Not in register; plausible behaviour change whose materiality needs adjudication.
- item-5: `non-material`, fix n/a, priority error False, group none. Quotes: 'The old check that the default CA bundle exists, with its clear OSError, was removed for verify=True'. True (diff of cert_verify), but a missing default bundle now fails at import instead (covered as GT-i2 in item 3); the change of error type/message alone is below the finding threshold.
- item-6: `defect:GT-i1`, fix absent, priority error True, group blind-2a1665:g1. Quotes: 'urllib3 reconfigures the shared context on every connection (context.verify_mode = ..., set_alpn_protocols, and check_hostname = False when assert_hostname/assert_fingerprint is set), so one adapter's settings leak into all others'. Confirmed at urllib3 connection.py:1042-1056. This is GT-i1's shared-mutation mechanism (per-connection mutation of one process-wide context). The 'skips hostname checks entirely' remark applies only to pools that opted out; other pools fall back to manual match, as the item says. No change proposed: absent.
- item-7: `non-material`, fix n/a, priority error False, group none. Quotes: 'For a custom verify path, cert_verify still sets conn.ca_certs/ca_cert_dir ... the speedup only applies to verify=True, and the file-vs-directory logic is now duplicated.' Accurate scope/maintainability observation (adapters.py:96-100, 314-317); no regression versus merge-base.
- item-8: `defect:GT-i2`, fix sufficient, priority error True, group blind-2a1665:g2. Quotes: 'puts file I/O and zip extraction on the import path' / 'Every import requests pays for load_verify_locations and, for zipped installs, a temp-file extraction via extract_zipped_paths, even if no HTTPS request is ever made' / 'A lazily created context cached per HTTPAdapter ... would avoid both.' Names GT-i2's mechanism and consequence; a lazily created cached context moves the trigger from import to use, satisfying the required outcome.
- item-9: `non-material`, fix n/a, priority error False, group none. Quotes: 'No tests were added for the new verify=True / ssl_context path'. True of the diff (only adapters.py changed), test-coverage hygiene with no independent consequence.

## att-055 (review-code-sonnet-high), blind-e839d7

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i1`, fix partial, priority error False, group none. Quotes: 'urllib3 calls load_cert_chain() on the passed ssl_context, so the module-level _preloaded_ssl_context keeps the client identity' / 'Fix: ... set pool_kwargs["ssl_context"] = _preloaded_ssl_context only when client_cert is None'. GT-i1 shared-mutation manifestation; override manifestation not fixed: partial.
- item-1: `unresolved`, fix n/a, priority error n/a, group none. NC-3: Quotes: 'An HTTPAdapter subclass overriding send() calls self.get_connection(url) and then self.cert_verify(conn, url, True, cert)' / 'urllib3 loads the OS trust store instead of certifi'. Head get_connection (adapters.py:406-436) passes no ssl_context and cert_verify (adapters.py:297-317) no longer sets ca_certs for verify=True; urllib3 connection.py:1061-1068 then loads OS defaults. Not in register: candidate.
- item-2: `defect:GT-i2`, fix absent, priority error n/a, group none. Quotes: 'The default CA bundle is now read at import requests, so a missing or unreadable certifi bundle raises at import time'. Identifies GT-i2's mechanism (adapters.py:75-78 at import) with an import-failure consequence. No change proposed: absent.

## att-056 (claude-builtin-sonnet-high), blind-6c56bc

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i1`, fix partial, priority error n/a, group blind-6c56bc:g1. Quotes: 'urllib3's ssl_wrap_socket (util/ssl_.py:431) then calls context.load_cert_chain(...) on the global context' / 'Fix: use the shared context only when client_cert is None.' GT-i1 shared-mutation manifestation; fix leaves the init_poolmanager override manifestation in place: partial.
- item-1: `defect:GT-i2`, fix sufficient, priority error n/a, group none. Quotes: 'Loading the CA bundle at import time means a missing or unreadable bundle now raises when requests is imported, and it adds load_verify_locations cost to every import' / 'Fix: create the context lazily behind a lock and cache it.' GT-i2 mechanism and consequences; lazy creation moves the trigger from import to use, satisfying the required outcome. (The 0.7s upper figure is inflated but not load-bearing.)
- item-2: `unresolved`, fix n/a, priority error n/a, group none. NC-1: Quotes: 'The default bundle is frozen at import time' / 'Code or tests that patch requests.adapters.DEFAULT_CA_BUNDLE_PATH ... or that swap in a different certifi bundle after import, no longer affect verify=True.' Merge-base read the adapters global per request; head builds once at adapters.py:75-78. (Patching requests.utils.DEFAULT_CA_BUNDLE_PATH had no effect at base either.) Not in register; materiality needs adjudication.
- item-3: `unresolved`, fix n/a, priority error n/a, group none. NC-3: Quotes: 'subclasses or third-party adapters call it with a connection from get_connection ... gets CERT_REQUIRED but no CA source. Verification then relies on urllib3's default context, which does not load the certifi bundle' plus stale ca_certs on reused pools. Head get_connection (adapters.py:406-436) builds pools without ssl_context and cert_verify no longer sets ca_certs for verify=True, so urllib3 load_default_certs (connection.py:1061-1068) applies; base set certifi. get_connection is documented as for subclass use. Not in register: candidate.
- item-4: `non-material`, fix n/a, priority error n/a, group none. Quotes: 'The str-verify branch ... duplicates the isdir/ca_certs logic in cert_verify' / 'verify=\'\' is a str, so it reaches ca_certs=\'\' in pool_kwargs, while cert_verify treats it as falsy'. Duplication is accurate hygiene; the verify='' inconsistency is pre-existing (merge-base also set pool_kwargs['ca_certs']=verify for any str and cert_verify set CERT_NONE for falsy verify), so not introduced by this change.
- item-5: `defect:GT-i1`, fix absent, priority error n/a, group blind-6c56bc:g1. Quotes: 'The shared context is a mutable global ... used across all sessions and threads, and urllib3 mutates it (verify_mode, cert chain)' / 'leaks to every other Session in the process'. Restates GT-i1's shared-mutation mechanism already in item 1; no fix proposed: absent.

## att-057 (claude-builtin-opus-high), blind-ea13a6

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i1`, fix absent, priority error False, group blind-ea13a6:g1. Quotes: 'urllib3's ssl_wrap_socket calls context.load_cert_chain(certfile, keyfile) on that shared context whenever the request has a client cert'. GT-i1 shared-mutation manifestation; no fix: absent.
- item-1: `defect:GT-i1`, fix absent, priority error False, group blind-ea13a6:g1. Quotes: 'The per-request pool_kwargs[\'ssl_context\'] replaces any ssl_context a user subclass passes through init_poolmanager ... because PoolManager._merge_pool_kwargs lets per-request values win.' GT-i1 override manifestation; no fix: absent.
- item-2: `unresolved`, fix n/a, priority error n/a, group none. NC-2: Quotes: 'urllib3's _connect_tls_proxy (connection.py:962-969) takes the proxy's CA from self.ca_certs and passes ssl_context=None when not forwarding, so TLS to an HTTPS proxy now uses the OS default store'. Confirmed in urllib3 connection.py:962-968 and 1061-1068; head cert_verify no longer sets ca_certs for verify=True. Not in register: candidate.
- item-3: `defect:GT-i2`, fix absent, priority error False, group blind-ea13a6:g2. Quotes: 'The CA bundle is now loaded when the module is imported, so a missing or unreadable DEFAULT_CA_BUNDLE_PATH makes import requests fail. Before, it raised OSError only on an actual verify=True HTTPS request.' GT-i2 mechanism and import-failure consequence; no fix: absent.
- item-4: `unresolved`, fix n/a, priority error n/a, group none. NC-3: Quotes: 'A subclass or third-party adapter that gets pools through the public get_connection(url) and then calls cert_verify(conn, url, True, None) gets a pool with no ssl_context and no ca_certs, so it silently trusts the OS store instead of certifi.' Supported by adapters.py:297-317 and 406-436 plus urllib3 connection.py:1061-1068. Not in register: candidate.
- item-5: `unresolved`, fix n/a, priority error n/a, group none. NC-1: Quotes: 'The default trust store is captured once at import, so changes made after import to requests.adapters.DEFAULT_CA_BUNDLE_PATH ... and in-place certifi updates, no longer affect verify=True.' Merge-base re-read the adapters global per request; head builds once. Not in register; materiality needs adjudication.
- item-6: `defect:GT-i1`, fix absent, priority error False, group blind-ea13a6:g1. Quotes: 'The global context is also changed on every connection by urllib3 (context.verify_mode = ..., context.check_hostname = False when assert_hostname or assert_fingerprint is set ...)' / 'One adapter configured with assert_fingerprint or assert_hostname turns off check_hostname on the context shared by every other Session'. Confirmed at urllib3 connection.py:1042-1056; this is GT-i1's shared-mutation mechanism. No fix: absent.
- item-7: `defect:GT-i2`, fix sufficient, priority error False, group blind-ea13a6:g2. Quotes: 'Every import requests now pays for create_urllib3_context() plus a full load_verify_locations() ... and may extract the bundle from a zip ... even for programs that never make an HTTPS request' / 'Build the context lazily on the first verify=True request (e.g. a cached helper) instead.' GT-i2 import-cost manifestation; lazy first-use construction meets the required outcome.
- item-8: `non-material`, fix n/a, priority error False, group none. Quotes: 'The fix only applies to verify=True. Any string verify ... still sets ca_certs or ca_cert_dir' / 'The CA-path logic is also duplicated'. Accurate scope/maintainability observation; no regression versus merge-base.

## att-058 (codex-default), blind-918fa1

Verdict 'patch is incorrect'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-i1`, fix partial, priority error False, group blind-918fa1:g1. Quotes: 'urllib3 calls load_cert_chain() on this shared context. The client identity then remains installed' / 'Avoid sharing this context with connections that load client certificates.' GT-i1 shared-mutation manifestation; fix doesn't address the override manifestation: partial.
- item-1: `defect:GT-i1`, fix partial, priority error False, group blind-918fa1:g1. Quotes: 'For adapters configuring PoolManager with a custom ssl_context, these per-request kwargs overwrite that context whenever verification is enabled' / 'Only select the preloaded context when the adapter has no conflicting TLS configuration.' GT-i1 override manifestation (ssl_version bypass also true: urllib3 only builds a context from ssl_version when none is given; docs/user/advanced.rst:1017-1033). Fix leaves shared mutation under cert=: partial.
- item-2: `non-material`, fix n/a, priority error False, group none. Quotes: 'On Python installations without the ssl module ... create_urllib3_context() raises during import.' Register non_defects: real edge case fixed later by #6724, out of scope and not a material defect of the pinned diff.

## New candidates

### NC-1

- Claim: The default trust store is captured once at import (adapters.py:75-78), so trust changes made after import (truststore/pyopenssl injection, reassigning requests.adapters.DEFAULT_CA_BUNDLE_PATH, replacing the certifi bundle file in a long-running process) no longer affect verify=True requests, whereas the merge-base re-read the bundle per pool/connection.
- Evidence: Merge-base cert_verify evaluated extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH) (module global) per request and urllib3 built a fresh context per pool; head builds _preloaded_ssl_context once at import and injects it for every verify=True pool. Mechanism true; not in the register; whether post-import mutation of these globals or late truststore injection is a supported contract is not settled by the clone.
- Confidence: medium
- Would settle: Adjudication of whether post-import trust-store changes (notably truststore.inject_into_ssl() after importing requests) are supported behaviour, e.g. upstream issue reports against 2.32.x, and a reproduction showing base honours and head ignores the change.
- Items: att-019 item-4 (blind-2a1665 item 5), att-001 item-2 (blind-366dc4 item 3), att-056 item-2 (blind-6c56bc item 3), att-057 item-5 (blind-ea13a6 item 6)

### NC-2

- Claim: With verify=True and an HTTPS proxy in tunnel mode, the TLS connection to the proxy is now verified against the OS default trust store rather than the certifi bundle, because cert_verify no longer sets conn.ca_certs and urllib3's _connect_tls_proxy uses ssl_context=None with ca_certs=self.ca_certs for non-forwarding proxies.
- Evidence: urllib3 2.8.0 connection.py:962-968 (non-forwarding: ssl_context=None, ca_certs=self.ca_certs) and 1061-1068 (load_default_certs when no CA given); head adapters.py:297-317 sets no ca_certs for verify=True, merge-base set the certifi path. Not reproduced end to end.
- Confidence: medium
- Would settle: A local reproduction with an HTTPS proxy whose certificate chains to a certifi-only root (or an empty OS store) at merge-base and head, observing which CA set verifies the proxy.
- Items: att-019 item-3 (blind-2a1665 item 4), att-057 item-2 (blind-ea13a6 item 3)

### NC-3

- Claim: Adapters/subclasses that obtain pools through the public get_connection(url) and then call cert_verify(conn, url, True, cert) now get pools with no ssl_context and no ca_certs, so verification silently uses the OS trust store instead of certifi (and a pool reused after a verify=<path> call keeps the stale ca_certs).
- Evidence: Head get_connection (adapters.py:406-436) builds pools via connection_from_url with no ssl_context; head cert_verify (adapters.py:297-317) only sets cert_reqs for verify=True; urllib3 connection.py:1061-1068 loads OS defaults when no CA is given. Merge-base cert_verify set conn.ca_certs to the certifi bundle. get_connection is documented as exposed for subclassing.
- Confidence: medium
- Would settle: Adjudication of whether the get_connection+cert_verify subclass path is a supported contract at this revision, and a reproduction showing base trusts certifi while head trusts the OS store on that path.
- Items: att-056 item-3 (blind-6c56bc item 4), att-055 item-1 (blind-e839d7 item 2), att-057 item-4 (blind-ea13a6 item 5)
