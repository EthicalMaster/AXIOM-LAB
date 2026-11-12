# Phase 01A testing evidence — bundle construction

## Backend

- Builder environment: Linux container, Python 3.13; FastAPI and openpyxl installed.
- Command: `PYTHONPATH=backend python -m pytest backend/tests -q`
- Observed: **14 passed** (Phase 00 tests and Phase 01A API/validation/persistence tests).
- Covered: health, OpenAPI, valid CSV, UTF-8 BOM, quoted commas, immutable bytes, SHA-256, SQLite metadata, unique IDs, bad headers, bad row widths, non-UTF-8 content, empty/oversized input, fake Excel files, XLSX multi-sheet/formula warnings, invalid ID, no write on invalid import.

## Not yet verified here

- Positive `.xls` import: `xlrd` could not be installed in the builder's offline environment; user must test with a genuine legacy XLS file.
- Actual Windows filesystem/port behaviour.
- Frontend Vitest/TypeScript/production build: npm dependencies were not available in this build environment; user must run locally.
- Manual browser accessibility and usability checks.

**Do not change this document to claim success for checks that were not executed.** Add separate local verification notes with observed output after running them.
