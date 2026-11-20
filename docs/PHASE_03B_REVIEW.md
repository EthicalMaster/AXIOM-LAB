# Phase 03B — Bounded polynomial algebra and calculus

Numerical coefficient arrays represent polynomials of degree 1–6; user-entered Python/SymPy syntax is **not** accepted. SymPy differentiates and integrates polynomials, and NumPy estimates roots. The antiderivative assumes C=0; users must supply an arbitrary constant for a general solution. Approximate roots of clustered/multiple roots may be unstable.

Check coefficients `[1,0,-4]` => derivative `2x`, antiderivative `x³/3−4x`, roots ±2. Check `x³−6x²+11x−6` => roots 1,2,3. Reject zero leading coefficient, nonfinite coefficients and degrees >6. Verify complete regression suite and frontend build. Explain why `coefficients` is safer than evaluating a symbolic code string and why root estimates need precision warnings.
