# Rulings: psf/requests#6667 (head 4089f3dc, merge-base 8dd3b26b)

| Claim | Ruling | Notes |
|---|---|---|
| NC-1 | not-material (true-sub-threshold) | Trust changes made after import are ignored at head. The mechanism is true, but it only affects unsupported interfaces and no consequence has been shown. |
| NC-2 | **material** (new) | The TLS leg to an HTTPS proxy is verified against the OS store instead of certifi. Same defect as NC-3. |
| NC-3 | **material** (new) | The `get_connection()` + `cert_verify(verify=True)` path uses the OS store instead of certifi, and a stale `ca_certs` survives on the pool. Same defect as NC-2. |

NC-2 and NC-3 share one root cause and one required outcome. They should become **one** new register entry (proposed GT-i3) with several manifestations. The `defect` blocks in `rulings.json` are identical for this reason.

## The change in question

`git diff main...HEAD -- src/` shows that head `cert_verify()` removes the verify=True default:

```
-            if not cert_loc:
-                cert_loc = extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH)
...
-            conn.cert_reqs = "CERT_REQUIRED"
-            if not os.path.isdir(cert_loc):
-                conn.ca_certs = cert_loc
```

At head, verify=True only sets `conn.cert_reqs = "CERT_REQUIRED"`. Trust now depends entirely on `_urllib3_request_context` injecting `pool_kwargs["ssl_context"] = _preloaded_ssl_context`. That context is used only for the destination handshake of pools built by the private `_get_connection`.

When urllib3 gets no CA, it falls back to the OS store. This is the same in 2.2.1 (fetched to `clone-work/u221_connection.py`, lines 692-717 and 784-794) and in the installed 2.8.0 (`connection.py` 962-968 and 1061-1068):

```
    if (not ca_certs and not ca_cert_dir and not ca_cert_data and default_ssl_context
        and hasattr(context, "load_default_certs")):
        context.load_default_certs()
```

For the proxy leg, `_connect_tls_proxy` passes `ca_certs=self.ca_certs` with `ssl_context=proxy_config.ssl_context` in 2.2.1. That context is None unless `proxy_ssl_context` is given, and requests never gives one. The 2.8.0 code is equivalent for tunnels (`ssl_context = self.ssl_context if self.proxy_is_forwarding else None`).

## Reproduction setup (all scratch files under `clone-work/`)

- `gen.py` uses trustme to create two independent roots. `certifi_ca` stands in for the certifi bundle: certifi is pointed at it by setting `certifi.core._CACERT_PATH` before `import requests`, as the #6726 reproducer does. `os_ca` stands in for the OS store, through `SSL_CERT_FILE=pki/os_ca.pem` and an empty `SSL_CERT_DIR`. Each root has a `localhost` leaf.
- `common.py` provides a threaded HTTPS server and a TLS-listening CONNECT proxy (an HTTPS proxy).
- The merge-base sources come from `git -C clone archive main src | tar -x -C clone-work/base`. The head is `clone/src`. The clone was not modified: `git status --short --ignored` is empty and HEAD is 4089f3dc.

Command, run for `rev` in base and head and `t` in nc3, nc2, nc1:

```
env -u HTTPS_PROXY -u https_proxy -u HTTP_PROXY -u http_proxy -u ALL_PROXY -u NO_PROXY -u no_proxy \
    -u REQUESTS_CA_BUNDLE -u CURL_CA_BUNDLE SSL_CERT_FILE=$PWD/pki/os_ca.pem SSL_CERT_DIR=$PWD/pki/emptydir \
    PYTHONPATH=$S:$PWD PYTHONDONTWRITEBYTECODE=1 timeout 120 ../clone-cache/venv/bin/python $t.py
```

(`S` is `clone-work/base/src` or `clone/src`. Python 3.13.15, OpenSSL 3.5.8, urllib3 2.8.0.)

Output:

