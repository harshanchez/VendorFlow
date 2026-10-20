# VendorFlow — Implementation Plan Draft for Codex

**Purpose:** Working planning brief for Codex to inspect, challenge, and turn into the final implementation plan.

**Project:** Zamp AI — AI Solutions Associate take-home assignment  
**Chosen problem statement:** PS-2 — Vendor Onboarding  
**Primary coding agent:** OpenAI Codex  
**Deadline:** Tuesday, 20 October 2026, end of day (confirm the exact submission timezone from the assignment email)  
**Current status:** Local workspace and developer tooling have been prepared; the application has not yet been implemented.

> **Codex instruction:** Treat this file as a strong draft, not as unquestionable truth. Inspect the actual assignment brief if it is available in the repository or conversation attachments, inspect the current repository and active project configuration, identify any discrepancies, and then produce a clear final plan. Do not start implementing the application during this planning pass.

---

## 1. Assignment outcome

Build a real, runnable vendor-onboarding process that takes a vendor submission through validation and a decision, explains the outcome, and gives follow-up instructions for cases that cannot be approved.

The demonstrated workflow must support three statuses:

- **Approved** — all required checks for the demo policy pass, with adequate evidence.
- **Pending** — information is missing, inconclusive, conflicting, invalid, or requires human review.
- **Rejected** — only when an explicitly documented hard-block rule is supported by sufficient evidence.

The submission must demonstrate a working process, not only a static UI. It should provide a live view of an individual run and a dashboard/history of previous runs. Include at least 2–4 realistic edge cases and a demo of no more than five minutes. Synthetic test data is allowed.

**Source-of-truth check:** Before finalizing the plan, compare each of the above requirements with the original assignment PDF/email. Quote or paraphrase only what the brief supports. Record any requirement that cannot be confirmed as an open question rather than inventing it.

## 2. Product framing

Working product name: **VendorFlow**.

Target demo context: India-first vendor onboarding for an internal procurement/operations team. This is a demonstration policy, not a complete tax, banking, identity, AML, or legal compliance product.

Primary user journey:

1. Operations user submits a vendor and supporting details/documents.
2. The app validates required fields and input formats.
3. The app extracts information from documents if that capability is implemented and available.
4. A deterministic rules engine compares the submitted fields and available evidence.
5. The app records the decision, evidence, reasons, follow-up actions, and processing events.
6. The operations user sees a live run summary and can inspect the vendor’s status and history.
7. A human can review exceptions; follow-up text can be generated as a draft, but should not be automatically sent.

## 3. Planning principles

1. **Working end-to-end workflow beats feature count.** A stable submission → validation → status → audit history flow is the top priority.
2. **Rules decide; AI assists.** Gemini may extract fields or flag ambiguity. It must not make the final approval/rejection decision.
3. **Keep uncertainty visible.** A missing, unreadable, conflicting, or unverified field should not silently be treated as valid.
4. **Use deterministic fixtures.** Edge cases must have controlled input data and known expected statuses.
5. **Use honest evidence.** Never claim a vendor, tax registration, bank account, or identity was externally verified unless an actual authorized source was queried successfully.
6. **Minimize dependencies.** External integrations are optional until the core is working and tested.
7. **No real personal or financial data.** Demo records, tax identifiers, account details, and documents must be fictional.
8. **No false production claims.** Label rules, data, and external checks as demo/synthetic wherever appropriate.
9. **Prefer inspectable code.** Use simple functions and explicit decision rules instead of elaborate agent frameworks.
10. **Codex is the primary agent.** Use the repository’s `AGENTS.md` and skills for shared instructions. Cursor’s agent is not part of the planned workflow.

## 4. Proposed technology choices — confirm before building

These are defaults to validate against the assignment and package compatibility. Codex should use Context7 to check current documentation for any dependency whose API/configuration matters.

