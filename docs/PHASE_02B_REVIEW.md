# Phase 02B acceptance — distribution and outlier indicators

1. Upload `examples/datasets/distribution_reference.csv`; select `value` in Distribution explorer.
2. Histogram must count actual observations (sum of bin counts = nonmissing numeric count). Verify table values; no synthetic data.
3. On values 1,2,3,4,5, the result has four Sturges bins (n=5), quartiles Q1=2, Q3=4, median=3 and zero Tukey indicators.
4. Verify a different sample (1,2,2,3,100) produces one Tukey outlier indicator. This is not proof an observation is erroneous.
5. Test single-valued column: one zero-width bin and caution; with <4 observations, indicator is N/A.
6. Missing cells are excluded, not filled. Mixed numeric/NA text values must be rejected, not silently coerced.
7. Run complete backend tests and frontend test/typecheck/build; revisit the saved experiment and quality audit.
8. Explain: frequency vs probability density; why histogram bins affect appearance; outlier indicator vs genuine data error; why an n<4 threshold is used.

No probability model fitting, inferential statistics or automated cleaning is included.
