# -*- coding:utf-8 -*- #

"""UI 主入口模块"""

import sys
import os
import json
import logging
import ctypes
from pathlib import Path

import webview

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app_initializer import initialize_app
from app_initializer.constants import (
    DEFAULT_SUBDIRECTORY, DEFAULT_INIT_DIR_NAME, DEFAULT_DEPENDENCY_TOOLS
)
from log_setup import setup_file_log
from log_setup.constants import LOGGER
from validators import PathValidator, UrlValidator, SettingsValidator, BilibiliParser
from config import SettingsManager
from handlers import TaskHandler, FileHandler
from api import TaskApi, SettingsApi, WindowApi

class UiApi:
    """
    pywebview JS API 桥接类（组合模式）
    将各 API 模块的方法聚合到此类中供前端调用
    """

    def __init__(self, app_dirs, logger):
        self.logger = logger
        self.app_dirs = app_dirs
        
        # 使用系统默认数据目录保存设置文件（%LOCALAPPDATA%/AudioDownloader）
        self.data_dir = SettingsManager.get_data_dir()
        os.makedirs(self.data_dir, exist_ok=True)
        self.settings_manager = SettingsManager(self.data_dir, self.logger)
        self.settings_manager.load()
        
        # 记录当前的 AudioDownloader 根目录路径
        self.audio_downloader_root = app_dirs["dir_result"]["log"].replace("\\Log", "").replace("/Log", "")
        
        # 初始化验证器
        self.path_validator = PathValidator(self.logger)
        self.url_validator = UrlValidator(self.logger)
        self.settings_validator = SettingsValidator(self.path_validator, self.logger)
        self.bilibili_parser = BilibiliParser(self.logger)
        
        # 初始化处理器
        self.file_handler = FileHandler(self.logger)
        self.task_handler = TaskHandler(self.settings_manager, self.logger)
        
        # 初始化 API
        self.task_api = TaskApi(self.task_handler)
        self.task_api.set_validators({
            "path_validator": self.path_validator,
            "url_validator": self.url_validator,
            "settings_validator": self.settings_validator,
            "bilibili_parser": self.bilibili_parser,
        })
        
        self.settings_api = SettingsApi(
            self.settings_manager, 
            self.settings_validator, 
            self.file_handler
        )
        
        self.window_api = WindowApi(self.file_handler, self.logger)
        
        # 暴露设置供前端访问
        self.settings = self.settings_manager.get_all()

    def _move_audio_downloader_folder(self, old_save_path, new_save_path):
        """
        移动 AudioDownloader 文件夹到新路径，并删除旧文件夹
        
        Args:
            old_save_path: 旧的保存路径
            new_save_path: 新的保存路径
            
        Returns:
            dict: 移动结果
        """
        import shutil
        
        old_root = self.audio_downloader_root
        new_root = os.path.join(new_save_path, "AudioDownloader")
        
        try:
            # 检查新路径是否有效
            if not os.path.isdir(new_save_path):
                self.logger.error(f"新路径无效: {new_save_path}")
                return {"success": False, "error": "新路径无效"}
            
            # 如果新路径下已存在 AudioDownloader，先删除
            if os.path.exists(new_root):
                self.logger.warning(f"新路径下已存在 AudioDownloader，将先删除: {new_root}")
                self._force_delete(new_root)
            
            # 创建新路径的父目录
            os.makedirs(new_save_path, exist_ok=True)
            
            # 先复制整个 AudioDownloader 文件夹到新路径
            shutil.copytree(old_root, new_root)
            self.logger.info(f"已将 AudioDownloader 复制到 {new_root}")
            
            # 关闭旧的日志处理器，释放文件锁
            self._close_old_log_handlers(old_root)
            
            # 复制成功后，删除旧文件夹
            self._force_delete(old_root)
            
            # 尝试清理旧的保存路径目录（如果为空）
            if os.path.isdir(old_save_path) and not os.listdir(old_save_path):
                os.rmdir(old_save_path)
                self.logger.info(f"已清理空的旧路径目录: {old_save_path}")
            
            # 更新内部路径
            self.audio_downloader_root = new_root
            
            # 重新初始化 app_dirs（注意：不要修改 settings_manager.data_dir，它应该始终指向系统默认数据目录）
            self.app_dirs["dir_result"]["data"] = os.path.join(new_root, "Data")
            self.app_dirs["dir_result"]["log"] = os.path.join(new_root, "Log")
            self.app_dirs["dir_result"]["audio_orig"] = os.path.join(new_root, "Music", "OriginalAudio")
            self.app_dirs["dir_result"]["audio_comp"] = os.path.join(new_root, "Music", "CompressedAudio")
            
            # 重新配置日志处理器到新路径
            self._reconfigure_log_handlers(new_root)
            
            return {"success": True, "new_path": new_root}
        except Exception as e:
            self.logger.error(f"移动 AudioDownloader 文件夹失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _close_old_log_handlers(self, old_root):
        """
        关闭指向旧路径的日志处理器，释放文件锁
        
        Args:
            old_root: 旧的 AudioDownloader 根目录
        """
        old_log_dir = os.path.join(old_root, "Log")
        
        for handler in self.logger.handlers[:]:
            if hasattr(handler, 'baseFilename'):
                # 检查日志文件是否在旧目录下
                if handler.baseFilename.startswith(old_log_dir):
                    handler.close()
                    self.logger.removeHandler(handler)
                    self.logger.info(f"已关闭旧日志处理器: {handler.baseFilename}")
    
    def _reconfigure_log_handlers(self, new_root):
        """
        重新配置日志处理器到新路径
        
        Args:
            new_root: 新的 AudioDownloader 根目录
        """
        new_log_dir = os.path.join(new_root, "Log")
        os.makedirs(new_log_dir, exist_ok=True)
        
        # 重新配置文件日志
        new_logger = setup_file_log(new_log_dir, {"logger": LOGGER})
        
        # 更新 logger 引用
        self.logger = new_logger
        self.logger.info(f"日志已重新配置到新路径: {new_log_dir}")
    
    def _force_delete(self, path):
        """
        强制删除文件夹，处理 Windows 下的文件锁定问题
        
        Args:
            path: 要删除的文件夹路径
        """
        import subprocess
        import time
        import stat
        
        if not os.path.exists(path):
            return
        
        # 先处理只读属性
        self._remove_readonly(path)
        
        # 多次重试删除
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    self.logger.info(f"第 {attempt + 1} 次尝试删除: {path}")
                    time.sleep(1)  # 等待1秒后重试
                
                # 使用 Windows 命令删除（更可靠）
                if os.name == 'nt':
                    # 使用 cmd 命令删除
                    cmd = f'rmdir /s /q "{path}"'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        self.logger.info(f"已删除文件夹: {path}")
                        return
                    else:
                        self.logger.warning(f"rmdir 命令失败: {result.stderr}")
                else:
                    import shutil
                    shutil.rmtree(path)
                    if not os.path.exists(path):
                        self.logger.info(f"已删除文件夹: {path}")
                        return
            except Exception as e:
                self.logger.warning(f"删除尝试 {attempt + 1} 失败: {path} - {e}")
        
        # 如果所有方法都失败，使用手动删除
        self.logger.warning(f"使用手动删除: {path}")
        self._manual_delete(path)
        
        # 最后确认
        if os.path.exists(path):
            self.logger.warning(f"文件夹删除失败，将在下次启动时清理: {path}")
    
    def _remove_readonly(self, path):
        """递归移除只读属性"""
        import stat
        
        for root, dirs, files in os.walk(path):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    if not os.access(file_path, os.W_OK):
                        os.chmod(file_path, stat.S_IWRITE)
                except Exception:
                    pass
            
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    if not os.access(dir_path, os.W_OK):
                        os.chmod(dir_path, stat.S_IWRITE)
                except Exception:
                    pass
        
        # 处理根目录
        try:
            if not os.access(path, os.W_OK):
                os.chmod(path, stat.S_IWRITE)
        except Exception:
            pass
    
    def _manual_delete(self, path):
        """
        手动递归删除文件夹
        
        Args:
            path: 要删除的文件夹路径
        """
        import stat
        import time
        
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    # 取消只读属性
                    if not os.access(file_path, os.W_OK):
                        os.chmod(file_path, stat.S_IWRITE)
                    os.remove(file_path)
                except Exception as e:
                    self.logger.warning(f"删除文件失败: {file_path} - {e}")
            
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    # 取消只读属性
                    if not os.access(dir_path, os.W_OK):
                        os.chmod(dir_path, stat.S_IWRITE)
                    os.rmdir(dir_path)
                except Exception as e:
                    self.logger.warning(f"删除文件夹失败: {dir_path} - {e}")
        
        # 删除根目录
        try:
            if not os.access(path, os.W_OK):
                os.chmod(path, stat.S_IWRITE)
            os.rmdir(path)
            self.logger.info(f"已手动删除文件夹: {path}")
        except Exception as e:
            self.logger.error(f"手动删除根目录失败: {path} - {e}")

    # ========== 任务 API 代理 ==========
    def get_tasks(self):
        return self.task_api.get_tasks()

    def start_download(self, task_data):
        return self.task_api.start_download(task_data)

    def start_task(self, task_id):
        return self.task_api.start_task(task_id)

    def pause_task(self, task_id):
        return self.task_api.pause_task(task_id)

    def delete_task(self, task_id):
        return self.task_api.delete_task(task_id)

    def parse_bilibili_links(self, urls):
        return self.task_api.parse_bilibili_links(urls)

    def parse_bilibili_favorites(self, fid):
        return self.task_api.parse_bilibili_favorites(fid)

    # ========== 设置 API 代理 ==========
    def get_settings(self):
        return self.settings_api.get_settings()

    def save_settings(self, settings):
        """保存设置并检测 savePath 变化"""
        # 检测 savePath 是否变化
        old_save_path = self.settings.get("savePath", "")
        new_save_path = settings.get("savePath", old_save_path)
        
        # 如果 savePath 变化，移动 AudioDownloader 文件夹
        if old_save_path and new_save_path and old_save_path != new_save_path:
            self.logger.info(f"检测到保存路径变化: {old_save_path} -> {new_save_path}")
            move_result = self._move_audio_downloader_folder(old_save_path, new_save_path)
            if not move_result["success"]:
                return move_result
        
        # 调用原有的保存逻辑
        result = self.settings_api.save_settings(settings)
        
        # 保存成功后，同步更新内存中的设置
        if result.get("success"):
            self.settings.update(settings)
            self.logger.info("内存设置已同步更新")
        
        return result

    def get_bg_image_data(self, image_path):
        return self.settings_api.get_bg_image_data(image_path)

    def get_default_path(self):
        return self.settings_api.get_default_path()

    def reset_settings(self):
        return self.settings_api.reset_settings()

    # ========== 窗口 API 代理 ==========
    def select_folder(self, current_path=""):
        return self.window_api.select_folder(current_path)

    def select_image(self, current_path=""):
        return self.window_api.select_image(current_path)

    def minimize(self):
        self.window_api.minimize()

    def close(self):
        self.window_api.close()

    def move_window(self, x, y):
        self.window_api.move_window(x, y)

    def get_window_position(self):
        return self.window_api.get_window_position()


def get_screen_center():
    """获取屏幕中心坐标"""
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    x = (screen_width - 900) // 2
    y = (screen_height - 700) // 2
    return x, y


def _load_user_save_path():
    """
    加载用户设置的默认保存路径
    从 Windows LocalAppData 目录读取设置，获取用户配置的保存路径
    
    Returns:
        str: 用户设置的默认保存路径
    """
    appdata_dir = SettingsManager.get_data_dir()
    settings_file = os.path.join(appdata_dir, SettingsManager.SETTINGS_FILE)
    
    # 如果存在设置文件，读取保存路径
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                save_path = settings.get("savePath", str(Path.home() / "Downloads"))
                return save_path
        except Exception as e:
            LOGGER.warning(f"读取设置文件失败: {e}")
    
    # 使用默认路径
    default_path = str(Path.home() / "Downloads")
    return default_path


def _cleanup_old_data_dir():
    """
    清理 audio_downloader 项目目录下的旧 data 文件夹
    """
    import shutil
    
    # 获取旧 data 目录路径
    current_dir = os.path.dirname(__file__)
    old_data_dir = os.path.normpath(os.path.join(current_dir, '..', 'data'))
    
    if os.path.exists(old_data_dir):
        try:
            shutil.rmtree(old_data_dir)
            LOGGER.info(f"已清理旧 data 文件夹: {old_data_dir}")
        except Exception as e:
            LOGGER.warning(f"清理旧 data 文件夹失败: {e}")
    else:
        LOGGER.info(f"旧 data 文件夹不存在，无需清理: {old_data_dir}")


def create_window():
    """创建 pywebview 窗口"""
    # 获取用户设置的默认保存路径
    save_path = _load_user_save_path()
    
    # 清理旧 data 文件夹
    _cleanup_old_data_dir()
    
    # 初始化日志系统（输出到 Log 文件夹）
    log_constants_config = {
        "logger": LOGGER,
    }
    log_dir = os.path.join(save_path, "AudioDownloader", "Log")
    os.makedirs(log_dir, exist_ok=True)
    logger = setup_file_log(log_dir, log_constants_config)
    logger.info("Audio Downloader UI 启动中...")
    
    # 初始化应用程序（执行 app_initializer）
    app_constants_config = {
        "subdirectory": DEFAULT_SUBDIRECTORY,
        "dir_init_name": DEFAULT_INIT_DIR_NAME,
        "dependency_tools": DEFAULT_DEPENDENCY_TOOLS,
    }
    app_dirs = initialize_app(save_path, app_constants_config, logger)
    
    logger.info(f"应用初始化完成，数据目录: {app_dirs}")
    
    # 创建 API 实例
    api = UiApi(app_dirs, logger)

    # 获取 HTML 文件路径
    html_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")

    # 获取屏幕中心坐标
    center_x, center_y = get_screen_center()

    window = webview.create_window(
        title="Audio Downloader",
        url=html_path,
        js_api=api,
        x=center_x,
        y=center_y,
        width=900,
        height=700,
        min_size=(800, 600),
        background_color="#1c1c1e",
        resizable=True,
        frameless=True,
        easy_drag=False,
    )

    def on_loaded():
        """窗口加载完成后注入设置数据"""
        settings_json = json.dumps(api.settings, ensure_ascii=False)
        inject_script = f'window.__INITIAL_SETTINGS__ = {settings_json}; loadSettings();'
        window.evaluate_js(inject_script)

    webview.start(on_loaded, debug=False)


if __name__ == "__main__":
    create_window()