- **Python 3.14** for the application runtime. Python 3.13/3.14 are installed. Do not upgrade to Python 3.15 just for perceived speed; only change runtime if a real compatibility need is demonstrated.
- **Streamlit** for the UI, live processing view, vendor list, status filters, and run/history details.
- **Pydantic** for input and extracted-field validation.
- **Pure Python deterministic rules** for policy evaluation and final status decisions.
- **Supabase PostgreSQL** for persistent records, processing runs, validation results, and review/audit events, provided that integration can be completed safely within the deadline.
- **Gemini API** as an optional extraction/ambiguity helper, not a decision-maker. The user has successfully made a Gemini API call; still, handle quota, network, and model failures gracefully.
- **PyMuPDF** for text extraction from text-based PDFs only if document uploads are included in the MVP.
- **pytest** for tests, **Ruff** for lint/format checks, and **Faker** or static fixtures for fictional records.
- **python-dotenv** or Streamlit secrets for local/deployed configuration. Secrets must not be hard-coded.

Do not make OCR, n8n, multi-agent orchestration, broad spend analytics, email sending, or live checks against public registries MVP requirements. Only add a stretch feature after all P0 acceptance criteria pass.

## 5. Scope priority

### P0 — Must work before submission

- A runnable app with an obvious entry point and setup instructions.
- Vendor submission form or a clear way to run known demo submissions.
- Structured input validation and deterministic status rules.
- Visible result: `Approved`, `Pending`, or `Rejected`, with reason(s) and next action(s).
- A repeatable successful/happy-path scenario.
- At least 2–4 deliberate edge cases, with stable expected outcomes.
- Live/current-run result view and persistent or clearly functional run history/dashboard.
- Audit trace for a run: inputs/field checks, rule outcomes, status, timestamps, and follow-up.
- Useful failure messages and a way to keep the demo usable if Gemini or Supabase is unavailable.
- README with install, configure, run, and test commands.
- A five-minute demo route/script and final submission checklist.

### P1 — Add only after P0 is stable

- Gemini-assisted field extraction from text extracted from a PDF.
- A document viewer or extracted-field review panel.
- Human review action recorded in history.
- Search and filtering by status/name/submission ID.
- Better event/timeline presentation in the live-run view.

### P2 — Stretch / defer unless everything else is done

- OCR for scanned files.
- n8n orchestration.
- AI natural-language dashboard assistant.
- Spend analytics requiring purchase-order/payment data.
- External registry APIs or actual bank verification.
- Automatic outbound email.
- Complex multi-agent design.

## 6. Proposed workflow and decision policy

Codex must make the policy explicit and testable in code. Proposed starting matrix:

| Check/outcome | Suggested status effect | Required user-facing explanation |
|---|---|---|
| Required field missing | Pending | Identify field and how to provide it |
| Required document missing | Pending | Name the missing document and upload/review action |
| Tax ID or identifier format invalid | Pending | Explain format failure; do not call it proof of fraud |
| Document text unreadable or extraction fails | Pending | Request a clearer document or manual review |
| Extracted value conflicts with submitted value | Pending | Show which fields conflict and require review |
| Bank account name mismatch | Pending | Manual review; do not assert the account is invalid |
| Potential duplicate vendor | Pending | Link or identify the possible match and request reviewer decision |
| External verification unavailable or not integrated | Pending or “not checked” within the validation detail | State plainly that no external verification was performed |
| Matches an explicitly configured synthetic block-list fixture | Rejected only if the demo policy clearly defines this as a hard block | Show the exact synthetic rule/evidence; label it as demo data |
| All required inputs/evidence pass demo policy | Approved | Summarize passing checks and clarify that this is demo-policy approval |

A severe issue should not be converted into a rejection merely to make the demo look intelligent. When evidence is ambiguous, use Pending.

Suggested validation result shape:

- `check_id`
- `check_name`
- `outcome` (for example `pass`, `fail`, `needs_review`, `not_checked`)
- `severity`
- `reason_code`
- `human_readable_reason`
- `evidence_reference` (file/field identifier; no unnecessary raw sensitive content)
- `follow_up_action`
- `created_at`

