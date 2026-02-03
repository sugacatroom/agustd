/* ----------------------------------------------------
   アルバム分類（必要に応じて追加・編集OK）
   ※ 曲名は JSON の title と完全一致させる
---------------------------------------------------- */
const albumMap = {
/* ------------------------- SUGA / Agust D ソロ作品 ------------------------- */
  "D-DAY": ["D‐Day", "해금", "HUH?!", "Snooze", "AMYGDALA", "SDL", "Polar Night", "Interlude : Dawn", "People Pt.2 (feat. IU)"],

  "D-2": ["Moonlight", "Daechwita", "28", "Burn It", "People", "Honsool", "Interlude : Set me free", "Strange", "Dear my friend"],

  "Agust D": ["Intro ; Dt sugA", "Agust D", "give it to me", "skit", "724148", "140503 at dawn", "The Last", "Tony Montana", "Interlude ; Dream, Reality", "So Far Away"],

   /* -------------------------  BTS アルバム（ユンギ参加曲）  ------------------------- */
  "BE": ["Life Goes On", "Fly To My Room", "Blue & Grey", "Skit", "Telepathy", "Dis-ease", "Stay", "Dynamite"],

  "MAP OF THE SOUL : 7": ["Interlude : Shadow", "Black Swan", "Filter", "My Time", "Louder than bombs", "ON", "UGH!", "00:00 (Zero O’Clock)", "Inner Child", "Friends", "Moon", "Respect", "We are Bulletproof : the Eternal"],

  "MAP OF THE SOUL : PERSONA": ["Intro : Persona", "Boy With Luv", "Mikrokosmos", "Make It Right", "HOME", "Jamais Vu", "Dionysus"],

  "LOVE YOURSELF 轉 'Tear'": ["Fake Love", "134340", "Paradise", "Love Maze", "Magic Shop", "Airplane pt.2", "Anpanman", "So What", "Outro : Tear"],

  "LOVE YOURSELF 承 'Her'": ["Intro : Serendipity", "DNA", "Best Of Me", "Dimple", "Pied Piper", "Skit : Billboard Music Awards Speech", "MIC Drop", "Go Go", "Outro : Her"],

  "LOVE YOURSELF 結 'Answer'": ["Euphoria", "Trivia 起 : Just Dance", "Serendipity (Full Length Edition)", "DNA", "Dimple", "Trivia 承 : Love", "Her", "Singularity", "Fake Love", "The Truth Untold", "Trivia 轉 : Seesaw", "Tear", "Epiphany", "I'm Fine", "IDOL", "Answer : Love Myself"],

  "WINGS": ["Begin", "Lie", "Stigma", "First Love", "Reflection", "MAMA", "Awake", "Lost", "BTS Cypher 4", "Am I Wrong", "21st Century Girl", "2! 3!"],

  "YOU NEVER WALK ALONE": ["Spring Day", "Not Today", "Outro : Wings"],

  "The Most Beautiful Moment in Life: Young Forever": ["Fire", "Save ME", "Epilogue : Young Forever"],

  "花樣年華 pt.2": ["RUN", "Butterfly", "Whalien 52", "Ma City", "Silver Spoon", "Autumn Leaves"],

  "花樣年華 pt.1": ["I Need U", "Hold Me Tight", "Dope", "Boyz with Fun", "Converse High", "Moving On"],

  "DARK&WILD": ["Danger", "War of Hormone", "Hip Hop Lover", "Let Me Know", "Rain", "BTS Cypher Pt.3 : Killer", "Interlude : What are you doing now"],

  "Skool Luv Affair": ["Boy In Luv", "Just One Day", "Tomorrow", "BTS Cypher Pt.2 : Triptych"],

  "O!RUL8,2?": ["N.O", "We On", "If I Ruled The World", "Coffee", "BTS Cypher Pt.1"],

  "2 COOL 4 SKOOL": [ "No More Dream", "We Are Bulletproof Pt.2", "I Like It" ],

  /* コラボ / OST / 単発リリース  ------------------------- */
  "Other Works": [ "Lilith (Diablo IV anthem)", "eight", "SUGA’s Interlude", "Over The Horizon", "Song Request", "신청곡", "Blueberry Eyes", "Blueberry Eyes (Steve Aoki remix)", "Girl of My Dreams", "That That", "에잇" ]
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
