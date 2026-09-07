# Ground-truth register — psf/requests PR #6667

## Target

- Repository: `psf/requests`
- PR: [#6667](https://github.com/psf/requests/pull/6667) — "Avoid reloading root certificates to improve concurrent performance"
- Head SHA (PR branch tip): `4089f3dc65f783beaa53cc032958ab625440d0ac`
- Merge-base: `8dd3b26bf59808de24fd654699f592abf6de581e`
- Squash-merge commit on `main`: `9a40d1277807f0a4f26c9a37eea8ec90faa8aadc` (tree-identical to the head SHA)
- Merged: 2024-05-15T20:07:26Z
- Sole changed file: `src/requests/adapters.py` (+28/-18)
- Method: cloned `/tmp/qual137/staging/requests.git` into a working tree, diffed both endpoints, read the file at both revisions, read urllib3's `PoolManager`/`ssl_wrap_socket` source (installed urllib3 2.2.x from PyPI) to check the merge semantics the hypothesis depends on, ran two self-written reproductions against both revisions, ran the focused test suite at both revisions, and read the PR's reviews/comments plus GitHub issues/PRs #6715, #6716, #6717, #6745, #6764, #6767, #6790 and psf/requests HISTORY.md.

## Verdict

2 material defects (deduplicated from the 3 candidates in the brief)

## Defect register

### GT-i1 — Forcing a single shared, mutable, process-wide `SSLContext` into every verified connection pool silently discards adapter-level CA/cipher customization and lets concurrent per-request client-cert loading mutate shared OpenSSL state

**Location (at head, `4089f3dc`), `src/requests/adapters.py`:**
- Module scope, lines 75–78: creation of the global,
  ```python
  _preloaded_ssl_context = create_urllib3_context()
  _preloaded_ssl_context.load_verify_locations(
      extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH)
  )
  ```
- `_urllib3_request_context()`, lines 81–115, specifically lines 94–95:
  ```python
  elif verify is True:
      pool_kwargs["ssl_context"] = _preloaded_ssl_context
  ```
- Consumed in `HTTPAdapter._get_connection()`, lines ~376–401, where `pool_kwargs` (containing `ssl_context`) is passed as `pool_kwargs=` to `self.poolmanager.connection_from_host(**host_params, pool_kwargs=pool_kwargs)` / the proxy-manager equivalent, on *every* `send()` call.

**Expected behaviour / violated contract.** `HTTPAdapter.init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs)` (lines 221–245) is the documented extension point: "This method should not be called from user code, and is only exposed for use when subclassing the `HTTPAdapter`... `pool_kwargs`: Extra keyword arguments used to initialize the Pool Manager." Requests' own docs and the pre-PR implementation guaranteed that whatever a subclass configured this way (a custom CA-loaded `ssl_context`, a lowered TLS `SECLEVEL`, an mTLS-preloaded context) was what the pool actually used. Verified with urllib3 2.2's own source: `PoolManager.connection_from_host()` calls `self._merge_pool_kwargs(pool_kwargs)`, whose docstring says overrides win: "Merge a dictionary of override values for `self.connection_pool_kw`... Any keys in the override dictionary... [otherwise] `base_pool_kwargs[key] = value`." So a non-`None` `ssl_context` passed per-request always beats whatever `init_poolmanager` set. Before this PR, `_urllib3_request_context()` never put an `ssl_context` key in `pool_kwargs` at all when `verify is True` (only `ca_certs` when `verify` was a string), so a subclass's `ssl_context` survived. After this PR it unconditionally does, on every request where `verify is True`.

Independently, urllib3's `ssl_wrap_socket()` (`urllib3/util/ssl_.py`, read from the installed 2.2.x package) does `context.load_cert_chain(certfile, keyfile)` directly on whatever `ssl_context` object it is handed, whenever `certfile` (Requests' `cert=` mTLS argument) is supplied — i.e., it *mutates* the context object in place at connection time rather than only reading it. Under this PR that object is the one shared global `_preloaded_ssl_context`, so a client certificate supplied on one request/thread is loaded into the context that every other concurrent Session/thread/pool in the process is simultaneously using for its own handshake.

**Trigger.**
1. *Override manifestation:* subclass `HTTPAdapter`, override `init_poolmanager` to inject a custom `ssl_context` (custom CA store, `load_default_certs()`, lowered cipher `SECLEVEL`, or a preloaded mTLS chain), mount it, and issue a request with `verify=True` (the default).
2. *Shared-mutation manifestation:* issue concurrent requests from multiple threads where at least one uses `cert=(certfile, keyfile)` with `verify=True` against any host.

