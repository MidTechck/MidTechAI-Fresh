from flask import Flask, render_template, request, jsonify
import json
import os
import asyncio
import aiohttp

# ---------------- CONFIG ----------------
HF_TOKEN = os.getenv("HF_TOKEN")  # Hugging Face token
HF_API = "https://api-inference.huggingface.co/models/flan-t5-large"
WIKI_SEARCH_API = "https://en.wikipedia.org/w/api.php"

# ---------------- APP SETUP ----------------
app = Flask(__name__)

# Self and owner info
SELF_NAME = "MidTechAI"
OWNER_NAME = "Charles"  # change as needed

# Load or create local knowledge
if os.path.exists("knowledge.json"):
    with open("knowledge.json", "r") as f:
        knowledge = json.load(f)
else:
    knowledge = {
        "owner": OWNER_NAME,
        "self_name": SELF_NAME,
        "facts": {}
    }

# ---------------- HELPERS ----------------
def query_local(question):
    q_lower = question.lower()
    for key, val in knowledge["facts"].items():
        if key in q_lower:
            return val
    # Self-awareness and owner recognition
    if "your name" in q_lower or "who are you" in q_lower:
        return f"My name is {SELF_NAME}."
    if "my name" in q_lower or "who am i" in q_lower:
        return f"Your name is {knowledge.get('owner', 'Unknown')}."
    if "who is my owner" in q_lower:
        return f"Your owner is {knowledge.get('owner', 'Unknown')}."
    return None

async def query_wikipedia(question):
    """Search Wikipedia and return summary."""
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": question
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(WIKI_SEARCH_API, params=params) as resp:
                data = await resp.json()
                search_results = data.get("query", {}).get("search", [])
                if not search_results:
                    return None
                top_title = search_results[0]["title"]
                async with session.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{top_title.replace(' ','_')}") as summary_resp:
                    if summary_resp.status == 200:
                        summary_data = await summary_resp.json()
                        extract = summary_data.get("extract")
                        if extract:
                            knowledge["facts"][question.lower()] = extract
                            with open("knowledge.json", "w") as f:
                                json.dump(knowledge, f, indent=2)
                            return extract
    except:
        return None

async def query_hf(question, context=None):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    prompt = question if not context else context + "\n" + question
    payload = {"inputs": prompt}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(HF_API, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and "generated_text" in data[0]:
                        return data[0]["generated_text"]
                    elif isinstance(data, list):
                        return data[0].get("generated_text", str(data[0]))
    except:
        return None

async def get_answer(question, memory=None):
    # Greetings
    greetings = ["hello", "hi", "hey", "good morning", "good evening"]
    if any(greet in question.lower() for greet in greetings):
        return f"Hello {knowledge.get('owner','User')}! How are you today?"

    # Local knowledge
    local = query_local(question)
    if local:
        return local

    # Wikipedia search
    wiki_answer = await query_wikipedia(question)
    if wiki_answer:
        hf_answer = await query_hf(question, context=wiki_answer)
        if hf_answer:
            return hf_answer
        return wiki_answer

    # Flan-T5 fallback
    context = "\n".join(memory) if memory else None
    hf_answer = await query_hf(question, context=context)
    if hf_answer:
        return hf_answer

    return "I'm not sure yet, but I'm learning more every day!"

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"answer": "Please ask a question!"})
    answer = asyncio.run(get_answer(question, memory=[]))
    return jsonify({"answer": answer})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
