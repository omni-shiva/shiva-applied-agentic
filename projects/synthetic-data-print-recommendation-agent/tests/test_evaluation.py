from print_recommendation_agent.evaluation import run_evaluation


def test_independent_scale_evaluation_passes_quality_gate() -> None:
    summary = run_evaluation()

    assert summary.holdout_cases == 12
    assert [item.scale for item in summary.scales] == [1, 10, 100]
    assert [item.training_rows for item in summary.scales] == [12, 120, 1200]
    assert summary.holdout_is_independent is True
    assert summary.passes_quality_gate is True
