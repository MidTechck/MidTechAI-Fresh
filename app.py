from flask import Flask, render_template, request, jsonify
import json
import os
import asyncio
import aiohttp

# ---------- CONFIG ----------
HF_TOKEN = os.getenv("HF_TOKEN")  # Hugging Face token
HF_API = "https://api-inference.huggingface.co/models/flan-t5-large"

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# ---------- APP SETUP ----------
app = Flask(__name__)

# Load local knowledge
if os.path.exists("knowledge.json"):
    with open("knowledge.json", "r") as f:
        knowledge = json.load(f)
else:
    knowledge = {"owner": "Unknown", "facts": {}}

# ---------- HELPERS ----------
def query_local(question):
    """
    Check local knowledge first
    """
    q_lower = question.lower()
    for key, val in knowledge["facts"].items():
        if key in q_lower:
            return val
    # owner recognition
    if "who is my owner" in q_lower:
        return f"Your owner is {knowledge.get('owner', 'Unknown')}."
    return None

async def query_wikipedia(question):
    """
    Try Wikipedia API for factual answers
    """
    try:
        search_term = question.replace(" ", "_")
        async with aiohttp.ClientSession() as session:
            async with session.get(WIKI_API + search_term) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("extract", None)
    except:
        return None

async def query_hf(question, context=None):
    """
    Query Hugging Face Flan-T5 API asynchronously
    """
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    prompt = question if not context else context + "\n" + question
    payload = {"inputs": prompt}
    async with aiohttp.ClientSession() as session:
        async with session.post(HF_API, headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                if isinstance(data, list) and "generated_text" in data[0]:
                    return data[0]["generated_text"]
                elif isinstance(data, list):
                    return data[0].get("generated_text", str(data[0]))
            return None

async def get_answer(question, memory=None):
    # 1. Greetings & casual conversation
    greetings = ["hello", "hi", "hey", "good morning", "good evening"]
    if any(greet in question.lower() for greet in greetings):
        return "Hello! How are you today?"

    # 2. Local knowledge
    local = query_local(question)
    if local:
        return local

    # 3. Wikipedia online fallback
    wiki_answer = await query_wikipedia(question)
    if wiki_answer:
        return wiki_answer

    # 4. Hugging Face reasoning fallback
    context = "\n".join(memory) if memory else None
    hf_answer = await query_hf(question, context=context)
    if hf_answer:
        return hf_answer

    # 5. Default response
    return "I'm not sure yet, but I'm learning more every day!"

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"answer": "Please ask a question!"})

    # memory could be enhanced for multi-turn conversations
    answer = asyncio.run(get_answer(question, memory=[]))
    return jsonify({"answer": answer})

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
