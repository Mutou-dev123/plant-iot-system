// Chart.jsを用いた直近の観測履歴のグラフ描画JavaScript

const canvas = document.getElementById("envChart");

let envChart = null;

if (canvas && typeof timeLabels !== "undefined") {

    const ctx = canvas.getContext("2d");

    envChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: timeLabels,
            datasets: [
                {
                    label: "土壌水分（％）",
                    data: moistureData,
                    borderColor: "#0dcaf0",
                    backgroundColor: "rgba(13, 202, 240, 0.1)",
                    tension: 0.3
                },
                {
                    label: "🌡️ 温度 (℃)",
                    data: tempData,
                    borderColor: "#dc3545",
                    backgroundColor: "rgba(220, 53, 69, 0.1)",
                    tension: 0.3
                },
                {
                    label: "💨 湿度 (%)",
                    data: humidityData,
                    borderColor: "#198754",
                    backgroundColor: "rgba(25, 135, 84, 0.1)",
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: "#ffffff"
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: "#333333" },
                    ticks: { color: "#aaaaaa" }
                },
                y: {
                    grid: { color: "#333333" },
                    ticks: { color: "#aaaaaa" },
                    min: 0,
                    max: 100
                }
            }
        }
    });

    // グラフ生成後にタイマー開始
    setInterval(updateChart, UPDATE_INTERVAL);
}

let lastLabel =
    timeLabels.length > 0
        ? timeLabels[timeLabels.length - 1]
        : null;

async function updateChart() {

    if (!envChart) return;

    try {

        const response = await fetch("/api/chart-data/");
        const data = await response.json();

        const newestLabel =
            data.labels[data.labels.length - 1];

        if (newestLabel === lastLabel) {
            return;
        }
        
        lastLabel = newestLabel;

        envChart.data.labels = data.labels;

        envChart.data.datasets[0].data = data.moisture;
        envChart.data.datasets[1].data = data.temperature;
        envChart.data.datasets[2].data = data.humidity;

        envChart.update();

        console.log("グラフ更新");

    } catch (error) {

        console.error(error);

    }

}