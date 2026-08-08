from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DocumentCategory = Literal["invoice", "report", "brochure", "photo", "presentation"]
PageSize = Literal["A4", "A3", "Letter"]
QualityPriority = Literal["economy", "standard", "premium"]
ColorMode = Literal["grayscale", "color"]
QualityMode = Literal["draft", "standard", "high"]


class DocumentProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=3, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    category: DocumentCategory
    text_ratio: float = Field(ge=0.0, le=1.0)
    image_ratio: float = Field(ge=0.0, le=1.0)
    color_ratio: float = Field(ge=0.0, le=1.0)
    page_size: PageSize
    page_count: int = Field(ge=1, le=500)
    quality_priority: QualityPriority


class PrintSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    color_mode: ColorMode
    dpi: Literal[300, 600, 1200]
    duplex: bool
    paper_size: PageSize
    quality_mode: QualityMode


class LabeledDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document: DocumentProfile
    recommendation: PrintSettings
    label_source: Literal["seed", "synthetic_policy"]
    parent_document_id: str | None = None
    label_review_required: bool = False


class HoldoutCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document: DocumentProfile
    expected_settings: PrintSettings
    rare_group: bool = False
    label_source: Literal["synthetic_policy_holdout"] = "synthetic_policy_holdout"


class ScarcityReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_documents: int
    category_counts: dict[str, int]
    observed_strata: int
    target_strata: int
    coverage_rate: float
    rare_categories: list[str]
    missing_strata: list[str]


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str
    recommended_settings: PrintSettings
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_document_ids: list[str]
    reasons: list[str]
    human_review_required: bool
    review_reasons: list[str]
    execution_performed: Literal[False] = False


class ScaleMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scale: Literal[1, 10, 100]
    training_rows: int
    observed_strata: int
    coverage_rate: float
    diversity_rate: float
    duplicate_rate: float
    exact_accuracy: float
    field_accuracy: float
    rare_group_accuracy: float
    human_review_rate: float


class EvaluationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    holdout_cases: int
    scales: list[ScaleMetrics]
    best_scale: Literal[1, 10, 100]
    saturation_detected: bool
    holdout_ids_are_disjoint: bool
    passes_quality_gate: bool
    findings: list[str]
