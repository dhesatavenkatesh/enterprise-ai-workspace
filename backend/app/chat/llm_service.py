from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Literal

from groq import AsyncGroq
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


MessageRole = Literal["system", "user", "assistant"]


class LLMServiceError(Exception):
    """Base exception for LLM service errors."""


class LLMConfigurationError(LLMServiceError):
    """Raised when an LLM provider is not configured correctly."""


class LLMTimeoutError(LLMServiceError):
    """Raised when an LLM request exceeds its timeout."""


class LLMProviderError(LLMServiceError):
    """Raised when an external LLM provider returns an error."""


@dataclass(slots=True)
class LLMMessage:
    role: MessageRole
    content: str

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
        }


@dataclass(slots=True)
class LLMResponse:
    content: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str | None = None


class LLMProvider(ABC):
    """
    Common interface implemented by all LLM providers.
    """

    provider_name: str

    def __init__(
        self,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout_seconds: float,
        max_retries: int,
    ) -> None:
        if not model.strip():
            raise LLMConfigurationError(f"A model name is required for {self.provider_name}.")

        if not 0 <= temperature <= 2:
            raise LLMConfigurationError("Temperature must be between 0 and 2.")

        if max_tokens <= 0:
            raise LLMConfigurationError("max_tokens must be greater than zero.")

        if timeout_seconds <= 0:
            raise LLMConfigurationError("timeout_seconds must be greater than zero.")

        if max_retries <= 0:
            raise LLMConfigurationError("max_retries must be greater than zero.")

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate one complete response."""

    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Yield incremental text chunks."""

    def _prepare_messages(
        self,
        messages: list[LLMMessage],
    ) -> list[dict[str, str]]:
        if not messages:
            raise LLMProviderError("At least one chat message is required.")

        prepared_messages: list[dict[str, str]] = []

        for message in messages:
            content = message.content.strip()

            if not content:
                raise LLMProviderError("Chat messages cannot contain empty content.")

            prepared_messages.append(
                {
                    "role": message.role,
                    "content": content,
                }
            )

        return prepared_messages

    def _temperature(
        self,
        override: float | None,
    ) -> float:
        value = self.temperature if override is None else override

        if not 0 <= value <= 2:
            raise LLMProviderError("Temperature must be between 0 and 2.")

        return value

    def _max_tokens(
        self,
        override: int | None,
    ) -> int:
        value = self.max_tokens if override is None else override

        if value <= 0:
            raise LLMProviderError("max_tokens must be greater than zero.")

        return value

    async def _run_with_retry(
        self,
        operation: Any,
    ) -> Any:
        """
        Retry a provider operation with exponential backoff.
        """

        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                return await asyncio.wait_for(
                    operation(),
                    timeout=self.timeout_seconds,
                )

            except TimeoutError as exc:
                last_error = exc

                logger.warning(
                    "%s request timed out on attempt %s/%s",
                    self.provider_name,
                    attempt,
                    self.max_retries,
                )

            except Exception as exc:
                last_error = exc

                logger.warning(
                    "%s request failed on attempt %s/%s: %s",
                    self.provider_name,
                    attempt,
                    self.max_retries,
                    exc,
                )

            if attempt < self.max_retries:
                delay = min(2 ** (attempt - 1), 8)
                await asyncio.sleep(delay)

        if isinstance(last_error, TimeoutError):
            raise LLMTimeoutError(
                f"{self.provider_name} request timed out after {self.max_retries} attempts."
            ) from last_error

        raise LLMProviderError(
            f"{self.provider_name} request failed after {self.max_retries} attempts: {last_error}"
        ) from last_error


