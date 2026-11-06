# Scientific validation policy

No scientific algorithms exist in Phase 0; this is an agreement for later phases.

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
