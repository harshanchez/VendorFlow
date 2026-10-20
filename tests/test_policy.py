import pytest

from vendorflow.fixtures import BULK_TEST_VENDORS, bulk_test_data_csv, intake_for
from vendorflow.models import OnboardingStatus
from vendorflow.policy import (
    decide,
    validate_consistency,
    validate_duplicate_and_blocklist,
    validate_fields,
)


@pytest.mark.parametrize(
    ("fixture_name", "expected_status", "expected_reasons"),
    [
        ("happy_acme", OnboardingStatus.APPROVED, []),
        ("edge_bank_name_mismatch", OnboardingStatus.PENDING, ["NAME_VS_BANK_ACCOUNT"]),
        ("edge_gstin_format", OnboardingStatus.PENDING, ["GSTIN_FORMAT"]),
        ("edge_blocklist", OnboardingStatus.REJECTED, ["BLOCKLIST_MATCH"]),
    ],
)
def test_fixture_statuses_and_reason_codes(fixture_name, expected_status, expected_reasons) -> None:
    intake = intake_for(fixture_name)
    checks = validate_fields(intake) + validate_consistency(intake) + validate_duplicate_and_blocklist(intake)
    decision = decide(checks)
    assert decision.status == expected_status
    assert decision.reason_codes == expected_reasons


def test_only_blocklist_rejects() -> None:
    intake = intake_for("edge_bank_name_mismatch")
    decision = decide(validate_fields(intake) + validate_consistency(intake) + validate_duplicate_and_blocklist(intake))
    assert decision.status != OnboardingStatus.REJECTED


def test_bulk_test_vendors_are_unique_and_approved() -> None:
    assert len(BULK_TEST_VENDORS) == 50
    legal_names = {vendor["legal_name"] for vendor in BULK_TEST_VENDORS.values()}
    gstins = {vendor["gstin"] for vendor in BULK_TEST_VENDORS.values()}
    assert len(legal_names) == len(gstins) == 50
    for fixture_name in BULK_TEST_VENDORS:
        intake = intake_for(fixture_name)
        checks = validate_fields(intake) + validate_consistency(intake) + validate_duplicate_and_blocklist(intake)
        assert decide(checks).status == OnboardingStatus.APPROVED


def test_bulk_test_data_csv_has_all_vendors() -> None:
    csv_data = bulk_test_data_csv().decode("utf-8")
    assert len(csv_data.strip().splitlines()) == 51
