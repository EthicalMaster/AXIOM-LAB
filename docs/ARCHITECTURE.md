# Architecture — Phase 0 proposal and runnable scaffold

## Decision

Modular monolith with two development processes: React/Vite frontend and Python/FastAPI backend. Neither can perform unbounded scientific code execution. API contracts are versioned from the outset. SQLite metadata and local immutable artifacts are **planned for Phase 01**, not currently implemented.

```text
Browser (React/TypeScript)
  -> /api/v1 HTTP requests (Vite dev proxy)
FastAPI application
  -> API validation / service layer (future)
  -> scientific computation functions (future; independently tested)
  -> experiment and dataset persistence (future)
  -> optional AI interpretation (future; never scientific source of truth)
```

## Implemented now

- `/api/v1/health` returns an explicit Phase 0 contract.
- Frontend shows real API connectivity based on that response.
- Backend test verifies a scientific route is **not** yet available.

## Boundaries to preserve

1. UI cannot execute arbitrary Python or shell commands.
2. Scientific functions must remain independently testable, without requiring a browser or LLM.
3. Dataset originals will be immutable; new cleaning steps create versions.
4. Every future run will reference the precise data version and frozen configuration.
5. Algorithms will return numerical evidence, diagnostics, warnings, and defined error information.
6. Optional LLM explanations can only use compact verified results.
7. No premature worker queues, cloud infra, or GPUs without benchmarked need.

## Runtime considerations

Vite proxies `/api` requests to `127.0.0.1:8000` in local development. This is not a deployment architecture; production reverse proxy and same-origin security rules will be evaluated in Phase 07.
