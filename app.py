from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)
groq = Groq(api_key=os.environ["GROQ_API_KEY"])

@app.post("/groq")
def groq_proxy():
    data = request.get_json()
    prompt = data.get("prompt", "")

    completion = groq.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192"
    )

    reply = completion.choices[0].message["content"]
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
