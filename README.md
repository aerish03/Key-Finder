
# SongBPM Quick Finder

A small web app whose backend performs a normal SongBPM search and extracts the
BPM and key from SongBPM's result page.

## Why this architecture

SongBPM does not expose a simple public browser API for this workflow. Its
search flow creates a server-side `/searches/<uuid>` page. The backend therefore
keeps the search request server-side: it first loads SongBPM to obtain the
session/CSRF token, then submits the search form to `/searches`, follows the
redirect, and parses the resulting song cards.

This avoids relying on a guessed `?q=` browser URL.

## Run locally

Python 3.10+ recommended.

    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # macOS/Linux:
    source .venv/bin/activate

    pip install -r requirements.txt
    python app.py

Open http://127.0.0.1:5000

## Production

Use:

    gunicorn app:app

Set PORT if your hosting provider requires it.

## Notes

- Results are source-of-truth values read from SongBPM.
- If a search returns multiple recordings, the app shows several matches so you
  can choose the exact recording.
- A short in-memory cache reduces repeated requests.
- The parser has a primary selector plus a fallback selector because website
  markup can change.
- This project does not invent BPM/key values when SongBPM does not list them.
- Respect SongBPM's terms, robots rules, and rate limits. If SongBPM changes its
  search flow or blocks automated requests, the parser may need updating.
