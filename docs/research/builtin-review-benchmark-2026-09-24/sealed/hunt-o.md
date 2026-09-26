# Hunt (o): security defect (authz/injection) in a web backend — buggy

## Inventory (in order examined)

| # | Repository | PR | Merged | Lines / files | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | nuxt/nuxt | none (direct commit 07e39cd6f2 / 3f3e3fa7b5, 2026-06-02, "Refs: GHSA-mm7m-92g8-7m47"; defect GHSA-hxvh-4h3w-prp9) | 2026-06-02 (commit) | not counted | pass | fail: June 2026, and no merged PR introduced it | – | – | fail: `commits/<sha>/pulls` returns only unrelated later PRs #36000/#36184; private-advisory commit, no review trail | – | – | – | – | – | dropped |
| 2 | spree/spree | #13770 "Unified Carts API" (introduced `find_cart_for_association`, defect GHSA-4825-p4xm-pcf2) | 2026-03-13 | 4740+/4616−, 102 files (gh) | pass | fail: March 2026 (fallback window only) | fail: 9356 lines / 102 files | – | – | – | – | – | – | – | dropped |
| 3 | wintercms/winter | #1473 "Various security improvements" (added `MyAccount` controller, commit 7f4507411; defect GHSA-mpmw-f6h6-3g26, fix cdbc8f5a2) | 2026-04-02 | 994+/61−, 14 files (gh) | pass | fail: April 2026 | fail: 1055 lines / 14 files | – | – | – | – | – | – | – | dropped |
| 4 | deepstreamIO/deepstream.io | introducing change for GHSA-89vx-jh4q-vg3w (PATCH_MULTI missing from Valve RULES_MAP; affects only =10.1.0) | ≤ 2026-05-26 (v10.1.0 release) | not counted | – | fail: v10.1.0 published 2026-05-26, so the change predates July | – | – | – | – | – | – | – | – | dropped |
| 5 | Budibase/budibase | change moving `/api/attachments/:datasourceId/url` from BUILDER to TABLE/WRITE (GHSA-xcx6-4f2g-hhgx) | ≤ 2026-05-28 (3.39.4 release) | not counted | – | fail: 3.39.4 published 2026-05-28 | – | – | – | – | – | – | – | – | dropped |
| 6 | apostrophecms/apostrophe | change that broke the `move()` destination guard (GHSA-wr5r-wqp2-x4fh; fix d50c6ad61 2026-07-08) | 2024-02-06 (commit 9f72bd229 "allow restore pages", found by `git log -S`) | not counted | – | fail: 2024 | – | – | – | – | – | – | – | – | dropped |
| 7 | openchoreo/openchoreo | #3433 (exec handler, 1666+/29−, 16 files) and #3571 (wirelogs handler, 2653+/18−, 19 files); defect GHSA-52gf-6rpq-fgmx, fix #4251 (4d372eaf1) | 2026-05-15 / 2026-05-26 | see left | pass | fail: May 2026 | fail: both over 400 lines | – | – | – | – | – | – | – | dropped |
| 8 | siyuan-note/siyuan | none: commit acfc02ee8 "Improve database field visibility across views" (GHSA-57v5-wqx3-cgj4, fix 64c26e74b) | 2026-07-23 (commit) | not counted | pass | pass (date) | – | – | fail: direct push by maintainer; `commits/acfc02ee8/pulls` returns no PR | – | – | – | – | – | dropped |
| 9 | go-gitea/gitea | #38009 "fix(auth): do not auto-reactivate disabled users on OAuth2 callback" (GHSA-vrhc-jjfc-m3m3) | 2026-06-06 | 71+/5−, 4 files (gh) | pass | fail: June 2026 | – | – | – | – | – | fail: advisory describes #38009 as an incomplete fix ("added a gate intended to reactivate users only when…"); reactivation predates it | – | – | dropped |
| 10 | zalando/skipper | #4126 "doc: Rego policy for max body exceeding" (GHSA-5gpm-rgj3-9q76) | 2026-07-09 | 205+/7−, 4 files (gh) | pass | pass | pass (gh count) | – | – | – | – | fail: advisory calls #4126's `truncated_body` guidance an incomplete mitigation ("fix chain … This finding is the third, still-open variant"); the truncation bypass predates the PR, so the PR did not introduce it | – | – | dropped (near miss) |
| 11 | authorizerdev/authorizer | blame hit: #742 (GHSA-29rf-f4vv-pvq6, OAuth identity linking) | 2026-08-06 | 5707+/211−, 118 files | – | – | fail | – | – | – | – | – | – | – | dropped: blame hit was noise in `cmd/root.go`; the account-linking logic in `oauth_callback.go` is older than #742, and #742 is far too large anyway |
| 12 | tinyauthapp/tinyauth | blame hit: #1026 "refactor: rework scheme validation…" (GHSA-328g-jx67-v94g) | 2026-07-18 | 107+/158−, 7 files | – | – | – | – | – | – | – | – | – | – | dropped: the advisory targets v5.0.7 (commit 479f1657), and the case-sensitive ACL lookup predates #1026, so the blame hit was noise |
| 13 | esphome/device-builder | #265 "Rename auth env vars to ESPHOME_USERNAME / ESPHOME_PASSWORD" (GHSA-rrxg-g2pf-6hh4, fix #1625) | 2026-05-04 | 327+/9−, 4 files (gh) | pass | fail: May 2026 | pass (gh count) | – | – | – | – | weak: the advisory says the rename "intentionally removed the bare names"; losing auth is a consequence of behaviour the PR openly chose | – | – | dropped (fallback-window near miss) |
| 14 | openbao/openbao | introducing change for GHSA-xp3c-3jw3-4vcr (LIST deny bypass with wildcards) | long-standing (range `>= 0.1.0`) | – | – | fail | – | – | – | – | – | – | – | – | dropped |
| 15 | project-zot/zot | introducing change for GHSA-qg67-7m6v-qg25 (DELETE mapped to push scope) | long-standing (range `< 2.1.18`, no lower bound) | – | – | fail | – | – | – | – | – | – | – | – | dropped |
| 16 | BerriAI/litellm | #20602 "fix(mcp): resolve OAuth2 'Capabilities: none' bug…" (GHSA-7488-6r32-c95q says the OAuth2 passthrough fallback was "added in #20602") | 2026-02-06 | 293+/11−, 4 files (gh) | pass | fallback only (Feb 2026) | pass (gh count) | not checked | – | – | – | – | – | – | parked as fallback; not pursued because Astro #16079 (below) is smaller and cleaner |
| 17 | traefik/traefik | #13572 "Fix auth singleflight key collision" (follow-up GHSA-8fcf-v89g-xpg6, fix #13816) | 2026-07-28 | – | pass | pass | – | – | – | – | – | – | – | – | dropped: wrong defect class; GHSA-8fcf is a username-enumeration timing oracle (information disclosure), not authz/injection, and its range `>= v3.6.11` dates the oracle to the original singleflight change, not #13572 |
| 18 | traefik/traefik | introducers of GHSA-m6wx-622r-48r9 / GHSA-cjr6-pf59-jq29 / GHSA-j994-9gqj-9hwq (ingress providers) | ≤ 2026-05-11 (v3.7.0 2026-05-05, v3.7.1 2026-05-11) | – | – | fail: May 2026 | – | – | – | – | – | – | – | – | dropped |
| 19 | go-gitea/gitea | #37698 "fix(web): enforce token scopes on raw, media, and attachment downloads" (named in GHSA-3pww-vcvm-3gmj) | 2026-05-16 | 286+/36−, 5 files (gh) | pass | fail: May 2026 | – | – | – | – | – | fail: the RSS/Atom feed handlers never had the scope check; #37698 added the check elsewhere and did not introduce the gap | – | – | dropped |
| 20 | perses/perses | blame hit 8015fb340b "Merge commit from fork … Fix miss-usage of project query param" (GHSA-vr5f-w35q-98jp) | 2026-07-03 | – | – | – | – | – | fail: private-fork security merge, no PR review | – | – | fail: a fix, not the introducer | – | – | dropped |
| 21 | rclone/rclone | introducer of GHSA-xwwr-4h3p-r22c (serve s3 `--auth-proxy` without `--auth-key`) | long-standing (range `< 1.75.1`; blame hit 2026-09-04 is the fix branch) | – | – | fail | – | – | – | – | – | – | – | – | dropped |
| 22 | withastro/astro | #16079 "fix(vercel): Fix ISR path rewrite to prevent 404" | 2026-03-25T16:40:00Z | 12+/1−, 2 files (numstat merge-base b089b904 → head 71ae5133) | pass (not listed; no withastro entries) | fallback: March 2026, accepted only because no preferred candidate qualified (rows 1–21) | pass | pass: exit 0, cutoff 2026-03-25T16:40:00Z, 1 conversation comment omitted | pass: GitHub-native review (1 APPROVED, 3 conversation comments) | pass: pnpm install 9 s + 2 s, build 10 s, probe 3–4 s; fails at head, passes at merge-base; tree clean | pass: one hunk in `entrypoint.ts`, contract in #15959's changeset/test one hop away | pass: PR promised only to stop ISR 404s | pass: GHSA-x27w-589x-frm2 names "Commit aa266364fe (PR #16079 …) brought the query parameter back"; fix 3a43cf0f36 (#17370, 2026-07-13) by maintainer matthewp | pass: MIT (LICENSE, package.json) | **PASS (fallback)** |
| 23 | middleapi/orpc | #1593 "feat: v2" (blame hit for GHSA-j9v4-rhgr-4m5f, Vary header injection) | 2026-06-21 | 70820+/137766−, 1649 files (gh) | – | fail: June | fail | – | – | – | – | – | – | – | dropped |
| 24 | BerriAI/litellm | #20602 "fix(mcp): resolve OAuth2 'Capabilities: none' bug for upstream MCP servers" (GHSA-7488-6r32-c95q; fix 73869f0faf / #26463 says "added in #20602") | 2026-02-06T23:00:35Z | 293+/11−, 4 files (gh) | pass | fallback only | pass (gh count) | not run | pass (GitHub reviews; only greptile-apps bot) | not run (repo 1.7 GB) | pass | fail/weak: PR body openly promises "on 401/403 failure fall back to permissive `UserAPIKeyAuth()` (OAuth2 passthrough)"; the advisory's defect is that same fallback | pass | pass (MIT outside `enterprise/`) | dropped as alternate (E8) |
| 25 | coder/coder | #17880 "feat: show devcontainer dirty status and allow recreate" (introduced handler for GHSA-jqj2-x4c5-jfxm; fix #25812 bb11946bd4) | 2025-05-19 | – | pass | fail: before 2025-10-01 | – | – | – | – | – | – | – | – | dropped (other Coder v2.34 advisories were backported to the 2.29 ESR line, so also old) |
| 26 | forgekeep/nebula-mesh | #258 "feat(webhooks): managed webhook subscriptions (phase 2)" (named in GHSA-7rx3-5wx3-5v76) | 2026-06-13 | 1375+/85−, 20 files (gh) | pass | fail: June | fail | – | – | – | – | – | – | – | dropped |
| 27 | deepstreamIO/deepstream.io | commit 82ffa8119d "task: allow multiple path updates in one atomic message" (named in GHSA-89vx-jh4q-vg3w) | 2026-05-26 | 162 lines (commit stats) | pass | fallback only | pass | – | fail: `commits/<sha>/pulls` returns no PR (direct push) | – | – | – | – | – | dropped |
| 28 | Budibase/budibase | #18864 "Fix/s3 upload" (commit 23d7531902 "allow app users to generate S3 upload signed URLs"; GHSA-xcx6-4f2g-hhgx) | ≤ 2026-05-28 | not counted | pass | fallback only | – | – | – | – | – | fail/weak: the PR openly aims to let app users obtain signed URLs, which is the advisory's permission change; the advisory lists no fix commit | – | – | dropped |
| 29 | traefik/traefik | #12803 "Make basic auth check timing constant" (commit 122175ac2f; lines up with GHSA-6765-c87h-8mrf range `>= v3.6.11`) | 2026-03-17 | 28+/9−, 2 files (commit stats) | pass | fallback only | pass | – | – | – | fail: #12803 targets `v2.11`, which has no singleflight path (the advisory: "the v2 line do[es] not carry the vulnerable deduplication path"); the collision appears only after the v2.11→v3.6 branch merge b1b520b186, so the reviewed diff does not contain it | – | fail: the advisory does not attribute the defect to #12803 | – | dropped |
| 30 | decolua/9router | blame hit b282f05549 "Refactor" (GHSA-x5c9-v98j-722r) | 2026-06-15 | – | – | fail: June | – | – | fail: direct push, no PR | – | – | – | – | – | dropped |
| 31 | fastify/fastify-static | fix for GHSA-x428-ghpx-8j92 (named in GHSA-83w8-p2f5-377r) | ≤ 2026-04-16 | – | – | fallback only | – | – | – | – | – | fail: GHSA-83w8 is an incomplete fix (range `<= 10.1.0`, all versions); the `..` bypass predates the helper | – | – | dropped |

