"""Shared bounded supervised-data contract; train/test preprocessing stays separate."""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from app.services.column_profiling import _source_rows, profile_columns
from app.services.dataset_validation import DatasetValidationError

SEED = 42
MAX_ML_ROWS = 2000
MAX_ML_FEATURES = 8

@dataclass
class MLData:
    X: np.ndarray
    y: np.ndarray
    dropped_targets: int
    feature_names: list[str]
    task: str


def read_supervised(raw: bytes, suffix: str, features: list[str], target: str, task: str) -> MLData:
    profile = profile_columns(raw, suffix)
    kinds = {c['name']: c['inferred_type'] for c in profile['columns']}
    if (task not in ('regression', 'classification') or
        not 1 <= len(features) <= MAX_ML_FEATURES or len(set(features)) != len(features) or
        target in features or target not in kinds or any(kinds.get(f) != 'numeric' for f in features)):
        raise DatasetValidationError('invalid_ml_columns', 'Choose 1–8 distinct numeric features and a separate target.')
    if task == 'regression' and kinds[target] != 'numeric':
        raise DatasetValidationError('invalid_ml_target', 'Regression requires a consistently numeric target.')
    if task == 'classification' and kinds[target] not in ('categorical', 'boolean'):
        raise DatasetValidationError('invalid_ml_target', 'Classification requires an explicitly categorical/boolean target.')
    if profile['row_count'] > MAX_ML_ROWS:
        raise DatasetValidationError('ml_size_limit', 'Interactive training is capped at 2,000 rows.')
    columns = [c['name'] for c in profile['columns']]
    indices = [columns.index(f) for f in features]
    target_index = columns.index(target)
    samples, labels, dropped = [], [], 0
    first = True
    with _source_rows(raw, suffix) as rows:
        for row in rows:
            cells = list(row)
            if not cells or all(v is None or not str(v).strip() for v in cells):
                continue
            if first:
                first=False
                continue
            padded=(cells + [None]*len(columns))[:len(columns)]
            y_value=padded[target_index]
            if y_value is None or not str(y_value).strip():
                dropped+=1
                continue
            xrow=[]
            for idx in indices:
                value=padded[idx]
                number=float(value) if value is not None and str(value).strip() else float('nan')
                if math.isfinite(number) and abs(number)>1e8:
                    raise DatasetValidationError('ml_range_limit', 'Feature values must be within ±100,000,000.')
                xrow.append(number)
            if all(math.isnan(v) for v in xrow):
                raise DatasetValidationError('ml_missing_row', 'A row has no present feature values; explicit cleaning is required.')
            samples.append(xrow)
            labels.append(float(y_value) if task=='regression' else str(y_value).strip())
    if len(samples)<16:
        raise DatasetValidationError('insufficient_ml_rows', 'At least 16 labelled rows are needed for the initial 75/25 holdout.')
    X=np.asarray(samples,dtype=np.float64)
    y=np.asarray(labels,dtype=np.float64 if task=='regression' else str)
    if not np.all(np.isfinite(X[~np.isnan(X)])) or (task=='regression' and (not np.all(np.isfinite(y)) or np.max(np.abs(y))>1e8)):
        raise DatasetValidationError('ml_range_limit', 'Non-finite or extreme values are unsupported.')
    if np.any(np.all(np.isnan(X),axis=0)):
        raise DatasetValidationError('ml_empty_feature', 'A feature is entirely missing.')
    if task=='classification':
        labels,counts=np.unique(y,return_counts=True)
        if not 2<=len(labels)<=8 or counts.min()<4:
            raise DatasetValidationError('ml_class_balance', 'Classification requires 2–8 classes with at least 4 rows per class.')
    return MLData(X,y,dropped,features,task)


def holdout(data: MLData):
    if data.task=='classification':
        n_classes=len(np.unique(data.y))
        n_test=math.ceil(len(data.y)*0.25)
        if n_test<n_classes:
            raise DatasetValidationError('insufficient_test_rows', 'Holdout must contain at least one observation per class.')
    return train_test_split(data.X,data.y,test_size=0.25,random_state=SEED,
                            stratify=data.y if data.task=='classification' else None)


def preprocessing(estimator=None):
    steps = [SimpleImputer(strategy='median'), StandardScaler()]
    if estimator is not None:
        steps.append(estimator)
    return make_pipeline(*steps)


def preview(raw:bytes,suffix:str,features:list[str],target:str,task:str)->dict:
    data=read_supervised(raw,suffix,features,target,task)
    X_train,X_test,_,_=holdout(data)
    prep=preprocessing()
    fitted_train=prep.fit_transform(X_train)
    fitted_test=prep.transform(X_test)
    imputer=prep.named_steps['simpleimputer']
    scaler=prep.named_steps['standardscaler']
    return {'method':'train-only-median-scaling-v1','task':task,'features':features,'target':target,
            'train_rows':len(X_train),'test_rows':len(X_test),'dropped_target_rows':data.dropped_targets,
            'training_medians':imputer.statistics_.tolist(),
            'training_scaler_means':scaler.mean_.tolist(),
            'train_preview':fitted_train[:3].tolist(),'test_preview':fitted_test[:3].tolist(),
            'seed':SEED,'warnings':['Random 75/25 holdout assumes independent samples; time-series and group-dependent datasets are not supported.',
                                    'Median imputation and scaling were fitted to training rows only. Test rows were transformed with training parameters.']}
