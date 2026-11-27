# Phase 05D — Reproducibility check

An explicit API re-executes **only the stored observation-sequence method** on verified original bytes. It creates a new run with `source_run_id` pointing to the saved run and checks JSON-equivalence of recorded/computed charts.

- API: `POST /api/v1/experiments/{experiment_id}/runs/{run_id}/reproduce`.
- Validation: immutable source SHA-256; known method/version; stored column name.
- Manual: create a run, reproduce it from History; confirm `exact_result_match`, revision increment, and lineage. Corrupt the source and confirm HTTP 409.
- Limits: exact equivalence is defined for this implemented chart method; this is not a general replay engine for all ML/statistical tools. Environment drift and dependency versions are noted, not guaranteed byte-for-byte reproducible across machines.
