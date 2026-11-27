"""Cloud PostgreSQL experiment persistence, preserving the local API contract."""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone

from app.persistence import cloud


def create_experiment(*, name: str, dataset_id: str, dataset_sha256: str,
                      configuration: dict, result: dict) -> dict:
    experiment_id = uuid.uuid4().hex
    run_id = uuid.uuid4().hex
    timestamp = datetime.now(timezone.utc).isoformat()
    environment = {'python': '.'.join(map(str, sys.version_info[:3])), 'algorithm': result['method']}
    with cloud.database() as connection:
        connection.execute('INSERT INTO experiments VALUES (%s, %s, %s, %s, %s)',
                           (experiment_id, name, dataset_id, dataset_sha256, timestamp))
        connection.execute('''INSERT INTO runs
            (id, experiment_id, created_at, status, method, configuration_json,
             result_json, environment_json, revision) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)''',
            (run_id, experiment_id, timestamp, 'completed', result['method'],
             json.dumps(configuration, allow_nan=False),
             json.dumps(result, allow_nan=False), json.dumps(environment)))
    return {'id': experiment_id, 'name': name, 'dataset_id': dataset_id,
            'dataset_sha256': dataset_sha256, 'created_at': timestamp,
            'run': {'id': run_id, 'created_at': timestamp, 'status': 'completed',
                    'method': result['method'], 'revision': 1, 'source_run_id': None, 'configuration': configuration,
                    'result': result, 'environment': environment}}


def read_experiment(experiment_id: str) -> dict | None:
    with cloud.database() as connection:
        experiment = connection.execute('SELECT * FROM experiments WHERE id = %s', (experiment_id,)).fetchone()
        if experiment is None:
            return None
        run = connection.execute('SELECT * FROM runs WHERE experiment_id = %s ORDER BY revision DESC, created_at DESC LIMIT 1', (experiment_id,)).fetchone()
        if run is None:
            return None
        return {
            'id': experiment['id'], 'name': experiment['name'], 'dataset_id': experiment['dataset_id'],
            'dataset_sha256': experiment['dataset_sha256'], 'created_at': experiment['created_at'],
            'run': {'id': run['id'], 'created_at': run['created_at'], 'status': run['status'],
                    'method': run['method'], 'revision': run['revision'], 'source_run_id': run['source_run_id'],
                    'configuration': json.loads(run['configuration_json']),
                    'result': json.loads(run['result_json']), 'environment': json.loads(run['environment_json'])},
        }


def list_experiments(limit: int = 20, offset: int = 0) -> dict:
    """Paginated history in local single-user mode; no user accounts yet."""
    with cloud.database() as connection:
        total = connection.execute('SELECT COUNT(*) AS total FROM experiments').fetchone()["total"]
        rows = connection.execute('''SELECT e.id, e.name, e.dataset_id, e.dataset_sha256,
            e.created_at, (SELECT COUNT(*) FROM runs AS r WHERE r.experiment_id = e.id) AS run_count
            FROM experiments AS e ORDER BY e.created_at DESC, e.id DESC LIMIT %s OFFSET %s''',
            (limit, offset)).fetchall()
        return {'total': total, 'items': [dict(row) for row in rows], 'limit': limit, 'offset': offset}


def list_experiment_runs(experiment_id: str, limit: int = 20, offset: int = 0) -> dict | None:
    with cloud.database() as connection:
        exists = connection.execute('SELECT id FROM experiments WHERE id = %s FOR UPDATE', (experiment_id,)).fetchone()
        if exists is None:
            return None
        total = connection.execute('SELECT COUNT(*) AS total FROM runs WHERE experiment_id = %s', (experiment_id,)).fetchone()["total"]
        rows = connection.execute('''SELECT * FROM runs WHERE experiment_id = %s
            ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s''', (experiment_id, limit, offset)).fetchall()
        return {'experiment_id': experiment_id, 'total': total, 'limit': limit, 'offset': offset,
                'items': [{'id': r['id'], 'created_at': r['created_at'], 'status': r['status'],
                           'method': r['method'], 'revision': r['revision'], 'source_run_id': r['source_run_id'],
                           'configuration': json.loads(r['configuration_json']),
                           'result': json.loads(r['result_json']), 'environment': json.loads(r['environment_json'])}
                          for r in rows]}


def append_experiment_run(experiment_id: str, configuration: dict, result: dict,
                          *, source_run_id: str | None = None) -> dict | None:
    """Append a run under an atomic per-experiment revision number."""
    timestamp = datetime.now(timezone.utc).isoformat()
    run_id = uuid.uuid4().hex
    environment = {'python': '.'.join(map(str, sys.version_info[:3])), 'algorithm': result['method']}
    with cloud.database() as connection:
        # Lock the experiment row before allocating its next revision.
        exists = connection.execute('SELECT id FROM experiments WHERE id = %s', (experiment_id,)).fetchone()
        if exists is None:
            return None
        revision = connection.execute('SELECT COALESCE(MAX(revision), 0)+1 AS revision FROM runs WHERE experiment_id=%s',
                                      (experiment_id,)) .fetchone()["revision"]
        connection.execute('''INSERT INTO runs (id, experiment_id, created_at, status, method,
            configuration_json, result_json, environment_json, revision, source_run_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (run_id, experiment_id, timestamp, 'completed', result['method'],
             json.dumps(configuration, allow_nan=False), json.dumps(result, allow_nan=False),
             json.dumps(environment), revision, source_run_id))
    return {'id': run_id, 'created_at': timestamp, 'status': 'completed', 'method': result['method'],
            'revision': revision, 'source_run_id': source_run_id,
            'configuration': configuration, 'result': result, 'environment': environment}


def get_run(experiment_id: str, run_id: str) -> dict | None:
    # Direct indexed lookup avoids a 50-run pagination limit.
    with cloud.database() as connection:
        row = connection.execute('SELECT * FROM runs WHERE experiment_id=%s AND id=%s',
                                 (experiment_id, run_id)).fetchone()
        if row is None:
            return None
        return {'id': row['id'], 'created_at': row['created_at'], 'status': row['status'],
                'method': row['method'], 'revision': row['revision'],
                'source_run_id': row['source_run_id'],
                'configuration': json.loads(row['configuration_json']),
                'result': json.loads(row['result_json']), 'environment': json.loads(row['environment_json'])}
