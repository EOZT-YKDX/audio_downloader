// 全局任务数据
const taskList = [];
const taskListDom = document.getElementById("taskList");
const emptyTip = document.getElementById("emptyTip");
const topBar = document.getElementById("topBar");

// 弹窗DOM
const addTaskMask = document.getElementById("addTaskMask");
const taskOkBtn = document.getElementById("taskOkBtn");
const taskCancelBtn = document.getElementById("taskCancelBtn");
const linkInput = document.getElementById("linkInput");
const parseResultText = document.getElementById("parseResultText");
const taskNameInput = document.getElementById("taskNameInput");
const speedLimitSelect = document.getElementById("speedLimitSelect");
const conflictGroup = document.getElementById("conflictGroup");
const conflictBtns = conflictGroup.querySelectorAll(".conflict-btn");

// 定时器池
const progressTimers = new Map();
const speedTimers = new Map();

// 检查是否使用真实后端
const useRealBackend = typeof window.pywebview !== "undefined";

window.addEventListener("load", () => {
    refreshEmptyTip();
    bindLocalBtn();
    bindAddTaskModal();
    listenParentMsg();
    
    // 初始化真实后端
    if (useRealBackend) {
        initRealBackend();
    }
});

async function initRealBackend() {
    try {
        // 加载配置
        const config = await window.pywebview.api.load_config();
        const savePathInput = document.getElementById("savePathInput");
        
        if (config && config.download && config.download.savePath) {
            // 恢复保存路径
            if (savePathInput) {
                savePathInput.value = config.download.savePath;
            }
        } else {
            // 使用 Python 端生成的默认路径
            const defaultPath = await window.pywebview.api.get_default_save_path();
            if (savePathInput && defaultPath) {
                savePathInput.value = defaultPath;
                downloadSettings.savePath = defaultPath;
            }
        }
        
        // 加载已有任务
        const tasks = await window.pywebview.api.get_all_tasks();
        if (tasks && tasks.length > 0) {
            tasks.forEach(taskData => {
                const task = {
                    id: taskData.id,
                    name: taskData.name,
                    progress: taskData.progress,
                    speed: taskData.speed,
                    totalMb: 0,
                    isRunning: taskData.status === "downloading",
                    status: taskData.status,
                    speedLimit: 0,
                    conflictAction: "skip",
                    dom: null,
                    progressTimer: null,
                    speedTimer: null
                };
                taskList.push(task);
                renderTask(task);
            });
            refreshEmptyTip();
        }
    } catch (e) {
        console.warn("初始化后端失败:", e);
    }
}

// 接收后端推送的进度
window.receiveTaskProgress = function(status) {
    const task = taskList.find(t => t.id == status.id);
    if (!task) return;
    
    task.progress = status.progress;
    task.speed = status.speed;
    task.status = status.status;
    
    if (task.dom) {
        task.dom.querySelector(".progress-bar").style.width = status.progress + "%";
        
        const statusText = status.status === "completed" ? "已完成" : 
                          status.status === "failed" ? "失败" :
                          status.status === "paused" ? "已暂停" : "";
        
        task.dom.querySelector(".task-desc").textContent = 
            `${status.speed.toFixed(0)} KB/s | ${status.progress.toFixed(1)}% ${statusText}`;
        
        if (status.status === "completed" || status.status === "failed") {
            stopAllTimers(task);
            const btn = task.dom.querySelector(".play-toggle");
            if (status.status === "completed") {
                btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="#4caf50"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>`;
            } else {
                btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="#f44336"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>`;
            }
        }
    }
};

function refreshEmptyTip() {
    const hasTask = taskList.length > 0;
    emptyTip.style.display = hasTask ? "none" : "flex";
    if (hasTask) {
        topBar.classList.add("show");
    } else {
        topBar.classList.remove("show");
        progressTimers.forEach(t => clearInterval(t));
        speedTimers.forEach(t => clearInterval(t));
        progressTimers.clear();
        speedTimers.clear();
    }
}

