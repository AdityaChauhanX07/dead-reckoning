import os
from pathlib import Path
from dotenv import load_dotenv
import httpx

load_dotenv(Path(__file__).parent.parent / ".env")

agent_endpoint = os.getenv("AGENT_ENDPOINT", "")
api_key = os.getenv("AGENT_ACCESS_KEY", "")

print(f"AGENT_ENDPOINT:       {agent_endpoint}")
print(f"AGENT_ACCESS_KEY:     {api_key[:20]}")

url = f"{agent_endpoint}/api/v1/chat/completions"
headers = {"Authorization": f"Bearer {api_key}"}
payload = {
    "messages": [{"role": "user", "content": "Say hello"}],
    "stream": False,
}

response = httpx.post(url, headers=headers, json=payload, timeout=30)

print(f"\nStatus: {response.status_code}")
print(f"Body:\n{response.text}")
