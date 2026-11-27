# Phase 05A — Saved experiment history

Read-only paginated listing of local saved experiments, including dataset reference, run count, creation date and immutable run results. It does **not** yet create multiple executions per experiment; 05B–05D will extend versioning, comparison and reproduction.

## Acceptance

1. Import a simple numeric dataset. Save three chart experiments with different names. Load experiment history and verify three entries and a run per entry.
2. Query `GET /api/v1/experiments?limit=2&offset=0`, followed by `offset=2`: verify distinct pages and total count 3.
3. Click a saved entry and retrieve its run IDs and statuses. Restart FastAPI and confirm history remains available.
4. Verify invalid IDs, invalid pagination, corrupted data references and empty history behave clearly. Check no dataset contents are logged or committed.
5. Run all backend tests, frontend tests, typecheck, build and browser workflow checks for every new panel.
6. Explain why a saved experiment identity differs from a run, why local SQLite does not provide tenant authorization, and what is still required for genuine reproducibility.

## Alternatives

A single table with overwritten experiment results would be simpler but would destroy run provenance. Dedicated `runs` records preserve future extension without a job scheduler. Paginated reads avoid returning unlimited history; a later production system needs authenticated ownership and indexes for multi-user scale.
