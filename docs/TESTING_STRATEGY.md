# Test strategy

## Phase 0 actual tests

- Backend `test_health_endpoint_returns_phase_zero`: HTTP 200 and exact health fields.
- Backend `test_unknown_science_route_is_not_implemented`: scientific endpoint returns 404.
- Backend `test_openapi_contract_includes_health`: API docs expose health route.
- Frontend unit tests: phase identifier and 7 planned modules.
- Frontend typecheck and production build.
- Manual end-to-end check: backend running -> UI reports API connected; backend stopped -> API unavailable on refresh.

## Later testing levels

1. Pure scientific unit tests with independently verified numbers.
2. API contract and validation tests.
3. Persistence and execution integration tests.
4. Browser end-to-end workflows.
5. Resource limit, abuse, and error-handling tests.
6. Reproducibility and migration tests.

No benchmark claims or pass counts should be committed until actually measured. Record test date, environment, command, exit code, and observed output in `testing/TEST_LOG.md`.
