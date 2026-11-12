# Phase 01B — Human review and acceptance gate

## Objectives

- Inspect all columns of an already imported CSV/XLSX/XLS dataset, not just the 8 preview rows.
- Show conservative type hints: numeric, categorical, boolean, datetime, mixed, empty.
- Show nonmissing/missing counts, bounded distinct counts and short examples.
- Preserve raw originals, warn about mixed values and leading-zero identifiers.

## Local automated tests

From `axiom-lab/` in Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -q
.\.venv\Scripts\python.exe -m compileall -q backend/app
cd frontend
npm run test
npm run typecheck
npm run build
```

Expected builder baseline: **26 backend tests passed**, frontend test/build/typecheck commands must exit successfully on the developer laptop.

## Browser acceptance

1. Keep FastAPI on port **8898** and Vite on **5173**. Confirm API connected.
2. Upload `examples/datasets/column_profile_demo.csv` (or recreate it if not included). Expected **4 rows, 5 columns**.
3. Profile: `sample` categorical; `temperature` numeric with 1 missing; `code` categorical with leading-zero warning; `condition` categorical with a missing value; `test_date` datetime.
4. Confirm that raw preview still shows original values and that the server did not rewrite the uploaded file.
5. Upload file with mixed values `x\n10\nNA\n20\n` (use actual newlines). It should display `mixed` with no missing observations.
6. Try a genuine XLSX with two worksheets. Only the first sheet is profiled; formula cells are not executed.
7. Check responsive table scrolling, keyboard focus and visibility of all warnings.
8. Restart backend and request `/api/v1/datasets/<dataset-id>/profile`. It should still work for the previously imported ID.
9. Inspect `git status --short` before committing. Uploaded datasets, SQLite, `.venv` and `node_modules` must not appear.

## Learning review

Read `docs/learning/concepts/COLUMN_PROFILING.md` and answer the six questions. If anything is unclear, report it before the commit.

**Not in scope:** means, medians, standard deviations, inferential tests, charts, experiment records. These arrive in later bundles.
