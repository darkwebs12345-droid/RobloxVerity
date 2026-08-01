from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

@app.post("/groq")
def groq_proxy():
    try:
        data = request.get_json(force=True)

        # Extract correct fields
        model = data.get("model")
        messages = data.get("messages")

        # Validate
        if not model or not messages:
            return jsonify({"error": "Missing model or messages"}), 400

        # Forward EXACTLY what Roblox sent
        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )

        reply = completion.choices[1].message["content"]

        return jsonify({
            "reply": reply,
            "raw": completion
        })

    except Exception as e:
        print("SERVER ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

