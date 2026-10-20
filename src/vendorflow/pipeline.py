"""The seven-stage, deterministic onboarding pipeline."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from .models import (
    CheckOutcome,
    Decision,
    DocumentInput,
    IntakeSubmission,
    OnboardingStatus,
    PipelineRun,
    PipelineStage,
    StageState,
    ValidationCheck,
)
from .pdf_extract import extract_document
from .policy import (
    FOLLOW_UPS,
    decide,
    validate_consistency,
    validate_duplicate_and_blocklist,
    validate_fields,
)

StageCallback = Callable[[PipelineStage], None]


def _stage(run: PipelineRun, stage_id: str, label: str, detail: str, callback: StageCallback | None, state: StageState = StageState.COMPLETE) -> None:
    item = PipelineStage(stage_id=stage_id, label=label, detail=detail, state=state)
    run.stages.append(item)
    if callback:
        callback(item)


def _invalid_intake_run(payload: dict[str, Any], callback: StageCallback | None) -> PipelineRun:
    error = "The form has missing or invalid required values."
    check = ValidationCheck(
        check_id="intake_validation",
        outcome=CheckOutcome.FAIL,
        reason_code="REQUIRED_FIELD",
        human_readable_reason=error,
        follow_up_action=FOLLOW_UPS["REQUIRED_FIELD"],
    )
    run = PipelineRun(
        decision=Decision(status=OnboardingStatus.PENDING, summary="Pending because the form is incomplete or invalid.", follow_up=FOLLOW_UPS["REQUIRED_FIELD"], checks=[check]),
        error=error,
    )
    _stage(run, "intake", "1. Intake received", "Form validation needs correction.", callback, StageState.ERROR)
    _stage(run, "document", "2. Optional document extraction", "No document checked because intake needs correction.", callback, StageState.SKIPPED)
    _stage(run, "field_validation", "3. Field validation", "Waiting for a valid form snapshot.", callback, StageState.SKIPPED)
    _stage(run, "cross_field", "4. Cross-field consistency", "Waiting for a valid form snapshot.", callback, StageState.SKIPPED)
    _stage(run, "duplicate_blocklist", "5. Duplicate / blocklist", "Waiting for a valid form snapshot.", callback, StageState.SKIPPED)
    _stage(run, "decision", "6. Decision + follow-up", "Pending follow-up created.", callback)
    _stage(run, "persist", "7. Persist", "Persistence is handled by the selected storage adapter.", callback)
    run.completed_at = datetime.now(UTC)
    return run


def run_pipeline(
    payload: IntakeSubmission | dict[str, Any],
    *,
    document: DocumentInput | None = None,
    previous_submissions: Iterable[dict[str, str]] = (),
    on_stage: StageCallback | None = None,
) -> PipelineRun:
    """Run every stage. A missing optional PDF emits only `not_checked` document checks."""
    try:
        intake = payload if isinstance(payload, IntakeSubmission) else IntakeSubmission.model_validate(payload)
    except ValidationError:
        return _invalid_intake_run(dict(payload) if isinstance(payload, dict) else {}, on_stage)

    placeholder = Decision(status=OnboardingStatus.PENDING, summary="Pipeline is running.")
    run = PipelineRun(intake=intake, decision=placeholder)
    _stage(run, "intake", "1. Intake received", "Captured an editable form snapshot.", on_stage)

    document_result = extract_document(document)
    run.document = document_result
    document_detail = "No document attached; document checks are not_checked." if document is None else "Optional document extraction completed."
    _stage(run, "document", "2. Optional document extraction", document_detail, on_stage, StageState.SKIPPED if document is None else StageState.COMPLETE)

    field_checks = validate_fields(intake)
    _stage(run, "field_validation", "3. Field validation", "Ran deterministic format checks; no registry was queried.", on_stage)

    consistency_checks = validate_consistency(intake)
    if document_result.extracted_text is not None:
        text = document_result.extracted_text.upper()
        document_matches = intake.legal_name.upper() in text and intake.gstin.upper() in text
        document_result.checks.append(
            ValidationCheck(
                check_id="document_vs_fields",
                outcome=CheckOutcome.PASS if document_matches else CheckOutcome.NEEDS_REVIEW,
                reason_code=None if document_matches else "DOCUMENT_VS_FIELDS",
                human_readable_reason="Optional PDF matches legal name and GSTIN fields." if document_matches else "Optional PDF does not contain the submitted legal name and GSTIN together.",
                follow_up_action=None if document_matches else FOLLOW_UPS["DOCUMENT_VS_FIELDS"],
            )
        )
    _stage(run, "cross_field", "4. Cross-field consistency", "Compared names, GSTIN state prefix, and any optional document text.", on_stage)

    duplicate_checks = validate_duplicate_and_blocklist(intake, previous_submissions)
    _stage(run, "duplicate_blocklist", "5. Duplicate / blocklist", "Checked available history and the synthetic demonstration blocklist.", on_stage)

    run.decision = decide(field_checks + consistency_checks + duplicate_checks + document_result.checks)
    _stage(run, "decision", "6. Decision + follow-up", f"Decision: {run.decision.status}.", on_stage)
    _stage(run, "persist", "7. Persist", "Ready for persistent storage or session fallback.", on_stage)
    run.completed_at = datetime.now(UTC)
    return run
