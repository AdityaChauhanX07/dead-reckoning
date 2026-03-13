import json
import os
from typing import AsyncGenerator

import httpx
from fastapi import HTTPException

from .harold import HAROLD_SYSTEM_PROMPT  # noqa: F401 — wired in via DO dashboard agent config


async def ask_harold(question: str) -> str:
    agent_id = os.getenv("GRADIENT_AI_AGENT_ID")
    api_key = os.getenv("DIGITALOCEAN_API_KEY")

    url = f"https://api.digitalocean.com/v2/gen-ai/agents/{agent_id}/chat"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "messages": [{"role": "user", "content": question}]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            # Response shape (OpenAI-compatible chat completion):
            # {
            #   "id": str,
            #   "object": "chat.completion",
            #   "created": int,
            #   "model": str,
            #   "choices": [
            #     {
            #       "index": int,
            #       "finish_reason": "stop" | "length" | "tool_calls" | "content_filter",
            #       "message": {
            #         "role": "assistant",
            #         "content": str | null,   # null if refusal or tool_calls
            #         "refusal": str | null,
            #         "tool_calls": [...] | null
            #       }
            #     }
            #   ],
            #   "usage": { "prompt_tokens": int, "completion_tokens": int, "total_tokens": int }
            # }
            content = data["choices"][0]["message"]["content"]
            if content is None:
                refusal = data["choices"][0]["message"].get("refusal")
                raise ValueError(refusal or "No content returned")
            return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Harold is unavailable: {e}")


async def ask_harold_stream(question: str) -> AsyncGenerator[str, None]:
    agent_id = os.getenv("GRADIENT_AI_AGENT_ID")
    api_key = os.getenv("DIGITALOCEAN_API_KEY")

    url = f"https://api.digitalocean.com/v2/gen-ai/agents/{agent_id}/chat"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "messages": [{"role": "user", "content": question}],
        "stream": True,
    }

    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, headers=headers, json=body) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = line[len("data: "):]
                    if payload.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(payload)
                        content = chunk["choices"][0]["delta"].get("content")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Harold is unavailable: {e}")
