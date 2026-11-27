# Cloud deployment (restricted single operator)
The local SQLite mode is unchanged. Do not deploy without passing CI and protected integration tests.
Use separate Vercel projects rooted in frontend and backend. Backend uses FastAPI with Python 3.12.
Supabase transaction pooler on port 6543; use axiom_backend.<project-ref>, not postgres.
Backend environment variables (server-only): AXIOM_STORAGE_MODE=supabase, AXIOM_PUBLIC_MODE=1,
AXIOM_ACCESS_TOKEN (random >=32 chars), AXIOM_PUBLIC_ORIGIN (exact frontend HTTPS origin),
AXIOM_DATABASE_URL (restricted role, TLS verify-full), AXIOM_SUPABASE_URL,
AXIOM_SUPABASE_PUBLISHABLE_KEY, AXIOM_STORAGE_EMAIL, AXIOM_STORAGE_PASSWORD, AXIOM_STORAGE_UID.
Create a dedicated confirmed Supabase Auth user. Configure exact UID storage policies
before enabling uploads. Do not reuse another application account, expose a service role,
or place secrets in Git or frontend variables.
Cloud uploads: 4 MiB; dataset allowance: 100 MiB total and at most 500 originals.
Pending reservations are counted, not automatically reclaimed. An administrator must
inspect pending metadata and object integrity before cleanup; never delete an existing bucket.
Use same-origin frontend API rewrites. Verify session cookies, origin enforcement, login rate
limits, uploads, SHA-256, revision concurrency, restart persistence and reports before production.
Rate limits are fixed-window and shared; the in-flight guard remains process-local.
No existing local data is automatically migrated.

For the hosted pooler, download the official public CA certificate from Supabase Database Settings > SSL Configuration. Set AXIOM_SUPABASE_CA_PEM to the complete PEM (including BEGIN/END CERTIFICATE). The backend uses verify-full with that CA; absent the variable, it uses system roots. Never disable hostname or certificate verification.
