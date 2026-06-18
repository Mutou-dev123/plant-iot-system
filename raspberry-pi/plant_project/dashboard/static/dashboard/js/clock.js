// 現在時刻表示表JavaScript

function updateClock() {
            const now = new Date(); // パソコンの現在時刻を取得
            
            // 時・分・秒をそれぞれ2桁の文字にする（例: 5秒 ➡ "05"）
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            
            // HTMLの「realtime-clock」の部分を、今の時間に書き換える
            document.getElementById('realtime-clock').textContent = `${hours}:${minutes}:${seconds}`;
        }

        // 画面が開いた瞬間に、まず1回時計を表示する
        updateClock();

        // ⏱️ 1000ミリ秒（＝1秒）ごとに、updateClock関数をずっと実行し続ける！
        setInterval(updateClock, 1000);