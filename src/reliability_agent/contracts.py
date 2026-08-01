from __future__ import annotations

import json
from pathlib import Path


class ContractStore:
    def __init__(self, contract_dir: Path) -> None:
        self._contracts: dict[tuple[str, str], dict[str, object]] = {}
        for path in contract_dir.glob("*.json"):
            contract = json.loads(path.read_text(encoding="utf-8"))
            key = (str(contract["tenant_id"]), str(contract["pipeline_id"]))
            self._contracts[key] = contract

    def inspect(self, tenant_id: str, pipeline_id: str) -> dict[str, object]:
        contract = self._contracts.get((tenant_id, pipeline_id))
        if contract is None:
            return {"found": False, "tenant_id": tenant_id, "pipeline_id": pipeline_id}

        expected = set(contract["expected_columns"])
        observed = set(contract["last_observed_columns"])
        return {
            **contract,
            "found": True,
            "missing_columns": sorted(expected - observed),
            "unexpected_columns": sorted(observed - expected),
            "schema_matches": expected == observed,
        }
