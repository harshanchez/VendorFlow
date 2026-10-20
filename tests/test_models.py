import pytest
from pydantic import ValidationError

from vendorflow.fixtures import FORM_VENDORS
from vendorflow.models import IntakeSubmission


def test_intake_rejects_missing_required_field() -> None:
    payload = {**FORM_VENDORS["happy_acme"]}
    del payload["legal_name"]
    with pytest.raises(ValidationError):
        IntakeSubmission.model_validate(payload)


def test_intake_rejects_blank_required_field() -> None:
    payload = {**FORM_VENDORS["happy_acme"], "bank_account_name": "   "}
    with pytest.raises(ValidationError):
        IntakeSubmission.model_validate(payload)


def test_intake_rejects_invalid_category() -> None:
    payload = {**FORM_VENDORS["happy_acme"], "vendor_category": "software"}
    with pytest.raises(ValidationError):
        IntakeSubmission.model_validate(payload)
