# Scorecard: l-bokeh-9232, mapping v1

Register v1 (f5b761a87af4), rubric v1, scored at 2026-09-27T07:11:04Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 536f41890f5126cff5131aa4fe1fd2a894914e182ae857c3a665306c89356315; session d60d44fe-596f-4bed-bb11-c1134b1ad519; read audit clean.

## att-003 (review-code-sonnet-high), blind-51a062

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-l1`, fix sufficient, priority error False, group none. Quote: "_unlocal_date now unconditionally subtracts `date.getTimezoneOffset() * 60000` from that instant; for a negative offset this ... rolls a true UTC-midnight timestamp back into the previous UTC calendar day" when `value`, `min_date`, or `max_date` is "set from the Python/server side" and rendered "in a browser whose local timezone has a negative UTC offset"; "head returns `Thu Sep 19 2019`, merge-base correctly returns `Fri Sep 20 2019`". This is the GT-l1 mechanism exactly: Python sends UTC-midnight ms via convert_datetime_type, and the new offset subtraction (clone/bokehjs/src/lib/models/widgets/date_picker.ts:78-87, called from render() at lines 68, 70, 71) moves it to the previous day west of UTC. It covers all three properties and the initial-render manifestation, and it contrasts this with the local-midnight _on_select toDateString anchor that the PR does fix. Fix: "Do not apply the getTimezoneOffset() compensation to inputs that are already true UTC-midnight epoch timestamps ...; only the client-only round trip through _on_select's date.toDateString() needs it, or compute the compensation so it is a no-op for genuine UTC-midnight inputs." This is the anchor-aware correction the register's required_outcome accepts. It keeps the correction for local-midnight input, so it does not bring back the east-of-UTC bug. Because the correction depends on the input's anchor, a Python-supplied date that comes back after a server round trip is also handled (the #9494 manifestation). I judge it sufficient.

## New candidates

None.
