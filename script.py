import os, json, requests, sys
from datetime import datetime

API_KEY = os.environ["YOUTUBE_API_KEY"]

VIDEO_IDS = [
    "iy9qZR_OGa0", # Haegeum
    "uVD-YgzDzyY", # People Pt.2
    "IX1dkYoLHVs", # AMYGDALA
    "qGjAWJ2zWWI", # Daechwita
    "_Zgc12yL5ss", # Give It To Me
    "3Y_Eiyg4bfk", # Agust D
    "PV1gCvzpSy0", # Interlude : Shadow
]

DATA_FILE = "data.json"


def get_stats(video_ids):
    """YouTube APIから動画の統計情報を取得"""
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"part": "statistics,snippet", "id": ",".join(video_ids), "key": API_KEY}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        results = {}
        for it in data.get("items", []):
            vid = it["id"]
            title = it["snippet"]["title"]
            views = int(it["statistics"]["viewCount"])
            results[vid] = {"title": title, "views": views}
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error getting YouTube stats: {e}", file=sys.stderr)
        sys.exit(1)


def load_history():
    """過去の履歴を読み込み"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_new_data(new_entry):
    """履歴に新しい日次データを追加"""
    history = load_history()
    history.append(new_entry)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    history = load_history()
    old = history[-1] if history else {}
    old_views_map = {v["videoId"]: v["views_total"] for v in old.get("videos", [])}

    new = get_stats(VIDEO_IDS)

    daily_stats = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "videos": []
    }

    for vid, info in new.items():
        prev_views = old_views_map.get(vid, info["views"])
        diff = info["views"] - prev_views
        daily_stats["videos"].append({
            "videoId": vid,
            "title": info["title"],
            "views_total": info["views"],
            "views_diff": diff
        })

    save_new_data(daily_stats)

