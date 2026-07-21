from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from app.agents.context import AgentContextManager
from app.agents.memory import AgentMemory, agent_memory
from app.agents.schemas import AgentDefinition, AgentRequest, AgentResponse, AgentStatus

if TYPE_CHECKING:
    from app.chat.llm_service import LLMService


class BaseAgent(ABC):
    name: str
    description: str
    capabilities: list[str] = []
    supported_tools: list[str] = []
    prompt_template: str = "You are a helpful enterprise AI assistant."

    def __init__(
        self,
        llm_service: LLMService | None = None,
        memory: AgentMemory | None = None,
    ) -> None:
        self._llm_service: Any = llm_service
        self.memory = memory or agent_memory

    @property
    def llm_service(self) -> Any:
        if self._llm_service is None:
            from app.chat.llm_service import LLMService

            self._llm_service = LLMService()
        return self._llm_service

    def definition(self) -> AgentDefinition:
        return AgentDefinition(
            name=self.name,
            description=self.description,
            capabilities=list(self.capabilities),
            supported_tools=list(self.supported_tools),
        )

    def build_messages(self, request: AgentRequest) -> list[Any]:
        from app.chat.llm_service import LLMMessage

        memory = self.memory.get(request.conversation_id)
        context_text = AgentContextManager.build(request, memory)
        user_content = request.message
        if context_text:
            user_content = f"{context_text}\n\nUser request:\n{request.message}"
        return [
            LLMMessage(role="system", content=self.prompt_template),
            LLMMessage(role="user", content=user_content),
        ]

    async def execute(self, request: AgentRequest) -> AgentResponse:
        self.memory.add(request.conversation_id or "", "user", request.message)
        result = await self.llm_service.generate(self.build_messages(request))
        self.memory.add(request.conversation_id or "", "assistant", result.content)
        return AgentResponse(
            agent_name=self.name,
            status=AgentStatus.SUCCESS,
            content=result.content,
            provider=result.provider,
            model=result.model,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.total_tokens,
        )

    @classmethod
    @abstractmethod
    def can_handle(cls, message: str) -> bool:
        raise NotImplementedError
