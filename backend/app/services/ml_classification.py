"""Small logistic classifier with stratified holdout and transparent metrics."""
from __future__ import annotations

from collections import Counter
import math
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from app.services.ml_common import read_supervised, holdout, preprocessing, SEED
from app.services.dataset_validation import DatasetValidationError


def classification(raw: bytes, suffix: str, features: list[str], target: str) -> dict:
    data=read_supervised(raw,suffix,features,target,'classification')
    X_train,X_test,y_train,y_test=holdout(data)
    pipeline=preprocessing(LogisticRegression(max_iter=400,random_state=SEED))
    pipeline.fit(X_train,y_train)
    predicted=pipeline.predict(X_test)
    clf=pipeline.named_steps['logisticregression']
    classes=[str(c) for c in clf.classes_]
    counts=Counter(map(str,data.y))
    matrix=confusion_matrix(y_test,predicted,labels=clf.classes_).tolist()
    result={'method':'logistic-classification-v1','target':target,'features':features,
        'train_rows':len(y_train),'test_rows':len(y_test),'seed':SEED,
        'labels':classes,'class_counts':dict(counts),
        'accuracy':float(accuracy_score(y_test,predicted)),
        'macro_precision':float(precision_score(y_test,predicted,average='macro',zero_division=0)),
        'macro_recall':float(recall_score(y_test,predicted,average='macro',zero_division=0)),
        'macro_f1':float(f1_score(y_test,predicted,average='macro',zero_division=0)),
        'confusion_matrix':matrix,'roc_auc':None,
        'warnings':['Stratified random holdout; independence and correct labels are assumed.',
                    'Inspect class-level errors: accuracy alone can conceal class imbalance.']}
    if len(classes)==2 and len(np.unique(y_test))==2:
        scores=pipeline.predict_proba(X_test)[:,1]
        result['roc_auc']=float(roc_auc_score(y_test==clf.classes_[1],scores))
    if min(counts.values())/max(counts.values())<0.25:
        result['warnings'].append('Strong class imbalance: inspect precision, recall and class-level counts.')
    if np.max(clf.n_iter_)>=400:
        result['warnings'].append('Optimization reached the iteration limit; coefficients may not have converged.')
    if not all(math.isfinite(v) for v in (result['accuracy'],result['macro_precision'],result['macro_recall'],result['macro_f1'])):
        raise DatasetValidationError('ml_numerical_error', 'Classification metrics were non-finite.')
    return result
