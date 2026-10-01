"""
DocumentSearchTool: search a user's own documents.

Risk: MEDIUM (accesses user documents). Ownership is enforced by
the injected retriever; the tool itself cannot bypass it.
"""

from typing import Any, ClassVar
from uuid import UUID

from agents.rag.retriever import Retriever
from agents.tools.base import BaseTool, RiskLevel


class DocumentSearchTool(BaseTool):
    """
    Search documents owned by the current user.

    Input:
        query:   str
        top_k:   int (default 5)

    Output:
        results: list of {
            text, score, rank, document_id, chunk_index
        }
    """

    name = "document_search"
    description = "Searches the user's own documents (ownership enforced)."
    risk_level: ClassVar[RiskLevel] = RiskLevel.MEDIUM
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"rag_agent"})
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "top_k": {"type": "integer"},
        },
        "required": ["query"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {"results": {"type": "array"}},
    }
    timeout_seconds = 10
    rate_limit_per_minute = 60

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        retriever = self.context.metadata.get("retriever")
        if retriever is None or not isinstance(retriever, Retriever):
            from agents.tools.errors import ToolExecutionError

            raise ToolExecutionError(
                "No retriever was injected in ToolContext.metadata['retriever'].",
                tool_name=self.name,
            )

        query = input_data["query"]
        top_k = int(input_data.get("top_k", 5))

        # CRITICAL: user_id comes from the trusted context, not from input.
        user_id = UUID(self.context.user_id)

        results = retriever.search(
            user_id=user_id,
            query=query,
            top_k=top_k,
        )

        return {
            "results": [
                {
                    "text": r.chunk.text,
                    "score": r.score,
                    "rank": r.rank,
                    "document_id": str(r.chunk.document_id),
                    "chunk_index": r.chunk.index,
                }
                for r in results
            ]
        }
