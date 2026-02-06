from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import math
import random

app = Flask(__name__)

# Conversation memory
conversation_memory = []

# Offline knowledge
offline_responses = {
    "hello": ["Hi there!", "Hello! How can I help you?", "Hey! Nice to see you!"],
    "hi": ["Hello!", "Hi! What’s up?", "Hey there!"],
    "how are you": ["I’m great! How about you?", "Feeling fantastic!", "I’m good, thanks for asking!"],
    "who created you": ["I was created by Charles.", "Charles made me!"],
    "your name": ["I am MidTechAI, your personal assistant.", "You can call me MidTechAI."],
    "bye": ["Goodbye! Have a great day!", "See you later!", "Farewell!"],
    "thanks": ["You're welcome! 😊", "No problem!", "Anytime!"],
    "thank you": ["No problem!", "You're welcome!", "Happy to help!"],
    "what do you do": ["I answer questions, do math, and chat with you!", "I am here to help you!"],
    "who are you": ["I am your assistant, MidTechAI.", "I am an AI assistant built by Charles."]
}

# Trivia knowledge
trivia = {
    "capital of france": "The capital of France is Paris.",
    "capital of zambia": "The capital of Zambia is Lusaka.",
    "einstein": "Albert Einstein was a theoretical physicist famous for the theory of relativity.",
    "newton": "Sir Isaac Newton formulated the laws of motion and gravity."
}

def get_time_info():
    now = datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')} and the time is {now.strftime('%H:%M:%S')}."

def search_wikipedia(query):
    """Free online fetch from Wikipedia"""
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

    # Offline responses
    for key, responses in offline_responses.items():
        if key in user_message:
            reply = random.choice(responses)
            conversation_memory.append({"role": "assistant", "content": reply})
            return jsonify({"reply": reply})

    # Trivia offline
    for key, answer in trivia.items():
        if key in user_message:
            conversation_memory.append({"role": "assistant", "content": answer})
            return jsonify({"reply": answer})

    # Time/date
    if "time" in user_message or "date" in user_message:
        reply = get_time_info()
        conversation_memory.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})

    # Math expressions
    try:
        if any(op in user_message for op in ["+", "-", "*", "/", "^"]):
            expr = user_message.replace("^", "**")
            result = eval(expr)
            reply = f"The result is: {result}"
            conversation_memory.append({"role": "assistant", "content": reply})
            return jsonify({"reply": reply})
        if "sqrt" in user_message:
            num = float(user_message.split("sqrt")[-1].strip())
            reply = f"The square root of {num} is {math.sqrt(num)}"
            conversation_memory.append({"role": "assistant", "content": reply})
            return jsonify({"reply": reply})
    except:
        pass

    # Fallback online fetch
    search_result = search_wikipedia(user_message.replace(" ", "_"))
    conversation_memory.append({"role": "assistant", "content": search_result})
    return jsonify({"reply": search_result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
