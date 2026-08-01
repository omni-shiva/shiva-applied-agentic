from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI

from .models import DocumentProfile, RecommendationResponse, ScarcityReport
from .service import PrintRecommendationService, build_service

app = FastAPI(
    title="Synthetic Data and Print Recommendation Agent",
    version="0.1.0",
    description="Synthetic portfolio API with evaluation and human-review boundaries.",
)


@lru_cache(maxsize=1)
def get_service() -> PrintRecommendationService:
    return build_service()


ServiceDependency = Annotated[PrintRecommendationService, Depends(get_service)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(service: ServiceDependency) -> dict[str, object]:
    return {
        "status": "ready",
        "training_scale": service.settings.training_scale,
        "training_rows": len(service.training_records),
    }


@app.get("/v1/scarcity", response_model=ScarcityReport)
def scarcity(service: ServiceDependency) -> ScarcityReport:
    return service.scarcity_report()


@app.post("/v1/recommend", response_model=RecommendationResponse)
def recommend(
    document: DocumentProfile,
    service: ServiceDependency,
) -> RecommendationResponse:
    return service.recommend(document)
