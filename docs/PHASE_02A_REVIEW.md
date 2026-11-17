# Phase 02A acceptance review — dataset quality

1. Upload `examples/datasets/quality_reference.csv`; verify missing cells, percent completeness and duplicate full-row count.
2. Repeated rows are **not** deleted, because repeated measurements may be valid.
3. A blank/whitespace-only cell counts as missing; a literal `NA` is text, not missing.
4. Duplicate comparisons use exact lexical values, preserving differences in whitespace and leading zeros; count is a lower bound after 10,000 distinct rows.
5. Verify `GET /api/v1/datasets/{id}/quality` and the UI audit (completeness, missingness bars, warnings).
6. Run all backend tests and frontend test/typecheck/build; verify pre-existing upload, statistics and saved experiments still work.
7. Explain: completeness vs scientific usefulness; why duplicates shouldn't be removed automatically; why a bounded count may be approximate.

No cleaning or imputing is implemented; no significance inference is claimed.
