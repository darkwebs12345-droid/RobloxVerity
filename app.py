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
        prompt = data.get("prompt")

        if not prompt:
            return jsonify({"error": "Missing 'prompt'"}), 400

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        # This matches the response format in your screenshot
        reply = completion.choices[0].message["content"]

        return jsonify({
            "reply": reply,
            "raw": completion  # optional: lets you inspect full Groq response
        })

    except Exception as e:
        print("SERVER ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

