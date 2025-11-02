import requests
import json
import base64
import os

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

# ====== トラック情報を取得 ======
def get_artist_tracks(artist_name, token):
    print(f"🔍 {artist_name} の曲を検索中...")
    url = "https://api.spotify.com/v1/search"
    params = {"q": artist_name, "type": "artist", "limit": 1}
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    artist = res.json()["artists"]["items"][0]
    artist_id = artist["id"]

    # アルバム一覧
    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    albums_params = {"include_groups": "album,single", "limit": 50}
    albums_res = requests.get(albums_url, headers=headers, params=albums_params)
    albums_res.raise_for_status()
    albums = albums_res.json()["items"]

    seen = set()
    tracks = []
    for album in albums:
        if album["id"] in seen:
            continue
        seen.add(album["id"])
        album_tracks_url = f"https://api.spotify.com/v1/albums/{album['id']}/tracks"
        album_tracks_res = requests.get(album_tracks_url, headers=headers)
        album_tracks_res.raise_for_status()
        for t in album_tracks_res.json()["items"]:
            tracks.append({
                "artist": artist_name,
                "album": album["name"],
                "track_name": t["name"],
                "id": t["id"]
            })
    return tracks

# ====== 人気度（popularity）を取得 ======
def add_popularity(tracks, token):
    headers = {"Authorization": f"Bearer {token}"}
    for t in tracks:
        track_url = f"https://api.spotify.com/v1/tracks/{t['id']}"
        res = requests.get(track_url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            t["popularity"] = data.get("popularity", None)
        else:
            t["popularity"] = None
    return tracks

# ====== 実行部分 ======
if __name__ == "__main__":
    token = get_token()
    all_tracks = []
    for name in ["SUGA", "Agust D"]:
        tracks = get_artist_tracks(name, token)
        all_tracks.extend(tracks)

    all_tracks = add_popularity(all_tracks, token)

    os.makedirs("spotify", exist_ok=True)
    with open("spotify/spotify_data.json", "w", encoding="utf-8") as f:
        json.dump(all_tracks, f, ensure_ascii=False, indent=2)

    print("💾 spotify/spotify_data.json に保存しました！")
