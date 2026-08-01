from fastapi.testclient import TestClient

from print_recommendation_agent.api import app, get_service

client = TestClient(app)


def test_health_and_readiness() -> None:
    assert client.get("/health").json() == {"status": "ok"}

    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["training_rows"] > 0


def test_scarcity_endpoint() -> None:
    response = client.get("/v1/scarcity")

    assert response.status_code == 200
    assert response.json()["coverage_rate"] < 1.0
    assert response.json()["missing_strata"]


def test_recommendation_rejects_unknown_fields() -> None:
    response = client.post(
        "/v1/recommend",
        json={
            "document_id": "incoming_invoice_001",
            "category": "invoice",
            "text_ratio": 0.9,
            "image_ratio": 0.1,
            "color_ratio": 0.05,
            "page_size": "A4",
            "page_count": 2,
            "quality_priority": "economy",
            "execute_print": True,
        },
    )

    assert response.status_code == 422


def teardown_module() -> None:
    get_service.cache_clear()
