"""Deterministic, evidence-limited suggestions; not automatic scientific conclusions."""

def suggest_methods(profile: dict, goal: str) -> dict:
    columns = profile['columns']
    numeric = [c for c in columns if c['inferred_type'] == 'numeric']
    classes = [c for c in columns if c['inferred_type'] in ('categorical','boolean')]
    n = profile['row_count']
    suggestions = []
    if goal == 'describe':
        if numeric:
            suggestions.append({'method':'descriptive-statistics','reason':'Consistently numeric columns are available.',
                'assumptions':['Observations represent the intended sample.'],
                'next_step':'Review per-column descriptive statistics and missing values.'})
    elif goal == 'distribution':
        if numeric:
            suggestions.append({'method':'histogram-and-quartiles','reason':'A numeric sample can be grouped into frequency bins.',
                'assumptions':['Histogram appearance depends on bin choice.'],
                'next_step':'Inspect frequencies and flagged extremes in Distribution Explorer.'})
    elif goal == 'mean_test':
        if numeric and n >= 2:
            suggestions.append({'method':'one-sample-t-test','reason':'A numeric column may be compared with a predeclared reference mean.',
                'assumptions':['Independent observations','Appropriate sampling','Normality is important for small samples'],
                'next_step':'Choose the reference mean before inspecting the test; review diagnostics.'})
    elif goal == 'prediction':
        if len(numeric) >= 2 and n >= 16:
            suggestions.append({'method':'regression-holdout','reason':'A numeric target and separate numeric predictor are available.',
                'assumptions':['Rows are independent','No time/group dependence','Predictor is not the target'],
                'next_step':'Select predictor and target in Machine Learning Studio; evaluate untouched holdout.'})
        if numeric and classes and n >= 16:
            suggestions.append({'method':'classification-holdout','reason':'Numeric predictors and a categorical target are available.',
                'assumptions':['Classes have enough examples','Rows are independent','No temporal/group leakage'],
                'next_step':'Verify target balance and use stratified classification.'})
    return {'goal':goal,'row_count':n,
            'column_types': [{'name':c['name'],'type':c['inferred_type'],'missing_count':c['missing_count']} for c in columns],
            'suggestions':suggestions,
            'warnings':([] if suggestions else ['Insufficient suitable columns or observations; the selected method is not recommended.']) +
                       ['Suggestions do not verify sampling design, independence, causality or study validity.'],
            'source':'deterministic-rules-v1'}
