"""Tests for TextChunker."""

from uuid import uuid4

import pytest

from agents.rag.chunker import TextChunker, chunk_text


class TestTextChunker:
    def test_empty_text_returns_no_chunks(self):
        chunks = chunk_text(
            document_id=uuid4(), user_id=uuid4(), text=""
        )
        assert chunks == []

    def test_short_text_produces_one_chunk(self):
        chunks = chunk_text(
            document_id=uuid4(),
            user_id=uuid4(),
            text="Short but sufficient text for one chunk.",
            chunk_size=100,
            overlap=10,  # ← explicitly set
        )
        assert len(chunks) == 1

    def test_long_text_produces_multiple_chunks(self):
        text = "word " * 500  # 2500 chars
        chunks = chunk_text(
            document_id=uuid4(),
            user_id=uuid4(),
            text=text,
            chunk_size=200,
            overlap=20,
        )
        assert len(chunks) > 5

    def test_chunks_preserve_user_id(self):
        user_id = uuid4()
        chunks = chunk_text(
            document_id=uuid4(),
            user_id=user_id,
            text="A " * 200,
            chunk_size=100,
            overlap=10,
        )
        assert all(c.user_id == user_id for c in chunks)

    def test_chunks_preserve_document_id(self):
        doc_id = uuid4()
        chunks = chunk_text(
            document_id=doc_id,
            user_id=uuid4(),
            text="A " * 200,
            chunk_size=100,
            overlap=10,
        )
        assert all(c.document_id == doc_id for c in chunks)

    def test_chunk_indices_are_sequential(self):
        chunks = chunk_text(
            document_id=uuid4(),
            user_id=uuid4(),
            text="A " * 500,
            chunk_size=100,
            overlap=10,
        )
        indices = [c.index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_offsets_are_monotonic(self):
        chunks = chunk_text(
            document_id=uuid4(),
            user_id=uuid4(),
            text="A " * 500,
            chunk_size=100,
            overlap=10,
        )
        for i in range(len(chunks) - 1):
            assert chunks[i].start_offset <= chunks[i + 1].start_offset

    def test_overlap_must_be_less_than_chunk_size(self):
        with pytest.raises(ValueError):
            TextChunker(chunk_size=100, overlap=100)

    def test_chunk_size_must_be_positive(self):
        with pytest.raises(ValueError):
            TextChunker(chunk_size=0)

    def test_metadata_is_attached(self):
        chunks = chunk_text(
            document_id=uuid4(),
            user_id=uuid4(),
            text="A " * 200,
            chunk_size=100,
            overlap=10,
            metadata={"source": "test"},
        )
        assert all(c.metadata["source"] == "test" for c in chunks)