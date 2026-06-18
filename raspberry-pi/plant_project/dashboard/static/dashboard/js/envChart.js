// Chart.jsを用いた直近の観測履歴のグラフ描画JavaScript

// ここでは描画ロジックのみを記述する
const ctx = document.getElementById('envChart').getContext('2d');

const envChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: timeLabels, // HTML側で作られた配列を使用
        datasets: [
            {
                label: '土壌水分（％）',
                data: moistureData,
                borderColor: '#0dcaf0',
                backgroundColor: 'rgba(13, 202, 240, 0.1)',
                tension: 0.3
            },
            {
                label: '🌡️ 温度 (℃)',
                data: tempData,
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.3
            },
            {
                label: '💨 湿度 (%)',
                data: humidityData,
                borderColor: '#198754',
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                tension: 0.3
            }
        ]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { labels: { color: '#ffffff' } }
        },
        scales: {
            x: { grid: { color: '#333333' }, ticks: { color: '#aaaaaa' } },
            y: { grid: { color: '#333333' }, ticks: { color: '#aaaaaa' }, min: 0, max: 100 }
        }
    }
})