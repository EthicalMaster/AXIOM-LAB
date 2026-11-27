# Phase 04E — Train-only cross-validation and model comparison

Both baselines receive the same 75/25 holdout and 3-fold training-only cross-validation. Every CV fold fits preprocessing on its own training partition. Regression compares linear and ridge by **negative MAE** (larger is better) and reports held-out MAE. Classification compares logistic regression and depth-4 decision tree by **macro F1** and reports held-out macro F1. This is not an exhaustive model search. The holdout should be consulted once, after choosing a model from training CV.

Check `y=4x+1` regression with model comparison; held-out MAE should be close to zero. Check categorical labels A/B and stratified CV. Test time-dependent rejection, integrity checks and full suite. Explain why preprocessing outside CV would leak validation folds, and why repeatedly trying new models after inspecting the test set undermines the test's independence.
