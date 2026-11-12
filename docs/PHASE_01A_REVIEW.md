# Phase 01A — Dataset Import and Validation: acceptance + learning

**Status:** implementation candidate. Do not mark complete until these steps pass on the developer's machine.

## Purpose and limits

This phase implements secure-bounded **structure validation**, a first 8-row **text preview**, and **immutable raw-file preservation** for UTF-8 CSV, XLSX and legacy XLS files. It does **not** perform type inference, statistics, cleaning, charting, or experiments. The original bytes are saved under an opaque dataset ID and can be referenced via metadata lookup.

## Install and run (Windows PowerShell)

From the project root, after the patch is applied:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
.\.venv\Scripts\python.exe -m pytest backend/tests -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8898
```

Keep the successful port 8898 and your existing `frontend/vite.config.ts` proxy mapping. From a **second terminal**:

```powershell
cd frontend
npm run test
npm run typecheck
npm run build
npm run dev
```

Open `http://127.0.0.1:5173`. If your port differs, point your existing Vite proxy to the port where FastAPI actually runs.

## Automated acceptance

- [ ] All backend tests pass (Phase 00 plus new Phase 01A tests).
- [ ] Frontend unit tests, typecheck, and build pass.
- [ ] GET `http://127.0.0.1:8898/api/v1/health` returns `phase: "01A"` and `scientific_engine: "not_implemented"`.
- [ ] GET `http://127.0.0.1:8898/docs` shows `POST /api/v1/datasets/import` and `GET /api/v1/datasets/{dataset_id}`.
- [ ] `.venv`, `runtime/`, `node_modules`, dataset uploads, and SQLite file are not staged for commit.

## Manual functional checks

Create a file called `measurements.csv` (using VS Code, save as UTF-8):

```csv
sample,temperature
A,22.5
B,24.0
C,23.5
```

- [ ] In the Data Lab, choose `measurements.csv` and click **Validate and import**.
- [ ] See `3` rows, `2` columns, `CSV`, and headers `sample` / `temperature`.
- [ ] See the three original data rows in the preview; no analysis is claimed.
- [ ] Record the dataset ID and SHA-256 fingerprint. Re-select the same file: its ID changes but SHA-256 stays the same.
- [ ] Open `http://127.0.0.1:8898/api/v1/datasets/YOUR_DATASET_ID` replacing the placeholder. See saved metadata (without preview).
- [ ] Restart FastAPI, repeat metadata lookup, confirm it still exists.
- [ ] Inspect `runtime/datasets/<dataset_id>/original.csv` on disk; it must match the original file exactly.
- [ ] Make an XLSX file with two columns and two data rows, import successfully. For a multiple-sheet workbook, only the first sheet is read and a warning is shown.
- [ ] If you have Excel, save a sample as `Excel 97-2003 Workbook (*.xls)`, import it and confirm the header and row count. This is an important local check because a successful XLS upload was not independently verified in the bundle-building environment.
- [ ] Try `.txt`, empty CSV, duplicate column names (`a,A`), inconsistent CSV rows, and a file larger than 5 MiB. Observe descriptive failure messages and no persisted dataset for the invalid file.
- [ ] Unplug/stop backend then attempt import: frontend must show an error, never a fabricated success.
- [ ] Resize to mobile width, use keyboard Tab/Enter to select and import; verify the preview remains scrollable.

## Important constraints

- File limit: **5 MiB**. Up to **50,000 data rows** and **150 columns**. CSV encoding: **UTF-8**. CSV separator: comma. The full original file is preserved; preview is limited to 8 data rows and clipped cell text.
- XLSX archive entries and uncompressed size are capped before parsing. This mitigates but does not fully sandbox malicious workbooks.
- The **first worksheet only** is parsed. No formulas are executed. For XLSX, formula-like cells are displayed as their literal expression in the preview, never evaluated. XLS values reflect the parser's raw cell values, not inferred scientific types.
- Data lives in `runtime/` and must **never be committed to GitHub**. The application is designed for **single-user local use**, not publicly exposed web upload endpoints.
- `POST /api/v1/datasets/import` returns HTTP 201 with a dataset ID, raw SHA-256 fingerprint and inspection summary. The GET endpoint returns metadata only. These are not run/experiment records yet.

## Explain these concepts in your own words

1. Why must the backend validate input even if React already checks the extension and size?
2. What is the difference between a file's original bytes and the preview rows displayed by React?
3. What does SHA-256 help us verify? Is it an encryption system?
4. Why does AXIOM LAB generate a random dataset ID instead of using the uploaded filename as a storage path?
5. Why does the dataset import have a dedicated validation layer, API route, and persistence layer?
6. Why can a dataset be structurally valid but still scientifically unsuitable for a statistical method?
7. What are three limitations of this implementation that Phase 01B should address?

## Failure report

```text
AXIOM LAB — BUNDLE 01A
Original Git commit (git rev-parse HEAD):
Patch check: PASS / FAIL
Backend installation: PASS / FAIL
Backend test result:
Frontend test/typecheck/build result:
CSV/XLSX/XLS manual import:
Command and expected behaviour:
Actual behaviour and complete error:
New files shown by git status:
Topics I need help understanding:
```

**If any required check fails, stop. Do not commit, push or attempt the next bundle until the cause is understood.**
