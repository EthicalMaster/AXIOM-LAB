"""Fair same-split comparison using pipeline-bound training-only cross-validation."""
from __future__ import annotations

import math
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score
from sklearn.metrics import mean_absolute_error, f1_score
from app.services.ml_common import read_supervised, holdout, preprocessing, SEED
from app.services.dataset_validation import DatasetValidationError


def compare_models(raw:bytes,suffix:str,features:list[str],target:str,task:str)->dict:
    data=read_supervised(raw,suffix,features,target,task)
    X_train,X_test,y_train,y_test=holdout(data)
    if task=='regression':
        candidates={'linear':LinearRegression(),'ridge':Ridge(alpha=1.0)}
        cv=KFold(n_splits=3,shuffle=True,random_state=SEED)
        scoring='neg_mean_absolute_error'
    else:
        labels,counts=np.unique(y_train,return_counts=True)
        if len(labels)<2 or counts.min()<3:
            raise DatasetValidationError('insufficient_cv_rows','At least 3 training samples per class are required for stratified CV.')
        candidates={'logistic':LogisticRegression(max_iter=400,random_state=SEED),
                    'decision_tree':DecisionTreeClassifier(max_depth=4,random_state=SEED)}
        cv=StratifiedKFold(n_splits=3,shuffle=True,random_state=SEED)
        scoring='f1_macro'
    records=[]
    for name,estimator in candidates.items():
        pipe=preprocessing(estimator)
        scores=cross_val_score(pipe,X_train,y_train,cv=cv,scoring=scoring,n_jobs=1)
        if not np.all(np.isfinite(scores)):
            raise DatasetValidationError('ml_numerical_error','Cross-validation produced non-finite metrics.')
        records.append({'name':name,'cv_mean':float(scores.mean()),'cv_std':float(scores.std()),
                        'cv_scores':[float(v) for v in scores]})
    chosen=max(records,key=lambda r:r['cv_mean'])
    final=preprocessing(candidates[chosen['name']])
    final.fit(X_train,y_train)
    prediction=final.predict(X_test)
    metric=(float(mean_absolute_error(y_test,prediction)) if task=='regression'
            else float(f1_score(y_test,prediction,average='macro',zero_division=0)))
    if not math.isfinite(metric):
        raise DatasetValidationError('ml_numerical_error','Held-out metric was not finite.')
    return {'method':'train-cv-model-comparison-v1','task':task,'features':features,'target':target,
            'cv_folds':3,'seed':SEED,'train_rows':len(y_train),'test_rows':len(y_test),
            'cv_metric':scoring,'models':records,'chosen_by_training_cv':chosen['name'],
            'heldout_metric_name':'mae' if task=='regression' else 'macro_f1',
            'heldout_metric':metric,
            'warnings':['Only training rows participate in 3-fold CV, including all fitted preprocessing.',
                        'Chosen model evaluated once on the original held-out data. Repeated test-driven choices invalidate this protection.',
                        'Two simple baselines only; model selection is not a universal best-algorithm claim.']}
