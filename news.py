import os
import requests
import pyttsx3

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 170)


def speak(text):
    try:
        engine.say(str(text))
        engine.runAndWait()
    except Exception as e:
        print("TTS error:", e)


def latestnews(category: str | None = None, max_articles: int = 5):
    """Fetch and speak latest news.

    Args:
        category: optional search term; if None returns top headlines (country=us).
        max_articles: maximum number of articles to read aloud.
    """
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        speak("News API key not set. Please set NEWSAPI_KEY environment variable.")
        print("Set NEWSAPI_KEY environment variable with your NewsAPI.org key.")
        return

    if category:
        url = f"https://newsapi.org/v2/everything?q={requests.utils.quote(category)}&sortBy=publishedAt&apiKey={api_key}"
    else:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"

    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        speak(f"Failed to contact news service: {e}")
        print("Request error:", e)
        return

    if resp.status_code != 200:
        speak(f"News service returned status {resp.status_code}")
        print("Response status:", resp.status_code, resp.text[:800])
        return

    try:
        news = resp.json()
    except Exception as e:
        speak("Received unexpected response from the news service.")
        print("Response parsing error:", e)
        print("Response text:", resp.text[:800])
        return

    if news.get("status") != "ok":
        speak("News API error")
        print("News API error response:", news)
        return

    articles = news.get("articles", [])
    if not articles:
        speak("No articles found right now.")
        return

    speak("Here are the top headlines.")
    count = 0
    for article in articles:
        if count >= max_articles:
            break
        title = article.get("title", "No title")
        print(f"- {title}")
        speak(title)
        url = article.get("url")
        if url:
            print("  Read more:", url)

        # allow user to stop or continue
        try:
            a = input("[1] next, [2] stop: ")
        except Exception:
            a = "1"

        if str(a).strip() == "2":
            break
        count += 1

    speak("That's all for now.")