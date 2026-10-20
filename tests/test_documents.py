import pytest

from vendorflow.fixtures import (
    BUNDLED_DOCUMENTS,
    SPOT_CHECK_EXPECTED,
    SPOT_CHECK_VENDORS,
    bundled_document,
    intake_for,
)
from vendorflow.models import OnboardingStatus
from vendorflow.pipeline import run_pipeline


@pytest.mark.parametrize("vendor_key", list(SPOT_CHECK_VENDORS))
def test_each_vendor_has_matching_and_conflicting_documents(vendor_key: str) -> None:
    for suffix in ("match", "conflict"):
        entry = BUNDLED_DOCUMENTS[f"{vendor_key}__{suffix}"]
        assert entry["path"].is_file(), f"missing {entry['path'].name}; run python scripts/make_demo_pdfs.py"


@pytest.mark.parametrize("vendor_key", list(SPOT_CHECK_VENDORS))
def test_matching_document_does_not_change_the_decision(vendor_key: str) -> None:
    expected_status, _ = SPOT_CHECK_EXPECTED[vendor_key]
    run = run_pipeline(intake_for(vendor_key), document=bundled_document(f"{vendor_key}__match"))
    assert run.decision.status.value == expected_status
    assert not any(code.startswith("DOCUMENT_") for code in run.decision.reason_codes)


@pytest.mark.parametrize("vendor_key", list(SPOT_CHECK_VENDORS))
def test_conflicting_document_is_flagged(vendor_key: str) -> None:
    expected_status, _ = SPOT_CHECK_EXPECTED[vendor_key]
    run = run_pipeline(intake_for(vendor_key), document=bundled_document(f"{vendor_key}__conflict"))
    assert "DOCUMENT_VS_FIELDS" in run.decision.reason_codes
    if expected_status == OnboardingStatus.REJECTED.value:
        assert run.decision.status == OnboardingStatus.REJECTED
    else:
        assert run.decision.status == OnboardingStatus.PENDING


def test_conflicting_documents_keep_the_legal_name_but_change_the_gstin() -> None:
    vendor_key = "test_happy_meridian"
    text = bundled_document(f"{vendor_key}__conflict").content
    import pymupdf

    with pymupdf.open(stream=text, filetype="pdf") as pdf:
        extracted = "".join(page.get_text() for page in pdf)
    vendor = SPOT_CHECK_VENDORS[vendor_key]
    assert vendor["legal_name"] in extracted
    assert vendor["gstin"] not in extracted
