from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ------------------------------
# BASIC MEMORY (offline knowledge)
# ------------------------------
memory = {
    "hello": "Hello! I am MidTechAI. Ask me anything.",
    "hi": "Hi there! How can I help you today?",
}


# ------------------------------
# INTERNET RESEARCH FUNCTIONS
# ------------------------------

def search_wikipedia(query):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("extract")
    except:
        return None


def search_duckduckgo(query):
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        return data.get("AbstractText")
    except:
        return None


def research_online(question):
    # Try Wikipedia first
    answer = search_wikipedia(question.replace(" ", "_"))
    if answer:
        return answer

    # Then DuckDuckGo
    answer = search_duckduckgo(question)
    if answer:
        return answer

    return None


# ------------------------------
# AI BRAIN
# ------------------------------

def midtechai_brain(user_message):
    msg = user_message.lower().strip()

    # 1. Check memory first
    if msg in memory:
        return memory[msg]

    # 2. If not known → research online
    online_answer = research_online(user_message)
    if online_answer:
        return online_answer

    # 3. Final fallback
    return "I couldn't find information about that yet. Try asking in a different way."


# ------------------------------
# API ROUTES
# ------------------------------

@app.route("/", methods=["GET"])
def home():
    return "MidTechAI is running!"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    reply = midtechai_brain(user_message)

    return jsonify({
        "user": user_message,
        "reply": reply
    })


# ------------------------------
# RUN SERVER
# ------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