class OpenAIProvider(LLMProvider):
    provider_name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout_seconds: float,
        max_retries: int,
    ) -> None:
        if not api_key:
            raise LLMConfigurationError("OPENAI_API_KEY is not configured.")

        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=0,
        )

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        prepared_messages = self._prepare_messages(messages)

        async def operation() -> Any:
            return await self.client.chat.completions.create(
                model=self.model,
                messages=prepared_messages,
                temperature=self._temperature(temperature),
                max_tokens=self._max_tokens(max_tokens),
                stream=False,
            )

        try:
            response = await self._run_with_retry(operation)
            choice = response.choices[0]
            usage = response.usage

            prompt_tokens = usage.prompt_tokens if usage is not None else 0
            completion_tokens = usage.completion_tokens if usage is not None else 0
            total_tokens = usage.total_tokens if usage is not None else 0

            return LLMResponse(
                content=choice.message.content or "",
                provider=self.provider_name,
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                finish_reason=choice.finish_reason,
            )

        except LLMServiceError:
            raise
        except Exception as exc:
            raise LLMProviderError(f"OpenAI generation failed: {exc}") from exc

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        prepared_messages = self._prepare_messages(messages)
        emitted_content = False

        for attempt in range(1, self.max_retries + 1):
            try:
                stream = await self.client.chat.completions.create(
                    model=self.model,
                    messages=prepared_messages,
                    temperature=self._temperature(temperature),
                    max_tokens=self._max_tokens(max_tokens),
                    stream=True,
                )

                async with asyncio.timeout(self.timeout_seconds):
                    async for chunk in stream:
                        content = chunk.choices[0].delta.content

                        if content:
                            emitted_content = True
                            yield content

                return

            except TimeoutError as exc:
                if emitted_content:
                    raise LLMTimeoutError("OpenAI stream timed out after output started.") from exc

                if attempt == self.max_retries:
                    raise LLMTimeoutError("OpenAI stream timed out.") from exc

            except Exception as exc:
                if emitted_content:
                    raise LLMProviderError(f"OpenAI stream interrupted: {exc}") from exc

                if attempt == self.max_retries:
                    raise LLMProviderError(f"OpenAI streaming failed: {exc}") from exc

            await asyncio.sleep(min(2 ** (attempt - 1), 8))


class GroqProvider(LLMProvider):
    provider_name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout_seconds: float,
        max_retries: int,
    ) -> None:
        if not api_key:
            raise LLMConfigurationError("GROQ_API_KEY is not configured.")

        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

        self.client = AsyncGroq(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=0,
        )

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        prepared_messages = self._prepare_messages(messages)

        async def operation() -> Any:
            return await self.client.chat.completions.create(
                model=self.model,
                messages=prepared_messages,
                temperature=self._temperature(temperature),
                max_tokens=self._max_tokens(max_tokens),
                stream=False,
            )

        try:
            response = await self._run_with_retry(operation)
            choice = response.choices[0]
            usage = response.usage

            prompt_tokens = usage.prompt_tokens if usage is not None else 0
            completion_tokens = usage.completion_tokens if usage is not None else 0
            total_tokens = usage.total_tokens if usage is not None else 0

            return LLMResponse(
                content=choice.message.content or "",
                provider=self.provider_name,
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                finish_reason=choice.finish_reason,
            )

        except LLMServiceError:
            raise
        except Exception as exc:
            raise LLMProviderError(f"Groq generation failed: {exc}") from exc

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        prepared_messages = self._prepare_messages(messages)
        emitted_content = False

        for attempt in range(1, self.max_retries + 1):
            try:
                stream = await self.client.chat.completions.create(
                    model=self.model,
                    messages=prepared_messages,
                    temperature=self._temperature(temperature),
                    max_tokens=self._max_tokens(max_tokens),
                    stream=True,
                )

                async with asyncio.timeout(self.timeout_seconds):
                    async for chunk in stream:
                        content = chunk.choices[0].delta.content

                        if content:
                            emitted_content = True
                            yield content

                return

            except TimeoutError as exc:
                if emitted_content:
                    raise LLMTimeoutError("Groq stream timed out after output started.") from exc

                if attempt == self.max_retries:
                    raise LLMTimeoutError("Groq stream timed out.") from exc

            except Exception as exc:
                if emitted_content:
                    raise LLMProviderError(f"Groq stream interrupted: {exc}") from exc

                if attempt == self.max_retries:
                    raise LLMProviderError(f"Groq streaming failed: {exc}") from exc

            await asyncio.sleep(min(2 ** (attempt - 1), 8))


