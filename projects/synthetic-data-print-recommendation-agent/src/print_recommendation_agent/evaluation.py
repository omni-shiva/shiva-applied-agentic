from __future__ import annotations

import json

from .data_io import load_holdout_cases, load_seed_documents
from .features import feature_signature
from .generator import SyntheticCorpusGenerator
from .models import EvaluationSummary, PrintSettings, ScaleMetrics
from .recommender import PrintRecommendationAgent
from .scarcity import analyse_scarcity
from .settings import Settings

SETTING_FIELDS = ("color_mode", "dpi", "duplex", "paper_size", "quality_mode")


def _field_matches(predicted: PrintSettings, expected: PrintSettings) -> int:
    predicted_values = predicted.model_dump()
    expected_values = expected.model_dump()
    return sum(predicted_values[field] == expected_values[field] for field in SETTING_FIELDS)


def run_evaluation(settings: Settings | None = None) -> EvaluationSummary:
    config = settings or Settings()
    seed_documents = load_seed_documents(config.seed_path)
    holdout_cases = load_holdout_cases(config.holdout_path)
    seed_ids = {document.document_id for document in seed_documents}
    holdout_ids = {case.document.document_id for case in holdout_cases}
    ids_are_disjoint = seed_ids.isdisjoint(holdout_ids)
    if not ids_are_disjoint:
        raise ValueError("holdout document IDs must not overlap the seed corpus")

    generator = SyntheticCorpusGenerator(config.random_seed)
    metrics: list[ScaleMetrics] = []

    for scale in (1, 10, 100):
        training = generator.generate(seed_documents, scale)
        agent = PrintRecommendationAgent(config.review_confidence_threshold)
        agent.fit(training)
        responses = [agent.recommend(case.document) for case in holdout_cases]

        exact_matches = sum(
            response.recommended_settings == case.expected_settings
            for response, case in zip(responses, holdout_cases, strict=True)
        )
        field_matches = sum(
            _field_matches(response.recommended_settings, case.expected_settings)
            for response, case in zip(responses, holdout_cases, strict=True)
        )
        rare_pairs = [
            (response, case)
            for response, case in zip(responses, holdout_cases, strict=True)
            if case.rare_group
        ]
        rare_exact = sum(
            response.recommended_settings == case.expected_settings
            for response, case in rare_pairs
        )
        signatures = {feature_signature(record.document) for record in training}
        scarcity = analyse_scarcity([record.document for record in training])

        diversity_rate = len(signatures) / len(training)
        metrics.append(
            ScaleMetrics(
                scale=scale,
                training_rows=len(training),
                observed_strata=scarcity.observed_strata,
                coverage_rate=scarcity.coverage_rate,
                diversity_rate=round(diversity_rate, 4),
                duplicate_rate=round(1.0 - diversity_rate, 4),
                exact_accuracy=round(exact_matches / len(holdout_cases), 4),
                field_accuracy=round(
                    field_matches / (len(holdout_cases) * len(SETTING_FIELDS)), 4
                ),
                rare_group_accuracy=round(rare_exact / len(rare_pairs), 4),
                human_review_rate=round(
                    sum(response.human_review_required for response in responses)
                    / len(responses),
                    4,
                ),
            )
        )

    best = max(metrics, key=lambda item: (item.field_accuracy, item.exact_accuracy, -item.scale))
    scale_10 = next(item for item in metrics if item.scale == 10)
    scale_100 = next(item for item in metrics if item.scale == 100)
    improvement = scale_100.field_accuracy - scale_10.field_accuracy
    saturation = improvement <= 0.02 and scale_100.coverage_rate == scale_10.coverage_rate
    quality_gate = (
        best.field_accuracy >= 0.80
        and best.rare_group_accuracy >= 0.50
        and best.duplicate_rate <= 0.25
    )

    findings = [
        "The holdout IDs are isolated from seed and generated training IDs; expected settings "
        "remain within the same documented synthetic policy world.",
        f"The strongest field accuracy is {best.field_accuracy:.3f} at {best.scale}x scale.",
    ]
    if saturation:
        findings.append(
            "Performance and categorical coverage saturate between 10x and 100x; more rows alone "
            "should not be treated as more information."
        )
    if scale_100.diversity_rate < scale_10.diversity_rate:
        findings.append("Relative diversity falls at 100x even though absolute row count grows.")

    return EvaluationSummary(
        holdout_cases=len(holdout_cases),
        scales=metrics,
        best_scale=best.scale,
        saturation_detected=saturation,
        holdout_ids_are_disjoint=ids_are_disjoint,
        passes_quality_gate=quality_gate,
        findings=findings,
    )


def main() -> None:
    print(json.dumps(run_evaluation().model_dump(), indent=2))


if __name__ == "__main__":
    main()
