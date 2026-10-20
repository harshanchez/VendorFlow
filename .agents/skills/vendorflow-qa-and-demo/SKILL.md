---
name: vendorflow-qa-and-demo
description: Tests, honesty, and the five-minute VendorFlow demo.
---

# QA and demo skill

- `ruff check src tests app.py` and `pytest -q` must pass with Gemini off.
- Assert exact fixture statuses/reason codes. Happy path has no document failure codes.
- Only blocklist yields Rejected.
- Persistence failure test: no exception leak, no auto-approve.
- Demo: hosted URL; form happy path without PDF; then bank mismatch, GSTIN format, blocklist; then dashboard.
- Follow `docs/DEMO_SCRIPT.md`. Five minutes max. Narrate real outcomes.
- Do not fabricate accuracy, savings, or “verified with GSTN.”
- Freeze features after the URL works; P1 Gemini only if P0 acceptance is green.
