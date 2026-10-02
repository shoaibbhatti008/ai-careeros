# RAG (Retrieval-Augmented Generation)

The RAG pipeline lets users ask questions grounded in their own documents.

## Pipeline

Upload → Validate → Extract → Chunk → Embed → Store

Query → Embed → Ownership Filter → Retrieve → Agent → Answer + Sources

## Ownership guarantee

Every query is filtered by user_id at the retriever layer. Even if
an agent tries, it cannot access chunks belonging to another user.

## Components

| Component | Purpose |
|-----------|---------|
| TextChunker | Splits text into overlapping windows |
| MockEmbedder | Deterministic hash-based embedder |
| Embedder | Interface for real embedders |
| Retriever | In-memory store with per-user isolation |
| DocumentSearchTool | Wraps retriever as a tool |
| RAGAgent | Answers questions with citations |

## Chunking example

    from uuid import uuid4
    from agents.rag.chunker import chunk_text

    chunks = chunk_text(
        document_id=uuid4(),
        user_id=uuid4(),
        text="Your long document...",
        chunk_size=800,
        overlap=100,
    )

Each Chunk includes:
- text
- index (0-based)
- start_offset, end_offset (for citation)
- document_id, user_id

## Retrieval example

    from agents.rag.retriever import Retriever
    from agents.rag.mock_embedder import MockEmbedder

    retriever = Retriever(MockEmbedder())
    retriever.add_chunks(chunks)

    results = retriever.search(
        user_id=user_id,
        query="python tutorial",
        top_k=5,
        min_score=0.3,
    )

## Using RAGAgent

    from agents.context import AgentContext
    from agents.implementations.rag_agent import RAGAgent

    ctx = AgentContext(
        user_id=user_id,
        allowed_tools=frozenset({"document_search"}),
        tool_executor=my_executor,
        metadata={"retriever": retriever},
    )
    agent = RAGAgent(ctx)
    result = agent.execute({"query": "What projects did I work on?"})

## Production swap-in

Replace MockEmbedder with a real embedder.

Replace Retriever with a pgvector-backed store.

The interface stays the same, so no agent code changes.

## Testing RAG

    def test_ownership_isolation():
        retriever = Retriever(MockEmbedder())
        _populate(retriever, user_id=user_a, text="Secret CodeWord Alpha")
        results = retriever.search(user_id=user_b, query="CodeWord Alpha")
        assert len(results) == 0

## Security guarantees

1. Ownership enforced at retriever
2. Chunks carry user_id
3. No cross-user leakage
4. Document tools accept no user_id from input