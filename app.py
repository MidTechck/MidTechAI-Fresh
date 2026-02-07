from flask import Flask, render_template, request, jsonify
import requests
import datetime
import random

app = Flask(__name__)

# -------- OFFLINE MEMORY --------
creator_info = {
    "name": "Charles Kanyama",
    "color": "black",
    "games": "Minecraft and eFootball",
    "sport": "soccer",
    "team": "Chelsea"
}

jokes_offline = [
    "Why don’t programmers like nature? Too many bugs.",
    "Why was the math book sad? It had too many problems.",
    "I told my computer I needed a break… it froze."
]

greetings = ["hello", "hi", "hey"]
farewells = ["bye", "goodbye"]

# -------- API FUNCTIONS --------
def wiki_search(query):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        r = requests.get(url).json()
        return r.get("extract")
    except:
        return None

def joke_api():
    try:
        r = requests.get("https://official-joke-api.appspot.com/random_joke").json()
        return f"{r['setup']} — {r['punchline']}"
    except:
        return random.choice(jokes_offline)

def advice_api():
    try:
        r = requests.get("https://api.adviceslip.com/advice").json()
        return r["slip"]["advice"]
    except:
        return "Always take care of yourself."

def quote_api():
    try:
        r = requests.get("https://api.quotable.io/random").json()
        return f"“{r['content']}” — {r['author']}"
    except:
        return "Keep pushing forward."

def time_api():
    try:
        r = requests.get("http://worldtimeapi.org/api/timezone/Africa/Lusaka").json()
        return r["datetime"]
    except:
        return str(datetime.datetime.now())

def country_api(name):
    try:
        r = requests.get(f"https://restcountries.com/v3.1/name/{name}").json()[0]
        return f"{r['name']['common']} — Capital: {r['capital'][0]}, Population: {r['population']}"
    except:
        return None

def news_api():
    try:
        url = "https://api.rss2json.com/v1/api.json?rss_url=http://feeds.bbci.co.uk/news/rss.xml"
        r = requests.get(url).json()
        articles = r["items"][:3]
        return "\n".join([a["title"] for a in articles])
    except:
        return "No news available."

def dictionary_api(word):
    try:
        r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}").json()
        meaning = r[0]["meanings"][0]["definitions"][0]["definition"]
        return meaning
    except:
        return None

# -------- CHAT LOGIC --------
def smart_reply(msg):
    m = msg.lower()

    # greetings
    if any(g in m for g in greetings):
        return "Hello! How can I help you today?"

    if any(f in m for f in farewells):
        return "Goodbye! Have a great day."

    # creator
    if "who created" in m or "creator" in m:
        return f"I was created by {creator_info['name']}."

    if "favorite color" in m:
        return f"My creator loves {creator_info['color']} color."

    # jokes
    if "joke" in m:
        return joke_api()

    # advice
    if "advice" in m:
        return advice_api()

    # quotes
    if "quote" in m:
        return quote_api()

    # time
    if "time" in m or "date" in m:
        return time_api()

    # news
    if "news" in m:
        return news_api()

    # country
    if "country" in m:
        word = m.split()[-1]
        info = country_api(word)
        if info:
            return info

    # dictionary
    if "meaning" in m:
        word = m.split()[-1]
        meaning = dictionary_api(word)
        if meaning:
            return meaning

    # wikipedia fallback
    result = wiki_search(msg.replace(" ", "_"))
    if result:
        return result

    return "I’m not sure yet, but I’m learning more every day!"

# -------- ROUTES --------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json["message"]
    reply = smart_reply(user_msg)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run()
