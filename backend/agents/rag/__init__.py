"""Retrieval-Augmented Generation (RAG).

Design principles:
- Ownership is enforced at the retrieval layer, not the prompt layer.
- Every chunk carries a user_id; retrieval filters by it.
- Embeddings are pluggable (mock for tests, real provider later).
- Chunking is deterministic and reversible (chunk → original offset).
"""

from agents.rag.chunker import TextChunker, chunk_text
from agents.rag.embedder import Embedder
from agents.rag.mock_embedder import MockEmbedder
from agents.rag.retriever import Retriever
from agents.rag.types import Chunk, Embedding, SearchResult

__all__ = [
    "Chunk",
    "Embedding",
    "SearchResult",
    "TextChunker",
    "chunk_text",
    "Embedder",
    "MockEmbedder",
    "Retriever",
]
