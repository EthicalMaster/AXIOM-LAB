# Post-roadmap release upgrade — acceptance gates

**Scope:** local-first, protected single-user research workspace. No public deployment or independent penetration test has been performed. Do not expose private datasets to separate users on a shared-token instance.

## Implemented controls

| Control | Default | Scope |
|---|---:|---|
| General API budget | 120 requests/min | Process-wide in public mode |
| Login | 12 requests/min | Process-wide in public mode |
| Import | 6 requests/min | Process-wide in public mode |
| Math / ML | 30 requests/min | Process-wide in public mode |
| Guide / AI POST | 20 requests/min | Process-wide in public mode |
| Provider requests | 10/min and 100/24h | Process-wide; local spending guard, not provider quota |
| Provider concurrency | 2 | Nonblocking admission |
| Active scientific HTTP requests | 4 | Per process, all modes; health and auth status excluded |
| Uploaded original | 5 MiB | Existing scientific validator |
| Request body | 6 MiB import; 64 KiB other mutations | Streaming byte cap, 15-second receive deadline |
| Dataset allowance | 256 MiB / 500 originals | Atomic SQLite recorded-data quota; not total filesystem quota |
| Browser request | 30-second wait for response headers | Cancellation does not promise server computation stops |

Configure limits using `.env.example`; restart to change window budgets. With Docker Compose, environment variables are passed through. For a native PowerShell dev server use `$env:NAME='value'` before starting Uvicorn; the app does not automatically read `.env` in that workflow. Exceeding budgets returns HTTP 429 with Retry-After; admission saturation returns 503; oversized input 413; dataset quota 507. These controls are global, not per-user or per-IP. Reboots reset the in-memory request budgets. They cannot prevent all abuse and a hostile client can consume the shared budget. Do not trust client-supplied forwarded IP headers. Place an edge rate limiter ahead of the service and restrict direct backend access. Use shared Redis/managed distributed rate limiting, genuine account identities and authorization before accepting multiple independent users.

## Contextual guide privacy

Built-in guidance is the default and requires no network provider. Optional provider requests send the question and limited, server-derived evidence only when explicitly requested. Do not include private information in the question; even aggregate statistics may be sensitive. Outputs are advisory, not scientific computations. The local request cap is separate from any hosted plan quota; verify provider availability and terms for your own account. No API key is exposed to the browser. A provider outage leaves local guidance available.

## Deployment architecture

Vercel serves the Vite static build; FastAPI runs on a persistent compute service. Keep `/api/v1/...` same-origin by configuring an HTTPS reverse proxy/rewrite to the actual backend origin. The sample `deploy/vercel.example.json` is a template only: set frontend as root directory and copy it as `frontend/vercel.json` only after replacing the placeholder with a trusted HTTPS backend URL. Confirm deployed upload limits with the actual proxy, cookie forwarding, HTTPS and POST requests before enabling access. Set `AXIOM_PUBLIC_MODE=1`, a strong unique `AXIOM_ACCESS_TOKEN`, and `AXIOM_PUBLIC_ORIGIN` equal to the exact browser origin, e.g. `https://your-frontend.example`. No provider secret in Vite variables. Public mode is for a restricted single-user preview only. Local Vite on 8898 is unchanged. Persistent volumes, filesystem quotas, secrets, TLS and backup policies must be set on the real host. Do not move SQLite or original uploads into ephemeral serverless storage.

## Verification and release gates

- Run all backend tests, frontend tests/typecheck/build, and local Compose build/start. Confirm one clean import and all mathematical, statistics, ML and experiment workflows; check chart values and reduced motion/keyboard access. No fabricated data should appear as evidence. Verify mobile layout and chart scale/labels. No generic raw JSON is required to use the primary result view; advanced details retain exact values.
- `python scripts/capacity_probe.py` uses an isolated temporary directory, in-process ASGI transport, synthetic data (400 rows) and a fixed mixed statistics/regression workload. It measures response status and p50/p95 of successful requests at concurrency 1/2/4/8. No public traffic or real data. Use results to check overload behavior only, not user capacity.
- Before a real launch, test the deployed staging environment with an approved bounded workload representative of actual users: latency percentiles, errors and throttles, memory/CPU, disk growth, cold starts, backups/restores, provider usage, and latency during simultaneous computations. Calculate capacity from observed demand per user rather than treating request concurrency as user count. Set a budget, monitoring and alerts, plus rollback criteria.
- Defensive testing: authorization, cross-origin rejection, input validation, upload size limits, error redaction, quota expiry, concurrent admission, provider failure, dependency audit (`npm audit`, a Python dependency scanner in CI), configuration and secret scanning. Independent security review, live HTTPS verification, external edge protection, session revocation, retention/deletion, accessibility review, and a multi-tenant threat model remain release gates. No unrestricted penetration testing against third-party systems.
- Remaining for broad production: distributed quota/rate state, tenant-scoped identity/storage, worker isolation and cancellation/job queue, observability dashboards, persistent database/object storage as appropriate, resilient backups, disaster recovery, privacy review, and cost controls. The in-process safeguards do not implement these.
