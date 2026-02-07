def clean_question(text):
    words_to_remove = [
        "who is", "who was", "what is", "tell me about",
        "explain", "define", "country", "meaning of",
        "the", "a", "an", "in", "on", "at"
    ]
    t = text.lower()
    for w in words_to_remove:
        t = t.replace(w, "")
    return t.strip()


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
        name = clean_question(m)
        info = country_api(name)
        if info:
            return info

    # meaning
    if "meaning" in m:
        word = clean_question(m)
        meaning = dictionary_api(word)
        if meaning:
            return meaning

    # -------- STRONG WIKIPEDIA FIX --------
    topic = clean_question(m)
    result = wiki_search(topic)
    if result:
        return result

    return "I’m not sure yet, but I’m learning more every day!"
