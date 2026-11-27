"""Bounded JSON, numeric CSV and PDF exports of one persisted chart run."""
import re
from typing import Literal
from fastapi import APIRouter, HTTPException, Query, Response
from app.persistence.experiment_store import read_experiment, get_run
from app.services.reporting import report_record, json_report, csv_report, pdf_report

router=APIRouter(prefix='/experiments',tags=['reports'])

@router.get('/{experiment_id}/runs/{run_id}/report')
def get_report(experiment_id: str, run_id: str, format:Literal['json','csv','pdf']=Query(default='pdf')) -> Response:
    if not all(re.fullmatch(r'[0-9a-f]{32}',i) for i in (experiment_id,run_id)):
        raise HTTPException(404,detail='Report not found')
    experiment=read_experiment(experiment_id)
    run=get_run(experiment_id,run_id)
    if not experiment or not run:
        raise HTTPException(404,detail='Report not found')
    payload=report_record(experiment,run)
    renderers={'json':(json_report,'application/json'),
               'csv':(csv_report,'text/csv; charset=utf-8'),
               'pdf':(pdf_report,'application/pdf')}
    renderer,media=renderers[format]
    raw=renderer(payload)
    return Response(content=raw,media_type=media,headers={
        'Content-Disposition':f'attachment; filename="axiom-{run_id}.{format}"',
        'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})
