from app.agents.base_agent import BaseAgent


class DocumentationAgent(BaseAgent):
    name = "documentation_agent"
    description = "Creates and improves technical and business documentation."
    capabilities = ["documentation", "summarization", "README generation", "API explanation"]
    supported_tools = ["document_search", "rag_search"]
    prompt_template = """You are the Enterprise Documentation Agent.
Create clear, structured and technically accurate documentation.
Use only the provided context.
Preserve exact endpoint names, commands, file paths and configuration values.
Do not fabricate features."""

    @classmethod
    def can_handle(cls, message: str) -> bool:
        keywords = (
            "document",
            "documentation",
            "readme",
            "summary",
            "summarize",
            "api guide",
            "manual",
        )
        text = message.lower()
        return any(word in text for word in keywords)
