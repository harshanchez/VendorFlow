# VendorFlow — Implementation Plan (Codex)

**Role:** This is the source of truth for building the app. Codex implements. Cursor Agent is not the coder.

**Assignment:** Zamp AI Solutions Associate case study 2026, **PS-2 Vendor Onboarding** (file in repo: `asa-case-study-candidate (2) (1) (1) (1).pdf`).

**Deadline:** User stated submission is tomorrow (treat as 21 Oct 2026 unless the hiring email says otherwise).

**Planning limits already respected:** no application implementation in the planning pass; no new Supabase project; no MCP writes; no secrets in git.

---

## 1. Verified assignment requirements vs recommendations

### Verified from the candidate PDF (must satisfy)

- Build a **working** process, not a mock: vendor submission in → process runs → output out.
- Output status is **approved**, **pending**, or **rejected**, with **reasoning visible**.
- For anything not approved, **communicate what is needed next**.
- Candidate defines **2–4 realistic edge cases**.
- UI: **live run view** (each stage as it executes) and a **dashboard** (history, status, outputs).
- Submit **two things**: a **live runnable URL** and a **5-minute demo video**.
- Synthetic test inputs are allowed (forms, JSON, PDFs you create).
- Any stack except Zamp/Pace.

### Recommendations (not assignment mandates)

GPT-chosen stack, India-first demo policy, Supabase history, optional Gemini, optional PDFs, skills, Ruff/pytest.

### Definition of done (P0)

- Operator can complete onboarding from a **form** (or one-click seeded form fixture) with **no PDF**.
- PDF attachment is an **optional extra check**, not required for Approved.
- Hosted Streamlit URL runs happy path + edge cases.
- pytest covers fixture statuses/reason codes **without** Gemini and **without** requiring a PDF on the happy path.
- README covers install, secrets, run, test, SQL apply, deploy.
- No secrets, no real PII, no false “GSTN/bank verified” claims.

---

## 2. Scope

### P0 — must ship

- Streamlit app with form intake, live run, dashboard.
- Seeded fictional vendors loadable into the form in one click.
- Deterministic rules → Approved / Pending / Rejected + follow-up text.
- Supabase persistence on existing `vendorflow-dev2` when configured; session fallback otherwise.
- Optional PDF upload / bundled PDF on a fixture: PyMuPDF text extract; if present, extra consistency checks.
- Live `st.status(..., type="step")` timeline.
- README, pytest, Ruff.

### P1 — after P0 acceptance

- Gemini candidate extraction from PDF text (and/or follow-up rewrite). `GEMINI_ENABLED` default **false**.
- Extracted-text / document panel.
- `review_actions` (human note).
- Dashboard search/filter.

### P2 — defer

OCR, n8n, multi-agent, NL assistant, spend analytics, registry APIs, outbound email.

### Non-goals

Production KYC/AML, real government/bank APIs, login, sending email, branding.

---

## 3. Architecture and stack (locked)

**Locked stack:** Python 3.14 (local), Streamlit `>=1.52`, Pydantic, pure-Python rules, Supabase (`vendorflow-dev2`, `ap-south-1`), PyMuPDF (optional documents), Gemini (optional helper), pytest, Ruff, python-dotenv / Streamlit secrets. Optional Faker for extra junk data only — **not** for graded fixtures.

```text
Form (primary) ─┐
                ├─► Pydantic ─► Rules ─► Status + follow-up ─► UI + persist
Optional PDF ───┘     ▲
                      └── P1 Gemini may propose candidates; never sets status
```

**Python on Cloud:** try 3.14 in Streamlit Community Cloud Advanced settings. If install fails, redeploy 3.13 or 3.12. Pin `streamlit>=1.52`. Also ship `requirements.txt` (Cloud). `pyproject.toml` is optional metadata.

**Why form-primary:** the assignment FAQ allows forms/JSON. A form is the reliable interview path. PDFs show “supporting documents” from PS-2 without making the core demo depend on parsing.

