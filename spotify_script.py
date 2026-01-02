import requests, json, os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

# ==============================
# 1. MusicBrainzからアーティスト情報を取得
# ==============================
# MusicBrainz のアーティストIDを固定（ユンギ本人のみ）
artist_ids = [
    "b629da42-c668-49d2-be67-498605ee2a13",  # SUGA
    "31dd895e-4473-4458-baed-8bcf36d3de7f",  # Agust D
    "f09d2950-e3c6-47b2-b21c-2bad2cd3f616"   # Min Yoon-gi
]

# ==============================
# 2. アーティストごとの楽曲一覧を取得
# ==============================

recordings = []
for artist_id in artist_ids:
    # 各アーティストの録音情報を取得（最大100件）
    url = f"https://musicbrainz.org/ws/2/recording?artist={artist_id}&fmt=json&limit=100"
    data = requests.get(url).json()
    for rec in data.get("recordings", []):
        recordings.append(rec["title"])

# 重複曲を削除
recordings = list(set(recordings))

# ==============================
# 3. Spotify APIで楽曲情報を検索
# ==============================

# Spotify認証（Secretsから環境変数を取得）
sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

results = []
for title in recordings:
    try:
        # 曲名＋アーティスト名で検索すると精度が高い
        search = sp.search(q=f"{title} artist:SUGA", type="track", limit=1)
        if search["tracks"]["items"]:
            track = search["tracks"]["items"][0]
            results.append({
                "title": title,
                "spotify_popularity": track["popularity"],  # 人気度（0〜100）
                "spotify_url": track["external_urls"]["spotify"]  # Spotifyリンク
            })
    except Exception as e:
        print(f"Error searching {title}: {e}")

# ==============================
# 4. JSONファイルに保存（更新日時付き）
# ==============================

# 出力データに更新日時を追加
output = {
    "updated_at": datetime.now().isoformat(),  # ISO形式の日時
    "tracks": results
}

# docsフォルダに保存（GitHub Pagesで公開可能）
os.makedirs("docs", exist_ok=True)
with open("docs/spotify_data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
