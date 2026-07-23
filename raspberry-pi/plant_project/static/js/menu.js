//==========================================
// ハンバーガーメニュー制御
//==========================================

// 要素取得
const menuButton = document.getElementById("menu-button");
const sidebar = document.getElementById("sidebar");

// ボタンが存在する場合のみ実行
if (menuButton && sidebar) {

    menuButton.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });
}