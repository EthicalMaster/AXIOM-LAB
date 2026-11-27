# Phase 07C — Single-user access gate, security and accessibility

- Local mode remains open only to a **loopback-bound** server. For deliberate public-mode access, set `AXIOM_PUBLIC_MODE=1` and generate a 32+-character unpredictable `AXIOM_ACCESS_TOKEN`. A missing secret fails closed with HTTP 503.
- Protected API endpoints use a short-lived HMAC-signed HttpOnly Secure SameSite=Strict cookie (8 hours) or direct administrator bearer token. Cookie-based state-changing requests require same-origin `Origin`; changing-method calls from other origins return HTTP 403. Source bytes and secret are never logged by this code.
- The browser gate does not retain the access token after successful login. API-provided session cookie is HttpOnly. Authentication is **single-user**, NOT multi-tenant account separation.
- Responses add nosniff, no-referrer, DENY framing and a restrictive permissions policy. The UI adds visible focus styles, minimum target sizes, a labeled access form, keyboard navigation and reduced-motion support. Manual keyboard, zoom, and screen-reader testing remains required.
- Manual: local mode works with no login; simulate public mode behind HTTPS, wrong-token login returns 401, valid login works, missing secret fails closed, cross-origin POST returns 403, logout removes access.
- High-priority limitations: reverse proxy TLS/auth/rate limits, ingress restrictions, durable identity/account isolation, CSP, audit logs, antivirus/office-file scanning, and penetration testing are **not verified**. Do not expose the development server to the internet.
