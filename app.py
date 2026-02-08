from flask import Flask, render_template, request, jsonify
import json
import random
import requests
import os

app = Flask(__name__)

# -----------------------------
# Offline Knowledge & Personality
# -----------------------------
offline_knowledge = {
    "assistant_name": "MidTechAI",
    "creator": "Your Name",
    "creator_favorites": {
        "color": "black",
        "game": ["Minecraft", "eFootball"],
        "sport": "soccer",
        "team": "Chelsea"
    },
    "greetings": [
        "Hey there!", "Hi! How’s it going?", "Hello! 😊", "Yo! What's up?"
    ],
    "farewells": [
        "Bye! Take care!", "See you later!", "Catch you soon!", "Goodbye!"
    ],
    "comforts": [
        "I’m here for you.", "Everything will be okay.", "Sending virtual hugs 🤗"
    ],
    "apologies": [
        "Sorry about that.", "My bad!", "I’ll do better next time."
    ],
    "appreciations": [
        "Thanks a lot!", "Much appreciated!", "I’m glad you said that!"
    ]
}

# -----------------------------
# Hugging Face API setup
# -----------------------------
HF_TOKEN = os.getenv("HF_TOKEN") or "YOUR_HF_TOKEN_HERE"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}
HF_MODEL = "google/flan-t5-small"

def humanize_response(text, user_input):
    payload = {
        "inputs": f"Explain this to a human in a friendly conversational way:\n{text}\nUser asked: {user_input}",
        "parameters": {"max_new_tokens": 300}
    }
    try:
        r = requests.post(f"https://api-inference.huggingface.co/models/{HF_MODEL}",
                          headers=HEADERS, json=payload, timeout=10)
        if r.status_code == 200:
            return r.json()[0].get('generated_text', text)
    except:
        pass
    return text

# -----------------------------
# Offline Response
# -----------------------------
def offline_reply(user_input):
    lower = user_input.lower()
    
    if any(g in lower for g in ["hello", "hi", "hey", "yo"]):
        return random.choice(offline_knowledge["greetings"])
    
    if any(f in lower for f in ["bye", "goodbye", "see you"]):
        return random.choice(offline_knowledge["farewells"])
    
    if any(w in lower for w in ["sad", "tired", "sick", "happy"]):
        return random.choice(offline_knowledge["comforts"])
    
    if "sorry" in lower:
        return random.choice(offline_knowledge["apologies"])
    
    if any(w in lower for w in ["thank", "thanks"]):
        return random.choice(offline_knowledge["appreciations"])
    
    if any(w in lower for w in ["who created you", "who is your creator", "who made you"]):
        fav = offline_knowledge["creator_favorites"]
        return f"I was created by {offline_knowledge['creator']}. " \
               f"They love {fav['color']}, play {', '.join(fav['game'])}, " \
               f"enjoy {fav['sport']}, and their favorite team is {fav['team']}."
    
    if any(w in lower for w in ["your name", "who are you"]):
        return f"My name is {offline_knowledge['assistant_name']}. I’m your assistant!"
    
    return None

# -----------------------------
# Online Search
# -----------------------------
def online_search(query):
    try:
        wiki_resp = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}",
            timeout=3
        )
        if wiki_resp.status_code == 200:
            data = wiki_resp.json()
            if "extract" in data:
                return data["extract"]
    except:
        pass
    try:
        ddg_resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": 1},
            timeout=3
        )
        data = ddg_resp.json()
        answer = data.get("AbstractText")
        if answer:
            return answer
    except:
        pass
    return None

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message")
    
    reply = offline_reply(user_input)
    if reply:
        return jsonify({"reply": reply})
    
    search_result = online_search(user_input)
    if search_result:
        reply = humanize_response(search_result, user_input)
        return jsonify({"reply": reply})
    
    return jsonify({"reply": "I’m thinking about that… give me a moment."})

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
