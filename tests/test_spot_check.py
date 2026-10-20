import pytest

from vendorflow.fixtures import SPOT_CHECK_EXPECTED, SPOT_CHECK_VENDORS, intake_for
from vendorflow.models import OnboardingStatus
from vendorflow.pipeline import run_pipeline


def test_ten_spot_check_vendors_exist() -> None:
    assert len(SPOT_CHECK_VENDORS) == 10
    assert set(SPOT_CHECK_VENDORS) == set(SPOT_CHECK_EXPECTED)


def test_spot_check_vendors_have_unique_identities() -> None:
    names = {vendor["legal_name"] for vendor in SPOT_CHECK_VENDORS.values()}
    gstins = {vendor["gstin"] for vendor in SPOT_CHECK_VENDORS.values()}
    pans = {vendor["pan"] for vendor in SPOT_CHECK_VENDORS.values()}
    accounts = {vendor["bank_account_number"] for vendor in SPOT_CHECK_VENDORS.values()}
    assert len(names) == len(gstins) == len(pans) == len(accounts) == 10


@pytest.mark.parametrize("fixture_name", list(SPOT_CHECK_VENDORS))
def test_spot_check_vendor_status_matches_its_label(fixture_name: str) -> None:
    expected_status, expected_reason = SPOT_CHECK_EXPECTED[fixture_name]
    run = run_pipeline(intake_for(fixture_name))
    assert run.decision.status.value == expected_status
    if expected_reason is None:
        assert run.decision.reason_codes == []
    else:
        assert run.decision.reason_codes == [expected_reason]


def test_spot_check_vendors_do_not_share_identity_with_graded_fixtures() -> None:
    from vendorflow.fixtures import FORM_VENDORS

    spot = SPOT_CHECK_VENDORS
    others = {key: value for key, value in FORM_VENDORS.items() if key not in spot}
    other_names = {vendor["legal_name"] for vendor in others.values()}
    other_gstins = {vendor["gstin"] for vendor in others.values()}
    for vendor in spot.values():
        assert vendor["legal_name"] not in other_names
        assert vendor["gstin"] not in other_gstins


def test_running_two_spot_check_vendors_in_sequence_has_no_duplicate() -> None:
    done: list[dict[str, str]] = []
    for fixture_name in ("test_happy_meridian", "test_happy_saffron"):
        run = run_pipeline(intake_for(fixture_name), previous_submissions=done)
        assert run.decision.status == OnboardingStatus.APPROVED
        assert "DUPLICATE_VENDOR" not in run.decision.reason_codes
        done.append({"legal_name": run.intake.legal_name, "gstin": run.intake.gstin})
