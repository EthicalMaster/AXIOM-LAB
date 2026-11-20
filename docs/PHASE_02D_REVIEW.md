# Phase 02D — Diagnostics acceptance

Only a Shapiro–Wilk normality diagnostic is introduced. No independence, sampling-bias or variance-equality checks are claimed. SciPy warns that for n>5000 its p-value may not be accurate; we withhold it there. Constant samples and n<3 are also withheld.

Check a numeric column with 3–5000 nonconstant values, a constant column, <3 observations, >5000 observations, missing values and corrupt files. Run all existing tests and frontend checks. Explain why p>0.05 is not proof of normality, and why a normality diagnostic does not establish independent observations. This phase completes the initial limited inference and diagnostic slices, not the entire statistics module.
