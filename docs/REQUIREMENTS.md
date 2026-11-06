# Requirements and traceability (initial baseline)

Statuses: **Planned** / **Implemented** / **Verified**. Verification requires actual execution evidence, not merely a source file.

| ID | Requirement | First phase | Status | Evidence needed |
|---|---|---|---|---|
| REQ-001 | Frontend connects to versioned backend API | 00 | Implemented (not user-verified) | UI connection status and request |
| REQ-002 | Backend health contract responds without fabricated science | 00 | Implemented (not user-verified) | Pytest and HTTP response |
| REQ-003 | Import and validate CSV/XLSX/XLS datasets | 01 | Planned | Import tests and manual workflow |
| REQ-004 | Inspect datasets and calculate basic descriptive statistics | 01 | Planned | Independent numeric reference tests |
| REQ-005 | Persist a minimal experiment and run | 01 | Planned | Save/reopen/re-run tests |
| REQ-006 | Hypothesis testing with assumptions and diagnostics | 02 | Planned | Reference test cases |
| REQ-007 | Safe mathematical expression processing | 03 | Planned | Security and mathematical tests |
| REQ-008 | Machine learning with leakage safeguards | 04 | Planned | Split/preprocess/evaluate tests |
| REQ-009 | Run comparison and reproducibility support | 05 | Planned | Replay and comparison tests |
| REQ-010 | Optional AI only explains verified computed results | 06 | Planned | Non-AI workflow and grounding tests |
| REQ-011 | Evidence-based PDF/CSV/JSON reporting | 07 | Planned | Export and report correctness tests |

## Open decisions

- Maximum dataset size; maximum execution time and RAM limits (determine with benchmarks).
- Sample vs population variance defaults and missing-value conventions (Phase 01).
- Exact mathematical grammar and supported functions (Phase 03).
- Public release license and hosting (before release).
