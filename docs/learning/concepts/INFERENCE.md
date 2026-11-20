# Why the one-sample t-test exists

For an independent sample with mean x̄, hypothesised mean μ₀, sample SD s and size n, `t=(x̄−μ₀)/(s/√n)`. Under a suitable null model it follows a Student t distribution with `n−1` degrees of freedom. A two-sided p-value uses both tails. A `(1−α)` confidence interval is `x̄ ± t_(1−α/2,n−1)×s/√n`.

The calculation does **not** prove causation, independence, random sampling or exact normality. An effect size and scientifically meaningful units remain necessary for interpretation. The method is versioned; invalid or zero-variance samples are rejected rather than manufacturing a result.
