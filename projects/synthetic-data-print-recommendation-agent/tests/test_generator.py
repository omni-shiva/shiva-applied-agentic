from print_recommendation_agent.data_io import load_holdout_cases, load_seed_documents
from print_recommendation_agent.generator import SyntheticCorpusGenerator
from print_recommendation_agent.scarcity import analyse_scarcity
from print_recommendation_agent.settings import Settings


def test_generator_is_deterministic_and_respects_scale() -> None:
    settings = Settings()
    seeds = load_seed_documents(settings.seed_path)
    generator = SyntheticCorpusGenerator(settings.random_seed)

    first = generator.generate(seeds, 10)
    second = generator.generate(seeds, 10)

    assert len(first) == len(seeds) * 10
    assert [record.model_dump() for record in first] == [
        record.model_dump() for record in second
    ]


def test_generation_improves_categorical_coverage() -> None:
    settings = Settings()
    seeds = load_seed_documents(settings.seed_path)
    generator = SyntheticCorpusGenerator(settings.random_seed)

    seed_report = analyse_scarcity(seeds)
    generated = generator.generate(seeds, 10)
    generated_report = analyse_scarcity([record.document for record in generated])

    assert generated_report.coverage_rate > seed_report.coverage_rate
    assert generated_report.observed_strata == generated_report.target_strata


def test_holdout_ids_are_not_used_for_training() -> None:
    settings = Settings()
    seeds = load_seed_documents(settings.seed_path)
    holdout = load_holdout_cases(settings.holdout_path)
    training = SyntheticCorpusGenerator(settings.random_seed).generate(seeds, 100)

    training_ids = {record.document.document_id for record in training}
    holdout_ids = {case.document.document_id for case in holdout}

    assert training_ids.isdisjoint(holdout_ids)
