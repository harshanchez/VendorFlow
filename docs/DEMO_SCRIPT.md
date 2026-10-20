# VendorFlow — 5-minute demo script

Record against the **hosted URL**. Narrate what is on screen. No slides. Stop at 5:00.

## Prep

- `GEMINI_ENABLED` off unless P1 is proven.
- Fixture buttons work; form is visible.
- At least one prior run in history (or seed from fixtures).
- Do not open `.env`.

## Script

**0:00–0:25 — Problem**  
Procurement has to onboard vendors from messy submissions. VendorFlow takes a form (optional PDF), runs explicit checks, and returns Approved, Pending, or Rejected with reasons and a follow-up. This is a demonstration policy, not GSTN or bank verification.

**0:25–0:50 — How it decides**  
Show the form. Explain: you can type a vendor or load a demo fixture. Rules decide; documents are optional; history goes to the dashboard.

**0:50–1:50 — Happy path (form only)**  
Click **Load happy path**. Point at legal name, GSTIN, matching bank account name. Do **not** attach a PDF. Run. Watch stages. Result: **Approved**. Read the caveat that no registry was queried.

**1:50–2:40 — Edge: bank name**  
Load **bank-name mismatch**. Run. **Pending**, `NAME_VS_BANK_ACCOUNT`. Read the follow-up (need matching account name evidence).

**2:40–3:20 — Edge: GSTIN format**  
Load **invalid GSTIN**. Run. **Pending**, not an accusation of fraud.

**3:20–4:00 — Edge: blocklist**  
Load **blocklist**. Run. **Rejected**. Say this is a synthetic demo list.

**4:00–4:30 — Dashboard**  
Open history. Point at statuses, a check list, run id. If a PDF fixture exists, optionally open extract text; skip if it would risk the clock.

**4:30–5:00 — Limits**  
No GSTN API, no email send, Gemini optional/off, PDFs extra not required. What you’d add next: Gemini extraction, human review notes.

If any run fails, do not improvise fake success. Say what happened and switch to a rehearsed fixture.
