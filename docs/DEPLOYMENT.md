# AXIOM LAB — Local release-candidate deployment

This is a **single-user local-first deployment candidate**, not certified public multi-user infrastructure.

## Prerequisites

Docker Engine + Docker Compose v2, internet to fetch images and Python/npm dependencies. Run these commands from the repository root:

```powershell
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps
```

Open **http://127.0.0.1:8080**. Data persists in the `axiom-data` Docker volume. The public port is bound **only to host loopback**. Backend port 8000 is available only to the internal Compose network. Stop with `docker compose down` (no `-v`); `down -v` destroys saved scientific data and must not be used for ordinary shutdown.

## Optional AI

Copy `.env.example` to `.env` and set `AXIOM_AI_BASE_URL`, `AXIOM_AI_MODEL` and `AXIOM_AI_API_KEY`. Never commit `.env`. Remote AI URLs must be HTTPS; no provider is necessary for scientific calculations.

## External publication (not certified)

Only behind an independently configured **HTTPS reverse proxy and network rate limits**. Keep Compose listening on loopback, forward TLS traffic to port 8080, and set:

```text
AXIOM_PUBLIC_MODE=1
AXIOM_ACCESS_TOKEN=<long random token from Python secrets.token_urlsafe(32)>
```

Browser login creates an HttpOnly Secure SameSite=Strict cookie, so HTTP access will not establish a production session. The application is **single-user**: do not give different users this shared token or place sensitive multi-tenant data on the same instance. There is no per-account isolation, audit trail, data deletion policy, background queue or validated high-concurrency deployment.

## Verification before publication

1. `python -m pytest backend/tests -q` and `python -m compileall -q backend/app`.
2. `cd frontend; npm ci; npm run test; npm run typecheck; npm run build`.
3. `python scripts/release_check.py` to validate required local artifacts.
4. Start Compose; verify frontend, dataset import, statistics, ML, histories, reports and optional AI-offline mode end-to-end. In public mode test wrong-token, successful login, logout and CSRF blocking.
5. Run `python scripts/load_smoke.py --requests 30 --concurrency 3` against the **local backend developer server**, not your external website. Docker backend is private and cannot be targeted from host directly without an explicit safe temporary bridge.
6. Inspect PDF output, run keyboard/screen-reader tests and a real vulnerability/dependency audit before exposure.

## Rollback and backup

Take an offline **consistent copy** of the Docker volume (stop writes first). Revert application image tags while preserving the volume; SQLite migrations are forward-only, so test rollback on a copied database first. Do not delete the volume during rollback. Database backups must include original uploaded files and the SQLite DB together.

## Known blockers for broad production

Rate limiting, managed user accounts, database authorization, isolated CPU workers, job queue, concurrency benchmarks, object storage, disaster-recovery validation and automated vulnerability scans remain future engineering work. Do not advertise 1,000-user readiness based on this Compose configuration.
