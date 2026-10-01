"""Tests for RAGAgent."""

from uuid import uuid4

import pytest

from agents.context import AgentBudgets, AgentContext
from agents.implementations.rag_agent import RAGAgent
from agents.rag.chunker import chunk_text
from agents.rag.mock_embedder import MockEmbedder
from agents.rag.retriever import Retriever
from agents.registry import AgentRegistry
from agents.tools.base import ToolContext
from agents.tools.career.document_search import DocumentSearchTool
from agents.tools.registry import ToolRegistry, execute_tool


@pytest.fixture(autouse=True)
def register_rag_agent_and_tool():
    ToolRegistry._tools.setdefault("document_search", DocumentSearchTool)
    AgentRegistry._agents.setdefault("rag_agent", RAGAgent)
    yield


def _make_context(
    *,
    retriever: Retriever,
    user_id,
    allowed_tools: frozenset[str] | None = None,
) -> AgentContext:
    if allowed_tools is None:
        tools = frozenset({"document_search"})
    else:
        tools = allowed_tools

    def tool_executor(tool_name: str, **kwargs: object) -> dict:
        tool_context = ToolContext(
            user_id=str(user_id),
            metadata={"retriever": retriever},
        )
        return execute_tool(
            tool_name=tool_name,
            agent_name="rag_agent",
            agent_allowed_tools=RAGAgent.allowed_tools,
            context_allowed_tools=tools,
            input_data=dict(kwargs),
            tool_context=tool_context,
        )

    return AgentContext(
        user_id=user_id,
        allowed_tools=tools,
        tool_executor=tool_executor,
    )


def _populate(retriever: Retriever, *, user_id, text: str):
    chunks = chunk_text(
        document_id=uuid4(),
        user_id=user_id,
        text=text,
        chunk_size=100,
        overlap=10,
    )
    retriever.add_chunks(chunks)


class TestRAGAgent:
    def test_answers_from_documents(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            text="Python is a versatile programming language. " * 10,
        )
        ctx = _make_context(retriever=retriever, user_id=user_id)
        agent = RAGAgent(ctx)
        result = agent.execute({"query": "python programming"})
        assert result.status.value == "completed"
        assert result.output["retrieved_count"] > 0

    def test_no_documents_returns_empty(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        ctx = _make_context(retriever=retriever, user_id=user_id)
        agent = RAGAgent(ctx)
        result = agent.execute({"query": "anything"})
        assert result.status.value == "completed"
        assert result.output["retrieved_count"] == 0
        assert result.output["citations"] == []

    def test_empty_query_fails(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        ctx = _make_context(retriever=retriever, user_id=user_id)
        agent = RAGAgent(ctx)
        result = agent.execute({"query": ""})
        assert result.status.value == "failed"

    def test_citations_included(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            text="Python code patterns. " * 20,
        )
        ctx = _make_context(retriever=retriever, user_id=user_id)
        agent = RAGAgent(ctx)
        result = agent.execute({"query": "python"})
        assert len(result.output["citations"]) > 0
        citation = result.output["citations"][0]
        assert "document_id" in citation
        assert "chunk_index" in citation
        assert "score" in citation

    def test_ownership_isolation(self):
        """User A cannot see User B's documents."""
        retriever = Retriever(MockEmbedder())
        user_a = uuid4()
        user_b = uuid4()

        _populate(
            retriever,
            user_id=user_a,
            text="Secret_CodeWord_Alpha is the project name. " * 10,
        )

        # User B queries for A's secret
        ctx = _make_context(retriever=retriever, user_id=user_b)
        agent = RAGAgent(ctx)
        result = agent.execute({"query": "Secret_CodeWord_Alpha"})
        assert result.output["retrieved_count"] == 0

    def test_top_k_respected(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            text="word " * 1000,
        )
        ctx = _make_context(retriever=retriever, user_id=user_id)
        agent = RAGAgent(ctx)
        result = agent.execute({"query": "word", "top_k": 3})
        assert len(result.output["citations"]) <= 3

    def test_top_k_clamped_to_20(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            text="word " * 2000,
        )
        ctx = _make_context(retriever=retriever, user_id=user_id)
        agent = RAGAgent(ctx)
        result = agent.execute({"query": "word", "top_k": 1000})
        assert len(result.output["citations"]) <= 20

    def test_missing_retriever_fails(self):
        user_id = uuid4()

        def no_retriever_executor(tool_name: str, **kwargs: object) -> dict:
            tool_context = ToolContext(user_id=str(user_id))  # no retriever
            return execute_tool(
                tool_name=tool_name,
                agent_name="rag_agent",
                agent_allowed_tools=RAGAgent.allowed_tools,
                context_allowed_tools=frozenset({"document_search"}),
                input_data=dict(kwargs),
                tool_context=tool_context,
            )

        ctx = AgentContext(
            user_id=user_id,
            allowed_tools=frozenset({"document_search"}),
            tool_executor=no_retriever_executor,
        )
        agent = RAGAgent(ctx)
        result = agent.execute({"query": "test"})
        assert result.status.value == "failed"

    def test_agent_is_registered(self):
        assert AgentRegistry.get("rag_agent") is RAGAgent

    def test_agent_declares_one_tool(self):
        assert RAGAgent.allowed_tools == frozenset({"document_search"})

    def test_respects_allowlist(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        ctx = _make_context(
            retriever=retriever,
            user_id=user_id,
            allowed_tools=frozenset(),  # empty
        )
        agent = RAGAgent(ctx)
        result = agent.execute({"query": "test"})
        assert result.status.value == "failed"

    def test_respects_budget(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        ctx = _make_context(retriever=retriever, user_id=user_id)
        ctx.budgets = AgentBudgets(max_tool_calls=0)
        agent = RAGAgent(ctx)
        result = agent.execute({"query": "test"})
        assert result.status.value == "failed"

    def test_summary_present(self):
        retriever = Retriever(MockEmbedder())
        user_id = uuid4()
        _populate(
            retriever,
            user_id=user_id,
            text="Python code " * 30,
        )
        ctx = _make_context(retriever=retriever, user_id=user_id)
        agent = RAGAgent(ctx)
        result = agent.execute({"query": "python"})
        assert result.summary