### How the inventory was searched

- **Advisory feed.** `gh api /advisories` (reviewed, published ≥ 2026-07-01), with CWE sets {862, 863, 639, 285, 284}, {89, 78, 77, 22, 94, 1336, 113, 93}, {306, 287, 288, 425, 915}, {943, 90, 917, 74, 75, 73, 23, 35, 1321, 98, 95, 116}. This gave 1,223 unique advisories (`scratch/all.json`).
- **Pass A: release dates.** For every advisory with a non-zero lower bound, I looked up that version's release date in its registry (npm, PyPI, Go proxy, Packagist, RubyGems, crates.io; `scratch/reldates.py` → `recent.tsv`). Almost every lower-bound release is before July 2026. The in-window ones are n8n (Sustainable Use License, fails E10), Open WebUI (branding-clause licence, not OSI, fails E10), OpenChoreo 1.2.0-rc.1 (the defects are older, `< 1.0.3`), Grav 2.0.7 (an incomplete fix), and non-backends (nltk, pnpm, nx).
- **Pass B: advisory text.** Regex over the descriptions for "introduced in/by", "regression", "added in", "commit `…`", "PR #…" (rows 3–10, 16, 19, 26, 31).
- **Pass C: fix commits and PRs.** For every advisory's fix commit or PR, I grepped the message or body for introduced/regress/caused by/from #N (`scratch/fixmsg.py`; rows 13–17, 24).
- **Pass D: blame.** GraphQL blame of the lines each fix touched, in the fix's parent commit, flagging code last changed on or after mid-June 2026 (`scratch/blamescan.py`, 218 advisories covered). The hits were mostly noise (rows 11, 12, 20, 21, 23, 30).
- **PR search.** Three `gh search prs` queries (merged ≥ 2026-07-01, "revert security…", "introduced in #" authorization, "security regression introduced"). They returned only unrelated low-signal repositories.
- **Result.** No candidate merged on or after 2026-07-01 passed. The two in-window PRs that surfaced both fail E8/E9: skipper #4126 (an incomplete mitigation, not the introducer) and traefik #13572 (a timing oracle, the wrong defect class). The recommendation below therefore uses the 2025-10-01 fallback.

