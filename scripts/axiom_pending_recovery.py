"""Audit one admitted user's pending uploads, optionally finalize a verified original.
No file or row deletion, no replacement, no automatic retries. Stop all writers before repair.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'backend'))


def validate_row(row):
    m = row.get('metadata')
    if not isinstance(m, dict) or row.get('ready') is not False:
        raise ValueError('Invalid pending metadata')
    if (not isinstance(row.get('id'), str) or not re.fullmatch('[0-9a-f]{32}',row['id'])
            or m.get('id') != row['id'] or m.get('format') not in ('csv','xls','xlsx')
            or type(m.get('size_bytes')) is not int or not 0<m['size_bytes']<=5242880
            or row.get('size_bytes') != m['size_bytes']
            or not isinstance(m.get('sha256'),str) or not re.fullmatch('[0-9a-f]{64}',m['sha256'])):
        raise ValueError('Invalid pending metadata')
    return m


def verify_pending(c, dataset_id, *, finalize=False):
    if not re.fullmatch('[0-9a-f]{32}', dataset_id):
        raise ValueError('Invalid dataset ID')
    row = c.one('datasets', id='eq.'+dataset_id, ready='eq.false', select='id,ready,size_bytes,metadata')
    if row is None:
        return 'not_pending'
    m = validate_row(row)
    if m['id'] != dataset_id:
        raise ValueError('Dataset mismatch')
    path = c.object_path(dataset_id, '.'+m['format'])
    raw = c.request('GET','/storage/v1/object/authenticated/'+path).content
    if len(raw)!=m['size_bytes'] or hashlib.sha256(raw).hexdigest()!=m['sha256']:
        return 'integrity_mismatch'
    if not finalize:
        return 'verified_pending'
    # A stopped-writers maintenance action, not a public API. Never changes ownership.
    result = c.request('PATCH','/rest/v1/axiom_datasets',params={
        'owner_id':'eq.'+c.owner(),'id':'eq.'+dataset_id,'ready':'eq.false',
        'size_bytes':'eq.'+str(m['size_bytes']),'metadata->>sha256':'eq.'+m['sha256']},
        json={'ready':True},headers={'Prefer':'return=representation'}).json()
    if not isinstance(result,list) or len(result)!=1 or result[0].get('ready') is not True or result[0].get('id')!=dataset_id:
        raise ValueError('Finalization not confirmed; inspect saved state')
    return 'finalized'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner',required=True,help='Verified Supabase UUID')
    p.add_argument('--dataset',help='32-character pending dataset ID (omit for list)')
    p.add_argument('--finalize',action='store_true')
    p.add_argument('--writers-stopped',action='store_true')
    a=p.parse_args()
    if a.finalize and (not a.dataset or not a.writers_stopped):
        p.error('Finalization requires one dataset ID and stopped writers.')
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env',override=False,interpolate=False)
    from app.core.tenant import tenant_scope, multi_user_enabled
    from app.persistence import cloud_store as c
    if not (c.enabled() and multi_user_enabled()):
        raise ValueError('Managed cloud mode required')
    with tenant_scope(str(UUID(a.owner))):
        if a.dataset:
            outcome=verify_pending(c,a.dataset,finalize=a.finalize)
            print(json.dumps({'result':outcome}))
            return int(outcome not in ('verified_pending','finalized'))
        total,items=c.page('datasets',100,0,ready='eq.false',select='id,size_bytes,created_at',order='created_at.asc,id.asc')
        print(json.dumps({'pending_total':total,'first_100':items},indent=2))
        return 0

if __name__=='__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'Recovery stopped ({type(exc).__name__}); no deletion performed. Check configuration and saved state.',file=sys.stderr)
        raise SystemExit(1)
