from flask import Flask, request, jsonify, render_template
import random
import os
import requests

app = Flask(__name__)

# ================== BOT / OWNER INFO ==================
BOT_NAME = "MidTechAI"
OWNER_NAME = "Charles Kanyama"
FAVORITES = {
    "color": "black",
    "game": "Minecraft and eFootball",
    "sport": "soccer",
    "team": "Chelsea"
}

# ================== HUGGING FACE SETUP ==================
HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}


def ask_huggingface(prompt):
    try:
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200, "temperature": 0.7},
        }
        r = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        data = r.json()
        if isinstance(data, list):
            return data[0]["generated_text"]
        return "I’m thinking..."
    except:
        return None


# ================== OFFLINE BRAIN ==================
def brain(user):
    u = user.lower()

    greetings = [
        "Hey there! 😊",
        "Hello! How can I help you today?",
        "Hi! I'm here for you.",
    ]

    jokes = [
        "Why don’t programmers like nature? Too many bugs.",
        "Why did the computer get cold? It forgot to close windows.",
    ]

    comfort = [
        "I'm really sorry you're feeling that way. I'm here for you.",
        "That sounds tough. Take a deep breath — you’re not alone.",
    ]

    # ================== INTENT MATCHING ==================
    if any(w in u for w in ["hello", "hi", "hey"]):
        return random.choice(greetings)

    if "your name" in u:
        return f"My name is {BOT_NAME}."

    if "who created you" in u or "who made you" in u:
        return f"I was created by {OWNER_NAME}. His favorite color is {FAVORITES['color']} and he loves {FAVORITES['game']}."

    if "joke" in u:
        return random.choice(jokes)

    if any(w in u for w in ["sad", "tired", "sick", "upset"]):
        return random.choice(comfort)

    if "favorite" in u and "team" in u:
        return f"{OWNER_NAME}'s favorite team is {FAVORITES['team']}."

    # Add more offline knowledge here as needed

    return None


# ================== ROUTES ==================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    # 1️⃣ Offline brain first
    reply = brain(user_message)

    # 2️⃣ Online fallback (Flan-T5)
    if not reply:
        hf_reply = ask_huggingface(user_message)
        if hf_reply:
            reply = hf_reply
        else:
            reply = "I’m not sure yet, but I’m learning every day!"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
