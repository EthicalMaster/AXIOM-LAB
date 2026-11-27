# AXIOM LAB — Architecture through Phase 05A

## Why this architecture

A local-first **modular monolith** keeps experiments, validation and computation independently testable without premature microservices. React + TypeScript displays typed results; FastAPI validates HTTP requests; pure Python service functions use scientific libraries; SQLite stores dataset/experiment metadata and immutable file references. The frontend never executes arbitrary Python.

```text
Browser (React) --HTTP /api/v1--> FastAPI routes
                                   |
                     source integrity / request validation
                                   |
      +----------------------------+----------------------+
      |                            |                      |
  Scientific services      Dataset bytes             Experiment store
  statistics/math/ML       SHA-256 checked           SQLite + frozen runs
      |
  JSON numbers, warnings, model versions --> React panels
```

## Current boundaries

- **Dataset and analysis:** `api/_dataset.py` verifies 32-character IDs, loads stored metadata and rechecks original bytes against SHA-256. Data processing is currently bounded, often on demand; no source mutation.
- **Inference:** explicit one-sample t-test and Shapiro–Wilk; the user remains responsible for design assumptions. No automatic statistical-method recommendation.
- **Mathematical input:** AST whitelisting for numeric expressions; polynomial coefficient arrays are bounded. No general SymPy string parsing, Python eval or unrestricted shells. These limits are not substitutes for OS-level worker isolation in production.
- **ML:** shared `ml_common.py` restricts numeric predictors and dataset size, creates deterministic 75/25 holdouts and fits imputers/scalers on training data only. Three-fold model comparison puts preprocessing inside *each* training fold. Time-dependent data is rejected for supervised tasks; grouped observations are not supported.
- **Experiment history:** `experiment_store.py` records initial chart runs and provides paginated, read-only lists. This is not a scheduler, permissions system or multi-run comparison engine.

## Alternatives and trade-offs

- **Python/FastAPI vs Node/Express/Spring:** Python directly supports the scientific stack; more concurrent CPU workloads will eventually require separate workers regardless of API framework.
- **SQLite vs PostgreSQL:** SQLite is straightforward for single-user local development; PostgreSQL becomes appropriate for multi-user writes, isolation and operational control.
- **Local immutable artifacts vs object storage:** local paths simplify development; cloud/multi-instance deployment needs shared durable object storage with authorization and lifecycle management.
- **Built-in/Numpy/SciPy/SymPy/sklearn vs custom algorithms:** vetted libraries reduce numerical implementation risk; method assumptions, versions and independent reference examples remain necessary.
- **Synchronous bounded tasks vs queues:** current small computational jobs are simple and testable; production requires actual measured load, bounded worker processes, cancellation and per-user fairness before public hosting.

## Design debt to review before release

The current React page is intentionally incremental and will require feature-level navigation and responsive UX review. Some services reparse datasets for separate reports; profile caching may help after measurement, but introduces invalidation and provenance risks. Scientific runtime metadata is partial (dependency versions, CPU/BLAS information, seeds, environment hashing); production reproducibility needs stronger contracts. No public multi-tenant safety or concurrency claim is made.
