from quart import Quart, request, jsonify
from openai import AsyncOpenAI
import os

app = Quart(__name__)

client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

@app.post("/groq")
async def groq_proxy():
    try:
        data = await request.get_json(force=True)

        model = data.get("model")
        messages = data.get("messages")

        if not model or not messages:
            return jsonify({"error": "Missing model or messages"}), 400

        completion = await client.chat.completions.create(
            model=model,
            messages=messages
        )

        reply = completion.choices[0].message.content

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()

