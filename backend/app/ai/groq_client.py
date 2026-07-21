from __future__ import annotations

import os

from groq import Groq


class GroqClient:
    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

        self.client = Groq(api_key=api_key)
        self.model = os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile",
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("Groq returned an empty response.")

        return content.strip()


groq_client = GroqClient()


def generate_with_groq(
    system_prompt: str,
    user_prompt: str,
) -> str:
    return groq_client.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )