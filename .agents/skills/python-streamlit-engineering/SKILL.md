---
name: python-streamlit-engineering
description: Streamlit + Python engineering constraints for VendorFlow local and Community Cloud.
---

# Streamlit engineering skill

- Entry point `app.py`. Also ship `requirements.txt` at repo root.
- `streamlit>=1.52` for Python 3.14. Local venv 3.14; Cloud try 3.14 then 3.13/3.12.
- Live run: `st.status(..., type="step")` for stages. Status text must not rely on color alone.
- Fixture buttons **fill the form**; they must not skip the form model.
- `st.file_uploader` is optional. Run must work if the uploader is empty.
- Read secrets from environment or `st.secrets`. Never hard-code keys. Never `st.write` secrets.
- Keep UI to Overview, New run, Live run, History. No fake KPI metrics.
- Prefer small functions over a god `app.py`; import from `src/vendorflow`.
