# -*- coding:utf-8 -*- #

"""文件处理器"""

import os
import base64
import logging
from pathlib import Path

import webview


class FileHandler:
    """文件选择与处理管理器"""

    IMAGE_MIME_TYPES = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
    }

    def __init__(self, logger=None):
        """
        初始化文件处理器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)

    def select_folder(self, current_path=""):
        """
        选择文件夹
        
        Args:
            current_path: 当前路径（用于定位对话框初始位置）
            
        Returns:
            str: 选择的文件夹路径，失败返回空字符串
        """
        try:
            initial_dir = current_path if current_path and os.path.isdir(current_path) else str(Path.home())
            file_path = webview.windows[0].create_file_dialog(
                dialog_type=webview.FileDialog.FOLDER,
                directory=initial_dir
            )
            if file_path and len(file_path) > 0:
                selected_path = file_path[0]
                abs_path = os.path.abspath(selected_path)
                normalized_path = os.path.normpath(abs_path)
                self.logger.info(f"选择的文件夹: {normalized_path}")
                return normalized_path
            return ""
        except Exception as e:
            self.logger.error(f"选择文件夹失败: {e}")
            return ""

    def select_image(self, current_path=""):
        """
        选择图片文件并返回 base64 编码
        
        Args:
            current_path: 当前路径（用于定位对话框初始位置）
            
        Returns:
            dict: {"path": str, "data": str} 图片路径和 base64 数据
        """
        try:
            initial_dir = current_path if current_path and os.path.isdir(current_path) else str(Path.home())
            file_path = webview.windows[0].create_file_dialog(
                dialog_type=webview.FileDialog.OPEN,
                directory=initial_dir,
                allow_multiple=False,
                file_types=("Image Files (*.png;*.jpg;*.jpeg;*.gif;*.webp;*.bmp)", "All Files (*.*)"),
            )
            if file_path and len(file_path) > 0:
                return self._process_image_file(file_path[0])
            return {"path": "", "data": ""}
        except Exception as e:
            self.logger.error(f"选择图片失败: {e}")
            return {"path": "", "data": ""}

    def get_image_data(self, image_path):
        """
        根据图片路径返回 base64 编码
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            dict: {"path": str, "data": str} 图片路径和 base64 数据
        """
        if not image_path or not os.path.exists(image_path):
            return {"path": "", "data": ""}
        
        try:
            return self._process_image_file(image_path)
        except Exception as e:
            self.logger.error(f"读取图片失败: {e}")
            return {"path": "", "data": ""}

    def _process_image_file(self, file_path):
        """
        处理图片文件，读取并转换为 base64
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            dict: {"path": str, "data": str} 图片路径和 base64 数据
        """
        abs_path = os.path.abspath(file_path)
        normalized_path = os.path.normpath(abs_path)
        self.logger.info(f"选择的图片: {normalized_path}")
        
        with open(normalized_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        ext = os.path.splitext(normalized_path)[1].lower()
        mime_type = self.IMAGE_MIME_TYPES.get(ext, 'image/png')
        
        return {
            "path": normalized_path,
            "data": f"data:{mime_type};base64,{image_base64}"
        }