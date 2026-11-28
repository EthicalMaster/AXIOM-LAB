-- Run in the dedicated AXIOM LAB SQL Editor after batches 09–16.
begin;
alter table public.axiom_datasets add column if not exists display_label text check(length(display_label)<=120);
create table if not exists public.axiom_projects (
 owner_id uuid not null, id text not null check(id ~ '^[0-9a-f]{32}$'), name text not null check(length(trim(name)) between 1 and 120), created_at timestamptz not null default now(), primary key(owner_id,id)
);
create table if not exists public.axiom_project_items (
 owner_id uuid not null, id text not null check(id ~ '^[0-9a-f]{32}$'), project_id text not null, dataset_id text, experiment_id text,
 primary key(owner_id,id), check ((dataset_id is null) <> (experiment_id is null)),
 foreign key(owner_id,project_id) references public.axiom_projects(owner_id,id),
 foreign key(owner_id,dataset_id) references public.axiom_datasets(owner_id,id),
 foreign key(owner_id,experiment_id) references public.axiom_experiments(owner_id,id),
 unique(owner_id,project_id,dataset_id), unique(owner_id,project_id,experiment_id)
);
create table if not exists public.axiom_profiles (
 owner_id uuid primary key, display_name text not null default '' check(length(display_name)<=80), deletion_requested_at timestamptz
);
create index if not exists axiom_projects_recent on public.axiom_projects(owner_id,created_at desc,id desc);
create index if not exists axiom_library_recent on public.axiom_datasets(owner_id,created_at desc,id desc) where ready;
alter table public.axiom_projects enable row level security;
alter table public.axiom_project_items enable row level security;
alter table public.axiom_profiles enable row level security;
revoke all on public.axiom_projects,public.axiom_project_items,public.axiom_profiles from public,anon,authenticated;
grant select,insert,update on public.axiom_projects,public.axiom_profiles to service_role;
grant select,insert,delete on public.axiom_project_items to service_role;
create or replace function public.axiom_library(p_owner uuid,p_search text,p_limit integer,p_offset integer)
returns jsonb language sql stable security invoker set search_path='' as $$
 select jsonb_build_object('total',(select count(*) from public.axiom_datasets where owner_id=p_owner and ready and (p_search='' or (strpos(lower(metadata->>'original_name'),lower(p_search))>0 or strpos(lower(coalesce(display_label,'')),lower(p_search))>0))),
 'items',coalesce((select jsonb_agg(t.metadata || jsonb_build_object('label',t.display_label) order by t.created_at desc,t.id desc) from (select metadata,display_label,created_at,id from public.axiom_datasets where owner_id=p_owner and ready and (p_search='' or (strpos(lower(metadata->>'original_name'),lower(p_search))>0 or strpos(lower(coalesce(display_label,'')),lower(p_search))>0)) order by created_at desc,id desc limit greatest(1,least(p_limit,50)) offset greatest(0,least(p_offset,10000))) t),'[]'::jsonb));
$$;
create or replace function public.axiom_project_create(p_owner uuid,p_id text,p_name text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare result jsonb;
begin
 perform pg_advisory_xact_lock(hashtextextended(p_owner::text,2101));
 if (select count(*) from public.axiom_projects where owner_id=p_owner)>=100 then return null; end if;
 insert into public.axiom_projects(owner_id,id,name) values(p_owner,p_id,p_name) returning jsonb_build_object('id',id,'name',name,'created_at',created_at) into result;
 return result;
end $$;
create or replace function public.axiom_project_attach(p_owner uuid,p_project text,p_kind text,p_id text)
returns text language plpgsql security invoker set search_path='' as $$
begin
 perform 1 from public.axiom_projects where owner_id=p_owner and id=p_project for update;
 if not found then return 'missing'; end if;
 if p_kind='dataset' then
  if not exists(select 1 from public.axiom_datasets where owner_id=p_owner and id=p_id and ready) then return 'missing'; end if;
 elsif p_kind='experiment' then
  if not exists(select 1 from public.axiom_experiments where owner_id=p_owner and id=p_id) then return 'missing'; end if;
 else return 'missing'; end if;
 if exists(select 1 from public.axiom_project_items where owner_id=p_owner and project_id=p_project and ((p_kind='dataset' and dataset_id=p_id) or (p_kind='experiment' and experiment_id=p_id))) then return 'ok'; end if;
 if (select count(*) from public.axiom_project_items where owner_id=p_owner and project_id=p_project)>=200 then return 'limit'; end if;
 insert into public.axiom_project_items(owner_id,id,project_id,dataset_id,experiment_id) values(p_owner,replace(gen_random_uuid()::text,'-',''),p_project,case when p_kind='dataset' then p_id end,case when p_kind='experiment' then p_id end);
 return 'ok';
end $$;
create or replace function public.axiom_profile_update(p_owner uuid,p_name text)
returns jsonb language sql security invoker set search_path='' as $$
 insert into public.axiom_profiles(owner_id,display_name) values(p_owner,p_name) on conflict(owner_id) do update set display_name=excluded.display_name returning jsonb_build_object('display_name',display_name,'deletion_requested_at',deletion_requested_at);
$$;
create or replace function public.axiom_deletion_request(p_owner uuid,p_request boolean)
returns jsonb language sql security invoker set search_path='' as $$
 insert into public.axiom_profiles(owner_id,deletion_requested_at) values(p_owner,case when p_request then now() end) on conflict(owner_id) do update set deletion_requested_at=case when p_request then coalesce(axiom_profiles.deletion_requested_at,now()) end returning jsonb_build_object('display_name',display_name,'deletion_requested_at',deletion_requested_at);
$$;
-- This is aggregate operator information, not a user-facing RPC.
create or replace function public.axiom_admin_summary(p_owner uuid)
returns jsonb language sql stable security invoker set search_path='' as $$
 select jsonb_build_object('dataset_owners',(select count(distinct owner_id) from public.axiom_datasets where ready),'datasets',(select count(*) from public.axiom_datasets where ready),'pending',(select count(*) from public.axiom_datasets where not ready),'bytes',(select coalesce(sum(size_bytes),0) from public.axiom_datasets),'projects',(select count(*) from public.axiom_projects),'experiments',(select count(*) from public.axiom_experiments),'deletion_requests',(select count(*) from public.axiom_profiles where deletion_requested_at is not null));
$$;
revoke all on function public.axiom_library(uuid,text,integer,integer),public.axiom_project_create(uuid,text,text),public.axiom_project_attach(uuid,text,text,text),public.axiom_profile_update(uuid,text),public.axiom_deletion_request(uuid,boolean),public.axiom_admin_summary(uuid) from public,anon,authenticated;
grant execute on function public.axiom_library(uuid,text,integer,integer),public.axiom_project_create(uuid,text,text),public.axiom_project_attach(uuid,text,text,text),public.axiom_profile_update(uuid,text),public.axiom_deletion_request(uuid,boolean),public.axiom_admin_summary(uuid) to service_role;
commit;
