# Review blind-33d937

### Item 1
Location: src/requests/adapters.py:297-317
Claim: Restore CA trust configuration for connections obtained via get_connection(). A subclass overrides send() to call the older, still-public self.get_connection(url, proxies) -- kept specifically "without breaking things" per the comment above _get_connection() -- instead of self._get_connection(request, verify, ...), then calls self.cert_verify(conn, url, True, cert): the exact shape HTTPAdapter.send() itself used before _get_connection() existed.
Consequence: The resulting pool has cert_reqs='CERT_REQUIRED' but ca_certs=None, ca_cert_dir=None, and no ssl_context, confirmed by direct introspection at the pinned head. urllib3's ssl_wrap_socket() then falls back to ssl.SSLContext.load_default_certs() (the OS trust store) instead of requests' pinned certifi bundle, or finds no usable certificates at all in a zip/frozen/minimal-CA environment -- precisely the scenario sigmavirus24 and tiran raised in review -- failing every HTTPS request through that adapter.
Fix: In cert_verify() (src/requests/adapters.py), when verify is True, also set the CA trust source on conn directly (e.g. conn.ssl_context = _preloaded_ssl_context), so any conn is fully configured regardless of how it was obtained, restoring cert_verify()'s pre-change self-sufficiency.
