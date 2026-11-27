# Phase 06C — Grounded explanations

- Record-scoped explanation endpoint: `POST /api/v1/ai/explain` (experiment ID and run ID).
- Returns distinct `evidence`, `evidence_sha256`, explanatory text, `source`, and an advisory warning. The evidence card is derived from one stored run, without shipping raw data to the provider.
- Offline mode uses a simple deterministic template; online mode uses optional AI commentary. AI text is never persisted as a verified scientific result.
- Displayed min/max are explicitly **sampled** where appropriate; they are not labeled as global extrema.
- Test: disable provider, save a chart, use History → Explain; confirm verified evidence and limitations. An unknown run returns 404.
