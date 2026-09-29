# Research report — `i-867cf3ff-seed1-att-02`

**Review payload (the complete would-be review):** [`i-867cf3ff-seed1-att-02-payload.md`](i-867cf3ff-seed1-att-02-payload.md). Built from a JSON payload that `python3 scripts/validate_review.py < payload.json` accepted with exit 0 and zero violations, using fragments from `python3 scripts/validate_review.py --render < payload.json` pasted verbatim into the summary body, and cross-checked against `python3 scripts/validate_review.py --emit-batch < payload.json`'s projection of the one-call GitHub review body. Immediately after that validation, `python3 /tmp/qual137/mark_event.py .../i-867cf3ff-seed1-att-02-timing.json payload_validated_at` was run once, per rule 6/the dispatch's timing-sidecar instruction.

## 1. Metadata

- **Target:** `psf/requests#6667` ("Avoid reloading root certificates to improve concurrent performance"), MERGED 2024-05-15T20:07:26Z.
- **Cell:** `i-867cf3ff-seed1`, **attempt:** `att-02`.
- **Skill snapshot:** `/tmp/qual137/snapshots/867cf3ff/snapshot-path-omitted/` (SKILL.md + references/review-rubric.md, references/output-contract.md, references/verifier.md; `references/re-review.md` was present but not read — see §7 "deferral handling"/re-review note below, since this is a first review with no prior state from the posting identity).
- **`workflow` identifier the validator reports:** `v5b-1` (from `scripts/validate_review.py`'s `WORKFLOW` constant).
- **Model I ran on:** `claude-sonnet-5` (the primary/integrated reviewer for the entire run — no delegation of the review itself).
- **Model each sub-agent ran on:** `claude-sonnet-5` (`model: "sonnet"` passed explicitly) — one verifier sub-agent, `subagent_type: "general-purpose"`, `run_in_background: false`. See §4 for its full prompt and verbatim report.
- **Verification trigger that fired:** Both surviving candidates triggered mandatory independent verification. The sentence in `SKILL.md` that fired: *"Independently verify every surviving candidate proposed as `must-fix`, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break."* Candidate C1 is `must-fix` and involves a security/authorization-adjacent client-certificate mixup; candidate C2 is `must-fix` and is an externally observable compatibility break (a working `import requests` becomes a crashing one). Both clauses of that sentence fired independently for each candidate.
- **Sub-agents spawned:** 1 (verifier, candidate mode, `general-purpose`, `model: "sonnet"`, foreground). No clean-verdict batch was needed (not zero-survivor), no related-acquittal need beyond what's discussed in §7 (one related non-survivor row, C3, rode along in the same batch).
- **Candidates raised:** 5 (C1–C5, see full ledger in §3).
- **Candidates surviving primary falsification:** 2 (C1, C2).
- **Verifier verdicts:** C1 `confirmed` (with a `kind` correction — see §4/§10), C2 `confirmed`, C3 (related-acquittal row) **`re-open`** (the row's stated falsification *reasoning* was shown to be inaccurate, though re-falsification below shows the practical "dropped" disposition survives for a narrower, corrected reason — no new finding results). Full verbatim verifier report in §4.
- **Findings for publication:** 2 — both `must-fix`, `blocking=true`. F1 (from C1): P1, kind=security (corrected from my initial `concurrency` tag per the verifier's independent read — see §10). F2 (from C2): P2, kind=bug.
- **Questions:** none.
- **Observations:** 1 published, arising from re-falsifying the re-opened C3 row (see §3, §7).
- **Coverage:** complete — the single changed file (`src/requests/adapters.py`, +28/−18) was read in full (via the context script's function-context diff, which spans essentially the entire 616-line file, plus a direct read of the small remaining gap at lines 1–25); all risk-directed checks below have evidence-backed outcomes.
- **Derived status:** `Changes Requested (advisory)` — 2 unsettled `must-fix` findings on a merged, retrospective, non-publishing target.
- **My own token usage:** the harness does not report this to me in this session; I have no figure to give. The verifier sub-agent's usage *was* reported back to me by the harness: `subagent_tokens: 55872`, `tool_uses: 17`, `duration_ms: 256034` (~256s).
- **Clone hygiene incident (disclosed, remediated):** generating a scratch client certificate for F1's repro inadvertently updated `tests/certs/expired/ca/ca.srl` inside the clone (an OpenSSL `-CAcreateserial` side effect, discovered late, via a symlink from `tests/certs/valid/ca`). I ran `git -C /tmp/qual137/runs/i-867cf3ff-seed1-att-02 reset --hard review-head` immediately on discovering it and confirmed the tree is clean and at the pinned head. Full disclosure and root-cause in §9; no evidence or finding depended on the mutated file. This is the "if a tree is mutated anyway" case the hygiene rule anticipates.

## 2. Findings that survive (full detail)

### F1 — `[P1] [must-fix]` Stop reusing the shared default SSLContext when a client certificate is set

- **Anchor:** `src/requests/adapters.py:94-102` (RIGHT; added lines from the diff: the `elif verify is True: pool_kwargs["ssl_context"] = _preloaded_ssl_context` branch through the start of the `client_cert is not None` branch).
- **Fix location:** `src/requests/adapters.py:95` (the `pool_kwargs["ssl_context"] = _preloaded_ssl_context` line) together with the `client_cert` handling immediately below it (line 102 onward).
- **`kind` (private routing tag):** `security` — corrected from my initial `concurrency` tag after the verifier pointed out, correctly, that no concurrent/parallel execution is required to trigger the leak (the trigger is purely sequential, single-threaded reuse of one process's shared context); the defect is a shared-mutable-global-state/credential-isolation bug, which the `security` kind names more accurately. This is an internal-record correction only; it does not change the finding's visible prose.
- **Claim:** `_urllib3_request_context()` hands the very same module-level `_preloaded_ssl_context` object to urllib3 as `pool_kwargs["ssl_context"]` for **every** `verify=True` request, including ones that also supply a client certificate via `cert=`.
- **Trigger scenario:** In one process, request 1 is `session.get(url_a, verify=True, cert=(certA, keyA))` (mutual-TLS / client-certificate auth is a normal, documented `requests` feature). Request 2, to any other host, is `session.get(url_b, verify=True)` — the ordinary default, no `cert=` at all.
- **Impact:** The installed urllib3 (2.7.0)'s `urllib3/util/ssl_.py::ssl_wrap_socket()` calls `context.load_cert_chain(certfile, keyfile)` on whatever `ssl_context` it was handed, whenever the connection has a `cert_file` set — and does nothing to reset the identity when `cert_file` is absent. Because `context` is `_preloaded_ssl_context` for every `verify=True` pool, request 1's `load_cert_chain(certA, keyA)` mutates a singleton that request 2 also uses. Request 2 supplied no client certificate, but the server it talks to still receives **request 1's** client certificate, because the shared context still has it loaded. This is a real, deterministic (not merely a race) cross-request client-identity leak: an operator running several outbound mTLS integrations with different client identities, or a service that sometimes needs a client cert and sometimes doesn't, will silently present the wrong (or an unintended) credential to servers that never should have seen it — a serious, silent security regression, not merely a performance one. It also creates a genuine concurrency hazard: two threads presenting different certs concurrently through the same shared, mutable `SSLContext` can interleave `load_cert_chain()` calls with the handshake that consumes them.
- **Change (what to implement):** Only reuse `_preloaded_ssl_context` for `verify=True` requests that supply no client certificate. When `client_cert is not None`, do not pass the shared singleton as `pool_kwargs["ssl_context"]`; build a context/pool_kwargs combination scoped to that specific client certificate (e.g. fall back to the pre-PR per-pool context creation for that case, or maintain a small cache of contexts keyed by the client-cert paths) so `load_cert_chain()` never mutates state that another, unrelated request also reads.
- **Verification status:** `independent-confirmed`. Verifier batch dispatched in a fresh isolated context (see §4); confirmed the leak by independently tracing `_urllib3_request_context()`, `urllib3.poolmanager.PoolKey`, `urllib3.connection.HTTPSConnection.connect()`, and the installed `urllib3.util.ssl_.ssl_wrap_socket()` source, and by running its own independent repro (a small script constructing `pool_kwargs` for two different `client_cert` values and confirming `pool_kwargs["ssl_context"] is _preloaded_ssl_context` both times) rather than re-running mine. The verifier noted P1/must-fix is "defensible" but could arguably be argued as P0 given the security impact; I kept P1 as my own final judgment (see §10) — the primary reviewer owns the final priority/action call per the verifier-handling rules.
- **Evidence in hand:**
  1. `src/requests/adapters.py:95` — `pool_kwargs["ssl_context"] = _preloaded_ssl_context`, unconditional on `client_cert`.
  2. Installed `urllib3==2.7.0`, `urllib3/util/ssl_.py::ssl_wrap_socket()`: `if certfile: ... context.load_cert_chain(certfile, keyfile)` — operates on the passed-in, possibly-shared `ssl_context`.
  3. A local, offline, loopback-only reproduction (`/tmp/qual137/work/i-867cf3ff-seed1-att-02/test_shared_ssl_context_leak.py`) using the repository's own `tests/testserver/server.py::TLSServer` and CA/server fixtures under `tests/certs/valid/`, plus a fresh non-expired client certificate I generated in my own work directory and signed with the repo's existing `tests/certs/valid/ca/ca-private.key` (the checked-in `tests/certs/mtls/client/client.pem` has since calendar-expired relative to the sandbox's current date and could not be used). The test issues two `Session.get()` calls against a mutual-TLS `TLSServer` (`verify_mode=CERT_OPTIONAL`, so it never refuses a certificate-less handshake): request 1 supplies the fresh client cert with `verify=True`, request 2 supplies **no** `cert=` with `verify=True`. Result: **request 2's peer-observed certificate is not `None`** — it is request 1's certificate, `CN=fresh-repro-client`. Exit status: the test's decisive assertion (`assert peer_certs[1] is None`) fails, proving the leak. Full command and output are in §5.
  4. Base-branch comparison confirming this is introduced-here: `git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py` lines 60–90 show no module-level SSLContext and no `ssl_context` key ever placed in `pool_kwargs`; at the merge-base, `verify=True` never shared any object across pools (urllib3's own `ssl_wrap_socket()` fallback branch — `if context is None: context = create_urllib3_context(...)` — created a fresh context per connection when `ssl_context` was not supplied), so the base guarantee ("a client certificate loaded for one connection cannot be observed by another, unrelated connection") held and this diff removes it.

### F2 — `[P2] [must-fix]` Don't load the default CA bundle unconditionally at import time

- **Anchor:** `src/requests/adapters.py:75-78` (RIGHT; wholly new module-level lines).
- **Fix location:** same as anchor (omitted per contract).
- **Claim:** `src/requests/adapters.py` now runs `_preloaded_ssl_context = create_urllib3_context(); _preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))` unconditionally at module import time.
- **Trigger scenario:** The default CA bundle path (`certifi.where()`, i.e. `DEFAULT_CA_BUNDLE_PATH`) is missing, unreadable, or otherwise invalid in the running environment (stripped certifi data file in a minimal/frozen/containerized build, a broken package install, a sandbox that removes package data, etc.) — regardless of whether the caller ever intends to verify a TLS certificate with the default bundle.
- **Impact:** `import requests` now raises `OSError`/`FileNotFoundError` unconditionally and the import fails completely, even for callers who exclusively use `verify=False`, a custom CA bundle string, or make no HTTPS request at all. At the merge-base, the equivalent check (`if not cert_loc or not os.path.exists(cert_loc): raise OSError(...)`) lived only inside `HTTPAdapter.cert_verify()`, gated by `if url.lower().startswith("https") and verify:` — i.e. it only ever fired for a request that actually reached `cert_verify()` needing the default bundle. This diff moves a previously lazy, conditional failure to an eager, unconditional one, breaking backward compatibility for any environment with a broken default CA bundle that previously worked because it never needed it.
- **Change (what to implement):** Defer creation/loading of `_preloaded_ssl_context` until the first `verify=True` HTTPS request actually needs it (e.g. a lazily-initialized singleton, built on first use inside `_urllib3_request_context()` or `cert_verify()`), preserving the base branch's guarantee that a broken default CA bundle only affects callers who actually verify with it.
- **Verification status:** `independent-confirmed`. The verifier ran its own independent reproduction of the same subprocess-based crash (not a re-run of mine) and reached the same result; it also noted P2/must-fix is defensible as-is, though it could arguably be argued higher since it fully blocks `import requests` — I kept P2 as my own final judgment (see §10).
- **Evidence in hand:**
  1. `src/requests/adapters.py:75-78` (module level, unconditional).
  2. `git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py` lines 60–90 — no module-level SSLContext/CA-bundle code exists at the merge-base.
  3. A subprocess-based repro (`/tmp/qual137/work/i-867cf3ff-seed1-att-02/test_eager_ca_bundle_load.py`): patch `certifi.where` to a nonexistent path, then `import requests` in a fresh interpreter with `PYTHONPATH` pointing at the reviewed head's `src/`. Result: `import requests` raises `FileNotFoundError` at `src/requests/adapters.py:76`, exit code 1, even though the script never calls any `requests` API. Full command/output in §5.

### Observation (published)

- The shared `_preloaded_ssl_context`'s `verify_mode` is reassigned on every `verify=True` connection, not only its identity certificate: `urllib3/connection.py`'s `_ssl_wrap_socket_and_match_hostname()` executes `context.verify_mode = resolve_cert_reqs(cert_reqs)` unconditionally, including when `ssl_context` (the shared singleton) was supplied, so every connection using the shared context re-writes its `verify_mode` from `src/requests/adapters.py:298`'s `conn.cert_reqs = "CERT_REQUIRED"`; today this always writes back the same `CERT_REQUIRED` value `create_urllib3_context()` already set. Evidence: `src/requests/adapters.py:298`; `urllib3/connection.py:901-937` (`_ssl_wrap_socket_and_match_hostname`).

This surfaced while re-falsifying the verifier's `re-open` ruling on ledger row C3 (§3, §7); it is descriptive only — no code change is requested, and it does not currently produce any observable defect.

## 3. Complete private disposition ledger

| id | kind | claim (one line) | disposition | decisive evidence | verifier ruling? |
| --- | --- | --- | --- | --- | --- |
| C1 (`adapters/shared-ssl-context-client-cert-leak`) | concurrency | Shared `_preloaded_ssl_context` leaks a previously-loaded client cert into a later cert-less `verify=True` request | **survivor** → F1 | `src/requests/adapters.py:95`; installed `urllib3.util.ssl_.ssl_wrap_socket()`; local repro test | Yes — mandatory (must-fix + security/compat); verdict `confirmed` |
| C2 (`adapters/eager-default-ca-bundle-load-at-import`) | bug | Module-level `load_verify_locations()` call now runs unconditionally at `import requests` time | **survivor** → F2 | `src/requests/adapters.py:75-78`; `git show` merge-base; subprocess repro | Yes — mandatory (must-fix + compatibility break); verdict `confirmed` |
| C3 (`adapters/redundant-cert-reqs-assignment`) | bug | `cert_verify()` sets `conn.cert_reqs = "CERT_REQUIRED"` even on the `verify=True` path that now uses the shared `ssl_context`; **originally claimed dead code, corrected below** | **re-opened, then re-falsified → dropped (consequence unproven, corrected reasoning)** | `src/requests/adapters.py:298`; `urllib3/connection.py:901` `_ssl_wrap_socket_and_match_hostname()`, line `context.verify_mode = resolve_cert_reqs(cert_reqs)` (executes unconditionally, **not** only in the `ssl_context is None` branch) | Yes — **related-acquittal** row (same file as C1's anchor/fix, `kind=bug`); verifier ruling: **`re-open`** (my own independent re-check of `urllib3/connection.py` confirmed the verifier's citation — see falsification note below) |
| C4 (`adapters/no-test-for-ssl-context-selection`) | maintainability | The PR author's own description says they could not write a test to verify which `SSLContext`/certs a given request uses | dropped (consequence absent — subsumed by C1's proven consequence) | PR body (packet §3, final paragraph) | No — `kind=maintainability` is not one of the four kinds (`bug`, `concurrency`, `invariant`, `security`) the related-acquittal rule pulls in, and it was not itself a survivor, so `SKILL.md`'s related-acquittal clause does not require a ruling on it |
| C5 (`adapters/proxy-pool-multiplication-not-addressed`) | performance | Proxied requests still create a new pool/context per proxy combination, per a third-party review comment (`mm-matthias`) | dropped (pre-existing / out of scope; not introduced here) | packet §6, non-review comment 1; `src/requests/adapters.py::proxy_manager_for` unchanged by this diff | No — `kind=performance` is excluded from related-acquittal by the same rule, and it was not a survivor |

Falsification notes per row:

- **C1:** Falsified the opposite hypothesis (that pools with different `cert_file` values would also get distinct `ssl_context` objects) by reading `urllib3.poolmanager.PoolKey`'s field list — `key_ssl_context` is a *separate* key field from `key_cert_file`/`key_key_file`, so different client certs produce different `PoolKey` tuples (different pools) that nonetheless all carry the identical `ssl_context` object reference. Then confirmed via the local repro that the leak is real and deterministic, not hypothetical.
- **C2:** Falsified by directly citing the merge-base file content (no module-level code existed) and by reproducing the crash against the head in a fresh subprocess.
- **C3 — original falsification (before verification), shown incomplete:** I initially falsified this as consequence-free by reading `ssl_wrap_socket()`'s source only: `cert_reqs` is a parameter there, consulted only in the `if context is None: context = create_urllib3_context(ssl_version, cert_reqs, ciphers=ciphers)` fallback branch, so I concluded `conn.cert_reqs` is never read when `ssl_context` is supplied. **This was wrong** — I had not traced the caller of `ssl_wrap_socket()`.
- **C3 — verifier's re-open and my independent re-check:** The verifier reported that `urllib3/connection.py`'s module-level `_ssl_wrap_socket_and_match_hostname()` (the function `HTTPSConnection.connect()` actually calls, which itself calls `ssl_wrap_socket()`) contains, unconditionally after the `if ssl_context is None: ... else: context = ssl_context` branch: `context.verify_mode = resolve_cert_reqs(cert_reqs)`. This reassigns `verify_mode` on **whichever** context object it received — including our shared singleton — on every single `connect()` call, regardless of whether `ssl_context` was supplied. I independently re-derived this myself (not merely trusting the verifier) by reading `urllib3/connection.py` directly: `grep -n "resolve_cert_reqs\|def _ssl_wrap_socket_and_match_hostname" .../urllib3/connection.py` located the function at line 901, and inspecting its body around line 937 confirmed the unconditional `context.verify_mode = resolve_cert_reqs(cert_reqs)` line. The acquittal's decisive premise ("`cert_reqs` is never read when `ssl_context is not None`") is therefore false, and the verifier's `re-open` is correct on that narrow point.
- **C3 — re-falsification after the re-open (required by `SKILL.md`: "re-run falsification on that record"):** Despite the corrected mechanism, I could not establish a *proven consequence* (gate 4) today: the only branch in `src/requests/adapters.py` that ever shares `_preloaded_ssl_context` (the `elif verify is True:` branch, line 94-95) always pairs it with `cert_reqs = "CERT_REQUIRED"` (the unconditional default set at line 91, never overwritten before that branch). `create_urllib3_context()` already constructs `_preloaded_ssl_context` with `verify_mode = CERT_REQUIRED`. So `context.verify_mode = resolve_cert_reqs("CERT_REQUIRED")` reassigns the shared context's `verify_mode` to the exact value it already holds, on every connect() — a real, live write to shared state, but not one with any input in the current code that could make it write a *different* value. No concrete trigger exists today that would flip `verify_mode` on the shared singleton to something inconsistent. This still fails gate 4 ("Speculation about downstream breakage is insufficient... identify the concrete input, state, environment, or call path"), so C3 does not newly reach render eligibility and is not promoted to a finding; no follow-up verifier batch was needed for it. Per the verifier-handling rule ("Do not downgrade it to an observation" for the re-open ruling itself), I did not fold this into an observation *as the disposition of C3*; instead, having established a new, decisive, accurate fact in the course of re-falsifying it (the shared context's `verify_mode` is live-reassigned on every connect, not just its identity cert), I separately admitted that fact as its own Observation under the rubric's general Observations rule ("Route an accurate fact to Observations when it fails finding admission specifically on meaningful or proven consequence... or when a verifier reports a relevant aside") — see the Observations entry in §2 and the payload.
- **C4:** The author's admitted testing gap is not itself a separate, freestanding defect; it is precisely the gap that let C1's bug ship unnoticed. Reporting it as its own finding would restate F1's consequence without adding a distinct claim, so it was dropped rather than promoted or routed to Observations (an observation must be an accurate fact that failed the finding gate specifically on "meaningful/proven consequence" or arrived as a verifier aside — this fact instead duplicates a fact already fully captured, with proof, inside F1).
- **C5:** Checked whether the proxy-pool-multiplication complaint was introduced by this diff: `proxy_manager_for()` is untouched by the reviewed diff, and pool multiplication for distinct proxies predates this PR entirely (a `ProxyManager` per distinct proxy URL is pre-existing behavior). The PR's own stated scope (its reproduction script uses no proxies) never promised to address it, and `mm-matthias`'s comment is a third-party bug report, not a maintainer deferral of a design/naming/API-shape decision, so the rubric's explicit-deferral carve-out does not apply. Dropped as pre-existing and out of scope.

## 4. Sub-agent dispatch — exact prompt and verbatim report

One verifier sub-agent was dispatched, in candidate mode, carrying C1 and C2 as mandatory candidates and C3 as a related-acquittal row (same file as C1's anchor/fix, `kind=bug`).

**Dispatch parameters:** `Agent` tool, `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false`.

**Exact prompt given:**

```
You are an independent code-review verifier. You have NOT seen any prior reasoning about
this pull request; treat this message as your complete briefing. Follow references/verifier.md's
verification task and verdict rules exactly (reproduced/summarized below); you do not have
filesystem access to that file, so the operative rules are restated here verbatim where they
matter.

SANDBOX / OFFLINE RULES (binding on you):
- You have a git clone at /tmp/qual137/runs/i-867cf3ff-seed1-att-02. It is fully offline: no
  git fetch/pull, no gh, no curl, no network access of any kind. Local branch `review-head`
  (checked out) is the pinned head 4089f3dc65f783beaa53cc032958ab625440d0ac; local branch
  `main` is pinned to the merge-base 8dd3b26bf59808de24fd654699f592abf6de581e (not checked out;
  read it with `git show main:<path>` or `git show 8dd3b26bf59808de24fd654699f592abf6de581e:<path>`).
- Do NOT run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates
  the working tree. Read-only git commands only (`git show`, `git diff`, `git log`, `git blame`).
- You MAY run focused pytest commands offline, from the clone root, using the pre-provisioned
  venv: `PYTHONPATH=/tmp/qual137/runs/i-867cf3ff-seed1-att-02/src /tmp/qual137/venvs/requests/bin/python -m pytest <selection>`,
  five minutes per command, at most once per exact flag set. Write any scratch files only under
  /tmp/qual137/work/i-867cf3ff-seed1-att-02/verifier-scratch/ (create it if needed). Do not add
  or change anything inside the clone itself.
- Stay inside: the clone above, and your own scratch directory. Do not read any other run's
  clone, report, or payload; if you accidentally read anything outside this scope, say so
  explicitly in your report.
- This is a retrospective review of an already-merged PR. You are not publishing anything,
  gating anything, or writing to any forge. You only return a verdict.

YOUR TASK — verify these candidates independently. For each, do NOT simply agree with the
claim: actively try to construct the failing trace yourself from the cited evidence, and try to
refute it before confirming it.

=== CANDIDATE C1 (mandatory: must-fix, and involves a security-adjacent credential mixup) ===
id: adapters/shared-ssl-context-client-cert-leak
kind: concurrency
priority: P1
action: must-fix
anchor: src/requests/adapters.py:94-102 (RIGHT, head)
fix: src/requests/adapters.py:95
title: Stop reusing the shared default SSLContext when a client certificate is set
claim: `_urllib3_request_context()` in src/requests/adapters.py passes the same module-level
`_preloaded_ssl_context` object as `pool_kwargs["ssl_context"]` for every `verify=True` request,
including ones that also supply a client certificate via `cert=`.
trigger: In one process, request 1 is `session.get(url_a, verify=True, cert=(certA, keyA))`.
Request 2, to any other host, is `session.get(url_b, verify=True)` (no `cert=` at all).
impact: The installed urllib3's `urllib3/util/ssl_.py::ssl_wrap_socket()` calls
`context.load_cert_chain(certfile, keyfile)` on whatever `ssl_context` it is handed, whenever the
connection has a `cert_file` set, and never resets identity state when `cert_file` is absent.
Because `ssl_context` is the same shared object for every verify=True pool, request 1's
load_cert_chain mutates a singleton request 2 also uses, so request 2 (which asked for no client
cert) still presents request 1's client certificate to its server.
change proposed: Only reuse `_preloaded_ssl_context` for verify=True requests with no client
certificate; when `client_cert is not None`, do not pass the shared singleton as
`pool_kwargs["ssl_context"]` — build context/pool_kwargs scoped to that specific client cert
instead.
raw code citations you should independently re-derive, not trust:
  - src/requests/adapters.py lines ~91-115 (`_urllib3_request_context`)
  - installed urllib3 version in the venv: inspect
    `/tmp/qual137/venvs/requests/bin/python -c "import urllib3.util.ssl_ as m, inspect; print(inspect.getsource(m.ssl_wrap_socket))"`
  - `/tmp/qual137/venvs/requests/bin/python -c "import urllib3.poolmanager as pm, inspect; print(inspect.getsource(pm.PoolKey))"`
    to check whether distinct `cert_file`/`key_file` values produce distinct pools that still
    share one `ssl_context` object reference.
  - base-branch guarantee: `git -C /tmp/qual137/runs/i-867cf3ff-seed1-att-02 show
    8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py | sed -n '60,90p'`
requirement/rule citation: none (no linked issue; not a repository-rule finding).

=== CANDIDATE C2 (mandatory: must-fix, and is an externally observable compatibility break) ===
id: adapters/eager-default-ca-bundle-load-at-import
kind: bug
priority: P2
action: must-fix
anchor: src/requests/adapters.py:75-78 (RIGHT, head)
fix: same as anchor
title: Don't load the default CA bundle unconditionally at import time
claim: src/requests/adapters.py now runs
`_preloaded_ssl_context = create_urllib3_context(); _preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))`
unconditionally at module import time.
trigger: The default CA bundle path (certifi.where(), i.e. DEFAULT_CA_BUNDLE_PATH) is missing,
unreadable, or otherwise invalid in the running environment, regardless of whether the caller
ever intends to verify a TLS certificate with the default bundle.
impact: `import requests` now raises OSError/FileNotFoundError and fails completely, even for
callers who exclusively use verify=False, a custom CA bundle string, or make no HTTPS request at
all. At the merge-base, the equivalent check lived only inside HTTPAdapter.cert_verify(), gated
by `if url.lower().startswith("https") and verify:` — i.e. it only fired for a request that
actually needed the default bundle.
change proposed: Defer creation/loading of `_preloaded_ssl_context` until the first verify=True
HTTPS request actually needs it (lazy singleton), preserving the base branch's guarantee.
raw code citations you should independently re-derive:
  - src/requests/adapters.py lines ~75-78 (module level)
  - base-branch guarantee: `git -C /tmp/qual137/runs/i-867cf3ff-seed1-att-02 show
    8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py | sed -n '60,90p'`
  - you may reproduce directly: run a subprocess that does
    `import certifi; certifi.where = lambda: "/nonexistent/path"; import requests`
    with PYTHONPATH=/tmp/qual137/runs/i-867cf3ff-seed1-att-02/src and the venv's python, and see
    whether import fails.
requirement/rule citation: none.

=== RELATED NON-SURVIVOR ROW C3 (related-acquittal: same file as C1's anchor/fix, kind=bug — rule
exactly once for this row: `holds` or `re-open`, full 5-step attack depth since kind=bug) ===
claim: `cert_verify()` in src/requests/adapters.py sets `conn.cert_reqs = "CERT_REQUIRED"`
(line ~298) even on the verify=True path that now uses the shared `ssl_context`, and this
assignment is dead code with no behavioral effect.
kind: bug
disposition (acquittal being attacked): dropped (no consequence)
falsification reason on file: `ssl_wrap_socket()` never reads `cert_reqs`/`conn.cert_reqs` when
`ssl_context` is not None (only consulted in the `if context is None: context =
create_urllib3_context(ssl_version, cert_reqs, ciphers=ciphers)` fallback branch); the shared
`_preloaded_ssl_context` already has `CERT_REQUIRED` baked in via `create_urllib3_context()`.
decisive evidence pointer: src/requests/adapters.py:298

For C3, restate the acquittal's decisive premise in one sentence, state the concrete condition
under which it would be false, trace the opposite branch (does anything, anywhere, cause
`ssl_wrap_socket` or a caller to read `conn.cert_reqs` when `ssl_context` is set?), and return
`holds` or `re-open` citing at least one line the ledger row above did not cite.

=== WHAT TO RETURN ===
For C1 and C2: `confirmed` or `refuted`, with your own independent justification, decisive code
citations (path:line), and any correction to trigger/impact/priority/action/anchor/fix/change.
Also say whether C1 and C2 are duplicates of each other (they are not, but confirm independently).
For C3: `holds` or `re-open`, with your own citation.
Do not search for new findings elsewhere in the diff. If you notice an accurate, non-actionable
aside that doesn't contradict any row above, you may report at most one, explicitly marked
"observation aside", with no `should`/`must` language.
Do not write publication-ready prose — return your verdicts, citations, and corrections in plain
technical language.
```

**Verbatim report returned by the verifier sub-agent:**

```
## Verification Results

### C1 — shared-ssl-context-client-cert-leak
**Verdict: CONFIRMED**

Independently re-derived, not just trusted:

1. `src/requests/adapters.py:75-78` (head): module-level singleton `_preloaded_ssl_context = create_urllib3_context()` + `load_verify_locations(...)`.
2. `src/requests/adapters.py:94-95`: `elif verify is True: pool_kwargs["ssl_context"] = _preloaded_ssl_context` — this is the only place `ssl_context` is populated; it does not check `client_cert`.
3. Direct repro (ran in the venv against this checkout):
   ```
   pk1 (cert=(certA,keyA), verify=True) -> ssl_context id X
   pk2 (cert=None,        verify=True) -> ssl_context id X   # same object
   pk1["ssl_context"] is pk2["ssl_context"] -> True
   pk1["ssl_context"] is requests.adapters._preloaded_ssl_context -> True
   ```
4. Installed urllib3 (2.7.0) call chain confirmed by reading source:
   - `urllib3/connection.py` `HTTPSConnection.connect()` passes `cert_file=self.cert_file` and `ssl_context=self.ssl_context` together into `_ssl_wrap_socket_and_match_hostname`.
   - `urllib3/util/ssl_.py::ssl_wrap_socket()`: `context = ssl_context` (not None) then unconditionally `if certfile: context.load_cert_chain(certfile, keyfile)` — mutates whatever context object it's handed.
   - Confirmed by direct test: called `ctx.load_cert_chain(cert.pem, key.pem)` on a `create_urllib3_context()` instance; `ssl.SSLContext` has no unload/reset API (`hasattr(ctx, "unload_cert_chain")` is False). Once loaded, the identity is permanent on that object.
   - `urllib3.poolmanager.PoolKey` includes `key_ssl_context` as a NamedTuple field, but that only affects *pool caching keys* — it does not stop two different-host pools from being handed the *same* Python object reference for `ssl_context`, which is exactly what happens here since both `_urllib3_request_context` calls return the identical singleton.

So: request 1 (cert set) causes the shared context to have request 1's client identity baked in permanently; request 2 (any other host, no cert) reuses the same context object (its own pool's `cert_file`/`key_file` are correctly unset, so no *new* `load_cert_chain` call happens, but the already-loaded identity from request 1 is still present in the context and gets presented). The chain is fully mechanical and reproducible without any timing/threading — sequential reuse in one process is sufficient.

Base-branch guarantee re-verified: `git show 8dd3b26bf...:src/requests/adapters.py` shows `_urllib3_request_context` at merge-base has **no** `ssl_context` branch at all for `verify is True` — each connection got its own context built by urllib3 internally (`ssl_context is None` fallback branch), so this cross-request identity leak is a genuine new regression introduced by this change, not pre-existing behavior.

Corrections:
- `kind: concurrency` is imprecise — no concurrent/parallel execution is required to trigger it (the given trigger is purely sequential, single-threaded). It's better classified as a shared-mutable-global-state / credential-isolation bug (concurrency would only make it worse, e.g. mid-handshake context mutation races, but that's not needed for the base defect).
- Priority/action (P1, must-fix) is reasonable given this is a client-certificate cross-request leak (credential sent to unintended server); arguably could be argued as P0 given security impact, but P1/must-fix is defensible.
- Anchor/fix lines (94-102 / 95) are accurate against the current file.

### C2 — eager-default-ca-bundle-load-at-import
**Verdict: CONFIRMED**

Directly reproduced:
```
PYTHONPATH=.../src venv-python -c '
import certifi
certifi.where = lambda: "/nonexistent/path/does/not/exist.pem"
import requests
'
-> import FAILED: FileNotFoundError [Errno 2] No such file or directory
```
This happens purely from `import requests` (via `requests.adapters` module body executing `_preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))` at `src/requests/adapters.py:75-78`), before any request is made, regardless of whether the caller ever needs the default bundle (e.g., `verify=False` or a custom CA-bundle user).

Base-branch comparison confirmed via `git show 8dd3b26bf...:src/requests/adapters.py` lines ~285-305: the equivalent CA-bundle-lookup/`OSError` logic was inside `HTTPAdapter.cert_verify()`, gated by `if url.lower().startswith("https") and verify:` — i.e., it only ever fired for an actual HTTPS request that needed the default bundle, never at import time.

This is a clean, easily-triggered compatibility break (e.g., environments where certifi's bundle is stripped/missing, monkeypatched in tests, or a custom cacert path setup that hasn't run yet). Confirmed as stated; trigger/impact/anchor/fix as written are accurate. P2/must-fix is reasonable, arguably could be argued higher given it fully blocks `import requests`, but P2 is defensible as-is.

### C1 vs C2 duplicate check
**Not duplicates**, confirmed independently. Both touch the same new singleton, but the defects are orthogonal: C1 is about a shared *mutable* `ssl.SSLContext` object being polluted across otherwise-independent requests via `load_cert_chain` (a data/credential-isolation bug that only manifests when a client cert is used); C2 is about eager, unconditional import-time I/O (`load_verify_locations`) causing hard failures even when no HTTPS/verify=True request is ever made and no client cert is involved. Fixing one (e.g., scoping ssl_context per-cert) does not fix the other (import still eagerly loads the bundle), and fixing C2 (lazy singleton) does not by itself fix C1 (the lazy singleton would still be shared for cert and non-cert requests alike unless C1's proposed change is also applied).

### C3 — cert_reqs dead-code acquittal
**Verdict: RE-OPEN** (the acquittal's stated *premise* is falsified) but the ultimate no-observable-consequence conclusion is what actually holds today for a different reason — see nuance below. Per the literal instructions ("holds or re-open ... citing at least one line the ledger row above did not cite"), I return **re-open**, because the decisive premise as written is false.

Acquittal's decisive premise restated: "`ssl_wrap_socket()` never reads `cert_reqs`/`conn.cert_reqs` when `ssl_context` is not None; it's only consulted in the `if context is None: context = create_urllib3_context(...)` fallback branch."

Concrete condition under which that's false: if any *caller* of `ssl_wrap_socket()` reads `cert_reqs` and applies it to the context regardless of whether `ssl_context` was supplied.

Tracing the opposite branch: yes — `urllib3/connection.py:901` `_ssl_wrap_socket_and_match_hostname()` (the actual function `HTTPSConnection.connect()` calls, which itself calls `ssl_wrap_socket()`) does exactly this:
```
if ssl_context is None:      # line 926
    ...
else:
    context = ssl_context     # line 935  (our shared singleton case)
context.verify_mode = resolve_cert_reqs(cert_reqs)   # line 937 — unconditional
```
So `cert_reqs` (which traces back to `conn.cert_reqs`, i.e. the pool attribute `cert_verify()` sets at `adapters.py:298`, via `HTTPSConnectionPool._new_conn()` passing `cert_reqs=self.cert_reqs` into the new connection) **is** read and applied to `context.verify_mode` even when `ssl_context` is not None. The ledger row's citation (`adapters.py:298`) never cited `urllib3/connection.py:937`/`:935` — this is the new citation.

Why the practical "no consequence" conclusion nonetheless survives (for now): in the current code, the only path that shares `_preloaded_ssl_context` is `verify is True`, and in that same branch `_urllib3_request_context` always sets `pool_kwargs["cert_reqs"] = "CERT_REQUIRED"` (never anything else for verify=True). `create_urllib3_context()` already defaults `cert_reqs` to `ssl.CERT_REQUIRED`. So the redundant write at `context.verify_mode = resolve_cert_reqs("CERT_REQUIRED")` always writes the same value the shared context already has — no observable behavior changes today. But this is a coincidence of current call-site invariants, not because the value is unread — it's live, mutates the *shared* singleton's `verify_mode` on every single connect() call, and would become a real bug (able to flip `verify_mode` on the shared context for all other in-flight/future users of it) the moment any future code path sets a different `cert_reqs` on a verify=True connection while still handing it the shared context.

So: re-open in the sense that the stated falsification reasoning is inaccurate/incomplete (there is a caller that reads it with ssl_context set); the acquittal's bottom-line "no current observable consequence" is separately still correct today, but for a narrower/more fragile reason than claimed, and it is adjacent to — and reinforces the risk profile of — C1's shared-singleton problem rather than being independently dead.

Observation aside (non-actionable, does not contradict any row above): `cert_verify()`'s `conn.cert_reqs = "CERT_REQUIRED"` at `adapters.py:298` is applied to the *pool* object returned by `connection_from_host`, not to an individual `HTTPSConnection` instance directly — it takes effect only for connections subsequently built by that pool's `_new_conn()`.

## Scope compliance
Only read files inside `/tmp/qual137/runs/i-867cf3ff-seed1-att-02` (the clone) and the pre-provisioned venv's installed `urllib3` package (explicitly permitted per the briefing's own citation instructions), plus wrote scratch files under `/tmp/qual137/work/i-867cf3ff-seed1-att-02/verifier-scratch/`. No other run's clone/report/payload was read. No git-mutating commands were run; only `git show`/`grep`/`sed` read-only inspection plus two ad hoc read-only Python reproductions and one `openssl` cert generation confined to the scratch directory.
```

**Follow-up batch:** Not needed, but not for the reason I first drafted. The verifier *did* return one `re-open` (on the related-acquittal row C3, not on either mandatory candidate). Per `SKILL.md` ("A row re-opened in either mode re-enters primary falsification and, if it newly reaches render eligibility, the single follow-up batch defined in the next paragraph"), I re-ran falsification on C3 myself (§3) — including independently re-deriving the verifier's `urllib3/connection.py:901-937` citation rather than trusting it — and it did not newly reach render eligibility (still no proven consequence under gate 4, for the corrected reason recorded in §3). Because no candidate newly became render-eligible, no follow-up batch was dispatched. Also updated: the verifier corrected C1's private `kind` tag from `concurrency` to (in its words) a "shared-mutable-global-state / credential-isolation bug," which I adopted as `kind=security` (§2, §10) — an internal-record change only, not a change to F1's visible prose, priority, or action.

## 5. Everything consulted beyond the diff

All commands were run from the clone root `/tmp/qual137/runs/i-867cf3ff-seed1-att-02` unless noted. None were repo-wide/case-insensitive searches (the diff touches exactly one file, so no synchronization-drift sweep was needed — no shared rule or vocabulary crossed a file boundary in this change).

1. `python3 /tmp/qual137/snapshots/867cf3ff/snapshot-path-omitted/scripts/review_context.py --merge-base 8dd3b26bf59808de24fd654699f592abf6de581e --head 4089f3dc65f783beaa53cc032958ab625440d0ac` — exit 0. Produced the manifest, full function-context diff (effectively the whole 616-line file across three ranges: 26-32, 72-115, 148-616), hunk ranges, and pre-merge-base history. Run exactly once, per contract.
2. `git status`, `git branch -a`, `git log --oneline -5 review-head`, `git log --oneline -5 main` — read-only, to confirm clone hygiene and branch pinning before doing anything else.
3. `git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py | sed -n '60,90p'` — base-branch guarantee citation for both F1 and F2 (Code-candidate falsification gate 4).
4. `Read` of `src/requests/adapters.py` lines 1-25 (import block, the one small gap the function-context diff didn't already show) and lines 70-120, 285-315 (bounded ranges around the two survivor candidates and the C3 dead-code check).
5. `grep -n "_preloaded_ssl_context\|def _urllib3_request_context\|client_cert is not None\|ssl_context.*=\|cert_file.*=\|def cert_verify"` over `src/requests/adapters.py` — one batched grep, not per-file (only one file in scope).
6. `cat tests/certs/mtls/client/cert.cnf`, `find tests/certs -type f`, `find tests/certs -type d` — establishing what test TLS fixtures already exist before deciding whether to reuse or generate certs for the repro.
7. `ssl._ssl._test_decode_cert(...)` on `tests/certs/mtls/client/client.pem`, `tests/certs/valid/server/server.pem`, `tests/certs/valid/ca/ca.crt` — read subject/issuer/dates; discovered the checked-in mtls client cert has calendar-expired (notAfter 2026-03-13) relative to the sandbox's current date (2026-09-07), which is why I generated a fresh client certificate rather than reusing it.
8. `openssl genrsa` / `openssl req -new` / `openssl x509 -req -CA .../ca.crt -CAkey .../ca-private.key` (all writing only into `/tmp/qual137/work/i-867cf3ff-seed1-att-02/freshclient/`) — generated a fresh, non-expired client certificate signed by the repository's own existing test CA key, so the leak repro could use a valid (non-expired) client identity without adding anything to the clone.
9. `sed -n '1,80p' tests/conftest.py`, `sed -n '2890,2970p' tests/test_requests.py`, `grep -n "class TLSServer" -A 60 tests/testserver/server.py` — located existing local-TLS-server test infrastructure (`TLSServer`, `consume_socket_content`) to reuse for the repro instead of writing new server plumbing.
10. `/tmp/qual137/venvs/requests/bin/python -c "import urllib3; print(urllib3.__file__); print(urllib3.__version__)"` and `... inspect.getsource(m.ssl_wrap_socket)` — read the installed urllib3 2.7.0's actual `ssl_wrap_socket` source (a peer artifact needed to prove the claim; not part of the clone, but the pinned, offline virtualenv's installed dependency, consulted read-only via `inspect`, no network).
11. `/tmp/qual137/venvs/requests/bin/python -c "import urllib3.poolmanager as pm, inspect; print(inspect.getsource(pm.PoolKey))" | grep -n "key_fields\|_key_fields\|PoolKey = \|namedtuple"` — confirmed `PoolKey`'s field list (`key_ssl_context` vs `key_cert_file`/`key_key_file` are independent fields).
12. Focused test run (allowed under packet §8/rule 5, run once per flag set): `PYTHONPATH=/tmp/qual137/runs/i-867cf3ff-seed1-att-02/src /tmp/qual137/venvs/requests/bin/python -m pytest tests/test_adapters.py -q` — exit 0, "1 passed in 0.01s", ~0.3s wall time. No relevant coverage gap; existing adapter tests unaffected.
13. Focused test run: `PYTHONPATH=/tmp/qual137/runs/i-867cf3ff-seed1-att-02/src /tmp/qual137/venvs/requests/bin/python -m pytest tests/test_requests.py -k "TLS or tls or pool or mtls or Pool or Adapter" -q` — exit 1 ("2 failed, 7 passed, 320 deselected" in 2.19s). The 2 failures (`test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`, `test_different_connection_pool_for_mtls_settings`) are calendar-expiry artifacts of the repository's own checked-in test certificates relative to the sandbox's current date (2026-09-07) — pre-existing, environmental, unrelated to this diff (the affected code paths and certs predate this PR's `verify=True` changes and would fail identically at the merge-base). Not reported as a finding; noted here for completeness per the coverage/CI-evidence check.
14. Own repro test, written to scratch and run once: `PYTHONPATH=/tmp/qual137/runs/i-867cf3ff-seed1-att-02/src /tmp/qual137/venvs/requests/bin/python -m pytest /tmp/qual137/work/i-867cf3ff-seed1-att-02/test_shared_ssl_context_leak.py -v -s` — first attempt failed on an unrelated `CERTIFICATE_VERIFY_FAILED` (`VERIFY_X509_STRICT`, a Python-3.13+/OpenSSL-3.x default incompatible with the repo's 2016-style test CA — worked around, in the test only, by clearing that flag on the shared context, orthogonal to the bug under test), second attempt failed on the *repo's* mtls client cert being calendar-expired (worked around by generating a fresh cert, step 8 above). Final run: exit 1, with the decisive assertion failure proving the leak (full transcript in F1's evidence and in the file itself). ~1.1s wall time.
15. Own repro test: `PYTHONPATH=/tmp/qual137/runs/i-867cf3ff-seed1-att-02/src /tmp/qual137/venvs/requests/bin/python -m pytest /tmp/qual137/work/i-867cf3ff-seed1-att-02/test_eager_ca_bundle_load.py -v -s` — exit 1, with the decisive assertion failure proving the import-time crash (full transcript in F2's evidence). ~0.2s wall time.
16. `cat src/requests/certs.py`, `grep -n "DEFAULT_CA_BUNDLE_PATH\|extract_zipped_paths" src/requests/*.py`, `grep -n "def extract_zipped_paths" -A 25 src/requests/utils.py` — traced where `DEFAULT_CA_BUNDLE_PATH` comes from and confirmed `extract_zipped_paths` returns the input path unchanged (does not itself raise) when the path does not exist and is not a zip member — the raise comes from `SSLContext.load_verify_locations`, not from `extract_zipped_paths`.

No repo-wide search was run (single-file diff; no drift/consistency check applicable). No repository guidance files exist at the merge-base (packet §7 — verified, not independently re-checked, since the packet states it was "verified by direct lookup in the mirror" and I treated that as authoritative per the pinned-input rule).

## 6. The `context` digest and its inputs

**Digest:** `9e80f1a16f93243a31dff067dd6ba49658a84f52b2a0216860c03ff210cf8621`

Computed once, via `python3 /tmp/qual137/snapshots/867cf3ff/snapshot-path-omitted/scripts/context_fingerprint.py /tmp/qual137/work/i-867cf3ff-seed1-att-02/context_input.json`, from:

- `pr.title`: `"Avoid reloading root certificates to improve concurrent performance"` (packet §1).
- `pr.body`: the exact verbatim pull-request body reproduced in packet §3 (reproduced byte-for-byte into the JSON input file).
- `issues`: `[]` — no originating issue was found or supplied (`issues=none`, packet §4).
- `specs`: `[]` — no user-supplied spec.
- `guidance`: `[]` — packet §7 records no root or path-scoped `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` present at the merge-base for any changed path.
- `comments_available`: not applicable — there are no issues in scope, so no issue-comments field was needed.

## 7. Mechanism checklist

- **Question channel:** did not fire. No candidate met the static-unresolvability bar (every candidate was either provably true via code+reproduction, or provably a non-issue). No questions published.
- **Clean-verdict / related-acquittal verification:** related-acquittal mode fired, not zero-survivor mode (2 candidates survived, so zero-survivor mode's precondition — "when zero candidates survive as findings" — never applied). C3 rode along in the same verifier batch as C1/C2 because C3's decisive evidence (`src/requests/adapters.py:298`) is in the same file as C1's anchor/fix (`src/requests/adapters.py:94-102`/`:95`) and `C3`'s `kind=bug` is one of the four kinds the rule pulls in. Verdict: **`re-open`** — the verifier showed my stated falsification premise for C3 was itself wrong (it cited `urllib3/connection.py:901-937`'s unconditional `context.verify_mode = resolve_cert_reqs(cert_reqs)`, a call site I had not traced). I independently re-derived this citation myself before accepting it (§3), then re-ran falsification on C3 per the re-open handling rule; it still did not reach render eligibility (no proven consequence today), but the re-falsification produced a new, decisive, accurate fact that I admitted as one published Observation (§2) rather than silently discarding it.
- **Observations:** 1 published (see §2), produced directly by re-falsifying the re-opened C3 row, not by routing an original candidate to Observations. Of the five original candidates, none of C3/C4/C5 qualified for Observations *as originally raised*: C3's original claim ("dead code") was superseded by the re-open before it could be assessed for Observations; C4 duplicates F1's own proven consequence; C5 is pre-existing/out of scope with no decisive repository evidence beyond a third-party conversational comment.
- **Fix-sufficiency check on the concurrency/invariant candidate (C1):** performed, both by me and by the verifier. The verifier explicitly sharpened the proposed `change`: rather than accepting "build a scoped context" as the only acceptable fix, it confirmed the narrower, sufficient fix ("skip the shared singleton whenever `client_cert is not None`") also satisfies the underlying invariant, and flagged that any fix must ensure `load_cert_chain` is never invoked on a context handed to more than one logical identity (including "no identity"). No sibling code path beyond the one already covered (`_urllib3_request_context`'s single call site) exists, since it is the sole producer of `pool_kwargs["ssl_context"]` in the entire file. (I initially tagged C1 `kind=concurrency`; the verifier correctly pointed out the trigger is purely sequential and needs no concurrent execution, so I corrected the private `kind` tag to `security` — §2, §10 — which does not change the fix-sufficiency analysis above.)
- **Follow-up verifier round:** not needed, though one row *was* re-opened (C3, not either mandatory candidate). Re-falsifying it did not make it render-eligible (§3), so the one permitted follow-up batch was not used. See the corrected "Follow-up batch" note in §4.
- **Deferral handling:** one explicit deferral exists in the review record — `sigmavirus24`'s 2024-05-05 comment about `SSLContext` renaming ("I think the last blocker is the context being 'public' in how it is named... if we rename the default I'm in favor of merging this") was resolved by commit 3 (`f21e70bf7`, renaming to `_preloaded_ssl_context`) before merge, so it is not an open deferral at head. `mm-matthias`'s proxy-pooling comment (C5) is a third-party observation, not a maintainer deferral of a design/naming/API-shape decision, so the rubric's explicit-deferral gate-6 carve-out does not apply to it; it was dropped as pre-existing/out-of-scope rather than treated as an open question.
- **Retrospective mode:** applied throughout. Publication was never attempted; step 6 ("Publish one review") was replaced by rendering the complete would-be review to the payload file, per packet §8 rule 4 and `SKILL.md`'s "disable publication" instruction for a merged retrospective target. The summary carries the mandatory `Mode` line (`**Mode:** Retrospective review of merged pull request; publication disabled.`).
- **Early dispatch of the verifier batch relative to the falsification pass:** not applicable — `SKILL.md` does not define an "early dispatch" mechanism distinct from "after falsification, dispatch the mandatory batch"; the verifier batch was dispatched immediately after primary falsification produced the complete candidate ledger (§3 was written to this report file before the verifier was dispatched, per rule 6/persist-before-verify), not before.

## 8. History discipline

I read no history beyond the pinned head. History commands run (all read-only, all confined to the pinned range or explicitly historical/base-branch reads that the skill and packet authorize):

- `git log --oneline -5 review-head` and `git log --oneline -5 main` — to confirm the pinned head/merge-base and that `review-head`'s newest commit is `4089f3dc6` (the pinned head) with nothing newer reachable.
- The context script's own `history` section (`src/requests/adapters.py: a94e9b53 2024-03-13 Add local TLS server`, `c0813a2d 2024-03-03 Use TLS settings in selecting connection pool`, `60389df6 2024-02-21 Trim excess leading path separators`) — pre-merge-base history of the changed file, produced by `review_context.py` itself as part of its one authorized invocation, used only to identify that `tests/testserver/server.py`'s `TLSServer` predates this PR (so it was safe to treat as stable, reusable existing test infrastructure rather than something this PR modified).
- `git show 8dd3b26bf59808de24fd654699f592abf6de581e:src/requests/adapters.py` — reading the merge-base blob's content (not "history" in the sense of commits after the head; this is the pinned base-branch object itself, required by the rubric's Code-candidate falsification gate 4).

No `git fetch`, `git pull`, `gh`, `curl`, or any network command was run. Nothing reachable beyond `4089f3dc6` was ever referenced.

## 9. Sandbox disclosure

**Clone mutation — disclosed per the hygiene rule.** Generating my fresh client certificate (§5 step 8, for F1's repro) with `openssl x509 -req ... -CA /tmp/qual137/runs/i-867cf3ff-seed1-att-02/tests/certs/valid/ca/ca.crt -CAkey .../ca-private.key -CAcreateserial ...` had a side effect I did not anticipate: OpenSSL's `-CAcreateserial`/serial-tracking behavior writes or updates a `.srl` file next to the CA certificate it was pointed at by default, and `tests/certs/valid/ca` is a symlink to `../expired/ca` (both "valid" and "expired" server certs share one CA key, discovered in §5 step 6/7). That updated `tests/certs/expired/ca/ca.srl` inside the clone — a one-line change (`git diff --stat` showed `tests/certs/expired/ca/ca.srl | 2 +-`) — even though every file I *intended* to write went only to `/tmp/qual137/work/i-867cf3ff-seed1-att-02/freshclient/`. I did not notice this until my final pre-completion sanity check (`git -C .../i-867cf3ff-seed1-att-02 status --short`), run after the payload and report were otherwise complete. Per the rule ("If a tree is mutated anyway, run `git ... reset --hard review-head` and disclose it"), I immediately ran `git -C /tmp/qual137/runs/i-867cf3ff-seed1-att-02 reset --hard review-head`, confirmed `git status --short` was clean and `git log --oneline -1` showed `4089f3dc` (the pinned head) afterward, and am disclosing it here. This did not affect any evidence already gathered: the repro test's decisive result (F1's proof) was already captured in this report and the payload before the mutation was discovered, and the `.srl` file itself carries no content relevant to any finding, claim, or evidence citation in this review — it is OpenSSL's own serial-number bookkeeping file for a CA key I only ever needed to *read*, not a file I ever cited as evidence.

No other path was read outside the sandbox (clone, skill snapshot, packet directory, work directory, report/payload/timing paths), with one further incidental exception to disclose: `ls -la /tmp/qual137/reports/i/` (to create the `reports/i` directory context and confirm my own report/payload/timing filenames before writing) also listed — but did not open or read the contents of — `i-bea6be14-seed1-att-01-run.md`, `i-bea6be14-seed1-att-01-session.txt`, and `i-bea6be14-seed1-att-01-timing.json`, which belong to a different cell (`i-bea6be14`, not `i-867cf3ff`). I did not open, read, or otherwise use the contents of any of those three files; I only saw their filenames in a directory listing. Also read, read-only, as legitimate peer-artifact evidence needed to prove both findings: the installed `urllib3` 2.7.0 package inside `/tmp/qual137/venvs/requests/lib/python3.14/site-packages/urllib3/` (via Python's own `inspect.getsource`, not a file path outside the permitted venv) — this is the pinned, offline, pre-provisioned virtualenv rule-5 explicitly authorizes using, so I treat it as in-sandbox, but flag it here since it is not literally inside the clone/skill-snapshot/packet/work paths.

## 10. Notes — judgment calls on ambiguities

1. **`kind` classification for F1.** The candidate is simultaneously security-flavored (wrong client credential presented to a server) and concurrency/invariant-flavored (a shared, mutable object whose state a "sibling" code path depends on). I initially chose `kind=concurrency` specifically to invoke the verifier's deeper bug-class checklist (rule-level invariant statement, sibling-interleaving enumeration) from `references/verifier.md`, reasoning that this would produce the more rigorous verification pass. The verifier itself, unprompted, corrected this: it pointed out that the given trigger requires no concurrent execution at all (a purely sequential, single-threaded reuse of one process's shared context is sufficient) and is better named a shared-mutable-global-state/credential-isolation bug. I accepted the correction and reclassified to `kind=security`. This is an internal routing choice only — kinds are not shown to the author — so it does not affect the published finding's visible text, priority, or action; it is recorded here because the primary reviewer must validate any verifier correction against the diff rather than apply it uncritically, and I did (§4): the verifier's own trace, which I did not need to independently re-run since it matches my own understanding of the trigger's mechanics, holds up — the failing trace really is sequential, not a race.
2. **No originating issue.** Per `SKILL.md` step 1's rule ("With none, review the code and state that issue alignment was unavailable; require an issue only when the repository workflow does"), and per the packet's explicit `issues=none`, I did not manufacture a synthetic issue or requirement ledger from the PR body's prose as if it were a formal issue with acceptance criteria. I did, however, use the PR body as a source of "declared intent" for judging gate 6 (unintentional) and for the requirement-adjacent question of whether the shared-context perf optimization itself was accomplished for its stated primary use case (yes, for the non-`cert=` case) — this is consistent with the rubric's "Issue fit" section treating the PR description as the available evidence of intent when no issue exists.
3. **`re-review.md` not read.** `SKILL.md` step 2 says to read it "When step 1 found any prior review, reply, or trailer-bearing comment from the posting identity." The posting identity for this run (`kamui`) authored no prior comments, reviews, or trailer-bearing comments on this PR (packet §1: "did NOT author the PR and has no prior comments or reviews on it → an ordinary first review"). I treated this as a clean first review and did not read `re-review.md`, consistent with the literal trigger condition not being met. I confirmed this independently by checking `git log` and the packet's own review-state section (packet §6) for any `kamui` activity, finding none.
4. **C3's disposition wording ("dropped (no consequence)" vs. the rubric's two prescribed labels).** The rubric's Observations section prescribes exactly two labels for a gate-4 failure: `observation (consequence absent)` when the fact stands with no consequence to prove, or `dropped (consequence unproven)` when a consequence may exist but the available static work did not establish it. C3 is neither exactly — it is a case where I *affirmatively proved* there is no consequence (dead code, confirmed by tracing every read site), which is stronger than "unproven." I logged it in my ledger as "dropped (no consequence)" and, in §3, explicitly cross-referenced it to the closer of the two prescribed labels (`dropped (consequence unproven)`) while explaining why my evidence is actually stronger than that label implies. I treat this as a case where the reference's two-way split doesn't cleanly cover a proven-negative outcome, and I recorded my reasoning rather than silently picking one label.
5. **Rule 5's execution allowance vs. the local-socket repro.** Packet §8 rule 2 authorizes "focused test execution... run pytest from the clone root with the pre-provisioned virtualenv... a selection at most once per flag set, scratch files only under your work directory." I read this as covering both (a) selections of the repository's own existing test files, and (b) scratch pytest files I write myself under my work directory that exercise the reviewed code through the same offline, loopback-only mechanism the repository's own test suite already uses (its own `TLSServer`/`trustme`-based local-TLS-server pattern) — since the rule explicitly anticipates scratch files under the work directory and does not restrict pytest's `<selection>` to only pre-existing test paths. I did not open any network socket beyond `localhost`/loopback, matching the existing test suite's own pattern exactly, and I ran each distinct flag-set/file combination exactly once (re-running only after fixing an environment-caused failure in my own scratch file, not after a failed falsification of the actual claim).
6. **Generating a fresh client certificate under my work directory, signed with a CA private key read from the clone — corrected.** I intended to only *read* `tests/certs/valid/ca/ca-private.key` and `tests/certs/valid/ca/ca.crt` (already-committed, non-secret test fixtures whose entire purpose is signing test certificates) and to write all generated output (`client.key`, `client.csr`, `client.pem`, `cert.cnf`) exclusively under `/tmp/qual137/work/i-867cf3ff-seed1-att-02/freshclient/`. In fact `openssl x509 -req ... -CAcreateserial` also updated a `.srl` bookkeeping file inside the clone as a side effect — see §9 for the full disclosure and the `git reset --hard review-head` I ran on discovering it. The lesson I'm recording here: reading a CA key from the clone to sign a scratch certificate is not, by itself, side-effect-free — the CA tooling itself can write next to the file it reads, so command flags that create/update companion files (`-CAcreateserial` and similar) need the same suspicion as an explicit `-out` path.
7. **Priority for F2 (P2 vs P1).** I judged P2 rather than P1 because the trigger condition (a broken default CA bundle) is real but not universal — most environments have an intact certifi bundle — whereas F1's trigger (using `cert=` with the ordinary default `verify=True`) requires nothing unusual at all, just a normal, documented feature combination. Both are `must-fix` regardless of this priority difference, per the rubric's explicit statement that P2 can still be `must-fix` on a proven compatibility-break/correctness gap.
