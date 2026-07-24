from app.agents.base_agent import BaseAgent


class HRAgent(BaseAgent):
    name = "hr_agent"
    description = "Handles employee, leave, payroll, benefits and HR policy questions."
    capabilities = ["leave policy", "payroll FAQ", "benefits", "employee policy"]
    supported_tools = ["rag_search", "employee_directory"]
    prompt_template = """You are the Enterprise HR Agent.
Answer HR questions accurately and professionally.
Use supplied context as the source of truth.
Do not invent company policies.
When information is missing, clearly say that HR confirmation is required.
Never expose private employee information without authorization."""

    @classmethod
    def can_handle(cls, message: str) -> bool:
        keywords = (
            "leave",
            "salary",
            "payroll",
            "employee",
            "hr",
            "holiday",
            "benefit",
            "attendance",
        )
        text = message.lower()
        return any(word in text for word in keywords)
