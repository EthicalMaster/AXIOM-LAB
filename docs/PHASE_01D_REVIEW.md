# Phase 01D acceptance — chart + saved experiment

1. Upload CSV with numerical column `reading` (e.g. rows 10, 15, 20). Select it, name experiment and click **Compute & save run**.
2. Confirm chart shows exactly three source points, no synthetic values; x-axis is valid observation index, **not time**.
3. Check two opaque IDs: experiment ID and run ID. Click **Reload saved run from storage** and confirm same chart and IDs.
4. Restart backend and verify saved record via `GET /api/v1/experiments/{id}` (Swagger /docs) or Reload if UI still holds ID.
5. Numeric identifiers with leading zeros must not appear as numeric chart columns.
6. Check missing values and >250-row data. Chart must label subsampling and retain endpoints.
7. Run backend suite, frontend test/typecheck/build. Ensure neither original uploads nor `runtime/` are staged in Git.
8. Learning: why is a chart insufficient for reproducibility? What is the difference between experiment and run? What is the meaning of a sampled view?

**Limitation:** this is a single-user local experiment record and one chart method, not a full experimentation scheduler or 3D visualization studio.
