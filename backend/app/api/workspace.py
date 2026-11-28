"""Private cloud workspace tools. All tenant IDs originate in the verified request context."""
import os
import re
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from app.persistence import cloud_store as cloud
from app.core.tenant import canonical
from app.services.dataset_validation import validate_dataset

router = APIRouter(prefix='/workspace', tags=['workspace'])
ID = r'^[0-9a-f]{32}$'


def identity():
    user = cloud.owner()
    if not cloud.enabled():
        raise HTTPException(409, 'Workspace management requires cloud storage mode.')
    return user


def valid_id(value):
    if not re.fullmatch(ID, value):
        raise HTTPException(404, 'Record not found.')
    return value


def operator():
    if identity() != canonical(os.getenv('AXIOM_GOOGLE_OWNER_ID','').strip()):
        raise HTTPException(403, 'Operator access required.')


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class Name(Input):
    name: str = Field(min_length=1, max_length=120)


class Label(Input):
    label: str = Field(max_length=120)


class Link(Input):
    kind: Literal['dataset','experiment']
    id: str = Field(pattern=ID)


class Profile(Input):
    display_name: str = Field(max_length=80)


class Deletion(Input):
    action: Literal['request','cancel']
    confirmation: str = Field(max_length=30)


@router.get('/datasets')
def library(search: str = Query('',max_length=120), limit: int = Query(20,ge=1,le=50), offset: int = Query(0,ge=0,le=10000)):
    identity()
    return cloud.rpc('axiom_library',p_search=search,p_limit=limit,p_offset=offset)


@router.patch('/datasets/{dataset_id}/label')
def label_dataset(dataset_id: str, body: Label):
    user=identity(); valid_id(dataset_id)
    result=cloud.request('PATCH','/rest/v1/axiom_datasets',params={'owner_id':'eq.'+user,'id':'eq.'+dataset_id,'ready':'eq.true'},json={'display_label':body.label or None},headers={'Prefer':'return=representation'}).json()
    if not result: raise HTTPException(404,'Dataset not found.')
    return {'label':result[0]['display_label']}


@router.get('/datasets/{dataset_id}/open')
def reopen(dataset_id: str):
    identity(); valid_id(dataset_id)
    meta=cloud.find_dataset(dataset_id)
    if not meta: raise HTTPException(404,'Dataset not found.')
    raw=cloud.read_original_dataset(dataset_id,meta)
    profile=validate_dataset(raw,'.'+meta['format'])
    return {**meta,'preview':profile.preview}


@router.get('/datasets/{dataset_id}/original')
def original(dataset_id: str):
    identity(); valid_id(dataset_id)
    meta=cloud.find_dataset(dataset_id)
    if not meta: raise HTTPException(404,'Dataset not found.')
    raw=cloud.read_original_dataset(dataset_id,meta)
    return Response(raw,media_type='application/octet-stream',headers={'Content-Disposition':f'attachment; filename="axiom-{dataset_id}.{meta["format"]}"','Cache-Control':'no-store'})


@router.get('/projects')
def projects(limit: int = Query(20,ge=1,le=50),offset: int = Query(0,ge=0,le=10000)):
    identity(); total,items=cloud.page('projects',limit,offset,select='id,name,created_at',order='created_at.desc,id.desc')
    return {'total':total,'items':items,'limit':limit,'offset':offset}


@router.post('/projects',status_code=201)
def create_project(body: Name):
    identity()
    result=cloud.rpc('axiom_project_create',p_id=uuid4().hex,p_name=body.name)
    if not result: raise HTTPException(409,'Project limit reached.')
    return result


@router.patch('/projects/{project_id}')
def rename_project(project_id: str,body: Name):
    user=identity(); valid_id(project_id)
    result=cloud.request('PATCH','/rest/v1/axiom_projects',params={'owner_id':'eq.'+user,'id':'eq.'+project_id},json={'name':body.name},headers={'Prefer':'return=representation'}).json()
    if not result: raise HTTPException(404,'Project not found.')
    return {'id':result[0]['id'],'name':result[0]['name']}


@router.get('/projects/{project_id}/items')
def project_items(project_id: str):
    identity(); valid_id(project_id)
    if not cloud.one('projects',id='eq.'+project_id,select='id'): raise HTTPException(404,'Project not found.')
    return {'items':cloud.rows('project_items',project_id='eq.'+project_id,select='id,dataset_id,experiment_id',order='id.asc',limit=200)}


@router.post('/projects/{project_id}/items')
def attach(project_id: str,body: Link):
    identity(); valid_id(project_id)
    result=cloud.rpc('axiom_project_attach',p_project=project_id,p_kind=body.kind,p_id=body.id)
    if result=='missing': raise HTTPException(404,'Project or record not found.')
    if result=='limit': raise HTTPException(409,'Project item limit reached.')
    if result!='ok': raise HTTPException(503,'Project update not confirmed.')
    return {'attached':True}


@router.delete('/projects/{project_id}/items/{item_id}')
def detach(project_id: str,item_id: str):
    user=identity(); valid_id(project_id); valid_id(item_id)
    rows=cloud.request('DELETE','/rest/v1/axiom_project_items',params={'owner_id':'eq.'+user,'project_id':'eq.'+project_id,'id':'eq.'+item_id},headers={'Prefer':'return=representation'}).json()
    if not rows: raise HTTPException(404,'Project item not found.')
    return {'detached':True}


@router.get('/account')
def account():
    identity()
    return cloud.one('profiles',select='display_name,deletion_requested_at') or {'display_name':'','deletion_requested_at':None}


@router.put('/account')
def update_account(body: Profile):
    identity(); return cloud.rpc('axiom_profile_update',p_name=body.display_name)


@router.post('/account/deletion')
def deletion(body: Deletion):
    identity()
    if body.confirmation != ('REQUEST DELETION' if body.action=='request' else 'CANCEL'):
        raise HTTPException(422,'Confirmation does not match.')
    return cloud.rpc('axiom_deletion_request',p_request=body.action=='request')


@router.get('/admin')
def admin():
    operator()
    return cloud.rpc('axiom_admin_summary')


@router.get('/admin/deletion-requests')
def deletion_requests(limit: int = Query(20,ge=1,le=50),offset: int = Query(0,ge=0,le=10000)):
    operator()
    return cloud.request('GET','/rest/v1/axiom_profiles',params={'deletion_requested_at':'not.is.null','select':'owner_id,deletion_requested_at','order':'deletion_requested_at.asc,owner_id.asc','limit':limit,'offset':offset}).json()
