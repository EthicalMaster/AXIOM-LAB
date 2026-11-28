-- Apply in the dedicated AXIOM LAB project's SQL editor. No data is migrated here.
begin;
create table if not exists public.axiom_datasets (
 owner_id uuid not null, id text not null check(id ~ '^[0-9a-f]{32}$'),
 metadata jsonb not null, size_bytes bigint not null check(size_bytes between 1 and 5242880),
 ready boolean not null default false, created_at timestamptz not null default now(),
 primary key(owner_id,id)
);
create table if not exists public.axiom_experiments (
 owner_id uuid not null, id text not null check(id ~ '^[0-9a-f]{32}$'), dataset_id text not null,
 record jsonb not null, created_at text not null, primary key(owner_id,id),
 foreign key(owner_id,dataset_id) references public.axiom_datasets(owner_id,id)
);
create table if not exists public.axiom_runs (
 owner_id uuid not null, experiment_id text not null, id text not null check(id ~ '^[0-9a-f]{32}$'),
 revision integer not null check(revision>0), record jsonb not null,
 primary key(owner_id,experiment_id,id), unique(owner_id,experiment_id,revision),
 foreign key(owner_id,experiment_id) references public.axiom_experiments(owner_id,id)
);
create index if not exists axiom_experiment_history on public.axiom_experiments(owner_id,created_at desc,id desc);
alter table public.axiom_datasets enable row level security;
alter table public.axiom_experiments enable row level security;
alter table public.axiom_runs enable row level security;
-- The trusted API is the only writer and reader. No browser CRUD grants/policies.
revoke all on public.axiom_datasets,public.axiom_experiments,public.axiom_runs from public,anon,authenticated;
grant select,insert,update on public.axiom_datasets,public.axiom_experiments,public.axiom_runs to service_role;
insert into storage.buckets(id,name,public,file_size_limit) values ('axiom-originals','axiom-originals',false,5242880) on conflict(id) do nothing;
do $$ begin
 if not exists(select 1 from storage.buckets where id='axiom-originals' and not public and file_size_limit=5242880) then raise exception 'Existing axiom-originals bucket must be private with a 5 MiB limit'; end if;
end $$;
-- Restrictive policies protect this bucket even if a broad permissive policy is added elsewhere.
drop policy if exists axiom_originals_backend_only on storage.objects;
create policy axiom_originals_backend_only on storage.objects as restrictive for all to anon,authenticated
 using (bucket_id <> 'axiom-originals') with check (bucket_id <> 'axiom-originals');
-- Atomic reservation: tenant and global caps include pending objects; no silent orphan cleanup.
create or replace function public.axiom_reserve(p_owner uuid,p_metadata jsonb,p_max_count integer,p_max_bytes bigint,p_global_bytes bigint)
returns boolean language plpgsql security invoker set search_path='' as $$
declare n bigint; b bigint; g bigint; s bigint := (p_metadata->>'size_bytes')::bigint;
begin
 perform pg_advisory_xact_lock(829104,1);
 select count(*),coalesce(sum(size_bytes),0) into n,b from public.axiom_datasets where owner_id=p_owner;
 select coalesce(sum(size_bytes),0) into g from public.axiom_datasets;
 if n>=p_max_count or b+s>p_max_bytes or g+s>p_global_bytes then return false; end if;
 insert into public.axiom_datasets(owner_id,id,metadata,size_bytes) values(p_owner,p_metadata->>'id',p_metadata,s);
 return true;
end $$;
create or replace function public.axiom_create_experiment(p_owner uuid,p_record jsonb,p_run jsonb)
returns jsonb language plpgsql security invoker set search_path='' as $$
begin
 perform pg_advisory_xact_lock(829104,2);
 if (select count(*) from public.axiom_experiments where owner_id=p_owner)>=5000 then raise exception 'Experiment quota reached'; end if;
 if not exists(select 1 from public.axiom_datasets where owner_id=p_owner and id=p_record->>'dataset_id' and ready and metadata->>'sha256'=p_record->>'dataset_sha256') then return null; end if;
 insert into public.axiom_experiments(owner_id,id,dataset_id,record,created_at) values(p_owner,p_record->>'id',p_record->>'dataset_id',p_record,p_record->>'created_at');
 insert into public.axiom_runs(owner_id,experiment_id,id,revision,record) values(p_owner,p_record->>'id',p_run->>'id',1,p_run);
 return p_record || jsonb_build_object('run',p_run);
end $$;
create or replace function public.axiom_append_run(p_owner uuid,p_experiment text,p_run jsonb)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare rev integer;
begin
 perform 1 from public.axiom_experiments where owner_id=p_owner and id=p_experiment for update;
 if not found then return null; end if;
 if p_run->>'source_run_id' is not null and not exists(select 1 from public.axiom_runs where owner_id=p_owner and experiment_id=p_experiment and id=p_run->>'source_run_id') then return null; end if;
 select coalesce(max(revision),0)+1 into rev from public.axiom_runs where owner_id=p_owner and experiment_id=p_experiment;
 if rev>1000 then raise exception 'Run quota reached'; end if;
 p_run:=p_run || jsonb_build_object('revision',rev);
 insert into public.axiom_runs(owner_id,experiment_id,id,revision,record) values(p_owner,p_experiment,p_run->>'id',rev,p_run);
 return p_run;
end $$;
revoke all on function public.axiom_reserve(uuid,jsonb,integer,bigint,bigint),public.axiom_create_experiment(uuid,jsonb,jsonb),public.axiom_append_run(uuid,text,jsonb) from public,anon,authenticated;
grant execute on function public.axiom_reserve(uuid,jsonb,integer,bigint,bigint),public.axiom_create_experiment(uuid,jsonb,jsonb),public.axiom_append_run(uuid,text,jsonb) to service_role;
commit;
