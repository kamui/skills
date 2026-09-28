# Review blind-0ad733

### Item 1
Location: (no file)
Claim: Loading the default CA bundle now happens once at import of `requests.adapters` rather than lazily on the first verify=True HTTPS request, so an unreadable default bundle would surface as an import-time exception instead of the previous per-request `OSError` (a related zip/pyinstaller-extraction concern was already raised and resolved during review by moving the extraction to this same call site).
Consequence: src/requests/adapters.py:75-78; PR conversation comment by sigmavirus24: "Ah, I see that the PR was updated and moved the extraction."
Fix: —
