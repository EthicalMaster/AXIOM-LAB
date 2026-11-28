"""Minimal immutable experiment and run persistence for Phase 01D.

This is not a scheduler, multi-user access control, or scientific notebook system.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import uuid
from contextlib import closing
from datetime import datetime, timezone

from app.persistence.dataset_store import _data_root, _database


def _ensure_tables(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE IF NOT EXISTS experiments (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, dataset_id TEXT NOT NULL,
        dataset_sha256 TEXT NOT NULL, created_at TEXT NOT NULL,
        FOREIGN KEY(dataset_id) REFERENCES datasets(id)
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL, created_at TEXT NOT NULL,
        status TEXT NOT NULL, method TEXT NOT NULL, configuration_json TEXT NOT NULL,
        result_json TEXT NOT NULL, environment_json TEXT NOT NULL,
        revision INTEGER NOT NULL DEFAULT 1, source_run_id TEXT,
        FOREIGN KEY(experiment_id) REFERENCES experiments(id)
    )""")
    # Forward-only migration: historical run rows retain revision 1.
    columns = {row[1] for row in connection.execute('PRAGMA table_info(runs)')}
    if 'revision' not in columns:
        connection.execute('ALTER TABLE runs ADD COLUMN revision INTEGER NOT NULL DEFAULT 1')
    if 'source_run_id' not in columns:
        connection.execute('ALTER TABLE runs ADD COLUMN source_run_id TEXT')
    connection.execute('CREATE INDEX IF NOT EXISTS idx_runs_experiment_revision ON runs(experiment_id, revision DESC)')
    connection.execute('CREATE INDEX IF NOT EXISTS idx_experiments_created ON experiments(created_at DESC, id DESC)')


def create_experiment(*, name: str, dataset_id: str, dataset_sha256: str,
                      configuration: dict, result: dict) -> dict:
    from app.persistence import cloud_store
    if cloud_store.enabled():
        return cloud_store.create_experiment(name=name, dataset_id=dataset_id, dataset_sha256=dataset_sha256, configuration=configuration, result=result)
    experiment_id = uuid.uuid4().hex
    run_id = uuid.uuid4().hex
    timestamp = datetime.now(timezone.utc).isoformat()
    environment = {'python': '.'.join(map(str, sys.version_info[:3])), 'algorithm': result['method']}
    with closing(_database(_data_root())) as connection, connection:
        connection.execute('PRAGMA foreign_keys = ON')
        _ensure_tables(connection)
        connection.execute('INSERT INTO experiments VALUES (?, ?, ?, ?, ?)',
                           (experiment_id, name, dataset_id, dataset_sha256, timestamp))
        connection.execute('''INSERT INTO runs
            (id, experiment_id, created_at, status, method, configuration_json,
             result_json, environment_json, revision) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)''',
            (run_id, experiment_id, timestamp, 'completed', result['method'],
             json.dumps(configuration, allow_nan=False),
             json.dumps(result, allow_nan=False), json.dumps(environment)))
    return {'id': experiment_id, 'name': name, 'dataset_id': dataset_id,
            'dataset_sha256': dataset_sha256, 'created_at': timestamp,
            'run': {'id': run_id, 'created_at': timestamp, 'status': 'completed',
                    'method': result['method'], 'revision': 1, 'source_run_id': None, 'configuration': configuration,
                    'result': result, 'environment': environment}}


def read_experiment(experiment_id: str) -> dict | None:
    from app.persistence import cloud_store
    if cloud_store.enabled():
        return cloud_store.read_experiment(experiment_id)
    root = _data_root()
    if not (root / 'axiom.sqlite3').exists():
        return None
    with closing(_database(root)) as connection:
        connection.row_factory = sqlite3.Row
        _ensure_tables(connection)
        experiment = connection.execute('SELECT * FROM experiments WHERE id = ?', (experiment_id,)).fetchone()
        if experiment is None:
            return None
        run = connection.execute('SELECT * FROM runs WHERE experiment_id = ? ORDER BY revision DESC, created_at DESC LIMIT 1', (experiment_id,)).fetchone()
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
    from app.persistence import cloud_store
    if cloud_store.enabled():
        return cloud_store.list_experiments(limit, offset)
    root = _data_root()
    if not (root / 'axiom.sqlite3').exists():
        return {'total': 0, 'items': [], 'limit': limit, 'offset': offset}
    with closing(_database(root)) as connection:
        connection.row_factory = sqlite3.Row
        _ensure_tables(connection)
        total = connection.execute('SELECT COUNT(*) FROM experiments').fetchone()[0]
        rows = connection.execute('''SELECT e.id, e.name, e.dataset_id, e.dataset_sha256,
            e.created_at, (SELECT COUNT(*) FROM runs AS r WHERE r.experiment_id = e.id) AS run_count
            FROM experiments AS e ORDER BY e.created_at DESC, e.id DESC LIMIT ? OFFSET ?''',
            (limit, offset)).fetchall()
        return {'total': total, 'items': [dict(row) for row in rows], 'limit': limit, 'offset': offset}


