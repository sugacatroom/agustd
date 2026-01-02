import requests
import json
import os
import time
from datetime import datetime
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# ==============================
# 0. 共通：安全な GET（リトライ付き）
# ==============================
def safe_get(url, headers=None, retries=3, delay=2):
    """
    APIアクセス時にエラーが出たら自動でリトライする関数
    retries: 最大リトライ回数
    delay: リトライ間隔（秒）
    """
    for i in range(retries):
        try:
            return requests.get(url, headers=headers).json()
        except requests.exceptions.RequestException as e:
            print(f"[Retry {i+1}/{retries}] Error: {e}")
            time.sleep(delay)
    return {}  # 全部失敗したら空のデータを返す


# ==============================
# 1. MusicBrainzから楽曲一覧を取得
# ==============================

# ユンギ本人の MusicBrainz アーティストIDを固定
artist_ids = [
    "b629da42-c668-49d2-be67-498605ee2a13",  # SUGA
    "31dd895e-4473-4458-baed-8bcf36d3de7f",  # Agust D
    "f09d2950-e3c6-47b2-b21c-2bad2cd3f616"   # Min Yoon-gi
]

# MusicBrainz 推奨の User-Agent
headers = {
    "User-Agent": "agustd-stats/1.0 ( https://github.com/sugacatroom/agustd )"
}

recordings = []

for artist_id in artist_ids:
    url = f"https://musicbrainz.org/ws/2/recording?artist={artist_id}&fmt=json&limit=100"
    data = safe_get(url, headers=headers)  # ← リトライ付き GET
    for rec in data.get("recordings", []):
        recordings.append(rec["title"])

# 重複削除
recordings = list(set(recordings))

# ============================== 
# 追加：ユンギ作詞作曲の BTS 曲を統合 
# ==============================
extra_tracks = [
    # 花様年華
    "Intro : The Most Beautiful Moment in Life",
    "Intro : Never Mind",
    "Butterfly",
    "Whalien 52",
    "Ma City",
    "Boyz with Fun",
    "Dead Leaves",
    "House of Cards",
    "Love Is Not Over",
    "I Need U",
    "Run",

    # WINGS / YNWA
    "First Love",
    "Blood Sweat & Tears",
    "2! 3!",
    "Spring Day",
    "Not Today",

    # LOVE YOURSELF 承 'Her'
    "Intro : Serendipity",
    "Best Of Me",
    "Pied Piper",
    "MIC Drop",
    "Go Go",
    "Outro : Her",

    # LOVE YOURSELF 轉 'Tear'
    "Fake Love",
    "The Truth Untold",
    "134340",
    "Paradise",
    "Love Maze",
    "Magic Shop",
    "Airplane pt.2",
    "Anpanman",
    "So What",
    "Outro : Tear",

    # LOVE YOURSELF 結 'Answer'
    "Trivia 轉 : Seesaw",
    "I'm Fine",
    "IDOL",
    "Answer : Love Myself",

    # PERSONA
    "Intro : Persona",
    "Boy With Luv",
    "Make It Right",
    "Home",
    "Dionysus",

    # MAP OF THE SOUL : 7
    "Interlude : Shadow",
    "Black Swan",
    "Filter",
    "My Time",
    "Louder than bombs",
    "UGH!",
    "Respect",
    "We are Bulletproof : the Eternal",

    # BE
    "Life Goes On",
    "Fly To My Room",
    "Blue & Grey",
    "Telepathy",
    "Dis-ease",
    "Stay"
]

# MusicBrainz の曲 + BTS 作詞作曲曲を統合
all_titles = list(set(recordings + extra_tracks))

# ==============================
# 2. Spotify APIで楽曲情報を取得
# ==============================

# Spotify認証（Secretsから環境変数を取得）
sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

def safe_spotify_search(query, retries=3, delay=2):
    """
    Spotify検索もリトライ対応
    """
    for i in range(retries):
        try:
            return sp.search(q=query, type="track", limit=1)
        except Exception as e:
            print(f"[Spotify Retry {i+1}/{retries}] Error: {e}")
            time.sleep(delay)
    return {"tracks": {"items": []}}

results = []

for title in all_titles:
    search = safe_spotify_search(f'track:"{title}"')
    items = search["tracks"]["items"]

    if items:
        track = items[0]
        results.append({
            "title": title,
            "spotify_popularity": track["popularity"],
            "spotify_url": track["external_urls"]["spotify"]
        })

# ==============================
# 3. JSONファイルに保存（更新日時付き）
# ==============================

output = {
    "updated_at": datetime.now().isoformat(),
    "tracks": results
}

os.makedirs("docs", exist_ok=True)
with open("docs/spotify_data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# 日付ごとの履歴保存
date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
history_path = f"docs/history/{date_str}.json"

os.makedirs("docs/history", exist_ok=True)
with open(history_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
