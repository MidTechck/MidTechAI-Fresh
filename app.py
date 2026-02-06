from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    try:
        now = datetime.now()
        time_info = now.strftime("%A, %d %B %Y | %H:%M")

        system_prompt = f"""
You are a smart AI assistant.
You can do math, explain things, summarize, and search knowledge.
You know the current date and time: {time_info}.
Be friendly, natural, and helpful.
Only reveal your name or creator if asked.
"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
