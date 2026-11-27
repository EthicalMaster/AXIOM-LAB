# Phase 05C — Run comparisons

Comparison is **only numerical when columns, methods, observation count, and x-positions match**. The endpoint reports differences in the stored chart observations, not claims about statistical significance. For sampled charts, it explicitly limits interpretation to selected points.

- API: `GET /api/v1/experiments/{id}/compare?left=<run>&right=<run>`.
- Browser: save two runs; use History → Compare two latest runs; verify identical reruns yield zero difference. Switch column for the next run and verify the API withholds numeric comparison.
- Security: run IDs must belong to the same experiment; invalid IDs give 404. No data leaves the service.
- Limit: broader scientific methods have not yet been adapted to this comparison contract.
