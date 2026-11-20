# Phase 04A — Training-only preprocessing

Selected features must be 1–8 distinct, fully numeric columns; targets are separate. A 75/25, seeded random split occurs **before** median imputation and standard scaling. Only training rows fit the preprocessing parameters; test rows are transformed with those parameters. Maximum 2,000 rows. Classification targets must be categorical/boolean with 2–8 classes and at least four records each.

Test 40-row numeric dataset: 30 training, 10 test. Verify training-only median and mean using the returned metrics; reject selecting target as a feature, mixed features, <16 labelled observations and `time_dependent=true`. Explain how train/test leakage arises and why time-based and group-based splits will require additional designs. No training algorithm is included in this bundle.