### Suggested layout (create files when implementing, not empty shells)

```text
app.py
requirements.txt
.env.example
src/vendorflow/
  models.py
  policy.py
  pipeline.py
  pdf_extract.py      # no-op path when no file
  persistence.py
  fixtures.py         # canonical fictional vendors
  integrations/gemini.py
tests/
  test_models.py
  test_policy.py
  test_pipeline.py
  test_pdf_extract.py
  fixtures/pdfs/      # optional bundled PDFs
supabase/migrations/
docs/                 # this plan + decisions + demo script
.agents/skills/
```

---

## 4. How to create vendor details (do this; do not use real companies)

You do **not** need real vendors, GSTN downloads, or bank letters. The assignment says create your own test inputs.

### 4.1 Three ways the operator enters a vendor

1. **Demo fixtures (primary for recording and interview)**  
   Codex hardcodes 4 fictional vendors in `fixtures.py`. The UI has buttons: “Load happy path”, “Load bank-name mismatch”, etc. Clicking fills the **form widgets**. Then Run. No typing during the 5-minute video.

2. **Manual form (primary product path)**  
   Same fields, empty by default. The operator (or interviewer) types values. Run uses whatever is in the form. This is how you prove it is not only a canned JSON dump.

3. **Optional PDF**  
   After the form is filled, attach a PDF **or** a fixture may include a path to a bundled PDF. If no file: document checks are `not_checked` and **do not block Approval**. If a file is present: extract text and run document checks.

Do not scrape registries. Do not use real PAN/GSTIN/account numbers.

### 4.2 Form fields (India demo policy)

| Field | Widget | Validation (demo) |
|---|---|---|
| Legal name | text | required |
| Country | select, default `IN` | required; P0 only fully rules `IN` |
| State code | text, 2-digit GST state (e.g. `29`) | required for IN |
| GSTIN | text | format regex; **not** GSTN lookup |
| PAN | text | `AAAAA9999A`-style regex |
| Bank account name | text | required; compared to legal name |
| Bank account number | text | required, digits-only length band |
| IFSC | text | `AAAA0XXXXXX`-style regex |
| Contact email | text | email |
| Vendor category | select (goods / services / both) | required |
| PDF | `st.file_uploader` type pdf | **optional** |

### 4.3 Inventing fictional identifiers

Prefix every legal name with `VF-DEMO` so nothing looks like a real supplier.

Use **format-shaped** IDs. P0 GSTIN/PAN/IFSC checks are **regex/length**, not government checksum verification (checksum is optional later). If you add checksums, generate IDs that satisfy them in the fixture factory — do not hand-wave.

**Canonical P0 fixtures** (Codex may tweak strings; keep expected statuses stable):

**`happy_acme` → Approved (form only; PDF optional)**  
- Legal name: `VF-DEMO Acme Packaging Pvt Ltd`  
- Country: `IN`, state: `29` (Karnataka)  
- GSTIN: `29AABCU9603R1ZM` (treat as fictional demo string; if regex is stricter, generate a matching fake)  
- PAN: `AABCU9603R`  
- Bank account name: `VF-DEMO Acme Packaging Pvt Ltd`  
- Account: `501234567890`  
- IFSC: `HDFC0001234`  
- Email: `accounts@vf-demo-acme.example`  
- Category: goods  
- PDF: none required. Optional matching PDF may be attached in a second demo click.

**`edge_bank_name_mismatch` → Pending**  
Same as happy path except bank account name `Ramesh Kumar`. Reason `NAME_VS_BANK_ACCOUNT`. Follow-up: ask for a cancelled cheque / account letter matching legal name.

**`edge_gstin_format` → Pending**  
GSTIN `29-INVALID`. Reason `GSTIN_FORMAT`. Do **not** call this fraud. Follow-up: provide a 15-character GSTIN.

