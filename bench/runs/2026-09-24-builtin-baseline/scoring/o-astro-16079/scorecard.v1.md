# Scorecard: o-astro-16079, mapping v1

Register v1 (1978c85a1dfe), rubric v1, scored at 2026-09-25T20:52:48Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 b9574ef6efcf3b55a4d42ee8931c4e9517d265addd5d50e264304bf8cc0b3d85; session d6d7f9d4-35e5-4f75-bc89-116072496563; read audit clean.

## att-030 (codex-default), blind-d82d5c

Verdict 'patch is incorrect'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-o1`, fix sufficient, priority error False, group none. Quote: 'An unauthenticated request carrying x-vercel-isr: 1 can now override routing through x_astro_path, including on _render... returns {"id":"public"} without this header but {"id":"private"} with it... Authenticate the override rather than treating a literal header value as proof of an internal ISR request.' Recovers GT-o1; authenticating the override (unforgeable proof) is the required outcome and closes both the /_isr and _render manifestations.

## att-031 (review-code-sonnet-high), blind-4afe8e

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-o1`, fix sufficient, priority error False, group none. Quote: 'Do not trust a client-settable header to allow path override... re-opening the override #15959 closed: in-process, /api/public returned {"id":"private"} with the header'. Recovers GT-o1 (entrypoint.ts:24-26). Fix: 'honour x_astro_path only in the ISR function (build-time flag) ..., or authenticate the request with a value clients cannot forge'. The unforgeable-value option meets the required outcome (upstream used middlewareSecret as a path token); ISR-only flag alone would be partial, but the sufficient option is proposed.
- item-1: `non-material`, fix n/a, priority error False, group none. Quote: 'if( lacks a space and the realPath = request.headers.get(ASTRO_PATH_HEADER) line lacks a semicolon'. True (entrypoint.ts:22-23) but style only; register non_defects rules formatting as style.

