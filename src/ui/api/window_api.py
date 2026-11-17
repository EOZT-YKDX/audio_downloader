# -*- coding:utf-8 -*- #

"""窗口控制 API"""

import ctypes
import ctypes.wintypes
import logging

import webview


class WindowApi:
    """窗口控制 API（供前端 JS 调用）"""

    def __init__(self, file_handler, logger=None):
        """
        初始化窗口 API
        
        Args:
            file_handler: 文件处理器实例
            logger: 日志记录器
        """
        self.file_handler = file_handler
        self.logger = logger or logging.getLogger(__name__)

    def select_folder(self, current_path=""):
        """选择文件夹"""
        return self.file_handler.select_folder(current_path)

    def select_image(self, current_path=""):
        """选择图片"""
        return self.file_handler.select_image(current_path)

    def minimize(self):
        """最小化窗口"""
        webview.windows[0].minimize()

    def close(self):
        """关闭窗口"""
        webview.windows[0].destroy()

    def move_window(self, x, y):
        """移动窗口到指定位置"""
        try:
            x = int(x)
            y = int(y)
            
            if x < -1000 or x > 5000 or y < -1000 or y > 5000:
                self.logger.warning(f"窗口坐标超出合理范围: ({x}, {y})")
                return
            
            window = webview.windows[0]
            window.move(x, y)
        except (ValueError, TypeError):
            self.logger.error(f"窗口坐标格式错误: x={x}, y={y}")
        except AttributeError:
            self._move_window_via_winapi(x, y)
        except Exception as e:
            self.logger.error(f"移动窗口失败: {e}")

    def get_window_position(self):
        """获取窗口当前位置"""
        try:
            window = webview.windows[0]
            return {"x": window.x, "y": window.y}
        except AttributeError:
            return self._get_window_position_via_winapi()
        except Exception as e:
            self.logger.error(f"获取窗口位置失败: {e}")
            return {"x": 0, "y": 0}

    def _move_window_via_winapi(self, x, y):
        """使用 Windows API 移动窗口"""
        try:
            hwnd = webview.windows[0].handle
            if hwnd:
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                ctypes.windll.user32.MoveWindow(
                    hwnd, x, y, 
                    rect.right - rect.left, 
                    rect.bottom - rect.top, 
                    True
                )
        except Exception as e:
            self.logger.error(f"移动窗口失败: {e}")

    def _get_window_position_via_winapi(self):
        """使用 Windows API 获取窗口位置"""
        try:
            hwnd = webview.windows[0].handle
            if hwnd:
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                return {"x": rect.left, "y": rect.top}
        except Exception as e:
            self.logger.error(f"获取窗口位置失败: {e}")
        return {"x": 0, "y": 0}