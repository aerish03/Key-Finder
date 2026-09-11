
from songbpm_parser import extract_song_cards, get_csrf_token

def test_current_style():
    html = """
    <a class="media" href="/@the-local-train/aaoge-tum-kabhi">
      <p class="artist-name">The Local Train</p>
      <p class="track-name">Aaoge Tum Kabhi</p>
      <p>Key C</p><p>Duration 5:13</p><p>98 BPM</p>
    </a>
    """
    r = extract_song_cards(html)
    assert r == [{
        "artist": "The Local Train",
        "title": "Aaoge Tum Kabhi",
        "bpm": 98,
        "key": "C",
        "url": "https://songbpm.com/@the-local-train/aaoge-tum-kabhi",
        "source": "SongBPM",
    }]

def test_fallback_anchor():
    html = """
    <a href="/@the-local-train/choo-lo">
      <p>The Local Train</p><p>Choo Lo</p>
      <span>Key E</span><span>Duration 3:54</span><span>146 BPM</span>
    </a>
    """
    r = extract_song_cards(html)
    assert r[0]["title"] == "Choo Lo"
    assert r[0]["artist"] == "The Local Train"
    assert r[0]["bpm"] == 146
    assert r[0]["key"] == "E"

def test_duplicate_removal():
    html = """
    <a class="media" href="/@x/a"><p class="artist-name">X</p><p class="track-name">A</p><p>Key C</p><p>100 BPM</p></a>
    <a class="media" href="/@x/a"><p class="artist-name">X</p><p class="track-name">A</p><p>Key C</p><p>100 BPM</p></a>
    """
    assert len(extract_song_cards(html)) == 1

def test_csrf():
    html = '<input type="hidden" name="_csrf" value="abc123">'
    assert get_csrf_token(html) == "abc123"
