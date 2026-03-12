import os
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
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Harold is unavailable: {e}")
