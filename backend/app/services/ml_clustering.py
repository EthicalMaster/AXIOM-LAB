"""Small K-means explorer: descriptive grouping, not verified ground-truth labels."""
from __future__ import annotations

import math
import warnings
import numpy as np
from sklearn.cluster import KMeans
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import silhouette_score
from app.services.column_profiling import profile_columns, _source_rows
from app.services.ml_common import MAX_ML_ROWS, MAX_ML_FEATURES, SEED, preprocessing
from app.services.dataset_validation import DatasetValidationError


def cluster(raw:bytes,suffix:str,features:list[str],n_clusters:int)->dict:
    profile=profile_columns(raw,suffix)
    columns=[col['name'] for col in profile['columns']]
    types={col['name']:col['inferred_type'] for col in profile['columns']}
    if not 1<=len(features)<=MAX_ML_FEATURES or len(set(features))!=len(features) or any(types.get(f)!='numeric' for f in features):
        raise DatasetValidationError('invalid_cluster_features','Choose 1–8 distinct numeric features.')
    if not 2<=n_clusters<=8 or not 8<=profile['row_count']<=MAX_ML_ROWS or n_clusters>=profile['row_count']:
        raise DatasetValidationError('invalid_cluster_configuration','Require 8–2,000 rows and 2–8 clusters, fewer than observations.')
    indices=[columns.index(f) for f in features]
    records=[];first=True
    with _source_rows(raw,suffix) as rows:
        for record in rows:
            cells=list(record)
            if not cells or all(v is None or not str(v).strip() for v in cells):continue
            if first:first=False;continue
            padded=(cells+[None]*len(columns))[:len(columns)]
            row=[float(padded[i]) if padded[i] is not None and str(padded[i]).strip() else float('nan') for i in indices]
            if all(math.isnan(v) for v in row) or any(math.isfinite(v) and abs(v)>1e8 for v in row):
                raise DatasetValidationError('invalid_cluster_row','Each row needs at least one finite feature and values within ±100,000,000.')
            records.append(row)
    X=np.asarray(records,dtype=float)
    if np.any(np.all(np.isnan(X),axis=0)):
        raise DatasetValidationError('empty_cluster_column','A feature is entirely missing.')
    prep=preprocessing()
    transformed=prep.fit_transform(X)  # Unsupervised exploratory task has no held-out score.
    if not np.all(np.isfinite(transformed)):
        raise DatasetValidationError('ml_numerical_error','Preprocessing produced a non-finite feature.')
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', ConvergenceWarning)
        model=KMeans(n_clusters=n_clusters,n_init=10,max_iter=200,random_state=SEED)
        labels=model.fit_predict(transformed)
    unique=np.unique(labels)
    silhouette=float(silhouette_score(transformed,labels)) if 1<len(unique)<len(X) else None
    return {'method':'kmeans-standardized-v1','features':features,'rows':len(X),'seed':SEED,
            'requested_clusters':n_clusters,'found_clusters':len(unique),
            'inertia':float(model.inertia_),'silhouette':silhouette,
            'cluster_counts':{str(int(i)):int(np.sum(labels==i)) for i in unique},
            'centers_scaled':model.cluster_centers_.tolist(),
            'example_assignments':[int(x) for x in labels[:25]],
            'warnings':['K-means centres are in standardized feature space; labels have no intrinsic meaning.',
                        'Silhouette is an internal separation measure, not predictive accuracy.']+
                       (['Not every requested cluster was distinct; data may contain duplicate or tied points.'] if len(unique)<n_clusters else [])}
