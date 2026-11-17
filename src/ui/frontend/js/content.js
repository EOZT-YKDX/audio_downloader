/* ============================================
   Audio Downloader - Content JavaScript (Animated)
   ============================================ */

document.addEventListener('DOMContentLoaded', async function() {
    // Wait for i18n to be initialized if not already
    if (window.i18n && !window.i18n.isInitialized) {
        const initialLocale = window.__INITIAL_SETTINGS__?.language || 'zh';
        await window.i18n.init(initialLocale);
    }
    initTaskList();
    initToolbar();
});

/* ============================================
   任务列表管理
   ============================================ */

let tasks = [];

function initTaskList() {
    loadTasks();
}

function initToolbar() {
    const btnStartAll = document.getElementById('btn-start-all');
    const btnPauseAll = document.getElementById('btn-pause-all');
    const btnDeleteAll = document.getElementById('btn-delete-all');
    
    if (btnStartAll) {
        btnStartAll.addEventListener('click', async function() {
            if (!window.pywebview || !window.pywebview.api) {
                console.error('API 不可用');
                return;
            }
            
            try {
                const pendingTasks = tasks.filter(t => t.status === 'pending' || t.status === 'paused');
                for (const task of pendingTasks) {
                    await window.pywebview.api.start_task(task.id);
                }
                loadTasks();
            } catch (e) {
                console.error('批量启动任务失败:', e);
                if (window.customModal && window.i18n) {
                    window.customModal.show({
                        title: window.i18n.t('modal.error_title'),
                        message: window.i18n.t('task_list.error.batch_start_failed'),
                        showCancel: false,
                        confirmText: window.i18n.t('add_task.buttons.ok')
                    }).catch(() => {});
                }
            }
        });
    }
    
    if (btnPauseAll) {
        btnPauseAll.addEventListener('click', async function() {
            if (!window.pywebview || !window.pywebview.api) {
                console.error('API 不可用');
                return;
            }
            
            try {
                const downloadingTasks = tasks.filter(t => t.status === 'downloading');
                for (const task of downloadingTasks) {
                    await window.pywebview.api.pause_task(task.id);
                }
                loadTasks();
            } catch (e) {
                console.error('批量暂停任务失败:', e);
                if (window.customModal && window.i18n) {
                    window.customModal.show({
                        title: window.i18n.t('modal.error_title'),
                        message: window.i18n.t('task_list.error.batch_pause_failed'),
                        showCancel: false,
                        confirmText: window.i18n.t('add_task.buttons.ok')
                    }).catch(() => {});
                }
            }
        });
    }
    
    if (btnDeleteAll) {
        btnDeleteAll.addEventListener('click', async function() {
            if (!window.pywebview || !window.pywebview.api || tasks.length === 0) {
                return;
            }
            
            try {
                const confirmed = await window.customModal.show({
                    title: window.i18n.t('modal.delete.title'),
                    message: window.i18n.t('modal.delete.message'),
                    confirmText: window.i18n.t('modal.delete.confirm'),
                    cancelText: window.i18n.t('modal.delete.cancel')
                });
                
                if (confirmed) {
                    for (const task of tasks) {
                        await window.pywebview.api.delete_task(task.id);
                    }
                    loadTasks();
                }
            } catch (e) {
                console.error('批量删除任务失败:', e);
                if (window.customModal && window.i18n) {
                    window.customModal.show({
                        title: window.i18n.t('modal.error_title'),
                        message: window.i18n.t('task_list.error.batch_delete_failed'),
                        showCancel: false,
                        confirmText: window.i18n.t('add_task.buttons.ok')
                    }).catch(() => {});
                }
            }
        });
    }
}

async function loadTasks() {
    if (window.pywebview && window.pywebview.api) {
        try {
            tasks = await window.pywebview.api.get_tasks();
            renderTasks();
        } catch (e) {
            console.error('加载任务列表失败:', e);
        }
    }
}

// 存储所有待清理的 timeout ID 和 interval ID
let pendingTimeouts = new Set();
let pendingIntervals = new Set();

function safeSetTimeout(callback, delay) {
    const timeoutId = setTimeout(() => {
        callback();
        pendingTimeouts.delete(timeoutId);
    }, delay);
    pendingTimeouts.add(timeoutId);
    return timeoutId;
}

function safeClearTimeout(timeoutId) {
    if (timeoutId !== undefined && timeoutId !== null) {
        clearTimeout(timeoutId);
        pendingTimeouts.delete(timeoutId);
    }
}

function safeSetInterval(callback, interval) {
    const intervalId = setInterval(callback, interval);
    pendingIntervals.add(intervalId);
    return intervalId;
}

function safeClearInterval(intervalId) {
    if (intervalId !== undefined && intervalId !== null) {
        clearInterval(intervalId);
        pendingIntervals.delete(intervalId);
    }
}