## att-032 (claude-builtin-sonnet-high), blind-512ebd

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-o1`, fix partial, priority error n/a, group blind-512ebd:g1. Quote: 'The path override now trusts a client-controllable x-vercel-isr: 1 header together with the x_astro_path query param, and this replaces the middleware-secret check'; 'GET /api/public?x_astro_path=/api/private with x-vercel-isr: 1 ... Astro routes to /api/private. This bypasses edge middleware, firewall rules and path-based auth'. Recovers GT-o1. No Fix line; the consequence only notes the change 'adds no verification that the request really came from the ISR proxy, such as a secret or an ISR-only function path' - an implied direction mixing a sufficient (secret) and an insufficient (ISR-only function path, leaves /_isr open) option without committing to either, so partial.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'x_astro_path value is applied to url.pathname without validation, and the param is left in the query string'; user code sees 'Astro.url.searchParams... polluted'. Register non_defects: param leakage predates #15959 and has no demonstrated consequence; traversal/redirect via pathname setter unsupported (origin cannot change). The item asserts no concrete harm beyond 'behave differently', so non-material rather than false.
- item-2: `defect:GT-o1`, fix absent, priority error n/a, group blind-512ebd:g1. Quote: 'the existing security tests do not cover the header-spoofing case... nothing checks that a spoofed header is rejected'. Register non_defects: a no-tests remark is GT-o1 when it names the unauthenticated override, which this does. Duplicate of item 1. Proposes only a test, no corrective change, so fix absent.
- item-3: `non-material`, fix n/a, priority error n/a, group none. Quote: 'if( has no space, the realPath = ... line has no semicolon, and let realPath = undefined is implicitly typed'. True, style/typing only (register non_defects).

## att-033 (claude-builtin-opus-high), blind-e33e0b

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-o1`, fix absent, priority error False, group blind-e33e0b:g1. Quote: 'trusts the client-controllable x-vercel-isr: 1 request header to decide whether x_astro_path may override the path... reopens the path-override bypass that #15959 closed'; _render returns { id: 'private' }. Recovers GT-o1 (_render manifestation). No change proposed in this item.
- item-1: `defect:GT-o1`, fix absent, priority error False, group blind-e33e0b:g1. Quote: 'Inside the real _isr function, x_astro_path is still an unauthenticated, attacker-chosen path. A request to /_isr?x_astro_path=<any route> renders that route... including routes the user listed in isr.exclude'. This is GT-o1's primary (advisory) manifestation, matching the register's reproduction (_isr rendered ISR-excluded /two). The add-on that the result is 'served to other users' from the shared cache is overstated (register non_defects: cache poisoning not demonstrated; cache is keyed on x_astro_path, so only requesters of that same /_isr URL get it), but the mechanism still recovers GT-o1. Same claim family as item 1; no change proposed.
- item-2: `defect:GT-o1`, fix partial, priority error False, group blind-e33e0b:g1. Quote: 'whether the ISR query param is allowed is decided per request from a header, when it should be decided per function at build time... A build-time flag ... that enables the param only in _isr would remove the bypass on _render entirely'. Same GT-o1 mechanism (duplicate). The proposed change fixes only the _render manifestation; /_isr?x_astro_path=<route> (the review's own item 2) stays open, so partial.
- item-3: `false-finding`, fix n/a, priority error n/a, group none. Quote: 'With a valid secret but no x-astro-path header, realPath is null... An _isr request that arrives with a valid secret header (for example, a middleware-forwarded request carrying x-vercel-isr) and without x-astro-path renders the literal /_isr path. The result is a 404'. Refuted: the only producer of the secret, Astro's edge middleware, always sets x-astro-path alongside it (src/serverless/middleware.ts:132-133), so the described request does not arise legitimately; and the secret-branch behaviour is unchanged from the merge-base. No supported 404 consequence.
- item-4: `non-material`, fix n/a, priority error False, group none. Quote: 'the internal x_astro_path search param stays on the request URL passed to user code... leak the internal routing param into rendered HTML'. Register non-defect: leakage predates #15959, no demonstrated consequence.
- item-5: `non-material`, fix n/a, priority error False, group none. Quote: 'If the override value contains ? or already-encoded characters, they end up percent-encoded in the path'; 'x_astro_path=/api/public%3Fa%3Db ... renders the route with param public%3Fa=b'. URL pathname setter percent-encodes ? (register non_defects notes this). The ISR case is identical to pre-#15959 code (git show 335a20416) and the secret-branch case is pre-existing and unchanged; hinges on Vercel $0 substitution which is unverified. No demonstrated consequence from this diff; non-material.
- item-6: `defect:GT-o1`, fix absent, priority error True, group blind-e33e0b:g1. Quote: 'This PR also has no test showing that _render rejects x-vercel-isr: 1 combined with x_astro_path, which is why the bypass in finding 1 went unnoticed.' Names the unauthenticated override (register non_defects: then GT-o1); duplicate of item 1. Test only, no corrective change.
- item-7: `non-material`, fix n/a, priority error False, group none. Quote: 'let realPath = undefined has no type annotation'. Typing/readability only.
- item-8: `non-material`, fix n/a, priority error False, group none. Quote: 'The new lines break the repo's Biome formatting'. True; style only.
- item-9: `non-material`, fix n/a, priority error False, group none. Quote: 'The x-vercel-isr header name is a magic string written inline'. Hygiene remark, no consequence.

## att-071 (review-code-sonnet-high), blind-47426b

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-o1`, fix sufficient, priority error False, group none. Quote: 'A client sends GET /api/public?x_astro_path=/api/private with header x-vercel-isr: 1 ... Without any secret, the entrypoint sets the pathname from the query param ... This is the bypass #15959 closed'. Recovers GT-o1 (register manifestation 2, reproduced in-process as the register did). Fix: 'enable it only for the _isr function (build-time flag) and/or require a trusted proof such as the middleware secret'. Requiring an unforgeable per-build proof satisfies the required outcome for both manifestations; the build-time flag alone would not cover the publicly addressable /_isr, but the 'and/or trusted proof' option is sufficient.

## att-072 (claude-builtin-sonnet-high), blind-c9cf06

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-o1`, fix partial, priority error n/a, group blind-c9cf06:g1. Quote: 'The ISR branch trusts the client-controllable x-vercel-isr: 1 header and the x_astro_path query param with no secret check. This reopens the path-override hole that #15959 closed'; the /api/public -> /api/private example on _render. Recovers GT-o1. No Fix line; the only implied remedy is 'The header is also not restricted to ISR functions, and the entrypoint has no way to tell that it is running as an ISR function' - restricting to the ISR function would still leave /_isr?x_astro_path=<route> (the advisory manifestation) open, so partial.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'The rewrite accepts any string from the query param, with no validation, and leaves x_astro_path in the URL's search params... should be deleted after use'. Empty string -> '/' is accurate; param leakage is a register non-defect (predates #15959, no demonstrated consequence); 'attacker-supplied value changes the route' is GT-o1 already reported in item 1. Hygiene, below threshold.
- item-2: `false-finding`, fix n/a, priority error n/a, group none. Quote: 'The locals header is still gated on hasValidMiddlewareSecret, which the ISR path never satisfies. Edge middleware locals are silently dropped or rejected for ISR requests... returns 403 for a legitimate ISR route'. Refuted: Astro's edge middleware always forwards the secret together with the locals and path headers (src/serverless/middleware.ts:132-134), so a middleware-forwarded request has hasValidMiddlewareSecret true; the locals gate (entrypoint.ts:40-46) is unchanged from the merge-base (introduced by #15959, commit 335a20416). Edge middleware not running for ISR routes is a register non-defect (pre-existing). No 403 on legitimate ISR requests is shown.
- item-3: `defect:GT-o1`, fix absent, priority error n/a, group blind-c9cf06:g1. Quote: 'the existing security tests do not exercise the new x-vercel-isr bypass... the new spoofable path stays green in CI'. Names the unauthenticated override, so per register non_defects this is GT-o1, duplicating item 1. Only a test is suggested; no corrective change.
- item-4: `non-material`, fix n/a, priority error n/a, group none. Quote: 'let realPath = undefined is implicitly typed, and the new block is missing semicolons and a space after if'. True, style only.

## att-073 (claude-builtin-opus-high), blind-dcc55e

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-o1`, fix absent, priority error False, group blind-dcc55e:g1. Quote: 'The path override is trusted whenever the request carries x-vercel-isr: 1, a header the client can set itself, which reopens the path-override bypass that #15959 fixed'; built _render returns {"id":"private"}. Recovers GT-o1 (index.ts:453/474/499 confirm shared entryFile). No change proposed in this item; the remedy appears in item 2.
- item-1: `defect:GT-o1`, fix sufficient, priority error False, group blind-dcc55e:g1. Quote: 'the handler guesses whether it is the ISR function from a request header'; 'A sounder fix would give the ISR function a build-time flag... The other option is to bring back the ISR secret in ISR_PATH that #15959 removed'. Same underlying claim as item 1 (duplicate). #15959 commit 335a20416 indeed says 'remove ISR secret plumbing'. Restoring a per-build secret in the ISR destination is the upstream-shaped fix and closes both manifestations while keeping legit ISR rewrites, so sufficient (the build-time flag alone would leave /_isr open).
- item-2: `defect:GT-o1`, fix absent, priority error False, group blind-dcc55e:g1. Quote: 'The security suite never sends x-vercel-isr... Both path-override-security.test.js and isr.test.js pass on this head (4/4) even though the spoofed-header bypass works'. Names the unauthenticated override (register non_defects: then GT-o1); duplicate of item 1. Test-only suggestion, no corrective change.
- item-3: `non-material`, fix n/a, priority error False, group none. Quote: 'searchParams.get decodes the path before it is assigned to url.pathname... If Vercel substitutes $0 ... without re-encoding it, a request for /api/a%2Fb ... routes differently'. The in-process observation is plausible, but it is conditional on unverified Vercel substitution behaviour and the exact same decode-then-assign code existed before #15959 (git show 335a20416: realPath = headers.get(...) ?? url.searchParams.get(ASTRO_PATH_PARAM)); the PR only restores long-standing behaviour. No demonstrated platform consequence; below the threshold.
- item-4: `non-material`, fix n/a, priority error False, group none. Quote: 'the internal x_astro_path query parameter stays in the URL that user code sees'. True but a register non-defect (predates #15959, no demonstrated consequence).
- item-5: `non-material`, fix n/a, priority error False, group none. Quote: 'a request with an empty x_astro_path rewrites to /'; 'x_astro_path=api/private renders the private route. The value is never checked to be a well-formed absolute path.' Accurate validation observations; selecting a route is GT-o1 (already item 1) and missing slash normalisation adds no separate consequence. Non-material.
- item-6: `non-material`, fix n/a, priority error False, group none. Quote: 'let realPath = undefined has no type annotation'. Typing/style only (register non_defects).
- item-7: `non-material`, fix n/a, priority error False, group none. Quote: 'The new lines break the repo's Biome formatting (if( with no space, missing semicolon on line 23)'. True; style only, later fixed by [ci] format.
- item-8: `non-material`, fix n/a, priority error False, group none. Quote: 'The magic string x-vercel-isr is written inline'. True hygiene remark; header casing/naming is not a defect (register non_defects).

## att-074 (review-code-sonnet-high), blind-28f105

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-o1`, fix sufficient, priority error False, group none. Quote: 'Do not trust a client-settable header to enable path override... carries x-vercel-isr: 1 and ?x_astro_path=/api/private without the middleware secret'; 'undoing the trusted-secret guard from #15959'. Exactly GT-o1's mechanism (entrypoint.ts:24-25 else-if) with the register's _render manifestation reproduced. Fix: 'Gate ... on something only the platform or build can supply (for example a build-time flag enabling it only in the _isr function, or a per-build secret in the ISR destination)'. The per-build secret in the ISR destination is the upstream #17370 shape and closes both /_isr and _render manifestations while keeping legit ISR rewrites; the build-time-flag alternative alone would leave /_isr?x_astro_path=<route> open, but the item offers the sufficient option explicitly.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'An empty x_astro_path= value on an ISR request yields url.pathname = "" ... which resolves to a 404 rather than falling back'. Accurate edge case (URL pathname setter turns '' into '/', which 404s when the app has no index), but only a caller-crafted empty param reaches it; Vercel's legit rewrite supplies $0. No material consequence.

## att-075 (codex-default), blind-a0fd03

Verdict 'patch is incorrect'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-o1`, fix sufficient, priority error False, group none. Quote: 'This fallback accepts a path override without the middleware secret, including in the shared _render handler... /api/public?x_astro_path=/api/private and x-vercel-isr: 1 returns the private route... reintroduces the untrusted route substitution'. Recovers GT-o1. Change: 'Authenticate the override or restrict it to a trusted ISR invocation rather than treating the literal header value as authorization'. Authenticating the override with unforgeable proof is the required outcome and covers both manifestations; judged sufficient, though the 'restrict to trusted ISR invocation' alternative alone would be weaker.

## New candidates

None.
