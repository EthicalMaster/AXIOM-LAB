# Phase 04D — K-means exploratory clustering

A limited numeric-feature K-means experiment fits median imputation and standardization over the entire unlabelled dataset. No held-out classification claim is made. Cluster IDs are arbitrary; inertia and silhouette are internal fit/shape indicators. K values 2–8, at most 2,000 rows and eight features keep local CPU use bounded.

Test 20 values around 0–19 and 20 around 100–119: find two groups and high silhouette. Verify group sizes add up to original observations. Check missing features, constant values, invalid K, source preservation. Explain why unsupervised grouping does not provide known truth labels or predictive accuracy.
