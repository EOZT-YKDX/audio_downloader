/* ============================================
   Audio Downloader - Frame JavaScript
   ============================================ */

/* ============================================
   FID Validation State
   ============================================ */
let fidValidationState = 'none'; // 'none', 'validating', 'valid', 'invalid'

/* ============================================
   统一错误处理工具
   ============================================ */

const ErrorHandler = {
    /**
     * 安全执行异步 API 调用
     * @param {Function} apiCall - API 调用函数
     * @param {Object} options - 配置选项
     * @param {string} options.errorMessage - 错误消息
     * @param {boolean} options.showErrorModal - 是否显示错误弹窗
     * @param {Function} options.onError - 自定义错误处理回调
     * @returns {Promise<any>} API 调用结果
     */
    async safeCall(apiCall, options = {}) {
        const {
            errorMessage = '操作失败',
            showErrorModal = false,
            onError = null
        } = options;

        try {
            // 检查 pywebview API 是否可用
            if (!window.pywebview || !window.pywebview.api) {
                throw new Error('API 不可用');
            }

            const result = await apiCall();
            return result;
        } catch (error) {
            console.error(`${errorMessage}:`, error);

            // 执行自定义错误处理
            if (onError) {
                onError(error);
            }

            // 显示错误弹窗
            if (showErrorModal && window.customModal && window.i18n) {
                const translatedError = window.i18n.translateBackendError(error.message);
                window.customModal.show({
                    title: window.i18n.t('modal.error_title'),
                    message: `${errorMessage}: ${translatedError}`,
                    showCancel: false,
                    confirmText: window.i18n.t('add_task.buttons.ok')
                }).catch(() => {});
            }

            return null;
        }
    },

    /**
     * 安全执行批量 API 调用
     * @param {Array} items - 项目列表
     * @param {Function} apiCall - API 调用函数，接收 item 作为参数
     * @param {Object} options - 配置选项
     * @returns {Promise<Array>} 成功的项目列表
     */
    async safeBatchCall(items, apiCall, options = {}) {
        const {
            errorMessage = '批量操作失败',
            onError = null,
            stopOnError = false
        } = options;

        const results = [];
        const errors = [];

        for (const item of items) {
            try {
                if (!window.pywebview || !window.pywebview.api) {
                    throw new Error('API 不可用');
                }

                const result = await apiCall(item);
                results.push({ item, result, success: true });
            } catch (error) {
                console.error(`${errorMessage}:`, error);
                errors.push({ item, error });

                if (onError) {
                    onError(item, error);
                }

                if (stopOnError) {
                    break;
                }
            }
        }

        return { results, errors };
    }
};

/* ============================================
   自定义弹窗组件
   ============================================ */

class CustomModal {
    constructor() {
        this.overlay = document.getElementById('customModal');
        this.titleEl = document.getElementById('customModalTitle');
        this.messageEl = document.getElementById('customModalMessage');
        this.inputEl = document.getElementById('customModalInput');
        this.confirmBtn = document.getElementById('customModalConfirm');
        this.cancelBtn = document.getElementById('customModalCancel');
        this.closeBtn = document.getElementById('customModalClose');
        this.resolve = null;
        this.audioContext = null;
        this.eventHandlers = {};
        this.init();
    }

    init() {
        // 存储事件处理器以便后续清理
        this.eventHandlers.close = () => this.close(null);
        this.eventHandlers.cancel = () => this.close(null);
        this.eventHandlers.confirm = () => this.confirm();
        this.eventHandlers.overlayClick = (e) => {
            if (e.target === this.overlay) this.close(null);
        };
        this.eventHandlers.keydown = (e) => {
            if (e.key === 'Escape' && this.overlay.classList.contains('show')) {
                this.close(null);
            }
            if (e.key === 'Enter' && this.overlay.classList.contains('show')) {
                this.confirm();
            }
        };

        this.closeBtn.addEventListener('click', this.eventHandlers.close);
        this.cancelBtn.addEventListener('click', this.eventHandlers.cancel);
        this.confirmBtn.addEventListener('click', this.eventHandlers.confirm);
        this.overlay.addEventListener('click', this.eventHandlers.overlayClick);
        document.addEventListener('keydown', this.eventHandlers.keydown);
    }

    cleanup() {
        // 移除所有事件监听器
        if (this.closeBtn) this.closeBtn.removeEventListener('click', this.eventHandlers.close);
        if (this.cancelBtn) this.cancelBtn.removeEventListener('click', this.eventHandlers.cancel);
        if (this.confirmBtn) this.confirmBtn.removeEventListener('click', this.eventHandlers.confirm);
        if (this.overlay) this.overlay.removeEventListener('click', this.eventHandlers.overlayClick);
        document.removeEventListener('keydown', this.eventHandlers.keydown);

        // 关闭 AudioContext
        if (this.audioContext) {
            try {
                this.audioContext.close();
            } catch (e) {
                console.warn('关闭 AudioContext 失败:', e);
            }
            this.audioContext = null;
        }

        // 清理 resolve 引用
        this.resolve = null;
    }

    isDndActive() {
        if (!window.pywebview || !window.pywebview.api) return false;
        
        const dndMode = document.getElementById('dnd-mode');
        if (!dndMode || !dndMode.checked) return false;
        
        const dndStart = document.getElementById('dnd-start');
        const dndEnd = document.getElementById('dnd-end');
        if (!dndStart || !dndEnd) return false;
        
        const now = new Date();
        const currentMinutes = now.getHours() * 60 + now.getMinutes();
        
        const [startH, startM] = dndStart.value.split(':').map(Number);
        const [endH, endM] = dndEnd.value.split(':').map(Number);
        const startMinutes = startH * 60 + startM;
        const endMinutes = endH * 60 + endM;
        
        if (startMinutes <= endMinutes) {
            return currentMinutes >= startMinutes && currentMinutes <= endMinutes;
        } else {
            return currentMinutes >= startMinutes || currentMinutes <= endMinutes;
        }
    }

