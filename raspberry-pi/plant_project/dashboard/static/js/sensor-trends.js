function initializeSensorTrends() {
    const data = document.getElementById("sensor-trend-data");
    const cardTemplate = document.getElementById("sensor-trend-chart-card");
    if (!data || !cardTemplate) return;

    if (!window.Chart) {
        document.getElementById("sensor-trend-chart-error").hidden = false;
        return;
    }

    const { boundaries, series, use_daily_summary } = JSON.parse(data.textContent);
    const metrics = [
        { key: "temperature", title: "温度推移（℃）", color: "#b83d38" },
        { key: "humidity", title: "湿度推移（%）", color: "#236fa6" },
        { key: "moisture", title: "土壌水分推移（%）", color: "#32754a" },
        { key: "light", title: "光量推移（スコア）", color: "#9a620c" },
    ];

    // サーバから受け取った日本時間をそのまま表示する。
    const formatDate = (stamp) => stamp.slice(0, 16).replace("T", " ");
    const includeTime = Date.parse(boundaries.at(-1)) - Data.parse(boundaries[0])
        <= 3 * 24 * 60 * 60 * 1000;
    const labels = boundaries.slice(0, -1).map((stamp) =>
        includeTime ? formatDate(stamp).slice(5) : stamp.slice(0, 10)
    );

    for (const grid of document.querySelectorAll(".sensor-trend-charts")) {
        const observations = series.filter((item) =>
            item.device_id === Number(grid.dataset.deviceID)
            && metrics.some(({ key }) => item[key].some((value) => value !== null))
        );
        if (observations.length === 0) continue;

        const cards = metrics.map(({ key, title, color }) => {
            const card = cardTemplate.contentEditable.cloneNode(true);
            const canvas = card.querySelector("canvas");
            const empty = card.querySelector("[data-no-measurement]");
            const values = observations[0][key];

            card.querySelector("h3").textContent = title;
            canvas.setAttribute("aria-label", title);
            empty.hidden = values.some((value) => value !== null);
            grid.append(card);

            const chart = new Chart(canvas, {
                type: "line",
                data: {
                    labels,
                    datasets: [{
                        data: values,
                        borderColor: color,
                        pointBackgroundColor: color,
                        pointRadius: 2,
                        tension: 0,
                        spanGaps: !use_daily_summary,
                        segment: {
                            borderDash: ({ p0, p1 }) =>
                                p0.skip || p1.skip ? [5, 4] : undefined,
                        },
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                title(items) {
                                    const index = items[0].dataIndex;
                                    const start = formatDate(boundaries[index]);
                                    const end = formatDate(boundaries[index + 1]);
                                    return start + " ～ " + end + "（日本時間）";
                                },
                            },
                        },
                    },
                    scales: {
                        x: { ticks: { maxTicksLimit: 6, maxRotation: 0 } },
                    },
                },
            });

            return { key, chart, empty };
        });

        const section = grid.closest(".sensor-trend-device");
        if (observations.length === 1) {
            const plantName = section.querySelector("[data-trend-plant-name]");
            plantName.textContent = observations[0].plantName;
            plantName.hidden = false;
            continue;
        }

        const select = section.querySelector("[data-trend-plant-select]");
        observations.forEach(({ plant_name }, index) => {
            select.add(new Option(plant_name, String(index)));
        });
        section.querySelector("[data-trend-plant-picker]").hidden = false;

        // 選択した植物の値で、このデバイスの4つのグラフを更新する。
        select.addEventListener("change", () => {
            const selected = observations[Number(select.value)];
            for (const { key, chart, empty } of cards) {
                const values = selected[key];
                chart.data.datasets[0].data = values;
                empty.hidden = values.some((value) => value !== null);
                chart.update("none");
            }
        });
    }
}

initializeSensorTrends();