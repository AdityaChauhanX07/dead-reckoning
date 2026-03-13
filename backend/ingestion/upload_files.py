import httpx
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[2] / ".env")

API_KEY = os.environ["DIGITALOCEAN_API_KEY"]
KB_UUID = os.environ["KNOWLEDGE_BASE_UUID"]

files = sorted(Path(__file__).parents[2].glob("data/harold/**/*.md"))

url = f"https://api.digitalocean.com/v2/gen-ai/knowledge_bases/{KB_UUID}/data_sources"
print(url)

for path in files:
    with path.open("rb") as f:
        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={"file": (path.name, f, "text/markdown")},
        )
    print(f"{path.name}: {response.status_code} — {response.text}")

print(f"\nDone — {len(files)} files uploaded")
