"""Transparent single linear-regression baseline with train-only fitted preprocessing."""
from __future__ import annotations

import math
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from app.services.ml_common import read_supervised, holdout, preprocessing, SEED
from app.services.dataset_validation import DatasetValidationError


def regression(raw: bytes, suffix: str, features: list[str], target: str) -> dict:
    data = read_supervised(raw,suffix,features,target,'regression')
    X_train,X_test,y_train,y_test=holdout(data)
    pipeline=preprocessing(LinearRegression())
    pipeline.fit(X_train,y_train)
    predicted=pipeline.predict(X_test)
    if not np.all(np.isfinite(predicted)):
        raise DatasetValidationError('ml_numerical_error', 'Predictions exceeded finite numerical limits.')
    mae=float(mean_absolute_error(y_test,predicted))
    rmse=float(math.sqrt(mean_squared_error(y_test,predicted)))
    # R² is undefined if the held-out target is constant.
    r2=float(r2_score(y_test,predicted)) if np.var(y_test)>0 else None
    if not all(math.isfinite(x) for x in (mae,rmse)) or (r2 is not None and not math.isfinite(r2)):
        raise DatasetValidationError('ml_numerical_error', 'Regression metrics exceeded finite numerical limits.')
    return {'method':'linear-regression-v1','target':target,'features':features,
            'train_rows':len(y_train),'test_rows':len(y_test),'dropped_target_rows':data.dropped_targets,
            'seed':SEED,'mae':mae,'rmse':rmse,'r2':r2,
            'training_r2':float(pipeline.score(X_train,y_train)) if np.var(y_train)>0 else None,
            'examples':[{'actual':float(a),'predicted':float(p)} for a,p in zip(y_test[:20],predicted[:20])],
            'warnings':['Preprocessing fits training rows only. Random holdout assumes independent, non-time-dependent observations.',
                        'This is a baseline, not a causal model. Check residuals and compare with appropriate alternatives.'] +
                       (['Held-out R² is undefined because test targets are constant.'] if r2 is None else [])}
