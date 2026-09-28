# Scorecard: i-requests-6667, mapping v1

Register v2 (af11241069d2), rubric v1, scored at 2026-09-28T03:04:04Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 9e8a50a3bb78f2f0f0b8b60f6c89b644ee732eafa18f3c6806affe40703c4369; session 292f76b3-5345-42fb-8aca-930ba49bf9b2; read audit clean.

## att-003 (review-code-sonnet-high-enforced-x394-trimmed), blind-0ad733

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery False; false clean False.

- item-0: `defect:GT-i2`, fix absent, priority error n/a, group none. Quote: "Loading the default CA bundle now happens once at import of `requests.adapters` rather than lazily on the first verify=True HTTPS request, so an unreadable default bundle would surface as an import-time exception instead of the previous per-request `OSError`", located at src/requests/adapters.py:75-78. Checked clone/src/requests/adapters.py:75-78 at head: module-level `_preloaded_ssl_context = create_urllib3_context(); _preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))` runs on import. This is GT-i2's mechanism exactly (CA-bundle loading moved from lazy per-verified-request execution to eager unconditional import-time execution), and the stated symptom, an exception raised out of `import requests` where previously the failure was per-request, is the #6764 manifestation class (PermissionError at adapters.py:77 on import). The contrast with the previous lazy behaviour points a reader at the required outcome (defer the load until a verified HTTPS connection is made). It does not mention the import-time cost regression, and its parenthetical treats the zip-extraction concern as resolved, but a partial symptom leading to the same mechanism and corrective outcome is a recovery. Fix line is "—" and the Consequence line only gives a location and a quote, so no change is proposed: fix_sufficiency absent.

## New candidates

None.
