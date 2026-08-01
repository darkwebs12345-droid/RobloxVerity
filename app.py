from quart import Quart, request, jsonify
from openai import AsyncOpenAI
import os
import random

app = Quart(__name__)

# Load multiple API keys from environment (comma-separated)
API_KEYS = [
    key.strip() for key in os.environ.get("GROQ_API_KEYS", "").split(",")
    if key.strip()
]

if not API_KEYS:
    raise RuntimeError("No API keys found in GROQ_API_KEYS")

def get_client(api_key):
    return AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

# ============================================================
# Multi-key failover logic
# ============================================================
async def groq_request(model, messages):
    for attempt in range(3):
        api_key = random.choice(API_KEYS)
        client = get_client(api_key)

        try:
            completion = await client.chat.completions.create(
                model=model,
                messages=messages
            )
            return completion.choices[0].message.content

        except Exception as e:
            print(f"[Groq Error] Key failed: {api_key} | {e}")

    return None

# ============================================================
# Health check
# ============================================================
@app.get("/")
async def health():
    return jsonify({"status": "ok"})

# ============================================================
# Main route
# ============================================================
@app.post("/groq")
async def groq_proxy():
    try:
        data = await request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        model = data.get("model")
        messages = data.get("messages")

        if not model or not messages:
            return jsonify({"error": "Missing model or messages"}), 400

        reply = await groq_request(model, messages)

        if reply is None:
            return jsonify({"error": "All API keys failed"}), 502

        return jsonify({"reply": reply})

    except Exception as e:
        print("[Server Error]", e)
        return jsonify({"error": str(e)}), 500



