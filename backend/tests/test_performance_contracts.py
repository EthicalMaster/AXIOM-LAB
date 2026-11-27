from fastapi.testclient import TestClient
from app.main import app
from app.persistence.experiment_store import _ensure_tables
import sqlite3

client=TestClient(app)

def test_server_timing_and_no_cache():
    r=client.get('/api/v1/health')
    assert r.status_code==200
    assert r.headers['cache-control']=='no-store'
    assert r.headers['server-timing'].startswith('app;dur=')

def test_history_indexes_present():
    connection=sqlite3.connect(':memory:')
    connection.execute('CREATE TABLE datasets(id TEXT PRIMARY KEY)')
    _ensure_tables(connection)
    names={i[1] for i in connection.execute("SELECT * FROM sqlite_master WHERE type='index'")}
    assert 'idx_runs_experiment_revision' in names
    assert 'idx_experiments_created' in names
    connection.close()
