"""Tests for Retriever."""

from uuid import uuid4

from agents.rag.chunker import chunk_text
from agents.rag.mock_embedder import MockEmbedder
from agents.rag.retriever import Retriever


def _populate(
    retriever: Retriever,
    *,
    user_id,
    document_id,
    text: str,
):
    chunks = chunk_text(
        document_id=document_id,
        user_id=user_id,
        text=text,
        chunk_size=100,
        overlap=10,
    )
    retriever.add_chunks(chunks)


class TestRetriever:
    def test_empty_store_returns_no_results(self):
        retriever = Retriever(MockEmbedder())
        results = retriever.search(user_id=uuid4(), query="python")
        assert results == []

    def test_returns_matching_chunks(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            document_id=uuid4(),
            text="Python is a programming language. " * 10,
        )
        results = retriever.search(user_id=user_id, query="python")
        assert len(results) > 0

    def test_ownership_enforced(self):
        """CRITICAL: user A cannot retrieve user B's chunks."""
        retriever = Retriever(MockEmbedder())
        user_a = uuid4()
        user_b = uuid4()

        _populate(
            retriever,
            user_id=user_a,
            document_id=uuid4(),
            text="Secret project code name is Falcon. " * 10,
        )
        _populate(
            retriever,
            user_id=user_b,
            document_id=uuid4(),
            text="Boring project about databases. " * 10,
        )

        # User B queries, should NOT see User A's secret
        results = retriever.search(user_id=user_b, query="Falcon secret")
        snippets = [r.chunk.text for r in results]
        assert all("Falcon" not in s for s in snippets)

    def test_top_k_limits_results(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            document_id=uuid4(),
            text="A " * 1000,
        )
        results = retriever.search(user_id=user_id, query="A", top_k=3)
        assert len(results) <= 3

    def test_min_score_filters(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            document_id=uuid4(),
            text="Python code. " * 20,
        )
        results = retriever.search(
            user_id=user_id, query="unrelated_xyz_term", min_score=0.9
        )
        assert results == []

    def test_results_sorted_by_score(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            document_id=uuid4(),
            text="Python django postgresql " * 20,
        )
        results = retriever.search(user_id=user_id, query="python")
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_ranks_are_sequential(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            document_id=uuid4(),
            text="Python django " * 50,
        )
        results = retriever.search(user_id=user_id, query="python", top_k=3)
        assert [r.rank for r in results] == list(range(len(results)))

    def test_clear_removes_all(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            document_id=uuid4(),
            text="Text " * 50,
        )
        retriever.clear()
        assert retriever.search(user_id=user_id, query="text") == []