# Phase plan and bundle roadmap

**Scope control:** Build one vertical slice, verify, learn, document, commit, then continue. Bundles can be split if a testable unit is too large.

| Phase | Bundles | Outcome |
|---|---|---|
| 00 Foundation | One initial ZIP | Runnable React/FastAPI starter, docs, tests, Git ready |
| 01 First Experiment | 01A upload/validation (user-verified CSV flow); 01B inspection (implementation candidate); 01C computation; 01D chart + minimal persistence | First reproducible real experiment |
| 02 Statistics | 02A profiling; 02B distributions; 02C tests; 02D diagnostics | Statistically validated investigation |
| 03 Mathematics | 03A safe expressions; 03B algebra/calculus; 03C linear algebra; 03D numerical methods | Bounded math workbench |
| 04 Machine Learning | 04A preprocessing; 04B regression; 04C classification; 04D clustering; 04E evaluation | Inspectable ML experiments |
| 05 Advanced Experiments | 05A history; 05B versions; 05C comparison; 05D reproduction | Full experiment management |
| 06 Optional AI | 06A adapter; 06B method guidance; 06C grounded explanations | AI enhances understanding only |
| 07 Reporting/Release | 07A reporting; 07B performance; 07C security/accessibility; 07D deployment | Audited showcase release |

## Gating criteria

Every bundle requires: defined objective, conceptual explanation, source and contract review, working interface where relevant, unit/integration/reference tests, human manual checks, learning notes, and a documented status. Failures must be reported before commit.

Minimal experiment identity/configuration/run records are intentionally introduced in Phase 01; Phase 05 extends them.

## Phase 01A implementation candidate

Bundle 01A adds a bounded import UI, backend CSV/XLSX/XLS validation, immutable original-file storage, SQLite metadata and readback. It does **not** include statistics, cleaning, interactive charts, or experiment records. Accept the bundle only after the Windows verification in `PHASE_01A_REVIEW.md` and a human review of the learning questions.

### Phase 01B exit gate

Column inspection must show truthful provisional type labels, missingness and bounded distinct counts from original persisted data, preserve the 01A workflow, and pass numerical-free structural tests. See `docs/PHASE_01B_REVIEW.md`.
