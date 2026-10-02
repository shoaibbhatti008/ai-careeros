"""
Resume analysis endpoint.

Uses ResumeAgentLLM when a real LLM provider is configured.
Falls back to heuristic ResumeAgent on failure.
"""

from apps.users.permissions import IsOwner
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Resume


class ResumeAnalyzeView(APIView):
    """POST /api/resumes/<id>/analyze/"""

    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request, pk):
        resume = get_object_or_404(Resume, pk=pk, user=request.user)

        version = (
            resume.versions.filter(is_current=True).first()
            or resume.versions.order_by("-version_number").first()
        )

        if version is None:
            return Response(
                {"detail": "Resume has no versions to analyze."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not version.raw_text:
            return Response(
                {"detail": "This resume has no text to analyze."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = self._run_agent(version.raw_text, resume.title)
        except Exception as exc:
            return Response(
                {"detail": f"Analysis failed: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not result.get("success"):
            return Response(
                {"detail": result.get("error", "Analysis failed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        version.analysis = result["output"]
        version.save(update_fields=["analysis", "updated_at"])

        return Response(
            {
                "resume_id": str(resume.id),
                "version_id": str(version.id),
                "analysis": result["output"],
                "summary": result.get("summary", ""),
                "provider": result.get("provider", "heuristic"),
                "model": result.get("model", ""),
                "tokens_used": result.get("tokens_used", 0),
            }
        )

    def _run_agent(self, resume_text: str, target_role: str = "") -> dict:
        from uuid import UUID

        from agents.context import AgentBudgets, AgentContext
        from agents.tools.base import ToolContext
        from agents.tools.registry import ToolRegistry, execute_tool

        user_id = UUID(str(self.request.user.id))

        try:
            from agents.llm.factory import get_provider

            provider = get_provider()
            if provider.provider_name != "mock":
                return self._run_llm_agent(
                    resume_text=resume_text,
                    target_role=target_role,
                    user_id=user_id,
                    provider=provider,
                    ToolRegistry=ToolRegistry,
                    AgentContext=AgentContext,
                    AgentBudgets=AgentBudgets,
                    ToolContext=ToolContext,
                    execute_tool=execute_tool,
                )
        except Exception as exc:
            print(f"[resume_analyze] LLM path failed, falling back: {exc}")

        return self._run_heuristic_agent(
            resume_text=resume_text,
            target_role=target_role,
            user_id=user_id,
            ToolRegistry=ToolRegistry,
            AgentContext=AgentContext,
            AgentBudgets=AgentBudgets,
            ToolContext=ToolContext,
            execute_tool=execute_tool,
        )

    def _run_llm_agent(
        self,
        *,
        resume_text: str,
        target_role: str,
        user_id,
        provider,
        ToolRegistry,
        AgentContext,
        AgentBudgets,
        ToolContext,
        execute_tool,
    ) -> dict:
        from agents.implementations.resume_agent_llm import ResumeAgentLLM
        from agents.tools.career.llm_analyzer import LLMAnalyzerTool

        ToolRegistry._tools.setdefault("llm_analyzer", LLMAnalyzerTool)

        def tool_executor(tool_name: str, **kwargs) -> dict:
            return execute_tool(
                tool_name=tool_name,
                agent_name="resume_agent_llm",
                agent_allowed_tools=ResumeAgentLLM.allowed_tools,
                context_allowed_tools=frozenset({"llm_analyzer"}),
                input_data=dict(kwargs),
                tool_context=ToolContext(
                    user_id=str(user_id),
                    metadata={"llm_provider": provider},
                ),
            )

        ctx = AgentContext(
            user_id=user_id,
            allowed_tools=frozenset({"llm_analyzer"}),
            tool_executor=tool_executor,
            budgets=AgentBudgets(
                max_steps=5,
                max_tool_calls=3,
                timeout_seconds=60,
            ),
        )

        agent = ResumeAgentLLM(ctx)
        result = agent.execute({"resume_text": resume_text, "target_role": target_role})

        if not result.is_success:
            raise RuntimeError(result.error or "LLM agent failed")

        return {
            "success": True,
            "output": result.output,
            "summary": result.summary,
            "error": "",
            "provider": provider.provider_name,
            "model": getattr(provider, "_model", ""),
            "tokens_used": 0,
        }

    def _run_heuristic_agent(
        self,
        *,
        resume_text: str,
        target_role: str,
        user_id,
        ToolRegistry,
        AgentContext,
        AgentBudgets,
        ToolContext,
        execute_tool,
    ) -> dict:
        from agents.implementations.resume_agent import ResumeAgent
        from agents.tools.career.resume_reader import ResumeReaderTool
        from agents.tools.career.skill_extractor import SkillExtractorTool

        ToolRegistry._tools.setdefault("resume_reader", ResumeReaderTool)
        ToolRegistry._tools.setdefault("skill_extractor", SkillExtractorTool)

        def tool_executor(tool_name: str, **kwargs) -> dict:
            return execute_tool(
                tool_name=tool_name,
                agent_name="resume_agent",
                agent_allowed_tools=ResumeAgent.allowed_tools,
                context_allowed_tools=frozenset({"resume_reader", "skill_extractor"}),
                input_data=dict(kwargs),
                tool_context=ToolContext(user_id=str(user_id)),
            )

        ctx = AgentContext(
            user_id=user_id,
            allowed_tools=frozenset({"resume_reader", "skill_extractor"}),
            tool_executor=tool_executor,
            budgets=AgentBudgets(max_steps=10, max_tool_calls=20),
        )

        agent = ResumeAgent(ctx)
        result = agent.execute({"resume_text": resume_text, "target_role": target_role})

        return {
            "success": result.is_success,
            "output": result.output,
            "summary": result.summary,
            "error": result.error,
            "provider": "heuristic",
            "model": "",
            "tokens_used": 0,
        }
