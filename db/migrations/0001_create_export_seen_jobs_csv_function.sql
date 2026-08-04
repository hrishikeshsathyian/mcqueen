-- Run this manually in the Supabase SQL editor (or via `supabase db execute`)
-- against the project database. There is no migration runner wired up in
-- this repo yet, so apply it once and keep this file as the source of truth.

create or replace function public.export_seen_jobs_csv()
returns table (
    global_id text,
    title text,
    company text,
    url text,
    fetched_at timestamptz
)
language sql
stable
as $$
    select
        global_id,
        title,
        company,
        coalesce(apply_url, url) as url,
        fetched_at
    from seen_jobs;
$$;
