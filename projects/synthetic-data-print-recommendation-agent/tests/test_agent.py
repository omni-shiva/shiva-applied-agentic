from print_recommendation_agent.models import DocumentProfile
from print_recommendation_agent.service import build_service


def test_recommendation_is_structured_and_never_executes() -> None:
    service = build_service()
    response = service.recommend(
        DocumentProfile(
            document_id="incoming_brochure_001",
            category="brochure",
            text_ratio=0.30,
            image_ratio=0.70,
            color_ratio=0.82,
            page_size="A4",
            page_count=8,
            quality_priority="premium",
        )
    )

    assert response.recommended_settings.color_mode == "color"
    assert response.recommended_settings.quality_mode == "high"
    assert response.evidence_document_ids
    assert response.confidence > 0.0
    assert response.execution_performed is False


def test_policy_boundary_requires_human_review() -> None:
    service = build_service()
    response = service.recommend(
        DocumentProfile(
            document_id="incoming_boundary_case",
            category="report",
            text_ratio=0.47,
            image_ratio=0.53,
            color_ratio=0.30,
            page_size="A4",
            page_count=7,
            quality_priority="premium",
        )
    )

    assert response.human_review_required is True
    assert response.review_reasons
    assert response.execution_performed is False