function listenParentMsg() {
    window.addEventListener("message", (e) => {
        const data = e.data;
        if (data.type === "switchView") {
            document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("show"));
            document.querySelector(`.${data.view}-view`).classList.add("show");
        } else if (data.type === "openAddTaskModal") {
            addTaskMask.classList.add("show");
            linkInput.value = "";
            parseResultText.textContent = "暂无解析内容";
            taskNameInput.value = "";
            speedLimitSelect.value = "0";
            conflictBtns.forEach(b => b.classList.remove("active"));
            conflictBtns[0].classList.add("active");
        } else if (data.type === "clearAllTask") {
            progressTimers.forEach(t => clearInterval(t));
            speedTimers.forEach(t => clearInterval(t));
            progressTimers.clear();
            speedTimers.clear();
            taskList.length = 0;
            document.querySelectorAll(".task-item").forEach(item => {
                item.classList.add("remove");
                setTimeout(() => {
                    item.remove();
                    refreshEmptyTip();
                }, 320);
            });
        }
    });
}

/**
 * 相似名称自动加后缀 -数字
 */
function getUniqueName(baseRaw) {
    const base = baseRaw.trim() || "下载任务";
    let maxSerial = -1;
    
    taskList.forEach(task => {
        if (task.name === base) {
            maxSerial = Math.max(maxSerial, 0);
        }
        const match = task.name.match(new RegExp(`^${base.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}-(\\d+)$`));
        if (match) {
            const num = parseInt(match[1], 10);
            maxSerial = Math.max(maxSerial, num);
        }
    });
    
    if (maxSerial === -1) return base;
    return `${base}-${maxSerial + 1}`;
}

function bindAddTaskModal() {
    taskCancelBtn.addEventListener("click", closeModal);
    addTaskMask.addEventListener("click", e => {
        if (e.target === addTaskMask) closeModal();
    });
    
    function closeModal() {
        addTaskMask.classList.remove("show");
        window.parent.postMessage({ type: "closeAddModal" }, "*");
    }

    linkInput.addEventListener("input", () => {
        const arr = linkInput.value.trim().split("\n").filter(i => i.trim());
        parseResultText.textContent = arr.length > 0 ? `已解析${arr.length}条下载链接` : "暂无解析内容";
    });

    conflictBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            conflictBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
        });
    });

    taskOkBtn.addEventListener("click", async () => {
        const links = linkInput.value.trim().split("\n").filter(line => line.trim());
        if (!links.length) return;
        const baseName = taskNameInput.value.trim() || "下载任务";
        const speedLimit = parseInt(speedLimitSelect.value);
        const conflictAction = conflictGroup.querySelector(".conflict-btn.active").dataset.action;
        
        // 获取保存路径
        let savePath = "";
        if (useRealBackend) {
            const config = await window.pywebview.api.load_config();
            savePath = config?.download?.savePath || "";
        }
        
        if (!savePath && useRealBackend) {
            alert("请先在设置中选择保存路径");
            return;
        }
        
        for (const link of links) {
            const finalName = getUniqueName(baseName);
            
            if (useRealBackend) {
                // 使用真实后端
                try {
                    const taskId = await window.pywebview.api.add_download_task(
                        link.trim(),
                        finalName,
                        savePath,
                        speedLimit,
                        conflictAction
                    );
                    
                    if (taskId) {
                        const newTask = {
                            id: taskId,
                            name: finalName,
                            progress: 0,
                            speed: 0,
                            totalMb: 0,
                            isRunning: false,
                            status: "pending",
                            speedLimit: speedLimit,
                            conflictAction: conflictAction,
                            dom: null,
                            progressTimer: null,
                            speedTimer: null
                        };
                        taskList.push(newTask);
                        renderTask(newTask);
                        
                        // 自动开始下载
                        await window.pywebview.api.start_task(taskId);
                    }
                } catch (e) {
                    console.error("添加任务失败:", e);
                }
            } else {
                // 使用模拟数据
                const newTask = {
                    id: Date.now() + Math.floor(Math.random() * 1000),
                    name: finalName,
                    progress: 0,
                    speed: Math.floor(Math.random() * 1700 + 100),
                    totalMb: Math.floor(Math.random() * 800 + 100),
                    isRunning: true,
                    speedLimit: speedLimit,
                    conflictAction: conflictAction,
                    dom: null,
                    progressTimer: null,
                    speedTimer: null
                };
                taskList.push(newTask);
                renderTask(newTask);
            }
        }
        closeModal();
        refreshEmptyTip();
    });
}

