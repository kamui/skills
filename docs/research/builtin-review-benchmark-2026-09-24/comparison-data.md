# Comparison data — built-in reviewer benchmark

No scored cell has run. The Phase 0 adapter fixtures that this file used to tabulate are filed as
the suite run [`bench/runs/2026-09-24-toy`](../../../bench/runs/2026-09-24-toy/README.md): one
`attempt.json` per attempt with its disposition, observed configuration, metered cost and archived
transcripts, and a rubric v1 mapping. Scored rows for this benchmark will be computed by
`score.py` into the run's `results.v<M>.json`, not pasted here.

One figure changed in the move. The Opus built-in's fixture (att-004, formerly C2) is priced at the
recorded Opus 5.5 cache-read rate of `$0.20` per million tokens, `$0.059`; the table this file held
had used the meter's default one-tenth ratio and shown `$0.07`.
