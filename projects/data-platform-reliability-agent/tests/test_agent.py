from reliability_agent.schemas import IncidentRequest
from reliability_agent.service import build_agent


def test_schema_incident_is_grounded_and_requires_approval() -> None:
    response = build_agent().diagnose(
        IncidentRequest(
            tenant_id="tenant_alpha",
            pipeline_id="orders_daily",
            question="Why did the latest orders pipeline fail after a schema change?",
        )
    )

    assert response.severity == "high"
    assert "SCHEMA_MISMATCH" in response.issue_summary
    assert any("customer_segment" in item for item in response.evidence)
    assert response.approval_required is True
    assert response.execution_performed is False
    assert {trace.tool for trace in response.tool_trace} == {
        "query_pipeline_events",
        "inspect_pipeline_contract",
        "search_runbooks",
    }
    assert response.citations


def test_sla_incident_compares_runtime_with_sla() -> None:
    response = build_agent().diagnose(
        IncidentRequest(
            tenant_id="tenant_alpha",
            pipeline_id="telemetry_hourly",
            question="Why did telemetry processing breach its runtime target?",
        )
    )

    assert "SLA_BREACH" in response.issue_summary
    assert any("exceeded" in item for item in response.evidence)
    assert response.confidence >= 0.7


def test_output_drop_is_critical() -> None:
    response = build_agent().diagnose(
        IncidentRequest(
            tenant_id="tenant_beta",
            pipeline_id="quality_rollup",
            question="Explain the latest output loss with evidence.",
        )
    )

    assert response.severity == "critical"
    assert "OUTPUT_DROP" in response.issue_summary
    assert response.approval_required is True