function bindLocalBtn() {
    document.getElementById("startAll").addEventListener("click", async () => {
        for (const task of taskList) {
            task.isRunning = true;
            const btn = task.dom.querySelector(".play-toggle");
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>`;
            
            if (useRealBackend) {
                await window.pywebview.api.start_task(task.id);
            } else {
                startAllTimers(task);
            }
        }
    });
    
    document.getElementById("pauseAll").addEventListener("click", async () => {
        for (const task of taskList) {
            task.isRunning = false;
            const btn = task.dom.querySelector(".play-toggle");
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><polygon points="5 3 19 12 5 21 5 3"></polygon>`;
            
            if (useRealBackend) {
                await window.pywebview.api.pause_task(task.id);
            } else {
                stopAllTimers(task);
            }
        }
    });
    
    document.getElementById("deleteAll").addEventListener("click", async () => {
        if (useRealBackend) {
            const tasks = [...taskList];
            for (const task of tasks) {
                await window.pywebview.api.delete_task(task.id);
            }
            taskList.length = 0;
            document.querySelectorAll(".task-item").forEach(item => {
                item.classList.add("remove");
                setTimeout(() => {
                    item.remove();
                    refreshEmptyTip();
                }, 320);
            });
        } else {
            window.parent.postMessage({ type: "openDeleteModal" }, "*");
        }
    });
}