Suggested top-level outcome shape:

- `submission_id`
- `vendor_id` if assigned
- `status`
- `decision_reason_codes`
- `summary`
- `required_follow_up[]`
- `validation_results[]`
- `processing_run_id`
- timestamps and processing outcome metadata

Codex should simplify these fields where appropriate; this is a proposed contract, not a mandate to overbuild.

## 7. Synthetic fixtures and required edge cases

Plan a small controlled fixture suite, ideally 8–12 submissions total, including a clear happy path and at least 2–4 edge cases. More test records are not inherently better.

Recommended cases:

1. **Happy path:** all required demo fields/documents consistent → Approved.
2. **Missing required document:** → Pending, with a precise upload request.
3. **Invalid tax ID format:** → Pending, not an accusation of fraud.
4. **Bank/vendor-name mismatch:** → Pending/manual review.
5. **Possible duplicate:** → Pending and identify the possible matching record.
6. **Unreadable or conflicting document text:** → Pending.
7. **Synthetic hard-block match:** → Rejected only if the chosen policy explicitly supports it and the fixture documents why.

Select the smallest 2–4 edge cases that can be demonstrated clearly within five minutes. Additional cases can remain automated tests. Each fixture must define expected status and expected reason codes, and should be repeatable regardless of API availability.

Do not use real vendor PII, real PAN/GSTIN values attributable to people/businesses, or real bank account numbers. Clearly fictionalize and/or use format-invalid synthetic identifiers where suitable.

## 8. UI plan

Keep the UI compact and reviewer-oriented. Proposed pages/tabs:

1. **Overview:** counts by Approved/Pending/Rejected, recent runs, and processing summary. Avoid fabricated performance metrics.
2. **New submission / Demo runs:** form and/or clearly labeled seeded scenarios.
3. **Live run detail:** progress/events, field checks, evidence notes, final status, rationale, follow-up instructions, and run ID.
4. **Vendor/submission history:** search/filter and a detail drawer/page with previous runs and review events.

The app must stay understandable if API calls fail. Display loading/error states honestly. Do not simulate real-time verification that did not happen. Keep status text accessible; do not rely on color alone.

## 9. Data persistence plan

Codex should propose the minimum persistent schema needed for the demonstrated workflow and place SQL migrations in the repository. Possible tables:

- `vendors` — canonical synthetic vendor identity/profile.
- `onboarding_submissions` — each submission and submitted fields.
- `vendor_documents` — document metadata, parse/extraction status, safe references; avoid storing sensitive raw content unless truly needed.
- `validation_results` — individual check results and rationale.
- `processing_runs` — status, start/end time, final outcome, failure state.
- `run_events` — timeline events for processing and human review.
- `review_actions` — explicit reviewer decisions/notes, if implemented.

Start with the smallest schema that meets P0. Avoid introducing all tables if a simpler relational model works. Define primary keys, foreign keys, timestamps, status constraints, and useful indexes. Establish Row Level Security (RLS) and least-privilege access if appropriate to the selected app architecture.

**MCP safety boundary:** Supabase MCP is configured to be project-scoped and read-only. Use it only to inspect the project/schema and current documentation. Do not use it to create tables, execute migrations, change settings, or perform writes. Create version-controlled SQL migration files locally. If a schema needs to be applied, document a safe, human-reviewed method (for example via the Supabase SQL Editor or an explicitly authorized CLI workflow); ask for approval before applying anything remotely.

Do not expose database passwords, service-role keys, access tokens, or `.env` values in files, logs, prompts, or screenshots. Keep secrets out of Git history. Prefer the least-privileged viable runtime integration. If service credentials are proposed, document why they are needed and ensure they remain server-side only.

## 10. Gemini integration and fallbacks

Gemini can optionally:

