document.addEventListener('DOMContentLoaded', () => {
  // 各要素の取得
  const loadingMessage = document.getElementById('loading-message');
  const lastUpdatedElement = document.getElementById('last-updated');
  const chartCanvas = document.getElementById('dailyChart');

  // キャッシュ回避のためにタイムスタンプ付きURLでJSON取得
  const dataUrl = 'https://sugacatroom.github.io/agustd/data.json?' + new Date().getTime();

  fetch(dataUrl)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
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

          // 金曜からの再生回数を計算して表示
          const weeklyTotal = calcWeeklyTotal(history, video.videoId);
          videoContainer.querySelector('.views-this-week').textContent = weeklyTotal.toLocaleString();

          // 累計再生回数を表示
          videoContainer.querySelector('.views-total').textContent = video.views_total.toLocaleString();
        }
      });

      // ========================
      // グラフ描画
      // ========================

      // ラベル生成（日付）
      const labels = history.map(d => {
        const date = new Date(d.date);
        date.setDate(date.getDate() - 1); // 1日前にずらす
        return `${date.getMonth() + 1}/${date.getDate()}`;
      });

      // ラベル省略関数
      function truncateLabel(text, maxLength = 40) {
        return text.length > maxLength ? text.slice(0, maxLength - 1) + "…" : text;
      }

      // データセット生成
      const datasets = [];
      latest.videos.forEach(video => {
        const dataPoints = history.map(d => {
          const found = d.videos.find(v => v.videoId === video.videoId);
          return found ? found.views_diff : 0;
        });

        datasets.push({
          label: truncateLabel(video.title, 20),
          data: dataPoints,
          borderWidth: 2,
          fill: false,
          tension: 0.2
        });
      });

      // ウォーターマーク用画像
      const logoImage = new Image();
      logoImage.src = "assets/images/cat_logo.png"; // PNGファイル

      // ウォーターマークプラグイン
      const watermarkPlugin = {
        id: "watermark",
        beforeDraw: (chart) => {
          if (logoImage.complete) {
            const ctx = chart.ctx;
            const chartArea = chart.chartArea;

            const targetWidth = chartArea.width * 0.3;
            const aspectRatio = logoImage.height / logoImage.width;
            const targetHeight = targetWidth * aspectRatio;

            const x = chartArea.left + (chartArea.width - targetWidth) / 2;
            const y = chartArea.top + (chartArea.height - targetHeight) / 2;

            ctx.save();
            ctx.globalAlpha = 0.5;
            ctx.drawImage(logoImage, x, y, targetWidth, targetHeight);
            ctx.restore();
          }
        }
      };

      // グラフ描画
      new Chart(chartCanvas, {
        type: 'line',
        data: { labels, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: { display: true, text: "日別 再生回数" },
            legend: { position: 'bottom', labels: { font: { size: 10 }, boxWidth: 12 } },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const videoId = latest.videos.find(v => truncateLabel(v.title, 20) === context.dataset.label)?.videoId;
                  const fullTitle = latest.videos.find(v => v.videoId === videoId)?.title || context.dataset.label;
                  return `${fullTitle}: ${context.formattedValue}回`;
                }
              }
            }
          },
          scales: {
            y: { beginAtZero: true, ticks: { stepSize: 5000 } }
          }
        },
        plugins: [watermarkPlugin] // ← プラグイン登録
      });

      // ローディングメッセージを非表示
      loadingMessage.style.display = 'none';
    })
    .catch(error => {
      console.error('データの取得中にエラーが発生しました:', error);
      loadingMessage.textContent = 'データの読み込みに失敗しました。';
    });

  // ========================
  // 背景色変更機能
  // ========================
  const colorPicker = document.getElementById('bgColorPicker');
  colorPicker.addEventListener('input', function () {
    document.body.style.backgroundColor = this.value;
  });

  // ========================
  // ヘルパー関数
  // ========================
  function calcWeeklyTotal(history, videoId) {
    const endIndex = history.length - 1;
    const latestDate = history[endIndex].date;

    const weekday = getJSTWeekday(latestDate); // 日=0, 月=1,...土=6

    // 最新日からさかのぼって直近の土曜を探す
    let startIndex = endIndex;
    while (startIndex > 0) {
      const d = getJSTWeekday(history[startIndex].date);
      if (d === 6) break; // 土曜
      startIndex--;
    }

    const weekData = history.slice(startIndex, endIndex + 1);

    return weekData.reduce((sum, day) => {
      const v = day.videos.find(v => v.videoId === videoId);
      return sum + (v ? v.views_diff : 0);
    }, 0);
  }

  // JST基準で曜日を返す関数
  function getJSTWeekday(dateString) {
    const parts = dateString.split("-");
    const y = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10) - 1;
    const d = parseInt(parts[2], 10);
    const jstDate = new Date(y, m, d);
    return jstDate.getDay();
  }
});