## Recommendation

**Primary: withastro/astro#16079 (fallback window; passes E1–E10).**
**Alternate: none.** No second candidate passed all of E1–E10. The closest misses are listed at the end.

### withastro/astro#16079: "fix(vercel): Fix ISR path rewrite to prevent 404"

- **Repository and people.** withastro/astro; author `empoulter-uclan` (external contributor); base branch `main`.
- **Merged** 2026-03-25T16:40:00Z; merge commit `aa266364fe9e105317b66e218fe04567307fb57f`.
- **Licence.** MIT: the root `LICENSE` reads "MIT License", and `packages/integrations/vercel/package.json` has `"license": "MIT"`. The GitHub API reports NOASSERTION because the monorepo holds more than one licence file.
- **SHAs.**
  - Head: `71ae513388df11d7dad6b1e0077c402ad03d0d62`. This is the PR's only commit, and `git fetch pull/16079/head` resolves to it.
  - PR-recorded base: `be661fb9fd1348ffb038f561f9f053b1c64a3696`.
  - Merge-base I computed on a full clone: `b089b904f1ed578e9edaefd129bf9843120a808f`.
  - They **disagree**: the recorded base is 2 commits ahead of the merge-base (`main` advanced, tip "[ci] format"). `git diff --stat b089b904 be661fb9 -- packages/integrations/vercel` is empty, so the diff under review is identical either way.
