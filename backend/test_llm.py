import asyncio

from app.chat.llm_service import (
    LLMMessage,
    LLMService,
)


async def test_normal_response() -> None:
    service = LLMService()

    response = await service.generate(
        messages=[
            LLMMessage(
                role="system",
                content=(
                    "You are an enterprise AI assistant. "
                    "Give clear and concise answers."
                ),
            ),
            LLMMessage(
                role="user",
                content="What is role-based access control?",
            ),
        ],
        temperature=0.3,
        max_tokens=300,
    )

    print("\n--- Normal response ---")
    print(response.content)

    print("\n--- Usage ---")
    print("Provider:", response.provider)
    print("Model:", response.model)
    print("Prompt tokens:", response.prompt_tokens)
    print("Completion tokens:", response.completion_tokens)
    print("Total tokens:", response.total_tokens)


async def test_streaming_response() -> None:
    service = LLMService()

    print("\n--- Streaming response ---")

    async for chunk in service.stream(
        messages=[
            LLMMessage(
                role="system",
                content=(
                    "You are an enterprise AI assistant. "
                    "Give clear and concise answers."
                ),
            ),
            LLMMessage(
                role="user",
                content="Explain FastAPI in five lines.",
            ),
        ],
        temperature=0.3,
        max_tokens=300,
    ):
        print(
            chunk,
            end="",
            flush=True,
        )

    print()


async def main() -> None:
    await test_normal_response()
    await test_streaming_response()


if __name__ == "__main__":
    asyncio.run(main())