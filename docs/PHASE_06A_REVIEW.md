# Phase 06A — Optional replaceable provider

Server-side environment variables configure an OpenAI-compatible endpoint. Nothing in deterministic computation calls the provider. A status endpoint reports **configuration only**; it cannot certify a remote model is reachable.

Safety: HTTPS for remote providers, HTTP only for explicitly enabled loopback, no redirects, bounded summary and response, short timeout, no raw dataset forwarding, no API key in browser. The provider must not be trusted to compute scientific numbers.

Manual: without variables verify `GET /api/v1/ai/status` returns `enabled=false`, while every scientific panel remains usable. Optionally configure a trusted test provider; never publish a real `.env` or API key.

Limitations: Rate limits/terms depend on the user-selected service. A configured endpoint may still be offline. Public multi-user access is not enabled by this bundle.
