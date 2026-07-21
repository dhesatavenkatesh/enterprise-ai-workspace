from app.agents.base_agent import BaseAgent


class KnowledgeAgent(BaseAgent):
    name = "knowledge_agent"
    description = "General enterprise knowledge and RAG question-answering agent."
    capabilities = ["general Q&A", "knowledge search", "RAG answers", "explanation"]
    supported_tools = ["rag_search", "document_search"]
    prompt_template = """You are the Enterprise Knowledge Agent.
Answer using the supplied context. Be clear and factual. Do not invent facts or citations.
When the context is insufficient, state what information is missing."""

    @classmethod
    def can_handle(cls, message: str) -> bool:
        return True
