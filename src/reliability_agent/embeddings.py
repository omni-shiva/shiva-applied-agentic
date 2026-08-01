from __future__ import annotations

import hashlib
import math
import re

TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower().replace("_", " "))


def hash_embedding(text: str, dimensions: int = 256) -> list[float]:
    """Create a deterministic local embedding for the zero-cost demo path."""
    tokens = tokenize(text)
    features = tokens + [f"{left}:{right}" for left, right in zip(tokens, tokens[1:], strict=False)]
    vector = [0.0] * dimensions

    for feature in features:
        digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        vector[bucket] += 1.0

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]
