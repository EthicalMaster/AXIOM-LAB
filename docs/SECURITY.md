# Security — Through Phase 07D local release candidate

## Current safeguards

- Allowlist `.csv`, `.xlsx`, `.xls` and file-size limit of 5 MiB.
- UTF-8 CSV parsing only, with duplicate/empty header rejection and rectangular row checks.
- Max 50,000 data rows, 150 columns; XLSX archive entries/uncompressed-size capped.
- Uploaded original filename sanitized for metadata; file storage is an opaque dataset-ID path, written exclusively.
- No formula execution, Python eval, arbitrary shell commands, or user-provided output paths.
- Error responses are structured and do not include full file content or filesystem paths.
- Runtime artifacts and database are under Git-ignored `runtime/`, not committed to GitHub.

## Remaining risks and limitations

- This is **not** a hosted public upload service: no authentication, per-user quota, rate limiting, malware scanning, or OS-level parser isolation.
- Request-body/multipart parsing occurs before the endpoint's size check; public deployment must also enforce reverse-proxy request-size bounds.
- XLSX archive limits reduce risk from decompression bombs but are not a complete protection against malicious workbooks.
- CSV preview values beginning `=` are displayed as text in React; future CSV/Excel exports must mitigate spreadsheet formula injection.
- Uploads are currently stored locally; backups, retention, encryption-at-rest and secure deletion policies are future decisions.
- Mathematical expression parsing and expensive computation will need separate safe execution controls when developed.

Never expose the backend beyond loopback or deploy publicly without an explicit security review.

## Phase 01B storage integrity and output limits

Column inspection reads a server-constructed path using a validated opaque dataset ID, verifies its size and SHA-256 against SQLite metadata, and refuses to profile a changed or missing original (HTTP 409). The endpoint returns small per-column examples (up to three truncated values), not full datasets. Exact distinct-value tracking stops at 1,000 entries per column. Real multi-user service **requires authorization for dataset IDs** and rate/CPU limits before deployment; random IDs are not authorization.

## Phase 02C–05A security and resource review

- `services/safe_math.py` accepts only whitelisted AST operators and math functions, with expression/depth/numeric magnitude bounds; arbitrary Python, attributes, imports and shells are forbidden. **This is not OS sandboxing**; users must not have untrusted unlimited access to synchronous compute endpoints.
- Polynomial degrees (≤6), square matrices (≤8), numerical intervals (−100..100), ML rows (≤2,000), features (≤8), clusters (2–8) and 3-fold CV constrain local workload. These caps do not guarantee concurrency safety or eliminate all denial-of-service paths.
- No user accounts or authorization checks protect imported dataset, model result or experiment IDs. Opaque random IDs are **not access control**. Do not deploy on a publicly accessible server until authorization, rate limiting, job isolation, storage policy and operational load testing are implemented.
- Model training and CV currently execute synchronously; under public load use dedicated CPU-limited worker processes with cancellation and request quotas.
- Treat Excel and CSV as untrusted. Actual reports/exports must mitigate spreadsheet formula injection and avoid leaking source records through logs and AI providers.

## Phase 07C–07D additional safeguards

An opt-in single-user access token protects `/api/v1` when `AXIOM_PUBLIC_MODE` is enabled. HMAC-signed HttpOnly Secure SameSite=Strict cookies expire after eight hours and cookie-authenticated mutations require same-origin browser Origin. Remote deployment also needs real HTTPS, edge rate limits, explicit secret rotation and audit logging. The backend is private to the Compose network; Nginx binds only to host 127.0.0.1:8080. Public multi-user operation remains **unsupported**.

Reporting exports evidence-only chart points, so CSV contains only numeric coordinates and avoids spreadsheet formula injection. AI receives compact server-selected metadata rather than uploaded data; it is optional and its explanations are not verified numerical computations.

**Unresolved:** Preventing uploads from consuming resources before multipart parsing, malicious Excel sandboxing, resource caps per request/user, access control per dataset, data-at-rest encryption, secret rotation, independent pentest, and production load/backup validation.
