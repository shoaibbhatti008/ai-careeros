"""
RAGAgent: answers questions using the user's own documents.

The agent:
1. Retrieves the top-K relevant chunks via document_search
2. Returns an answer with citations (chunk text + score)
3. Never accesses chunks from other users (enforced by the tool)

Optional: if an LLM provider is available, the agent can produce
a natural-language answer grounded in retrieved chunks. Otherwise it
returns the raw retrieved chunks with a simple summary.
"""

from typing import Any

from agents.base import BaseAgent
from agents.registry import register_agent
from agents.result import AgentResult


@register_agent
class RAGAgent(BaseAgent):
    """Answers questions using the user's own documents."""

    name = "rag_agent"
    description = "Answers questions grounded in the user's own documents."
    allowed_tools = frozenset({"document_search"})

    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "top_k": {"type": "integer"},
        },
        "required": ["query"],
    }

    output_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "answer": {"type": "string"},
            "citations": {"type": "array"},
            "retrieved_count": {"type": "integer"},
        },
    }

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        query = (input_data.get("query") or "").strip()
        if not query:
            return AgentResult.failed("query is required and cannot be empty.")

        top_k = int(input_data.get("top_k", 5))
        top_k = max(1, min(top_k, 20))

        # Retrieve
        search_result = self.call_tool("document_search", query=query, top_k=top_k)
        results = search_result.get("results", [])

        if not results:
            return AgentResult.completed(
                output={
                    "query": query,
                    "answer": "No relevant documents found.",
                    "citations": [],
                    "retrieved_count": 0,
                },
                summary="No relevant documents found.",
            )

        # Build a simple answer (heuristic) + citations
        top_text = results[0]["text"]
        answer = (
            f"Based on your documents, the most relevant passage is: "
            f"\"{top_text[:300]}{'...' if len(top_text) > 300 else ''}\""
        )

        citations = [
            {
                "document_id": r["document_id"],
                "chunk_index": r["chunk_index"],
                "score": r["score"],
                "snippet": r["text"][:200],
            }
            for r in results
        ]

        return AgentResult.completed(
            output={
                "query": query,
                "answer": answer,
                "citations": citations,
                "retrieved_count": len(results),
            },
            summary=f"Retrieved {len(results)} relevant chunks for query.",
            citations=citations,
            usage={
                "steps": self.context.usage.steps,
                "tool_calls": self.context.usage.tool_calls,
            },
        )
