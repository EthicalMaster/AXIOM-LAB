# Phase 04B — Linear regression baseline

A `SimpleImputer(median) → StandardScaler → LinearRegression` pipeline fits only training rows after a deterministic 75/25 holdout. Metrics MAE, RMSE and R² are computed on unseen test rows. If test targets are constant, R² is explicitly unavailable. One training score is included for overfitting inspection, not selection.

Use `y=3x+2`, x=1..80: all held-out scores should be near perfect (MAE≈0, R²≈1). Try missing predictor values, constant test targets, invalid feature names and source corruption. Run regression tests plus frontend checks; interpret what each metric means, why a good fit cannot establish causation, and what information the random holdout assumes.