- **Changed files** (numstat, merge-base → head): 2 files, 13 lines.

  | File | + | − |
  |---|---|---|
  | `.changeset/common-cats-travel.md` | 5 | 0 |
  | `packages/integrations/vercel/src/serverless/entrypoint.ts` | 7 | 1 |

- **Originating issue.** None (`closingIssuesReferences` is empty). The body says #15959 "introduced a bug with the vercel adaptor which made any route served by ISR result in a 404", noticed in a comment on #15959 (issuecomment-4103539941).
- **Review record up to the merge instant.**
  - `changeset-bot[bot]` posted the changeset notice (12:02Z).
  - `Princesseuh` (maintainer) APPROVED with an empty body at 2026-03-25T12:19:44Z.
  - `leifmarcus` asked when it would be released (16:09Z); Princesseuh replied "Tomorrow most likely, with the rest of 6.1." (16:22Z).
  - A later "Thanks a lot!" (17:12Z) is after the cutoff and is the one omission the packet reports.
  - There are no inline review threads, and **nobody raised the security implication**.

#### The defect

- **Location.** `packages/integrations/vercel/src/serverless/entrypoint.ts`, `fetch()` at the head, lines 21–34. The new `else if (request.headers.get('x-vercel-isr') === '1') { realPath = url.searchParams.get(ASTRO_PATH_PARAM); }` rewrites `url.pathname` to the caller-supplied `x_astro_path` query value. It does this whenever the request carries `x-vercel-isr: 1`, with no check of the per-build `middlewareSecret`.
- **Violated rule.**
  - The contract comes from #15959 (commit 335a204161, 2026-03-19, in the merge-base history two commits before the head on this file). Its changeset `.changeset/short-cycles-fail.md` says: "Fix Vercel serverless path override handling so override values are only applied when the trusted middleware secret is present."
  - Its test `packages/integrations/vercel/test/path-override-security.test.js` asserts `'ignores untrusted x_astro_path query param on _render'`.
  - The PR restores a caller-controlled path override guarded only by a request header, which anyone can send and which Vercel itself sets on external requests to `/_isr`.