class OllamaProvider(LLMProvider):
    provider_name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout_seconds: float,
        max_retries: int,
    ) -> None:
        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

        try:
            from ollama import AsyncClient
        except ImportError as exc:
            raise LLMConfigurationError(
                "Ollama support requires the 'ollama' package. Install it using: pip install ollama"
            ) from exc

        self.client = AsyncClient(
            host=base_url,
            timeout=timeout_seconds,
        )

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        prepared_messages = self._prepare_messages(messages)

        async def operation() -> Any:
            return await self.client.chat(
                model=self.model,
                messages=prepared_messages,
                stream=False,
                options={
                    "temperature": self._temperature(temperature),
                    "num_predict": self._max_tokens(max_tokens),
                },
            )

        try:
            response = await self._run_with_retry(operation)

            content = response["message"]["content"]
            prompt_tokens = int(response.get("prompt_eval_count", 0))
            completion_tokens = int(response.get("eval_count", 0))

            return LLMResponse(
                content=content,
                provider=self.provider_name,
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                finish_reason=response.get("done_reason"),
            )

        except LLMServiceError:
            raise
        except Exception as exc:
            raise LLMProviderError(f"Ollama generation failed: {exc}") from exc

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        prepared_messages = self._prepare_messages(messages)
        emitted_content = False

        for attempt in range(1, self.max_retries + 1):
            try:
                stream = await self.client.chat(
                    model=self.model,
                    messages=prepared_messages,
                    stream=True,
                    options={
                        "temperature": self._temperature(temperature),
                        "num_predict": self._max_tokens(max_tokens),
                    },
                )

                async with asyncio.timeout(self.timeout_seconds):
                    async for chunk in stream:
                        content = chunk["message"]["content"]

                        if content:
                            emitted_content = True
                            yield content

                return

            except TimeoutError as exc:
                if emitted_content:
                    raise LLMTimeoutError("Ollama stream timed out after output started.") from exc

                if attempt == self.max_retries:
                    raise LLMTimeoutError("Ollama stream timed out.") from exc

            except Exception as exc:
                if emitted_content:
                    raise LLMProviderError(f"Ollama stream interrupted: {exc}") from exc

                if attempt == self.max_retries:
                    raise LLMProviderError(f"Ollama streaming failed: {exc}") from exc

            await asyncio.sleep(min(2 ** (attempt - 1), 8))


class LLMService:
    """
    Application-level LLM service.

    This class allows the chat API to use Groq, OpenAI or Ollama
    without depending directly on a particular SDK.
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
    ) -> None:
        self.provider = provider or create_llm_provider()

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        return await self.provider.generate(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        async for chunk in self.provider.stream(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk


def create_llm_provider(
    provider_name: str | None = None,
    model: str | None = None,
) -> LLMProvider:
    """
    Factory that creates the configured LLM provider.
    """

    selected_provider = (provider_name or settings.llm_provider or "groq").strip().lower()

    common_options = {
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
        "timeout_seconds": settings.llm_timeout_seconds,
        "max_retries": settings.llm_max_retries,
    }

    if selected_provider == "groq":
        return GroqProvider(
            api_key=settings.groq_api_key or "",
            model=model or settings.groq_model,
            **common_options,
        )

    if selected_provider == "openai":
        return OpenAIProvider(
            api_key=settings.openai_api_key or "",
            model=model or settings.openai_model,
            **common_options,
        )

    if selected_provider == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=model or settings.ollama_model,
            **common_options,
        )

    raise LLMConfigurationError(
        f"Unsupported LLM provider: {selected_provider}. "
        "Supported providers are: groq, openai and ollama."
    )


def get_llm_service() -> LLMService:
    """
    FastAPI dependency for obtaining the configured LLM service.
    """

    return LLMService()
