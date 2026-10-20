"""Pydantic contracts shared by the form, rules, pipeline, and storage layers."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OnboardingStatus(StrEnum):
    APPROVED = "Approved"
    PENDING = "Pending"
    REJECTED = "Rejected"


class CheckOutcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    NEEDS_REVIEW = "needs_review"
    NOT_CHECKED = "not_checked"


class StageState(StrEnum):
    COMPLETE = "complete"
    SKIPPED = "skipped"
    FALLBACK = "fallback"
    ERROR = "error"


class IntakeSubmission(BaseModel):
    """Raw form data. Format validation deliberately belongs to the rules layer."""

    model_config = ConfigDict(str_strip_whitespace=True)

    legal_name: str = Field(min_length=1, max_length=160)
    country: str = Field(min_length=2, max_length=2)
    state_code: str = Field(min_length=1, max_length=8)
    gstin: str = Field(min_length=1, max_length=32)
    pan: str = Field(min_length=1, max_length=32)
    bank_account_name: str = Field(min_length=1, max_length=160)
    bank_account_number: str = Field(min_length=1, max_length=32)
    ifsc: str = Field(min_length=1, max_length=32)
    contact_email: str = Field(min_length=1, max_length=254)
    vendor_category: Literal["goods", "services", "both"]

    @field_validator("country")
    @classmethod
    def country_must_be_letters(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("country must be a two-letter code")
        return value.upper()

    @field_validator("gstin", "pan", "ifsc")
    @classmethod
    def uppercase_identifiers(cls, value: str) -> str:
        return value.upper()


class ValidationCheck(BaseModel):
    check_id: str
    outcome: CheckOutcome
    reason_code: str | None = None
    human_readable_reason: str
    evidence_reference: str | None = None
    follow_up_action: str | None = None
    in_scope: bool = True


class Decision(BaseModel):
    status: OnboardingStatus
    summary: str
    follow_up: str | None = None
    checks: list[ValidationCheck] = Field(default_factory=list)

    @property
    def reason_codes(self) -> list[str]:
        return [check.reason_code for check in self.checks if check.reason_code]


class PipelineStage(BaseModel):
    stage_id: str
    label: str
    state: StageState = StageState.COMPLETE
    detail: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DocumentInput(BaseModel):
    filename: str
    content: bytes


class DocumentResult(BaseModel):
    filename: str | None = None
    parse_status: CheckOutcome
    extracted_text: str | None = None
    checks: list[ValidationCheck] = Field(default_factory=list)


class PipelineRun(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    intake: IntakeSubmission | None = None
    decision: Decision
    stages: list[PipelineStage] = Field(default_factory=list)
    document: DocumentResult | None = None
    error: str | None = None

    def as_storage_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
