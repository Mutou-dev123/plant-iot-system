//==========================================
// ハンバーガーメニュー制御
//==========================================

// 要素取得
const menuButton = document.getElementById("menu-button");
const sidebar = document.getElementById("sidebar");
const main = document.querySelector("main");

// ページによって要素がない場合は処理を終了する
if (menuButton && sidebar && main) {
    let closeTimer = null;

    // メニューを開き、ボタンの状態も更新する
    function openMenu() {
        clearTimeout(closeTimer);
        sidebar.classList.add("open");
        main.classList.add("shift");
        menuButton.setAttribute("aria-expanded-", "true");
    }

    // メニューを閉じ、ボタンの状態も更新する
    function closeMenu() {
        clearTimeout(closeTimer);
        sidebar.classList.remove("open");
        main.classList.remove("shift");
        menuButton.setAttribute("aria-expanded", "false");
    }

    // メニュー外へカーソルが出たとき、少し待ってから閉じる
    function scheduleClose(event) {
        const nextTarget = event.relatedTarget;

        // ボタンとメニューの間を移動している場合は閉じない
        if (
            nextTarget instanceof Node &&
            (menuButton.contains(nextTarget) || sidebar.contains(nextTarget))
        ) {
            return;
        }

        clearTimeout(closeTimer);
        closeTimer = setTimeout(() => {
            closeMenu();
        }, 400);
    }

    // ボタンまたはメニューにカーソルが入ったら開く
    menuButton.addEventListener("mouseenter", openMenu);
    sidebar.addEventListener("mouseenter", openMenu);

    // どちらからもカーソルが離れた場合だけ、閉じる処理を予約する
    menuButton.addEventListener("mouseleave", scheduleClose);
    sidebar.addEventListener("mouseleave", scheduleClose);

    // クリック・タップで開閉する
    menuButton.addEventListener("click", () => {
        if (sidebar.classList.contains("open")) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    // マウスホバーに対応したPCでだけ自動開閉を有効にする
    const canHover = window.matchMedia("(hover: hover) and (pointer: fine)");

    if (canHover.matches) {
        //ボタンまたはメニューにカーソルが入ったら開く
        menuButton.addEventListener("mouseenter", openMenu);
        sidebar.addEventListener("mouseenter", openMenu);

        // どちらからもカーソルが離れたら、少し待って閉じる
        menuButton.addEventListener("mouseleave", scheduleClose);
        sidebar.addEventListener("mouseleave", scheduleClose);
    }

    // メニューとボタンの外をクリックしたら閉じる
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

    // Escapeキーで閉じる
    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {
            closeMenu();
        }
    });
}