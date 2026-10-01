"""
Embedder interface.

Implementations:
- MockEmbedder (deterministic, no network)
- OpenAIEmbedder (future)
- SentenceTransformerEmbedder (future)
"""

from abc import ABC, abstractmethod

from agents.rag.types import Chunk


class Embedder(ABC):
    """Abstract embedder."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name (e.g. 'mock', 'text-embedding-3-small')."""
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding dimension."""
        raise NotImplementedError

    @abstractmethod
    def embed(self, text: str) -> tuple[float, ...]:
        """Embed a single text into a vector."""
        raise NotImplementedError

    def embed_chunks(self, chunks: list[Chunk]) -> list[tuple[float, ...]]:
        """Embed a list of chunks. Override for batching."""
        return [self.embed(c.text) for c in chunks]
