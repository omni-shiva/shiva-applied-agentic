from __future__ import annotations

import random
from itertools import product

from .features import CATEGORIES, PAGE_SIZES, PRIORITIES
from .models import DocumentProfile, LabeledDocument
from .rules import label_review_reasons, recommendation_policy

RATIO_BASES = {
    "invoice": (0.90, 0.10, 0.05),
    "report": (0.72, 0.28, 0.18),
    "brochure": (0.35, 0.65, 0.78),
    "photo": (0.05, 0.95, 0.96),
    "presentation": (0.45, 0.55, 0.68),
}


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


class SyntheticCorpusGenerator:
    def __init__(self, random_seed: int = 42) -> None:
        self._random_seed = random_seed

    def generate(self, seed_documents: list[DocumentProfile], scale: int) -> list[LabeledDocument]:
        if not seed_documents:
            raise ValueError("at least one seed document is required")
        if scale not in {1, 10, 100}:
            raise ValueError("scale must be one of 1, 10 or 100")

        records = [
            LabeledDocument(
                document=document,
                recommendation=recommendation_policy(document),
                label_source="seed",
                label_review_required=bool(label_review_reasons(document)),
            )
            for document in seed_documents
        ]
        target_rows = len(seed_documents) * scale
        if target_rows == len(records):
            return records

        rng = random.Random(self._random_seed + scale)
        target_strata = list(product(CATEGORIES, PAGE_SIZES, PRIORITIES))

        for index in range(len(records), target_rows):
            stratum_index = (index - len(seed_documents)) % len(target_strata)
            cycle = (index - len(seed_documents)) // len(target_strata)
            category, page_size, priority = target_strata[stratum_index]
            parent = seed_documents[index % len(seed_documents)]
            _, image_base, color_base = RATIO_BASES[category]
            image_ratio = _bounded(image_base + rng.uniform(-0.09, 0.09))
            text_ratio = _bounded(1.0 - image_ratio)
            color_ratio = _bounded(color_base + rng.uniform(-0.10, 0.10))

            if category == "photo":
                page_count = 1 + (cycle % 3)
            elif category in {"brochure", "presentation"}:
                page_count = 2 + ((stratum_index + cycle) % 15)
            else:
                page_count = 1 + ((stratum_index * 3 + cycle) % 48)

            document = DocumentProfile(
                document_id=f"synthetic_{scale}x_{index:04d}",
                category=category,
                text_ratio=text_ratio,
                image_ratio=image_ratio,
                color_ratio=color_ratio,
                page_size=page_size,
                page_count=page_count,
                quality_priority=priority,
            )
            records.append(
                LabeledDocument(
                    document=document,
                    recommendation=recommendation_policy(document),
                    label_source="synthetic_policy",
                    parent_document_id=parent.document_id,
                    label_review_required=bool(label_review_reasons(document)),
                )
            )

        return records
