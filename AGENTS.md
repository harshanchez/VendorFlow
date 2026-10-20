# AGENTS.md

You are **Codex** implementing VendorFlow for a Zamp ASA take-home (PS-2). Cursor Agent is not the implementation agent.

## Read first

1. `docs/IMPLEMENTATION_PLAN.md` (source of truth)
2. `docs/DECISIONS.md`
3. `docs/DEMO_SCRIPT.md`

Do not treat `VendorFlow_PLANNING_BRIEF.md` or `VendorFlow_IMPLEMENTATION_PLAN_DRAFT.md` as overrides.

## Product rules

- **Form is primary.** PDFs are optional. Happy-path Approved must work with no file.
- **Rules set status.** Gemini never approves or rejects.
- Fictional `VF-DEMO` data only. No real tax/bank identifiers.
- Format checks are not external verification. Do not claim GSTN/IFSC/PAN lookup.
- Rejected only for the documented demo blocklist.
- Missing/ambiguous → Pending with a concrete follow-up. No outbound email.

## Engineering rules

- Stack: Python 3.14, Streamlit >=1.52, Pydantic, PyMuPDF, supabase, python-dotenv, pytest, ruff. Optional Gemini behind `GEMINI_ENABLED=false`.
- Ship `requirements.txt` for Streamlit Community Cloud.
- Secrets only in `.env` / Streamlit secrets. Never print them. Never commit `.env` or `.streamlit/secrets.toml`.
- Do not create a new Supabase project. Commit SQL; the human applies it in the SQL Editor. No MCP writes.
- Prefer small modules. Do not add n8n, OCR, LangChain, or extra agents.
- Finish P0 acceptance in the plan before P1 Gemini.
- Use Context7 or current official docs when pinning Gemini/Streamlit/Supabase APIs.

## Skills

`.agents/skills/` contains scoped checklists. Follow them; do not duplicate a second architecture.
