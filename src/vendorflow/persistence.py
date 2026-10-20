"""Supabase repository with an explicit, honest session-storage fallback."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlsplit, urlunsplit

from .models import PipelineRun, StageState


class SessionStore(Protocol):
    def __getitem__(self, key: str) -> Any: ...

    def __setitem__(self, key: str, value: Any) -> None: ...


@dataclass(frozen=True)
class PersistenceResult:
    stored_remotely: bool
    message: str


def _record_persistence_outcome(run: PipelineRun, *, stored_remotely: bool, message: str) -> None:
    """Replace the optimistic pipeline placeholder with the actual storage result."""
    for stage in reversed(run.stages):
        if stage.stage_id == "persist":
            stage.state = StageState.COMPLETE if stored_remotely else StageState.FALLBACK
            stage.detail = message
            return


def normalize_supabase_url(url: str | None) -> str | None:
    """Return the project root URL expected by supabase-py.

    Supabase dashboard REST examples often include `/rest/v1`; supabase-py adds
    that API path itself, so retaining it produces an invalid doubled endpoint.
    """
    if not url:
        return None
    parsed = urlsplit(url.strip())
    if parsed.path.rstrip("/") == "/rest/v1":
        return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
    return url.strip()


def describe_supabase_error(error: Exception) -> str:
    """Give the UI a useful, secret-free explanation for common demo failures."""
    message = str(error)
    if "PGRST205" in message or "onboarding_submissions" in message and "schema cache" in message:
        return "Supabase is configured, but the VendorFlow tables are missing. Apply the committed SQL migration in the Supabase SQL Editor."
    return "Supabase history is unavailable; showing session history only."


def supabase_credentials(secrets: Any | None = None) -> tuple[str | None, str | None]:
    """Read config without rendering or logging secret values."""
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    if secrets is not None:
        try:
            url = url or secrets.get("SUPABASE_URL")
            anon_key = anon_key or secrets.get("SUPABASE_ANON_KEY")
        except Exception:  # noqa: BLE001 - Streamlit raises when no secrets file exists
            return url, anon_key
    return url, anon_key


class Repository:
    def __init__(self, *, url: str | None = None, anon_key: str | None = None) -> None:
        self.url = normalize_supabase_url(url)
        self.anon_key = anon_key

    @property
    def configured(self) -> bool:
        return bool(self.url and self.anon_key)

    def _client(self):
        if not self.configured:
            raise RuntimeError("Supabase is not configured.")
        from supabase import create_client

        return create_client(self.url, self.anon_key)

    def history(self) -> list[dict[str, Any]]:
        if not self.configured:
            return []
        response = (
            self._client()
            .table("onboarding_submissions")
            .select("id,legal_name,gstin,status,summary,reason_codes,created_at,processing_run_id")
            .order("created_at", desc=True)
            .execute()
        )
        return list(response.data or [])

    def persist(self, run: PipelineRun) -> None:
        """Write the relational run graph. Errors are intentionally handled by the caller."""
        if run.intake is None:
            raise RuntimeError("A malformed intake cannot be sent to Supabase.")
        client = self._client()
        intake = run.intake.model_dump(mode="json")
        run_id = str(run.id)
        vendor_row = client.table("vendors").insert(
            {
                "legal_name": intake["legal_name"],
                "gstin": intake["gstin"],
                "pan": intake["pan"],
            }
        ).execute()
        vendor_id = vendor_row.data[0]["id"]
        client.table("processing_runs").insert(
            {
                "id": run_id,
                "started_at": run.started_at.isoformat(),
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "final_status": run.decision.status.value,
                "error": run.error,
            }
        ).execute()
        submission_row = client.table("onboarding_submissions").insert(
            {
                "vendor_id": vendor_id,
                "processing_run_id": run_id,
                "legal_name": intake["legal_name"],
                "gstin": intake["gstin"],
                "fields": intake,
                "status": run.decision.status.value,
                "summary": run.decision.summary,
                "reason_codes": run.decision.reason_codes,
            }
        ).execute()
        submission_id = submission_row.data[0]["id"]
        if run.document and run.document.filename:
            client.table("vendor_documents").insert(
                {
                    "submission_id": submission_id,
                    "filename": run.document.filename,
                    "document_type": "supporting_pdf",
                    "parse_status": run.document.parse_status.value,
                    "extracted_text": run.document.extracted_text,
                }
            ).execute()
        validation_rows = [
            {"submission_id": submission_id, **check.model_dump(mode="json")}
            for check in run.decision.checks
        ]
        if validation_rows:
            client.table("validation_results").insert(validation_rows).execute()
        event_rows = [
            {
                "processing_run_id": run_id,
                "stage_id": stage.stage_id,
                "label": stage.label,
                "state": stage.state.value,
                "detail": stage.detail,
                "occurred_at": stage.occurred_at.isoformat(),
            }
            for stage in run.stages
        ]
        if event_rows:
            client.table("run_events").insert(event_rows).execute()


def session_history(session: SessionStore) -> list[dict[str, Any]]:
    return list(session.get("vendorflow_history", []))


def persist_with_fallback(run: PipelineRun, repository: Repository, session: SessionStore) -> PersistenceResult:
    """Save to Supabase when possible; session fallback never pretends a remote save worked."""
    record = {
        "id": str(run.id),
        "legal_name": run.intake.legal_name if run.intake else "Invalid form",
        "gstin": run.intake.gstin if run.intake else "",
        "status": run.decision.status.value,
        "summary": run.decision.summary,
        "reason_codes": run.decision.reason_codes,
        "created_at": run.completed_at.isoformat() if run.completed_at else run.started_at.isoformat(),
        "processing_run_id": str(run.id),
    }
    history = session_history(session)
    if not repository.configured:
        message = "Supabase is not configured; this run is saved only in this browser session."
        session["vendorflow_history"] = [record, *history]
        _record_persistence_outcome(run, stored_remotely=False, message=message)
        return PersistenceResult(False, message)
    try:
        repository.persist(run)
    except Exception as exc:  # noqa: BLE001 - any client/database failure must fall back without a crash
        message = f"{describe_supabase_error(exc)} This run is saved only in this browser session."
        session["vendorflow_history"] = [record, *history]
        _record_persistence_outcome(run, stored_remotely=False, message=message)
        return PersistenceResult(False, message)
    message = "Saved to Supabase."
    _record_persistence_outcome(run, stored_remotely=True, message=message)
    return PersistenceResult(True, message)
