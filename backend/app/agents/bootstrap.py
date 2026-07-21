from __future__ import annotations

from app.agents.registry import AgentRegistry, agent_registry
from app.agents.specialized import (
    CustomerSupportAgent,
    DocumentationAgent,
    HRAgent,
    KnowledgeAgent,
    ProjectAgent,
)


def register_default_agents(registry: AgentRegistry | None = None) -> AgentRegistry:
    selected_registry = registry or agent_registry
    for agent_class in (
        HRAgent,
        DocumentationAgent,
        CustomerSupportAgent,
        ProjectAgent,
        KnowledgeAgent,
    ):
        selected_registry.register(agent_class())
    return selected_registry
