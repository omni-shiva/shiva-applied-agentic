from __future__ import annotations

from .models import DocumentProfile, PrintSettings


def recommendation_policy(document: DocumentProfile) -> PrintSettings:
    """Create synthetic labels. This policy is not treated as real ground truth."""
    color_mode = (
        "color"
        if document.color_ratio >= 0.30
        or document.category in {"brochure", "photo", "presentation"}
        else "grayscale"
    )

    if document.quality_priority == "premium" and document.image_ratio >= 0.55:
        dpi = 1200
    elif document.image_ratio >= 0.35 or document.quality_priority == "premium":
        dpi = 600
    else:
        dpi = 300

    duplex = document.page_count >= 4 and document.category in {"invoice", "report"}
    quality_mode = {
        "economy": "draft",
        "standard": "standard",
        "premium": "high",
    }[document.quality_priority]

    return PrintSettings(
        color_mode=color_mode,
        dpi=dpi,
        duplex=duplex,
        paper_size=document.page_size,
        quality_mode=quality_mode,
    )


def label_review_reasons(document: DocumentProfile) -> list[str]:
    reasons: list[str] = []
    if abs(document.color_ratio - 0.30) <= 0.03:
        reasons.append("colour ratio is close to the policy boundary")
    if abs(document.image_ratio - 0.55) <= 0.03:
        reasons.append("image ratio is close to the premium-resolution boundary")
    if document.page_size == "A3" and document.category in {"invoice", "photo"}:
        reasons.append("the category and page-size combination is uncommon")
    return reasons
