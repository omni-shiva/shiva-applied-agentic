from __future__ import annotations

import math

from .models import DocumentProfile

CATEGORIES = ("invoice", "report", "brochure", "photo", "presentation")
PAGE_SIZES = ("A4", "A3", "Letter")
PRIORITIES = ("economy", "standard", "premium")


def _one_hot(value: str, options: tuple[str, ...]) -> tuple[float, ...]:
    return tuple(1.0 if value == option else 0.0 for option in options)


def feature_vector(document: DocumentProfile) -> tuple[float, ...]:
    """Create a transparent feature vector without external model dependencies."""
    return (
        *_one_hot(document.category, CATEGORIES),
        *_one_hot(document.page_size, PAGE_SIZES),
        *_one_hot(document.quality_priority, PRIORITIES),
        document.text_ratio,
        document.image_ratio,
        document.color_ratio,
        min(1.0, math.log1p(document.page_count) / math.log(501)),
        float(document.image_ratio >= 0.55),
        float(document.color_ratio >= 0.30),
        float(document.page_count >= 8),
    )


def feature_distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right):
        raise ValueError("feature vectors must have the same length")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))


def feature_signature(document: DocumentProfile) -> tuple[object, ...]:
    """A bounded signature used to identify repetitive synthetic profiles."""
    return (
        document.category,
        document.page_size,
        document.quality_priority,
        round(document.text_ratio, 2),
        round(document.image_ratio, 2),
        round(document.color_ratio, 2),
        document.page_count,
    )