- **Trigger.** `@astrojs/vercel` with `isr` enabled, and a route protected at the edge (Vercel path or firewall rule, or `edgeMiddleware: true` auth). Send an unauthenticated `GET /_isr?x_astro_path=/admin`, or in my probe `GET /api/public?x_astro_path=/api/private` with the header `x-vercel-isr: 1`.
- **Demonstrated consequence.** The origin renders the protected route. The edge only saw `/_isr` or `/api/public`, so its rules never applied. My probe at the head returned `id: 'private'` for a request addressed to `/api/public`.
- **Upstream confirmation.**
  - Advisory: GHSA-x27w-589x-frm2, published 2026-07-20, CWE-441/CWE-862, affects `@astrojs/vercel >= 10.0.3, < 11.0.3`. Verbatim: "Commit aa266364fe (PR #16079, "Fix ISR path rewrite to prevent 404") brought the query parameter back, guarded only by the `x-vercel-isr` header. That header is not a security boundary, so the fix was effectively undone for ISR routes starting in 10.0.3."
  - Fix: commit `3a43cf0f3690a8e33cb30109bc5165611cf38fcd`, "fix(@astrojs/vercel): improve internal ISR route handling (#17370)", by maintainer Matthew Phillips (`matthewp`), 2026-07-13; PR #17370 head `b6eb4d1a3c9d1ba05d7e86fc193c9d3ef6c02e3c`; released in `@astrojs/vercel@11.0.3`. The fix commit message is deliberately vague, so the advisory is the identifying record.
  - Parent advisory: GHSA-mr6q-rp88-fx84 / CVE-2026-33768 (published 2026-03-26), fixed by #15959.
