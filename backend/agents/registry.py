"""
AgentRegistry: registry of all available agents.
"""

from typing import Any

from agents.base import BaseAgent
from agents.exceptions import AgentError


class AgentRegistry:
    """Central registry of agents."""

    _agents: dict[str, type[BaseAgent]] = {}

    @classmethod
    def register(cls, agent_cls: type[BaseAgent]) -> type[BaseAgent]:
        name = getattr(agent_cls, "name", None)
        if not name:
            raise AgentError(f"Cannot register {agent_cls.__name__}: missing 'name' attribute.")
        if name in cls._agents:
            raise AgentError(f"Agent '{name}' is already registered.")
        cls._agents[name] = agent_cls
        return agent_cls

    @classmethod
    def get(cls, name: str) -> type[BaseAgent]:
        if name not in cls._agents:
            raise AgentError(f"Agent '{name}' is not registered.")
        return cls._agents[name]

    @classmethod
    def list_agents(cls) -> dict[str, dict[str, Any]]:
        return {
            name: {
                "name": name,
                "description": cls._agents[name].description,
                "allowed_tools": sorted(cls._agents[name].allowed_tools),
            }
            for name in cls._agents
        }

    @classmethod
    def clear(cls) -> None:
        cls._agents.clear()


def register_agent(agent_cls: type[BaseAgent]) -> type[BaseAgent]:
    """Decorator to register an agent class."""
    return AgentRegistry.register(agent_cls)
