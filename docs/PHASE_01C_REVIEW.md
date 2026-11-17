# Phase 01C acceptance review — descriptive statistics

1. Upload `examples/datasets/descriptive_reference.csv`.
2. Confirm `value` has mean=3, median=3, sample variance=2.5, population variance=2, Q1=2, Q3=4; `code` must NOT become numeric.
3. Confirm the display is marked descriptive, not inferential, and the original preview is unchanged.
4. `PYTHONPATH=backend python -m pytest backend/tests -q` should pass; `npm run test && npm run typecheck && npm run build` from frontend should pass.
5. Error case: a mixed column containing `NA` is never silently coerced.
6. Check health endpoint phase `01C` and that /docs lists the statistics endpoint.
7. Discuss: sample vs population variance; why n=1 has no sample standard deviation; why a numerical column may be excluded.

Do not mark verified until the local browser flow and automated checks pass.
