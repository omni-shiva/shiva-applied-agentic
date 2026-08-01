import math

from reliability_agent.embeddings import hash_embedding


def test_hash_embedding_is_deterministic_and_normalized() -> None:
    first = hash_embedding("schema contract missing column")
    second = hash_embedding("schema contract missing column")

    assert first == second
    assert len(first) == 256
    assert math.isclose(sum(value * value for value in first), 1.0, rel_tol=1e-9)
