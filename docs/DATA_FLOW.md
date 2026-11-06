# Data flow — implementation status

## Actual Phase 0 flow

```text
Browser loads React UI
  -> GET /api/v1/health (through Vite proxy)
  -> FastAPI responds with explicit Phase 0 state
  -> React shows connected / unavailable
```

## Planned Phase 01 scientific flow (NOT implemented)

```text
Upload -> Validate -> Store immutable dataset version
       -> Profile -> Configure scientific method
       -> Execute reference-tested algorithm
       -> Save frozen run and results
       -> Render chart -> Inspect diagnostics
```

Raw user data must not be silently altered, passed unnecessarily to AI, or dumped into runtime logs.
