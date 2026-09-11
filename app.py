
import os
import re
import time
from urllib.parse import quote

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

SONGBPM = "https://songbpm.com"
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "900"))
_cache = {}

session = requests.Session()
session.headers.update({
    "User-Agent": os.getenv(
        "SONGBPM_USER_AGENT",
        "Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0 Mobile Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
})

from songbpm_parser import get_csrf_token, extract_song_cards

def score_result(item, query):
    q = normalize(query).lower()
    title = item["title"].lower()
    artist = item["artist"].lower()
    score = 0
    if title == q:
        score += 100
    if q in title:
        score += 60
    if title in q:
        score += 35
    if q in artist:
        score += 15
    # Exact phrase matching should dominate.
    return score

def song_search(query):
    query = normalize(query)
    if not query:
        raise ValueError("Enter a song name.")

    key = query.casefold()
    cached = cache_get(key)
    if cached is not None:
        return cached

    # SongBPM creates a server-side /searches/<uuid> page after its search form
    # is submitted. We reproduce the normal browser flow: GET homepage for the
    # session/CSRF token, then POST the search form.
    home = session.get(SONGBPM + "/", timeout=20)
    home.raise_for_status()

    csrf = get_csrf_token(home.text)
    payload = {"q": query}
    if csrf:
        payload["_csrf"] = csrf

    response = session.post(
        SONGBPM + "/searches",
        data=payload,
        allow_redirects=True,
        timeout=20,
        headers={"Referer": SONGBPM + "/"},
    )
    response.raise_for_status()

    results = extract_song_cards(response.text)

    # A direct GET fallback helps if the site changes the search endpoint.
    if not results:
        direct = session.get(
            SONGBPM + "/?q=" + quote(query),
            allow_redirects=True,
            timeout=20,
            headers={"Referer": SONGBPM + "/"},
        )
        direct.raise_for_status()
        results = extract_song_cards(direct.text)

    results.sort(key=lambda x: score_result(x, query), reverse=True)
    results = results[:10]

    data = {
        "query": query,
        "results": results,
        "source": "SongBPM",
        "source_url": response.url,
    }
    cache_put(key, data)
    return data

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/search")
def api_search():
    query = request.args.get("q", "")
    try:
        return jsonify(song_search(query))
    except requests.RequestException as exc:
        return jsonify({
            "error": "SongBPM could not be reached right now.",
            "detail": str(exc),
        }), 502
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "SongBPM Quick Finder"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
