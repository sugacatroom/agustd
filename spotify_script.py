import requests, json, os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

# ==============================
# 1. MusicBrainzからアーティスト情報を取得
# ==============================

# 複数名義（SUGAの別名義も含める）
artist_names = ["SUGA", "Agust D", "Gloss", "Min Yoon-gi"]

artist_ids = []
for name in artist_names:
    # MusicBrainz APIでアーティスト検索
    url = f"https://musicbrainz.org/ws/2/artist?query=artist:{name}&fmt=json"
    data = requests.get(url).json()
    if data.get("artists"):
        # 最初の一致結果のIDを保存
        artist_ids.append(data["artists"][0]["id"])

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
