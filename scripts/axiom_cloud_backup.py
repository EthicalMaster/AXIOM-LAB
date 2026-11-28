"""Export one admitted cloud workspace to a new local SQLite snapshot. Stop all writers first."""
import argparse
import json
import os
import shutil
import sys
import tempfile
from contextlib import closing
from pathlib import Path
from uuid import UUID

from axiom_cloud_transfer import ROOT, inspect


def all_rows(c,table,**params):
    offset=0
    while True:
        total,items=c.page(table,100,offset,**params)
        yield from items
        offset+=len(items)
        if offset>=total:return
        if not items:raise ValueError('Inconsistent cloud pagination.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('destination',type=Path);p.add_argument('--owner',required=True);p.add_argument('--writers-stopped',action='store_true');a=p.parse_args()
    if not a.writers_stopped:p.error('Stop all writers before backing up.')
    dest=a.destination.resolve()
    if dest.exists():raise ValueError('Destination already exists.')
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env',override=False,interpolate=False)
    from app.core.tenant import tenant_scope
    from app.persistence import cloud_store as c
    from app.persistence.dataset_store import _database
    from app.persistence.experiment_store import _ensure_tables
    dest.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.axiom-backup-',dir=dest.parent))
    try:
        with tenant_scope(str(UUID(a.owner))),closing(_database(staging)) as conn,conn:
            _ensure_tables(conn)
            if c.one('datasets',ready='eq.false',select='id'):raise ValueError('Pending uploads need administrator reconciliation first.')
            for row in all_rows(c,'datasets',ready='eq.true',select='metadata',order='id.asc'):
                m=row['metadata']; raw=c.read_original_dataset(m['id'],m); rel=Path('datasets')/m['id']/('original.'+m['format']); path=staging/rel;path.parent.mkdir(parents=True,exist_ok=False);path.write_bytes(raw)
                conn.execute('INSERT INTO datasets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',(m['id'],m['original_name'],m['format'],m['sha256'],m['size_bytes'],m['uploaded_at'],m['row_count'],m['column_count'],json.dumps(m['headers']),m['worksheet'],json.dumps(m['sheet_names']),json.dumps(m['warnings']),rel.as_posix()))
            for row in all_rows(c,'experiments',select='record',order='id.asc'):
                r=row['record'];conn.execute('INSERT INTO experiments VALUES (?,?,?,?,?)',tuple(r[k] for k in ('id','name','dataset_id','dataset_sha256','created_at')))
            for row in all_rows(c,'runs',select='experiment_id,record',order='experiment_id.asc,revision.asc'):
                r=row['record'];conn.execute('INSERT INTO runs (id,experiment_id,created_at,status,method,configuration_json,result_json,environment_json,revision,source_run_id) VALUES (?,?,?,?,?,?,?,?,?,?)',(r['id'],row['experiment_id'],r['created_at'],r['status'],r['method'],json.dumps(r['configuration']),json.dumps(r['result']),json.dumps(r['environment']),r['revision'],r['source_run_id']))
        datasets,experiments,runs=inspect(staging)
        if dest.exists():raise ValueError('Destination already exists.')
        staging.rename(dest)
        print(f'Verified snapshot: {len(datasets)} datasets, {len(experiments)} experiments, {len(runs)} runs.')
    finally:
        if staging.exists():shutil.rmtree(staging)

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(f'Backup stopped ({type(exc).__name__}); no completed snapshot published.',file=sys.stderr);sys.exit(1)
