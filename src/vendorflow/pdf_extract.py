"""Optional PDF extraction. It never runs for a form-only submission."""

from __future__ import annotations

from .models import CheckOutcome, DocumentInput, DocumentResult, ValidationCheck


def extract_document(document: DocumentInput | None) -> DocumentResult:
    if document is None:
        return DocumentResult(
            parse_status=CheckOutcome.NOT_CHECKED,
            checks=[
                ValidationCheck(
                    check_id="document_text_readable",
                    outcome=CheckOutcome.NOT_CHECKED,
                    human_readable_reason="No document attached; document extraction was not checked.",
                    in_scope=False,
                ),
                ValidationCheck(
                    check_id="document_vs_fields",
                    outcome=CheckOutcome.NOT_CHECKED,
                    human_readable_reason="No document attached; document consistency was not checked.",
                    in_scope=False,
                ),
            ],
        )
    try:
        from io import BytesIO

        import pymupdf

        with pymupdf.open(stream=BytesIO(document.content), filetype="pdf") as pdf:
            text = "\n".join(page.get_text() for page in pdf).strip()
    except Exception:  # noqa: BLE001 - malformed/unsupported optional PDFs are pending, never fatal
        text = ""
    if not text:
        return DocumentResult(
            filename=document.filename,
            parse_status=CheckOutcome.NEEDS_REVIEW,
            checks=[
                ValidationCheck(
                    check_id="document_text_readable",
                    outcome=CheckOutcome.NEEDS_REVIEW,
                    reason_code="DOCUMENT_TEXT_UNREADABLE",
                    human_readable_reason="PDF text could not be read for the optional document check.",
                    follow_up_action="Upload a readable PDF or provide the requested details in the form.",
                )
            ],
        )
    return DocumentResult(
        filename=document.filename,
        parse_status=CheckOutcome.PASS,
        extracted_text=text,
        checks=[
            ValidationCheck(
                check_id="document_text_readable",
                outcome=CheckOutcome.PASS,
                human_readable_reason="Optional PDF text was extracted.",
            )
        ],
    )