```
===== base nc3
send() default path, verify=True, certifi-rooted server:  OK 200
get_connection+cert_verify subclass, verify=True, certifi-rooted server:  OK 200
send() default path, verify=True, OS-rooted server:  FAIL SSL certificate verify failed: unable to get local issuer certificate
get_connection+cert_verify subclass, verify=True, OS-rooted server:  FAIL SSL certificate verify failed: unable to get local issuer certificate
after verify=<os_ca path>: conn.ca_certs = os_ca.pem
after verify=True:          conn.ca_certs = certifi_ca.pem
===== base nc2
proxy cert chains to certifi root:  OK 200
proxy cert chains to certifi root, verify=<certifi path> control:  OK 200
proxy cert chains to OS root:  FAIL SSL certificate verify failed: unable to get local issuer certificate
proxy cert chains to OS root, verify=<certifi path> control:  FAIL SSL certificate verify failed: unable to get local issuer certificate
===== base nc1
baseline: certifi-rooted OK 200 | OS-rooted FAIL SSL certificate verify failed: unable to get local issuer certificate
(a) after reassigning requests.adapters.DEFAULT_CA_BUNDLE_PATH -> os_ca: certifi-rooted FAIL SSL ... | OS-rooted OK 200
(b) after rewriting the bundle file with os_ca: certifi-rooted FAIL SSL ... | OS-rooted OK 200
===== head nc3
send() default path, verify=True, certifi-rooted server:  OK 200
get_connection+cert_verify subclass, verify=True, certifi-rooted server:  FAIL SSL certificate verify failed: unable to get local issuer certificate
send() default path, verify=True, OS-rooted server:  FAIL SSL certificate verify failed: unable to get local issuer certificate
get_connection+cert_verify subclass, verify=True, OS-rooted server:  OK 200
after verify=<os_ca path>: conn.ca_certs = os_ca.pem
after verify=True:          conn.ca_certs = os_ca.pem
===== head nc2
proxy cert chains to certifi root:  FAIL SSL certificate verify failed: unable to get local issuer certificate
proxy cert chains to certifi root, verify=<certifi path> control:  OK 200
proxy cert chains to OS root:  OK 200
proxy cert chains to OS root, verify=<certifi path> control:  FAIL SSL certificate verify failed: unable to get local issuer certificate
===== head nc1
baseline: certifi-rooted OK 200 | OS-rooted FAIL SSL certificate verify failed: unable to get local issuer certificate
(a) after reassigning requests.adapters.DEFAULT_CA_BUNDLE_PATH -> os_ca: certifi-rooted OK 200 | OS-rooted FAIL SSL ...
(b) after rewriting the bundle file with os_ca: certifi-rooted OK 200 | OS-rooted FAIL SSL ...
```

I did not run the pytest suite; no claim here depends on existing tests.

## Upstream evidence consulted (public GitHub API, gitlab API)

- **#6726** (2024-05-29). jeffreytolar: "2.32.x isn't passing a CA bundle to urllib3 … that causes urllib3 to load the OS default, rather than using `certifi`". sigmavirus24: "I thought the optimization broke the zipped paths extraction".
- **#6710**, comments 2137799723 and 2137802782. A custom adapter got CERTIFICATE_VERIFY_FAILED; "I need to add `context.load_default_certs()` … It wasn't required before". nateprewitt: "We may not be loading the cert bundle the same as we were previously."
- **#6730**, "Certificate loading regression with HTTPAdapters in 2.32.3", and its duplicate **#6736**. jaraco reports "widespread breakage" (httpie, IBM SDKs, requests_pkcs12).
- **#6731** (draft by nateprewitt): "ensuring that when opting out of the default SSLContext, we're still supplying to the default CA Cert bundle correctly". It was closed in favour of #6767.
- **#6767**, the revert, merged 2025-06-13 and released in 2.32.5. It restores `cert_loc = extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH)` and `conn.ca_certs = cert_loc` in `cert_verify`.
- **#6715**. nateprewitt: "`truststore` MUST be imported before any networking code for either urllib3 or Requests. `inject_into_ssl()` is not an intended entry point for any library or package code."
- **gitlab alelec/pip-system-certs#27**. The v4.0 `wrapt_requests.py` breaks through its `init_poolmanager(ssl_context=…)` override, which is GT-i1, not a post-import trust change.
- **Docs at head.** `docs/user/advanced.rst:652-662`: "using a proxy for https connections typically requires your local machine to trust the proxy's root certificate. By default the list of certificates trusted by Requests can be found with `from requests.utils import DEFAULT_CA_BUNDLE_PATH`", overridable through `REQUESTS_CA_BUNDLE`. Lines 282-283: "Requests uses certificates from the package certifi."

## NC-1: not-material (true-sub-threshold)

**True at head, and introduced by this PR.** Nc1 output (a) and (b) show that the merge-base honours both a post-import reassignment of `requests.adapters.DEFAULT_CA_BUNDLE_PATH` and an on-disk rewrite of the bundle, while the head ignores both. The head's trust set is frozen by the import-time `_preloaded_ssl_context`.

**Not in the register.** GT-i2 is about *where* the load runs (import versus first use). A lazily cached context would satisfy GT-i2 and still ignore later changes, so this is a different outcome. It matches no `non_defects` entry.