function renderTask(task) {
    const item = document.createElement("div");
    item.className = "task-item";
    item.dataset.taskId = task.id;
    item.innerHTML = `
        <div class="task-header">
            <div class="task-name">${task.name}</div>
            <div class="task-actions">
                <button class="action-btn play-toggle">
                    ${task.isRunning
                        ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></svg>`
                        : `<svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><polygon points="5 3 19 12 5 21 5 3"></polygon>`}
                </button>
                <button class="action-btn delete-btn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
        </div>
        <div class="task-progress-row">
            <div class="progress-wrap">
                <div class="progress-bar" style="width:${task.progress}%"></div>
            </div>
            <div class="task-desc">${task.speed} KB/s | ${task.progress.toFixed(1)}% | ${task.totalMb}MB</div>
        </div>
    `;
    taskListDom.appendChild(item);
    setTimeout(() => item.classList.add("show"), 10);
    task.dom = item;
    if (task.isRunning) startAllTimers(task);
    item.querySelector(".play-toggle").addEventListener("click", () => toggleTask(task));
    item.querySelector(".delete-btn").addEventListener("click", () => deleteTask(task));
}

function startAllTimers(task) {
    if (useRealBackend) return;
    
    if (!progressTimers.has(task.id)) {
        const pTimer = setInterval(() => {
            if (!task.isRunning || task.progress >= 100) {
                clearInterval(pTimer);
                progressTimers.delete(task.id);
                return;
            }
            task.progress = Math.min(100, task.progress + 0.08);
            task.dom.querySelector(".progress-bar").style.width = task.progress + "%";
            task.dom.querySelector(".task-desc").textContent = `${task.speed} KB/s | ${task.progress.toFixed(1)}% | ${task.totalMb}MB`;
        }, 100);
        task.progressTimer = pTimer;
        progressTimers.set(task.id, pTimer);
    }
    
    if (!speedTimers.has(task.id)) {
        const sTimer = setInterval(() => {
            if (!task.isRunning || task.progress >= 100) {
                clearInterval(sTimer);
                speedTimers.delete(task.id);
                return;
            }
            task.speed = Math.floor(Math.random() * 1700 + 100);
            task.dom.querySelector(".task-desc").textContent = `${task.speed} KB/s | ${task.progress.toFixed(1)}% | ${task.totalMb}MB`;
        }, 300);
        task.speedTimer = sTimer;
        speedTimers.set(task.id, sTimer);
    }
}

function stopAllTimers(task) {
    if (task.progressTimer) clearInterval(task.progressTimer);
    if (task.speedTimer) clearInterval(task.speedTimer);
    progressTimers.delete(task.id);
    speedTimers.delete(task.id);
}

async function toggleTask(task) {
    task.isRunning = !task.isRunning;
    const btn = task.dom.querySelector(".play-toggle");
    
    if (useRealBackend) {
        if (task.isRunning) {
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>`;
            await window.pywebview.api.start_task(task.id);
        } else {
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><polygon points="5 3 19 12 5 21 5 3"></polygon>`;
            await window.pywebview.api.pause_task(task.id);
        }
    } else {
        if (task.isRunning) {
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>`;
            startAllTimers(task);
        } else {
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><polygon points="5 3 19 12 5 21 5 3"></polygon>`;
            stopAllTimers(task);
        }
    }
}

async function deleteTask(task) {
    stopAllTimers(task);
    const idx = taskList.findIndex(t => t.id === task.id);
    if (idx > -1) taskList.splice(idx, 1);
    
    if (useRealBackend) {
        await window.pywebview.api.delete_task(task.id);
    }
    
    task.dom.classList.add("remove");
    setTimeout(() => {
        task.dom.remove();
        refreshEmptyTip();
    }, 320);
}

// 外观与主题设置
const themeSettings = {
    mode: "system",
    accentColor: "#007aff",
    bgType: "solid",
    bgColor: "#ffffff",
    bgImage: null
};

const downloadSettings = {
    format: "mp3",
    savePath: "",
    taskCount: 3
};

const languageTimeSettings = {
    language: "zh-CN",
    timeFormat: "24",
    dateFormat: "YMD"
};

const notificationSettings = {
    style: "banner",
    position: "corner",
    sound: true,
    vibration: false,
    preview: true,
    dndEnabled: false,
    dndStart: "22:00",
    dndEnd: "08:00"
};

function bindAppearanceSettings() {
    // 主题模式切换
    const themeModeGroup = document.getElementById("themeModeGroup");
    if (themeModeGroup) {
        themeModeGroup.querySelectorAll(".theme-mode-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                themeModeGroup.querySelectorAll(".theme-mode-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                themeSettings.mode = btn.dataset.mode;
                applyThemeMode(themeSettings.mode);
                saveThemeSettings();
            });
        });
    }

    // 主题色切换
    const accentColorGroup = document.getElementById("accentColorGroup");
    if (accentColorGroup) {
        accentColorGroup.querySelectorAll(".accent-color-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                if (btn.classList.contains("custom-color")) return;
                accentColorGroup.querySelectorAll(".accent-color-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                themeSettings.accentColor = btn.dataset.color;
                applyAccentColor(themeSettings.accentColor);
                saveThemeSettings();
            });
        });

        const customColorBtn = document.getElementById("customColorBtn");
        const customColorPicker = document.getElementById("customColorPicker");
        if (customColorBtn && customColorPicker) {
            customColorBtn.addEventListener("click", () => customColorPicker.click());
            customColorPicker.addEventListener("input", () => {
                accentColorGroup.querySelectorAll(".accent-color-btn").forEach(b => b.classList.remove("active"));
                customColorBtn.classList.add("active");
                customColorBtn.style.background = customColorPicker.value;
                themeSettings.accentColor = customColorPicker.value;
                applyAccentColor(themeSettings.accentColor);
                saveThemeSettings();
            });
        }
    }

    // 背景类型切换
    const bgTypeGroup = document.getElementById("bgTypeGroup");
    const bgColorItem = document.getElementById("bgColorItem");
    const bgImageItem = document.getElementById("bgImageItem");
    if (bgTypeGroup) {
        bgTypeGroup.querySelectorAll(".bg-type-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                bgTypeGroup.querySelectorAll(".bg-type-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                themeSettings.bgType = btn.dataset.type;
                if (bgColorItem) bgColorItem.style.display = themeSettings.bgType === "solid" ? "flex" : "none";
                if (bgImageItem) bgImageItem.style.display = themeSettings.bgType === "image" ? "flex" : "none";
                applyBackground();
                saveThemeSettings();
            });
        });
    }

    // 背景图片选择
    const bgImageBtn = document.getElementById("bgImageBtn");
    const bgImageInput = document.getElementById("bgImageInput");
    const bgImagePreview = document.getElementById("bgImagePreview");
    if (bgImageBtn && bgImageInput) {
        bgImageBtn.addEventListener("click", () => bgImageInput.click());
        bgImageInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (ev) => {
                themeSettings.bgImage = ev.target.result;
                if (bgImagePreview) {
                    bgImagePreview.style.backgroundImage = `url(${ev.target.result})`;
                }
                applyBackground();
                saveThemeSettings();
            };
            reader.readAsDataURL(file);
        });
    }
}

function bindDownloadSettings() {
    // 格式选择
    const formatSelect = document.getElementById("formatSelect");
    if (formatSelect) {
        formatSelect.addEventListener("change", () => {
            downloadSettings.format = formatSelect.value;
            saveDownloadSettings();
        });
    }

    // 保存路径选择
    const savePathBtn = document.getElementById("savePathBtn");
    const savePathInput = document.getElementById("savePathInput");
    if (savePathBtn && savePathInput) {
        savePathBtn.addEventListener("click", async () => {
            if (useRealBackend) {
                // 使用 Python 后端选择文件夹
                const currentPath = savePathInput.value || "";
                const path = await window.pywebview.api.select_folder(currentPath);
                if (path) {
                    savePathInput.value = path;
                    downloadSettings.savePath = path;
                    
                    // 保存到后端配置
                    await window.pywebview.api.save_config({
                        download: { savePath: path }
                    });
                }
            } else {
                // 使用浏览器 API 模拟
                const dirInput = document.createElement("input");
                dirInput.type = "file";
                dirInput.webkitdirectory = true;
                dirInput.directory = true;
                dirInput.style.display = "none";
                dirInput.addEventListener("change", (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        const path = file.path || file.webkitRelativePath.split("/")[0];
                        savePathInput.value = path;
                        downloadSettings.savePath = path;
                        saveDownloadSettings();
                    }
                });
                dirInput.click();
            }
        });
    }

    // 任务数选择
    const taskCountGroup = document.getElementById("taskCountGroup");
    if (taskCountGroup) {
        taskCountGroup.querySelectorAll(".task-count-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                taskCountGroup.querySelectorAll(".task-count-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                downloadSettings.taskCount = parseInt(btn.dataset.count);
                saveDownloadSettings();
            });
        });
    }
}

function saveDownloadSettings() {
    localStorage.setItem("downloadSettings", JSON.stringify(downloadSettings));
    
    // 同步到后端
    if (useRealBackend) {
        window.pywebview.api.save_config({
            download: {
                format: downloadSettings.format,
                savePath: downloadSettings.savePath,
                taskCount: downloadSettings.taskCount,
            }
        }).catch(e => console.warn("同步下载设置到后端失败:", e));
    }
}

async function loadDownloadSettings() {
    // 优先从后端加载
    if (useRealBackend) {
        try {
            const config = await window.pywebview.api.load_config();
            if (config && config.download) {
                Object.assign(downloadSettings, config.download);
                
                // 恢复 UI
                const formatSelect = document.getElementById("formatSelect");
                if (formatSelect) formatSelect.value = downloadSettings.format;
                
                const savePathInput = document.getElementById("savePathInput");
                if (savePathInput && downloadSettings.savePath) {
                    savePathInput.value = downloadSettings.savePath;
                }
                
                const taskCountGroup = document.getElementById("taskCountGroup");
                if (taskCountGroup) {
                    taskCountGroup.querySelectorAll(".task-count-btn").forEach(btn => {
                        btn.classList.toggle("active", parseInt(btn.dataset.count) === downloadSettings.taskCount);
                    });
                }
                return;
            }
        } catch (e) {
            console.warn("从后端加载下载设置失败:", e);
        }
    }
    
    // 降级到 localStorage
    const saved = localStorage.getItem("downloadSettings");
    if (saved) {
        try {
            const settings = JSON.parse(saved);
            Object.assign(downloadSettings, settings);
            
            const formatSelect = document.getElementById("formatSelect");
            if (formatSelect) formatSelect.value = downloadSettings.format;
            
            const savePathInput = document.getElementById("savePathInput");
            if (savePathInput && downloadSettings.savePath) {
                savePathInput.value = downloadSettings.savePath;
            }
            
            const taskCountGroup = document.getElementById("taskCountGroup");
            if (taskCountGroup) {
                taskCountGroup.querySelectorAll(".task-count-btn").forEach(btn => {
                    btn.classList.toggle("active", parseInt(btn.dataset.count) === downloadSettings.taskCount);
                });
            }
        } catch (e) {
            console.warn("无法加载下载设置:", e);
        }
    }
}

function bindLanguageTimeSettings() {
    // 界面语言切换
    const languageSelect = document.getElementById("languageSelect");
    if (languageSelect) {
        languageSelect.addEventListener("change", () => {
            languageTimeSettings.language = languageSelect.value;
            saveLanguageTimeSettings();
        });
    }

    // 时间格式切换
    const timeFormatGroup = document.getElementById("timeFormatGroup");
    if (timeFormatGroup) {
        timeFormatGroup.querySelectorAll(".time-format-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                timeFormatGroup.querySelectorAll(".time-format-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                languageTimeSettings.timeFormat = btn.dataset.format;
                saveLanguageTimeSettings();
            });
        });
    }

    // 日期顺序切换
    const dateFormatGroup = document.getElementById("dateFormatGroup");
    if (dateFormatGroup) {
        dateFormatGroup.querySelectorAll(".date-format-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                dateFormatGroup.querySelectorAll(".date-format-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                languageTimeSettings.dateFormat = btn.dataset.format;
                saveLanguageTimeSettings();
            });
        });
    }
}

function saveLanguageTimeSettings() {
    localStorage.setItem("languageTimeSettings", JSON.stringify(languageTimeSettings));
}

function loadLanguageTimeSettings() {
    const saved = localStorage.getItem("languageTimeSettings");
    if (saved) {
        try {
            const settings = JSON.parse(saved);
            Object.assign(languageTimeSettings, settings);
            
            // 恢复界面语言
            const languageSelect = document.getElementById("languageSelect");
            if (languageSelect) {
                languageSelect.value = languageTimeSettings.language;
            }

            // 恢复时间格式
            const timeFormatGroup = document.getElementById("timeFormatGroup");
            if (timeFormatGroup) {
                timeFormatGroup.querySelectorAll(".time-format-btn").forEach(btn => {
                    btn.classList.toggle("active", btn.dataset.format === languageTimeSettings.timeFormat);
                });
            }

            // 恢复日期顺序
            const dateFormatGroup = document.getElementById("dateFormatGroup");
            if (dateFormatGroup) {
                dateFormatGroup.querySelectorAll(".date-format-btn").forEach(btn => {
                    btn.classList.toggle("active", btn.dataset.format === languageTimeSettings.dateFormat);
                });
            }
        } catch (e) {
            console.warn("无法加载语言与时间设置:", e);
        }
    }
}

function bindNotificationSettings() {
    // 通知弹窗样式
    const notificationStyleGroup = document.getElementById("notificationStyleGroup");
    if (notificationStyleGroup) {
        notificationStyleGroup.querySelectorAll(".notification-style-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                notificationStyleGroup.querySelectorAll(".notification-style-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                notificationSettings.style = btn.dataset.style;
                saveNotificationSettings();
            });
        });
    }

    // 通知显示位置
    const notificationPositionGroup = document.getElementById("notificationPositionGroup");
    if (notificationPositionGroup) {
        notificationPositionGroup.querySelectorAll(".notification-position-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                notificationPositionGroup.querySelectorAll(".notification-position-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                notificationSettings.position = btn.dataset.position;
                saveNotificationSettings();
            });
        });
    }

    // 声音提示
    const soundToggle = document.getElementById("soundToggle");
    if (soundToggle) {
        soundToggle.addEventListener("change", () => {
            notificationSettings.sound = soundToggle.checked;
            saveNotificationSettings();
        });
    }

    // 振动提示
    const vibrationToggle = document.getElementById("vibrationToggle");
    if (vibrationToggle) {
        vibrationToggle.addEventListener("change", () => {
            notificationSettings.vibration = vibrationToggle.checked;
            saveNotificationSettings();
        });
    }

    // 预览内容
    const previewToggle = document.getElementById("previewToggle");
    if (previewToggle) {
        previewToggle.addEventListener("change", () => {
            notificationSettings.preview = previewToggle.checked;
            saveNotificationSettings();
        });
    }

    // 免打扰时段
    const dndToggle = document.getElementById("dndToggle");
    const dndTimeGroup = document.getElementById("dndTimeGroup");
    const dndStartTime = document.getElementById("dndStartTime");
    const dndEndTime = document.getElementById("dndEndTime");
    if (dndToggle) {
        dndToggle.addEventListener("change", () => {
            notificationSettings.dndEnabled = dndToggle.checked;
            if (dndTimeGroup) {
                dndTimeGroup.style.display = notificationSettings.dndEnabled ? "flex" : "none";
            }
            saveNotificationSettings();
        });
    }
    if (dndStartTime) {
        dndStartTime.addEventListener("change", () => {
            notificationSettings.dndStart = dndStartTime.value;
            saveNotificationSettings();
        });
    }
    if (dndEndTime) {
        dndEndTime.addEventListener("change", () => {
            notificationSettings.dndEnd = dndEndTime.value;
            saveNotificationSettings();
        });
    }
}

function applyThemeMode(mode) {
    const root = document.documentElement;
    if (mode === "dark") {
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
    } else if (mode === "light") {
        root.style.setProperty("--bg-primary", "#FDFBF7");
        root.style.setProperty("--bg-secondary", "#ffffff");
        root.style.setProperty("--bg-tertiary", "#d1d1d6");
        root.style.setProperty("--text-primary", "#1c1c1e");
        root.style.setProperty("--text-secondary", "#333333");
        root.style.setProperty("--border-color", "#d1d1d6");
        root.style.setProperty("--btn-bg", "#4a4a4e");
        root.style.setProperty("--btn-text", "#ffffff");
        root.style.setProperty("--btn-hover-bg", "#5a5a5e");
        root.style.setProperty("--font-weight-normal", "400");
        root.style.setProperty("--font-weight-medium", "400");
        root.style.setProperty("--font-weight-semibold", "400");
        root.style.setProperty("--title-color", "#1c1c1e");
    } else if (mode === "system") {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        applyThemeMode(prefersDark ? "dark" : "light");
        return;
    }
    
    // 同步到父窗口
    syncThemeToParent();
}

function applyAccentColor(color) {
    document.documentElement.style.setProperty("--accent-color", color);
    
    // 同步到父窗口
    syncThemeToParent();
}

function applyBackground() {
    const body = document.body;
    if (themeSettings.bgType === "solid") {
        body.style.background = "var(--bg-primary)";
        body.style.backgroundImage = "none";
    } else if (themeSettings.bgType === "image" && themeSettings.bgImage) {
        body.style.backgroundImage = `url(${themeSettings.bgImage})`;
        body.style.backgroundSize = "cover";
        body.style.backgroundPosition = "center";
    } else {
        body.style.background = "var(--bg-primary)";
        body.style.backgroundImage = "none";
    }
    
    // 同步到父窗口
    syncThemeToParent();
}

function syncThemeToParent() {
    try {
        if (window.parent && window.parent !== window) {
            window.parent.postMessage({
                type: "themeUpdate",
                theme: themeSettings
            }, "*");
        }
    } catch (e) {
        console.warn("无法同步主题到父窗口:", e);
    }
}

function adjustColor(hex, amount) {
    const num = parseInt(hex.slice(1), 16);
    const r = Math.min(255, Math.max(0, (num >> 16) + amount));
    const g = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + amount));
    const b = Math.min(255, Math.max(0, (num & 0x0000FF) + amount));
    return `#${(r << 16 | g << 8 | b).toString(16).padStart(6, "0")}`;
}

