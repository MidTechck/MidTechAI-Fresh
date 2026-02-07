from flask import Flask, render_template, request, jsonify
import random
import requests

app = Flask(__name__)

# -----------------------
# Offline memory & owner info
# -----------------------
OWNER_INFO = {
    "name": "Charles",
    "favorite_color": "black",
    "favorite_game": ["Minecraft", "eFootball"],
    "favorite_sport": "soccer",
    "favorite_team": "Chelsea"
}

BOT_INFO = {
    "name": "MidTechAI",
    "creator": OWNER_INFO["name"],
    "purpose": "To chat, provide information, advice, jokes, and comfort when needed.",
    "abilities": "Offline knowledge, online research, math, jokes, advice, time/date, owner info."
}

OFFLINE_RESPONSES = {
    "greetings": [
        "Hello there! How’s your day going?",
        "Hi! Nice to see you.",
        "Hey! How can I help you today?"
    ],
    "farewell": [
        "Goodbye! Talk to you soon.",
        "See you later! Stay safe.",
        "Bye! Have a great day."
    ],
    "comfort": [
        "I understand. Take a deep breath, everything will be fine.",
        "I’m here for you. Stay strong!",
        "It’s okay to feel that way. I’m with you."
    ],
    "jokes": [
        "Why don’t scientists trust atoms? Because they make up everything!",
        "Why did the math book look sad? Because it had too many problems!",
        "I would tell you a construction joke, but I’m still working on it!"
    ],
    "advice": [
        "Remember to take breaks and stay hydrated.",
        "Always focus on what you can control.",
        "Learning is a journey; don’t rush it."
    ]
}

# -----------------------
# Helper Functions
# -----------------------
def get_offline_reply(message):
    message = message.lower()

    # Greetings
    if any(greet in message for greet in ["hello", "hi", "hey"]):
        return random.choice(OFFLINE_RESPONSES["greetings"])

    # Farewell
    if any(farewell in message for farewell in ["bye", "goodbye", "see you"]):
        return random.choice(OFFLINE_RESPONSES["farewell"])

    # Comfort
    if any(word in message for word in ["sad", "tired", "sick", "unhappy"]):
        return random.choice(OFFLINE_RESPONSES["comfort"])

    # Jokes
    if "joke" in message:
        return random.choice(OFFLINE_RESPONSES["jokes"])

    # Advice
    if "advice" in message or "help me" in message:
        return random.choice(OFFLINE_RESPONSES["advice"])

    # Owner info
    if any(word in message for word in ["who created you", "who made you", "creator", "owner"]):
        return f"I was created by {OWNER_INFO['name']}."

    if "your name" in message or "who are you" in message:
        return BOT_INFO["name"]

    if "favorite color" in message:
        return f"My creator's favorite color is {OWNER_INFO['favorite_color']}."

    if "favorite game" in message:
        games = ", ".join(OWNER_INFO["favorite_game"])
        return f"My creator loves to play {games}."

    if "favorite sport" in message:
        return f"My creator's favorite sport is {OWNER_INFO['favorite_sport']}."

    if "favorite team" in message:
        return f"My creator supports {OWNER_INFO['favorite_team']}."

    return None

def fetch_wikipedia(query):
    """
    Fetch a summary from Wikipedia API.
    """
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "extract" in data:
                return data["extract"]
        return None
    except:
        return None

def fetch_duckduckgo(query):
    """
    Fetch a short summary from DuckDuckGo Instant Answer API.
    """
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&skip_disambig=1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("AbstractText"):
                return data["AbstractText"]
        return None
    except:
        return None

# -----------------------
# Routes
# -----------------------
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.get_json().get("message", "")
    
    # 1️⃣ Offline memory first
    reply = get_offline_reply(user_message)
    if reply:
        return jsonify({"reply": reply})

    # 2️⃣ Wikipedia summary
    wiki_reply = fetch_wikipedia(user_message)
    if wiki_reply:
        return jsonify({"reply": wiki_reply})

    # 3️⃣ DuckDuckGo Instant Answer
    ddg_reply = fetch_duckduckgo(user_message)
    if ddg_reply:
        return jsonify({"reply": ddg_reply})

    # 4️⃣ Final fallback
    return jsonify({"reply": "I’m not sure about that yet, but I’m learning more every day!"})

# -----------------------
# Run App
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
