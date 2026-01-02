/* ----------------------------------------------------
   アルバム分類（必要に応じて追加・編集OK）
   ※ 曲名は JSON の title と完全一致させる
---------------------------------------------------- */
const albumMap = {
  "D-DAY": ["D‐Day", "해금", "HUH?!", "Snooze", "AMYGDALA"],
  "D-2": ["Moonlight", "Daechwita", "Burn It", "People", "Strange", "28"],
  "Agust D": ["Agust D", "give it to me", "The Last", "724148", "140503 at dawn"],
  "BE": ["Life Goes On", "Fly To My Room", "Blue & Grey", "Telepathy", "Dis-ease", "Stay"],
  "LOVE YOURSELF 轉 'Tear'": ["Fake Love", "134340", "Paradise", "Magic Shop", "So What", "Outro : Tear"]
};


/* ----------------------------------------------------
   メイン処理
---------------------------------------------------- */
async function loadData() {

  /* 今日のデータを読み込み */
  const today = await fetch("../docs/spotify_data.json").then(r => r.json());

  /* 前日のデータが無い場合（初回）は空データで代用 */
  let yesterday = { tracks: [] };
  try {
    yesterday = await fetch("../docs/spotify_data_prev.json").then(r => r.json());
  } catch (e) {
    console.log("前日のデータがありません（初回実行）");
  }

  /* 更新日時を表示（上部とフッター） */
  document.getElementById("updated").textContent =
    "更新日時：" + today.updated_at;

  document.getElementById("footer-updated").textContent =
    "最終更新：" + today.updated_at;

  /* 前日の人気度をマッピング（高速検索用） */
  const prevMap = {};
  yesterday.tracks.forEach(t => {
    prevMap[t.title] = t.spotify_popularity;
  });

  /* アルバムごとの UI を生成 */
  const albumsDiv = document.getElementById("albums");

  for (const [album, titles] of Object.entries(albumMap)) {

    /* アルバム枠 */
    const albumBox = document.createElement("div");
    albumBox.className = "album";

    /* アルバム名（タップで開閉） */
    const header = document.createElement("div");
    header.className = "album-header";
    header.textContent = album;

    /* 曲リスト（最初は閉じている） */
    const content = document.createElement("div");
    content.className = "album-content";

    /* 曲を1行ずつ追加 */
    titles.forEach(title => {
      const track = today.tracks.find(t => t.title === title);
      if (!track) return; // JSON に無い曲はスキップ

      const prev = prevMap[title];
      let diff = "";
      let diffClass = "diff-same";

      /* 前日比の計算 */
      if (prev !== undefined) {
        const d = track.spotify_popularity - prev;
        if (d > 0) { diff = `↑${d}`; diffClass = "diff-up"; }
        else if (d < 0) { diff = `↓${Math.abs(d)}`; diffClass = "diff-down"; }
        else diff = "→0";
      }

      /* 曲1行の UI */
      const row = document.createElement("div");
      row.className = "track-row";
      row.innerHTML = `
        <a href="${track.spotify_url}" target="_blank">${track.title}</a>
        <span>${track.spotify_popularity}</span>
        <span class="${diffClass}">${diff}</span>
      `;
      content.appendChild(row);
    });

    /* 開閉アニメーション */
    header.addEventListener("click", () => {
      content.style.display = content.style.display === "block" ? "none" : "block";
    });

    /* DOM に追加 */
    albumBox.appendChild(header);
    albumBox.appendChild(content);
    albumsDiv.appendChild(albumBox);
  }
}

/* 実行 */
loadData();
