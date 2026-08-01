from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI

from .agent import ReliabilityAgent
from .evaluation import run_evaluation
from .schemas import (
    DiagnosisResponse,
    EvaluationSummary,
    IncidentRequest,
    RemediationPreview,
    RemediationPreviewRequest,
)
from .service import build_agent
from .settings import Settings

app = FastAPI(
    title="Data Platform Reliability Agent",
    version="0.1.0",
    description="Synthetic, tenant-safe incident diagnosis with retrieval and evaluation.",
)

AgentDependency = Annotated[ReliabilityAgent, Depends(build_agent)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(agent: AgentDependency) -> dict[str, str]:
    del agent
    return {"status": "ready"}


@app.post("/v1/diagnose", response_model=DiagnosisResponse)
def diagnose(
    request: IncidentRequest,
    agent: AgentDependency,
) -> DiagnosisResponse:
    return agent.diagnose(request)


@app.post("/v1/remediations/preview", response_model=RemediationPreview)
def preview_remediation(request: RemediationPreviewRequest) -> RemediationPreview:
    return RemediationPreview(
        tenant_id=request.tenant_id,
        pipeline_id=request.pipeline_id,
        proposed_action=request.action,
        safety_checks=[
            "Tenant and pipeline scope must match the authenticated operator context.",
            "The action must be idempotent or have an explicit rollback plan.",
            "A human operator must approve execution outside this demo service.",
        ],
    )


@app.post("/v1/evaluations/run", response_model=EvaluationSummary)
def evaluate(agent: AgentDependency) -> EvaluationSummary:
    return run_evaluation(agent, Settings().eval_cases_path)
