from flask import Flask, render_template, request, jsonify
import requests
import datetime
import random

app = Flask(__name__)

# ---------------- CREATOR MEMORY ----------------
creator_info = {
    "name": "Charles Kanyama",
    "color": "black",
    "games": "Minecraft and eFootball",
    "sport": "soccer",
    "team": "Chelsea"
}

greetings = ["hi", "hello", "hey"]
farewells = ["bye", "goodbye"]

# ---------------- APIs ----------------

def wiki_search(query):
    try:
        # Search correct page title first
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }
        search = requests.get(search_url, params=params).json()
        title = search["query"]["search"][0]["title"]

        # Get summary
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        summary = requests.get(summary_url).json()
        return summary.get("extract")
    except:
        return None


def country_api(name):
    try:
        r = requests.get(f"https://restcountries.com/v3.1/name/{name}").json()
        c = r[0]
        return (
            f"Country: {c['name']['common']}\n"
            f"Capital: {c['capital'][0]}\n"
            f"Population: {c['population']}\n"
            f"Region: {c['region']}"
        )
    except:
        return None


def joke_api():
    try:
        r = requests.get("https://official-joke-api.appspot.com/random_joke").json()
        return f"{r['setup']} — {r['punchline']}"
    except:
        return "Why don’t programmers like nature? Too many bugs."


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
        return f"Current time: {r['datetime']}"
    except:
        return str(datetime.datetime.now())


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

# ---------------- SMART REPLY ----------------

def smart_reply(msg):
    m = msg.lower()

    # greetings
    if any(g in m for g in greetings):
        return "Hello! How can I help you today?"

    if any(f in m for f in farewells):
        return "Goodbye! Have a great day."

    # creator questions
    if "who created" in m or "creator" in m:
        return f"I was created by {creator_info['name']}."

    if "favorite color" in m:
        return f"My creator's favorite color is {creator_info['color']}."

    if "favorite game" in m:
        return f"{creator_info['name']} enjoys {creator_info['games']}."

    if "team" in m or "club" in m:
        return f"The favorite team is {creator_info['team']}."

    # joke
    if "joke" in m:
        return joke_api()

    # advice
    if "advice" in m:
        return advice_api()

    # quote
    if "quote" in m or "motivate" in m:
        return quote_api()

    # time/date
    if "time" in m or "date" in m:
        return time_api()

    # news
    if "news" in m:
        return news_api()

    # country
    if "country" in m:
        name = m.split()[-1]
        info = country_api(name)
        if info:
            return info

    # meaning
    if "meaning" in m:
        word = m.split()[-1]
        meaning = dictionary_api(word)
        if meaning:
            return meaning

    # wikipedia fallback for anything else
    result = wiki_search(msg)
    if result:
        return result

    return "I’m not sure yet, but I’m learning more every day!"

# ---------------- ROUTES ----------------

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
