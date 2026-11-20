# Phase 02C — One-sample statistical inference

## Purpose and limitations

The platform now supports an explicit, *two-sided* one-sample Student t-test for a uniformly numeric column. It returns a statistic, degrees of freedom, two-sided p-value, confidence interval, Cohen's d, and limitations. This is **not** a general hypothesis-testing engine. Independent observations and approximate normality (particularly for small samples) must be justified by the user. Never interpret a p-value as `P(H0 is true)`.

## Checks before committing

1. Import a CSV with `v` values `1,2,3,4,5`; set null mean `0`. Check `t≈4.24264`, `p≈0.01324`, and 95% CI approximately `[1.0368,4.9632]`.
2. Repeat with null mean `3`: `t=0` and `p=1`.
3. Use one observation, all-constant observations, missing cells and text-mixed observations: check graceful errors and warnings.
4. Revisit all earlier features. Run `pytest`, `npm run test`, `npm run typecheck`, `npm run build`.
5. Explain the difference between statistical and practical significance, the standard error, and why this test needs an assumption about independent observations.

## Engineering decision

SciPy's Student t distribution is used for tail probabilities and critical values rather than reimplementing distribution functions. Alternative: custom statistical routines (worse validation burden); a larger statistics framework (unnecessary now). Risk: proper inference depends on experimental design, which a CSV alone cannot establish.
