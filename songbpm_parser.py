
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

SONGBPM = "https://songbpm.com"

def normalize(s):
    return re.sub(r"\s+", " ", (s or "")).strip()

def get_csrf_token(html):
    soup = BeautifulSoup(html, "html.parser")
    candidates = soup.select(
        'input[name="_csrf"], input[name="csrf"], meta[name="csrf-token"]'
    )
    for node in candidates:
        value = node.get("value") or node.get("content")
        if value:
            return value
    return None

def extract_song_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    anchors = soup.select("a.media")
    if not anchors:
        anchors = [
            a for a in soup.find_all("a", href=True)
            if re.match(r"^/@[^/]+/[^/?#]+", a["href"])
        ]

    seen = set()
    for a in anchors:
        text = normalize(a.get_text(" ", strip=True))
        href = urljoin(SONGBPM, a.get("href", ""))

        bpm_match = re.search(r"\b(\d{2,3}(?:\.\d+)?)\s*BPM\b", text, re.I)
        if not bpm_match:
            bpm_node = a.select_one(".bpm, [class*='bpm'], [data-bpm]")
            bpm_match = re.search(
                r"\b(\d{2,3}(?:\.\d+)?)\b",
                normalize(bpm_node.get_text(" ", strip=True)) if bpm_node else "",
            )
        if not bpm_match:
            continue

        bpm = float(bpm_match.group(1))
        bpm = int(bpm) if bpm.is_integer() else bpm

        key_match = re.search(
            r"\bKey\s+([A-G](?:♯|♭|#|b)?(?:\s*/\s*[A-G](?:♯|♭|#|b)?)?)",
            text,
            re.I,
        )
        key = normalize(key_match.group(1)) if key_match else None

        artist_node = a.select_one(".artist-name, [class*='artist-name']")
        title_node = a.select_one(".track-name, [class*='track-name']")
        artist = normalize(artist_node.get_text(" ", strip=True)) if artist_node else None
        title = normalize(title_node.get_text(" ", strip=True)) if title_node else None

        if not title or not artist:
            ps = [normalize(p.get_text(" ", strip=True)) for p in a.find_all("p")]
            ps = [p for p in ps if p]
            if len(ps) >= 2:
                artist = artist or ps[0]
                title = title or ps[1]

        if not title:
            clean = re.sub(
                r"\bKey\s+[A-G](?:♯|♭|#|b)?(?:\s*/\s*[A-G](?:♯|♭|#|b)?)?\b",
                "",
                text,
                flags=re.I,
            )
            clean = re.sub(r"\b\d{2,3}(?:\.\d+)?\s*BPM\b", "", clean, flags=re.I)
            clean = re.sub(r"\bDuration\s+\d+:\d+\b", "", clean, flags=re.I)
            parts = [normalize(x) for x in re.split(r"\s{2,}|\n", clean) if normalize(x)]
            if len(parts) >= 2:
                artist, title = parts[0], parts[1]

        if not title:
            continue

        item = {
            "artist": artist or "Unknown artist",
            "title": title,
            "bpm": bpm,
            "key": key,
            "url": href,
            "source": "SongBPM",
        }

        dedupe = (
            item["artist"].lower(),
            item["title"].lower(),
            item["bpm"],
            item["key"],
        )
        if dedupe not in seen:
            seen.add(dedupe)
            results.append(item)

    return results
