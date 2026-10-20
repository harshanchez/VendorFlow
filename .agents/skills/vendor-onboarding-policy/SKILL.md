---
name: vendor-onboarding-policy
description: Demonstration vendor-onboarding policy: statuses, honesty, and fictional data.
---

# Policy skill

- Statuses: Approved, Pending, Rejected only.
- Rules engine decides. Gemini does not.
- Rejected only on `DEMO_BLOCKLIST` match. Label it as demo data.
- Ambiguous, missing, invalid, conflicting, unreadable → Pending with follow-up. Not fraud.
- No PDF → document checks `not_checked`; they must not block Approval.
- PDF present → extract with PyMuPDF; conflict/unreadable → Pending.
- Never claim GSTN, bank, or identity verification unless a real authorized API ran (P0: none did).
- Fictional vendors only. Prefix `VF-DEMO`. No real PAN/GSTIN/accounts.
- Do not send follow-up email; display draft/template text in the UI.