function saveThemeSettings() {
    try {
        localStorage.setItem("themeSettings", JSON.stringify(themeSettings));
        
        // 同步到后端
        if (useRealBackend) {
            window.pywebview.api.save_config({
                theme: {
                    mode: themeSettings.mode,
                    accentColor: themeSettings.accentColor,
                    bgType: themeSettings.bgType,
                    bgImage: themeSettings.bgImage,
                }
            }).catch(e => console.warn("同步主题设置到后端失败:", e));
        }
    } catch (e) {
        console.warn("无法保存主题设置:", e);
    }
}

async function loadThemeSettings() {
    // 优先从后端加载
    if (useRealBackend) {
        try {
            const config = await window.pywebview.api.load_config();
            if (config && config.theme) {
                Object.assign(themeSettings, config.theme);
                
                // 恢复 UI
                document.querySelectorAll(".theme-mode-btn").forEach(btn => {
                    btn.classList.toggle("active", btn.dataset.mode === themeSettings.mode);
                });
                document.querySelectorAll(".accent-color-btn").forEach(btn => {
                    if (!btn.classList.contains("custom-color")) {
                        btn.classList.toggle("active", btn.dataset.color === themeSettings.accentColor);
                    }
                });

                const bgTypeGroup = document.getElementById("bgTypeGroup");
                if (bgTypeGroup) {
                    bgTypeGroup.querySelectorAll(".bg-type-btn").forEach(btn => {
                        btn.classList.toggle("active", btn.dataset.type === themeSettings.bgType);
                    });
                }

                // 应用设置
                applyThemeMode(themeSettings.mode);
                applyAccentColor(themeSettings.accentColor);
                applyBackground();
                return;
            }
        } catch (e) {
            console.warn("从后端加载主题设置失败:", e);
        }
    }
    
    // 降级到 localStorage
    try {
        const saved = localStorage.getItem("themeSettings");
        if (saved) {
            const parsed = JSON.parse(saved);
            Object.assign(themeSettings, parsed);
            
            document.querySelectorAll(".theme-mode-btn").forEach(btn => {
                btn.classList.toggle("active", btn.dataset.mode === themeSettings.mode);
            });
            document.querySelectorAll(".accent-color-btn").forEach(btn => {
                if (!btn.classList.contains("custom-color")) {
                    btn.classList.toggle("active", btn.dataset.color === themeSettings.accentColor);
                }
            });

            const bgTypeGroup = document.getElementById("bgTypeGroup");
            if (bgTypeGroup) {
                bgTypeGroup.querySelectorAll(".bg-type-btn").forEach(btn => {
                    btn.classList.toggle("active", btn.dataset.type === themeSettings.bgType);
                });
            }

            applyThemeMode(themeSettings.mode);
            applyAccentColor(themeSettings.accentColor);
            applyBackground();
        }
    } catch (e) {
        console.warn("无法加载主题设置:", e);
    }
}

