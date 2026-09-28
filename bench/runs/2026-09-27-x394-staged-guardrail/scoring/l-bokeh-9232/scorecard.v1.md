# Scorecard: l-bokeh-9232, mapping v1

Register v1 (f5b761a87af4), rubric v1, scored at 2026-09-28T03:32:45Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 0990548a0709dd5fd7a5c55d5d22fd43fc61dc5df0d7c06b746690b48306b0b8; session 4993dba3-dec4-412b-842a-22bb26e2ad0e; read audit clean.

## att-006 (review-code-sonnet-high-enforced-x394-trimmed), blind-9aa839

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-l1`, fix sufficient, priority error False, group none. Quote: "_unlocal_date now shows the wrong day for negative-UTC-offset users ... rendered with a value/min_date/max_date coming from the server ... bokeh's Python side always serializes a dt.date/dt.datetime value as a UTC-midnight timestamp ... This diff instead shifts the Date by -getTimezoneOffset() minutes first ... the picker now displays one day earlier" and "under TZ=America/New_York ... head body ... yields 'Mon Jul 29 2019' (wrong)". This is GT-l1's exact mechanism (correction valid only for the local-midnight anchor, wrong for Python's UTC-midnight anchor west of UTC), covering value, min_date and max_date on initial render. Verified in clone: date_picker.ts:78-87 subtracts getTimezoneOffset()*60000, called at lines 67/69/70 on value/min_date/max_date; serialization.py:182-184 serializes a date as ms since epoch as if UTC. Fix: "Do not change _unlocal_date's general UTC-based extraction ... Instead fix ... _on_select stores the selected date as date.toDateString() ... re-parses it ... as LOCAL midnight ... Fix that specific round trip (e.g. normalize/parse the stored string consistently, or track the picked calendar day separately) so both the selection round trip and the server-set-value path read correctly in every timezone." This removes the anchor ambiguity at the source (_on_select) while keeping the UTC extraction that is correct for Python-supplied dates, and it explicitly requires that both paths be correct in every timezone. So it does not bring back the east-of-UTC bug and it meets the register's required outcome (anchor-aware handling, or removing the ambiguity at the source). The fix is somewhat unspecific about the exact encoding, but its stated outcome covers both manifestations, so it is sufficient.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "_unlocal_date mutates its date argument in place (date.setTime(...)) ... every current call site passes a freshly constructed new Date(...) so no aliasing bug is currently observable". This is accurate (date_picker.ts:83; call sites at 67/69/70 each pass a fresh new Date), and the item itself concedes there is no observable effect. The register lists this exact claim under non_defects as style with no observable aliasing. It is below the finding threshold.

## New candidates

None.
