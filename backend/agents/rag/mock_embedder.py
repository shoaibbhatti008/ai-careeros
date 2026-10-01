"""
Mock embedder for deterministic testing.

Produces a bag-of-words hashed embedding. Not semantically meaningful,
but stable and reproducible.
"""

import hashlib

from agents.rag.embedder import Embedder


class MockEmbedder(Embedder):
    """
    Deterministic, hash-based embedder.

    The embedding is a fixed-dimension vector derived from token hashes.
    Similar texts produce similar vectors (bag-of-words behavior).
    """

    def __init__(self, dimension: int = 128) -> None:
        self._dim = dimension

    @property
    def name(self) -> str:
        return "mock"

    @property
    def dimension(self) -> int:
        return self._dim

    def embed(self, text: str) -> tuple[float, ...]:
        vec = [0.0] * self._dim
        tokens = text.lower().split()
        if not tokens:
            return tuple(vec)

        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)  # noqa: S324
            idx = h % self._dim
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign

        # Normalize to unit length (avoid div-by-zero)
        norm = sum(v * v for v in vec) ** 0.5
        if norm == 0:
            return tuple(vec)
        return tuple(v / norm for v in vec)