function saveNotificationSettings() {
    try {
        localStorage.setItem("notificationSettings", JSON.stringify(notificationSettings));
    } catch (e) {
        console.warn("无法保存通知设置:", e);
    }
}

function loadNotificationSettings() {
    try {
        const saved = localStorage.getItem("notificationSettings");
        if (saved) {
            const parsed = JSON.parse(saved);
            Object.assign(notificationSettings, parsed);
            
            // 恢复 UI 状态
            document.querySelectorAll(".notification-style-btn").forEach(btn => {
                btn.classList.toggle("active", btn.dataset.style === notificationSettings.style);
            });
            
            document.querySelectorAll(".notification-position-btn").forEach(btn => {
                btn.classList.toggle("active", btn.dataset.position === notificationSettings.position);
            });
            
            const soundToggle = document.getElementById("soundToggle");
            if (soundToggle) soundToggle.checked = notificationSettings.sound;
            
            const vibrationToggle = document.getElementById("vibrationToggle");
            if (vibrationToggle) vibrationToggle.checked = notificationSettings.vibration;
            
            const previewToggle = document.getElementById("previewToggle");
            if (previewToggle) previewToggle.checked = notificationSettings.preview;
            
            const dndToggle = document.getElementById("dndToggle");
            if (dndToggle) dndToggle.checked = notificationSettings.dndEnabled;
            
            const dndTimeGroup = document.getElementById("dndTimeGroup");
            if (dndTimeGroup) {
                dndTimeGroup.style.display = notificationSettings.dndEnabled ? "flex" : "none";
            }
            
            const dndStartTime = document.getElementById("dndStartTime");
            if (dndStartTime) dndStartTime.value = notificationSettings.dndStart;
            
            const dndEndTime = document.getElementById("dndEndTime");
            if (dndEndTime) dndEndTime.value = notificationSettings.dndEnd;
        }
    } catch (e) {
        console.warn("无法加载通知设置:", e);
    }
}

