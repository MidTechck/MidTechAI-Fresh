from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import random
import re

app = Flask(__name__)

# =========================
# Identity & Creator Memory
# =========================
AI = {
    "name": "MidTechAI",
    "creator": "Charles",
    "country": "Zambia",
    "favorite_color": "black",
    "favorite_games": ["Minecraft", "eFootball"],
    "favorite_sport": "soccer",
    "favorite_team": "Chelsea"
}

# =========================
# Conversation Memory
# =========================
memory = {
    "user_name": None,
    "history": []
}

# =========================
# Offline Knowledge Base
# =========================
offline_knowledge = {
    "python": "Python is a powerful programming language used for web, AI, automation and more.",
    "html": "HTML is used to structure content on the web.",
    "css": "CSS styles and designs web pages.",
    "javascript": "JavaScript makes websites interactive.",
    "zambia": "Zambia is a country in Southern Africa, known for Victoria Falls.",
    "ai": "Artificial Intelligence allows machines to simulate human intelligence.",
    "flask": "Flask is a lightweight Python web framework.",
    "github": "GitHub is a platform for hosting and collaborating on code.",
}

# =========================
# Helper Functions
# =========================
def say_random(options):
    return random.choice(options)

def contains(text, words):
    return any(word in text for word in words)

# =========================
# Human Responses
# =========================
greetings = ["Hello! How can I help you?", "Hi there!", "Hey! What’s up?"]
farewells = ["Goodbye!", "See you later!", "Bye!"]

happy = ["That’s great to hear!", "I love the positive energy!", "Nice! Keep smiling."]
sad = ["I’m here for you.", "Sorry you feel that way.", "Things will get better."]
tired = ["You should rest a bit.", "Take a short break.", "Relax and recharge."]
sick = ["Please rest and drink water.", "Hope you recover soon.", "Take care of yourself."]

jokes = [
    "Why do programmers love dark mode? Because light attracts bugs!",
    "Why did the computer get cold? It forgot to close its Windows!",
]

# =========================
# Identity Recognition
# =========================
def identity_answers(msg):
    if contains(msg, ["your name", "who are you"]):
        return f"I am {AI['name']}."
    if contains(msg, ["who created you", "who made you", "your creator"]):
        return f"I was created by {AI['creator']} from {AI['country']}."
    if "favorite color" in msg:
        return f"My creator's favorite color is {AI['favorite_color']}."
    if "favorite game" in msg:
        return f"He enjoys {', '.join(AI['favorite_games'])}."
    if "favorite sport" in msg:
        return f"He loves {AI['favorite_sport']}."
    if "favorite team" in msg:
        return f"His favorite team is {AI['favorite_team']}."
    return None

# =========================
# Emotion Detection
# =========================
def emotion_reply(msg):
    if contains(msg, ["happy", "good", "great"]):
        return say_random(happy)
    if contains(msg, ["sad", "down"]):
        return say_random(sad)
    if contains(msg, ["tired", "exhausted"]):
        return say_random(tired)
    if contains(msg, ["sick", "ill"]):
        return say_random(sick)
    return None

# =========================
# Offline Answer
# =========================
def offline_answer(msg):
    for key in offline_knowledge:
        if key in msg:
            return offline_knowledge[key]
    return None

# =========================
# Online Wikipedia
# =========================
def online_search(query):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        r = requests.get(url, timeout=4)
        data = r.json()
        return data.get("extract")
    except:
        return None

# =========================
# Routes
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message", "").lower()
    memory["history"].append(msg)

    # Learn user name
    if "my name is" in msg:
        name = msg.split("my name is")[-1].strip().title()
        memory["user_name"] = name
        return jsonify({"reply": f"Nice to meet you, {name}!"})

    # Greetings
    if contains(msg, ["hello", "hi", "hey"]):
        return jsonify({"reply": say_random(greetings)})

    # Identity
    identity = identity_answers(msg)
    if identity:
        return jsonify({"reply": identity})

    # Emotions
    emo = emotion_reply(msg)
    if emo:
        return jsonify({"reply": emo})

    # Jokes
    if "joke" in msg:
        return jsonify({"reply": say_random(jokes)})

    # Math
    try:
        if re.search(r'[\d\+\-\*\/\^\.]+', msg):
            result = eval(msg.replace("^", "**"))
            return jsonify({"reply": f"The result is {result}"})
    except:
        pass

    # Offline knowledge first
    off = offline_answer(msg)
    if off:
        return jsonify({"reply": off})

    # Online search fallback
    online = online_search(msg.replace(" ", "_"))
    if online:
        return jsonify({"reply": online})

    return jsonify({"reply": "I’m not sure about that yet, but I’m learning more every day!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
