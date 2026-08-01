from __future__ import annotations

import json
import uuid
from pathlib import Path

from qdrant_client import QdrantClient, models

from .embeddings import hash_embedding, tokenize

COLLECTION = "pipeline_runbooks"
VECTOR_SIZE = 256


class RunbookStore:
    def __init__(self, runbook_dir: Path) -> None:
        self._runbook_dir = runbook_dir
        self._client = QdrantClient(":memory:")
        self._client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
        )
        self._load()

    def _load(self) -> None:
        records = json.loads((self._runbook_dir / "index.json").read_text(encoding="utf-8"))
        points: list[models.PointStruct] = []
        for record in records:
            text = (self._runbook_dir / record["file"]).read_text(encoding="utf-8")
            payload = {**record, "text": text}
            point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"runbook:{record['id']}"))
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=hash_embedding(f"{record['title']} {' '.join(record['tags'])} {text}"),
                    payload=payload,
                )
            )
        self._client.upsert(collection_name=COLLECTION, points=points, wait=True)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, object]]:
        response = self._client.query_points(
            collection_name=COLLECTION,
            query=hash_embedding(query),
            limit=10,
            with_payload=True,
        )
        query_terms = set(tokenize(query))
        matches: list[dict[str, object]] = []
        for point in response.points:
            payload = point.payload or {}
            metadata = f"{payload.get('title', '')} {' '.join(payload.get('tags', []))}"
            overlap = query_terms.intersection(tokenize(metadata))
            keyword_score = min(1.0, len(overlap) / 2)
            combined_score = (0.35 * float(point.score)) + (0.65 * keyword_score)
            matches.append(
                {
                    "source_id": payload.get("id", "unknown"),
                    "title": payload.get("title", "Untitled runbook"),
                    "tags": payload.get("tags", []),
                    "score": round(max(0.0, min(1.0, combined_score)), 4),
                    "excerpt": str(payload.get("text", ""))[:700],
                }
            )
        matches.sort(key=lambda match: float(match["score"]), reverse=True)
        return matches[:top_k]
