//==========================================
// ハンバーガーメニュー制御
//==========================================

// 要素取得
const menuButton = document.getElementById("menu-button");
const sidebar = document.getElementById("sidebar");
const main = document.querySelector("main");

function openMenu() {
    sidebar.classList.add("open");
    main.classList.add("shift");
}

function closeMenu() {
    sidebar.classList.remove("open");
    main.classList.remove("shift");
}

menuButton.addEventListener("click", () => {

    if (sidebar.classList.contains("open")) {
        closeMenu();
    } else {
        openMenu();
    }

});

// メニュー外押下時に、メニューを閉じる
document.addEventListener("click", (event) => {

    // メニューが閉じているなら何もしない
    if (!sidebar.classList.contains("open")) {
        return;
    }

    // サイドバー内・メニューボタンなら閉じない
    if (
        sidebar.contains(event.target) ||
        menuButton.contains(event.target)
    ) {
        return;
    }

    closeMenu();

});

// PCのESCキーでメニューを閉じる
document.addEventListener("keydown", (event) => {

    if (event.key === "Escape") {
        closeMenu();
    }

});