    playNotifySound() {
        if (this.isDndActive()) return;
        
        const soundNotify = document.getElementById('sound-notify');
        if (!soundNotify || !soundNotify.checked) return;
        
        try {
            if (!this.audioContext || this.audioContext.state === 'closed') {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            const now = this.audioContext.currentTime;
            
            const playTone = (freq, startTime, endTime, volume = 0.15) => {
                const oscillator = this.audioContext.createOscillator();
                const gainNode = this.audioContext.createGain();
                
                oscillator.type = 'sine';
                oscillator.connect(gainNode);
                gainNode.connect(this.audioContext.destination);
                
                oscillator.frequency.setValueAtTime(freq, startTime);
                
                gainNode.gain.setValueAtTime(0, startTime);
                gainNode.gain.linearRampToValueAtTime(volume, startTime + 0.01);
                gainNode.gain.setValueAtTime(volume, endTime - 0.02);
                gainNode.gain.linearRampToValueAtTime(0, endTime);
                
                oscillator.start(startTime);
                oscillator.stop(endTime);
                
                // 确保 oscillator 在播放完成后被清理
                oscillator.onended = () => {
                    oscillator.disconnect();
                    gainNode.disconnect();
                };
            };
            
            playTone(523.25, now, now + 0.08);
            playTone(659.25, now + 0.06, now + 0.14);
            playTone(783.99, now + 0.12, now + 0.22);
            playTone(1046.50, now + 0.18, now + 0.35, 0.12);
        } catch (e) {
            console.warn('播放提示音失败:', e);
        }
    }

    getNotifyStyle() {
        const styleBtn = document.querySelector('.notification-style-btn.active');
        return styleBtn ? styleBtn.dataset.style : 'banner';
    }

    getNotifyPosition() {
        const posBtn = document.querySelector('.notification-position-btn.active');
        return posBtn ? posBtn.dataset.position : 'corner';
    }

    applyModalStyle() {
        const style = this.getNotifyStyle();
        const position = this.getNotifyPosition();
        
        this.overlay.classList.remove('modal-banner', 'modal-silent', 'modal-badge');
        this.overlay.classList.remove('modal-top', 'modal-bottom', 'modal-corner', 'modal-center');
        
        this.overlay.classList.add(`modal-${style}`);
        this.overlay.classList.add(`modal-${position}`);
        
        const modal = this.overlay.querySelector('.custom-modal');
        if (modal) {
            modal.style.position = '';
            modal.style.top = '';
            modal.style.bottom = '';
            modal.style.left = '';
            modal.style.right = '';
            modal.style.width = '';
            modal.style.maxWidth = '';
            modal.style.borderRadius = '';
            
            if (style === 'banner') {
                modal.style.position = 'absolute';
                modal.style.width = '90%';
                modal.style.maxWidth = '600px';
                modal.style.borderRadius = '0 0 12px 12px';
                
                if (position === 'center') {
                    modal.style.top = '50%';
                    modal.style.left = '50%';
                    modal.style.transform = 'translate(-50%, -50%)';
                } else {
                    modal.style.top = '0';
                    modal.style.right = '0';
                    modal.style.left = 'auto';
                    modal.style.transform = 'none';
                }
            } else if (style === 'silent') {
                modal.style.position = 'absolute';
                modal.style.width = 'auto';
                modal.style.minWidth = '200px';
                modal.style.maxWidth = '300px';
                modal.style.borderRadius = '8px';
                modal.style.opacity = '0.85';
                
                if (position === 'center') {
                    modal.style.top = '50%';
                    modal.style.left = '50%';
                    modal.style.transform = 'translate(-50%, -50%)';
                } else {
                    modal.style.bottom = '10px';
                    modal.style.right = '10px';
                    modal.style.transform = 'none';
                }
            } else if (style === 'badge') {
                modal.style.position = 'absolute';
                modal.style.width = 'auto';
                modal.style.minWidth = '160px';
                modal.style.maxWidth = '240px';
                modal.style.borderRadius = '8px';
                
                if (position === 'center') {
                    modal.style.top = '50%';
                    modal.style.left = '50%';
                    modal.style.transform = 'translate(-50%, -50%)';
                } else {
                    modal.style.bottom = '10px';
                    modal.style.right = '10px';
                    modal.style.transform = 'none';
                }
            }
        }
    }

    show(options = {}) {
        const {
            title = '提示',
            message = '',
            input = false,
            defaultValue = '',
            placeholder = '',
            confirmText = '确定',
            cancelText = '取消',
            showCancel = true,
            notify = true
        } = options;

        this.titleEl.textContent = title;
        
        const previewContent = document.getElementById('preview-content');
        const showDetail = previewContent ? previewContent.checked : true;
        
        if (showDetail) {
            this.messageEl.textContent = message;
        } else {
            this.messageEl.textContent = title || '通知';
        }
        
        this.confirmBtn.textContent = confirmText;
        this.cancelBtn.textContent = cancelText;
        this.cancelBtn.style.display = showCancel ? 'block' : 'none';

        if (input) {
            this.inputEl.style.display = 'block';
            this.inputEl.value = defaultValue;
            this.inputEl.placeholder = placeholder;
            setTimeout(() => this.inputEl.focus(), 100);
        } else {
            this.inputEl.style.display = 'none';
        }

        this.applyModalStyle();
        this.overlay.classList.add('show');

        const style = this.getNotifyStyle();
        if (notify && style !== 'silent') {
            this.playNotifySound();
        }

        return new Promise((resolve) => {
            this.resolve = resolve;
        });
    }

    confirm() {
        const value = this.inputEl.style.display !== 'none' ? this.inputEl.value : true;
        this.close(value);
    }

    close(value) {
        this.overlay.classList.remove('show');
        if (this.resolve) {
            this.resolve(value);
            this.resolve = null;
        }
    }
}

window.customModal = new CustomModal();

document.addEventListener('DOMContentLoaded', async function() {
    // Initialize i18n first
    const initialLocale = window.__INITIAL_SETTINGS__?.language || 'zh';
    await window.i18n.init(initialLocale);
    
    initDragWindow();
    initWindowControls();
    initSidebar();
    initDownloadTypeSwitcher();
    initConflictButtons();
    initThemeModeButtons();
    initSystemThemeWatcher();
    initBgTypeButtons();
    initBgImageButtons();
    initColorPicker();
    initToggleSwitches();
    initBrowseButton();
    initTaskCountButtons();
    initCompressTaskCountButtons();
    initTimeFormatButtons();
    initDateFormatButtons();
    initNotificationStyleButtons();
    initNotificationPositionButtons();
    initActionButtons();
    initSelectChanges();
    loadSettings();
});

/* ============================================
   窗口拖拽功能（仅标题栏和侧边栏）
   ============================================ */

let dragEventHandlers = {};

function initDragWindow() {
    const dragBar = document.getElementById('dragBar');
    const sidebar = document.querySelector('.sidebar');
    
    if (!dragBar && !sidebar) return;

    let isDragging = false;
    let startMouseX, startMouseY;
    let startWindowX, startWindowY;

    async function startDrag(e) {
        // 排除按钮和交互元素
        if (e.target.closest('.min-btn, .close-btn, .sidebar-item, button, a, input, select, textarea')) return;
        
        isDragging = true;
        startMouseX = e.screenX;
        startMouseY = e.screenY;
        
        // 获取窗口当前绝对位置
        if (window.pywebview && window.pywebview.api) {
            try {
                const pos = await window.pywebview.api.get_window_position();
                startWindowX = pos.x;
                startWindowY = pos.y;
            } catch (e) {
                console.error('获取窗口位置失败:', e);
                isDragging = false;
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
                return;
            }
        }
        
        document.body.style.cursor = 'move';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    }

    function onDrag(e) {
        if (!isDragging) return;
        
        // 计算鼠标移动的绝对差值
        const deltaX = e.screenX - startMouseX;
        const deltaY = e.screenY - startMouseY;
        
        // 只有移动距离超过阈值才触发拖动
        if (Math.abs(deltaX) > 2 || Math.abs(deltaY) > 2) {
            if (window.pywebview && window.pywebview.api) {
                try {
                    // 使用起始位置 + 差值计算新位置
                    window.pywebview.api.move_window(startWindowX + deltaX, startWindowY + deltaY);
                } catch (e) {
                    console.error('移动窗口失败:', e);
                }
            }
        }
    }

    function stopDrag() {
        if (!isDragging) return;
        isDragging = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
    }

    // 存储事件处理器引用
    dragEventHandlers = {
        dragBar,
        sidebar,
        startDrag,
        onDrag,
        stopDrag
    };

    if (dragBar) {
        dragBar.addEventListener('mousedown', startDrag);
    }

    if (sidebar) {
        sidebar.addEventListener('mousedown', startDrag);
    }

    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', stopDrag);
}

function cleanupDragWindow() {
    if (dragEventHandlers.dragBar) {
        dragEventHandlers.dragBar.removeEventListener('mousedown', dragEventHandlers.startDrag);
    }
    if (dragEventHandlers.sidebar) {
        dragEventHandlers.sidebar.removeEventListener('mousedown', dragEventHandlers.startDrag);
    }
    document.removeEventListener('mousemove', dragEventHandlers.onDrag);
    document.removeEventListener('mouseup', dragEventHandlers.stopDrag);
    dragEventHandlers = {};
}

/* ============================================
   窗口控制按钮（最小化/关闭）
   ============================================ */

function initWindowControls() {
    const minBtn = document.getElementById('minBtn');
    const closeBtn = document.getElementById('closeBtn');

    if (minBtn) {
        minBtn.addEventListener('click', function() {
            if (window.pywebview && window.pywebview.api) {
                try {
                    window.pywebview.api.minimize();
                } catch (e) {
                    console.error('最小化窗口失败:', e);
                }
            }
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            try {
                if (window.pywebview && window.pywebview.api) {
                    window.pywebview.api.close();
                } else {
                    window.close();
                }
            } catch (e) {
                console.error('关闭窗口失败:', e);
                // 强制关闭
                window.close();
            }
        });
    }
}

/* ============================================
   侧边栏导航
   ============================================ */

function initSidebar() {
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    
    sidebarItems.forEach(item => {
        item.addEventListener('click', function() {
            const page = this.dataset.page;
            
            sidebarItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
            const targetPage = document.getElementById('page-' + page);
            if (targetPage) {
                targetPage.style.display = 'block';
            }
        });
    });
}

/* ============================================
   下载类型切换器
   ============================================ */

function initDownloadTypeSwitcher() {
    const switcher = document.getElementById('downloadTypeSwitcher');
    if (!switcher) return;
    
    const typeBtns = switcher.querySelectorAll('.type-btn');
    const linkInputArea = document.getElementById('linkInputArea');
    const favoritesInputArea = document.getElementById('favoritesInputArea');
    const linkInput = document.getElementById('linkInput');
    const parseResultText = document.getElementById('parseResultText');
    const favoritesIdInput = document.getElementById('favoritesIdInput');
    const favoritesParseResult = document.getElementById('favoritesParseResult');
    
    typeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            typeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const type = this.dataset.type;
            
            if (type === 'link-download') {
                if (linkInputArea) linkInputArea.style.display = 'flex';
                if (favoritesInputArea) favoritesInputArea.style.display = 'none';
            } else if (type === 'fav-download') {
                if (linkInputArea) linkInputArea.style.display = 'none';
                if (favoritesInputArea) favoritesInputArea.style.display = 'flex';
            }
        });
    });
    
    // 链接输入监听 - 停止输入后自动检测并解析
    if (linkInput && parseResultText) {
        let parseTimeout;
        const linkInputHandler = function() {
            const arr = this.value.trim().split('\n').filter(i => i.trim());
            
            if (parseTimeout) {
                clearTimeout(parseTimeout);
            }
            
            if (arr.length === 0) {
                parseResultText.textContent = window.i18n.t('add_task.link.empty');
                parseResultText.className = 'result-empty';
                return;
            }
            
            parseResultText.textContent = window.i18n.t('add_task.link.detecting');
            parseResultText.className = 'result-empty';
            
            parseTimeout = setTimeout(() => {
                const isBilibili = url => url.includes('bilibili.com') || url.includes('b23.tv') || /^BV\w{10}$/.test(url);
                const hasBilibili = arr.some(isBilibili);
                
                if (hasBilibili) {
                    parseBilibiliLinks(arr);
                } else {
                    renderLinkValidation(arr);
                }
            }, 500);
        };
        
        linkInput.addEventListener('input', linkInputHandler);
        window._linkInputHandler = linkInputHandler;
    }
    
    if (favoritesIdInput && favoritesParseResult) {
        let favParseTimeout;
        const favoritesInputHandler = function() {
            const fid = this.value.trim();
            const favoritesParseText = document.getElementById('favoritesParseText');
            
            if (favParseTimeout) {
                clearTimeout(favParseTimeout);
            }
            
            if (!fid || !/^\d+$/.test(fid)) {
                favoritesParseText.textContent = window.i18n.t('add_task.favorite.empty');
                favoritesParseText.className = 'result-empty';
                setFidValidationState('none', '');
                fidValidationState = 'none';
                const refreshBtn = document.getElementById('refreshFavoritesBtn');
                if (refreshBtn) refreshBtn.style.display = 'none';
                return;
            }
            
            setFidValidationState('validating', '');
            fidValidationState = 'validating';
            
            favParseTimeout = setTimeout(() => parseFavorites(fid), 500);
        };
        
        favoritesIdInput.addEventListener('input', favoritesInputHandler);
        window._favoritesInputHandler = favoritesInputHandler;
    }
    
    const refreshBtn = document.getElementById('refreshFavoritesBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async function() {
            const fidInput = document.getElementById('favoritesIdInput');
            const fid = fidInput ? fidInput.value.trim() : '';
            if (!fid || !/^\d+$/.test(fid)) return;
            
            refreshBtn.classList.add('spinning');
            refreshBtn.disabled = true;
            
            setFidValidationState('validating', window.i18n.t('add_task.favorite.parsing'));
            fidValidationState = 'validating';
            
            try {
                await parseFavorites(fid);
            } finally {
                refreshBtn.classList.remove('spinning');
                refreshBtn.disabled = false;
            }
        });
    }
}

