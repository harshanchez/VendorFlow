from vendorflow.fixtures import bundled_document, intake_for
from vendorflow.models import CheckOutcome, DocumentInput, OnboardingStatus
from vendorflow.pipeline import run_pipeline


def _pdf_bytes(text: str) -> bytes:
    import pymupdf

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def test_form_only_happy_path_is_approved_and_document_is_not_checked() -> None:
    run = run_pipeline(intake_for("happy_acme"))
    assert run.decision.status == OnboardingStatus.APPROVED
    assert len(run.stages) == 7
    assert run.stages[1].stage_id == "document"
    assert run.stages[1].state.value == "skipped"
    document_checks = [check for check in run.decision.checks if check.check_id.startswith("document_")]
    assert all(check.outcome == CheckOutcome.NOT_CHECKED for check in document_checks)
    assert not any(check.reason_code and check.reason_code.startswith("DOCUMENT_") for check in document_checks)


def test_failed_in_scope_check_cannot_approve() -> None:
    run = run_pipeline(intake_for("edge_gstin_format"))
    assert run.decision.status == OnboardingStatus.PENDING
    assert "GSTIN_FORMAT" in run.decision.reason_codes


def test_matching_optional_pdf_preserves_approval() -> None:
    intake = intake_for("happy_acme")
    document = DocumentInput(
        filename="match.pdf",
        content=_pdf_bytes(f"{intake.legal_name}\nGSTIN: {intake.gstin}"),
    )
    run = run_pipeline(intake, document=document)
    assert run.decision.status == OnboardingStatus.APPROVED
    assert not any(code.startswith("DOCUMENT_") for code in run.decision.reason_codes)


def test_conflicting_optional_pdf_is_pending() -> None:
    intake = intake_for("happy_acme")
    document = DocumentInput(
        filename="conflict.pdf",
        content=_pdf_bytes(f"{intake.legal_name}\nGSTIN: 27AABCU9603R1ZM"),
    )
    run = run_pipeline(intake, document=document)
    assert run.decision.status == OnboardingStatus.PENDING
    assert "DOCUMENT_VS_FIELDS" in run.decision.reason_codes


def test_bundled_conflicting_pdf_is_pending() -> None:
    run = run_pipeline(intake_for("happy_acme"), document=bundled_document("optional_pdf_conflict"))
    assert run.decision.status == OnboardingStatus.PENDING
    assert "DOCUMENT_VS_FIELDS" in run.decision.reason_codes
