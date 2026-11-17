# -*- coding:utf-8 -*- #

"""设置数据验证器"""

import re
import os
import logging


class SettingsValidator:
    """设置数据验证工具类"""

    VALID_THEME_MODES = ["light", "dark", "system"]
    VALID_BG_TYPES = ["solid", "image"]
    VALID_OUTPUT_FORMATS = ["mp3", "flac", "wav", "aac", "ogg"]
    VALID_LANGUAGES = ["zh", "en", "ja"]
    VALID_TIME_FORMATS = ["12", "24"]
    VALID_DATE_FORMATS = ["YMD", "MDY", "DMY"]
    VALID_NOTIFY_STYLES = ["banner", "silent", "badge"]
    VALID_NOTIFY_POSITIONS = ["center", "corner"]
    VALID_SPEED_LIMITS = [0, 500, 1024, 2048, 5120]
    VALID_CONFLICT_ACTIONS = ["skip", "overwrite", "rename"]
    BOOLEAN_SETTINGS = ["soundNotify", "previewContent", "dndMode"]

    DEFAULT_SETTINGS = {
        "themeMode": "system",
        "themeColor": "#007aff",
        "bgType": "solid",
        "bgImagePath": "",
        "outputFormat": "mp3",
        "savePath": "",
        "concurrentTasks": 3,
        "concurrentCompressTasks": 5,
        "language": "zh",
        "timeFormat": "24",
        "dateFormat": "YMD",
        "notifyStyle": "banner",
        "notifyPosition": "center",
        "soundNotify": False,
        "previewContent": True,
        "dndMode": False,
        "dndStart": "22:00",
        "dndEnd": "08:00",
    }

    def __init__(self, path_validator, logger=None):
        self.path_validator = path_validator
        self.logger = logger or logging.getLogger(__name__)

    def validate_settings(self, settings):
        """
        验证设置数据的合法性
        
        Args:
            settings: 设置数据字典
            
        Returns:
            tuple: (是否有效, 验证后的设置字典, 错误信息列表)
        """
        if not isinstance(settings, dict):
            error_msg = "设置数据格式错误：期望字典类型"
            self.logger.error(error_msg)
            return False, self.DEFAULT_SETTINGS.copy(), [error_msg]
        
        validated = self.DEFAULT_SETTINGS.copy()
        errors = []
        warnings = []
        
        self._validate_theme_mode(settings, validated, errors)
        self._validate_theme_color(settings, validated, errors)
        self._validate_bg_type(settings, validated, errors)
        self._validate_bg_image_path(settings, validated, errors, warnings)
        self._validate_output_format(settings, validated, errors)
        self._validate_save_path(settings, validated, errors, warnings)
        self._validate_concurrent_tasks(settings, validated, errors, warnings)
        self._validate_concurrent_compress_tasks(settings, validated, errors, warnings)
        self._validate_language(settings, validated, errors)
        self._validate_time_format(settings, validated, errors)
        self._validate_date_format(settings, validated, errors)
        self._validate_notify_style(settings, validated, errors)
        self._validate_notify_position(settings, validated, errors)
        self._validate_boolean_settings(settings, validated, errors)
        self._validate_dnd_time(settings, validated, errors)
        
        if errors:
            error_summary = f"设置验证失败 ({len(errors)} 个错误): " + "; ".join(errors)
            self.logger.error(error_summary)
            return False, validated, errors
        
        if warnings:
            for warning in warnings:
                self.logger.warning(warning)
        
        self.logger.info(f"设置验证通过，共验证 {len(settings)} 个字段")
        return True, validated, []

    def validate_speed_limit(self, speed):
        """验证下载限速"""
        try:
            limit = int(speed)
            if limit in self.VALID_SPEED_LIMITS:
                return True, limit
            else:
                self.logger.warning(f"不支持的限速值: {limit}，使用默认值 0")
                return True, 0
        except (ValueError, TypeError):
            self.logger.warning(f"限速格式错误: {speed}，使用默认值 0")
            return True, 0

    def validate_conflict_action(self, action):
        """验证冲突处理方式"""
        if action in self.VALID_CONFLICT_ACTIONS:
            return True, action
        else:
            self.logger.warning(f"不支持的冲突处理方式: {action}，使用默认值 skip")
            return True, "skip"

    def validate_favorite_id(self, fid):
        """验证收藏夹 ID"""
        if not fid or not str(fid).strip():
            return False, ""
        
        fid_str = str(fid).strip()
        
        if not fid_str.isdigit():
            self.logger.warning(f"收藏夹 ID 格式错误: {fid_str}")
            return False, ""
        
        if len(fid_str) > 20:
            self.logger.warning(f"收藏夹 ID 过长: {len(fid_str)} 字符")
            return False, ""
        
        return True, fid_str

    def _validate_theme_mode(self, settings, validated, errors):
        """验证主题模式"""
        theme_mode = settings.get("themeMode")
        if theme_mode is None:
            return
        
        if not isinstance(theme_mode, str):
            errors.append(f"themeMode 类型错误：期望字符串，实际为 {type(theme_mode).__name__}")
            return
        
        if theme_mode in self.VALID_THEME_MODES:
            validated["themeMode"] = theme_mode
        else:
            errors.append(f"themeMode 值无效: '{theme_mode}'，有效值: {', '.join(self.VALID_THEME_MODES)}")

    def _validate_theme_color(self, settings, validated, errors):
        """验证主题颜色"""
        theme_color = settings.get("themeColor")
        if theme_color is None:
            return
        
        if not isinstance(theme_color, str):
            errors.append(f"themeColor 类型错误：期望字符串，实际为 {type(theme_color).__name__}")
            return
        
        if re.match(r'^#[0-9a-fA-F]{6}$', theme_color):
            validated["themeColor"] = theme_color
        else:
            errors.append(f"themeColor 格式错误: '{theme_color}'，期望格式: #RRGGBB")

    def _validate_bg_type(self, settings, validated, errors):
        """验证背景类型"""
        bg_type = settings.get("bgType")
        if bg_type is None:
            return
        
        if not isinstance(bg_type, str):
            errors.append(f"bgType 类型错误：期望字符串，实际为 {type(bg_type).__name__}")
            return
        
        if bg_type in self.VALID_BG_TYPES:
            validated["bgType"] = bg_type
        else:
            errors.append(f"bgType 值无效: '{bg_type}'，有效值: {', '.join(self.VALID_BG_TYPES)}")

    def _validate_bg_image_path(self, settings, validated, errors, warnings):
        """验证背景图片路径"""
        bg_path = settings.get("bgImagePath")
        if bg_path is None:
            return
        
        if not isinstance(bg_path, str):
            errors.append(f"bgImagePath 类型错误：期望字符串，实际为 {type(bg_path).__name__}")
            return
        
        if not bg_path.strip():
            validated["bgImagePath"] = ""
            return
        
        valid, cleaned = self.path_validator.validate(bg_path, allow_empty=True)
        if valid:
            validated["bgImagePath"] = cleaned
            if not os.path.exists(cleaned):
                warnings.append(f"背景图片路径不存在: {cleaned}")
        else:
            errors.append(f"bgImagePath 路径无效: '{bg_path}'")

    def _validate_output_format(self, settings, validated, errors):
        """验证输出格式"""
        output_format = settings.get("outputFormat")
        if output_format is None:
            return
        
        if not isinstance(output_format, str):
            errors.append(f"outputFormat 类型错误：期望字符串，实际为 {type(output_format).__name__}")
            return
        
        if output_format in self.VALID_OUTPUT_FORMATS:
            validated["outputFormat"] = output_format
        else:
            errors.append(f"outputFormat 值无效: '{output_format}'，有效值: {', '.join(self.VALID_OUTPUT_FORMATS)}")

    def _validate_save_path(self, settings, validated, errors, warnings):
        """验证保存路径"""
        save_path = settings.get("savePath")
        if save_path is None:
            return
        
        if not isinstance(save_path, str):
            errors.append(f"savePath 类型错误：期望字符串，实际为 {type(save_path).__name__}")
            return
        
        if not save_path.strip():
            errors.append("savePath 不能为空")
            return
        
        valid, cleaned = self.path_validator.validate(save_path, allow_empty=False)
        if valid:
            validated["savePath"] = cleaned
            if not os.path.exists(cleaned):
                warnings.append(f"保存路径不存在，将自动创建: {cleaned}")
        else:
            errors.append(f"savePath 路径无效: '{save_path}'")

    def _validate_concurrent_tasks(self, settings, validated, errors, warnings):
        """验证并发任务数"""
        concurrent = settings.get("concurrentTasks")
        if concurrent is None:
            return
        
        try:
            count = int(concurrent)
            if 1 <= count <= 10:
                validated["concurrentTasks"] = count
            else:
                warnings.append(f"并发任务数超出范围 (1-10): {count}，使用默认值 3")
        except (ValueError, TypeError):
            errors.append(f"concurrentTasks 格式错误: '{concurrent}'，期望整数")

    def _validate_concurrent_compress_tasks(self, settings, validated, errors, warnings):
        """验证同时压缩任务数"""
        concurrent = settings.get("concurrentCompressTasks")
        if concurrent is None:
            return
        
        try:
            count = int(concurrent)
            if 1 <= count <= 10:
                validated["concurrentCompressTasks"] = count
            else:
                warnings.append(f"同时压缩任务数超出范围 (1-10): {count}，使用默认值 5")
        except (ValueError, TypeError):
            errors.append(f"concurrentCompressTasks 格式错误: '{concurrent}'，期望整数")

    def _validate_language(self, settings, validated, errors):
        """验证语言设置"""
        language = settings.get("language")
        if language is None:
            return
        
        if not isinstance(language, str):
            errors.append(f"language 类型错误：期望字符串，实际为 {type(language).__name__}")
            return
        
        if language in self.VALID_LANGUAGES:
            validated["language"] = language
        else:
            errors.append(f"language 值无效: '{language}'，有效值: {', '.join(self.VALID_LANGUAGES)}")

    def _validate_time_format(self, settings, validated, errors):
        """验证时间格式"""
        time_format = settings.get("timeFormat")
        if time_format is None:
            return
        
        if not isinstance(time_format, str):
            errors.append(f"timeFormat 类型错误：期望字符串，实际为 {type(time_format).__name__}")
            return
        
        if time_format in self.VALID_TIME_FORMATS:
            validated["timeFormat"] = time_format
        else:
            errors.append(f"timeFormat 值无效: '{time_format}'，有效值: {', '.join(self.VALID_TIME_FORMATS)}")

    def _validate_date_format(self, settings, validated, errors):
        """验证日期格式"""
        date_format = settings.get("dateFormat")
        if date_format is None:
            return
        
        if not isinstance(date_format, str):
            errors.append(f"dateFormat 类型错误：期望字符串，实际为 {type(date_format).__name__}")
            return
        
        if date_format in self.VALID_DATE_FORMATS:
            validated["dateFormat"] = date_format
        else:
            errors.append(f"dateFormat 值无效: '{date_format}'，有效值: {', '.join(self.VALID_DATE_FORMATS)}")

    def _validate_notify_style(self, settings, validated, errors):
        """验证通知样式"""
        notify_style = settings.get("notifyStyle")
        if notify_style is None:
            return
        
        if not isinstance(notify_style, str):
            errors.append(f"notifyStyle 类型错误：期望字符串，实际为 {type(notify_style).__name__}")
            return
        
        if notify_style in self.VALID_NOTIFY_STYLES:
            validated["notifyStyle"] = notify_style
        else:
            errors.append(f"notifyStyle 值无效: '{notify_style}'，有效值: {', '.join(self.VALID_NOTIFY_STYLES)}")

    def _validate_notify_position(self, settings, validated, errors):
        """验证通知位置"""
        notify_pos = settings.get("notifyPosition")
        if notify_pos is None:
            return
        
        if not isinstance(notify_pos, str):
            errors.append(f"notifyPosition 类型错误：期望字符串，实际为 {type(notify_pos).__name__}")
            return
        
        if notify_pos in self.VALID_NOTIFY_POSITIONS:
            validated["notifyPosition"] = notify_pos
        else:
            errors.append(f"notifyPosition 值无效: '{notify_pos}'，有效值: {', '.join(self.VALID_NOTIFY_POSITIONS)}")

    def _validate_boolean_settings(self, settings, validated, errors):
        """验证布尔类型设置"""
        for key in self.BOOLEAN_SETTINGS:
            value = settings.get(key)
            if value is None:
                continue
            
            if isinstance(value, bool):
                validated[key] = value
            elif isinstance(value, str):
                if value.lower() in ('true', '1', 'yes'):
                    validated[key] = True
                elif value.lower() in ('false', '0', 'no'):
                    validated[key] = False
                else:
                    errors.append(f"{key} 布尔值格式错误: '{value}'")
            elif isinstance(value, (int, float)):
                validated[key] = bool(value)
            else:
                errors.append(f"{key} 类型错误：期望布尔值，实际为 {type(value).__name__}")

    def _validate_dnd_time(self, settings, validated, errors):
        """验证免打扰时间段"""
        time_pattern = re.compile(r'^([01]\d|2[0-3]):[0-5]\d$')
        
        dnd_start = settings.get("dndStart")
        if dnd_start is not None:
            if not isinstance(dnd_start, str):
                errors.append(f"dndStart 类型错误：期望字符串，实际为 {type(dnd_start).__name__}")
            elif time_pattern.match(dnd_start):
                validated["dndStart"] = dnd_start
            else:
                errors.append(f"dndStart 格式错误: '{dnd_start}'，期望格式: HH:MM (24小时制)")
        
        dnd_end = settings.get("dndEnd")
        if dnd_end is not None:
            if not isinstance(dnd_end, str):
                errors.append(f"dndEnd 类型错误：期望字符串，实际为 {type(dnd_end).__name__}")
            elif time_pattern.match(dnd_end):
                validated["dndEnd"] = dnd_end
            else:
                errors.append(f"dndEnd 格式错误: '{dnd_end}'，期望格式: HH:MM (24小时制)")