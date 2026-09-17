import os
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:14b")


async def generate_response(system_prompt: str, user_message: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": user_message,
        "stream": False,
        "options": {"temperature": 0.2},
    }

    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["response"].strip()
