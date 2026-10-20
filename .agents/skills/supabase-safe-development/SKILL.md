---
name: supabase-safe-development
description: Safe Supabase usage for vendorflow-dev2. Planning/implementation must not write via MCP.
---

# Supabase safety skill

- Project: **vendorflow-dev2** (Mumbai). Do not create another project.
- Codex writes SQL under `supabase/migrations/` only.
- The human applies SQL in the Supabase SQL Editor. Ask before any remote apply.
- Treat MCP as read-only if present. No inserts, DDL, or dashboard setting changes via MCP.
- Prefer anon key + RLS policies for select/insert on synthetic tables. Avoid service_role in Streamlit secrets.
- Never commit URLs-with-keys, `.env`, or service role tokens. Do not print them in README or UI.
- If the table is missing or the API errors: session fallback + honest banner. Do not crash. Do not fake persistence.
