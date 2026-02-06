import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversation_memory = []

def get_time_info():
    now = datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')} and the time is {now.strftime('%H:%M:%S')}."

def system_prompt():
    return """
You are MidTechAI Assistant.

Rules:
- You are intelligent, friendly, and futuristic.
- Do NOT mention your creator unless asked.
- If asked who created you, say: "I was created by Charles."
- You can do math, summarize, research, explain, and chat naturally.
- Understand greetings, farewells, and appreciation.
- If user asks for time/date, provide it.
- Keep responses clear and smart.
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message")

    if "time" in user_message.lower() or "date" in user_message.lower():
        return jsonify({"reply": get_time_info()})

    conversation_memory.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt()}] + conversation_memory
    )

    ai_reply = response.choices[0].message.content
    conversation_memory.append({"role": "assistant", "content": ai_reply})

    return jsonify({"reply": ai_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
