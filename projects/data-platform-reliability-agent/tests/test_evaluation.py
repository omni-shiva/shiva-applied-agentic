from reliability_agent.evaluation import run_evaluation
from reliability_agent.service import build_agent
from reliability_agent.settings import Settings


def test_versioned_evaluation_suite_passes() -> None:
    summary = run_evaluation(build_agent(), Settings().eval_cases_path)

    assert summary.total_cases == 25
    assert summary.pass_rate == 1.0
    assert summary.required_tool_trace_rate == 1.0
    assert summary.evidence_present_rate == 1.0
    assert summary.approval_guard_rate == 1.0
