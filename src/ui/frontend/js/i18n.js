/* ============================================
   Audio Downloader - i18n Module
   ============================================ */

class I18nManager {
    constructor() {
        this.currentLocale = 'zh';
        this.translations = {};
        this.fallbackLocale = 'zh';
        this.isInitialized = false;
    }

    async init(defaultLocale = 'zh') {
        if (this.isInitialized) return;
        
        this.currentLocale = defaultLocale;
        await this.loadLocale(this.currentLocale);
        this.isInitialized = true;
        
        // Apply translations to DOM after initialization
        this.applyTranslations();
    }

    async loadLocale(locale) {
        if (this.translations[locale]) {
            this.currentLocale = locale;
            return;
        }

        try {
            const response = await fetch(`locales/${locale}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load locale: ${locale}`);
            }
            this.translations[locale] = await response.json();
            this.currentLocale = locale;
        } catch (e) {
            console.error(`加载语言文件失败 (${locale}):`, e);
            if (locale !== this.fallbackLocale) {
                await this.loadLocale(this.fallbackLocale);
            }
        }
    }

    t(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations[this.currentLocale];

        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                value = this.getFallbackValue(keys);
                break;
            }
        }

        if (typeof value === 'string' && Object.keys(params).length > 0) {
            return this.interpolate(value, params);
        }

        return typeof value === 'string' ? value : key;
    }

    getFallbackValue(keys) {
        if (this.currentLocale !== this.fallbackLocale) {
            let value = this.translations[this.fallbackLocale];
            for (const k of keys) {
                if (value && typeof value === 'object' && k in value) {
                    value = value[k];
                } else {
                    return keys.join('.');
                }
            }
            return typeof value === 'string' ? value : keys.join('.');
        }
        return keys.join('.');
    }

    interpolate(template, params) {
        return template.replace(/\{(\w+)\}/g, (match, key) => {
            return params[key] !== undefined ? params[key] : match;
        });
    }

    setLocale(locale) {
        if (this.currentLocale === locale) return;
        this.currentLocale = locale;
        this.applyTranslations();
    }

    getLocale() {
        return this.currentLocale;
    }

    applyTranslations() {
        this.updateStaticText();
        this.updatePlaceholders();
        this.updateTooltips();
        this.updateTaskList();
        this.updateDataI18nElements();
    }

    /**
     * Update all elements with data-i18n attributes
     */
    updateDataI18nElements() {
        // Update text content
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            if (key) {
                el.textContent = this.t(key);
            }
        });

        // Update placeholders
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.dataset.i18nPlaceholder;
            if (key) {
                el.placeholder = this.t(key);
            }
        });

        // Update titles/tooltips
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.dataset.i18nTitle;
            if (key) {
                el.title = this.t(key);
            }
        });
    }

    updateStaticText() {
        // App title
        const appTitle = document.querySelector('.window-title');
        if (appTitle) appTitle.textContent = this.t('app.window_title');

        // Sidebar
        const sidebarItems = document.querySelectorAll('.sidebar-item');
        sidebarItems.forEach(item => {
            const page = item.dataset.page;
            if (page === 'download') item.title = this.t('sidebar.download_tasks');
            else if (page === 'add-task') item.title = this.t('sidebar.add_task');
            else if (page === 'settings') item.title = this.t('sidebar.settings');
        });

        // Toolbar
        const btnStartAll = document.getElementById('btn-start-all');
        if (btnStartAll) btnStartAll.textContent = this.t('toolbar.start_all');
        
        const btnPauseAll = document.getElementById('btn-pause-all');
        if (btnPauseAll) btnPauseAll.textContent = this.t('toolbar.pause_all');
        
        const btnDeleteAll = document.getElementById('btn-delete-all');
        if (btnDeleteAll) btnDeleteAll.textContent = this.t('toolbar.delete_all');

        // Empty tip
        const emptyTip = document.getElementById('emptyTip');
        if (emptyTip) emptyTip.textContent = this.t('task_list.empty');

        // Add task modal
        const modalTitle = document.querySelector('.modal-title');
        if (modalTitle) modalTitle.textContent = this.t('add_task.title');

        // Download type switcher
        const typeBtns = document.querySelectorAll('.type-btn');
        typeBtns.forEach(btn => {
            const type = btn.dataset.type;
            const span = btn.querySelector('span');
            if (type === 'link-download' && span) {
                span.textContent = this.t('add_task.download_type.link');
            } else if (type === 'fav-download' && span) {
                span.textContent = this.t('add_task.download_type.favorite');
            }
        });

        // Link input
        const linkInput = document.getElementById('linkInput');
        if (linkInput) linkInput.placeholder = this.t('add_task.link.placeholder');

        // Parse result
        const parseResultH4 = document.querySelector('#parseResultArea h4');
        if (parseResultH4) parseResultH4.textContent = this.t('add_task.link.parse_result');
        
        const parseResultText = document.getElementById('parseResultText');
        if (parseResultText && parseResultText.classList.contains('result-empty')) {
            parseResultText.textContent = this.t('add_task.link.empty');
        }

        // Favorites input
        const favLabel = document.querySelector('.favorites-label span');
        if (favLabel) favLabel.textContent = this.t('add_task.favorite.label');
        
        const favInput = document.getElementById('favoritesIdInput');
        if (favInput) favInput.placeholder = this.t('add_task.favorite.placeholder');
        
        const favHelp = document.querySelector('.favorites-help-text span');
        if (favHelp) favHelp.textContent = this.t('add_task.favorite.help');
        
        const favResultH4 = document.querySelector('#favoritesParseResult h4');
        if (favResultH4) favResultH4.textContent = this.t('add_task.favorite.parse_result');
        
        const favParseText = document.getElementById('favoritesParseText');
        if (favParseText && favParseText.classList.contains('result-empty')) {
            favParseText.textContent = this.t('add_task.favorite.empty');
        }

        // Download settings
        const settingH4s = document.querySelectorAll('.download-setting h4');
        settingH4s.forEach(h4 => h4.textContent = this.t('add_task.settings.title'));

        // Task name label - use data-i18n attribute
        const taskNameLabel = document.querySelector('[data-i18n="add_task.settings.task_name"]');
        if (taskNameLabel) taskNameLabel.textContent = this.t('add_task.settings.task_name');
        
        const taskNameInput = document.getElementById('task-name');
        if (taskNameInput) taskNameInput.placeholder = this.t('add_task.settings.task_name_placeholder');

        // Speed limit label
        const speedLimitLabel = document.querySelector('[data-i18n="add_task.settings.speed_limit"]');
        if (speedLimitLabel) speedLimitLabel.textContent = this.t('add_task.settings.speed_limit');
        
        const speedLimitSelect = document.getElementById('speed-limit');
        if (speedLimitSelect) {
            const options = speedLimitSelect.querySelectorAll('option');
            options.forEach(opt => {
                const val = opt.value;
                if (val === '0') opt.textContent = this.t('add_task.settings.speed_options.unlimited');
                else if (val === '500') opt.textContent = this.t('add_task.settings.speed_options.500k');
                else if (val === '1024') opt.textContent = this.t('add_task.settings.speed_options.1m');
                else if (val === '2048') opt.textContent = this.t('add_task.settings.speed_options.2m');
                else if (val === '5120') opt.textContent = this.t('add_task.settings.speed_options.5m');
            });
        }

        // Conflict handling label
        const conflictLabel = document.querySelector('[data-i18n="add_task.settings.conflict"]');
        if (conflictLabel) conflictLabel.textContent = this.t('add_task.settings.conflict');
        
        const conflictBtns = document.querySelectorAll('.conflict-btn');
        conflictBtns.forEach(btn => {
            const val = btn.dataset.value;
            const span = btn.querySelector('span');
            if (val === 'skip' && span) span.textContent = this.t('add_task.settings.conflict_actions.skip');
            else if (val === 'overwrite' && span) span.textContent = this.t('add_task.settings.conflict_actions.overwrite');
            else if (val === 'rename' && span) span.textContent = this.t('add_task.settings.conflict_actions.rename');
        });

        // Buttons
        const btnOk = document.getElementById('btn-ok');
        if (btnOk) btnOk.textContent = this.t('add_task.buttons.ok');
        
        const btnCancel = document.getElementById('btn-cancel');
        if (btnCancel) btnCancel.textContent = this.t('add_task.buttons.cancel');

        // Settings page
        this.updateSettingsPage();

        // Modal
        const modalTitleEl = document.getElementById('customModalTitle');
        if (modalTitleEl) modalTitleEl.textContent = this.t('modal.title');
        
        const modalConfirmBtn = document.getElementById('customModalConfirm');
        if (modalConfirmBtn) modalConfirmBtn.textContent = this.t('modal.confirm');
        
        const modalCancelBtn = document.getElementById('customModalCancel');
        if (modalCancelBtn) modalCancelBtn.textContent = this.t('modal.cancel');
    }

    updateSettingsPage() {
        // Section titles - use data-i18n
        const sectionTitles = document.querySelectorAll('.section-title');
        const sectionKeys = [
            'settings.sections.appearance',
            'settings.sections.download',
            'settings.sections.language_time',
            'settings.sections.notification'
        ];
        sectionTitles.forEach((title, index) => {
            if (sectionKeys[index]) {
                title.textContent = this.t(sectionKeys[index]);
            }
        });

        // Theme buttons
        const themeBtns = document.querySelectorAll('.theme-mode-btn');
        themeBtns.forEach(btn => {
            const mode = btn.dataset.mode;
            const span = btn.querySelector('span');
            if (mode === 'light' && span) span.textContent = this.t('settings.theme.light');
            else if (mode === 'dark' && span) span.textContent = this.t('settings.theme.dark');
            else if (mode === 'system' && span) span.textContent = this.t('settings.theme.system');
        });

        // Background type buttons
        const bgTypeBtns = document.querySelectorAll('.bg-type-btn');
        bgTypeBtns.forEach(btn => {
            const type = btn.dataset.type;
            const span = btn.querySelector('span');
            if (type === 'solid' && span) span.textContent = this.t('settings.background.solid');
            else if (type === 'image' && span) span.textContent = this.t('settings.background.image');
        });

        // Background image button
        const bgImageBtnSpan = document.querySelector('#bgImageBtn span');
        if (bgImageBtnSpan) bgImageBtnSpan.textContent = this.t('settings.background.select_image');

        // Save path
        const savePathInput = document.getElementById('savePathInput');
        if (savePathInput) savePathInput.placeholder = this.t('settings.save_path.placeholder');
        
        const savePathBtnSpan = document.querySelector('#savePathBtn span');
        if (savePathBtnSpan) savePathBtnSpan.textContent = this.t('settings.save_path.browse');

        // Language select
        const languageSelect = document.getElementById('language');
        if (languageSelect) {
            const options = languageSelect.querySelectorAll('option');
            options.forEach(opt => {
                const val = opt.value;
                if (val === 'zh') opt.textContent = this.t('settings.language.zh');
                else if (val === 'en') opt.textContent = this.t('settings.language.en');
                else if (val === 'ja') opt.textContent = this.t('settings.language.ja');
            });
        }

        // Time format buttons
        const timeFormatBtns = document.querySelectorAll('.time-format-btn');
        timeFormatBtns.forEach(btn => {
            const format = btn.dataset.format;
            const span = btn.querySelector('span');
            if (format === '24' && span) span.textContent = this.t('settings.time_format.h24');
            else if (format === '12' && span) span.textContent = this.t('settings.time_format.h12');
        });

        // Date format buttons
        const dateFormatBtns = document.querySelectorAll('.date-format-btn');
        dateFormatBtns.forEach(btn => {
            const format = btn.dataset.format;
            const span = btn.querySelector('span');
            if (format === 'YMD' && span) span.textContent = this.t('settings.date_format.ymd');
            else if (format === 'MDY' && span) span.textContent = this.t('settings.date_format.mdy');
            else if (format === 'DMY' && span) span.textContent = this.t('settings.date_format.dmy');
        });

        // Notification style buttons
        const notifyStyleBtns = document.querySelectorAll('.notification-style-btn');
        notifyStyleBtns.forEach(btn => {
            const style = btn.dataset.style;
            const span = btn.querySelector('span');
            if (style === 'banner' && span) span.textContent = this.t('settings.notification.banner');
            else if (style === 'silent' && span) span.textContent = this.t('settings.notification.silent');
            else if (style === 'badge' && span) span.textContent = this.t('settings.notification.badge');
        });

        // Notification position buttons
        const notifyPosBtns = document.querySelectorAll('.notification-position-btn');
        notifyPosBtns.forEach(btn => {
            const pos = btn.dataset.position;
            const span = btn.querySelector('span');
            if (pos === 'center' && span) span.textContent = this.t('settings.notification.center');
            else if (pos === 'corner' && span) span.textContent = this.t('settings.notification.corner');
        });

        // DND separator
        const dndSeparator = document.querySelector('.dnd-time-separator');
        if (dndSeparator) dndSeparator.textContent = this.t('settings.notification.to');

        // Reset section
        const resetText = document.querySelector('.reset-section span:not(.reset-line):not(.reset-icon)');
        if (resetText) resetText.textContent = this.t('settings.reset.title');
    }

    updatePlaceholders() {
        const linkInput = document.getElementById('linkInput');
        if (linkInput) linkInput.placeholder = this.t('add_task.link.placeholder');
        
        const favoritesIdInput = document.getElementById('favoritesIdInput');
        if (favoritesIdInput) favoritesIdInput.placeholder = this.t('add_task.favorite.placeholder');
        
        const taskNameInput = document.getElementById('task-name');
        if (taskNameInput) taskNameInput.placeholder = this.t('add_task.settings.task_name_placeholder');
        
        const savePathInput = document.getElementById('savePathInput');
        if (savePathInput) savePathInput.placeholder = this.t('settings.save_path.placeholder');
    }

    updateTooltips() {
        const helpTips = document.querySelectorAll('.help-tip[data-tip-key]');
        helpTips.forEach(tip => {
            const tipKey = tip.dataset.tipKey;
            if (tipKey) {
                tip.dataset.tip = this.t(tipKey);
            }
        });
    }

    updateTaskList() {
        const taskItems = document.querySelectorAll('.task-item');
        taskItems.forEach(item => {
            const taskId = item.dataset.id;
            if (window.tasks) {
                const task = window.tasks.find(t => t.id === taskId);
                if (task) {
                    // Update status text if needed
                }
            }
        });
    }

    /**
     * Translate backend error messages that use i18n keys
     * Backend returns "i18n:key.path" format or just "key.path"
     */
    translateBackendError(errorMsg) {
        if (!errorMsg) return '';
        if (typeof errorMsg !== 'string') return String(errorMsg);
        
        // Hardcoded fallback translations for all supported locales (PRIMARY METHOD)
        const fallbackTranslations = {
            zh: {
                'add_task.validation.no_valid_links': '没有有效的下载链接',
                'add_task.validation.links_empty': '链接列表不能为空',
                'add_task.validation.links_format_error': '链接列表格式错误',
                'add_task.validation.links_too_many': '单次任务最多支持 100 个链接',
                'add_task.validation.fid_format_error': '收藏夹 ID 格式错误',
                'add_task.validation.task_data_format_error': '任务数据格式错误',
                'add_task.validation.unsupported_task_type': '不支持的任务类型',
                'add_task.validation.task_name_invalid_chars': '任务名称包含非法字符',
                'add_task.validation.save_path_invalid': '保存路径不合法',
                'add_task.validation.link_process_failed': '链接处理失败',
                'add_task.validation.favorite_process_failed': '收藏夹处理失败',
                'add_task.validation.task_id_format_error': '任务 ID 格式错误',
                'add_task.validation.task_not_found': '任务不存在',
            },
            en: {
                'add_task.validation.no_valid_links': 'No valid download links',
                'add_task.validation.links_empty': 'Links list cannot be empty',
                'add_task.validation.links_format_error': 'Invalid links list format',
                'add_task.validation.links_too_many': 'Maximum 100 links per task',
                'add_task.validation.fid_format_error': 'Invalid Favorites ID format',
                'add_task.validation.task_data_format_error': 'Invalid task data format',
                'add_task.validation.unsupported_task_type': 'Unsupported task type',
                'add_task.validation.task_name_invalid_chars': 'Task name contains invalid characters',
                'add_task.validation.save_path_invalid': 'Invalid save path',
                'add_task.validation.link_process_failed': 'Link processing failed',
                'add_task.validation.favorite_process_failed': 'Favorites processing failed',
                'add_task.validation.task_id_format_error': 'Invalid task ID format',
                'add_task.validation.task_not_found': 'Task not found',
            },
            ja: {
                'add_task.validation.no_valid_links': '有効なダウンロードリンクがありません',
                'add_task.validation.links_empty': 'リンクリストは空にできません',
                'add_task.validation.links_format_error': 'リンクリストの形式が無効です',
                'add_task.validation.links_too_many': '1つのタスクあたり最大100リンク',
                'add_task.validation.fid_format_error': 'お気に入りIDの形式が無効です',
                'add_task.validation.task_data_format_error': 'タスクデータの形式が無効です',
                'add_task.validation.unsupported_task_type': 'サポートされていないタスクタイプ',
                'add_task.validation.task_name_invalid_chars': 'タスク名に無効な文字が含まれています',
                'add_task.validation.save_path_invalid': '保存パスが無効です',
                'add_task.validation.link_process_failed': 'リンクの処理に失敗しました',
                'add_task.validation.favorite_process_failed': 'お気に入りの処理に失敗しました',
                'add_task.validation.task_id_format_error': 'タスクIDの形式が無効です',
                'add_task.validation.task_not_found': 'タスクが見つかりません',
            }
        };
        
        // Key mapping from backend i18n keys to locale keys
        const keyMap = {
            'add_task.validation.no_valid_links': 'backend.no_valid_links',
            'add_task.validation.links_empty': 'backend.links_empty',
            'add_task.validation.links_format_error': 'backend.links_format_error',
            'add_task.validation.links_too_many': 'backend.links_too_many',
            'add_task.validation.fid_format_error': 'backend.fid_format_error',
            'add_task.validation.task_data_format_error': 'backend.task_data_format_error',
            'add_task.validation.unsupported_task_type': 'backend.unsupported_task_type',
            'add_task.validation.task_name_invalid_chars': 'backend.task_name_invalid_chars',
            'add_task.validation.save_path_invalid': 'backend.save_path_invalid',
            'add_task.validation.link_process_failed': 'backend.link_process_failed',
            'add_task.validation.favorite_process_failed': 'backend.favorite_process_failed',
            'add_task.validation.task_id_format_error': 'backend.task_id_format_error',
            'add_task.validation.task_not_found': 'backend.task_not_found',
        };
        
        // Plain Chinese text fallback mapping
        const plainTextMap = {
            '没有有效的下载链接': 'backend.no_valid_links',
            '链接列表不能为空': 'backend.links_empty',
            '链接列表格式错误': 'backend.links_format_error',
            '单次任务最多支持 100 个链接': 'backend.links_too_many',
            '收藏夹 ID 格式错误': 'backend.fid_format_error',
            '任务数据格式错误': 'backend.task_data_format_error',
            '不支持的任务类型': 'backend.unsupported_task_type',
            '任务名称包含非法字符': 'backend.task_name_invalid_chars',
            '保存路径不合法': 'backend.save_path_invalid',
            '链接处理失败': 'backend.link_process_failed',
            '收藏夹处理失败': 'backend.favorite_process_failed',
            '任务 ID 格式错误': 'backend.task_id_format_error',
            '任务不存在': 'backend.task_not_found',
        };
        
        // Strip i18n: prefix if present
        let key = errorMsg;
        if (errorMsg.startsWith('i18n:')) {
            key = errorMsg.substring(5);
        }
        
        // PRIMARY: Use hardcoded fallback translations (most reliable)
        // Always default to Chinese if currentLocale is not set or invalid
        const locale = this.currentLocale || 'zh';
        const localeFallbacks = fallbackTranslations[locale] || fallbackTranslations['zh'];
        if (localeFallbacks[key]) {
            return localeFallbacks[key];
        }
        
        // SECONDARY: Try direct translation lookup
        const directTranslated = this.t(key);
        if (directTranslated !== key) {
            return directTranslated;
        }
        
        // TERTIARY: Try mapped key translation
        const mappedKey = keyMap[key];
        if (mappedKey) {
            const mappedTranslated = this.t(mappedKey);
            if (mappedTranslated !== mappedKey) {
                return mappedTranslated;
            }
        }
        
        // QUATERNARY: Plain Chinese text — try to map to locale key
        const plainMappedKey = plainTextMap[errorMsg];
        if (plainMappedKey) {
            const translated = this.t(plainMappedKey);
            if (translated !== plainMappedKey) {
                return translated;
            }
        }
        
        // Last resort: return the original error message
        return errorMsg;
    }

    getT(key, params = {}) {
        return this.t(key, params);
    }
}

// Create global i18n instance
window.i18n = new I18nManager();