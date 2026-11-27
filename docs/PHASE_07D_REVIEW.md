# Phase 07D — Local release-candidate packaging

Includes Docker Compose (bound to localhost), a non-root backend, non-root static frontend, SQLite volume, Nginx same-origin API reverse proxy with basic CSP, and a deployment/runbook. The local frontend proxy defaults to the user's Windows port 8898 while Docker routes internally to 8000. Docker uses a single Python worker; this is deliberate for local reproducibility, not capacity optimization.

Exit gate: 100% backend tests, full npm test/typecheck/build, Docker Compose build and local smoke walkthrough, PDF rendering and accessibility/manual security checks. Docker is not available in the builder environment; local Compose build and cross-platform runtime are **unverified** until performed on your machine.

No public launch until threat modeling, secret management, user isolation, data lifecycle policies, ingress rate limits, load verification and independent security review.
