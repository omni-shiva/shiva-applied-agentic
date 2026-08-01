from __future__ import annotations

from collections import defaultdict

from .features import feature_distance, feature_vector
from .models import DocumentProfile, LabeledDocument, PrintSettings, RecommendationResponse
from .rules import label_review_reasons


class PrintRecommendationAgent:
    def __init__(self, review_confidence_threshold: float = 0.65, neighbours: int = 7) -> None:
        self._review_confidence_threshold = review_confidence_threshold
        self._neighbours = neighbours
        self._training: list[tuple[tuple[float, ...], LabeledDocument]] = []

    def fit(self, records: list[LabeledDocument]) -> None:
        if not records:
            raise ValueError("at least one labelled document is required")
        self._training = [(feature_vector(record.document), record) for record in records]

    def recommend(self, document: DocumentProfile) -> RecommendationResponse:
        if not self._training:
            raise RuntimeError("fit must be called before recommend")

        query = feature_vector(document)
        ranked = sorted(
            (
                (feature_distance(query, vector), record)
                for vector, record in self._training
                if record.document.document_id != document.document_id
            ),
            key=lambda pair: pair[0],
        )
        neighbours = ranked[: min(self._neighbours, len(ranked))]
        if not neighbours:
            raise RuntimeError("no evidence documents are available")

        recommendation, confidence = self._vote(neighbours)
        nearest_distance = neighbours[0][0]
        review_reasons = label_review_reasons(document)
        if confidence < self._review_confidence_threshold:
            review_reasons.append("recommendation confidence is below the review threshold")
        if nearest_distance > 1.75:
            review_reasons.append("the document is outside the nearby training distribution")

        reasons = [
            f"used {len(neighbours)} nearest labelled document profiles",
            f"nearest engineered-feature distance is {nearest_distance:.3f}",
            "each print-setting field is selected by distance-weighted evidence",
        ]
        return RecommendationResponse(
            document_id=document.document_id,
            recommended_settings=recommendation,
            confidence=round(confidence, 4),
            evidence_document_ids=[record.document.document_id for _, record in neighbours[:5]],
            reasons=reasons,
            human_review_required=bool(review_reasons),
            review_reasons=review_reasons,
            execution_performed=False,
        )

    @staticmethod
    def _vote(
        neighbours: list[tuple[float, LabeledDocument]],
    ) -> tuple[PrintSettings, float]:
        field_votes: dict[str, dict[object, float]] = defaultdict(lambda: defaultdict(float))
        total_weight = 0.0
        for distance, record in neighbours:
            weight = 1.0 / (0.10 + distance)
            total_weight += weight
            for field, value in record.recommendation.model_dump().items():
                field_votes[field][value] += weight

        selected: dict[str, object] = {}
        confidence_parts: list[float] = []
        for field, votes in field_votes.items():
            value, value_weight = max(votes.items(), key=lambda item: item[1])
            selected[field] = value
            confidence_parts.append(value_weight / total_weight)

        confidence = sum(confidence_parts) / len(confidence_parts)
        return PrintSettings.model_validate(selected), confidence
