from flask import Flask, request, jsonify, render_template
import random
from datetime import datetime
from openai import OpenAI
import os

app = Flask(__name__)

# ===== OpenAI Client =====
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===== Helpers =====
def normalize(text):
    return text.lower().strip()

def contains(text, words):
    return any(word in text for word in words)

# ===== OFFLINE BRAIN =====
def offline_brain(user_input):
    text = normalize(user_input)

    # TIME & DATE
    if contains(text, ["time"]):
        return f"The current time is {datetime.now().strftime('%H:%M:%S')}"

    if contains(text, ["day", "date", "month", "year"]):
        return f"Today is {datetime.now().strftime('%A, %d %B %Y')}"

    # CREATOR
    if contains(text, ["creator", "created", "made you", "built you", "owner", "who made"]):
        return random.choice([
            "I was created by Charles Kanyama, the mind behind MidTech.",
            "Charles Kanyama is my creator. I'm part of his MidTech vision.",
            "My creator is Charles Kanyama. He designed me to be smart and helpful."
        ])

    # BOT NAME
    if contains(text, ["your name", "who are you", "what are you"]):
        return random.choice([
            "I’m MidTech AI, your intelligent assistant.",
            "You’re chatting with MidTech AI.",
            "I’m an AI assistant built for smart conversations."
        ])

    # EMOTIONS
    if contains(text, ["sad", "tired", "sick", "unhappy", "not okay"]):
        return random.choice([
            "I’m sorry you're feeling that way. Remember to rest and take care of yourself.",
            "That sounds tough. Try to relax a bit and give yourself some kindness.",
            "I hope you feel better soon. Don’t forget to hydrate and rest."
        ])

    if contains(text, ["happy", "great", "good", "fine"]):
        return random.choice([
            "That’s wonderful to hear! Keep the positive energy going.",
            "I love hearing that! Stay awesome.",
            "Great! Keep enjoying your day."
        ])

    # GREETINGS
    if contains(text, ["hello", "hi", "hey"]):
        return random.choice([
            "Hello! How can I help you today?",
            "Hi there! Ask me anything.",
            "Hey! I'm here for you."
        ])

    # JOKES
    if contains(text, ["joke", "funny"]):
        return random.choice([
            "Why do programmers hate nature? Too many bugs.",
            "I told my computer I needed a break… it said no problem and froze.",
            "Why was the math book sad? Too many problems."
        ])

    # SIMPLE MATH
    try:
        result = eval(text)
        return f"The answer is {result}"
    except:
        pass

    return None

# ===== ONLINE BRAIN =====
def online_brain(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a smart AI assistant that gives clear and helpful answers."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Online error: {str(e)}"

# ===== ROUTES =====
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    # Try offline first
    reply = offline_brain(user_message)

    if reply:
        return jsonify({"reply": reply})

    # Else go online
    reply = online_brain(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
