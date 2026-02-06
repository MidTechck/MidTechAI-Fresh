from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests

app = Flask(__name__)

conversation_memory = []

# Simple offline responses
offline_responses = {
    "hello": "Hi there! How can I help you today?",
    "hi": "Hello! What can I do for you?",
    "who created you": "I was created by Charles.",
    "your name": "I am called MidTechAI, your assistant.",
    "bye": "Goodbye! Have a great day!",
    "thanks": "You're welcome! 😊",
    "thank you": "No problem!"
}

def get_time_info():
    now = datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')} and the time is {now.strftime('%H:%M:%S')}."

def search_wikipedia(query):
    """Fetch a short summary from Wikipedia for free."""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        r = requests.get(url, timeout=5)
        data = r.json()
        if 'extract' in data:
            return data['extract']
        else:
            return "I couldn't find information on that topic."
    except:
        return "I couldn't fetch information right now."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower()
    conversation_memory.append({"role": "user", "content": user_message})

    # Check for greetings / offline responses
    for key, response in offline_responses.items():
        if key in user_message:
            conversation_memory.append({"role": "assistant", "content": response})
            return jsonify({"reply": response})

    # Check for time/date
    if "time" in user_message or "date" in user_message:
        reply = get_time_info()
        conversation_memory.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})

    # Check for math expressions
    try:
        if any(op in user_message for op in ["+", "-", "*", "/", "^"]):
            expr = user_message.replace("^", "**")
            result = eval(expr)
            reply = f"The result is: {result}"
            conversation_memory.append({"role": "assistant", "content": reply})
            return jsonify({"reply": reply})
    except:
        pass

    # Try free online search (Wikipedia)
    search_result = search_wikipedia(user_message.replace(" ", "_"))
    conversation_memory.append({"role": "assistant", "content": search_result})
    return jsonify({"reply": search_result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
