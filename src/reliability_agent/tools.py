from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import ContractStore
from .events import PipelineEventStore
from .knowledge import RunbookStore


@dataclass
class ToolExecution:
    name: str
    status: str
    summary: str
    result: dict[str, Any]


class ToolRegistry:
    def __init__(
        self,
        events: PipelineEventStore,
        contracts: ContractStore,
        runbooks: RunbookStore,
    ) -> None:
        self._events = events
        self._contracts = contracts
        self._runbooks = runbooks

    @staticmethod
    def definitions() -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "name": "query_pipeline_events",
                "description": (
                    "Read recent synthetic run events for one authorized tenant and pipeline."
                ),
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "pipeline_id": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                    "required": ["tenant_id", "pipeline_id", "limit"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "inspect_pipeline_contract",
                "description": (
                    "Compare the expected and latest observed schema for one authorized pipeline."
                ),
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "pipeline_id": {"type": "string"},
                    },
                    "required": ["tenant_id", "pipeline_id"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "search_runbooks",
                "description": (
                    "Retrieve relevant operational runbooks from the local Qdrant vector store."
                ),
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "pipeline_id": {"type": "string"},
                        "query": {"type": "string"},
                        "top_k": {"type": "integer", "minimum": 1, "maximum": 5},
                    },
                    "required": ["tenant_id", "pipeline_id", "query", "top_k"],
                    "additionalProperties": False,
                },
            },
        ]

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        authorized_tenant: str,
    ) -> ToolExecution:
        requested_tenant = arguments.get("tenant_id")
        if requested_tenant != authorized_tenant:
            return ToolExecution(
                name=name,
                status="blocked",
                summary="Tenant boundary blocked the tool call.",
                result={"error": "tenant_scope_violation"},
            )

        if name == "query_pipeline_events":
            events = self._events.recent(
                tenant_id=authorized_tenant,
                pipeline_id=str(arguments["pipeline_id"]),
                limit=int(arguments["limit"]),
            )
            return ToolExecution(
                name=name,
                status="ok",
                summary=f"Retrieved {len(events)} tenant-scoped run events.",
                result={"events": events},
            )

        if name == "inspect_pipeline_contract":
            result = self._contracts.inspect(
                tenant_id=authorized_tenant,
                pipeline_id=str(arguments["pipeline_id"]),
            )
            return ToolExecution(
                name=name,
                status="ok",
                summary="Compared expected and observed contract fields.",
                result=result,
            )

        if name == "search_runbooks":
            matches = self._runbooks.search(str(arguments["query"]), int(arguments["top_k"]))
            return ToolExecution(
                name=name,
                status="ok",
                summary=f"Retrieved {len(matches)} runbook passages.",
                result={"matches": matches},
            )

        return ToolExecution(
            name=name,
            status="error",
            summary="Unknown tool was rejected.",
            result={"error": "unknown_tool"},
        )
