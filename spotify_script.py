import requests
import json
import os
from datetime import datetime
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# ============================================
# 0. Spotify 認証
# ============================================
sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

# ============================================
# 1. Spotify：アーティストID
# ============================================
ARTISTS = {
    "Agust D": "0b1sIQumIAsNbqAoIClSpy",
    "SUGA": "0TnOYISbd1XYRBk9myaseg",
    "BTS": "3Nrfpe0tUJi4K4DXYWgMUX"
}

# ============================================
# 2. コラボ曲（手動 track_id）
# ============================================
COLLAB_TRACK_IDS = [
    "7GNRUsU3M4XNDDB9xle5Dz",  # That That
    "21hbZ0yllYOoXEbiFDYMSI",  # eight
    "0pYacDCZuRhcrwGUA5nTBe",  # 에잇
    "5dn6QANKbf76pANGjMBida",  # Blueberry Eyes
    "09YHm6IkdZko28KdEbXtPb",  # Girl of My Dreams
    "3l6LBCOL9nPsSY29TUY2VE",  # Lilith
]

# ============================================
# 3. Spotify：アーティストの全曲を取得
# ============================================
def get_tracks_from_artist(artist_id, artist_name):
    tracks = []
    albums = sp.artist_albums(artist_id, album_type="album,single,compilation", limit=50)

    album_ids = list({a["id"] for a in albums["items"]})

    for album_id in album_ids:
        album_tracks = sp.album_tracks(album_id)
        for t in album_tracks["items"]:
            # メインアーティストが一致する曲だけ採用
            if t["artists"][0]["name"] != artist_name:
                continue

            isrc = t.get("external_ids", {}).get("isrc")

            tracks.append({
                "title": t["name"],
                "track_id": t["id"],
                "isrc": isrc,
                "artist": ", ".join([a["name"] for a in t["artists"]])
            })

    return tracks

# ============================================
# 4. VocaDB：ユンギ作詞作曲曲を取得
# ============================================
def get_yoongi_written_tracks():
    url = "https://vocadb.net/api/songs"
    params = {
        "artistId": 23607,  # Min Yoongi
        "artistParticipation": "Composer,Arranger,Lyricist",
        "fields": "Names,Artists,PVServices,SongType,WebLinks",
        "maxResults": 500
    }

    data = requests.get(url, params=params).json()

    isrc_list = []
    for song in data.get("items", []):
        for link in song.get("webLinks", []):
            if link["description"] == "ISRC":
                isrc_list.append(link["url"])

    return set(isrc_list)

# ============================================
# 5. BTS の全曲からユンギ作詞作曲曲だけを抽出
# ============================================
def filter_bts_tracks_by_yoongi(bts_tracks, yoongi_isrcs):
    filtered = []
    for t in bts_tracks:
        if t["isrc"] in yoongi_isrcs:
            filtered.append(t)
    return filtered

# ============================================
# 6. popularity を track_id で取得
# ============================================
def enrich_with_popularity(track):
    info = sp.track(track["track_id"])
    track["popularity"] = info["popularity"]
    track["spotify_url"] = info["external_urls"]["spotify"]
    return track

# ============================================
# 7. メイン処理
# ============================================
def main():
    all_tracks = []

    # Agust D / SUGA / BTS の全曲を取得
   agustd_tracks = get_tracks_from_artist(ARTISTS["Agust D"], "Agust D")
   suga_tracks   = get_tracks_from_artist(ARTISTS["SUGA"], "SUGA")
   bts_tracks    = get_tracks_from_artist(ARTISTS["BTS"], "BTS")

    # VocaDB からユンギ作詞作曲曲の ISRC を取得
    yoongi_isrcs = get_yoongi_written_tracks()

    # BTS 曲の中からユンギ作詞作曲曲だけ抽出
    bts_yoongi_tracks = filter_bts_tracks_by_yoongi(bts_tracks, yoongi_isrcs)

    # コラボ曲（手動 track_id）
    collab_tracks = []
    for tid in COLLAB_TRACK_IDS:
        info = sp.track(tid)
        collab_tracks.append({
            "title": info["name"],
            "track_id": tid,
            "artist": ", ".join([a["name"] for a in info["artists"]]),
            "isrc": info["external_ids"].get("isrc")
        })

    # すべて統合
    combined = agustd_tracks + suga_tracks + bts_yoongi_tracks + collab_tracks

    # popularity を付与
    final = [enrich_with_popularity(t) for t in combined]

    # JSON 保存
    output = {
        "updated_at": datetime.now().isoformat(),
        "tracks": final
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/spotify_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("spotify_data.json を更新しました！")

if __name__ == "__main__":
    main()