- Extract candidate values from extracted document text into a strict Pydantic schema.
- Return confidence/ambiguity notes for human review.
- Produce draft follow-up wording from known reason codes.

Gemini must not:

- Make the final approval/rejection decision.
- Invent a verification that was not performed.
- Treat missing evidence as a pass.
- Send email/messages automatically.
- Receive secrets or unnecessary sensitive document data.

Validate every model response against a schema. If the response is malformed, the API is unavailable, quota is exhausted, or the result is ambiguous, fall back to deterministic rules and return Pending where needed. The demo must still run if Gemini is disabled. Use a configuration flag such as `GEMINI_ENABLED`; never hard-code credentials.

If integrating Gemini would threaten the P0 schedule, demonstrate deterministic fixtures first and defer live Gemini calls to P1.

## 11. Repository structure proposal

Codex should refine this only as needed; avoid empty scaffolding:

```text
VendorFlow/
├── AGENTS.md
├── README.md
├── .gitignore
├── pyproject.toml
├── .env.example
├── app.py
├── src/
│   └── vendorflow/
│       ├── __init__.py
│       ├── models.py
│       ├── policy.py
│       ├── pipeline.py
│       ├── persistence.py
│       ├── integrations/
│       │   └── gemini.py
│       └── fixtures.py
├── tests/
│   ├── test_models.py
│   ├── test_policy.py
│   ├── test_pipeline.py
│   └── fixtures/
├── supabase/
│   └── migrations/
├── docs/
│   ├── IMPLEMENTATION_PLAN.md
│   ├── DECISIONS.md
│   └── DEMO_SCRIPT.md
└── .agents/
    └── skills/
        ├── vendorflow-planning/SKILL.md
        ├── vendor-onboarding-policy/SKILL.md
        ├── python-streamlit-engineering/SKILL.md
        ├── supabase-safe-development/SKILL.md
        └── vendorflow-qa-and-demo/SKILL.md
```

Do not create source-code files during this planning pass. The tree is a proposal for planning, not an instruction to create empty directories/files beyond the requested planning artifacts.

## 12. Test strategy and acceptance criteria

At minimum, the final implementation should be able to demonstrate:

- Pydantic validation rejects malformed required input cleanly.
- Every documented fixture produces its expected status and reason codes.
- No missing, invalid, or ambiguous check can accidentally pass.
- Only the explicit synthetic hard-block fixture can trigger a demo rejection.
- Gemini timeout/malformed response and Supabase timeout/connection errors are handled without a crash or false positive approval.
- Run status, validation results, and important state changes are persisted when Supabase is configured.
- A local fallback or seeded-demo mode allows the UI and deterministic workflow to be demonstrated if remote services are unavailable.
- The README setup/run/test commands work in a clean environment.
- Ruff and pytest run successfully.
- The application does not expose secrets or real personal/banking data.

Codex should define exact commands and a compact acceptance checklist in the final plan. Do not claim a test passes until it has actually been run.

## 13. Deployment and demo

Propose the simplest deployment approach that can realistically be completed and verified before the deadline. Streamlit Community Cloud is a candidate if compatible and deployable in time; otherwise, a tested local run with a clean documented startup may be a fallback, but the final plan must explicitly check that this satisfies the assignment’s required submission format.

Never claim a live link exists until deployment succeeds and the URL is tested. Keep deployment secrets in the hosting provider's secret settings, not in source control.

Five-minute demo outline:

- **0:00–0:30:** Introduce the workflow, user problem, and scope.
- **0:30–1:00:** Briefly explain the architecture and deterministic decision boundary.
- **1:00–2:00:** Submit/show the happy path and inspect passing checks/status.
- **2:00–3:30:** Run 2–3 edge cases, focusing on Pending/Rejected rationale and follow-up.
- **3:30–4:30:** Show run history, validation evidence, and audit trail.
- **4:30–5:00:** Explain limitations, human review, and what was intentionally not claimed.

