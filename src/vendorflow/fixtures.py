"""Canonical, fictional form fixtures used in tests and the live demo."""

import csv
from io import StringIO
from pathlib import Path

from .models import DocumentInput, IntakeSubmission

_HAPPY_PATH = {
    "legal_name": "VF-DEMO Acme Packaging Pvt Ltd",
    "country": "IN",
    "state_code": "29",
    "gstin": "29AABCU9603R1ZM",
    "pan": "AABCU9603R",
    "bank_account_name": "VF-DEMO Acme Packaging Pvt Ltd",
    "bank_account_number": "501234567890",
    "ifsc": "HDFC0001234",
    "contact_email": "accounts@vf-demo-acme.example",
    "vendor_category": "goods",
}


def _bulk_test_vendor(number: int) -> dict[str, str]:
    """Create one of the 50 deterministic, fictional, duplicate-safe test records."""
    pan = f"VFDMO{number:04d}A"
    gstin_suffix = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[(number - 1) % 36]
    legal_name = f"VF-DEMO Test Vendor {number:03d} Pvt Ltd"
    return {
        "legal_name": legal_name,
        "country": "IN",
        "state_code": "29",
        "gstin": f"29{pan}1Z{gstin_suffix}",
        "pan": pan,
        "bank_account_name": legal_name,
        "bank_account_number": f"700000{number:06d}",
        "ifsc": f"DEMO0{number:06d}",
        "contact_email": f"vendor-{number:03d}@vf-demo.example",
        "vendor_category": ("goods", "services", "both")[(number - 1) % 3],
    }


BULK_TEST_VENDORS = {
    f"test_vendor_{number:03d}": _bulk_test_vendor(number) for number in range(1, 51)
}


_SPOT_CHECK_VENDORS: dict[str, dict[str, str]] = {
    "test_happy_meridian": {
        "legal_name": "VF-DEMO Meridian Freight Pvt Ltd",
        "country": "IN",
        "state_code": "27",
        "gstin": "27MERID1234F1Z5",
        "pan": "MERID1234F",
        "bank_account_name": "VF-DEMO Meridian Freight Pvt Ltd",
        "bank_account_number": "512345678901",
        "ifsc": "HDFC0001234",
        "contact_email": "accounts@vf-demo-meridian.example",
        "vendor_category": "services",
    },
    "test_happy_saffron": {
        "legal_name": "VF-DEMO Saffron Logistics Pvt Ltd",
        "country": "IN",
        "state_code": "07",
        "gstin": "07SAFFR4821K1Z3",
        "pan": "SAFFR4821K",
        "bank_account_name": "VF-DEMO Saffron Logistics Pvt Ltd",
        "bank_account_number": "604321987654",
        "ifsc": "ICIC0004321",
        "contact_email": "accounts@vf-demo-saffron.example",
        "vendor_category": "both",
    },
    "test_bank_name_mismatch_kiran": {
        "legal_name": "VF-DEMO Kiran Traders Pvt Ltd",
        "country": "IN",
        "state_code": "29",
        "gstin": "29KIRAN5678L1Z2",
        "pan": "KIRAN5678L",
        "bank_account_name": "Suresh Naik",
        "bank_account_number": "501234509876",
        "ifsc": "HDFC0005678",
        "contact_email": "accounts@vf-demo-kiran.example",
        "vendor_category": "goods",
    },
    "test_invalid_gstin_veer": {
        "legal_name": "VF-DEMO Veer Tools Pvt Ltd",
        "country": "IN",
        "state_code": "29",
        "gstin": "29VEER0INVALID",
        "pan": "VEERT1234V",
        "bank_account_name": "VF-DEMO Veer Tools Pvt Ltd",
        "bank_account_number": "501234501122",
        "ifsc": "HDFC0009012",
        "contact_email": "accounts@vf-demo-veer.example",
        "vendor_category": "goods",
    },
    "test_gstin_state_mismatch_nova": {
        "legal_name": "VF-DEMO Nova Ceramics Pvt Ltd",
        "country": "IN",
        "state_code": "29",
        "gstin": "27NOVAC9012N1Z7",
        "pan": "NOVAC9012N",
        "bank_account_name": "VF-DEMO Nova Ceramics Pvt Ltd",
        "bank_account_number": "501234503344",
        "ifsc": "HDFC0003456",
        "contact_email": "accounts@vf-demo-nova.example",
        "vendor_category": "both",
    },
    "test_invalid_pan_northwind": {
        "legal_name": "VF-DEMO Northwind Papers Pvt Ltd",
        "country": "IN",
        "state_code": "29",
        "gstin": "29NORTH3456P1Z9",
        "pan": "NORTH1234",
        "bank_account_name": "VF-DEMO Northwind Papers Pvt Ltd",
        "bank_account_number": "501234505566",
        "ifsc": "HDFC0007788",
        "contact_email": "accounts@vf-demo-northwind.example",
        "vendor_category": "goods",
    },
    "test_invalid_ifsc_orbit": {
        "legal_name": "VF-DEMO Orbit Components Pvt Ltd",
        "country": "IN",
        "state_code": "29",
        "gstin": "29ORBIT7890R1Z4",
        "pan": "ORBIT7890R",
        "bank_account_name": "VF-DEMO Orbit Components Pvt Ltd",
        "bank_account_number": "501234507788",
        "ifsc": "ORBIT0001",
        "contact_email": "accounts@vf-demo-orbit.example",
        "vendor_category": "goods",
    },
    "test_bad_account_bluewave": {
        "legal_name": "VF-DEMO Bluewave Chemicals Pvt Ltd",
        "country": "IN",
        "state_code": "29",
        "gstin": "29BLUEW2345B1Z8",
        "pan": "BLUEW2345B",
        "bank_account_name": "VF-DEMO Bluewave Chemicals Pvt Ltd",
        "bank_account_number": "5012-345-678",
        "ifsc": "HDFC0002211",
        "contact_email": "accounts@vf-demo-bluewave.example",
        "vendor_category": "both",
    },
    "test_bad_email_stonebridge": {
        "legal_name": "VF-DEMO Stonebridge Metals Pvt Ltd",
        "country": "IN",
        "state_code": "29",
        "gstin": "29STONE6789S1Z6",
        "pan": "STONE6789S",
        "bank_account_name": "VF-DEMO Stonebridge Metals Pvt Ltd",
        "bank_account_number": "501234511233",
        "ifsc": "HDFC0004433",
        "contact_email": "accounts.at.vf-demo-stonebridge",
        "vendor_category": "services",
    },
    "test_blocklist_pinnacle": {
        "legal_name": "VF-DEMO Pinnacle Holdings Pvt Ltd",
        "country": "IN",
        "state_code": "29",
        "gstin": "29PINNA4321P1Z1",
        "pan": "PINNA4321P",
        "bank_account_name": "VF-DEMO Pinnacle Holdings Pvt Ltd",
        "bank_account_number": "501234519955",
        "ifsc": "HDFC0006655",
        "contact_email": "accounts@vf-demo-pinnacle.example",
        "vendor_category": "both",
    },
}

