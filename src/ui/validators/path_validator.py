# -*- coding:utf-8 -*- #

"""路径验证器"""

import os
import logging


class PathValidator:
    """路径验证工具类"""

    MAX_PATH_LENGTH = 260
    FORBIDDEN_CHARS = ['<', '>', '|', '?', '*']

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def validate(self, path, allow_empty=False):
        """
        验证路径合法性
        
        Args:
            path: 待验证的路径字符串
            allow_empty: 是否允许空路径
            
        Returns:
            tuple: (是否有效, 清理后的路径)
        """
        if not path or not path.strip():
            return allow_empty, path.strip() if path else ""
        
        cleaned = os.path.normpath(os.path.abspath(path.strip()))
        
        if len(cleaned) > self.MAX_PATH_LENGTH:
            self.logger.warning(f"路径过长: {len(cleaned)} 字符")
            return False, ""
        
        if any(c in cleaned for c in self.FORBIDDEN_CHARS):
            self.logger.warning(f"路径包含非法字符: {cleaned}")
            return False, ""
        
        return True, cleaned

    def validate_task_name(self, name):
        """
        验证任务名称
        
        Args:
            name: 任务名称
            
        Returns:
            tuple: (是否有效, 清理后的名称)
        """
        if not name or not name.strip():
            return True, "下载任务"
        
        cleaned = name.strip()[:50]
        
        forbidden = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(c in cleaned for c in forbidden):
            self.logger.warning(f"任务名称包含非法字符: {cleaned}")
            return False, ""
        
        return True, cleaned

    @staticmethod
    def get_default_path():
        """获取默认保存路径"""
        from pathlib import Path
        default_path = str(Path.home() / "Downloads")
        abs_path = os.path.abspath(default_path)
        return os.path.normpath(abs_path)