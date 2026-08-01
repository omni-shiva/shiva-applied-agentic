from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path


class PipelineEventStore:
    def __init__(self, event_path: Path) -> None:
        self._connection = sqlite3.connect(":memory:", check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._create_schema()
        self._load(event_path)

    def _create_schema(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE pipeline_events (
                tenant_id TEXT NOT NULL,
                pipeline_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                status TEXT NOT NULL,
                error_code TEXT,
                message TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                sla_seconds INTEGER NOT NULL,
                records_in INTEGER NOT NULL,
                records_out INTEGER NOT NULL,
                retry_count INTEGER NOT NULL,
                PRIMARY KEY (tenant_id, pipeline_id, run_id)
            )
            """
        )

    def _load(self, event_path: Path) -> None:
        records = [json.loads(line) for line in event_path.read_text().splitlines() if line.strip()]
        columns = tuple(records[0])
        placeholders = ",".join("?" for _ in columns)
        sql = f"INSERT INTO pipeline_events ({','.join(columns)}) VALUES ({placeholders})"
        with self._connection:
            values = [tuple(record[col] for col in columns) for record in records]
            self._connection.executemany(sql, values)

    def recent(self, tenant_id: str, pipeline_id: str, limit: int = 8) -> list[dict[str, object]]:
        sql = """
            SELECT *
            FROM pipeline_events
            WHERE tenant_id = ? AND pipeline_id = ?
            ORDER BY observed_at DESC
            LIMIT ?
        """
        with self._lock:
            rows = self._connection.execute(sql, (tenant_id, pipeline_id, limit)).fetchall()
        return [dict(row) for row in rows]
