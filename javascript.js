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

          // 金曜からの再生回数を計算して表示
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

        datasets.push({
          label: truncateLabel(video.title, 20), // ラベルを省略して表示
          data: dataPoints,
          borderWidth: 2,
          fill: false,
          tension: 0.2
        });
      });

      // 折れ線グラフを描画
      new Chart(chartCanvas, {
        type: 'line',
        data: { labels, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: "毎日の再生回数"
            },
            legend: {
              position: 'bottom',
              labels: {
                font: {
                  size: 10 // ラベルの文字サイズを小さく
                },
                boxWidth: 12 // 色の四角も小さく
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  // ツールチップではフルタイトルを表示
                  const videoId = latest.videos.find(v => truncateLabel(v.title, 20) === context.dataset.label)?.videoId;
                  const fullTitle = latest.videos.find(v => v.videoId === videoId)?.title || context.dataset.label;
                  return `${fullTitle}: ${context.formattedValue}回`;
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 5000 // Y軸の目盛り間隔
              }
            }
          }
        }
      });

      // ローディングメッセージを非表示に
      loadingMessage.style.display = 'none';
    })
    .catch(error => {
      console.error('データの取得中にエラーが発生しました:', error);
      loadingMessage.textContent = 'データの読み込みに失敗しました。';
    });

  // JST基準で曜日を返す関数（日=0, 月=1,...土=6）
  function getJSTWeekday(dateString) {
    const parts = dateString.split("-");
    const y = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10) - 1;
    const d = parseInt(parts[2], 10);
    const jstDate = new Date(y, m, d);
    return jstDate.getDay();
  }

  // 金曜起点で曜日に応じた再生数合計を返す関数
  function calcWeeklyTotal(history, videoId) {
    const latestDate = history[history.length - 1].date;
    const todayWeekday = getJSTWeekday(latestDate); // 今日の曜日

    // 金曜のインデックスを探す（最新日からさかのぼる）
    let startIndex = history.length - 1;
    while (startIndex > 0) {
      if (getJSTWeekday(history[startIndex].date) === 5) break; // 金曜
      startIndex--;
    }

    // 金曜から今日の曜日までのデータを抽出
    const weekData = history.slice(startIndex).filter(day => {
      const dayWeek = getJSTWeekday(day.date);
      if (startIndex === history.length - 1) return true; // 金曜だけ
      if (dayWeek === todayWeekday || dayWeek === 5 || dayWeek < todayWeekday) return true;
      return false;
    });

    // views_diff を合計して返す
    return weekData.reduce((sum, day) => {
      const v = day.videos.find(v => v.videoId === videoId);
      return sum + (v ? v.views_diff : 0);
    }, 0);
  }

  // 背景色変更機能
  const colorPicker = document.getElementById('bgColorPicker');
  colorPicker.addEventListener('input', function () {
    document.body.style.backgroundColor = this.value;
  });
});
