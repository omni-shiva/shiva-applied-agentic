from __future__ import annotations

from .data_io import load_seed_documents
from .generator import SyntheticCorpusGenerator
from .models import DocumentProfile, RecommendationResponse, ScarcityReport
from .recommender import PrintRecommendationAgent
from .scarcity import analyse_scarcity
from .settings import Settings


class PrintRecommendationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.seed_documents = load_seed_documents(self.settings.seed_path)
        self.generator = SyntheticCorpusGenerator(self.settings.random_seed)
        self.training_records = self.generator.generate(
            self.seed_documents, self.settings.training_scale
        )
        self.agent = PrintRecommendationAgent(self.settings.review_confidence_threshold)
        self.agent.fit(self.training_records)

    def scarcity_report(self) -> ScarcityReport:
        return analyse_scarcity(self.seed_documents)

    def recommend(self, document: DocumentProfile) -> RecommendationResponse:
        return self.agent.recommend(document)


def build_service(settings: Settings | None = None) -> PrintRecommendationService:
    return PrintRecommendationService(settings)
