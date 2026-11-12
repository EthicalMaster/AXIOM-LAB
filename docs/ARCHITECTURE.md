# Architecture — Phase 01B implementation candidate

## Decision

AXIOM LAB is a local-first modular monolith with React/Vite frontend and Python/FastAPI backend. Versioned API routes call independently testable services. SQLite is used for dataset **metadata**; uploaded original bytes live in `runtime/datasets`. Scientific computation and LLM interpretation are **not** implemented in this milestone.

```text
Browser (React + TypeScript)
    -> /api/v1/datasets/import  [multipart file]
Vite proxy -> FastAPI dataset API (api/datasets.py)
    -> validation service (services/dataset_validation.py)
    -> immutable byte storage + SQLite metadata (persistence/dataset_store.py)
    -> HTTP 201 structured metadata + bounded preview
Browser renders raw preview, warning messages and source fingerprint.

GET /api/v1/datasets/{id} -> stored metadata (no raw-file download).
```

## Implemented in 01A

- `GET /api/v1/health`: operational status; current phase label is 01B, numerical scientific engine explicitly not implemented.
- `POST /api/v1/datasets/import`: validated format, encoding, rows and columns, bounded upload, original file saved, record created, preview returned.
- `GET /api/v1/datasets/{id}`: read back persisted dataset metadata using opaque random ID.
- React UI: file selection, upload, status, result preview, warnings and error handling.
- Backend unit/integration tests; frontend tests require verification on the developer machine.

## Architectural boundary: validation vs computation

Dataset validation is not data analysis. Phase 01B will add type inference and profiling. Phase 01C will calculate reference-tested descriptive statistics. Phase 01D will add charting and minimal experiment/run records. Later phases will add inference and ML with explicit method assumptions.

## Boundaries to preserve

1. The UI does not execute arbitrary Python or shell commands.
2. Computational functions remain independent of API/React and must be reference-tested.
3. Uploaded originals are immutable; derived datasets must get separate versions.
4. A future experiment run will reference a precise dataset version and frozen configuration.
5. Numerical results will include evidence, assumptions and diagnostic warnings.
6. AI is optional and cannot invent scientific outputs.
7. Do not introduce unneeded queues, cloud infrastructure or GPU dependencies.

## Runtime considerations

Developer selected port **8898** after Windows denied binding to 8000. The Vite proxy points to the backend's actual local port in the developer's working configuration and is intentionally **not modified** by Bundle 01A. This is local-only architecture; public deployment needs authentication, resource isolation and a production reverse proxy.

## Phase 01B — column inspection boundary

`GET /api/v1/datasets/{id}/profile` resolves persisted dataset metadata, reads the original file from an opaque ID-derived path, verifies size and SHA-256, and performs **on-demand** structural profiling. This operation never modifies the dataset or stored metadata.

`services/column_profiling.py` is independent of FastAPI routing. It uses the Phase 01A validator as an initial bound-check and reparses the immutable file in a second pass. For the current 5 MiB limit this is a deliberate simplicity/correctness trade-off. Reassess the two-pass cost before raising limits.

Column types are conservative hints only (`numeric`, `boolean`, `datetime`, `categorical`, `mixed`, `empty`); mixed or identifier-like values are never coerced. Distinct values are tracked up to 1,000 examples per column to bound memory, with the API explicitly marking lower bounds.

Multi-tenant deployment requires authorization on dataset IDs, per-user storage isolation, request limits and asynchronous job handling; none of those claims are made for Phase 01B.
