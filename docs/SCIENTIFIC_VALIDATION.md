# Scientific validation policy

Phase 01C–02B now includes descriptive numerical methods, empirical histogram bins and heuristic outlier indicators. These are candidates pending developer-machine acceptance; the following scientific validation principles remain mandatory.

## Required evidence for each method

1. Define input types, units, domain, mathematical formulation, and expected outputs.
2. Identify numerical assumptions, precision policy, and the method's failure modes.
3. Compare to independent or hand-verifiable reference examples, not only another invocation of the same underlying function.
4. Test edge cases, invalid inputs, missing or degenerate data, and numerical instability.
5. Document sample size, missing-value handling, variance convention, and confidence level when applicable.
6. Show approximation errors, statistical uncertainty, and scientifically relevant warnings.
7. Store method version, dataset fingerprint, parameters, random seed where relevant, dependency versions.

## Explicit safeguards

- Never equate a p-value with the probability that the null hypothesis is true.
- Separate statistical significance from practical significance and effect size.
- Never infer causation from correlation alone.
- Prevent preprocessing leakage: fit transformations on training data only.
- Require time-aware splits for time-ordered data.
- Mark non-convergent, non-finite, or unsupported calculations explicitly.
- When numerical exact replay is impossible, document expected differences.

## Phase 02C–05A methods under review

One-sample Student t and Shapiro–Wilk are limited inferential helpers, not universal selection or proof of assumptions. Mathematical operations enforce documented domains and report approximate numerical solutions where appropriate. ML uses numeric predictors only, a fixed seed for local reproducibility, training-only imputation and scaling, task-appropriate holdouts and training-only CV. Never use test-set results to repeatedly tune a model without obtaining a new independent validation set.

Required future checks: platform-dependent floating-point variability, meaningful units and effect-size interpretation, grouped/time-series splits, fairness and class imbalance, persisted train/run provenance, numerical denial-of-service stress, repeated run comparison and independent scientific review.
