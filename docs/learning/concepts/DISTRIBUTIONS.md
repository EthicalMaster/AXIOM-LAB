# Distributions and numerical assumptions

- Histogram = empirical frequencies across intervals; it is not a probability density or a fitted statistical model.
- Bin rule: Sturges k=ceil(1+log2(n)), capped at 20, equal widths; last bin includes its upper edge.
- For constant observations, show a single zero-width bin with the exact value.
- Tukey fences Q1−1.5IQR and Q3+1.5IQR are heuristic markers. The record may be a valid extreme, not an error.
- For n<4, do not report an outlier count. For IQR=0, warn that the heuristic can be unstable.
- Alternative bin schemes: Freedman–Diaconis, Scott, square-root, quantile bins; each has assumptions and tradeoffs.
- Never coerce text `NA`, never silently drop records, never fit a probability model without disclosure.
