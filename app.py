import os
import random
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI

app = FastAPI()

# ============================================================
# Load API keys (multiple Groq keys)
# ============================================================
raw_keys = os.environ.get("GROQ_API_KEYS", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

if not API_KEYS:
    raise RuntimeError("No API keys found in GROQ_API_KEYS")

def get_client(api_key: str) -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

# ============================================================
# Core Groq request with multi-key + fast failover
# ============================================================
async def groq_request(model: str, messages: list) -> str | None:
    if not isinstance(messages, list):
        return None

    # Try fewer keys
    for attempt in range(min(2, len(API_KEYS))):  # FIXED: only 2 attempts
        api_key = random.choice(API_KEYS)
        client = get_client(api_key)

        try:
            completion = await client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=1.5  # FIXED: shorter timeout
            )

            if completion and completion.choices:
                return completion.choices[0].message.content

        except Exception as e:
            print(f"[Groq Error] Key {api_key} failed on attempt {attempt+1}: {e}")
            continue

    return None

# ============================================================
# Health check
# ============================================================
@app.get("/")
async def health():
    return JSONResponse({"status": "ok"})

# ============================================================
# Main Groq proxy route
# ============================================================
@app.post("/groq")
async def groq_proxy(request: Request):
    try:
        data = await request.json()

        model = data.get("model")
        messages = data.get("messages")

        if not isinstance(model, str):
            return JSONResponse({"error": "Missing or invalid model"}, status_code=400)

        if not isinstance(messages, list):
            return JSONResponse({"error": "Missing or invalid messages"}, status_code=400)

        reply = await groq_request(model, messages)

        if reply is None:
            return JSONResponse({"error": "All API keys failed"}, status_code=502)

        return JSONResponse({"reply": reply})

    except Exception as e:
        print("[Server Error]", e)
        return JSONResponse({"error": str(e)}, status_code=500)

