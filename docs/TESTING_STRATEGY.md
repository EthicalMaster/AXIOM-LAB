# Test strategy — Phase 01B

## Executed builder tests

See both `docs/testing/PHASE_01A_TEST_EVIDENCE.md` and `docs/testing/PHASE_01B_TEST_EVIDENCE.md` for tested evidence and limitations. Phase 01A backend included 14 tests; Phase 01B includes 12 additional backend tests, giving 26 in the builder environment covering health, OpenAPI, CSV parsing, XLSX validation, data retention, metadata lookup, invalid formats, size bounds, and malformed files.

## Required local tests before acceptance

- Backend `pytest` and `compileall` using the local venv.
- Frontend `npm run test`, `npm run typecheck`, and `npm run build`.
- Browser manual import of valid UTF-8 CSV, XLSX and genuine legacy XLS.
- Metadata lookup after restarting server; file integrity/fingerprint verification.
- Invalid-input attempts, backend downtime, keyboard navigation and responsive preview.
- Check Git ignore rules to ensure uploaded data and SQLite files are never staged.

## Later testing levels

1. Scientific unit tests against independent reference numbers.
2. API contract and validation tests.
3. Persistence/execution integration tests and migrations.
4. Browser end-to-end workflow automation.
5. Resource limit, abuse and failure-mode testing.
6. Reproducibility and experiment versioning checks.

No pass count is a claim of local Windows success until the developer runs and records it.

## Phase 01B acceptance tests

- Numeric, categorical, boolean, ISO date, mixed and empty column types.
- Blank-cell policy vs literal `NA`, `nan`, `inf` and leading-zero identifiers.
- Distinct count cap and explicit lower-bound indicator.
- XLSX first-worksheet restriction and formula non-execution.
- Stored-file integrity mismatch returns a clear error without modifying source.
- Existing Phase 01A import and health tests still pass.
- Frontend tests, TypeScript build and manual UI checks on the owner's Windows environment remain required.
