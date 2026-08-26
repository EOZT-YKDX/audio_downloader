// 窗口拖拽变量
const dragWindow = document.getElementById("dragWindow");
const dragBar = document.getElementById("dragBar");
let isDrag = false;
let dragStartX, dragStartY, winStartX, winStartY;

// 弹窗元素
const delMask = document.getElementById("delMask");
const cancelDel = document.getElementById("cancelDel");
const confirmDel = document.getElementById("confirmDel");
let needClearAll = false;

// iframe及导航按钮
const iframe = document.getElementById("contentIframe");
const navBtns = document.querySelectorAll(".sidebar-btn[data-view]");
const addTaskBtn = document.getElementById("addTaskBtn");
const sidebarAllBtns = document.querySelectorAll(".sidebar-btn");
const closeBtn = document.getElementById("closeBtn");
const minBtn = document.getElementById("minBtn");

// 初始化
window.addEventListener("load", () => {
    initDragWindow();
    initModalEvent();
    initViewSwitch();
    initAddTaskBtn();
    initCloseBtn();
    initMinBtn();
    initThemeSync();
});

// 主题同步（接收 iframe 消息）
function initThemeSync() {
    window.addEventListener("message", (e) => {
        if (e.data && e.data.type === "themeUpdate") {
            applyThemeFromIframe(e.data.theme);
        }
    });
}

function applyThemeFromIframe(theme) {
    const root = document.documentElement;
    
    // 应用主题模式
    if (theme.mode === "dark") {
        root.style.setProperty("--bg-primary", "#1c1c1e");
        root.style.setProperty("--bg-secondary", "#2b2b2d");
        root.style.setProperty("--bg-tertiary", "#3a3a3c");
        root.style.setProperty("--text-primary", "#fff");
        root.style.setProperty("--text-secondary", "#999");
        root.style.setProperty("--border-color", "#3a3a3c");
        root.style.setProperty("--btn-bg", "#3a3a3c");
        root.style.setProperty("--btn-text", "#ffffff");
        root.style.setProperty("--btn-hover-bg", "#48484a");
        root.style.setProperty("--font-weight-normal", "400");
        root.style.setProperty("--font-weight-medium", "500");
        root.style.setProperty("--font-weight-semibold", "500");
        root.style.setProperty("--title-color", "#fff");
    } else if (theme.mode === "light") {
        root.style.setProperty("--bg-primary", "#F3F3F5");
        root.style.setProperty("--bg-secondary", "#F3F3F5");
        root.style.setProperty("--bg-tertiary", "#E5E7EB");
        root.style.setProperty("--text-primary", "#5E5E6B");
        root.style.setProperty("--text-secondary", "#5E5E6B");
        root.style.setProperty("--border-color", "#E5E7EB");
        root.style.setProperty("--btn-bg", "#D1D5DB");
        root.style.setProperty("--btn-text", "#374151");
        root.style.setProperty("--btn-hover-bg", "#C0C4CC");
        root.style.setProperty("--font-weight-normal", "400");
        root.style.setProperty("--font-weight-medium", "400");
        root.style.setProperty("--font-weight-semibold", "400");
        root.style.setProperty("--title-color", "#5E5E6B");
    } else if (theme.mode === "system") {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        applyThemeFromIframe({ ...theme, mode: prefersDark ? "dark" : "light" });
        return;
    }
    
    // 应用主题色
    if (theme.accentColor) {
        root.style.setProperty("--accent-color", theme.accentColor);
    }
    
    // 应用背景
    if (theme.bgType === "solid") {
        document.body.style.background = "var(--bg-primary)";
        document.body.style.backgroundImage = "none";
    } else if (theme.bgType === "image" && theme.bgImage) {
        document.body.style.backgroundImage = `url(${theme.bgImage})`;
        document.body.style.backgroundSize = "cover";
        document.body.style.backgroundPosition = "center";
    } else {
        document.body.style.background = "var(--bg-primary)";
        document.body.style.backgroundImage = "none";
    }
    
    // 应用字号
    if (theme.fontSize) {
        root.style.setProperty("--font-size-base", `${theme.fontSize}px`);
        document.body.style.fontSize = `${theme.fontSize}px`;
    }
}

function adjustColor(hex, amount) {
    const num = parseInt(hex.slice(1), 16);
    const r = Math.min(255, Math.max(0, (num >> 16) + amount));
    const g = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + amount));
    const b = Math.min(255, Math.max(0, (num & 0x0000FF) + amount));
    return `#${(r << 16 | g << 8 | b).toString(16).padStart(6, "0")}`;
}

// 窗口拖拽功能
function initDragWindow() {
    dragBar.addEventListener("mousedown", (e) => {
        isDrag = true;
        dragStartX = e.clientX;
        dragStartY = e.clientY;
        const rect = dragWindow.getBoundingClientRect();
        winStartX = rect.left;
        winStartY = rect.top;
        dragWindow.style.transition = "none";
    });

    document.addEventListener("mousemove", (e) => {
        if (!isDrag) return;
        const dx = e.clientX - dragStartX;
        const dy = e.clientY - dragStartY;
        dragWindow.style.left = winStartX + dx + "px";
        dragWindow.style.top = winStartY + dy + "px";
        dragWindow.style.transform = "translate(0,0)";
    });

    document.addEventListener("mouseup", () => {
        isDrag = false;
        dragWindow.style.transition = "";
    });
}

// 视图切换
function initViewSwitch() {
    navBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetView = btn.dataset.view;
            navBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            iframe.contentWindow.postMessage({ type: "switchView", view: targetView }, "*");
        });
    });
}

// 新建任务按钮
function initAddTaskBtn() {
    addTaskBtn.addEventListener("click", () => {
        if (!iframe.contentWindow) return;
        sidebarAllBtns.forEach(btn => btn.disabled = true);
        iframe.contentWindow.postMessage({ type: "openAddTaskModal" }, "*");
    });
}

// 最小化按钮
function initMinBtn() {
    minBtn.addEventListener("click", () => {
        if (window.pywebview) {
            window.pywebview.api.minimize();
        } else if (window.require) {
            const { ipcRenderer } = window.require('electron');
            ipcRenderer.send('minimize-window');
        }
    });
}

// 退出按钮
function initCloseBtn() {
    closeBtn.addEventListener("click", () => {
        if (window.pywebview) {
            window.pywebview.api.close();
        } else if (window.require) {
            const { ipcRenderer } = window.require('electron');
            ipcRenderer.send('close-window');
        } else {
            window.close();
        }
    });
}

// 删除弹窗事件
function initModalEvent() {
    cancelDel.addEventListener("click", () => {
        delMask.classList.remove("show");
        needClearAll = false;
    });

    confirmDel.addEventListener("click", () => {
        delMask.classList.remove("show");
        if (!needClearAll) return;
        iframe.contentWindow.postMessage({ type: "clearAllTask" }, "*");
        needClearAll = false;
    });

    delMask.addEventListener("click", (e) => {
        if (e.target === delMask) delMask.classList.remove("show");
    });

    window.addEventListener("message", (e) => {
        if (e.data.type === "openDeleteModal") {
            needClearAll = true;
            delMask.classList.add("show");
        }
        if (e.data.type === "closeAddModal") {
            sidebarAllBtns.forEach(btn => btn.disabled = false);
        }
    });
}