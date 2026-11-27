# Phase 07B — Performance evidence and bounded load smoke

- Added SQLite indexes for newest experiments and per-experiment runs, without changing the append-only data contract.
- All API responses include timing metadata (`Server-Timing: app;dur=...`) and `Cache-Control: no-store` to avoid shared caching of scientific data.
- `python scripts/load_smoke.py --requests 30 --concurrency 3` exercises **only** the local health endpoint, with strict limits (max 80 requests, max 5 workers). It measures observed median and p95 latency, and fails if requests fail.
- CI tests verify timing header and index creation. For meaningful capacity claims, benchmark actual uploads, scientific computations and concurrent sessions on production-like hardware; this bundle does **not** verify 1,000-user concurrency.
- Further risks: SQLite contention, CPU-bound numerical jobs in the request process, filesystem storage and one-host runtime. Address with workers, queues, object storage and multi-user data isolation before public scale.
