from app.agents.base_agent import BaseAgent


class CustomerSupportAgent(BaseAgent):
    name = "customer_support_agent"
    description = "Handles customer questions, incidents, tickets and troubleshooting."
    capabilities = ["ticket assistance", "troubleshooting", "response drafting", "issue classification"]
    supported_tools = ["ticket_search", "knowledge_base", "rag_search"]
    prompt_template = """You are the Enterprise Customer Support Agent.
Be empathetic, concise and action-oriented. Diagnose the issue from available facts and give safe steps.
Do not claim that an action was completed unless a tool result confirms it. Escalate uncertain critical issues."""

    @classmethod
    def can_handle(cls, message: str) -> bool:
        keywords = ("customer", "support", "ticket", "issue", "problem", "error", "refund", "complaint")
        text = message.lower()
        return any(word in text for word in keywords)
