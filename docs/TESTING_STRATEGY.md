# Test strategy — Phase 01A

## Executed builder tests

See `docs/testing/PHASE_01A_TEST_EVIDENCE.md` for actual test output and limitations. Backend includes 14 tests covering health, OpenAPI, CSV parsing, XLSX validation, data retention, metadata lookup, invalid formats, size bounds, and malformed files.

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
