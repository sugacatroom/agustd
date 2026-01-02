import requests, json, os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# 複数名義
artist_names = ["SUGA", "Agust D", "Gloss", "Min Yoon-gi"]

artist_ids = []
for name in artist_names:
    url = f"https://musicbrainz.org/ws/2/artist?query=artist:{name}&fmt=json"
    data = requests.get(url).json()
    if data.get("artists"):
        artist_ids.append(data["artists"][0]["id"])

# 楽曲一覧取得
recordings = []
for artist_id in artist_ids:
    url = f"https://musicbrainz.org/ws/2/recording?artist={artist_id}&fmt=json&limit=100"
    data = requests.get(url).json()
    for rec in data.get("recordings", []):
        recordings.append(rec["title"])

# Spotify認証
sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id = os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
))

results = []
for title in recordings:
    search = sp.search(q=title, type="track", limit=1)
    if search["tracks"]["items"]:
        track = search["tracks"]["items"][0]
        results.append({
            "title": title,
            "spotify_popularity": track["popularity"],
            "spotify_url": track["external_urls"]["spotify"]
        })

# JSON保存（docs配下）
os.makedirs("docs", exist_ok=True)
with open("docs/spotify_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
