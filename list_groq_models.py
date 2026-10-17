import os
import httpx
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")
r = httpx.get(
    "https://api.groq.com/openai/v1/models",
    headers={"Authorization": f"Bearer {key}"},
    timeout=30,
)
print("Status:", r.status_code)

for m in sorted(r.json().get("data", []), key=lambda x: x["id"]):
    print(m["id"])