from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def query_huggingface(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 200}
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    result = response.json()
    if isinstance(result, list):
        return result[0]["generated_text"]
    return "I’m having trouble thinking right now."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    # Build smart prompt
    prompt = f"""
You are MidTechAI, a smart, friendly assistant created by Charles.
Answer clearly, like a human assistant.

User: {user_message}
Assistant:
"""

    reply = query_huggingface(prompt)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