/**
 * Set FID validation status display
 */
function setFidValidationState(state, message) {
    const statusEl = document.getElementById('fidValidationStatus');
    if (!statusEl) return;
    
    const iconEl = statusEl.querySelector('.fid-status-icon');
    const textEl = statusEl.querySelector('.fid-status-text');
    
    statusEl.className = 'fid-validation-status';
    
    if (state === 'none') {
        statusEl.style.display = 'none';
        return;
    }
    
    statusEl.style.display = 'flex';
    statusEl.classList.add(state);
    
    if (state === 'validating') {
        textEl.textContent = window.i18n.t('add_task.favorite.parsing');
    } else if (state === 'valid') {
        textEl.textContent = message || window.i18n.t('add_task.favorite.valid');
    } else if (state === 'invalid') {
        textEl.textContent = message || window.i18n.t('add_task.favorite.invalid');
    }
}

/* ============================================
   B站链接解析
   ============================================ */

async function parseBilibiliLinks(urls) {
    const parseResultText = document.getElementById('parseResultText');
    if (!parseResultText) return;

    parseResultText.textContent = window.i18n.t('parse.parsing');
    parseResultText.className = 'result-empty';

    if (window.pywebview && window.pywebview.api) {
        try {
            const result = await window.pywebview.api.parse_bilibili_links(urls);
            if (result && result.success && result.results) {
                const { uniqueResults, duplicateBvids } = filterDuplicateBvids(result.results);
                renderParseResults(uniqueResults, duplicateBvids);
            } else {
                parseResultText.textContent = result?.error || window.i18n.t('parse.failed');
                parseResultText.className = 'result-empty';
            }
        } catch (e) {
            console.error('B站解析失败:', e);
            parseResultText.textContent = window.i18n.t('parse.error', { error: e.message });
            parseResultText.className = 'result-empty';
        }
    } else {
        const mockResults = urls.map(url => ({
            url: url,
            type: 'video',
            bvid: /^BV\w{10}$/.test(url) ? url : 'BV1xx411c7mD',
            title: '模拟视频标题',
            author: '模拟作者',
            duration: '03:25',
            view: '12.3万',
            danmaku: '1234',
            reply: '567',
            pubdate: '2024-01-15',
        }));
        const { uniqueResults, duplicateBvids } = filterDuplicateBvids(mockResults);
        renderParseResults(uniqueResults, duplicateBvids);
    }
}

