import requests
import json
import base64
import os
import time
from datetime import datetime

# ====== Spotify API 認証情報 ======
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

print("🔍 CLIENT_ID:", "✅ 読み込み成功" if CLIENT_ID else "❌ None")
print("🔍 CLIENT_SECRET:", "✅ 読み込み成功" if CLIENT_SECRET else "❌ None")

# ====== アクセストークンを取得 ======
def get_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    token = response.json()["access_token"]
    print("✅ Access Token 取得成功")
    return token

# ====== 安全なリクエスト関数（リトライ付き） ======
def safe_request(method, url, headers=None, params=None, retries=3):
    for i in range(retries):
        res = requests.request(method, url, headers=headers, params=params)
        if res.status_code == 200:
            return res
        elif res.status_code == 429:
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
        albums_url = data.get("next")

    seen = set()
    tracks = []
    for album in albums:
        if album["id"] in seen:
            continue
        seen.add(album["id"])

        album_tracks_url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks"
        album_tracks_res = safe_request("GET", album_tracks_url, headers=headers)
        album_tracks_data = album_tracks_res.json()

        # ジャケット画像を取得
        album_image = album["images"][0]["url"] if album["images"] else None

        for t in album_tracks_data["items"]:
            tracks.append({
                "artist": artist_name,
                "album": album["name"],
                "album_image": album_image,
                "track_name": t["name"],
                "id": t["id"],
                "spotify_url": f"https://open.spotify.com/track/{t['id']}"
            })

    print(f"✅ {len(tracks)} 曲取得完了 ({artist_name})")
    return tracks

# ====== 人気度情報など追加 ======
def add_popularity(tracks, token):
    print("\n⭐ 人気度データを取得中...")
    headers = {"Authorization": f"Bearer {token}"}
    updated_tracks = []
    for i in range(0, len(tracks), 50):
        batch = tracks[i:i+50]
        ids = ",".join(t["id"] for t in batch)
        url = "https://api.spotify.com/v1/tracks"
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

    artist_ids = {
        "SUGA": "0ebNdVaOfp6N0oZ1guIxM8",
        "Agust D": "5RmQ8k4l3HZ8JoPb4mNsML"
    }

    all_tracks = []
    for name, artist_id in artist_ids.items():
        all_tracks.extend(get_artist_tracks(name, artist_id, token))

    all_tracks = add_popularity(all_tracks, token)

    filename = "spotify_data.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_tracks, f, ensure_ascii=False, indent=2)

    print(f"\n💾 保存完了: {filename}")
    print(f"🎉 取得総数: {len(all_tracks)} 曲")