def list_experiment_runs(experiment_id: str, limit: int = 20, offset: int = 0) -> dict | None:
    from app.persistence import cloud_store
    if cloud_store.enabled():
        return cloud_store.list_experiment_runs(experiment_id, limit, offset)
    root = _data_root()
    if not (root / 'axiom.sqlite3').exists():
        return None
    with closing(_database(root)) as connection:
        connection.row_factory = sqlite3.Row
        _ensure_tables(connection)
        exists = connection.execute('SELECT id FROM experiments WHERE id = ?', (experiment_id,)).fetchone()
        if exists is None:
            return None
        total = connection.execute('SELECT COUNT(*) FROM runs WHERE experiment_id = ?', (experiment_id,)).fetchone()[0]
        rows = connection.execute('''SELECT * FROM runs WHERE experiment_id = ?
            ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?''', (experiment_id, limit, offset)).fetchall()
        return {'experiment_id': experiment_id, 'total': total, 'limit': limit, 'offset': offset,
                'items': [{'id': r['id'], 'created_at': r['created_at'], 'status': r['status'],
                           'method': r['method'], 'revision': r['revision'], 'source_run_id': r['source_run_id'],
                           'configuration': json.loads(r['configuration_json']),
                           'result': json.loads(r['result_json']), 'environment': json.loads(r['environment_json'])}
                          for r in rows]}


def append_experiment_run(experiment_id: str, configuration: dict, result: dict,
                          *, source_run_id: str | None = None) -> dict | None:
    """Append a run under an atomic per-experiment revision number."""
    from app.persistence import cloud_store
    if cloud_store.enabled():
        return cloud_store.append_experiment_run(experiment_id, configuration, result, source_run_id=source_run_id)
    timestamp = datetime.now(timezone.utc).isoformat()
    run_id = uuid.uuid4().hex
    environment = {'python': '.'.join(map(str, sys.version_info[:3])), 'algorithm': result['method']}
    with closing(_database(_data_root())) as connection:
        connection.execute('PRAGMA foreign_keys = ON')
        _ensure_tables(connection)
        with connection:
            connection.execute('BEGIN IMMEDIATE')
            exists = connection.execute('SELECT id FROM experiments WHERE id = ?', (experiment_id,)).fetchone()
            if exists is None:
                return None
            revision = connection.execute('SELECT COALESCE(MAX(revision), 0)+1 FROM runs WHERE experiment_id=?',
                                          (experiment_id,)).fetchone()[0]
            connection.execute('''INSERT INTO runs (id, experiment_id, created_at, status, method,
                configuration_json, result_json, environment_json, revision, source_run_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (run_id, experiment_id, timestamp, 'completed', result['method'],
                 json.dumps(configuration, allow_nan=False), json.dumps(result, allow_nan=False),
                 json.dumps(environment), revision, source_run_id))
    return {'id': run_id, 'created_at': timestamp, 'status': 'completed', 'method': result['method'],
            'revision': revision, 'source_run_id': source_run_id,
            'configuration': configuration, 'result': result, 'environment': environment}


def get_run(experiment_id: str, run_id: str) -> dict | None:
    # Direct indexed lookup avoids a 50-run pagination limit.
    from app.persistence import cloud_store
    if cloud_store.enabled():
        return cloud_store.get_run(experiment_id, run_id)
    root = _data_root()
    if not (root / 'axiom.sqlite3').exists():
        return None
    with closing(_database(root)) as connection:
        connection.row_factory = sqlite3.Row
        _ensure_tables(connection)
        row = connection.execute('SELECT * FROM runs WHERE experiment_id=? AND id=?',
                                 (experiment_id, run_id)).fetchone()
        if row is None:
            return None
        return {'id': row['id'], 'created_at': row['created_at'], 'status': row['status'],
                'method': row['method'], 'revision': row['revision'],
                'source_run_id': row['source_run_id'],
                'configuration': json.loads(row['configuration_json']),
                'result': json.loads(row['result_json']), 'environment': json.loads(row['environment_json'])}
