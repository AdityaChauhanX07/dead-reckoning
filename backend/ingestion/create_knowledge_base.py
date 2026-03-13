import httpx
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parents[2] / ".env")

API_KEY = os.environ["DIGITALOCEAN_API_KEY"]

payload = {
    "name": "harold-jennings",
    "region": "tor1",
    "embedding_model": {
        "model": "text-embedding-3-small",
        "type": "OPEN_AI",
    },
}

response = httpx.post(
    "https://api.digitalocean.com/v2/gen-ai/knowledge_bases",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json=payload,
)

data = response.json()
print(data)

kb_id = data["knowledge_base"]["uuid"]
Path("kb_id.txt").write_text(kb_id)
print(f"Saved knowledge base UUID: {kb_id}")
