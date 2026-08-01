from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

# Safe API key loading
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise Exception("GROQ_API_KEY is missing from environment variables")

groq = Groq(api_key=api_key)

@app.post("/groq")
def groq_proxy():
    try:
        # Force JSON parsing (prevents NoneType errors)
        data = request.get_json(force=True)

        # Validate JSON structure
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON"}), 400

        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "Missing 'prompt' field"}), 400

        # Groq API call
        completion = groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192"
        )

        reply = completion.choices[0].message["content"]

        return jsonify({"reply": reply})

    except Exception as e:
        # Print error to logs for debugging
        print("SERVER ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
