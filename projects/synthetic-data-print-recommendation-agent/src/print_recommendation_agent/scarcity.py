from __future__ import annotations

from collections import Counter
from itertools import product

from .features import CATEGORIES, PAGE_SIZES, PRIORITIES
from .models import DocumentProfile, ScarcityReport


def _stratum(document: DocumentProfile) -> tuple[str, str, str]:
    return document.category, document.page_size, document.quality_priority


def analyse_scarcity(documents: list[DocumentProfile]) -> ScarcityReport:
    if not documents:
        raise ValueError("at least one document is required")

    category_counts = Counter(document.category for document in documents)
    observed = {_stratum(document) for document in documents}
    target = set(product(CATEGORIES, PAGE_SIZES, PRIORITIES))
    rare_limit = max(1, round(len(documents) * 0.15))
    rare_categories = sorted(
        category for category in CATEGORIES if category_counts.get(category, 0) <= rare_limit
    )
    missing = ["/".join(parts) for parts in sorted(target - observed)]

    return ScarcityReport(
        total_documents=len(documents),
        category_counts={category: category_counts.get(category, 0) for category in CATEGORIES},
        observed_strata=len(observed),
        target_strata=len(target),
        coverage_rate=round(len(observed) / len(target), 4),
        rare_categories=rare_categories,
        missing_strata=missing,
    )
