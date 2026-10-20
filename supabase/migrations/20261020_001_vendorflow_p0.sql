-- VendorFlow P0 schema for the existing vendorflow-dev2 project only.
-- Synthetic demo data only. The anon policies below are intentionally demo-insecure.

create table if not exists public.vendors (
    id uuid primary key default gen_random_uuid(),
    legal_name text not null,
    gstin text not null,
    pan text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.processing_runs (
    id uuid primary key,
    started_at timestamptz not null,
    completed_at timestamptz,
    final_status text not null check (final_status in ('Approved', 'Pending', 'Rejected')),
    error text,
    created_at timestamptz not null default now()
);

create table if not exists public.onboarding_submissions (
    id uuid primary key default gen_random_uuid(),
    vendor_id uuid not null references public.vendors(id),
    processing_run_id uuid not null references public.processing_runs(id),
    legal_name text not null,
    gstin text not null,
    fields jsonb not null,
    status text not null check (status in ('Approved', 'Pending', 'Rejected')),
    summary text not null,
    reason_codes jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists public.vendor_documents (
    id uuid primary key default gen_random_uuid(),
    submission_id uuid not null references public.onboarding_submissions(id) on delete cascade,
    filename text not null,
    document_type text not null,
    parse_status text not null check (parse_status in ('pass', 'fail', 'needs_review', 'not_checked')),
    extracted_text text,
    created_at timestamptz not null default now()
);

create table if not exists public.validation_results (
    id uuid primary key default gen_random_uuid(),
    submission_id uuid not null references public.onboarding_submissions(id) on delete cascade,
    check_id text not null,
    outcome text not null check (outcome in ('pass', 'fail', 'needs_review', 'not_checked')),
    reason_code text,
    human_readable_reason text not null,
    evidence_reference text,
    follow_up_action text,
    in_scope boolean not null default true,
    created_at timestamptz not null default now()
);

create table if not exists public.run_events (
    id bigint generated always as identity primary key,
    processing_run_id uuid not null references public.processing_runs(id) on delete cascade,
    stage_id text not null,
    label text not null,
    state text not null check (state in ('complete', 'skipped', 'fallback', 'error')),
    detail text not null,
    occurred_at timestamptz not null,
    created_at timestamptz not null default now()
);

create index if not exists onboarding_submissions_created_at_idx on public.onboarding_submissions (created_at desc);
create index if not exists onboarding_submissions_gstin_idx on public.onboarding_submissions (gstin);
create index if not exists vendors_legal_name_idx on public.vendors (legal_name);

alter table public.vendors enable row level security;
alter table public.processing_runs enable row level security;
alter table public.onboarding_submissions enable row level security;
alter table public.vendor_documents enable row level security;
alter table public.validation_results enable row level security;
alter table public.run_events enable row level security;

grant usage on schema public to anon;
grant select, insert on public.vendors, public.processing_runs, public.onboarding_submissions, public.vendor_documents, public.validation_results, public.run_events to anon;
grant usage, select on sequence public.run_events_id_seq to anon;

create policy "vendorflow_demo_anon_select_vendors" on public.vendors for select to anon using (true);
create policy "vendorflow_demo_anon_insert_vendors" on public.vendors for insert to anon with check (true);
create policy "vendorflow_demo_anon_select_processing_runs" on public.processing_runs for select to anon using (true);
create policy "vendorflow_demo_anon_insert_processing_runs" on public.processing_runs for insert to anon with check (true);
create policy "vendorflow_demo_anon_select_submissions" on public.onboarding_submissions for select to anon using (true);
create policy "vendorflow_demo_anon_insert_submissions" on public.onboarding_submissions for insert to anon with check (true);
create policy "vendorflow_demo_anon_select_documents" on public.vendor_documents for select to anon using (true);
create policy "vendorflow_demo_anon_insert_documents" on public.vendor_documents for insert to anon with check (true);
create policy "vendorflow_demo_anon_select_validation" on public.validation_results for select to anon using (true);
create policy "vendorflow_demo_anon_insert_validation" on public.validation_results for insert to anon with check (true);
create policy "vendorflow_demo_anon_select_events" on public.run_events for select to anon using (true);
create policy "vendorflow_demo_anon_insert_events" on public.run_events for insert to anon with check (true);
