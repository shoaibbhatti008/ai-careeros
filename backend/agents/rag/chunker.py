"""
Text chunking.

Chunking is deterministic and preserves offsets so we can cite
the original document positions.
"""

import re
from dataclasses import dataclass
from uuid import UUID, uuid4

from agents.rag.types import Chunk


@dataclass
class TextChunker:
    """
    Chunk text into overlapping windows.

    Args:
        chunk_size:    target characters per chunk (default 800)
        overlap:       overlap characters between chunks (default 100)
        min_chunk_len: minimum characters for a chunk to be kept (default 40)
    """

    chunk_size: int = 800
    overlap: int = 100
    min_chunk_len: int = 40

    def __post_init__(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if self.overlap < 0:
            raise ValueError("overlap must be >= 0")
        if self.overlap >= self.chunk_size:
            raise ValueError("overlap must be < chunk_size")

    def chunk(
        self,
        *,
        document_id: UUID,
        user_id: UUID,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """Chunk the text into overlapping windows."""
        text = text.strip()
        if not text:
            return []

        # Normalize whitespace to avoid tiny chunks
        normalized = re.sub(r"\s+", " ", text)

        chunks: list[Chunk] = []
        step = self.chunk_size - self.overlap
        start = 0
        idx = 0

        while start < len(normalized):
            end = min(start + self.chunk_size, len(normalized))
            piece = normalized[start:end].strip()
            if len(piece) >= self.min_chunk_len:
                chunks.append(
                    Chunk(
                        chunk_id=uuid4(),
                        document_id=document_id,
                        user_id=user_id,
                        text=piece,
                        index=idx,
                        start_offset=start,
                        end_offset=end,
                        metadata=metadata or {},
                    )
                )
                idx += 1

            if end == len(normalized):
                break
            start += step

        return chunks


def chunk_text(
    *,
    document_id: UUID,
    user_id: UUID,
    text: str,
    chunk_size: int = 800,
    overlap: int = 100,
    metadata: dict | None = None,
) -> list[Chunk]:
    """Convenience wrapper around TextChunker."""
    return TextChunker(chunk_size=chunk_size, overlap=overlap).chunk(
        document_id=document_id,
        user_id=user_id,
        text=text,
        metadata=metadata,
    )
