from quart import Quart, request, jsonify
from openai import AsyncOpenAI
import os
import random

app = Quart(__name__)

# ============================================================
# Load fallback API keys (server-side)
# ============================================================
raw_keys = os.environ.get("GROQ_API_KEYS", "")
SERVER_KEYS = [key.strip() for key in raw_keys.split(",") if key.strip()]

def get_client(api_key):
    return AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

# ============================================================
# Multi-key failover logic (now supports Roblox key)
# ============================================================
async def groq_request(model, messages, roblox_key=None):
    # Build priority list:
    # 1. Roblox-provided key (if any)
    # 2. Server fallback keys
    key_pool = []

    if roblox_key:
        key_pool.append(roblox_key)

    key_pool.extend(SERVER_KEYS)

    if not key_pool:
        raise RuntimeError("No API keys available (Roblox or server)")

    # Validate messages format
    if not isinstance(messages, list):
        print("[Error] messages must be a list")
        return None

    # Try up to 3 attempts
    for attempt in range(3):
        api_key = random.choice(key_pool)
        client = get_client(api_key)

        try:
            completion = await client.chat.completions.create(
                model=model,
                messages=messages
            )

            if not completion.choices:
                print("[Groq Error] No choices returned")
                continue

            return completion.choices[0].message.content

        except Exception as e:
            print(f"[Groq Error] Key failed: {api_key} | Attempt {attempt+1}/3 | {e}")

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

        # NEW: Roblox-provided API key
        roblox_key = data.get("roblox_api_key")

        if not model:
            return jsonify({"error": "Missing model"}), 400

        if not messages:
            return jsonify({"error": "Missing messages"}), 400

        reply = await groq_request(model, messages, roblox_key)

        if reply is None:
            return jsonify({"error": "All API keys failed"}), 502

        return jsonify({"reply": reply})

    except Exception as e:
        print("[Server Error]", e)
        return jsonify({"error": str(e)}), 500