- **Corrective outcome.** Any sufficient fix must restore this: an unauthenticated request can never choose the rendered route through `x_astro_path` (or any other override). A path override is honoured only when it provably comes from Astro's own build-time rewrite or middleware (a per-build secret or equivalent unforgeable proof), and the ISR 404 fix must still work. Upstream did this with a secret `x_astro_path_token` added to the rewrite and to `allowQuery`.

#### Tempting false positives

1. **`JSON.parse(astroLocalsHeader)` on a request header** (lines 40–46). Not new, and already gated: without a valid middleware secret the handler returns 403 before parsing.
2. **Non-constant-time comparison `middlewareSecretHeader === middlewareSecret`** (line 20). Pre-existing and unchanged by the PR. It is also a cryptographic-primitive or timing concern, which this slot excludes.
3. **`let realPath = undefined` instead of `null`, and the missing semicolon.** Harmless: `searchParams.get` and `headers.get` return `null` when absent, and `typeof realPath === 'string'` still gates the rewrite. The style issue was fixed by the "[ci] format" commit 66830865d3.
4. **Forwarding `body: request.body` without `duplex: 'half'`.** A pre-existing functional bug for streamed bodies on Node 22+, fixed later by #16486. It is not introduced here and is not a security issue.
5. **Case of the `x-vercel-isr` header name.** `Headers.get` is case-insensitive, so there is no bypass or miss from casing. The real flaw is that the header is trusted at all.

#### Leak set

