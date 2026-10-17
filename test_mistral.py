import os
import httpx
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("MISTRAL_API_KEY")
print("Key found:", bool(key), "| length:", len(key or ""))

r = httpx.post(
    "https://api.mistral.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": "Say hi"}],
        "max_tokens": 10,
    },
    timeout=30,
)

print("Status:", r.status_code)
print("Body:", r.text[:300])
for k, v in r.headers.items():
    if "limit" in k.lower() or "retry" in k.lower():
        print(k, "=", v)