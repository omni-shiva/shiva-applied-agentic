from fastapi.testclient import TestClient

from reliability_agent.api import app

client = TestClient(app)


def test_health_and_readiness() -> None:
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}


def test_diagnose_endpoint_returns_trace_and_citations() -> None:
    response = client.post(
        "/v1/diagnose",
        json={
            "tenant_id": "tenant_beta",
            "pipeline_id": "inventory_hourly",
            "question": "Why did the latest inventory pipeline fail?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "UPSTREAM_DELAY" in body["issue_summary"]
    assert body["tool_trace"]
    assert body["citations"]


def test_remediation_endpoint_only_previews() -> None:
    response = client.post(
        "/v1/remediations/preview",
        json={
            "tenant_id": "tenant_alpha",
            "pipeline_id": "orders_daily",
            "action": "Backfill the failed date after contract approval.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["approval_required"] is True
    assert body["execution_enabled"] is False


def test_invalid_identifier_is_rejected() -> None:
    response = client.post(
        "/v1/diagnose",
        json={
            "tenant_id": "../tenant_alpha",
            "pipeline_id": "orders_daily",
            "question": "Try an invalid tenant identifier.",
        },
    )
    assert response.status_code == 422
