-- Run only in the AXIOM LAB project, after cloud batch 09–12.
begin;
create table if not exists public.axiom_request_windows (
 owner_id uuid primary key, window_start timestamptz not null,
 used integer not null check (used between 1 and 1200)
);
alter table public.axiom_request_windows enable row level security;
revoke all on public.axiom_request_windows from public,anon,authenticated;
grant select,insert,update,delete on public.axiom_request_windows to service_role;
-- One row per active identity. All replicas share the same UTC minute window.
create or replace function public.axiom_take_request(p_owner uuid,p_limit integer)
returns boolean language plpgsql security invoker set search_path='' as $$
declare current_window timestamptz := pg_catalog.date_trunc('minute',pg_catalog.clock_timestamp()); accepted integer;
begin
 if p_owner is null or p_limit is null or p_limit not between 1 and 1200 then return false; end if;
 insert into public.axiom_request_windows as w(owner_id,window_start,used) values(p_owner,current_window,1)
 on conflict(owner_id) do update set
 window_start=greatest(w.window_start,excluded.window_start),
 used=case when w.window_start<excluded.window_start then 1 else w.used+1 end
 where w.window_start<excluded.window_start or w.used<p_limit
 returning used into accepted;
 return accepted is not null;
end $$;
create or replace function public.axiom_workspace_usage(p_owner uuid)
returns jsonb language sql stable security invoker set search_path='' as $$
 select pg_catalog.jsonb_build_object('datasets',count(*) filter(where ready),'bytes',coalesce(sum(size_bytes),0),'pending',count(*) filter(where not ready))
 from public.axiom_datasets where owner_id=p_owner;
$$;
revoke all on function public.axiom_take_request(uuid,integer),public.axiom_workspace_usage(uuid) from public,anon,authenticated;
grant execute on function public.axiom_take_request(uuid,integer),public.axiom_workspace_usage(uuid) to service_role;
commit;