**`edge_blocklist` → Rejected**  
Legal name `VF-DEMO Northstar Holdings Pvt Ltd` (on `DEMO_BLOCKLIST`). Reason `BLOCKLIST_MATCH`. UI: “Demonstration blocklist — not a government sanction list.”

**Optional document fixtures (added feature, not required for P0 happy path):**

- `optional_pdf_match` — happy form + PDF whose text contains legal name and GSTIN. Status still Approved; extra checks `pass`.
- `optional_pdf_conflict` — happy form + PDF text with a different GSTIN. **Pending** `DOCUMENT_VS_FIELDS`.

If time is short, generate the two PDFs with PyMuPDF in a one-off `scripts/make_demo_pdfs.py` that writes a single page of fixture text, commit the PDFs, then stop. Do not spend time on letterhead design.

Optional Faker: only to fill “create random vendor” for dashboard volume. Never let Faker change graded fixture expected outcomes.

---

## 5. Status rules

Label the UI: **Demonstration policy — not a legal, tax, or bank verification product.**

**Check outcomes:** `pass` | `fail` | `needs_review` | `not_checked`.

**Aggregation:**

1. **Rejected** only if `BLOCKLIST_MATCH`.
2. Else **Pending** if any **in-scope** check is `fail` or `needs_review`.
3. Else **Approved**. Summary must say no GSTN/bank registry was queried.

**In-scope without PDF:** required fields, GSTIN/PAN/IFSC/email format, name vs bank, GSTIN state vs `state_code`, duplicate vendor, blocklist.

**In-scope only when a PDF is provided:** `DOCUMENT_TEXT_READABLE`, `DOCUMENT_VS_FIELDS`.  
When no PDF: those checks are `not_checked` and are **not** in-scope for aggregation.

Missing/ambiguous form data → Pending with a specific follow-up. Never invent verification.

**Duplicate:** same normalized legal name or GSTIN in prior runs (DB + session), excluding current id → Pending `DUPLICATE_VENDOR`.

Follow-up: templates keyed by reason code. Do not send email. P1 Gemini may rewrite templates.

---

## 6. Pipeline and live UI

Stages (`st.status`, `type="step"`):

1. Intake received (form snapshot)
2. Optional document extraction (skip with “no document attached” if none)
3. Field validation
4. Cross-field consistency
5. Duplicate / blocklist
6. Decision + follow-up
7. Persist

Short sleep (≤0.4s/step) is OK for the interview. Logic must not depend on it.

**Tabs:** Overview counts · New run (fixtures + form + optional uploader) · Live run · History.

Do not use color as the only status signal.

---

## 7. Persistence (user applies SQL)

Existing project only: **vendorflow-dev2**. Codex commits SQL; user pastes into the Supabase SQL Editor. No MCP writes. No new project.

P0 tables:

- `vendors` — `id`, `legal_name`, `gstin`, `pan`, timestamps  
- `onboarding_submissions` — fields, `vendor_id`, `status`, `summary`, `reason_codes`, timestamps  
- `vendor_documents` — filename, doc type, parse status, extracted text, `submission_id` (row omitted when no PDF)  
- `validation_results` — check_id, outcome, reason_code, human_readable_reason, evidence_reference, follow_up_action  
- `processing_runs` — start/end, final status, error  
- `run_events` — timeline  

P1: `review_actions`.

Enable RLS. Prefer **anon** key with insert/select on these tables (synthetic data). Do **not** put the service role in Streamlit secrets unless anon insert cannot work. Document that this is demo-insecure.

Fallback: `st.session_state` + fixture catalog. Banner if DB is down. Never claim a save that failed.

---

## 8. Gemini (P1)

Ship `integrations/gemini.py` with `GEMINI_ENABLED=false`. When true: extract candidates from PDF text into Pydantic, or draft follow-up from reason codes. Timeouts/malformed output → `not_checked` + templates. Gemini never sets status.

