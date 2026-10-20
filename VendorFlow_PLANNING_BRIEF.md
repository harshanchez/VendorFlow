# VendorFlow — Planning Brief

**Purpose:** Input brief for a planning agent to produce a strong, implementation-ready plan. This is context and a set of constraints, **not a prescribed architecture or mandatory repository structure**.

**Assignment:** Zamp AI — AI Solutions Associate take-home case study  
**Chosen problem statement:** PS-2 — Vendor Onboarding  
**Primary implementation agent after planning:** OpenAI Codex  
**Deadline:** Tuesday, 20 October 2026, end of day; confirm the exact timezone from the assignment communication. Treat this as time-critical and plan for a credible submission today.

## 1. The outcome we need

Build a real, runnable vendor-onboarding workflow that can accept a submission, assess its information and supporting evidence, assign a status, explain the decision, and tell the operator or vendor what should happen next when it cannot be approved.

The submission should demonstrate an actual working process, not just static mockups. It should include a useful live/current-run view and a dashboard or history view. Use a small set of realistic, controlled edge cases. Synthetic data is allowed and preferred for the demonstration.

The assignment's authoritative wording and exact submission requirements take precedence over this brief. Before finalizing the plan, inspect the original assignment file if it is available. Clearly label anything that cannot be verified.

## 2. Required business behavior

The visible outcome should be one of:

- **Approved:** the submission satisfies the explicitly defined demo policy and has sufficient evidence for the checks actually performed.
- **Pending:** information is missing, inconsistent, invalid, ambiguous, unavailable, or requires human review. Explain the issue and the next action.
- **Rejected:** use only where a documented hard-block rule and sufficient evidence justify it. Do not force rejection merely to make the demo appear smarter.

For every result, show human-readable reasoning. For anything not approved, give clear follow-up or review instructions. Record enough run history to make the process inspectable and credible.

Treat all policy as a **demonstration policy**, not a production-grade legal, tax, banking, identity, AML, or compliance engine.

## 3. Product and operating context

A reasonable starting point is an India-first demonstration for an internal procurement or operations team, but evaluate whether this is the simplest defensible scope for the assignment.

A likely user journey is: submit vendor details and supporting files → validate fields/evidence → evaluate explicit rules → show status and reasons → record the run → inspect the dashboard/history → provide a review or follow-up action for exceptions. Refine this journey when you see a clearer, simpler solution.

The working project name is **VendorFlow**. Keep naming easy to change; do not over-invest in branding.

## 4. Architecture ideas to evaluate, not blindly follow

The current preference is a small Python application with a lightweight UI, structured validation, explicit deterministic business rules, persistent history if feasible, and optional AI assistance. A plausible starting stack is:

- Python 3.14 (already installed; Python 3.13 is also present).
- Streamlit for a compact UI.
- Pydantic for structured validation.
- A straightforward Python rules engine for status decisions.
- Supabase/PostgreSQL for persistence, if it can be integrated and safely deployed within the deadline.
- Gemini API as an optional helper for extracting candidate fields or identifying ambiguity, never as the final approver/rejector.
- PyMuPDF only if text-based PDF processing materially improves the MVP.
- pytest and Ruff for verification.

These are preferences rather than requirements. The planner should test the assumptions, consider simpler alternatives when they reduce delivery risk, and explain meaningful deviations. Avoid introducing a framework, service, or dependency solely because it is available.

The user has a successful Gemini API call and has created a Supabase development project named `vendorflow-dev2` in Mumbai (`ap-south-1`). Supabase MCP has been configured in Codex as project-scoped and read-only and appeared in MCP settings; successful tool invocation should be verified before relying on it. **Do not create another Supabase project.** The setup also includes Python, Pylance, Ruff, and Context7 for Codex. Codex is the implementation agent; the user does not plan to rely on Cursor Agent for coding. Cursor Plan Mode is being used for an independent plan critique/refinement only.

## 5. Important safety and evidence rules

- Use fictional vendors, identifiers, documents, and account details. Do not use real personal, tax, or banking data.
- Missing, unreadable, conflicting, malformed, or uncertain information should normally lead to Pending with a specific follow-up or human-review reason.
- A format check is not external verification. Never claim that a tax registration, bank account, identity, or vendor was verified unless a real, authorized integration actually performed that check.
- Do not scrape CAPTCHA-protected registries or invent external APIs or capabilities.
- Gemini can suggest candidate extracted values or draft follow-up text. Validate its output and treat ambiguity as uncertainty. It must not independently decide approval/rejection, and the core workflow must remain usable when Gemini is unavailable.
- Never hard-code or expose API keys, OAuth tokens, database passwords, service-role keys, or other secrets. Keep secrets out of Git and docs.
- Treat Supabase MCP as read-only. Use it only for inspection and documentation. Do not apply schema changes, migrations, or writes through MCP. If remote database changes are necessary, create migration files locally and propose a safe, human-reviewed application step.
- Label synthetic fixtures and demo-only checks honestly. Do not fabricate accuracy, savings, verification, or performance metrics.

## 6. Priority and deadline

The most important outcome is a stable end-to-end demonstration. Prioritize a smaller feature set that runs reliably over extra features that risk completion. The plan should explicitly separate:

- **Essential:** what must work to satisfy the brief.
- **Useful next:** features worth adding only after the core works.
- **Stretch/defer:** features that should be excluded unless the essential scope is complete and tested.

Potential stretch items include OCR, n8n orchestration, multiple cooperating agents, a natural-language dashboard assistant, broad spend analytics, external registry APIs, automatic outbound email, and advanced workflow orchestration. The planner may recommend one only if the assignment strongly warrants it and the remaining time supports it.

## 7. What the planning agent should work out

Use judgment and inspect evidence rather than treating the following as a fixed checklist or fixed file layout:

- The smallest credible end-to-end architecture and user journey.
- The appropriate separation between input validation, evidence extraction, business rules, status decisions, persistence, and UI.
- Whether uploaded documents are essential to the MVP or whether structured submission plus clearly simulated/controlled evidence is more reliable.
- The simplest defensible data model, audit trail, and migration approach.
- How a demo runs locally and, if feasible, how it is deployed; include a fallback if a hosted database/API is unavailable.
- A small but persuasive set of synthetic scenarios and deterministic tests.
- Useful failure states, observability, security, and secret handling.
- What must be demonstrated in a five-minute video, with honest claims.
- Dependency, configuration, compatibility, and deployment risks, alongside realistic fallbacks.
- Which assumptions require user approval before implementation.
- A repository structure that fits the project; don't create empty scaffolding or files without a purpose.

The final plan may add, remove, merge, or rename sections, documents, skills, or source modules where there is a clear benefit. Do not let the proposed technology list or any anticipated file tree constrain a better design.

## 8. Expected result of this planning pass

Produce one authoritative, actionable implementation plan for Codex. It should be concise enough to use while coding but detailed enough to make design decisions and acceptance criteria explicit. Include:

- Scope and non-goals.
- Architecture and key decisions with rationale and trade-offs.
- Workflow and status/decision matrix.
- Data model/persistence strategy, if applicable.
- UI and operational behavior.
- Test scenarios and acceptance criteria.
- Setup, local run, deployment, configuration, and recovery instructions.
- Prioritized implementation order and a five-minute demo/submission checklist.
- Known risks, open questions, and fallback paths.

Where practical, also recommend the minimum repository instructions or agent skills that would help Codex work consistently. Do not require any particular set of files or skill names in advance.

**Final principle:** Treat this brief as informed context. Verify the source material, challenge assumptions, choose the lowest-risk path to a strong submission, and document why.
