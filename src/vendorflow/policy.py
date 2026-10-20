"""Deterministic demonstration policy. These checks are not external verification."""

from __future__ import annotations

import re
from collections.abc import Iterable

from .models import (
    CheckOutcome,
    Decision,
    IntakeSubmission,
    OnboardingStatus,
    ValidationCheck,
)

DEMO_BLOCKLIST = {
    "vf demo northstar holdings pvt ltd",
    "vf demo pinnacle holdings pvt ltd",
}

FOLLOW_UPS = {
    "GSTIN_FORMAT": "Provide a 15-character GSTIN in the expected demo format.",
    "PAN_FORMAT": "Provide a PAN in the expected demo format.",
    "IFSC_FORMAT": "Provide an IFSC in the expected demo format.",
    "EMAIL_FORMAT": "Provide a valid contact email address.",
    "BANK_ACCOUNT_FORMAT": "Provide a digits-only bank account number in the accepted length range.",
    "STATE_CODE_FORMAT": "Provide a two-digit GST state code.",
    "GSTIN_STATE_MISMATCH": "Confirm the GSTIN state prefix and state code agree.",
    "NAME_VS_BANK_ACCOUNT": "Provide a cancelled cheque or account letter matching the legal name.",
    "DUPLICATE_VENDOR": "Review the prior submission and confirm whether this is a duplicate vendor.",
    "DOCUMENT_TEXT_UNREADABLE": "Upload a readable PDF or provide the requested details in the form.",
    "DOCUMENT_VS_FIELDS": "Correct the conflicting field or upload a document that matches the form.",
    "REQUIRED_FIELD": "Complete the missing required form field and run the check again.",
    "INTAKE_INVALID": "Correct the invalid form value and run the check again.",
}

GSTIN_PATTERN = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]$")
PAN_PATTERN = re.compile(r"^[A-Z]{5}\d{4}[A-Z]$")
IFSC_PATTERN = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ACCOUNT_PATTERN = re.compile(r"^\d{9,18}$")
STATE_PATTERN = re.compile(r"^\d{2}$")


def normalize(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def _check(
    check_id: str,
    valid: bool,
    reason_code: str,
    passed_reason: str,
    failed_reason: str,
) -> ValidationCheck:
    return ValidationCheck(
        check_id=check_id,
        outcome=CheckOutcome.PASS if valid else CheckOutcome.FAIL,
        reason_code=None if valid else reason_code,
        human_readable_reason=passed_reason if valid else failed_reason,
        follow_up_action=None if valid else FOLLOW_UPS[reason_code],
    )


def validate_fields(intake: IntakeSubmission) -> list[ValidationCheck]:
    """Check formats only; no government, tax, or bank registry is queried."""
    return [
        _check("gstin_format", bool(GSTIN_PATTERN.fullmatch(intake.gstin)), "GSTIN_FORMAT", "GSTIN has the expected demo format.", "GSTIN does not have the expected 15-character demo format."),
        _check("pan_format", bool(PAN_PATTERN.fullmatch(intake.pan)), "PAN_FORMAT", "PAN has the expected demo format.", "PAN does not have the expected demo format."),
        _check("ifsc_format", bool(IFSC_PATTERN.fullmatch(intake.ifsc)), "IFSC_FORMAT", "IFSC has the expected demo format.", "IFSC does not have the expected demo format."),
        _check("email_format", bool(EMAIL_PATTERN.fullmatch(intake.contact_email)), "EMAIL_FORMAT", "Contact email has a valid format.", "Contact email does not have a valid format."),
        _check("bank_account_format", bool(ACCOUNT_PATTERN.fullmatch(intake.bank_account_number)), "BANK_ACCOUNT_FORMAT", "Bank account number has the expected demo format.", "Bank account number must contain 9 to 18 digits only."),
        _check("state_code_format", bool(STATE_PATTERN.fullmatch(intake.state_code)), "STATE_CODE_FORMAT", "State code has the expected format.", "State code must be two digits."),
    ]


def validate_consistency(intake: IntakeSubmission) -> list[ValidationCheck]:
    names_match = normalize(intake.legal_name) == normalize(intake.bank_account_name)
    state_matches = bool(STATE_PATTERN.fullmatch(intake.state_code)) and intake.gstin[:2] == intake.state_code
    return [
        _check("name_vs_bank_account", names_match, "NAME_VS_BANK_ACCOUNT", "Legal name matches bank account name.", "Legal name does not match bank account name."),
        _check("gstin_state", state_matches, "GSTIN_STATE_MISMATCH", "GSTIN prefix matches the state code.", "GSTIN prefix does not match the state code."),
    ]


def validate_duplicate_and_blocklist(
    intake: IntakeSubmission, previous_submissions: Iterable[dict[str, str]] = (),
) -> list[ValidationCheck]:
    current_name = normalize(intake.legal_name)
    current_gstin = intake.gstin.upper()
    duplicate = any(
        normalize(str(item.get("legal_name", ""))) == current_name
        or str(item.get("gstin", "")).upper() == current_gstin
        for item in previous_submissions
    )
    blocklisted = current_name in DEMO_BLOCKLIST
    return [
        _check("duplicate_vendor", not duplicate, "DUPLICATE_VENDOR", "No duplicate vendor was found in available history.", "A matching legal name or GSTIN exists in available history."),
        ValidationCheck(
            check_id="demo_blocklist",
            outcome=CheckOutcome.FAIL if blocklisted else CheckOutcome.PASS,
            reason_code="BLOCKLIST_MATCH" if blocklisted else None,
            human_readable_reason=(
                "Demonstration blocklist match — not a government sanction list."
                if blocklisted
                else "No demonstration blocklist match."
            ),
            follow_up_action="Escalate the synthetic demo blocklist match for demonstration review." if blocklisted else None,
        ),
    ]


def decide(checks: list[ValidationCheck]) -> Decision:
    reason_codes = [check.reason_code for check in checks if check.reason_code]
    if "BLOCKLIST_MATCH" in reason_codes:
        return Decision(
            status=OnboardingStatus.REJECTED,
            summary="Rejected due to a demonstration blocklist match — not a government sanction list.",
            follow_up="No automated outreach is sent. Review the synthetic demonstration blocklist result.",
            checks=checks,
        )
    failing = [check for check in checks if check.in_scope and check.outcome in {CheckOutcome.FAIL, CheckOutcome.NEEDS_REVIEW}]
    if failing:
        follow_up = failing[0].follow_up_action or "Resolve the listed checks and run again."
        return Decision(
            status=OnboardingStatus.PENDING,
            summary="Pending because one or more deterministic demonstration checks need follow-up.",
            follow_up=follow_up,
            checks=checks,
        )
    return Decision(
        status=OnboardingStatus.APPROVED,
        summary="Approved by deterministic demonstration checks. No GSTN, bank, or identity registry was queried.",
        checks=checks,
    )