Confirm the current Google GenAI Python package name from current docs before pinning.

---

## 9. Tests and P0 acceptance

Commands: `ruff check src tests app.py` · `pytest -q`

Must pass with Gemini off:

- Form models reject missing required fields.
- Four form fixtures: exact status + reason codes (`happy_acme` has no document reasons).
- Aggregation never Approves with a failed in-scope check.
- Only blocklist Rejects.
- No-PDF path does not emit document `fail`.
- With a conflicting PDF fixture, Pending `DOCUMENT_VS_FIELDS` (if that fixture is implemented).
- Persistence exception → fallback, no crash, no auto-approve.

**Do not start P1 until:** form happy path Approved; three form edge cases; live steps; dashboard; hosted URL; README; optional PDF does not break form-only.

---

## 10. Setup, secrets, deploy, fallbacks

`.env.example` keys only (no values): `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `GEMINI_API_KEY`, `GEMINI_ENABLED=false`, `GEMINI_MODEL`.

Local: Python 3.14 venv, `pip install -r requirements.txt`, copy `.env`, `streamlit run app.py`.

Deploy: public GitHub → Streamlit Community Cloud, `app.py`, secrets in Advanced settings. Confirm the URL in a browser. Localhost is not a valid submission.

Fallbacks: Supabase down → session; Gemini off → skip; PDF parse fail → Pending on **that run only**; Cloud Python fail → pin Streamlit, retry 3.12.

---

## 11. Risks

- Cloud Python 3.14 wheel issues → fallback 3.13/3.12.  
- SQL not applied yet → fallback banner.  
- `vendorflow-dev2` schema not inspected during planning.  
- PyMuPDF on Cloud → optional path; form-only demo still works.  
- Exact hiring-email timestamp not in the PDF.

---

## 12. Build sequence for Codex

1. Hygiene: `requirements.txt`, `.env.example`, package layout (planning docs already exist).  
2. Models + `fixtures.py` (form vendors) + policy + tests.  
3. Pipeline without I/O; PDF extract module with a no-file path.  
4. Streamlit form + fixture buttons + live steps + in-memory history.  
5. SQL + persistence + dashboard.  
6. Optional bundled PDFs + document checks.  
7. ruff/pytest; user applies SQL; local smoke.  
8. Deploy URL; record demo; freeze.  
9. P1 Gemini only if 1–8 are green.

### First five implementation tasks (exact order)

1. `requirements.txt`, `.env.example`, Pydantic intake/check/decision models, tests for missing/invalid form fields.  
2. `fixtures.py` with the four form vendors + `policy.py` + pytest for expected statuses/reason codes.  
3. `pipeline.py` emitting the seven stages; document stage records `not_checked` when no file.  
4. `app.py`: fixture load-into-form buttons, editable form, Run, live `st.status` steps, in-memory persist.  
5. SQL migrations + `persistence.py` (Supabase + fallback) + dashboard.

---

## 13. Five-minute demo outline

See `docs/DEMO_SCRIPT.md`. Use real on-screen outcomes only.

---

## 14. Submission checklist

- Live URL loads; form happy path runs without a local PDF.  
- Video ≤ 5 minutes.  
- Email coordinator: URL + video.  
- SQL only on `vendorflow-dev2`.  
- No secrets in git.

---

## 15. `.gitignore` (Codex must create this file; Plan mode could not write non-markdown)

```
.env
.env.*
!.env.example
.streamlit/secrets.toml
.venv/
venv/
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.ruff_cache/
.mypy_cache/
dist/
build/
.DS_Store
Thumbs.db
.idea/
.vscode/
*.log
.coverage
htmlcov/
```

## 16. Open items that do not block coding

- Exact deadline timezone from the hiring email.  
- Enable Gemini only after P0.  
- User must paste SQL and Streamlit secrets when Codex has produced the migration and `.env.example`.
