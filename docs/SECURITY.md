# Security — Phase 01A local-only dataset import

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
