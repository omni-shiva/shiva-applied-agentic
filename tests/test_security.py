from reliability_agent.contracts import ContractStore
from reliability_agent.events import PipelineEventStore
from reliability_agent.knowledge import RunbookStore
from reliability_agent.settings import Settings
from reliability_agent.tools import ToolRegistry


def test_tool_registry_blocks_cross_tenant_arguments() -> None:
    settings = Settings()
    registry = ToolRegistry(
        events=PipelineEventStore(settings.data_dir / "pipeline_events.jsonl"),
        contracts=ContractStore(settings.data_dir / "contracts"),
        runbooks=RunbookStore(settings.data_dir / "runbooks"),
    )

    result = registry.execute(
        "query_pipeline_events",
        {"tenant_id": "tenant_beta", "pipeline_id": "finance_snapshot", "limit": 5},
        authorized_tenant="tenant_alpha",
    )

    assert result.status == "blocked"
    assert result.result == {"error": "tenant_scope_violation"}


def test_event_query_never_returns_another_tenant() -> None:
    settings = Settings()
    store = PipelineEventStore(settings.data_dir / "pipeline_events.jsonl")
    rows = store.recent("tenant_alpha", "orders_daily")

    assert rows
    assert {row["tenant_id"] for row in rows} == {"tenant_alpha"}
