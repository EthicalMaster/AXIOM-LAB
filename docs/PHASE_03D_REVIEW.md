# Phase 03D — Numerical methods

SciPy's bounded `brentq` searches for a root only when function values at interval ends change sign or one endpoint is zero. Even-multiplicity roots can be missed without sign change. `quad` numerically integrates the same polynomial and returns an *estimated* absolute error, not an exact guarantee.

Use coefficients `[1,0,-4]`, bounds 0..3: root 2 and definite integral -3. Test `x²+1` over [-1,1] (no bracketed root) and invalid/excessive intervals. Run full Python and JS checks, then explain bracketing versus unconstrained root solving, and why numerical quadrature differs from symbolic integration.
