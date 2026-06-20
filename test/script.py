import os, json, requests, sys
from datetime import datetime, timedelta, timezone

# 環境変数からAPIキーを取得（GitHub Actionsのsecretsで設定）
API_KEY = os.environ["YOUTUBE_API_KEY"]

# 対象の動画ID一覧（Agust DとBTS関連）
VIDEO_IDS = [
    "iy9qZR_OGa0",  # Haegeum
    "uVD-YgzDzyY",  # People Pt.2
    "IX1dkYoLHVs",  # AMYGDALA
    "qGjAWJ2zWWI",  # Daechwita
    "_Zgc12yL5ss",  # Give It To Me
    "3Y_Eiyg4bfk",  # Agust D
    "PV1gCvzpSy0",  # Interlude : Shadow
]

# データ保存先ファイル
DATA_FILE = "data.json"

# 日本時間（JST）を定義
JST = timezone(timedelta(hours=9))

# YouTube APIから再生数とタイトルを取得する関数
def get_stats(video_ids):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
        "key": API_KEY
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        results = {}
        for item in data.get("items", []):
            vid = item["id"]
            title = item["snippet"]["title"]
            views = int(item["statistics"]["viewCount"])
            results[vid] = {"title": title, "views": views}
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error getting YouTube stats: {e}", file=sys.stderr)
        sys.exit(1)

# 過去の履歴データを読み込む関数
def load_history():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# 新しいデータを保存する関数（同じ日付なら上書き）
def save_new_data(new_entry):
    history = load_history()

    # 今日のデータがすでにある場合は上書き、なければ追加
    if history and history[-1]["date"] == new_entry["date"]:
        history[-1] = new_entry
    else:
        history.append(new_entry)

    # 最新7件だけ保持（古いデータは削除）
    history = history[-7:]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

# メイン処理
if __name__ == "__main__":
    history = load_history()

    # JSTで今日と昨日の日付を取得
    today = datetime.now(JST).strftime("%Y-%m-%d")
    yesterday = (datetime.now(JST) - timedelta(days=1)).strftime("%Y-%m-%d")

    # 昨日のデータを探す（なければ空）
    prev_entry = next((d for d in reversed(history) if d["date"] == yesterday), {})
    old_views_map = {v["videoId"]: v["views_total"] for v in prev_entry.get("videos", [])}

    # 最新の再生数を取得
    new = get_stats(VIDEO_IDS)

    # 今日のデータを構築
    daily_stats = {
        "date": today,
        "videos": []
    }

    # 各動画について、前日との差分を計算
    for vid, info in new.items():
        prev_views = old_views_map.get(vid, info["views"])  # 前日がなければ差分0
        diff = info["views"] - prev_views
        daily_stats["videos"].append({
            "videoId": vid,
            "title": info["title"],
            "views_total": info["views"],
            "views_diff": diff
        })

    # 保存
    save_new_data(daily_stats)