SPOT_CHECK_VENDORS = _SPOT_CHECK_VENDORS

SPOT_CHECK_EXPECTED: dict[str, tuple[str, str | None]] = {
    "test_happy_meridian": ("Approved", None),
    "test_happy_saffron": ("Approved", None),
    "test_bank_name_mismatch_kiran": ("Pending", "NAME_VS_BANK_ACCOUNT"),
    "test_invalid_gstin_veer": ("Pending", "GSTIN_FORMAT"),
    "test_gstin_state_mismatch_nova": ("Pending", "GSTIN_STATE_MISMATCH"),
    "test_invalid_pan_northwind": ("Pending", "PAN_FORMAT"),
    "test_invalid_ifsc_orbit": ("Pending", "IFSC_FORMAT"),
    "test_bad_account_bluewave": ("Pending", "BANK_ACCOUNT_FORMAT"),
    "test_bad_email_stonebridge": ("Pending", "EMAIL_FORMAT"),
    "test_blocklist_pinnacle": ("Rejected", "BLOCKLIST_MATCH"),
}

SPOT_CHECK_LABELS = {
    key: f"{_SPOT_CHECK_VENDORS[key]['legal_name']} — {status}"
    + (f" ({reason})" if reason else "")
    for key, (status, reason) in SPOT_CHECK_EXPECTED.items()
}


FORM_VENDORS: dict[str, dict[str, str]] = {
    "happy_acme": _HAPPY_PATH,
    "edge_bank_name_mismatch": {**_HAPPY_PATH, "bank_account_name": "Ramesh Kumar"},
    "edge_gstin_format": {**_HAPPY_PATH, "gstin": "29-INVALID"},
    "edge_blocklist": {
        **_HAPPY_PATH,
        "legal_name": "VF-DEMO Northstar Holdings Pvt Ltd",
        "bank_account_name": "VF-DEMO Northstar Holdings Pvt Ltd",
    },
    **BULK_TEST_VENDORS,
    **SPOT_CHECK_VENDORS,
}


FIXTURE_LABELS = {
    "happy_acme": "Load happy path",
    "edge_bank_name_mismatch": "Load bank-name mismatch",
    "edge_gstin_format": "Load invalid GSTIN",
    "edge_blocklist": "Load blocklist",
}


_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_PDF_DIR = _REPOSITORY_ROOT / "tests" / "fixtures" / "pdfs"

BUNDLED_DOCUMENTS: dict[str, dict[str, str | Path]] = {
    "optional_pdf_match": {
        "label": "Matching fictional PDF",
        "path": _PDF_DIR / "optional_pdf_match.pdf",
    },
    "optional_pdf_conflict": {
        "label": "Conflicting fictional PDF",
        "path": _PDF_DIR / "optional_pdf_conflict.pdf",
    },
}

for _vendor_key in _SPOT_CHECK_VENDORS:
    BUNDLED_DOCUMENTS[f"{_vendor_key}__match"] = {
        "label": "Matching fictional PDF",
        "path": _PDF_DIR / f"{_vendor_key}__match.pdf",
    }
    BUNDLED_DOCUMENTS[f"{_vendor_key}__conflict"] = {
        "label": "Conflicting fictional PDF (different GSTIN)",
        "path": _PDF_DIR / f"{_vendor_key}__conflict.pdf",
    }


def documents_for(vendor_key: str | None) -> list[str]:
    """Return the bundled document keys offered for the loaded vendor."""
    if vendor_key in _SPOT_CHECK_VENDORS:
        return [f"{vendor_key}__match", f"{vendor_key}__conflict"]
    return ["optional_pdf_match", "optional_pdf_conflict"]


def intake_for(name: str) -> IntakeSubmission:
    """Return a validated copy so callers cannot mutate the fixture catalog."""
    return IntakeSubmission.model_validate(FORM_VENDORS[name])


def bulk_test_data_csv() -> bytes:
    """Return the bulk test data as a UTF-8 CSV for operators to inspect or keep."""
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(_HAPPY_PATH))
    writer.writeheader()
    writer.writerows(BULK_TEST_VENDORS.values())
    return output.getvalue().encode("utf-8")


def bundled_document(name: str) -> DocumentInput:
    """Load a committed, fictional PDF fixture for the optional document demo."""
    path = BUNDLED_DOCUMENTS[name]["path"]
    return DocumentInput(filename=path.name, content=path.read_bytes())