function loadThemeSettings() {
    try {
        const saved = localStorage.getItem("themeSettings");
        if (saved) {
            const parsed = JSON.parse(saved);
            Object.assign(themeSettings, parsed);
            
            // 恢复 UI 状态
            document.querySelectorAll(".theme-mode-btn").forEach(btn => {
                btn.classList.toggle("active", btn.dataset.mode === themeSettings.mode);
            });
            document.querySelectorAll(".accent-color-btn").forEach(btn => {
                if (!btn.classList.contains("custom-color")) {
                    btn.classList.toggle("active", btn.dataset.color === themeSettings.accentColor);
                }
            });

            const bgTypeGroup = document.getElementById("bgTypeGroup");
            if (bgTypeGroup) {
                bgTypeGroup.querySelectorAll(".bg-type-btn").forEach(btn => {
                    btn.classList.toggle("active", btn.dataset.type === themeSettings.bgType);
                });
            }

            // 应用设置
            applyThemeMode(themeSettings.mode);
            applyAccentColor(themeSettings.accentColor);
            applyBackground();
        }
    } catch (e) {
        console.warn("无法加载主题设置:", e);
    }
}

// 在页面加载时初始化主题设置
window.addEventListener("load", () => {
    loadThemeSettings();
    loadDownloadSettings();
    loadLanguageTimeSettings();
    loadNotificationSettings();
    bindAppearanceSettings();
    bindDownloadSettings();
    bindLanguageTimeSettings();
    bindNotificationSettings();
});