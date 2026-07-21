from __future__ import annotations

from app.agents.schemas import AgentResponse, AgentStatus


class ResultAggregator:
    @staticmethod
    def aggregate(results: list[AgentResponse]) -> str:
        successful = [result for result in results if result.status == AgentStatus.SUCCESS]
        if not successful:
            errors = [result.error for result in results if result.error]
            return "Agent execution failed. " + ("; ".join(errors) if errors else "No response was produced.")

        if len(successful) == 1:
            return successful[0].content

        sections: list[str] = []
        for result in successful:
            sections.append(f"### {result.agent_name}\n{result.content.strip()}")
        return "\n\n".join(sections)