- **SHAs a truncated mirror must exclude.**
  - Merge commit `aa266364fe9e105317b66e218fe04567307fb57f`.
  - Post-merge format commit `66830865d3` ("[ci] format").
  - Fix `3a43cf0f3690a8e33cb30109bc5165611cf38fcd` (#17370) and its PR head `b6eb4d1a3c9d1ba05d7e86fc193c9d3ef6c02e3c`.
  - Later commits on the adapter's entrypoint or index paths: `0bae1a51f0` (#16486), `5557dcabbf` (#15719), `d1bb7fa005` (#17569), `ce9f1da486` (#17680), `0a22ff5b7e` (#17687), `98c07e1735` (#18044), `a09b3288d5` (#18008).
  - Truncating the mirror at the merge-base `b089b904` is sufficient.
  - The PR has no branch heads after the reviewed head (single commit `71ae5133`).
- **Answer-revealing records.** GHSA-x27w-589x-frm2 / CVE record; GHSA-mr6q-rp88-fx84 (published after the cutoff, and it names the `x_astro_path` query parameter as the vulnerability); PR #17370; the `@astrojs/vercel@11.0.3` release notes; the changeset `.changeset/modern-otters-smoke.md`.
- **Keep visible.** #15959 and its test and changeset predate the review; they are the contract, not a leak.

#### Provisioning and test evidence (run by me)

- **Provisioning.**
  - `git clone https://github.com/withastro/astro.git`: exit 0, 17 s.
  - `corepack pnpm install --frozen-lockfile --filter '@astrojs/vercel...' --filter astro-scripts` (pnpm 10.30.3 from `packageManager`): exit 0, 9 s. The machine's pnpm store was warm.
  - Adding `--filter '{packages/integrations/vercel/test/fixtures/**}'`: exit 0, 2 s.
  - `pnpm -r --filter '@astrojs/vercel...' build`: the first attempt failed (exit 1, 3 s) because nested scripts call `pnpm`, which isn't on PATH. With a scratch shim `scratch/bin/pnpm` → `corepack pnpm` it exits 0 in 10 s at both revisions.
- **Focused probe.** `node --test scratch/probe/isr-path-override.test.mjs` (lives outside the repo) builds the upstream fixture `serverless-with-dynamic-routes` and calls the built `_render` function's `fetch`.
  - Head `71ae5133`: **exit 1, 4 s**. The control (query parameter without the header, rendering `public`) passes. The ISR case fails with `actual: 'private', expected: 'public'`.
  - Merge-base `b089b904`: **exit 0, 3 s**, 2/2 pass ("rendered id with x-vercel-isr: public").
- **Upstream tests.** `node --test test/path-override-security.test.js test/isr.test.js` exits 0 in 4 s with 4/4 passing at **both** revisions. The existing suite never exercised the header branch, which is how the regression passed CI.
- **Tree cleanliness.** `git status --porcelain` was empty after every run; only ignored build outputs appeared (52 `!!` entries).
- **Checkout state.** The clone is left at the head, built.

#### E4

`build_packet.py --repo withastro/astro --pr 16079 --head 71ae5133… --merge-base b089b904… --base-sha be661fb9… --staging scratch/astro --target o --out scratch/packet-16079.md` **exited 0** with the default cutoff 2026-03-25T16:40:00Z. Omitted after the cutoff: reviews 0, thread comments 0, conversation 1, issue comments 0. The packet lists 2 files, 1 commit, 1 review, 3 conversation comments.

#### Confidence

- **High** for the defect and its attribution. The maintainer-published advisory names this exact PR and mechanism. The focused test flips between the merge-base and the head. The diff is 8 code lines.
- **Medium-high** for slot fit.
  - It is a web framework's server-side HTTP entrypoint, and the defect is a missing-authorization / confused-deputy access-control bypass (CWE-862).
  - The platform fact that Vercel sets `x-vercel-isr` on external `/_isr` requests comes from the advisory and can't be verified offline. The defect doesn't depend on it, though: a client-supplied header is not an authorization boundary, and the probe sets it directly.
- **Main caveat.** The merge date is in the fallback window (2026-03-25), so the change may be in reviewers' training data.

## Closest misses (for an alternate)

- **zalando/skipper#4126** (merged 2026-07-09, 212 lines / 4 files, preferred window). Fails E8/E9: GHSA-5gpm-rgj3-9q76 treats its `truncated_body` guidance as an incomplete mitigation of an older bypass, not a defect the PR introduced.
- **BerriAI/litellm#20602** (2026-02-06, 304 lines / 4 files). The upstream fix names it ("added in #20602"). Fails E8: its body openly promises the permissive fallback that the advisory calls the vulnerability. E4 and E6 were not run (the repo is 1.7 GB).
- **esphome/device-builder#265** (2026-05-04, 336 lines / 4 files). The advisory attributes the open dashboard to it, but the removal of the bare `USERNAME`/`PASSWORD` names was intentional (weak on E8).
- **traefik/traefik#12803** (2026-03-17, 37 lines). It lines up with GHSA-6765's range, but its v2.11 diff doesn't contain the collision; that appears only after the branch merge (fails E7/E9).
