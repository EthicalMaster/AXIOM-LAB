"""Short, deterministic scientific guidance; arbitrary user questions are not computation."""
from __future__ import annotations
import json
import re
from app.services.ai_provider import AIUnavailable, chat_from_evidence

TOPICS = (
    (('p-value','p value','hypothesis'), 'A p-value measures how extreme the observed result is under the null hypothesis. It is not the probability that the null is true. Review the chosen alpha, effect size, interval and assumptions.'),
    (('confidence','interval'), 'A confidence interval describes sampling uncertainty under a stated procedure and assumptions. A 95% procedure covers the true parameter in 95% of repeated samples; it does not certify one particular interval.'),
    (('r2','r²','r-squared','regression','rmse','mae'), 'On held-out data, R² compares squared prediction error to a constant test-mean baseline; it may be negative. MAE averages absolute error, and RMSE emphasizes larger errors. These measures are not causal evidence.'),
    (('classification','confusion','f1','precision','recall'), 'Confusion matrices compare actual rows to predicted columns. Precision measures the share of predicted positives that are correct, recall measures the share of actual positives retrieved, and F1 balances them. Macro averages treat classes equally.'),
    (('cluster','silhouette','inertia'), 'Clusters are unsupervised groups, not known classes. Silhouette describes separation and cohesion; inertia measures within-cluster squared distances in standardized feature space.'),
    (('outlier','quartile','histogram','distribution','median','mean','variance','standard deviation'), 'Mean is the arithmetic average; median is the middle ordered value. Quartiles describe position, standard deviation describes dispersion. Histograms count values in intervals. An outlier indicator is not proof of an error.'),
    (('matrix','determinant','eigenvalue','condition'), 'The determinant and rank describe a square matrix; a large condition number warns that small input changes may strongly affect numerical solutions. Inverses may be withheld for singular or ill-conditioned matrices.'),
    (('import','upload','dataset','missing','completeness'), 'Import a supported dataset in Overview. Data Lab shows missing cells, variable types and duplicate indicators. Original bytes are preserved; these findings do not automatically change the data.'),
    (('run','experiment','reproduce','report','export'), 'Save a chart experiment, then open Experiments and load its history. Reproduce or compare a compatible recorded run, and export the evidence as PDF, CSV or JSON.'),
    (('api','error','loading','connection','offline'), 'Open System checks to inspect API reachability, HTTPS, session state and provider configuration. A failed or timed-out save may have completed; inspect History before repeating it.'),
    (('root','polynomial','integral','derivative'), 'The mathematical workbench accepts bounded numerical expressions and polynomial coefficients. Numerical roots are approximations, and bracketing cannot guarantee detection of all roots.'),
)


def explain(question: str, page: str, evidence: dict | None, use_provider: bool, *, selection: dict | None = None) -> dict:
    normalized = question.casefold()
    def match(text):
        # Match whole terms, prefer the most specific topic. Avoid matching 'mean' in 'meaning'.
        candidates = [(max((len(word) for word in words if re.search(r'(?<!\w)' + re.escape(word) + r'(?!\w)', text)), default=0), answer) for words, answer in TOPICS]
        score, result = max(candidates, key=lambda item: item[0])
        return result if score else None
    answer = match(normalized)
    if answer is None and selection:
        answer = match((selection['label'] + ' ' + selection['excerpt']).casefold())
    if answer is None:
        answer = ('The built-in guide has no exact answer to this question. Try asking about a metric, assumptions, import, or experiment workflow. '
                  'It does not compute new statistics from a chat question.')
    if evidence:
        answer += f"\n\n## Active dataset\n- {evidence['row_count']} rows\n- {evidence['column_count']} variables"
        if evidence.get('column_statistics'):
            values=evidence['column_statistics']
            answer += f"\n- Selected numeric column: mean {values['mean']:.6g}, median {values['median']:.6g}, valid count {values['count']}. Missing cells were excluded."
    if selection:
        answer += '\n\n## Selection context\nThe selected display is client-supplied context, not an independently verified calculation. Review the original result and assumptions.'
    source = 'Built-in scientific guide'
    if use_provider:
        compact=json.dumps({'question':question,'workspace':page,'verified_summary':evidence,'built_in_explanation':answer,'client_selection':selection},ensure_ascii=False)
        try:
            answer=chat_from_evidence(compact)
            source='Optional AI · advisory, not verified calculation'
        except AIUnavailable:
            answer += '\n\n**Provider unavailable:** Optional provider unavailable or at its limit; showing local guidance.'
    return {'answer':answer,'source':source,'evidence':evidence}
