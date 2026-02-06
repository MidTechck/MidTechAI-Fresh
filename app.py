from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import math
import random

app = Flask(__name__)

conversation_memory = []

# ====================
# Creator info (real favorites)
# ====================
creator_info = {
    "name": "Charles",
    "favorite_color": "black",
    "favorite_game": ["Minecraft", "eFootball"],
    "favorite_sport": "soccer",
    "favorite_team": "Chelsea",
    "country": "Zambia"
}

# ====================
# Offline responses
# ====================
offline_responses = {
    # Greetings
    "hello": ["Hi there!", "Hello! How can I help you?", "Hey! Nice to see you!"],
    "hi": ["Hello!", "Hi! What’s up?", "Hey there!"],
    "hey": ["Hey!", "Hello! How’s it going?", "Hi there!"],

    # Farewells
    "bye": ["Goodbye! Have a great day!", "See you later!", "Farewell! Take care!"],
    "goodbye": ["Bye! Stay safe!", "See you soon!", "Catch you later!"],

    # Appreciation
    "thanks": ["You're welcome! 😊", "No problem!", "Anytime!"],
    "thank you": ["No problem!", "You're welcome!", "Happy to help!"],

    # Name
    "your name": [
        "I am MidTechAI, your personal assistant.",
        "You can call me MidTechAI.",
        "MidTechAI at your service!"
    ],

    # General purpose
    "what do you do": [
        "I answer questions, do math, tell jokes, and chat with you!",
        "I am here to assist you in learning and exploring!",
        "I can provide advice, answers, and even cheer you up!"
    ],
    "who are you": [
        "I am your assistant, MidTechAI.",
        "I am an AI helper created to make your life easier.",
        "MidTechAI here! I can chat, calculate, and fetch info."
    ],

    # Emotions / comfort
    "i am happy": [
        "I'm glad to hear that! 😊 Keep smiling!",
        "Happiness is contagious! Enjoy your day!",
        "Yay! Stay positive and have fun!"
    ],
    "i am sad": [
        "I'm here for you. Things will get better.",
        "Sadness comes and goes. Take a deep breath.",
        "I know it’s tough. Sending virtual support!"
    ],
    "i am tired": [
        "Rest is important. Take a break if you can!",
        "Don’t push too hard! Relax for a while.",
        "Listen to your body and recharge. You deserve it!"
    ],
    "i am sick": [
        "I’m sorry to hear that. Drink water and rest well.",
        "Take care of yourself! Health comes first.",
        "Hope you feel better soon! Remember to stay hydrated."
    ],

    # Small talk
    "how are you": [
        "I’m doing great! How about you?",
        "Feeling fantastic today! What about you?",
        "I’m good! Ready to help you anytime."
    ],
    "what's up": [
        "Just assisting you, as always!",
        "Exploring knowledge and chatting with you.",
        "Staying sharp and ready for questions!"
    ],

    # Jokes
    "tell me a joke": [
        "Why did the computer go to the doctor? Because it caught a virus! 😂",
        "Why did the smartphone need glasses? Because it lost its contacts! 😎",
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛"
    ],

    # Advice
    "give me advice": [
        "Always keep learning and never stop exploring!",
        "Remember to take breaks and take care of yourself.",
        "Stay curious and keep asking questions!"
    ]
}

# ====================
# Creator question variations
# ====================
creator_questions = [
    "who created you", "who is your creator", "who made you",
    "who built you", "who designed you", "who is your maker", "who is your father"
]

for q in creator_questions:
    offline_responses[q] = [
        f"I was created by {creator_info['name']}, your tech genius.",
        f"{creator_info['name']} made me with care and code.",
        f"My creator is {creator_info['name']}, who loves {creator_info['favorite_color']} and enjoys {random.choice(creator_info['favorite_game'])}.",
        f"{creator_info['name']} is from {creator_info['country']} and loves {creator_info['favorite_sport']}, supporting {creator_info['favorite_team']}!"
    ]

# Trivia / offline knowledge
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

    # ====================
    # Offline response match
    # ====================
    for key, responses in offline_responses.items():
        if key in user_message:
            reply = random.choice(responses)
            conversation_memory.append({"role": "assistant", "content": reply})
            return jsonify({"reply": reply})

    # ====================
    # Trivia offline
    # ====================
    for key, answer in trivia.items():
        if key in user_message:
            conversation_memory.append({"role": "assistant", "content": answer})
            return jsonify({"reply": answer})

    # ====================
    # Time/date
    # ====================
    if "time" in user_message or "date" in user_message:
        reply = get_time_info()
        conversation_memory.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})

    # ====================
    # Math
    # ====================
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

    # ====================
    # Fallback online fetch
    # ====================
    search_result = search_wikipedia(user_message.replace(" ", "_"))
    conversation_memory.append({"role": "assistant", "content": search_result})
    return jsonify({"reply": search_result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
