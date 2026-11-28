# AXIOM LAB — Authentication batch 05–08

Apply after batch 01–04. The GitHub main inspected during packaging was still pre-01–04; the changes below target the previous delivered installer output, plus the observed current repository persistence code. The preflight refuses unexpected source anchors or existing payload paths. This package is a **private beta candidate**, not a public production release.

## What's included
- 05: Google identity/profile in the session toolbar, private `/api/v1/auth/me`, verified UUID admission, remount of the workspace when account changes.
- 06: A verified user UUID selects a private SQLite database and original-file directory. FastAPI binds this identity in a request-scoped ContextVar before any scientific route. No client-supplied user ID controls storage. Existing dataset, experiment, run, reporting and AI evidence routes use the shared persistence root.
- 07: Server-enforced storage access policy, deny missing or unauthorized tenant context, private namespace, refusal of redirected namespace directories, opt-in mode, old cookie-only access denied in multi-user mode, existing process rate limits applied. Auth remains Supabase; scientific data remains SQLite and files. No Supabase Postgres or Storage migration/RLS policy is applied, because those services do not currently hold research data. Never expose the runtime directory through a static file server or grant other users OS access to it.
- 08: Focused middleware/tenant tests and full-app cross-user dataset, history, report and mutation tests.

## Installation
Stop the app processes. From the repository root in PowerShell:

```powershell
python "$env:USERPROFILE\Downloads\axiom-auth-batch-05-08\apply.py" . --check
python "$env:USERPROFILE\Downloads\axiom-auth-batch-05-08\apply.py" .
cd frontend
npm run typecheck
npm run test
npm run build
cd ..
.\.venv\Scripts\python.exe -m pytest backend/tests -q
```

Run commands separately; stop at any failure. No new package installation is required. Existing private `.env` files are untouched. The installer does not commit or push. Do not run it twice. Back up private data before enabling the new mode; keep the backup outside the repo. Existing single-user mode remains the default (`AXIOM_MULTI_USER=0`).

## Enable local private beta only after tests pass
Keep existing `AXIOM_GOOGLE_AUTH=1`, Supabase URL/key, and owner UUID in the root `.env`. Add:

```env
AXIOM_MULTI_USER=1
AXIOM_MULTI_USER_IDS=
```

With a valid `AXIOM_GOOGLE_OWNER_ID`, the owner is admitted by default. Other Google users can verify their identity but cannot access the workspace until an administrator explicitly adds their verified Supabase Authentication user UUID to `AXIOM_MULTI_USER_IDS` (comma-separated). Cross-check the account in Supabase before admitting it. Do not enter emails, tokens or client secrets in this allowlist. Restart backend after changing settings. Use the same frontend origin on each OAuth round trip. For local tests, leave `AXIOM_PUBLIC_MODE=0`. Start backend and frontend as before. Do not deploy publicly yet. In hosted mode existing preflight still requires public mode and a strong configured token; multi-user mode authorizes through verified bearer identity rather than that shared token. Hosted deployment, proxy headers, backups and rate budgets are not validated here.

## Data handling and rollback
Multi-user mode starts a new namespace for EVERY user, including the owner. Example:

```
runtime/axiom.sqlite3                    # legacy single-user store
runtime/datasets/                       # legacy originals
runtime/tenants/<verified-uuid>/axiom.sqlite3
runtime/tenants/<verified-uuid>/datasets/
```

No data is moved, deleted or automatically made visible. Existing legacy datasets will not show in the new workspace. To access legacy research locally, stop the app, set `AXIOM_MULTI_USER=0`, restart and use the previously configured owner mode. New tenant records remain in their private directories. Do not disable Google auth on a remotely exposed app. The old backup utility expects one database root; it does NOT recursively back up tenants. For now, stop all writers and take separate private verified snapshots per tenant and legacy root using the existing backup utility, plus a secure host backup of configuration. Migration of legacy records and a centrally managed multi-tenant backup/restore workflow remain future work. Never manually merge user databases.

## Manual acceptance checks
1. Sign in with owner, import synthetic CSV, create a chart experiment and report; reload, verify session, history, sign out.
2. Sign in with a second Google account, verify denied workspace, then admit its verified UUID in the root `.env`, restart and retry. Use separate browser profiles for concurrent testing. The second user starts empty and cannot fetch the first user's saved IDs. Verify in both directions.
3. Verify invalid/expired tokens and access-code-only calls cannot open protected APIs in multi-user mode. Check API responses for 401/403/404, not raw credentials.
4. Check owner-only mode remains working and legacy records are still present when multi-user mode is disabled. Check tenant records remain separate across restart.

## Security and scale limitations
This is a deliberately small change preserving the scientific engine. Supabase Auth verification still uses the online Auth service; it adds latency. SQLite and per-user directories suit a single persistent host and a small invited beta, not horizontally scaled workloads. The per-user original-data quota is inherited; host-level aggregate disk limits, experiment/run growth limits, per-user rate controls, secure centralized backups and deletion/export workflows remain required. The global rate limiter may let one user consume the beta's capacity. A hostile filesystem administrator is outside the threat model. The browser uses persistent Supabase sessions; enforce CSP and review third-party scripts before deployment. Supabase Postgres RLS and private Storage policies must be implemented and tested if research data is migrated to those services. No live OAuth credentials or project settings were accessed or modified by this update.

## Verification evidence
Six focused tests passed against actual new tenant/middleware modules and Batch 01–04 verifier, with mocked identity and a small ASGI app, including concurrent identities and worker-thread propagation. Full repository checkout could not be cloned in the packaging environment; full-app integration tests, frontend compilation and live OAuth were not executed here. The supplied integration tests exercise the real app after local application. Passing isolated tests alone does not establish public-production security.
