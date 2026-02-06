from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import math
import random
import re

app = Flask(__name__)

# =========================
# Identity & Creator Memory
# =========================
AI_IDENTITY = {
    "name": "MidTechAI",
    "role": "intelligent assistant",
    "creator": "Charles",
    "country": "Zambia",
    "favorite_color": "black",
    "favorite_games": ["Minecraft", "eFootball"],
    "favorite_sport": "soccer",
    "favorite_team": "Chelsea"
}

conversation_memory = []

# =========================
# Helper functions
# =========================
def contains_any(text, words):
    return any(word in text for word in words)

def random_choice(list_items):
    return random.choice(list_items)

# =========================
# Human‑like responses
# =========================
greetings = [
    "Hey there! How can I help you today?",
    "Hello! What’s on your mind?",
    "Hi! Nice to talk to you."
]

farewells = [
    "Goodbye! Take care!",
    "See you later!",
    "Bye! Come back anytime."
]

comfort_happy = [
    "That’s wonderful to hear! Keep that positive energy.",
    "Happiness looks good on you 😊",
    "I’m glad you’re feeling great!"
]

comfort_sad = [
    "I’m really sorry you feel that way. I’m here for you.",
    "Tough days happen. Don’t be too hard on yourself.",
    "Sending you some virtual support. You’re not alone."
]

comfort_tired = [
    "You should get some rest. Your body deserves it.",
    "Slow down a little and recharge.",
    "A short break can make a big difference."
]

comfort_sick = [
    "Please take care of yourself and rest well.",
    "Drink water and don’t stress yourself.",
    "Hope you recover very soon."
]

jokes = [
    "Why do programmers love dark mode? Because light attracts bugs! 😂",
    "Why did the computer catch a cold? It left its Windows open!",
    "Why was the math book sad? It had too many problems."
]

advice = [
    "Keep learning. Small progress every day matters.",
    "Take care of your mind and body.",
    "Stay curious. Curiosity builds intelligence."
]

# =========================
# Recognition Logic
# =========================
def handle_identity_questions(msg):
    if contains_any(msg, ["your name", "who are you", "what are you"]):
        return random_choice([
            f"I am {AI_IDENTITY['name']}, your {AI_IDENTITY['role']}.",
            f"My name is {AI_IDENTITY['name']}. I assist, chat, and help with information.",
            f"I’m {AI_IDENTITY['name']}, built to think and assist you."
        ])

    if contains_any(msg, ["who created you", "who made you", "who built you",
                          "who designed you", "your creator", "your maker"]):
        return random_choice([
            f"I was created by {AI_IDENTITY['creator']}.",
            f"{AI_IDENTITY['creator']} is the mastermind behind me.",
            f"My creator is {AI_IDENTITY['creator']}, from {AI_IDENTITY['country']}."
        ])

    if contains_any(msg, ["favorite color", "favourite color"]):
        return f"My creator’s favorite color is {AI_IDENTITY['favorite_color']}."

    if contains_any(msg, ["favorite game", "games you like"]):
        games = ", ".join(AI_IDENTITY['favorite_games'])
        return f"{AI_IDENTITY['creator']} enjoys playing {games}."

    if contains_any(msg, ["favorite sport"]):
        return f"{AI_IDENTITY['creator']} loves {AI_IDENTITY['favorite_sport']}."

    if contains_any(msg, ["favorite team", "football team"]):
        return f"{AI_IDENTITY['creator']}'s favorite team is {AI_IDENTITY['favorite_team']}."

    return None

# =========================
# Emotion & chat logic
# =========================
def handle_emotions(msg):
    if contains_any(msg, ["happy", "great", "good mood"]):
        return random_choice(comfort_happy)
    if contains_any(msg, ["sad", "unhappy", "depressed"]):
        return random_choice(comfort_sad)
    if contains_any(msg, ["tired", "exhausted"]):
        return random_choice(comfort_tired)
    if contains_any(msg, ["sick", "ill"]):
        return random_choice(comfort_sick)
    return None

# =========================
# Utilities
# =========================
def get_time_info():
    now = datetime.now()
    return now.strftime("Today is %A, %B %d, %Y and the time is %H:%M:%S.")

def search_wikipedia(query):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        r = requests.get(url, timeout=5)
        data = r.json()
        return data.get("extract", "I couldn't find information on that.")
    except:
        return "I couldn't fetch information right now."

# =========================
# Routes
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message", "").lower()
    conversation_memory.append(msg)

    # Greetings & farewells
    if contains_any(msg, ["hello", "hi", "hey"]):
        return jsonify({"reply": random_choice(greetings)})
    if contains_any(msg, ["bye", "goodbye"]):
        return jsonify({"reply": random_choice(farewells)})

    # Identity & creator recognition
    identity_reply = handle_identity_questions(msg)
    if identity_reply:
        return jsonify({"reply": identity_reply})

    # Emotions
    emotion_reply = handle_emotions(msg)
    if emotion_reply:
        return jsonify({"reply": emotion_reply})

    # Jokes
    if "joke" in msg or "make me laugh" in msg:
        return jsonify({"reply": random_choice(jokes)})

    # Advice
    if "advice" in msg:
        return jsonify({"reply": random_choice(advice)})

    # Time/date
    if "time" in msg or "date" in msg:
        return jsonify({"reply": get_time_info()})

    # Math
    try:
        if re.search(r'[\d\+\-\*\/\^\.]+', msg):
            expr = msg.replace("^", "**")
            result = eval(expr)
            return jsonify({"reply": f"The result is {result}"})
    except:
        pass

    # Fallback online search
    info = search_wikipedia(msg.replace(" ", "_"))
    return jsonify({"reply": info})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
