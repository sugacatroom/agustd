// アルバム分類（必要に応じて追加）
const albumMap = {
  "D-DAY": ["D‐Day", "해금", "HUH?!", "Snooze", "AMYGDALA"],
  "D-2": ["Moonlight", "Daechwita", "Burn It", "People", "Strange", "28"],
  "Agust D": ["Agust D", "give it to me", "The Last", "724148", "140503 at dawn"],
  "BE": ["Life Goes On", "Fly To My Room", "Blue & Grey", "Telepathy", "Dis-ease", "Stay"],
  "LOVE YOURSELF 轉 'Tear'": ["Fake Love", "134340", "Paradise", "Magic Shop", "So What", "Outro : Tear"]
};

async function loadData() {
  const today = await fetch("../docs/spotify_data.json").then(r => r.json());
  const yesterday = await fetch("../docs/spotify_data_prev.json").then(r => r.json());

  document.getElementById("updated").textContent =
    "更新日時：" + today.updated_at;

  const prevMap = {};
  yesterday.tracks.forEach(t => prevMap[t.title] = t.spotify_popularity);

  const albumsDiv = document.getElementById("albums");

  for (const [album, titles] of Object.entries(albumMap)) {
    const albumBox = document.createElement("div");
    albumBox.className = "album";

    const header = document.createElement("div");
    header.className = "album-header";
    header.textContent = album;

    const content = document.createElement("div");
    content.className = "album-content";

    titles.forEach(title => {
      const track = today.tracks.find(t => t.title === title);
      if (!track) return;

      const prev = prevMap[title];
      let diff = "";
      let diffClass = "diff-same";

      if (prev !== undefined) {
        const d = track.spotify_popularity - prev;
        if (d > 0) { diff = `↑${d}`; diffClass = "diff-up"; }
        else if (d < 0) { diff = `↓${Math.abs(d)}`; diffClass = "diff-down"; }
        else diff = "→0";
      }

      const row = document.createElement("div");
      row.className = "track-row";
      row.innerHTML = `
        <a href="${track.spotify_url}" target="_blank">${track.title}</a>
        <span>${track.spotify_popularity}</span>
        <span class="${diffClass}">${diff}</span>
      `;
      content.appendChild(row);
    });

    header.addEventListener("click", () => {
      content.style.display = content.style.display === "block" ? "none" : "block";
    });

    albumBox.appendChild(header);
    albumBox.appendChild(content);
    albumsDiv.appendChild(albumBox);
  }
}

loadData();

