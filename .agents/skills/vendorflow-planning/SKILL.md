---
name: vendorflow-planning
description: Keep Codex aligned with the locked VendorFlow plan; do not reopen stack debates during implementation.
---

# VendorFlow planning skill

- Follow `docs/IMPLEMENTATION_PLAN.md`. Do not re-derive architecture unless a P0 blocker appears.
- Form intake is required. PDFs are optional.
- Stack is locked: Python 3.14, Streamlit, Pydantic, rules, Supabase vendorflow-dev2, PyMuPDF, optional Gemini, pytest, Ruff.
- If a dependency fails on Streamlit Cloud, change versions/runtime, not the product shape.
- Do not add n8n, OCR, multi-agent, registry scraping, or email send.
- Preserve `VendorFlow_PLANNING_BRIEF.md` and `VendorFlow_IMPLEMENTATION_PLAN_DRAFT.md`.
