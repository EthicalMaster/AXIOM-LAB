# Phase 04C — Logistic classification

This is an explicit categorical/boolean-target classification task. Fitting happens inside a preprocessing+logistic pipeline after a stratified 75/25 holdout. At least four samples per class and 16 labelled rows are required. Accuracy, macro precision/recall/F1, confusion matrix and (binary only, when valid) ROC-AUC describe held-out behaviour. Random rows must be independently sampled; target label quality cannot be established by code.

Test binary groups `A` vs `B` with feature separation: verify class order, confusion matrix counts, stratified test composition and ROC-AUC. Check rare-class rejection, invalid numeric targets, repeatability and no source mutation. Explain why accuracy alone can mislead under imbalance and why ROC-AUC is omitted for unsupported configurations.
