"""
Retriever: ownership-enforced vector search over chunks.

CRITICAL: Every query filters by user_id at the retriever layer.
This is the last line of defense against cross-user data leakage.
"""

from dataclasses import dataclass
from uuid import UUID

from agents.rag.embedder import Embedder
from agents.rag.types import Chunk, SearchResult


@dataclass
class _StoredChunk:
    """Internal storage: chunk + its embedding."""

    chunk: Chunk
    vector: tuple[float, ...]


class Retriever:
    """
    In-memory retriever with per-user isolation.

    For production, replace with pgvector or similar; the interface
    (add_chunks, search) stays the same.
    """

    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder
        self._store: dict[UUID, list[_StoredChunk]] = {}  # user_id → chunks

    # ==========================================================
    # Write
    # ==========================================================

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """Store chunks with their embeddings, indexed by user_id."""
        for chunk in chunks:
            vec = self._embedder.embed(chunk.text)
            self._store.setdefault(chunk.user_id, []).append(_StoredChunk(chunk=chunk, vector=vec))

    def clear(self) -> None:
        """Remove all stored chunks (used in tests)."""
        self._store.clear()

    # ==========================================================
    # Read (ownership enforced)
    # ==========================================================

    def search(
        self,
        *,
        user_id: UUID,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[SearchResult]:
        """
        Search for chunks belonging to `user_id` only.

        Args:
            user_id:   owner of the chunks (mandatory)
            query:     query text
            top_k:     maximum results
            min_score: minimum cosine score

        Returns:
            Sorted list of SearchResult (descending by score).
        """
        user_chunks = self._store.get(user_id, [])
        if not user_chunks:
            return []

        query_vec = self._embedder.embed(query)
        scored: list[tuple[float, _StoredChunk]] = []
        for stored in user_chunks:
            score = self._cosine(query_vec, stored.vector)
            if score >= min_score:
                scored.append((score, stored))

        scored.sort(key=lambda x: x[0], reverse=True)

        results: list[SearchResult] = []
        for rank, (score, stored) in enumerate(scored[:top_k]):
            results.append(SearchResult(chunk=stored.chunk, score=round(score, 4), rank=rank))
        return results

    @staticmethod
    def _cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
        """Cosine similarity for normalized vectors (dot product)."""
        if len(a) != len(b):
            return 0.0
        return sum(x * y for x, y in zip(a, b, strict=False))
