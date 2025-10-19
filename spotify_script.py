import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import os

# GitHub Secretsから環境変数として読み込む
client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# Agust DのSpotifyアーティストID
artist_ids = ['2auC28zjQyVTsiZKNgPRGs', '0C0XlULifJtAgn6ZNCW2eu']  # Agust D と SUGA

# アルバム一覧を取得
all_tracks = []

for artist_id in artist_ids:
    albums = sp.artist_albums(artist_id, album_type='album,single', limit=50)
    album_ids = [album['id'] for album in albums['items']]

    for album_id in album_ids:
        tracks = sp.album_tracks(album_id)
        for track in tracks['items']:
            track_info = sp.track(track['id'])
            all_tracks.append({
                'name': track['name'],
                'popularity': track_info['popularity'],
                'album': track_info['album']['name'],
                'release_date': track_info['album']['release_date']
            })


# トラック情報を取得
all_tracks = []
for album_id in album_ids:
    tracks = sp.album_tracks(album_id)
    for track in tracks['items']:
        track_info = sp.track(track['id'])
        all_tracks.append({
            'name': track['name'],
            'popularity': track_info['popularity'],
            'album': track_info['album']['name'],
            'release_date': track_info['album']['release_date']
        })

# JSONファイルに保存
with open('spotify_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_tracks, f, ensure_ascii=False, indent=2)

print("Spotifyデータの取得と保存が完了しました！")
