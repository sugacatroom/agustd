document.addEventListener('DOMContentLoaded', () => {
  // 各要素の取得
  const loadingMessage = document.getElementById('loading-message');
  const lastUpdatedElement = document.getElementById('last-updated');
  const chartCanvas = document.getElementById('dailyChart');

  // キャッシュ回避のためにタイムスタンプ付きURLでJSON取得
  const dataUrl = 'https://sugacatroom.github.io/agustd/data.json?' + new Date().getTime();

  fetch(dataUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(history => {
      if (!Array.isArray(history) || history.length === 0) {
        throw new Error("履歴データが取得できません");
      }

      // 最終更新日を表示
      lastUpdatedElement.textContent = `最終更新日: ${history[history.length - 1].date}`;

      // 最新データを使って動画情報を更新
      const latest = history[history.length - 1];
      latest.videos.forEach(video => {
        const videoContainer = document.querySelector(`.video-item[data-video-id="${video.videoId}"]`);
        if (videoContainer) {
          // タイトル表示
          videoContainer.querySelector('.title').textContent = video.title;

          // 金曜からの再生回数を計算して表示（曜日ごとに分岐）
          const weeklyTotal = calcWeeklyTotal(history, video.videoId);
          videoContainer.querySelector('.views-this-week').textContent = weeklyTotal.toLocaleString();

          // 累計再生回数を表示
          videoContainer.querySelector('.views-total').textContent = video.views_total.toLocaleString();
        }
      });

      // グラフ用ラベル（日付）を生成
      const labels = history.map(d => {
        const date = new Date(d.date);
        date.setDate(date.getDate() - 1); // 任意で1日前にずらす
        return `${date.getMonth() + 1}/${date.getDate()}`;
      });

      // ラベルを省略する関数（最大20文字）
      function truncateLabel(text, maxLength = 20) {
        return text.length > maxLength ? text.slice(0, maxLength - 1) + "…" : text;
      }

      // グラフ用データセットを生成
      const datasets = [];
      latest.videos.forEach(video => {
        const dataPoints = history.map(d => {
          const found = d.videos.find(v => v.videoId === video.videoId);
          return found ? found.views_diff : 0;
        });

