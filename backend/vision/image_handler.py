import os

import httpx

from persona.agent import ask_harold


async def analyze_clock_image(image_base64: str, mime_type: str) -> str:
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    vision_response = await httpx.AsyncClient().post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "You are examining a clock or watch. Describe in technical detail: "
                                "what parts are visible, their condition, any visible damage or wear, "
                                "the movement type if identifiable, and anything a clockmaker should note."
                            ),
                        },
                    ],
                }
            ],
        },
    )
    vision_response.raise_for_status()
    description = vision_response.json()["content"][0]["text"]

    return await ask_harold(
        f"I'm looking at a clock and here's what I can see: {description}. What do you make of this?"
    )
