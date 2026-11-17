# -*- coding:utf-8 -*- #

"""设置管理器"""

import os
import json
import logging
from pathlib import Path


class SettingsManager:
    """设置加载与保存管理器"""

    SETTINGS_FILE = "audio_downloader_ui_settings.json"

    DEFAULT_SETTINGS = {
        "themeMode": "system",
        "themeColor": "#007aff",
        "bgType": "image",
        "bgImagePath": os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'static', '山-极简主义.png')),
        "outputFormat": "mp3",
        "savePath": str(Path.home() / "Downloads"),
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

    def __init__(self, data_dir, logger=None):
        """
        初始化设置管理器
        
        Args:
            data_dir: 数据存储目录（Windows AppData 目录）
            logger: 日志记录器
        """
        self.data_dir = data_dir
        self.logger = logger or logging.getLogger(__name__)
        self.settings = self.DEFAULT_SETTINGS.copy()

    @staticmethod
    def get_data_dir():
        """
        获取电脑默认数据保存目录（Windows LocalAppData/AudioDownloader）
        
        Returns:
            str: 数据目录的绝对路径
        """
        # 使用 Windows 默认数据保存目录 (LocalAppData)
        localappdata = os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData' / 'Local'))
        data_dir = os.path.join(localappdata, 'AudioDownloader')
        normalized_path = os.path.normpath(data_dir)
        return normalized_path

    def load(self):
        """
        从数据目录加载设置
        
        Returns:
            dict: 设置数据字典
        """
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        settings_file = os.path.join(self.data_dir, self.SETTINGS_FILE)
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
                    self.logger.info(f"设置已从 {settings_file} 加载")
            except Exception as e:
                self.logger.error(f"加载设置失败: {e}")
        else:
            self.logger.info("使用默认设置")
        
        return self.settings

    def save(self):
        """
        将设置保存到数据目录
        
        Returns:
            bool: 保存是否成功
        """
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        settings_file = os.path.join(self.data_dir, self.SETTINGS_FILE)
        
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            self.logger.info(f"设置已保存到 {settings_file}")
            return True
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            return False

    def update(self, new_settings):
        """
        更新设置
        
        Args:
            new_settings: 新的设置数据字典
        """
        self.settings.update(new_settings)

    def get(self, key, default=None):
        """
        获取设置值
        
        Args:
            key: 设置键名
            default: 默认值
            
        Returns:
            设置值或默认值
        """
        return self.settings.get(key, default)

    def get_all(self):
        """
        获取所有设置
        
        Returns:
            dict: 完整的设置数据字典
        """
        return self.settings.copy()

    def reset_to_defaults(self):
        """
        恢复默认设置
        
        Returns:
            bool: 是否成功
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        return self.save()