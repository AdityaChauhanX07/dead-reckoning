import httpx
import json
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parents[2] / ".env")

API_KEY = os.environ["DIGITALOCEAN_API_KEY"]

# files will be uploaded separately after KB creation
payload = {
    "name": "harold-jennings",
    "region": "tor1",
    "embedding_model_uuid": "22653204-79ed-11ef-bf8f-4e013e2ddde4",
    "project_id": "e6e551fe-b535-4fd0-acf0-d94a693f8fbc",
}

response = httpx.post(
    "https://api.digitalocean.com/v2/gen-ai/knowledge_bases",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json=payload,
)

data = response.json()
print(json.dumps(data, indent=2))

kb_id = data["knowledge_base"]["uuid"]
Path("kb_id.txt").write_text(kb_id)
print(f"\nSaved knowledge base UUID: {kb_id}")
