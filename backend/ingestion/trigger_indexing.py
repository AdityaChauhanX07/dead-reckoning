import httpx
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[2] / ".env")

API_KEY = os.environ["DIGITALOCEAN_API_KEY"]
KB_UUID = os.environ["KNOWLEDGE_BASE_UUID"]

headers = {"Authorization": f"Bearer {API_KEY}"}
base = f"https://api.digitalocean.com/v2/gen-ai/knowledge_bases/{KB_UUID}"

data_sources = httpx.get(f"{base}/data_sources", headers=headers).json()

for ds in data_sources.get("data_sources", []):
    ds_uuid = ds["uuid"]
    ds_name = ds.get("name", ds_uuid)

    response = httpx.post(f"{base}/data_sources/{ds_uuid}/indexing_jobs", headers=headers)
    print(f"{ds_name}: {json.dumps(response.json(), indent=2)}")
