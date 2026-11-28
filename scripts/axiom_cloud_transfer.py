"""Offline migration from a stopped, verified local SQLite snapshot. No deletes.
Use --apply only against an empty cloud workspace; interrupted transfers require review.
"""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from uuid import UUID

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))


def inspect(source):
    source=source.resolve()
    db=source/'axiom.sqlite3'
    if not db.is_file() or db.is_symlink(): raise ValueError('Snapshot database unavailable.')
    with closing(sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)) as conn:
        conn.row_factory=sqlite3.Row
        if conn.execute('PRAGMA integrity_check').fetchall()[0][0]!='ok' or conn.execute('PRAGMA foreign_key_check').fetchall(): raise ValueError('SQLite integrity check failed.')
        datasets=[]; experiments=[]; runs=[]
        for r in conn.execute('SELECT * FROM datasets ORDER BY id'):
            id=r['id']; fmt=r['file_format']
            if not re.fullmatch('[0-9a-f]{32}',id) or fmt not in ('csv','xls','xlsx'): raise ValueError('Invalid dataset identifier or format.')
            raw_path=source/'datasets'/id/('original.'+fmt)
            if raw_path.resolve()!=raw_path or not raw_path.is_file() or raw_path.stat().st_size!=r['size_bytes'] or not 0<r['size_bytes']<=5242880: raise ValueError('Invalid original path or size.')
            raw=raw_path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=r['sha256']: raise ValueError('Original fingerprint mismatch.')
            meta={k:r[k] for k in ('id','original_name','sha256','size_bytes','uploaded_at','row_count','column_count')}
            meta.update(format=fmt,worksheet=r['sheet_name'],headers=json.loads(r['headers_json']),sheet_names=json.loads(r['sheet_names_json']),warnings=json.loads(r['warnings_json']))
            datasets.append((meta,raw_path))
        tables={r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if 'experiments' in tables:
            if 'runs' not in tables: raise ValueError('Experiment runs table missing.')
            datasets_by_id={m['id']:m for m,_ in datasets}
            for r in conn.execute('SELECT * FROM experiments ORDER BY id'):
                record=dict(r); d=datasets_by_id.get(record['dataset_id'])
                if not d or d['sha256']!=record['dataset_sha256'] or not re.fullmatch('[0-9a-f]{32}',record['id']): raise ValueError('Experiment dataset reference mismatch.')
                experiments.append(record)
                previous=set()
                for n,rr in enumerate(conn.execute('SELECT * FROM runs WHERE experiment_id=? ORDER BY revision',(r['id'],)),1):
                    run={k:rr[k] for k in ('id','created_at','status','method','revision','source_run_id')}
                    if not re.fullmatch('[0-9a-f]{32}',run['id']) or run['revision']!=n or (run['source_run_id'] and run['source_run_id'] not in previous): raise ValueError('Invalid run lineage.')
                    previous.add(run['id']);run.update(configuration=json.loads(rr['configuration_json']),result=json.loads(rr['result_json']),environment=json.loads(rr['environment_json']))
                    runs.append((r['id'],run))
                if not previous: raise ValueError('Experiment has no run.')
        if 'runs' in tables and conn.execute('SELECT count(*) FROM runs').fetchone()[0]!=len(runs): raise ValueError('Unassociated runs.')
    return datasets,experiments,runs


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('snapshot',type=Path);p.add_argument('--owner',required=True);p.add_argument('--apply',action='store_true');p.add_argument('--writers-stopped',action='store_true');a=p.parse_args()
    if not a.writers_stopped: p.error('Stop all writers and use an independently verified snapshot.')
    owner=str(UUID(a.owner));datasets,experiments,runs=inspect(a.snapshot)
    print(f'Verified snapshot: {len(datasets)} datasets, {len(experiments)} experiments, {len(runs)} runs, {sum(m["size_bytes"] for m,_ in datasets)} bytes.')
    if not a.apply: return
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env',override=False,interpolate=False)
    from app.core.tenant import tenant_scope,admitted
    from app.persistence import cloud_store as c
    if not admitted(owner): raise ValueError('Owner must already be an admitted tenant.')
    with tenant_scope(owner):
        if any(c.rows(t,select='id',limit=1) for t in ('datasets','experiments','runs')): raise ValueError('Cloud workspace is not empty. Refusing to overwrite.')
        for meta,path in datasets:
            c.persist_original(meta,path.read_bytes(),'.'+meta['format'])
            if c.find_dataset(meta['id'])!=meta: raise ValueError('Cloud dataset metadata mismatch.')
        groups={r['id']:[] for r in experiments}
        for eid,run in runs: groups[eid].append(run)
        for record in experiments:
            eid=record['id']; first,*rest=groups[eid]
            if c.rpc('axiom_create_experiment',p_record=record,p_run=first)!={**record,'run':first}: raise ValueError('Cloud experiment verification failed.')
            for run in rest:
                if c.rpc('axiom_append_run',p_experiment=eid,p_run=run)!=run: raise ValueError('Cloud run verification failed.')
        for meta,_ in datasets: c.read_original_dataset(meta['id'],meta)
        for record in experiments:
            if c.read_experiment(record['id'])!={**record,'run':groups[record['id']][-1]}: raise ValueError('Final experiment verification failed.')
            for run in groups[record['id']]:
                if c.get_run(record['id'],run['id'])!=run: raise ValueError('Final run verification failed.')
    print('Cloud records and originals verified. Local snapshot was not modified.')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(f'Transfer stopped ({type(exc).__name__}). Do not retry a partial import until an administrator checks cloud state. Local snapshot remains unchanged.',file=sys.stderr);sys.exit(1)
