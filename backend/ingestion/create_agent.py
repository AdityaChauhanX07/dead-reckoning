import httpx
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parents[2]))

load_dotenv(Path(__file__).parents[2] / ".env")

from backend.persona.harold import HAROLD_SYSTEM_PROMPT

API_KEY = os.environ["DIGITALOCEAN_API_KEY"]
KB_UUID = os.environ["KNOWLEDGE_BASE_UUID"]

payload = {
    "name": "harold-jennings",
    "region": "tor1",
    "project_id": "e6e551fe-b535-4fd0-acf0-d94a693f8fbc",
    "model": {"uuid": "c4811790-0c4e-11f1-b074-4e013e2ddde4"},
    "instruction": HAROLD_SYSTEM_PROMPT,
    "knowledge_base_uuids": [KB_UUID],
    "temperature": 0.7,
    "max_tokens": 1024,
}

response = httpx.post(
    "https://api.digitalocean.com/v2/gen-ai/agents",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json=payload,
)

data = response.json()
print(json.dumps(data, indent=2))

agent_uuid = data["agent"]["uuid"]
Path("agent_id.txt").write_text(agent_uuid)
print(f"\nSaved agent UUID: {agent_uuid}")
