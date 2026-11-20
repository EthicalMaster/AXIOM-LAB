# Phase 03C — Linear algebra verification

NumPy operates on real, finite, square matrices with 1–8 rows. Determinants, eigenvalues, rank, condition number and optional systems are computed; inversion/solving is withheld when condition number is nonfinite or exceeds 1e12. This heuristic is not a universal numerical guarantee.

Check `[[2,0],[0,4]]` with RHS `[2,8]`: determinant 8, inverse diagonal `[0.5,0.25]`, solution `[1,2]`, eigenvalues 2 and 4. Check a singular matrix and invalid shape. Run full backend/frontend tests. Explain why a determinant near zero does not alone establish safe invertibility, and why numeric conditioning matters.
