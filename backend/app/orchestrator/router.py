from __future__ import annotations

from dataclasses import dataclass

from app.agents.registry import AgentRegistry, agent_registry


@dataclass(frozen=True)
class RouteResult:
    agent_names: list[str]
    reason: str
    confidence: float


class AgentRouter:
    """Select the best registered agent or agents for a user request."""

    KEYWORDS: dict[str, tuple[str, ...]] = {
        "hr_agent": (
            "hr", "employee", "leave", "payroll", "salary", "benefit",
            "policy", "holiday", "attendance", "recruitment", "onboarding",
        ),
        "documentation_agent": (
            "document", "documentation", "readme", "manual", "guide",
            "summary", "summarize", "technical writing", "api docs",
        ),
        "customer_support_agent": (
            "customer", "support", "ticket", "complaint", "refund",
            "issue", "incident", "service request", "sla",
        ),
        "project_agent": (
            "project", "sprint", "task", "jira", "roadmap", "timeline",
            "risk", "milestone", "story", "backlog", "team",
        ),
        "knowledge_agent": (
            "explain", "what is", "how does", "knowledge", "research",
            "question", "information", "compare",
        ),
    }

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or agent_registry

    def route(self, message: str, *, max_agents: int = 1) -> RouteResult:
        normalized = message.lower().strip()
        available = {agent.name for agent in self.registry.all()}
        scores: dict[str, int] = {}

        for agent_name, keywords in self.KEYWORDS.items():
            if agent_name not in available:
                continue
            scores[agent_name] = sum(1 for keyword in keywords if keyword in normalized)

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        matched = [(name, score) for name, score in ranked if score > 0]

        if not matched:
            fallback = "knowledge_agent"
            if fallback not in available:
                if not available:
                    raise RuntimeError("No agents are registered.")
                fallback = sorted(available)[0]
            return RouteResult(
                agent_names=[fallback],
                reason="No specialist keywords matched; using the general knowledge agent.",
                confidence=0.5,
            )

        selected = [name for name, _ in matched[:max(1, max_agents)]]
        top_score = matched[0][1]
        confidence = min(0.95, 0.55 + (top_score * 0.1))
        return RouteResult(
            agent_names=selected,
            reason=f"Matched request keywords to: {', '.join(selected)}.",
            confidence=confidence,
        )