function renderTasks() {
    const taskList = document.getElementById('taskList');
    const topBar = document.getElementById('topBar');
    const emptyTip = document.getElementById('emptyTip');
    
    if (!tasks || tasks.length === 0) {
        taskList.innerHTML = '';
        topBar.classList.remove('show');
        emptyTip.style.display = 'block';
        if (window.i18n) {
            emptyTip.textContent = window.i18n.t('task_list.empty');
        }
        return;
    }
    
    topBar.classList.add('show');
    emptyTip.style.display = 'none';
    
    // Get existing task IDs
    const existingIds = new Set();
    taskList.querySelectorAll('.task-item').forEach(el => {
        existingIds.add(el.dataset.id);
    });
    
    // Remove tasks that no longer exist (with animation)
    taskList.querySelectorAll('.task-item').forEach(el => {
        if (!tasks.find(t => t.id === el.dataset.id)) {
            el.classList.add('remove');
            el.classList.remove('show');
            const timeoutId = safeSetTimeout(() => {
                if (el.parentNode) {
                    el.remove();
                }
            }, 320);
        }
    });
    
    // Update or add tasks
    tasks.forEach((task, index) => {
        let taskEl = taskList.querySelector(`.task-item[data-id="${task.id}"]`);
        
        if (taskEl) {
            // Update existing task
            updateTaskElement(taskEl, task);
        } else {
            // Create new task with animation
            taskEl = createTaskElement(task);
            taskList.appendChild(taskEl);
            // Trigger animation with slight delay
            requestAnimationFrame(() => {
                const timeoutId = safeSetTimeout(() => {
                    taskEl.classList.add('show');
                }, index * 50);
            });
        }
    });
}

function createTaskElement(task) {
    const div = document.createElement('div');
    div.className = 'task-item';
    div.dataset.id = task.id;
    div.innerHTML = getTaskHTML(task);
    return div;
}

function updateTaskElement(el, task) {
    el.innerHTML = getTaskHTML(task);
}

function getTaskHTML(task) {
    const progressPercent = task.progress || 0;
    const speed = task.speed ? formatSpeed(task.speed) : '';
    const progress = task.progress !== undefined ? `${task.progress.toFixed(1)}%` : '';
    const size = task.size ? formatSize(task.size) : '';
    
    const infoParts = [speed, progress, size].filter(Boolean);
    const infoText = infoParts.join(' | ');
    
    return `
        <div class="task-header">
            <div class="task-name">${task.name}</div>
            <div class="task-actions">
                ${task.status === 'downloading' ? `
                <button class="action-btn" onclick="pauseTask('${task.id}')" title="${window.i18n.t('task_list.actions.pause')}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="6" y="4" width="4" height="16"/>
                        <rect x="14" y="4" width="4" height="16"/>
                    </svg>
                </button>
                ` : ''}
                ${task.status === 'paused' ? `
                <button class="action-btn" onclick="pauseTask('${task.id}')" title="${window.i18n.t('task_list.actions.resume')}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="5 3 19 12 5 21 5 3"/>
                    </svg>
                </button>
                ` : ''}
                <button class="action-btn danger" onclick="deleteTask('${task.id}')" title="${window.i18n.t('task_list.actions.delete')}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                </button>
            </div>
        </div>
        <div class="task-progress-section">
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progressPercent}%"></div>
            </div>
        </div>
        <div class="task-footer">
            <div class="task-info-text">${infoText}</div>
        </div>
    `;
}

function formatSpeed(bytesPerSecond) {
    if (!bytesPerSecond || bytesPerSecond === 0) return '';
    if (bytesPerSecond < 1024) {
        return bytesPerSecond + ' ' + window.i18n.t('units.b_s');
    } else if (bytesPerSecond < 1024 * 1024) {
        return (bytesPerSecond / 1024).toFixed(0) + ' ' + window.i18n.t('units.kb_s');
    } else {
        return (bytesPerSecond / (1024 * 1024)).toFixed(1) + ' ' + window.i18n.t('units.mb_s');
    }
}

function formatSize(bytes) {
    if (!bytes) return '';
    if (bytes < 1024) {
        return bytes + ' ' + window.i18n.t('units.b');
    } else if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(0) + ' ' + window.i18n.t('units.kb');
    } else if (bytes < 1024 * 1024 * 1024) {
        return (bytes / (1024 * 1024)).toFixed(0) + ' ' + window.i18n.t('units.mb');
    } else {
        return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' ' + window.i18n.t('units.gb');
    }
}

function getStatusText(status) {
    return window.i18n.t(`task_list.status.${status}`);
}

async function pauseTask(taskId) {
    if (!window.pywebview || !window.pywebview.api) {
        console.error('API 不可用');
        return;
    }
    
    try {
        await window.pywebview.api.pause_task(taskId);
        loadTasks();
    } catch (e) {
        console.error('暂停任务失败:', e);
        if (window.customModal && window.i18n) {
            window.customModal.show({
                title: window.i18n.t('modal.error_title'),
                message: window.i18n.t('task_list.error.pause_failed'),
                showCancel: false,
                confirmText: window.i18n.t('add_task.buttons.ok')
            }).catch(() => {});
        }
    }
}