Use only real observed outcomes during recording. Do not fabricate processing-time improvements, accuracy metrics, or production capabilities.

## 14. Execution sequence — proposed

Given the deadline is 20 October 2026, plan from the actual time remaining when this draft is reviewed. If the time budget is tight, reduce scope rather than pushing unverified features into the demo.

1. **P0-A — Confirm requirements and lock scope:** compare assignment brief; record assumptions and acceptance criteria.
2. **P0-B — Create repository guidance:** `AGENTS.md`, `.gitignore`, skill files, decisions, and the final plan.
3. **P0-C — Implement typed models and deterministic rules:** include unit tests and stable synthetic fixtures.
4. **P0-D — Build the basic Streamlit submission/live-result/history UI:** prove the whole core flow locally.
5. **P0-E — Add persistence:** create reviewed migration files; apply through a safe, explicitly approved route; verify reads/writes from the app using appropriate runtime credentials.
6. **P0-F — Exercise edge cases and resilience:** run pytest/Ruff, verify failures and fallbacks.
7. **P1 — Gemini-assisted extraction only if P0 works:** keep it optional and observable.
8. **P0-G — Deploy/verify the submission path and record the five-minute demo.**
9. **Final freeze:** keep time for regression testing, recording, and submission; do not add features after the freeze unless fixing a blocker.

Codex should reorder or compress these tasks based on its inspection, and assign rough timeboxes with explicit stop conditions. The assignment submission is the ultimate deliverable; do not let tooling setup displace implementation and testing time.

## 15. Expected outputs of Codex’s planning pass

Codex must inspect the repository and then:

1. Validate this draft against the assignment brief and current repository state.
2. Produce `docs/IMPLEMENTATION_PLAN.md` as the concise, final source of truth for implementation.
3. Produce `docs/DECISIONS.md` including accepted decisions, trade-offs, and unresolved issues.
4. Produce a concise root `AGENTS.md` for Codex, with no dependency on Cursor Agent.
5. Create the five skill files named in Section 11, with useful and scoped instructions.
6. Ensure `.gitignore` protects secrets, virtual environments, caches, and generated files without hiding source/tests/migrations/docs.
7. Keep this draft as `IMPLEMENTATION_PLAN_DRAFT.md` or otherwise preserve it as a reference; do not silently overwrite it.
8. Report discrepancies, unknowns, risky assumptions, final P0 scope, the first five coding tasks, and any decision requiring user approval.
9. Confirm that it did not implement application code, install dependencies, modify Supabase, or deploy anything during this pass.

### Planning-pass boundaries

- Do not implement the application in this pass.
- Do not install dependencies or upgrade Python.
- Do not execute database migrations or writes through MCP.
- Do not use web scraping or claim external verification integrations.
- Do not create or modify anything outside the repository, except to read available assignment materials.
- If a critical assignment requirement is unavailable, ask a specific question or mark it as unresolved; do not invent an answer.

---

## Prompt to give Codex after adding this file to the repository

> Read `IMPLEMENTATION_PLAN_DRAFT.md` in full. Inspect the current repository, existing configuration, and the original Zamp AI assignment brief if available. Use Context7 to verify current documentation for any framework/configuration details that materially affect the plan. Do not use Cursor Agent. Refine the draft into the final `docs/IMPLEMENTATION_PLAN.md`, and create/update `AGENTS.md`, `.gitignore`, `docs/DECISIONS.md`, and the five `.agents/skills/*/SKILL.md` files specified in the draft. Challenge scope and feasibility against the 20 October 2026 deadline; prefer the smallest credible end-to-end submission. Keep database access read-only during this planning phase. Do not implement app code, install dependencies, apply migrations, change remote settings, or deploy. At the end, list files changed, unresolved questions, the first five implementation tasks, and confirm all boundaries were respected. If a requested file already exists, inspect it and make a careful revision rather than blindly overwriting it.
