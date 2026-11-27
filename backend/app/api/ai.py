"""Optional AI feature status: no credentials exposed."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import json
from typing import Literal
from app.persistence.dataset_store import find_dataset, read_original_dataset, DatasetStorageError
from app.services.column_profiling import profile_columns
from app.services.dataset_validation import DatasetValidationError
from app.services.method_guidance import suggest_methods
from app.persistence.experiment_store import read_experiment, get_run
from app.services.evidence_explanation import evidence_for_run, evidence_hash, offline_interpretation
from app.services.ai_provider import chat_from_evidence
from app.services.ai_provider import configuration, AIUnavailable

router=APIRouter(prefix='/ai',tags=['optional-ai'])

@router.get('/status')
def ai_status() -> dict:
    try:
        return configuration()
    except AIUnavailable:
        return {'enabled':False,'model':None,'reason':'AI provider configuration is invalid.'}


class GuidanceRequest(BaseModel):
    dataset_id: str = Field(pattern=r'^[0-9a-f]{32}$')
    goal: Literal['describe','distribution','mean_test','prediction']
    use_provider: bool = False


@router.post('/guidance')
def method_guidance(request: GuidanceRequest) -> dict:
    metadata=find_dataset(request.dataset_id)
    if metadata is None:
        raise HTTPException(404,detail='Dataset not found')
    try:
        profile=profile_columns(read_original_dataset(request.dataset_id,metadata),'.'+metadata['format'])
    except DatasetStorageError as exc:
        raise HTTPException(409,detail='Dataset integrity failure') from exc
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code,detail=exc.message) from exc
    result=suggest_methods(profile,request.goal)
    result['ai_commentary']=None
    try:
        # Names and missing counts only. Never forward observations or original file bytes.
        evidence=json.dumps({'goal':result['goal'],'row_count':result['row_count'],
                             'column_types':result['column_types'][:20],
                             'suggestions':result['suggestions']},ensure_ascii=True)
        if request.use_provider and len(evidence)<=3400:
            result['ai_commentary']=chat_from_evidence(evidence)
    except AIUnavailable:
        pass
    return result


class ExplainRequest(BaseModel):
    experiment_id: str = Field(pattern=r'^[0-9a-f]{32}$')
    run_id: str = Field(pattern=r'^[0-9a-f]{32}$')
    use_provider: bool = False


@router.post('/explain')
def explain_saved_evidence(request: ExplainRequest) -> dict:
    experiment=read_experiment(request.experiment_id)
    run=get_run(request.experiment_id,request.run_id)
    if not experiment or not run:
        raise HTTPException(404,detail='Saved run not found')
    evidence=evidence_for_run(experiment,run)
    explanation=offline_interpretation(evidence)
    source='deterministic-evidence-template'
    try:
        summary=json.dumps(evidence,sort_keys=True)
        if request.use_provider:
            explanation=chat_from_evidence(summary)
            source='ai-advisory-commentary'
    except AIUnavailable:
        pass
    return {'evidence':evidence,'evidence_sha256':evidence_hash(evidence),
            'explanation':explanation,'source':source,
            'warning':'Only the evidence block is verified by the computation record. Commentary is explanatory, not an independent scientific calculation.'}


class GuideRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    page: Literal['Overview','Data Lab','Statistics','Mathematics','Machine Learning','Experiments','Method guide','System checks']
    dataset_id: str | None = Field(default=None, pattern=r'^[0-9a-f]{32}$')
    column: str | None = Field(default=None, max_length=200)
    use_provider: bool = False


@router.post('/guide')
def contextual_guide(payload: GuideRequest) -> dict:
    from app.services.guide import explain
    from app.services.descriptive_statistics import numeric_series, describe_values
    evidence = None
    if payload.dataset_id:
        metadata = find_dataset(payload.dataset_id)
        if not metadata:
            raise HTTPException(404, detail='Dataset not found')
        evidence = {'row_count':metadata['row_count'], 'column_count':metadata['column_count']}
        if payload.column:
            try:
                raw = read_original_dataset(payload.dataset_id, metadata)
                values, missing = numeric_series(raw, '.' + metadata['format'], payload.column)
                summary = describe_values(values, missing)
                evidence['column_statistics'] = {key: summary[key] for key in ('count','missing_count','mean','median','sample_stddev','q1','q3')}
            except DatasetStorageError as exc:
                raise HTTPException(409, detail='Dataset integrity failure') from exc
            except DatasetValidationError as exc:
                raise HTTPException(exc.status_code, detail=exc.message) from exc
    return explain(payload.question, payload.page, evidence, payload.use_provider)
