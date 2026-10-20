from vendorflow.fixtures import intake_for
from vendorflow.models import StageState
from vendorflow.persistence import (
    Repository,
    describe_supabase_error,
    normalize_supabase_url,
    persist_with_fallback,
)
from vendorflow.pipeline import run_pipeline


class BrokenRepository(Repository):
    @property
    def configured(self) -> bool:
        return True

    def persist(self, run) -> None:
        raise RuntimeError("network unavailable")


def test_persistence_failure_uses_session_fallback_without_changing_decision() -> None:
    run = run_pipeline(intake_for("happy_acme"))
    session = {}
    result = persist_with_fallback(run, BrokenRepository(), session)
    assert not result.stored_remotely
    assert run.decision.status.value == "Approved"
    assert session["vendorflow_history"][0]["status"] == "Approved"
    assert run.stages[-1].state == StageState.FALLBACK
    assert "browser session" in run.stages[-1].detail


def test_normalize_supabase_rest_endpoint_to_project_root() -> None:
    assert normalize_supabase_url("https://example.supabase.co/rest/v1/") == "https://example.supabase.co"
    assert normalize_supabase_url("https://example.supabase.co") == "https://example.supabase.co"


def test_schema_cache_error_explains_missing_migration() -> None:
    error = Exception("PGRST205: Could not find onboarding_submissions in the schema cache")
    assert "SQL migration" in describe_supabase_error(error)