function filterDuplicateBvids(results) {
    const seenBvids = new Map();
    const uniqueResults = [];
    const duplicateBvids = [];

    for (const item of results) {
        if (item.error) {
            uniqueResults.push(item);
            continue;
        }

        const bvid = item.bvid;
        if (!bvid) {
            uniqueResults.push(item);
            continue;
        }

        if (seenBvids.has(bvid)) {
            if (!duplicateBvids.includes(bvid)) {
                duplicateBvids.push(bvid);
            }
        } else {
            seenBvids.set(bvid, true);
            uniqueResults.push(item);
        }
    }

    return { uniqueResults, duplicateBvids };
}

function renderParseResults(results, duplicateBvids = []) {
    const parseResultText = document.getElementById('parseResultText');
    if (!parseResultText) return;

    if (results.length === 0) {
        parseResultText.textContent = window.i18n.t('add_task.link.empty');
        parseResultText.className = 'result-empty';
        return;
    }

    let html = '';

    if (duplicateBvids.length > 0) {
        html += `
            <div class="parse-warning">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <span>${window.i18n.t('add_task.link.duplicate_warning', { count: duplicateBvids.length })}</span>
            </div>
        `;
    }

    parseResultText.className = 'parse-list';
    html += results.map(item => {
        if (item.error) {
            return `
                <div class="parse-item error">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="15" y1="9" x2="9" y2="15"/>
                        <line x1="9" y1="9" x2="15" y2="15"/>
                    </svg>
                    <div class="parse-item-content">
                        <div class="parse-item-title">${escapeHtml(item.url)}</div>
                        <div class="parse-item-error">${escapeHtml(item.error)}</div>
                    </div>
                </div>
            `;
        }

        return `
            <div class="parse-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19.1c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.43z"/>
                    <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/>
                </svg>
                <div class="parse-item-content">
                    <div class="parse-item-title">${escapeHtml(item.title)}</div>
                    <div class="parse-item-meta">
                        <span class="parse-item-author">${escapeHtml(item.author)}</span>
                        <span class="parse-item-separator">·</span>
                        <span class="parse-item-duration">${escapeHtml(item.duration)}</span>
                    </div>
                    <div class="parse-item-stats">
                        <span>👁 ${escapeHtml(item.view)}</span>
                        <span>💬 ${escapeHtml(item.danmaku)}</span>
                        <span>📝 ${escapeHtml(item.reply)}</span>
                        <span>📅 ${escapeHtml(item.pubdate)}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    parseResultText.innerHTML = html;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/* ============================================
   链接验证渲染
   ============================================ */

function renderLinkValidation(urls) {
    const parseResultText = document.getElementById('parseResultText');
    if (!parseResultText) return;

    if (urls.length === 0) {
        parseResultText.textContent = window.i18n.t('add_task.link.empty');
        parseResultText.className = 'result-empty';
        return;
    }

    parseResultText.className = 'parse-list';
    parseResultText.innerHTML = urls.map(url => {
        const isValid = isValidUrl(url);
        return `
            <div class="parse-item ${isValid ? '' : 'error'}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    ${isValid 
                        ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>'
                        : '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>'
                    }
                </svg>
                <div class="parse-item-content">
                    <div class="parse-item-title">${escapeHtml(url)}</div>
                    <div class="parse-item-error">${isValid ? window.i18n.t('add_task.link.valid') : window.i18n.t('add_task.link.invalid')}</div>
                </div>
            </div>
        `;
    }).join('');
}

function isValidUrl(url) {
    if (!url || !url.trim()) return false;
    try {
        const u = new URL(url);
        return ['http:', 'https:', 'ftp:'].includes(u.protocol);
    } catch {
        return false;
    }
}

/* ============================================
   收藏夹解析
   ============================================ */

async function parseFavorites(fid) {
    const favoritesParseText = document.getElementById('favoritesParseText');
    const refreshBtn = document.getElementById('refreshFavoritesBtn');
    if (!favoritesParseText) return;

    if (window.pywebview && window.pywebview.api) {
        try {
            const result = await window.pywebview.api.parse_bilibili_favorites(fid);
            if (result && result.success && result.result) {
                const mediaCount = result.result.media_count || 0;
                const hasMediaList = result.result.media_list && result.result.media_list.length > 0;
                
                if (mediaCount === 0 || !hasMediaList) {
                    fidValidationState = 'invalid';
                    setFidValidationState('invalid', window.i18n.t('add_task.favorite.empty'));
                    renderFavoritesResults(result.result);
                    if (refreshBtn) refreshBtn.style.display = 'none';
                } else {
                    fidValidationState = 'valid';
                    setFidValidationState('valid', window.i18n.t('add_task.favorite.total_videos', { count: mediaCount }));
                    renderFavoritesResults(result.result);
                    if (refreshBtn) refreshBtn.style.display = 'flex';
                }
            } else {
                fidValidationState = 'invalid';
                setFidValidationState('invalid', result?.error || window.i18n.t('parse.failed'));
                favoritesParseText.textContent = result?.error || window.i18n.t('parse.failed');
                favoritesParseText.className = 'result-empty';
                if (refreshBtn) refreshBtn.style.display = 'none';
            }
        } catch (e) {
            console.error('收藏夹解析失败:', e);
            fidValidationState = 'invalid';
            setFidValidationState('invalid', window.i18n.t('parse.error', { error: e.message }));
            favoritesParseText.textContent = window.i18n.t('parse.error', { error: e.message });
            favoritesParseText.className = 'result-empty';
            if (refreshBtn) refreshBtn.style.display = 'none';
        }
    } else {
        fidValidationState = 'valid';
        setFidValidationState('valid', window.i18n.t('add_task.favorite.total_videos', { count: 5 }));
        renderFavoritesResults({
            fid: fid,
            title: '模拟收藏夹',
            upper_name: '模拟用户',
            media_count: 5,
            display_count: 5,
            media_list: [
                { bvid: 'BV1xx411c7mD', title: '模拟视频1', author: '模拟作者', duration: '03:25', view: '12.3万', pubdate: '2024-01-15' },
                { bvid: 'BV1xx411c7mE', title: '模拟视频2', author: '模拟作者', duration: '05:10', view: '8.5万', pubdate: '2024-02-20' },
            ],
        });
        if (refreshBtn) refreshBtn.style.display = 'flex';
    }
}

function renderFavoritesResults(data) {
    const favoritesParseText = document.getElementById('favoritesParseText');
    if (!favoritesParseText) return;

    if (!data || !data.media_list || data.media_list.length === 0) {
        favoritesParseText.textContent = window.i18n.t('add_task.favorite.total_videos', { count: data?.media_count || 0 });
        favoritesParseText.className = 'result-empty';
        return;
    }

    favoritesParseText.className = 'parse-list';
    
    let html = `
        <div class="parse-item fav-header">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
            </svg>
            <div class="parse-item-content">
                <div class="parse-item-title">${escapeHtml(data.title)}</div>
                <div class="parse-item-meta">
                    <span class="parse-item-author">${escapeHtml(data.upper_name)}</span>
                    <span class="parse-item-separator">·</span>
                    <span>${window.i18n.t('add_task.favorite.total_videos', { count: data.media_count })}</span>
                    ${data.display_count < data.media_count ? `<span class="parse-item-separator">·</span><span>${window.i18n.t('add_task.favorite.showing', { count: data.display_count })}</span>` : ''}
                </div>
            </div>
        </div>
    `;
    
    html += data.media_list.map(item => `
        <div class="parse-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19.1c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.43z"/>
                <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/>
            </svg>
            <div class="parse-item-content">
                <div class="parse-item-title">${escapeHtml(item.title)}</div>
                <div class="parse-item-meta">
                    <span class="parse-item-author">${escapeHtml(item.author)}</span>
                    <span class="parse-item-separator">·</span>
                    <span class="parse-item-duration">${escapeHtml(item.duration)}</span>
                </div>
                <div class="parse-item-stats">
                    <span>👁 ${escapeHtml(item.view)}</span>
                    <span>📅 ${escapeHtml(item.pubdate)}</span>
                </div>
            </div>
        </div>
    `).join('');
    
    favoritesParseText.innerHTML = html;
}

/* ============================================
   冲突处理按钮组
   ============================================ */

function initConflictButtons() {
    const conflictGroup = document.getElementById('conflictGroup');
    if (!conflictGroup) return;
    
    const buttons = conflictGroup.querySelectorAll('.conflict-btn');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

/* ============================================
   主题模式按钮组
   ============================================ */

function initThemeModeButtons() {
    const themeModeGroup = document.getElementById('themeModeGroup');
    if (!themeModeGroup) return;
    
    const buttons = themeModeGroup.querySelectorAll('.theme-mode-btn');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const mode = this.dataset.mode;
            applyThemeMode(mode);
            autoSaveSettings();
        });
    });
}

/* ============================================
   主题管理系统
   ============================================ */

// 主题配置映射
const THEME_CONFIG = {
    dark: {
        stylesheetId: 'theme-stylesheet-dark',
        label: '深色',
        isDark: true
    },
    light: {
        stylesheetId: 'theme-stylesheet-light',
        label: '浅色',
        isDark: false
    }
};

// 当前主题状态
let currentTheme = 'dark';

/**
 * 应用主题模式
 * @param {string} mode - 主题模式：'light' | 'dark' | 'system'
 */
function applyThemeMode(mode) {
    let targetTheme = mode;
    
    // 处理系统主题
    if (mode === 'system') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        targetTheme = prefersDark ? 'dark' : 'light';
    }
    
    // 如果主题未改变，直接返回
    if (targetTheme === currentTheme) return;
    
    // 切换主题
    switchTheme(targetTheme);
}

/**
 * 切换主题
 * @param {string} themeName - 主题名称：'light' | 'dark'
 */
function switchTheme(themeName) {
    const config = THEME_CONFIG[themeName];
    if (!config) {
        console.error(`主题 "${themeName}" 不存在`);
        return;
    }
    
    // 获取所有主题样式表
    const darkStylesheet = document.getElementById('theme-stylesheet-dark');
    const lightStylesheet = document.getElementById('theme-stylesheet-light');
    
    if (!darkStylesheet || !lightStylesheet) {
        console.error('主题样式表未找到');
        return;
    }
    
    // 使用 disabled 属性切换主题，避免重新加载 CSS
    if (themeName === 'dark') {
        darkStylesheet.disabled = false;
        lightStylesheet.disabled = true;
    } else {
        darkStylesheet.disabled = true;
        lightStylesheet.disabled = false;
    }
    
    // 更新当前主题状态
    currentTheme = themeName;
    
    // 更新 body 的 data-theme 属性（用于 CSS 选择器）
    document.body.setAttribute('data-theme', themeName);
    
    console.log(`主题已切换至: ${config.label}`);
}

/**
 * 获取当前主题
 * @returns {string} 当前主题名称
 */
function getCurrentTheme() {
    return currentTheme;
}

/**
 * 监听系统主题变化
 */
function initSystemThemeWatcher() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    mediaQuery.addEventListener('change', (e) => {
        // 仅在 system 模式下响应系统主题变化
        const themeModeBtn = document.querySelector('.theme-mode-btn.active');
        if (themeModeBtn && themeModeBtn.dataset.mode === 'system') {
            const newTheme = e.matches ? 'dark' : 'light';
            switchTheme(newTheme);
        }
    });
}

/* ============================================
   背景类型按钮组
   ============================================ */

function initBgTypeButtons() {
    const bgTypeGroup = document.getElementById('bgTypeGroup');
    if (!bgTypeGroup) return;
    
    const buttons = bgTypeGroup.querySelectorAll('.bg-type-btn');
    const bgImageItem = document.getElementById('bgImageItem');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const bgType = this.dataset.type;
            if (bgType === 'image' && bgImageItem) {
                bgImageItem.style.display = 'flex';
                // 切换到图片模式时，如果已保存过图片则恢复显示
                if (window.__bgImageData__) {
                    const bgImagePreview = document.getElementById('bgImagePreview');
                    if (bgImagePreview) {
                        bgImagePreview.style.backgroundImage = `url(${window.__bgImageData__})`;
                    }
                    document.body.style.backgroundImage = `url(${window.__bgImageData__})`;
                    document.body.style.backgroundSize = 'cover';
                    document.body.style.backgroundPosition = 'center';
                } else if (window.__bgImagePath__ && window.pywebview && window.pywebview.api) {
                    // 如果有路径但没有缓存数据，从后端获取
                    window.pywebview.api.get_bg_image_data(window.__bgImagePath__)
                        .then(function(result) {
                            if (result && result.data) {
                                window.__bgImageData__ = result.data;
                                const bgImagePreview = document.getElementById('bgImagePreview');
                                if (bgImagePreview) {
                                    bgImagePreview.style.backgroundImage = `url(${result.data})`;
                                }
                                document.body.style.backgroundImage = `url(${result.data})`;
                                document.body.style.backgroundSize = 'cover';
                                document.body.style.backgroundPosition = 'center';
                            }
                        })
                        .catch(function(e) {
                            console.error('加载背景图片失败:', e);
                        });
                }
            } else if (bgImageItem) {
                bgImageItem.style.display = 'none';
                // 选择纯色时，清除背景图片显示，但保留路径和数据以便恢复
                document.body.style.backgroundImage = '';
                document.body.style.backgroundSize = '';
                document.body.style.backgroundPosition = '';
                const bgImagePreview = document.getElementById('bgImagePreview');
                if (bgImagePreview) {
                    bgImagePreview.style.backgroundImage = '';
                }
            }
            
            autoSaveSettings();
        });
    });
}

/* ============================================
   背景图片按钮
   ============================================ */

function initBgImageButtons() {
    const bgImageBtn = document.getElementById('bgImageBtn');
    const bgImageInput = document.getElementById('bgImageInput');
    const bgImagePreview = document.getElementById('bgImagePreview');
    
    if (!bgImageBtn || !bgImageInput) return;
    
    bgImageBtn.addEventListener('click', async function() {
        if (!window.pywebview || !window.pywebview.api) {
            bgImageInput.click();
            return;
        }
        
        try {
            const currentPath = window.__bgImagePath__ || '';
            const result = await window.pywebview.api.select_image(currentPath);
            if (result && result.path) {
                window.__bgImagePath__ = result.path;
                window.__bgImageData__ = result.data;
                if (bgImagePreview) {
                    bgImagePreview.style.backgroundImage = `url(${result.data})`;
                }
                document.body.style.backgroundImage = `url(${result.data})`;
                document.body.style.backgroundSize = 'cover';
                document.body.style.backgroundPosition = 'center';
                autoSaveSettings();
            }
        } catch (e) {
            console.error('选择图片失败:', e);
            if (window.customModal && window.i18n) {
                window.customModal.show({
                    title: window.i18n.t('modal.error_title'),
                    message: window.i18n.t('settings.error.select_image_failed'),
                    showCancel: false,
                    confirmText: window.i18n.t('add_task.buttons.ok')
                }).catch(() => {});
            }
        }
    });
    
    bgImageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(event) {
            if (bgImagePreview) {
                bgImagePreview.style.backgroundImage = `url(${event.target.result})`;
            }
            document.body.style.backgroundImage = `url(${event.target.result})`;
            document.body.style.backgroundSize = 'cover';
            document.body.style.backgroundPosition = 'center';
            autoSaveSettings();
        };
        reader.readAsDataURL(file);
    });
}

/* ============================================
   颜色选择器
   ============================================ */

function initColorPicker() {
    const colorOptions = document.querySelectorAll('.color-option:not(.add-color)');
    
    colorOptions.forEach(option => {
        option.addEventListener('click', function() {
            colorOptions.forEach(o => o.classList.remove('active'));
            this.classList.add('active');
            
            const color = this.dataset.color;
            document.documentElement.style.setProperty('--primary-color', color);
            autoSaveSettings();
        });
    });
    
    // 自定义颜色按钮
    const customColorBtn = document.getElementById('customColorBtn');
    const customColorPicker = document.getElementById('customColorPicker');
    
    if (customColorBtn && customColorPicker) {
        customColorBtn.addEventListener('click', function() {
            customColorPicker.click();
        });
        
        customColorPicker.addEventListener('change', function() {
            const color = this.value;
            colorOptions.forEach(o => o.classList.remove('active'));
            customColorBtn.classList.add('active');
            document.documentElement.style.setProperty('--primary-color', color);
            autoSaveSettings();
        });
    }
}

/* ============================================
   开关切换
   ============================================ */

function initToggleSwitches() {
    const toggles = document.querySelectorAll('.toggle-switch input');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            // 免打扰模式特殊处理：显示/隐藏时间段
            if (this.id === 'dnd-mode') {
                const timeRange = document.getElementById('dndTimeRange');
                if (timeRange) {
                    timeRange.classList.toggle('show', this.checked);
                }
            }
            autoSaveSettings();
        });
    });
    
    // 免打扰时间段输入变化时自动保存
    const dndStart = document.getElementById('dnd-start');
    const dndEnd = document.getElementById('dnd-end');
    if (dndStart) dndStart.addEventListener('change', autoSaveSettings);
    if (dndEnd) dndEnd.addEventListener('change', autoSaveSettings);
}

/* ============================================
   浏览按钮
   ============================================ */

function initBrowseButton() {
    const savePathBtn = document.getElementById('savePathBtn');
    const savePathInput = document.getElementById('savePathInput');
    
    if (savePathBtn) {
        savePathBtn.addEventListener('click', async function() {
            if (!window.pywebview || !window.pywebview.api) {
                console.error('API 不可用');
                return;
            }
            
            try {
                const currentPath = document.getElementById('savePathInput').value;
                const path = await window.pywebview.api.select_folder(currentPath);
                if (path) {
                    document.getElementById('savePathInput').value = path;
                    autoSaveSettings();
                }
            } catch (e) {
                console.error('选择文件夹失败:', e);
                if (window.customModal && window.i18n) {
                    window.customModal.show({
                        title: window.i18n.t('modal.error_title'),
                        message: window.i18n.t('settings.error.select_folder_failed'),
                        showCancel: false,
                        confirmText: window.i18n.t('add_task.buttons.ok')
                    }).catch(() => {});
                }
            }
        });
    }
}

/* ============================================
   同时下载任务数按钮组
   ============================================ */

function initTaskCountButtons() {
    const taskCountGroup = document.getElementById('taskCountGroup');
    if (!taskCountGroup) return;
    
    const buttons = taskCountGroup.querySelectorAll('.task-count-btn');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            autoSaveSettings();
        });
    });
}

function initCompressTaskCountButtons() {
    const compressTaskCountGroup = document.getElementById('compressTaskCountGroup');
    if (!compressTaskCountGroup) return;
    
    const buttons = compressTaskCountGroup.querySelectorAll('.task-count-btn');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            autoSaveSettings();
        });
    });
}

/* ============================================
   时间格式按钮组
   ============================================ */

function initTimeFormatButtons() {
    const timeFormatGroup = document.getElementById('timeFormatGroup');
    if (!timeFormatGroup) return;
    
    const buttons = timeFormatGroup.querySelectorAll('.time-format-btn');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            autoSaveSettings();
        });
    });
}

/* ============================================
   日期顺序按钮组
   ============================================ */

function initDateFormatButtons() {
    const dateFormatGroup = document.getElementById('dateFormatGroup');
    if (!dateFormatGroup) return;
    
    const buttons = dateFormatGroup.querySelectorAll('.date-format-btn');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            autoSaveSettings();
        });
    });
}

/* ============================================
   通知样式按钮组
   ============================================ */

function initNotificationStyleButtons() {
    const notificationStyleGroup = document.getElementById('notificationStyleGroup');
    if (!notificationStyleGroup) return;
    
    const buttons = notificationStyleGroup.querySelectorAll('.notification-style-btn');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            autoSaveSettings();
        });
    });
}

/* ============================================
   通知位置按钮组
   ============================================ */

function initNotificationPositionButtons() {
    const notificationPositionGroup = document.getElementById('notificationPositionGroup');
    if (!notificationPositionGroup) return;
    
    const buttons = notificationPositionGroup.querySelectorAll('.notification-position-btn');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            autoSaveSettings();
        });
    });
}

/* ============================================
   操作按钮
   ============================================ */

function initActionButtons() {
    const btnOk = document.getElementById('btn-ok');
    const btnCancel = document.getElementById('btn-cancel');
    
    if (btnOk) {
        btnOk.addEventListener('click', async function() {
            await handleStartDownload();
        });
    }
    
    if (btnCancel) {
        btnCancel.addEventListener('click', function() {
            document.querySelector('[data-page="download"]').click();
        });
    }

    // 恢复默认设置
    const resetItem = document.getElementById('resetSettingItem');
    if (resetItem) {
        resetItem.style.cursor = 'pointer';
        resetItem.addEventListener('click', async function() {
            const confirmed = await window.customModal.show({
                title: window.i18n.t('settings.reset.confirm_title'),
                message: window.i18n.t('settings.reset.confirm_message'),
                confirmText: window.i18n.t('settings.reset.confirm_btn'),
                cancelText: window.i18n.t('settings.reset.cancel_btn')
            });
            if (confirmed) {
                if (window.pywebview && window.pywebview.api) {
                    const result = await window.pywebview.api.reset_settings();
                    if (result && result.success) {
                        loadSettings(true);
                        await window.customModal.show({
                            title: window.i18n.t('settings.reset.success_title'),
                            message: window.i18n.t('settings.reset.success_message'),
                            showCancel: false,
                            confirmText: window.i18n.t('settings.reset.ok_btn')
                        });
                    } else {
                        await window.customModal.show({
                            title: window.i18n.t('settings.reset.error_title'),
                            message: window.i18n.t('settings.reset.error_message', { error: result?.error || window.i18n.t('modal.unknown_error') }),
                            showCancel: false,
                            confirmText: window.i18n.t('settings.reset.ok_btn')
                        });
                    }
                }
            }
        });
    }
}

/* ============================================
   开始下载处理
   ============================================ */

async function handleStartDownload() {
    const activeTypeBtn = document.querySelector('.type-btn.active');
    const isLinkDownload = activeTypeBtn?.dataset.type === 'link-download';
    
    let links = [];
    let fid = '';
    
    if (isLinkDownload) {
        const linkInput = document.getElementById('linkInput');
        const text = linkInput.value.trim();
        if (!text) {
            await window.customModal.show({
                title: window.i18n.t('modal.title'),
                message: window.i18n.t('add_task.validation.enter_link'),
                showCancel: false,
                confirmText: window.i18n.t('add_task.buttons.ok')
            });
            return;
        }
        links = text.split('\n').filter(l => l.trim());
    } else {
        const fidInput = document.getElementById('favoritesIdInput');
        fid = fidInput.value.trim();
        if (!fid) {
            await window.customModal.show({
                title: window.i18n.t('modal.title'),
                message: window.i18n.t('add_task.validation.enter_fid'),
                showCancel: false,
                confirmText: window.i18n.t('add_task.buttons.ok')
            });
            return;
        }
        
        // Check FID validation state
        if (fidValidationState !== 'valid') {
            const fidStatusEl = document.getElementById('fidValidationStatus');
            const statusText = fidStatusEl?.querySelector('.fid-status-text')?.textContent;
            await window.customModal.show({
                title: window.i18n.t('modal.error_title'),
                message: statusText || window.i18n.t('add_task.validation.fid_format_error'),
                showCancel: false,
                confirmText: window.i18n.t('add_task.buttons.ok')
            });
            return;
        }
    }
    
    const taskName = document.getElementById('task-name').value || '下载任务';
    const speedLimit = document.getElementById('speed-limit').value;
    const conflictAction = document.querySelector('#conflictGroup .conflict-btn.active')?.dataset.value || 'skip';
    const savePath = document.getElementById('savePathInput').value;
    
    const taskData = {
        type: isLinkDownload ? 'link' : 'favorite',
        links: links,
        fid: fid,
        taskName: taskName,
        speedLimit: parseInt(speedLimit),
        conflictAction: conflictAction,
        savePath: savePath
    };
    
    if (window.pywebview && window.pywebview.api) {
        const result = await window.pywebview.api.start_download(taskData);
        if (result && result.success) {
            document.querySelector('[data-page="download"]').click();
        } else {
            const translatedError = window.i18n ? window.i18n.translateBackendError(result?.error) : (result?.error || '未知错误');
            await window.customModal.show({
                title: window.i18n.t('modal.error_title'),
                message: window.i18n.t('add_task.validation.add_failed', { error: translatedError }),
                showCancel: false,
                confirmText: window.i18n.t('add_task.buttons.ok')
            });
        }
    } else {
        console.log('Task data:', taskData);
        document.querySelector('[data-page="download"]').click();
    }
}

/* ============================================
   下拉框变更
   ============================================ */

function initSelectChanges() {
    const selects = document.querySelectorAll('.setting-select');
    
    selects.forEach(select => {
        select.addEventListener('change', function() {
            autoSaveSettings();
        });
    });
    
    // Language select special handler
    const languageSelect = document.getElementById('language');
    if (languageSelect) {
        languageSelect.addEventListener('change', async function() {
            try {
                const newLocale = this.value;
                await window.i18n.loadLocale(newLocale);
                window.i18n.applyTranslations();
                autoSaveSettings();
            } catch (e) {
                console.error('切换语言失败:', e);
            }
        });
    }
}

/* ============================================
   自动保存设置
   ============================================ */

async function autoSaveSettings() {
    const settings = collectSettings();
    
    if (window.pywebview && window.pywebview.api) {
        try {
            await window.pywebview.api.save_settings(settings);
        } catch (e) {
            console.error('保存设置失败:', e);
        }
    }
}

function collectSettings() {
    const settings = {};
    
    // 主题模式 - 通过 theme-mode-btn 查找
    const themeModeBtn = document.querySelector('.theme-mode-btn.active');
    if (themeModeBtn) settings.themeMode = themeModeBtn.dataset.mode;
    
    // 背景类型 - 通过 bg-type-btn 查找
    const bgTypeBtn = document.querySelector('.bg-type-btn.active');
    if (bgTypeBtn) settings.bgType = bgTypeBtn.dataset.type;
    
    // 背景图片路径
    settings.bgImagePath = window.__bgImagePath__ || '';
    
    // 背景图片数据 (base64)
    settings.bgImageData = window.__bgImageData__ || '';
    
    // 主题色
    const activeColor = document.querySelector('.color-option.active:not(.add-color)');
    const customColorBtn = document.getElementById('customColorBtn');
    const customColorPicker = document.getElementById('customColorPicker');
    
    if (customColorBtn && customColorBtn.classList.contains('active') && customColorPicker) {
        settings.themeColor = customColorPicker.value;
    } else if (activeColor) {
        settings.themeColor = activeColor.dataset.color;
    }
    
    // 输出格式
    const outputFormat = document.getElementById('formatSelect');
    if (outputFormat) settings.outputFormat = outputFormat.value;
    
    // 保存路径
    const savePath = document.getElementById('savePathInput');
    if (savePath) settings.savePath = savePath.value;
    
    // 并发任务数
    const concurrentBtn = document.querySelector('.task-count-btn.active');
    if (concurrentBtn) settings.concurrentTasks = parseInt(concurrentBtn.dataset.count);
    
    // 并发压缩任务数
    const compressConcurrentBtn = document.querySelector('#compressTaskCountGroup .task-count-btn.active');
    if (compressConcurrentBtn) settings.concurrentCompressTasks = parseInt(compressConcurrentBtn.dataset.count);
    
    // 语言
    const language = document.getElementById('language');
    if (language) settings.language = language.value;
    
    // 时间格式
    const timeFormatBtn = document.querySelector('.time-format-btn.active');
    if (timeFormatBtn) settings.timeFormat = timeFormatBtn.dataset.format;
    
    // 日期顺序
    const dateFormatBtn = document.querySelector('.date-format-btn.active');
    if (dateFormatBtn) settings.dateFormat = dateFormatBtn.dataset.format;
    
    // 通知样式
    const notifyStyleBtn = document.querySelector('.notification-style-btn.active');
    if (notifyStyleBtn) settings.notifyStyle = notifyStyleBtn.dataset.style;
    
    // 通知位置
    const notifyPosBtn = document.querySelector('.notification-position-btn.active');
    if (notifyPosBtn) settings.notifyPosition = notifyPosBtn.dataset.position;
    
    // 开关
    const soundNotify = document.getElementById('sound-notify');
    if (soundNotify) settings.soundNotify = soundNotify.checked;
    
    const previewContent = document.getElementById('preview-content');
    if (previewContent) settings.previewContent = previewContent.checked;
    
    const dndMode = document.getElementById('dnd-mode');
    if (dndMode) settings.dndMode = dndMode.checked;
    
    const dndStart = document.getElementById('dnd-start');
    if (dndStart) settings.dndStart = dndStart.value;
    
    const dndEnd = document.getElementById('dnd-end');
    if (dndEnd) settings.dndEnd = dndEnd.value;
    
    return settings;
}

/* ============================================
   加载设置
   ============================================ */

async function loadSettings(forceReload = false) {
    // 强制重新加载时，清除初始设置缓存和背景图片缓存
    if (forceReload) {
        window.__INITIAL_SETTINGS__ = null;
        window.__bgImagePath__ = '';
        window.__bgImageData__ = '';
    }
    
    // 优先使用后端注入的初始设置（窗口创建前已注入）
    if (window.__INITIAL_SETTINGS__) {
        console.log('使用注入的初始设置:', window.__INITIAL_SETTINGS__);
        applySettings(window.__INITIAL_SETTINGS__);
        return;
    }
    
    // 降级方案：等待 pywebview API 就绪后获取
    let retries = 0;
    const maxRetries = 10;
    
    while (retries < maxRetries) {
        if (window.pywebview && window.pywebview.api) {
            break;
        }
        await new Promise(resolve => setTimeout(resolve, 200));
        retries++;
    }
    
    if (window.pywebview && window.pywebview.api) {
        try {
            const settings = await window.pywebview.api.get_settings();
            console.log('通过 API 加载的设置:', settings);
            applySettings(settings);
        } catch (e) {
            console.error('加载设置失败:', e);
        }
    } else {
        console.warn('pywebview API 未就绪，使用默认设置');
    }
}

function applySettings(settings) {
    if (!settings) return;
    
    // 应用主题模式
    if (settings.themeMode) {
        document.querySelectorAll('.theme-mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === settings.themeMode);
        });
        applyThemeMode(settings.themeMode);
    }
    
    // 应用背景类型
    if (settings.bgType) {
        document.querySelectorAll('.bg-type-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.type === settings.bgType);
        });
        const bgImageItem = document.getElementById('bgImageItem');
        if (bgImageItem) {
            bgImageItem.style.display = settings.bgType === 'image' ? 'flex' : 'none';
        }
    }
    
    // 应用背景图片（始终加载缓存数据，但仅在图片模式下应用显示）
    if (settings.bgImagePath) {
        window.__bgImagePath__ = settings.bgImagePath;
        
        // 优先使用缓存的 base64 数据
        if (settings.bgImageData) {
            window.__bgImageData__ = settings.bgImageData;
        }
        
        // 仅当背景类型为图片时才应用显示
        if (settings.bgType === 'image') {
            const bgImagePreview = document.getElementById('bgImagePreview');
            
            if (window.__bgImageData__) {
                if (bgImagePreview) {
                    bgImagePreview.style.backgroundImage = `url(${window.__bgImageData__})`;
                }
                document.body.style.backgroundImage = `url(${window.__bgImageData__})`;
                document.body.style.backgroundSize = 'cover';
                document.body.style.backgroundPosition = 'center';
            } else if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.get_bg_image_data(settings.bgImagePath).then(function(result) {
                    if (result && result.data) {
                        window.__bgImageData__ = result.data;
                        if (bgImagePreview) {
                            bgImagePreview.style.backgroundImage = `url(${result.data})`;
                        }
                        document.body.style.backgroundImage = `url(${result.data})`;
                        document.body.style.backgroundSize = 'cover';
                        document.body.style.backgroundPosition = 'center';
                    }
                }).catch(function(e) {
                    console.error('加载背景图片失败:', e);
                });
            }
        }
    } else {
        // 没有背景图片路径时，清除所有缓存和显示
        window.__bgImagePath__ = '';
        window.__bgImageData__ = '';
        const bgImagePreview = document.getElementById('bgImagePreview');
        if (bgImagePreview) {
            bgImagePreview.style.backgroundImage = '';
        }
        document.body.style.backgroundImage = '';
        document.body.style.backgroundSize = '';
        document.body.style.backgroundPosition = '';
    }
    
    // 应用主题色
    if (settings.themeColor) {
        document.documentElement.style.setProperty('--primary-color', settings.themeColor);
        const presetColors = ['#007aff', '#5856d6', '#ff2d55', '#ff9500', '#34c759', '#af52de'];
        const isCustomColor = !presetColors.includes(settings.themeColor);
        
        document.querySelectorAll('.color-option').forEach(opt => {
            opt.classList.toggle('active', opt.dataset.color === settings.themeColor);
        });
        
        const customColorBtn = document.getElementById('customColorBtn');
        const customColorPicker = document.getElementById('customColorPicker');
        if (customColorBtn && customColorPicker) {
            customColorBtn.classList.toggle('active', isCustomColor);
            if (isCustomColor) {
                customColorPicker.value = settings.themeColor;
            }
        }
    }
    
    // 应用输出格式
    if (settings.outputFormat) {
        const formatEl = document.getElementById('formatSelect');
        if (formatEl) formatEl.value = settings.outputFormat;
    }
    
    // 应用保存路径
    const savePathEl = document.getElementById('savePathInput');
    if (savePathEl && settings.savePath !== undefined) {
        savePathEl.value = settings.savePath || '';
    }
    
    // 应用并发任务数
    if (settings.concurrentTasks !== undefined) {
        document.querySelectorAll('.task-count-btn').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.count) === settings.concurrentTasks);
        });
    }
    
    // 应用并发压缩任务数
    if (settings.concurrentCompressTasks !== undefined) {
        document.querySelectorAll('#compressTaskCountGroup .task-count-btn').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.count) === settings.concurrentCompressTasks);
        });
    }
    
    // 应用语言
    if (settings.language) {
        const languageEl = document.getElementById('language');
        if (languageEl) languageEl.value = settings.language;
        
        // 应用 i18n 翻译
        if (window.i18n && window.i18n.getLocale() !== settings.language) {
            window.i18n.loadLocale(settings.language).then(() => {
                window.i18n.applyTranslations();
            });
        }
    }
    
    // 应用时间格式
    if (settings.timeFormat) {
        document.querySelectorAll('.time-format-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.format === settings.timeFormat);
        });
    }
    
    // 应用日期顺序
    if (settings.dateFormat) {
        document.querySelectorAll('.date-format-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.format === settings.dateFormat);
        });
    }
    
    // 应用通知样式
    if (settings.notifyStyle) {
        document.querySelectorAll('.notification-style-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.style === settings.notifyStyle);
        });
    }
    
    // 应用通知位置
    if (settings.notifyPosition) {
        document.querySelectorAll('.notification-position-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.position === settings.notifyPosition);
        });
    }
    
    // 应用开关状态
    if (settings.soundNotify !== undefined) {
        const el = document.getElementById('sound-notify');
        if (el) el.checked = settings.soundNotify;
    }
    if (settings.previewContent !== undefined) {
        const el = document.getElementById('preview-content');
        if (el) el.checked = settings.previewContent;
    }
    if (settings.dndMode !== undefined) {
        const el = document.getElementById('dnd-mode');
        if (el) {
            el.checked = settings.dndMode;
            const timeRange = document.getElementById('dndTimeRange');
            if (timeRange) {
                timeRange.classList.toggle('show', settings.dndMode);
            }
        }
    }
    if (settings.dndStart !== undefined) {
        const el = document.getElementById('dnd-start');
        if (el) el.value = settings.dndStart;
    }
    if (settings.dndEnd !== undefined) {
        const el = document.getElementById('dnd-end');
        if (el) el.value = settings.dndEnd;
    }
}

/* ============================================
   清理资源 - 防止内存泄漏
   ============================================ */

function cleanupFrameResources() {
    // 清理 CustomModal
    if (window.customModal) {
        window.customModal.cleanup();
    }
    
    // 清理窗口拖拽事件
    cleanupDragWindow();
    
    // 清理输入框事件监听器
    const linkInput = document.getElementById('linkInput');
    if (linkInput && window._linkInputHandler) {
        linkInput.removeEventListener('input', window._linkInputHandler);
        delete window._linkInputHandler;
    }
    
    const favoritesIdInput = document.getElementById('favoritesIdInput');
    if (favoritesIdInput && window._favoritesInputHandler) {
        favoritesIdInput.removeEventListener('input', window._favoritesInputHandler);
        delete window._favoritesInputHandler;
    }
    
    // 清理背景图片数据
    window.__bgImageData__ = null;
    window.__bgImagePath__ = null;
    
    // 清理初始设置数据
    window.__INITIAL_SETTINGS__ = null;
    
    // 清理内容资源
    if (window.cleanupContentResources) {
        window.cleanupContentResources();
    }
    
    console.log('Frame 资源已清理');
}

// 监听窗口关闭事件
window.addEventListener('beforeunload', function() {
    cleanupFrameResources();
});