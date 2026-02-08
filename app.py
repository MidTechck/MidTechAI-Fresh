from flask import Flask, render_template, request, jsonify
import json
import os
import requests

# ---------------- CONFIG ----------------
HF_TOKEN = os.getenv("HF_TOKEN")  # Hugging Face token
HF_API = "https://api-inference.huggingface.co/models/flan-t5-large"
WIKI_API = "https://en.wikipedia.org/w/api.php"

# ---------------- APP SETUP ----------------
app = Flask(__name__)

SELF_NAME = "MidTechAI"
OWNER_NAME = "Charles"

# Load or create knowledge
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
    q = question.lower()
    for key, val in knowledge["facts"].items():
        if key in q:
            return val
    if "your name" in q or "who are you" in q:
        return f"My name is {SELF_NAME}."
    if "my name" in q or "who am i" in q:
        return f"Your name is {knowledge.get('owner','Unknown')}."
    if "who is my owner" in q:
        return f"Your owner is {knowledge.get('owner','Unknown')}."
    return None

def query_wikipedia(question):
    """Search Wikipedia and return top summary"""
    try:
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": question
        }
        search_resp = requests.get(WIKI_API, params=search_params).json()
        results = search_resp.get("query", {}).get("search", [])
        if not results:
            return None
        top_title = results[0]["title"]
        summary_resp = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{top_title.replace(' ','_')}").json()
        extract = summary_resp.get("extract")
        if extract:
            knowledge["facts"][question.lower()] = extract
            with open("knowledge.json", "w") as f:
                json.dump(knowledge, f, indent=2)
            return extract
    except:
        return None

def query_hf(question, context=None):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": question if not context else context + "\n" + question}
    try:
        resp = requests.post(HF_API, headers=headers, json=payload, timeout=20)
        data = resp.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        elif isinstance(data, list):
            return data[0].get("generated_text", str(data[0]))
    except:
        return None

def get_answer(question):
    # greetings
    greetings = ["hello","hi","hey","good morning","good evening"]
    if any(g in question.lower() for g in greetings):
        return f"Hello {knowledge.get('owner','User')}! How are you today?"
    
    # local knowledge
    local = query_local(question)
    if local:
        return local

    # online knowledge
    wiki_answer = query_wikipedia(question)
    if wiki_answer:
        hf_answer = query_hf(question, context=wiki_answer)
        if hf_answer:
            return hf_answer
        return wiki_answer

    # Flan-T5 fallback
    hf_answer = query_hf(question)
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
    question = data.get("question","")
    if not question:
        return jsonify({"answer":"Please ask a question!"})
    answer = get_answer(question)
    return jsonify({"answer": answer})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