**Demonstrated consequence.**
- Self-reproduced (commands run from this session):
  ```
  # at head 4089f3dc, pip install -e . into /tmp/qual137/work/venv
  python /tmp/qual137/work/repro.py
  # -> poolmanager.connection_pool_kw ssl_context is custom_ctx: True
  # -> pool.conn_kw['ssl_context'] is custom_ctx: False
  # -> pool.conn_kw['ssl_context'] is preloaded: True

  # at merge-base 8dd3b26b, pip install -e .
  python /tmp/qual137/work/repro_base.py
  # -> custom ctx preserved: True
  ```
  This isolates the override mechanically: identical `CustomAdapter` code produces a pool that uses the developer's `ssl_context` at the merge-base and one that silently uses the global preloaded context at head.
- Two independent user reports opened one week after the release that shipped this PR (2.32.0, released 2024-05-20), both against the exact `init_poolmanager(ssl_context=...)` pattern:
  - [#6715](https://github.com/psf/requests/issues/6715) (2024-05-22): a custom adapter loading a client cert chain into its own context now fails with `SSLError: ... SSLV3_ALERT_HANDSHAKE_FAILURE` because the client cert is never presented (the custom context is discarded).
  - [#6717](https://github.com/psf/requests/issues/6717) (2024-05-22): a custom adapter calling `context.load_default_certs()` for a locally-issued CA now fails with `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate` for the same reason; the reporter had to reach into the private `requests.adapters._preloaded_ssl_context` as a workaround.
  - [#6716](https://github.com/psf/requests/pull/6716) ("Allow for overriding of specific pool key params", merged 2024-05-24, shipped in 2.32.3 per HISTORY.md: "Fixed bug breaking the ability to specify custom SSLContexts in sub-classes of HTTPAdapter") is the maintainers' own acknowledgement and partial fix: it changes `_urllib3_request_context` to only inject the preloaded context `if not has_poolmanager_ssl_context` — i.e., it does not deny the defect, it patches exactly the mechanism identified above.
- Segfault/crash manifestation: [#6745](https://github.com/psf/requests/issues/6745) ("Segmentation fault" after upgrading to 2.32.0, not present in 2.31.0) with a stack trace through `urllib3/util/ssl_.py:ssl_wrap_socket` → `connection.py:connect`, reproduced with concurrent `requests.get(..., cert=('./client.crt','./client.key'))` calls from multiple threads — matching exactly the `load_cert_chain`-mutates-shared-context mechanism above. On [#6767](https://github.com/psf/requests/pull/6767) (the eventual full revert), a 2025-06-02 comment from `Conobi` states: "This unsafe caching can make some applications vulnerable to DOS attack when using mTLS authentication, causing Python to crash," citing a CPython tracker item (not independently verified by me, but consistent with the `load_cert_chain` mechanism read from urllib3 source).
- Ultimate disposition: PR #6767 ("Revert caching a default SSLContext", opened 2024-07-18, merged 2025-06-13, released in 2.32.5 on 2025-08-18) fully removes `_preloaded_ssl_context` and restores per-request `extract_zipped_paths`/`cert_verify` logic. Its body: "Due to the number of edge cases and concurrency issues we've encountered with this change, we've decided the benefit doesn't currently outweigh the pain to existing infrastructure... We may be able to revisit this in a later version... but we'll need a much more comprehensive test plan." HISTORY.md 2.32.5: "The SSLContext caching feature originally introduced in 2.32.0 has created a new class of issues in Requests that have had negative impact across a number of use cases... long term maintenance of it is proving to be unsustainable."

**Required corrective outcome.** A sufficient fix must ensure that (a) a `SSLContext` configured by a subclassed `HTTPAdapter` through `init_poolmanager` is what that adapter's pool actually uses for `verify=True` requests — it must not be silently replaced by a module-global default; and (b) per-request customization that mutates an `SSLContext` object (client certs via `cert=`, in the current urllib3 protocol) must not be applied to an object shared across concurrent unrelated connections/pools/threads. This can be satisfied either by not sharing one global mutable context at all (the approach the revert took) or by any design that preserves per-adapter/per-pool `ssl_context` identity and confines any in-place mutation to a context that is not concurrently in use elsewhere — the specific shape of the fix is not prescribed.

**Class.** Unintended error. The PR's stated and demonstrated goal was purely a concurrency/performance improvement (avoiding redundant `load_verify_locations()` calls); nothing in the PR description, its docs, or the maintainers' review promised any change to how custom adapters' `ssl_context` is honored, nor any new cross-Session/cross-thread state sharing for per-request client certs. Both effects are accidental byproducts of the chosen implementation (one eagerly-created module-level context reused everywhere), not the advertised behavior change.

### GT-i2 — Moving CA-bundle loading (`extract_zipped_paths` + `SSLContext.load_verify_locations`) from lazy, per-verified-request execution to eager, unconditional module-import-time execution

**Location (at head, `4089f3dc`), `src/requests/adapters.py`, lines 75–78** (same lines cited in GT-i1, different consequence):
```python
_preloaded_ssl_context = create_urllib3_context()
_preloaded_ssl_context.load_verify_locations(
    extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH)
)
```
This executes unconditionally at `import requests.adapters` time (transitively, `import requests`). At the merge-base, the equivalent call — `cert_loc = extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH)` inside `HTTPAdapter.cert_verify()` (merge-base lines ~296–298) — only ran when an actual HTTPS request with `verify` truthy was being sent, i.e., lazily and only for processes that actually perform verified TLS requests.

**Expected behaviour / violated contract.** No explicit written contract promises "importing `requests` does no I/O", but it is the de facto behavior the maintainers themselves treat as a baseline (see HISTORY.md 2.32.5 revert notes, and the maintainers accepting #7292 later to remove the now-unused `extract_zipped_paths` call from `cert_verify` post-revert). `extract_zipped_paths()` (in `requests/utils.py`) has a pre-existing, previously-reported multi-user race/permission hazard when `requests`/`certifi` are loaded from inside a zip/pex archive: it writes an extracted copy to a shared temp path (e.g. `/tmp/cacert.pem`) the first time it runs, and issue [#5994](https://github.com/psf/requests/issues/5994) (pre-existing, not part of this PR) already documents that a later user without write/reuse permission on that path can hit `PermissionError`. That hazard existed before this PR, but was only reachable by a program that actually issued a verified HTTPS request from inside such a zip.

**Trigger.** Merely `import requests` (or any module that imports it) from within a zipapp/pex-style archive on a multi-user filesystem where a previous, differently-privileged user has already run the same code and left an unreadable/unwritable `/tmp/cacert.pem` behind — no HTTPS request needs to be made.

**Demonstrated consequence.**
- [#6764](https://github.com/psf/requests/issues/6764) ("permission denied regression reading extracted certs with multiple users", 2024-07-09): reporter's repro is `python -m pytest test/test_utils.py` — no network call — and the traceback shows the `PermissionError` raised straight out of `import requests`, ending in `.../requests/adapters.py", line 77, in <module>` (the module-level `load_verify_locations` line). The issue explicitly states "this issue was not present with version 2.31.0" and "Seems related to #6667."
- [#6790](https://github.com/psf/requests/issues/6790) ("Import time regression", 2024-08-15): reports a measured ~25% `import requests` time increase between 2.31.0 and 2.32.3, attributed via `tuna`/`-X importtime` profiling to this PR moving `load_verify_locations()` to import time.
- Self-reproduced, `python -X importtime -c "import requests"`, self/cumulative time attributed to the `requests.adapters` submodule specifically (not the whole `import requests`, which is dominated by other modules in this environment):
  - head (`4089f3dc`): self 6704 µs / cumulative 8849 µs
  - merge-base (`8dd3b26b`): self 2586 µs / cumulative 4489 µs
  This is a ~2.6× self-time / ~2× cumulative-time increase in the one module this PR touches, consistent in direction and mechanism with #6790's reported regression (the PR's own description acknowledges timing is highly environment/OpenSSL-build dependent, so the absolute percentage varies but the mechanism and direction reproduce here).
- Both are subsumed by the same fix as GT-i1: PR #6767's revert removes the module-level block entirely, restoring lazy per-request extraction/loading, and HISTORY.md 2.32.5 lumps "the SSLContext caching feature" as one unit of revert.

**Deduplication.** #6764 and #6790 are two manifestations (a correctness/crash-adjacent one and a pure-performance one) of one underlying defect — eager, unconditional execution of CA-bundle discovery/loading as an import-time side effect — with one required corrective outcome, so they are recorded as a single defect, GT-i2, not two.

**Required corrective outcome.** `import requests` must not perform filesystem-touching CA-bundle extraction or (expensive) `SSLContext` construction/`load_verify_locations()` unconditionally as a side effect of import; that work must remain deferred until a verified HTTPS connection is actually being established (matching the merge-base's lazy `cert_verify()`-time behavior), so that (a) processes that import but never make a verified HTTPS request cannot be crashed by an unrelated multi-user temp-file permission conflict, and (b) `import requests` does not regress in wall-clock cost. The exact caching strategy is not prescribed as long as the trigger is "about to use CA-bundle verification," not "module import."

**Class.** Unintended error / side effect of the implementation, not the advertised behavior change (the PR's promised benefit was reducing *per-connection* `load_verify_locations()` calls during concurrent request bursts, not import-time cost, and certainly not new import-time filesystem writes).

## Reproduction

Environment: macOS/arm64, Python 3.14 (venv at `/tmp/qual137/work/venv`), `pip install -e . -r requirements-dev.txt` against each checked-out revision of `/tmp/qual137/work/requests` (bare-clone from `/tmp/qual137/staging/requests.git`).

| Command | Revision | Result | Duration |
|---|---|---|---|
| `python /tmp/qual137/work/repro.py` (custom `ssl_context` via `init_poolmanager`, then `adapter._get_connection(pr, verify=True)`) | head `4089f3dc` | custom context **not** used; pool gets `_preloaded_ssl_context` instead | instant |
| `python /tmp/qual137/work/repro_base.py` (same adapter code) | merge-base `8dd3b26b` | custom context **is** used (`True`) | instant |
| `python -X importtime -c "import requests"` (self/cumulative time of `requests.adapters`) | head `4089f3dc` | self 6704 µs / cumulative 8849 µs | instant |
| same | merge-base `8dd3b26b` | self 2586 µs / cumulative 4489 µs | instant |
| `pytest tests/test_adapters.py -q` | head `4089f3dc` | 1 passed | 1.2s |
| `pytest tests/test_requests.py -q -k "ssl or verify or cert or Adapter or adapter"` | head `4089f3dc` | 1 failed, 20 passed, 308 deselected | 3.4s |
| same | merge-base `8dd3b26b` | 1 failed, 20 passed, 308 deselected (same failing test) | 2.5s |
| `pytest tests/ -q -x` (deselecting the above known-failing test) | head `4089f3dc` | 1 failed (different test, `test_redirecting_to_bad_url`), 338 passed, 1 skipped, 1 xpassed | 51.6s |

Notes on failures found:
- `TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert` fails identically at **both** head and merge-base with `SSLCertVerificationError: ... Missing Authority Key Identifier` — a stale/incompatible bundled test certificate under this environment's modern OpenSSL, **not introduced by this PR**.
- `TestPreparingURLs::test_redirecting_to_bad_url[http://localhost:-1-InvalidURL]` fails due to a `werkzeug`/Python-3.14 `urllib.parse` incompatibility in the test's local Flask fixture server (`ValueError: Port could not be cast to integer value as '-1'`), unrelated to `adapters.py` and to this PR; not investigated further at merge-base since the failure is self-evidently an environment/tooling version mismatch, not a code path this PR touches.
- No test in the repository at either revision exercises the `_preloaded_ssl_context` injection path or a custom `init_poolmanager(ssl_context=...)` adapter — consistent with PR author `agubelu`'s own review comment ("I tried to write corresponding tests to verify that the SSLContexts used in different scenarios have the correct certificates loaded, but I couldn't find a way to access such low-level information about a request in the exposed classes"). GT-i1 and GT-i2 are therefore not caught by any pre-existing or PR-added regression test; they surfaced only via field reports after release.

## Not ground truth

- **"The performance optimization doesn't work / isn't real."** False — it works as intended. The PR's own before/after profiling, and post-merge confirmations from `cyberw` (locust load generator, large Windows speedup) and `agubelu`, corroborate the claimed concurrency win. A reviewer should not fault the core mechanism (caching a loaded `SSLContext` to skip redundant `load_verify_locations()` calls) as pointless or non-functional.
- **"`verify` as a string (custom CA bundle/dir) is broken."** Not true at head: `_urllib3_request_context()` correctly branches `isinstance(verify, str)` into `ca_certs` vs `ca_cert_dir` based on `os.path.isdir(verify)`, and `cert_verify()` still validates the path exists and raises `OSError` if not (lines 304–317 at head). This path is unaffected by GT-i1/GT-i2 and is not itself defective.
- **"`verify=False` no longer disables verification."** Not true: `cert_reqs = "CERT_NONE"` is still set at both the `_urllib3_request_context` and `cert_verify` level when `verify` is falsy; unaffected by this PR.
- **CVE-2024-35195 (GHSA-9wx4-h78v-vm56, "Session object does not verify requests after making first request with verify=False")** was fixed in the same 2.32.0 release that shipped this PR, but it is a **different, unrelated fix** (in `sessions.py`'s per-Session `verify` merging logic, not in `adapters.py`) landed via a different PR. A reviewer must not attribute this CVE to #6667.
- **"The eager module-level `SSLContext` creation will raise `ImportError`/`AttributeError` on Python builds without the `ssl` module."** This is a real edge case (fixed later by [#6724](https://github.com/psf/requests/pull/6724)/`e1887993`, "Don't create default SSLContext if ssl module isn't present"), but it postdates the pinned head and is not present as a defect *at* `4089f3dc`: at head, `import ssl` is not guarded, but neither was it guarded pre-PR in a way this PR removed — treat any claim about this specific edge case as out of scope for the pinned diff (it is a genuine but separate, later-identified gap in the same feature, not something demonstrable from `4089f3dc` alone without importing the `create_urllib3_context`/`ssl` chain on such a build, which was not tested here).
- **"Renaming to `_preloaded_ssl_context` (leading underscore) doesn't fully solve the design concern."** True as a statement (see `sigmavirus24`'s own comment below), but the PR never claimed the rename was a complete fix for the sharing/override problem — it was an agreed *reduction* of accidental public-API surface, not a claim to have fixed GT-i1. A finding that only restates "the context is still shared" without an accompanying demonstrated consequence like GT-i1's is a style/design observation, not a material defect on its own.
- **"Docstrings weren't updated for the new `pool_kwargs`/`ssl_context` behavior."** A real gap (`init_poolmanager`'s and `cert_verify`'s docstrings don't mention the new shared-context caveat) but purely a documentation/hygiene issue with no demonstrated consequence beyond GT-i1 itself; do not score it as a separate defect from GT-i1.

## Preexisting hints

All quotes below are from the PR's review record **before** the merge instant (2024-05-15T20:07:26Z):

- `sigmavirus24`, inline review comment, 2024-03-21T01:45:42Z, on the line removing the zip-CA fallback: *"This is actually critical behavior you're removing"* — flagged the original (pre-revision) patch's loss of `extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH)` support. This is what prompted `agubelu` to introduce the module-level `_preloaded_ssl_context.load_verify_locations(extract_zipped_paths(...))` — i.e., the very code whose *placement* (import time) later caused GT-i2. The reviewer surfaced the underlying CA-bundle-handling requirement but did not anticipate the import-time side effect the fix would introduce.
- `sigmavirus24`, PR conversation, 2024-05-05T01:44:58Z: *"Given this breaks the behavior of the module for a whole class of users as it's written today, there's not much to do to advance it. Even still, I'm pretty sure SSLContext is not itself thread safe... so loading it at the module level will likely cause issues"* — a direct, named concern about thread-safety/sharing of the module-level context, i.e., a preexisting gesture at the mechanism behind GT-i1's concurrency/mutation manifestation (though the specific `load_cert_chain`-on-shared-context mutation path was not spelled out).
- `tiran` (CPython core/`ssl` module maintainer), PR conversation, 2024-05-05T05:08:40Z: *"`SSLContext` is designed to be shared and used for multiple connections. It is thread safe as long as you don't reconfigure it once it is used by a connection. Adding new certs to the internal trust store is fine, but changing ciphers, verification settings, or mTLS certs can lead to surprising behavior."* — this is a precise, expert preexisting warning that reconfiguring (e.g., loading mTLS certs into) a context already in concurrent use is unsafe — exactly the mechanism this register identifies (via reading `ssl_wrap_socket`'s `load_cert_chain` call) as the segfault/DOS root cause in GT-i1.
- `sigmavirus24`, PR conversation, 2024-05-05T14:54:54Z: *"I expect people to use this to work around libraries that aren't written correctly that leverage requests but do not allow people to specify a trust store or customize a session... if we rename the default I'm in favor of merging this."* — the maintainers explicitly traded off the known "someone may rely on/be surprised by the shared context" risk for the performance win, mitigating only by making the name conventionally private (leading underscore), not by preventing override/sharing. This documents that GT-i1's risk was known and consciously accepted at merge time, not undiscovered.

No comment before the merge instant anticipates GT-i2's specific `PermissionError` multi-user race manifestation (#6764) or the quantified import-time regression (#6790); those were only reported after release.

## Leakage

A truncated mirror of this PR for the evaluation must exclude at least the following SHAs and issue/PR numbers, all of which reveal or strongly imply the defects above:

**Commits (on `main`, all after the target merge commit `9a40d127`):**
- `145b5399` — merge commit for PR #6716 ("Allow for overriding of specific pool key params") — direct partial fix for GT-i1
- `a62a2d35`, `92075b33`, `b1d73ddb` — constituent commits of PR #6716
- `e1887993` — "Don't create default SSLContext if ssl module isn't present" (#6724) — edge-case follow-up fix in the same feature
- `aa1461b6` — "Move `_get_connection` to `get_connection_with_tls_context`" — renames the exact function this register cites, part of the post-merge CVE-2024-35195 response bundled in the same release train; excluding avoids hinting that this function/area is under scrutiny
- `90fee087` — merge commit for PR #6767, the full revert — reveals both defects outright
- `8ff173b1` and any other constituent commit of PR #6767
- `e331a288` — "Remove unused extraction call" (#7292, 2026-03-24) — later cleanup of the exact `extract_zipped_paths`/`DEFAULT_CA_BUNDLE_PATH` code path central to GT-i2

**Issues/PRs whose content gives away the answer:**
- #6715, #6716, #6717 (GT-i1 reports and partial fix)
- #6745 (segfault manifestation of GT-i1)
- #6764, #6790 (GT-i2 reports)
- #6767 (the full revert PR and its discussion, including the 2025 mTLS-DOS/crash comment)
- #6710 and the associated deprecation of `_get_connection` (adjacent, same release train, could bias a reviewer toward suspecting `adapters.py`'s connection-selection code generally)
- The GHSA-9wx4-h78v-vm56 security advisory / CVE-2024-35195 discussion — not a defect in this PR, but bundled in the same 2.32.0 release notes; exposure to it could cause a reviewer to (incorrectly) fold it into this PR's findings or (correctly, but via leakage rather than analysis) become primed to scrutinize `verify`/session-level TLS handling harder than an uninformed reviewer would.

## Adjudicator's confidence and limits

- GT-i1 is high confidence: mechanically reproduced (both the override and, via reading urllib3's `_merge_pool_kwargs`, the precedence rule that causes it), and corroborated by two independent field reports, a partial-fix PR, and an eventual full revert with an explicit "concurrency issues" rationale from the maintainers. The specific segfault/DOS mutation mechanism (`ssl_wrap_socket`'s `load_cert_chain` call mutating whatever context it's given) is confirmed by reading urllib3 2.2.x source directly; I did not, however, myself reproduce an actual crash (that would require inducing a genuine data race under GIL contention/OpenSSL internals, which is inherently flaky and not something I attempted to force in this session). Treat the segfault claim's *mechanism* as confirmed and its *manifestation* as `unresolved` at the level of "I personally triggered a crash" — it rests on the #6745 report plus source-level mechanism analysis, not a self-produced core dump.
- GT-i2's ~25% import-time figure from #6790 was not reproduced at that exact magnitude in this session's environment (I measured a ~2× increase confined to the `requests.adapters` submodule's own self/cumulative time, which is a smaller fraction of total `import requests` time here than apparently reported elsewhere); the PR author's own submission acknowledges this varies enormously by OS/OpenSSL build, so I treat the direction and mechanism as confirmed and the exact percentage as environment-dependent, not in dispute.
- The `PermissionError` race in #6764 was not independently reproduced (would require constructing a genuine zipapp/pex with mismatched-permission multi-user temp directories); I rely on the reporter's traceback, which unambiguously shows the exception originating from the module-level `load_verify_locations` line at `adapters.py:77` during a bare `import requests`, and on the structural diff confirming this code path is new at import time relative to merge-base. This is `unresolved` only in the sense of "not independently reproduced end-to-end by me," not in the sense of the causal mechanism being in doubt.
- I did not exhaustively audit every other function in the diff (e.g., I did not construct a scenario exercising the proxy-manager branch of `_get_connection`) beyond what was needed to confirm/refute the specific hypothesis and its two secondary candidates; I am not aware of and did not search for additional, unrelated defects beyond the scope the brief asked me to adjudicate.
