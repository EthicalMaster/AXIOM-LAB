# AXIOM LAB · Cloud persistence candidate (bundles 09–12)

## Scope and decisions

- 09: opt-in cloud adapter uses PostgreSQL through Supabase PostgREST; existing SQLite store remains default. Experiments and runs have composite tenant foreign keys and transactional creation/revision allocation.
- 10: private `axiom-originals` bucket; verified owner UUID prefix, immutable object writes, read-back SHA-256 verification, no browser access. Metadata is reserved first, and only marked ready after object verification. Pending reservations count toward quotas and require manual reconciliation; there is no automatic retry or deletion.
- 11: atomic per-user and global original-byte quotas, per-user dataset cap, experiment and run caps, plus process-local per-user request limits. Global original quota is not a complete database/Storage billing cap. Auth verification still goes through Supabase per request. This is not a distributed limiter or measured scalability improvement.
- 12: offline cloud export to a new verified SQLite snapshot, dry-run local snapshot inspection, explicit import to an empty admitted cloud workspace with IDs, original hashes and run lineage preserved. No deletion or automatic data migration. Stop all writers first, use a private/encrypted backup location and verify a separate restore.

The API uses a server-only `sb_secret_` key (which bypasses RLS), not browser tokens for data operations. Consequently every cloud request is scoped by the server-verified tenant and every Storage object path is derived from that identity. SQL RLS plus revoked direct grants protect against browser access. Do not grant authenticated access to these tables or bucket; doing so would bypass the application quota and immutable-record rules. A compromised server key can access the project: restrict access, rotate it if exposed, never use a `VITE_` prefix. SQL is provided for review and manual execution, not applied by the installer.

## Install and test locally

1. Stop frontend/backend, commit previous work, then from repository root run the extracted `apply.py . --check` followed by `apply.py .`. Installer validates source anchors/AST and never writes `.env`, SQLite or runtime files. Keep `AXIOM_CLOUD_STORAGE=0` (default) while running all backend and frontend tests. No new dependencies.
2. In the dedicated AXIOM LAB Supabase project, open SQL Editor and review/run `supabase/axiom_cloud_setup.sql`. Verify that all three tables have RLS, only service_role has CRUD grants, and that `axiom-originals` is private, with a 5 MiB maximum and the restrictive browser-denial policy. Run database security advisors. Do not run this in portfolio projects.
3. Under Settings → API Keys create a backend secret key. Enter only in root `.env` (not frontend):

```env
AXIOM_CLOUD_STORAGE=0
SUPABASE_SECRET_KEY=your_server_only_key
AXIOM_CLOUD_GLOBAL_MIB=512
AXIOM_USER_INFLIGHT=2
AXIOM_USER_RPM=60
```

Keep previous `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `AXIOM_GOOGLE_AUTH=1`, `AXIOM_MULTI_USER=1` and the admitted UUIDs. Keep the server access-token setting if required by existing hosted preflight. A user request with cloud enabled but no managed multi-user configuration fails closed.
4. Verify both real Google accounts in local mode before switching. Then use an empty cloud test workspace, set `AXIOM_CLOUD_STORAGE=1`, restart backend, and test new CSV import, profiling, statistics, saved experiments, compare/reproduce, report download, AI offline evidence, logout/login, and cross-user rejection. Check cloud table records and private Storage. Check direct browser-token reads/writes fail. Return to cloud disabled if anything fails. Do not run the normal local regression suite with cloud env injected into the test process.

## Transfer and recovery (optional, never automatic)

Use the existing `scripts/storage_backup.py` to snapshot a local tenant directory `runtime/tenants/<verified UUID>` (or configured data root). Stop all writers and use a new destination. For legacy data use the separately verified legacy snapshot only if the administrator explicitly assigns it to the chosen owner. This batch never assigns legacy records silently.

From the repo root with the venv installed:

```powershell
.\.venv\Scripts\python.exe scripts/axiom_cloud_transfer.py backups/tenant-snapshot --owner YOUR_UUID --writers-stopped
```

This checks SQLite integrity, FK relationships, IDs, file sizes/hashes and run lineage without uploading anything. To actually copy data, ensure the target cloud workspace is empty, SQL/keys are configured, quotas are sufficient and all writers are stopped. Add `--apply` to that command. Do not run it during a live application session. If interrupted, do not blindly retry: review the cloud workspace, pending rows and objects; source remains intact. The importer checks every transferred record and original. A complete backup of the whole project requires separate backups for every admitted tenant and Supabase database/Auth configuration backups; these scripts do not export Auth identities.

To export a cloud workspace into a new local snapshot (stop writers):

```powershell
.\.venv\Scripts\python.exe scripts/axiom_cloud_backup.py backups/cloud-snapshot-01 --owner YOUR_UUID --writers-stopped
```

Verify the resulting snapshot using the transfer dry-run. Restore into an empty cloud workspace only with explicit owner selection, or use existing local restore procedure into a new directory. The backup is not encrypted by this script; protect it with host permissions, encryption and retention policies. Keep offsite copies if appropriate. Existing data is never removed by these scripts.

## Verification status and remaining gates

Eight focused Python tests pass in an isolated harness using the previous actual tenant module and test doubles for existing request settings/storage exception classes. Python syntax compile passed. Full repo, SQL execution, live Storage REST, deployment and full migration round-trip tests remain unverified here. The SQL and integration scripts must be tested in the actual dedicated project before production. Keep beta admission restricted. Pending upload reconciliation and distributed per-user limits, connection pooling, application monitoring and load tests are follow-up work. No claim of production readiness or thousands-user capacity.