async function deleteTask(taskId) {
    if (!window.pywebview || !window.pywebview.api) {
        console.error('API 不可用');
        return;
    }
    
    try {
        // Animate removal
        const taskEl = document.querySelector(`.task-item[data-id="${taskId}"]`);
        if (taskEl) {
            taskEl.classList.add('remove');
            taskEl.classList.remove('show');
            safeSetTimeout(() => {
                if (taskEl.parentNode) {
                    taskEl.remove();
                }
            }, 320);
        }
        
        await window.pywebview.api.delete_task(taskId);
        loadTasks();
    } catch (e) {
        console.error('删除任务失败:', e);
        if (window.customModal && window.i18n) {
            window.customModal.show({
                title: window.i18n.t('modal.error_title'),
                message: window.i18n.t('task_list.error.delete_failed'),
                showCancel: false,
                confirmText: window.i18n.t('add_task.buttons.ok')
            }).catch(() => {});
        }
    }
}

/* ============================================
   实时更新
   ============================================ */

let updateInterval = null;

function startAutoUpdate() {
    if (updateInterval) return;
    
    updateInterval = safeSetInterval(async function() {
        if (window.pywebview && window.pywebview.api) {
            try {
                const updatedTasks = await window.pywebview.api.get_tasks();
                if (updatedTasks && updatedTasks.length > 0) {
                    const hasChanges = checkTaskChanges(updatedTasks);
                    if (hasChanges) {
                        tasks = updatedTasks;
                        renderTasks();
                    }
                } else if (tasks && tasks.length > 0) {
                    tasks = [];
                    renderTasks();
                }
            } catch (e) {
                console.error('更新任务状态失败:', e);
            }
        }
    }, 1000);
}

function stopAutoUpdate() {
    if (updateInterval) {
        safeClearInterval(updateInterval);
        updateInterval = null;
    }
}

function checkTaskChanges(newTasks) {
    if (!tasks || tasks.length !== newTasks.length) return true;
    
    for (let i = 0; i < newTasks.length; i++) {
        if (tasks[i].status !== newTasks[i].status ||
            tasks[i].progress !== newTasks[i].progress ||
            tasks[i].completed !== newTasks[i].completed) {
            return true;
        }
    }
    return false;
}

function updateTaskProgress(taskId, progress, status) {
    const taskItem = document.querySelector(`.task-item[data-id="${taskId}"]`);
    if (!taskItem) return;
    
    const progressFill = taskItem.querySelector('.progress-fill');
    const infoText = taskItem.querySelector('.task-info-text');
    
    if (progressFill) progressFill.style.width = progress + '%';
    if (infoText) {
        const task = tasks.find(t => t.id === taskId);
        if (task) {
            const speed = task.speed ? formatSpeed(task.speed) : '';
            const progressStr = task.progress !== undefined ? `${task.progress.toFixed(1)}%` : '';
            const size = task.size ? formatSize(task.size) : '';
            const infoParts = [speed, progressStr, size].filter(Boolean);
            infoText.textContent = infoParts.join(' | ');
        }
    }
}

/* ============================================
   页面切换监听 - 启动/停止自动更新
   ============================================ */

let sidebarEventListeners = [];

document.addEventListener('DOMContentLoaded', function() {
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    
    sidebarItems.forEach(item => {
        const handler = function() {
            const page = this.dataset.page;
            
            if (page === 'download') {
                startAutoUpdate();
            } else {
                stopAutoUpdate();
            }
        };
        
        item.addEventListener('click', handler);
        sidebarEventListeners.push({ element: item, handler });
    });
    
    // 初始检查是否在下载页面
    const activePage = document.querySelector('.sidebar-item.active');
    if (activePage && activePage.dataset.page === 'download') {
        startAutoUpdate();
    }
});

/* ============================================
   清理资源 - 防止内存泄漏
   ============================================ */

function cleanupAllResources() {
    // 停止自动更新
    stopAutoUpdate();
    
    // 清理所有 pending timeouts
    pendingTimeouts.forEach(timeoutId => clearTimeout(timeoutId));
    pendingTimeouts.clear();
    
    // 清理所有 pending intervals
    pendingIntervals.forEach(intervalId => clearInterval(intervalId));
    pendingIntervals.clear();
    
    // 清理侧边栏事件监听器
    sidebarEventListeners.forEach(({ element, handler }) => {
        element.removeEventListener('click', handler);
    });
    sidebarEventListeners = [];
    
    // 清理任务列表 DOM
    const taskList = document.getElementById('taskList');
    if (taskList) {
        taskList.innerHTML = '';
    }
    
    // 清理任务数据
    tasks = [];
    
    // 清理所有任务元素
    document.querySelectorAll('.task-item').forEach(el => {
        el.remove();
    });
    
    console.log('Content 资源已清理');
}

// 监听窗口关闭事件
window.addEventListener('beforeunload', function() {
    cleanupAllResources();
});

// 导出清理函数供外部调用
window.cleanupContentResources = cleanupAllResources;