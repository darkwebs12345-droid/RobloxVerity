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
        print("Incoming JSON:", data)

        model = data.get("model")
        messages = data.get("messages")

        if not model or not messages:
            return jsonify({"error": "Missing model or messages"}), 400

        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )

        # Python uses 0‑based indexing
        reply = completion.choices[0].message["content"]

        return jsonify({
            "reply": reply
        })

    except Exception as e:
        print("SERVER ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

