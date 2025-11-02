import requests
import json
import base64
import os
import time
from datetime import datetime

# ====== Spotify API 認証情報 ======
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# ====== アクセストークンを取得 ======
def get_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# ====== 安全なリクエスト関数（リトライ付き） ======
def safe_request(method, url, headers=None, params=None, retries=3):
    for i in range(retries):
        res = requests.request(method, url, headers=headers, params=params)
        if res.status_code == 200:
            return res
        elif res.status_code == 429:  # Rate Limit対応
            wait = int(res.headers.get("Retry-After", 5))
            print(f"⚠️ Rate limit発生中。{wait}秒待機します...")
            time.sleep(wait)
        else:
            print(f"⚠️ エラー発生 ({res.status_code}): {res.text}")
            time.sleep(2)
    res.raise_for_status()
    return res

# ====== アーティストのアルバム＆トラックを取得 ======
def get_artist_tracks(artist_name, artist_id, token):
    print(f"\n🎵 {artist_name} の曲を取得中...")
    headers = {"Authorization": f"Bearer {token}"}
    albums = []
    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {"include_groups": "album,single", "limit": 50}

    # --- ページング対応 ---
    while albums_url:
        res = safe_request("GET", albums_url, headers=headers, params=params)
        data = res.json()
        albums.extend(data["items"])
        albums_url = data.get("next")  # 次ページがある場合は続行

    # --- トラック取得 ---
    seen = set()
    tracks = []
    for album in albums:
        if album["id"] in seen:
            continue
        seen.add(album["id"])

        album_tracks_url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks"
        album_tracks_res = safe_request("GET", album_tracks_url, headers=headers)
        for t in album_tracks_res.json()["items"]:
            tracks.append({
                "artist": artist_name,
                "album": album["name"],
                "track_name": t["name"],
                "id": t["id"]
            })

    print(f"✅ {len(tracks)} 曲取得完了 ({artist_name})")
    return tracks

# ====== 人気度（popularity）をまとめて取得 ======
def add_popularity(tracks, token):
    print("\n⭐ 人気度データを取得中...")
    headers = {"Authorization": f"Bearer {token}"}
    updated_tracks = []
    for i in range(0, len(tracks), 50):
        batch = tracks[i:i+50]
        ids = ",".join(t["id"] for t in batch)
        url = f"https://api.spotify.com/v1/tracks"
        res = safe_request("GET", url, headers=headers, params={"ids": ids})
        items = res.json().get("tracks", [])
        for t, info in zip(batch, items):
            t["popularity"] = info.get("popularity", None)
            t["duration_ms"] = info.get("duration_ms", None)
            t["preview_url"] = info.get("preview_url", None)
            updated_tracks.append(t)
    print("✅ 人気度情報を追加しました！")
    return updated_tracks

# ====== 実行部分 ======
if __name__ == "__main__":
    token = get_token()

    # 🎧 Spotify公式アーティストID
    artist_ids = {
        "SUGA": "6HaGTQPmzraVmaVxvz6EUc",
        "Agust D": "2auC28zjQyVTsiZKNgPRGs"
    }

    all_tracks = []
    for name, artist_id in artist_ids.items():
        tracks = get_artist_tracks(name, artist_id, token)
        all_tracks.extend(tracks)

    # 人気度データを追加
    all_tracks = add_popularity(all_tracks, token)

    # 💾 保存処理（日付付きファイル名）
    os.makedirs("spotify", exist_ok=True)
    filename = f"spotify/spotify_data_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_tracks, f, ensure_ascii=False, indent=2)

    print(f"\n💾 保存完了: {filename}")
    print(f"🎉 取得総数: {len(all_tracks)} 曲")
