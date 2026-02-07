from flask import Flask, render_template, request, jsonify
import requests
import datetime
import random

# ---------------- FLASK APP ----------------
app = Flask(__name__)

# ---------------- CREATOR INFO ----------------
creator_info = {
    "name": "Charles Kanyama",
    "color": "black",
    "games": "Minecraft, eFootball",
    "sport": "Soccer",
    "team": "Chelsea"
}

# ---------------- HELPER FUNCTIONS ----------------
def clean_text(text):
    remove = [
        "who is", "who was", "what is", "tell me about",
        "explain", "define", "meaning of", "country",
        "the", "a", "an", "in", "on", "at"
    ]
    t = text.lower()
    for r in remove:
        t = t.replace(r, "")
    return t.strip()


def wiki_search(query):
    try:
        search = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":query,"format":"json"},
            timeout=5
        ).json()
        title = search["query"]["search"][0]["title"]
        summary = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}", timeout=5
        ).json()
        return summary.get("extract")
    except:
        return None


def country_info(name):
    try:
        r = requests.get(f"https://restcountries.com/v3.1/name/{name}", timeout=5).json()[0]
        return f"{r['name']['common']} — Capital: {r['capital'][0]}, Population: {r['population']}"
    except:
        return None


def get_time():
    try:
        r = requests.get("http://worldtimeapi.org/api/timezone/Africa/Lusaka", timeout=5).json()
        return r["datetime"]
    except:
        return str(datetime.datetime.now())


def get_joke():
    try:
        j = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5).json()
        return f"{j['setup']} — {j['punchline']}"
    except:
        return "Why don’t programmers like nature? Too many bugs."


def get_advice():
    try:
        a = requests.get("https://api.adviceslip.com/advice", timeout=5).json()
        return a["slip"]["advice"]
    except:
        return "Stay positive and keep learning."


def get_quote():
    try:
        q = requests.get("https://api.quotable.io/random", timeout=5).json()
        return f"{q['content']} — {q['author']}"
    except:
        return "Keep going."


def get_news():
    try:
        r = requests.get(
            "https://api.rss2json.com/v1/api.json?rss_url=http://feeds.bbci.co.uk/news/rss.xml", timeout=5
        ).json()
        return "\n".join([item["title"] for item in r["items"][:3]])
    except:
        return "No news available."


# ---------------- CHAT LOGIC ----------------
def smart_reply(message):
    m = message.lower()

    greetings = ["hello","hi","hey","good morning","good evening"]
    farewells = ["bye","goodbye","see you","later"]

    if any(g in m for g in greetings):
        return random.choice([
            "Hello! How can I help you?",
            "Hi there! Ready to chat?",
            "Hey! What's up?"
        ])

    if any(f in m for f in farewells):
        return random.choice([
            "Goodbye! Have a great day.",
            "See you later!",
            "Bye! Stay safe."
        ])

    if "who created" in m or "creator" in m:
        return f"I was created by {creator_info['name']}."

    if "favorite color" in m:
        return f"My creator's favorite color is {creator_info['color']}."

    if "favorite game" in m:
        return f"{creator_info['name']} enjoys {creator_info['games']}."

    if "sport" in m or "team" in m:
        return f"The favorite team is {creator_info['team']}."

    if "joke" in m:
        return get_joke()

    if "advice" in m:
        return get_advice()

    if "quote" in m or "motivate" in m:
        return get_quote()

    if "time" in m or "date" in m:
        return get_time()

    if "news" in m:
        return get_news()

    if "country" in m:
        topic = clean_text(m)
        c = country_info(topic)
        if c:
            return c

    # Wikipedia fallback
    topic = clean_text(m)
    w = wiki_search(topic)
    if w:
        return w

    return "I’m not sure yet, but I’m learning more every day!"


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    reply = smart_reply(user_message)
    return jsonify({"reply": reply})


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run()
