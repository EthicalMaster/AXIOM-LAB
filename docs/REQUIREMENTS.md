# Requirements and traceability — v1.0 RC

Implemented means source and corresponding tests exist; automated evidence does not certify browser, hosted or scientific acceptance. See [release assurance](RELEASE_ASSURANCE.md).

| ID | Bounded requirement | Status | Automated evidence / outstanding acceptance |
|---|---|---|---|
| REQ-001 | Versioned API connection | Implemented | Frontend CI; browser check pending |
| REQ-002 | Health contract | Implemented | `test_health.py` |
| REQ-003 | CSV/XLSX/XLS import | Implemented | `test_datasets.py`; browser file boundary checks pending |
| REQ-004 | Inspection and descriptive statistics | Implemented | `test_column_profiling.py`, `test_statistics.py`, `test_quality.py`, `test_distributions.py` |
| REQ-005 | Persist chart experiments | Implemented | `test_experiments.py`, `test_experiment_history.py` |
| REQ-006 | Hypothesis testing and diagnostics | Implemented | `test_hypothesis.py`, `test_diagnostics.py`; bounded methods |
| REQ-007 | Safe math | Implemented | `test_safe_math.py`, `test_polynomial.py`, `test_linear_algebra.py`, `test_numerical_methods.py` |
| REQ-008 | ML and leakage safeguards | Implemented | `test_ml_preprocessing.py`, regression/classification/clustering/evaluation tests |
| REQ-009 | Compatible comparisons and replay | Implemented | `test_run_comparison.py`, `test_run_reproduction.py`, `test_experiment_versions.py`; chart-only replay |
| REQ-010 | Optional advisory AI and consent | Implemented | `test_ai_provider.py`, `test_contextual_guide.py`, `test_lens.py`; live provider pending |
| REQ-011 | Evidence PDF/CSV/JSON | Implemented | `test_reports.py`; visual inspection pending |
| REQ-012 | Theme and motion | Implemented | Frontend CI; keyboard/mobile/reduced-motion acceptance pending |
| REQ-013 | Single-operator protection and recovery | Implemented | `test_release_security.py`, `test_request_guard.py`, `test_backup_restore.py` |
| REQ-014 | Release packaging | Candidate | `test_hosted_release.py`, `test_release_assets.py`; Docker and hosted checks pending |

## Open decisions

Hosting and measured resource budgets; license and data-handling policy; public multi-user identity, authorization, isolated storage, distributed quotas and workers are outside v1.0 RC. Method conventions and limits remain in historical phase reviews and [scientific validation](SCIENTIFIC_VALIDATION.md).
