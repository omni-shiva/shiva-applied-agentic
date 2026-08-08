from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Identifier = str


class IncidentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: Identifier = Field(pattern=r"^[a-z][a-z0-9_]{2,31}$")
    pipeline_id: Identifier = Field(pattern=r"^[a-z][a-z0-9_]{2,63}$")
    question: str = Field(min_length=8, max_length=1_000)
    allow_remediation: bool = False


class Citation(BaseModel):
    source_id: str
    title: str
    score: float = Field(ge=0.0, le=1.0)


class ToolTrace(BaseModel):
    tool: str
    status: Literal["ok", "blocked", "error"]
    summary: str


class DiagnosisResponse(BaseModel):
    request_id: str
    tenant_id: str
    pipeline_id: str
    severity: Literal["low", "medium", "high", "critical"]
    issue_summary: str
    likely_causes: list[str]
    evidence: list[str]
    recommendations: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    approval_required: bool
    proposed_action: str | None = None
    execution_performed: bool = False
    citations: list[Citation]
    tool_trace: list[ToolTrace]
    agent_mode: Literal["offline", "openai", "offline_fallback"]
    model_summary: str | None = None


class RemediationPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: Identifier = Field(pattern=r"^[a-z][a-z0-9_]{2,31}$")
    pipeline_id: Identifier = Field(pattern=r"^[a-z][a-z0-9_]{2,63}$")
    action: str = Field(min_length=8, max_length=500)


class RemediationPreview(BaseModel):
    tenant_id: str
    pipeline_id: str
    proposed_action: str
    approval_required: bool = True
    execution_enabled: bool = False
    safety_checks: list[str]


class EvaluationSummary(BaseModel):
    total_cases: int
    passed_cases: int
    pass_rate: float
    required_tool_trace_rate: float
    evidence_present_rate: float
    approval_guard_rate: float
