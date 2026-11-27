"""Derive a compact evidence card from one saved chart run, without raw uploads."""
from __future__ import annotations
import hashlib
import json


def evidence_for_run(experiment:dict, run:dict) -> dict:
    chart=run['result']
    points=chart.get('points',[])
    ys=[point['y'] for point in points]
    return {
        'experiment_id':experiment['id'], 'run_id':run['id'],
        'revision':run['revision'], 'dataset_sha256':experiment['dataset_sha256'],
        'method':run['method'], 'column':chart.get('column'),
        'observations_total':chart.get('original_point_count'),
        'shown_observations':chart.get('shown_point_count'),
        'missing_observations':chart.get('missing_count'),
        'sampled':chart.get('sampled',False),
        'displayed_minimum':min(ys) if ys else None,
        'displayed_maximum':max(ys) if ys else None,
        'limitations':['Displayed range covers sampled points only.' if chart.get('sampled') else 'Displayed range covers all chart points.',
                       'Observation order is not time; this result does not establish causality.'],
    }


def evidence_hash(evidence:dict) -> str:
    return hashlib.sha256(json.dumps(evidence,sort_keys=True,allow_nan=False).encode()).hexdigest()


def offline_interpretation(evidence: dict) -> str:
    count = evidence['observations_total']
    column = evidence['column']
    prefix = (f"The recorded {evidence['method']} chart contains {count} "
              f"nonempty observations for column {column!r}. ")
    visibility = ('The display is sampled; its minimum and maximum may miss extremes. '
                  if evidence['sampled'] else 'All valid observations are displayed. ')
    return prefix + visibility + ('This descriptive result does not establish a causal or '
                                  'time-dependent relationship.')
