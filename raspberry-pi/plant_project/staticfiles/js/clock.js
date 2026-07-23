// ==============================
// リアルタイム時計
// ==============================

function updateClock() {

    const clock = document.getElementById("realtime-clock");

    // 時計表示がないページでは何も表示しない
    if (!clock){
        return;
    }

    const now = new Date();

    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");

    clock.textContent = `${hours}:${minutes}:${seconds}`;
}

// 初回表示
updateClock();

// 1秒ごとに更新
setInterval(updateClock, 1000);