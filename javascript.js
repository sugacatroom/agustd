
        document.addEventListener('DOMContentLoaded', () => {
            const loadingMessage = document.getElementById('loading-message');
            const lastUpdatedElement = document.getElementById('last-updated');
            const chartCanvas = document.getElementById('dailyChart');

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

                    // 最新日付を表示
                    lastUpdatedElement.textContent = `最終更新日: ${history[history.length - 1].date}`;

                    // --- 上部の動画情報更新 ---
                    const latest = history[history.length - 1];
                    latest.videos.forEach(video => {
                        const videoContainer = document.querySelector(`.video-item[data-video-id="${video.videoId}"]`);
                        if (videoContainer) {
                            videoContainer.querySelector('.title').textContent = video.title;
                            const weeklyTotal = calcWeeklyTotal(history, video.videoId);
                            videoContainer.querySelector('.views-this-week').textContent = weeklyTotal.toLocaleString();
                            videoContainer.querySelector('.views-total').textContent = video.views_total.toLocaleString();
                        }
                    });
                    // JST基準で曜日を返す関数
            function getJSTWeekday(dateString) {
              const parts = dateString.split("-");
              const y = parseInt(parts[0], 10);
              const m = parseInt(parts[1], 10) - 1; // 0始まり
              const d = parseInt(parts[2], 10);
              const jstDate = new Date(y, m, d);
              return jstDate.getDay(); // 日=0, 月=1,...土=6
            }

 　　　　　 function calcWeeklyTotal(history, videoId) {
           const latestDate = history[history.length - 1].date;
           const weekday = getJSTWeekday(latestDate); // JSTの曜日 (日=0, 月=1, ..., 土=6)
           
           // JSTの金曜を週のスタートにする
           // 金曜=5, 土曜=6, 日曜=0, ...
           // → 直近の金曜日を探す
           const endIndex = history.length - 1;

           // 最新日からさかのぼって「金曜」を探す
           let startIndex = endIndex;
           while (startIndex > 0) {
               const d = getJSTWeekday(history[startIndex].date);
               if (d === 5) break; // 金曜
               startIndex--;
           }

           // 金曜から最新日までを集計
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
           return jstDate.getDay(); // JSTの曜日 (日=0, 月=1,...土=6)
           }
                });
            // --- 全曲まとめて折れ線グラフ ---
            //yyyy-mm-dd表示
            //const labels = history.map(d => d.date);
            // 例: "9/17"
            const labels = history.map(d => {
            const date = new Date(d.date);
                date.setDate(date.getDate() - 1); // ← ここで1日前にずらす
                return `${date.getMonth() + 1}/${date.getDate()}`; 
            });
            const datasets = [];

            latest.videos.forEach(video => {
                const dataPoints = history.map(d => {
                    const found = d.videos.find(v => v.videoId === video.videoId);
                    return found ? found.views_diff : 0;
                });
                
                datasets.push({
                    label: video.title,
                    data: dataPoints,
                    borderWidth: 2,
                    fill: false,
                    tension: 0.2
                });
            });
            
            new Chart(chartCanvas, {
                type: 'line',
                data: { labels, datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false, 
                    plugins: {
                        title: { display: true, text: "毎日の再生回数" },
                        legend: { position: 'bottom' }
                            },
                            scales: {
                                y: { 
                                    beginAtZero: true,
                                    //suggestedMax: 80000,   // データに応じて調整
                                    ticks: {
                                      stepSize: 5000    // 目盛りを10000単位で表示
                                   }
                                }
                            }
                        }
                    });

                    loadingMessage.style.display = 'none';
                })
                .catch(error => {
                    console.error('データの取得中にエラーが発生しました:', error);
                    loadingMessage.textContent = 'データの読み込みに失敗しました。';
                });



// 背景色変更
      const colorPicker = document.getElementById('bgColorPicker');

        colorPicker.addEventListener('input', function () {
          document.body.style.backgroundColor = this.value;
        });

