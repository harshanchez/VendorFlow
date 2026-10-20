"""Create the fictional optional-PDF fixtures used by VendorFlow.

Each spot-check vendor gets a matching and a conflicting document so the
optional document stage can be demonstrated on any of them. All names,
identifiers, and account details are fictional demonstration data.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pymupdf

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPOSITORY_ROOT / "src"))

from vendorflow.fixtures import BUNDLED_DOCUMENTS, SPOT_CHECK_VENDORS

MATCH_TEMPLATE = """VendorFlow supporting document (fictional demonstration data)

Legal name: {legal_name}
GSTIN: {gstin}
PAN: {pan}
Bank account name: {bank_account_name}
IFSC: {ifsc}

This optional PDF matches the submitted form fields.
No external tax, bank, or identity verification was performed.
"""

CONFLICT_TEMPLATE = """VendorFlow supporting document (fictional demonstration data)

Legal name: {legal_name}
GSTIN: {conflict_gstin}
PAN: {pan}
Bank account name: {bank_account_name}
IFSC: {ifsc}

This optional PDF intentionally shows a GSTIN that differs from the submitted form.
No external tax, bank, or identity verification was performed.
"""

ACME = {
    "legal_name": "VF-DEMO Acme Packaging Pvt Ltd",
    "gstin": "29AABCU9603R1ZM",
    "pan": "AABCU9603R",
    "bank_account_name": "VF-DEMO Acme Packaging Pvt Ltd",
    "ifsc": "HDFC0001234",
}


def conflicting_gstin(gstin: str) -> str:
    """Return the same identifier with a different GST state prefix."""
    prefix = "29" if gstin[:2] != "29" else "27"
    return prefix + gstin[2:]


def create_pdf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = pymupdf.open()
    page = document.new_page(width=595, height=842)
    rect = pymupdf.Rect(72, 72, 523, 770)
    page.insert_textbox(rect, text, fontsize=13, fontname="helv", lineheight=1.5)
    document.save(path)
    document.close()


def main() -> None:
    create_pdf(BUNDLED_DOCUMENTS["optional_pdf_match"]["path"], MATCH_TEMPLATE.format(**ACME))
    create_pdf(
        BUNDLED_DOCUMENTS["optional_pdf_conflict"]["path"],
        CONFLICT_TEMPLATE.format(conflict_gstin=conflicting_gstin(ACME["gstin"]), **ACME),
    )
    for vendor_key, vendor in SPOT_CHECK_VENDORS.items():
        create_pdf(
            BUNDLED_DOCUMENTS[f"{vendor_key}__match"]["path"],
            MATCH_TEMPLATE.format(**vendor),
        )
        create_pdf(
            BUNDLED_DOCUMENTS[f"{vendor_key}__conflict"]["path"],
            CONFLICT_TEMPLATE.format(conflict_gstin=conflicting_gstin(vendor["gstin"]), **vendor),
        )


if __name__ == "__main__":
    main()
