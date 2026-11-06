# Security foundation

Phase 0 has no file uploads and no user-defined computation. Never interpret absence of features as production readiness.

## Mandatory future safeguards

- Strict input schemas; allowlisted operations and parameters.
- No shell/exec evaluation of user-supplied expressions.
- No Python `eval`, arbitrary notebook execution, or unsafe `sympy.parse_expr` usage.
- Restricted math grammar and expression complexity limits.
- Upload byte/type checks, size limits, filename/path isolation, sheet and formula handling.
- Isolation, timeouts, and memory limits for expensive computations.
- Safe API error responses without secrets or file system paths.
- No secrets, sensitive datasets, runtime logs, local database, or generated artifacts in Git.
- Review production deployment, CORS, ownership, authentication, and rate limits if public exposure is added.