**Not material.** Every trigger is outside a supported interface, and no consequence has been shown:

- `requests.adapters.DEFAULT_CA_BUNDLE_PATH` is an undocumented module global. The docs present `requests.utils.DEFAULT_CA_BUNDLE_PATH` only as something to print, and give `REQUESTS_CA_BUNDLE`/`CURL_CA_BUNDLE` or `verify=<path>` as the override. Those are resolved per request and still work at head.
- The maintainers explicitly require truststore to be injected before requests is imported (#6715).
- Replacing the certifi file on disk under a running process has no report anywhere I could find.
- The one plausibly related report (pip-system-certs) traces to GT-i1.

Late truststore and pyOpenSSL injection were not executed (truststore is not installed); that part rests on reading the code and on the maintainer statement.

**Proposed non_defect:** "The verify=True default trust store is captured at import, so post-import reassignment of `requests.adapters.DEFAULT_CA_BUNDLE_PATH`, late truststore/pyOpenSSL injection or on-disk bundle replacement is not seen. True, but these are unsupported mechanisms with no demonstrated consequence, and the documented overrides are unaffected."

**Counter-argument.** The merge-base honoured all of these, and the revert restored per-connection loading. I reject this: the revert was motivated by GT-i1/GT-i2-class failures and by the NC-2/NC-3 defect below, not by this one.

## NC-2 and NC-3: material, one new defect

**Title.** `cert_verify()` no longer supplies the default (certifi) CA bundle for verify=True. As a result, any verified TLS handshake that does not receive `_preloaded_ssl_context` falls back to the OS trust store, or keeps a stale custom CA.

**True at head, and introduced by this PR.** See the nc2 and nc3 output above. Each ruling is a mirror image across the two revisions: whatever succeeds at the merge-base fails at head, and vice versa. The stock `send()` path and the `verify=<path>` controls behave the same at both revisions, which isolates the fault to the removed default in `cert_verify`.

**Manifestations:**

1. **NC-2.** The TLS leg to an HTTPS proxy is verified against the OS store. This contradicts the documented statement that the proxy's root must be in `DEFAULT_CA_BUNDLE_PATH`.
2. **NC-3.** Pools from the public `get_connection(url)` followed by `cert_verify(conn, url, True, cert)` are verified against the OS store. This covers `send()`-overriding subclasses and, from 2.32.2, the maintainers' recommended `get_connection_with_tls_context` → `get_connection` pass-through.
3. **NC-3.** A `get_connection` pool reused after `verify=<path>` keeps `ca_certs=<path>` for a later verify=True call (reproduced: `conn.ca_certs = os_ca.pem` at head, `certifi_ca.pem` at the merge-base).
4. **Post-merge exposure.** Once GT-i1's override was lifted by #6716, custom `init_poolmanager` contexts lost certifi (#6730/#6736).

**Consequences:**

- CERTIFICATE_VERIFY_FAILED wherever certifi trusts the peer but the OS store does not: python.org macOS builds without "Install Certificates", slim containers, and the setup reproduced here.
- A silent widening of trust wherever the OS store holds roots that certifi does not.

**Not in the register.** GT-i1's required outcome (the subclass's context must be the one used) was met by #6716, yet this failure remained and was reported as #6730. GT-i2 is about import-time placement. None of the `non_defects` covers it. It is the concrete, consequential form of the "cert_verify changed" concern: upstream fixed it by restoring exactly the removed lines (#6767).

**Required outcome.** For verify=True, every TLS handshake requests performs or configures must verify against the default CA bundle (`DEFAULT_CA_BUNDLE_PATH`/certifi, zip-extracted as before), exactly as the merge-base did. That covers the destination, the HTTPS-proxy leg, and pools reached through `get_connection()`/`cert_verify()`. `cert_verify(..., True, ...)` must also reset any custom CA previously set on the pool. The mechanism is not prescribed.

**Counter-arguments:**

- *Proxy leg (NC-2).* TLS to an HTTPS proxy is uncommon, most proxy users set `REQUESTS_CA_BUNDLE` (a string, so unaffected), and no upstream report names the proxy leg.
- *Subclass path (NC-3).* The stock `send()` at this head already bypasses `get_connection`.
- *Both.* OS stores often contain certifi's roots, so many users would never notice.

I do not accept these as bringing the defect below the bar:

- The failure is reproduced end to end at both revisions.
- It contradicts documented behaviour for HTTPS proxies and for the documented subclassing hooks.
- The same cause produced the widely reported #6730/#6736/#6710 regressions, and upstream acknowledged it ("Address certificate loading regression", #6731) and fixed it in the revert.
