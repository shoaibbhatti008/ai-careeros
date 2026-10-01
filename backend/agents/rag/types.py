"""Data types for RAG."""

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class Chunk:
    """A chunk of text from a document."""

    chunk_id: UUID
    document_id: UUID
    user_id: UUID
    text: str
    index: int
    start_offset: int
    end_offset: int
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Embedding:
    """An embedding vector associated with a chunk."""

    chunk_id: UUID
    vector: tuple[float, ...]
    model: str = "mock"
    dimension: int = 128


@dataclass(frozen=True)
class SearchResult:
    """A search result from the retriever."""

    chunk: Chunk
    score: float  # 0.0–1.0 (higher = better)
    rank: int  # 0-based
