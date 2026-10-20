# VendorFlow — Decisions

Interview-facing log. Status: accepted unless noted.

## Stack (accepted)

Use the GPT-chosen stack: Python 3.14, Streamlit, Pydantic, deterministic Python rules, Supabase `vendorflow-dev2`, PyMuPDF, optional Gemini, pytest, Ruff.

**Why:** already installed/proven locally (Python, Gemini call, Supabase project). Streamlit Community Cloud is the shortest live URL. Rules stay testable.

**Trade-off:** Cloud may not honor 3.14. App logic must run on 3.12–3.14. Pin `streamlit>=1.52`.

## Intake (accepted)

**Form is the primary intake.** PDF is an optional extra check.

**Why:** Assignment FAQ allows forms/JSON. Interview must not die on a parser. PS-2 still mentions documents, so keep PyMuPDF as an added path.

**How vendors are created:** fictional `VF-DEMO-*` records in `fixtures.py`, loaded into form widgets; operator can also type the form; optional tiny text PDFs generated from those same fields. No real PAN/GSTIN.

## Status authority (accepted)

Rules engine sets Approved / Pending / Rejected. Gemini never does.

Rejected only for a labeled **demo blocklist**. Ambiguity → Pending, not fraud.

Format checks ≠ external verification. UI must say so.

## Persistence (accepted)

Full GPT-ish relational schema (vendors, submissions, documents, validation_results, processing_runs, run_events). User applies SQL in the dashboard. Anon insert/select for synthetic data. Session fallback if DB is down.

**Do not** create a second Supabase project. **Do not** commit service role keys.

## Gemini (accepted)

P1, default off. Extract candidates or draft follow-up. Fallback to templates.

## Deferred (accepted)

OCR, n8n, multi-agent, registry APIs, outbound email, spend analytics.

## Hosting (accepted)

Streamlit Community Cloud public URL is P0 (assignment requires a live link). Local-only is not a valid submit.
