# Why descriptive statistics are implemented this way

- **Purpose**: describe finite observations without estimating population parameters or making significance claims.
- **Mean**: sum of observations / n; **median**: middle ranked value.
- **Sample variance**: sum((x-mean)^2)/(n-1) for n≥2; **population variance** uses n.
- **Quartiles**: type-7 interpolation at index (n−1)p; other software offers different definitions, so record the convention.
- **Missing values**: empty cells omitted, not estimated; nonstandard tokens like `NA` keep the whole column mixed.
- **Alternatives**: NumPy/Pandas can speed vectorized computation but add dependencies and dtype policy; `statistics` works for bounded early workloads.
- **Limitations**: finite floating-point arithmetic; explicit large-magnitude rejection; no units, weights, uncertainty estimates, or inferential tests yet.
- **Scale**: 50k rows/5MiB max and repeated reading are deliberate temporary constraints; production needs benchmarks and job isolation.
