# Candidate CSV schema

Use the current session's 42-column CSV layout, generalized to the user's area, timezone and selected hospitals. When continuing an existing CSV, preserve its established labels/order and adapt only what the new request requires. Hospital 1 and Hospital 2 are stable source slots: identify their actual names in Source list and in Notes. Do not swap slots midway through a search.

## Default column order

1. Ranking
2. Doctor
3. Degree
4. Years of experience (approx.; since professional degree)
5. Source list
6. First-pass screening status
7. Earliest appointment after 12pm (LOCAL_TIMEZONE)
8. Afternoon availability status
9. Earliest online appointment any time (LOCAL_TIMEZONE)
10. Location
11. Area subdivision
12. Insurance plan checked
13. Network status
14. Zocdoc rating
15. Zocdoc review count
16. Google rating
17. Google review count
18. Healthgrades rating
19. Healthgrades rating count
20. WebMD rating
21. WebMD rating count
22. Zocdoc link
23. Google review or search link
24. Healthgrades link
25. WebMD link
26. Hospital 1 profile link
27. Appointment source link
28. Zocdoc review status
29. Google review status
30. Healthgrades review status
31. WebMD review status
32. Checked date
33. Search cutoff
34. Hospital 2 profile link
35. Hospital 2 patient rating
36. Hospital 2 rating count
37. Patient eligibility screening
38. Office phone
39. Vitals rating
40. Vitals review count
41. Vitals URL
42. Notes

Replace LOCAL_TIMEZONE with a real timezone identifier, such as America/New_York. If the user chooses another preferred time, adapt columns 7 and 8 to it. The original session used MD graduation, Borough, Five-week cutoff, NYU profile link and HSS profile/rating/count: these become professional degree, Area subdivision, Search cutoff and the corresponding hospital slots. Preserve original headers when updating that original file.

If Hospital 1 publishes patient ratings, insert **Hospital 1 patient rating** and **Hospital 1 rating count** before Notes. For another source actually used, insert **SOURCE rating**, **SOURCE rating count**, **SOURCE link** before Notes. Preserve one Notes column at the end. Vitals columns are retained from the original format; empty values mean not collected/unknown unless Notes says a verified profile has no ratings. Do not populate other doctors with ratings taken from suggested-doctor widgets.

## Field semantics

- Ranking: consecutive positive integers for active candidates; N/A for excluded audited candidates. It represents review confidence, not medical effectiveness.
- Source list: Zocdoc and/or the actual selected hospital names. Combine multiple discovery sources on one row.
- First-pass screening status: Include, Conditional or Exclude. Deeper-review decisions belong in Notes; retain original practical screening when ranking reviews alone.
- Appointment timestamps: YYYY-MM-DD HH:mm in the header's timezone. Date-only evidence uses YYYY-MM-DD and Notes explicitly says the time is unknown. No guessed time or appointment.
- After-noon status: Confirmed, Unknown/phone scheduling, No eligible slot found, or Confirmed outside horizon. Distinguish what was observed from a proven absence of availability.
- Location: eligible office address(es), with separate location/time pairs in Notes when there are several. Area subdivision may be a borough, neighborhood, city or district.
- Insurance plan checked: exact user plan and matched listed plan when different. This required field must contain the user plan or an explicit Self-pay/uninsured instruction.
- Network status: Confirmed in-network; Similar plan / exact network unverified; Carrier only / exact network unverified; Unknown; Confirmed out-of-network; or Not applicable; self-pay/uninsured. Explain evidence/scope in Notes.
- Ratings: numeric values on their published scale. These platforms normally use /5; label any different scale in its header/Notes.
- Rating/review counts: published total counts, not a guessed number of written reviews. Notes separately gives actual comments read. Use 0 only for a verified empty profile; absent/unknown data is blank.
- Source/profile links: direct physician/review/booking URL when verified; search link only when no direct match exists, explicitly labeled as a search/unverified match in status or Notes.
- Review statuses: Rated; Profile found; no ratings/reviews; Matching profile not found; Not checked; or Access limited / cached evidence. Missing Zocdoc data for a hospital candidate is not itself disqualifying.
- Checked date and Search cutoff: YYYY-MM-DD. Checked date belongs to the evidence collection, not file-save date; document fresh checks in Notes rather than silently dating old facts as new.
- Experience: numeric approximate years, with degree year, source URL and consistent definition in Notes. Missing is blank; avoid mixing years since graduation with years after fellowship.
- Patient eligibility: short evidence statement, such as Adult specialist; no obvious women-only restriction, Pediatric-only; excluded for adult search, or Eligibility unverified.
- Notes: include pass status, decision, medical positives/concerns, uncertainty, actual written-review coverage, evidence dates/direct links for otherwise unsourced claims, hospital-selection source URLs, and practical constraints. Use concise paraphrases; stay within source quotation and attribution limits.

## File integrity

Use UTF-8 CSV (BOM allowed for Excel), comma delimiters, valid quoting of commas/newlines/quotes and empty fields for unknowns. Do not put formulas or Markdown into numeric fields. Do not truncate doctor names, addresses, review explanations or URLs for display. Keep one row per real physician and one final candidate CSV. Backups and evidence belong outside outputs/.

Before delivery, parse the CSV, compare its headers with the chosen schema, check unique doctor identities and ranks, and confirm Notes is last. On updates compare untouched fields against the prior file. A brief preview can verify leading columns; the saved CSV remains the authoritative deliverable.
