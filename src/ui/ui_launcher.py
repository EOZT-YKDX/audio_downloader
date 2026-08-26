# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/08/02
# Date Modified: 2026/08/02
# Program Name: ui - ui_launcher

import os
import ctypes
import webview

# 定义JS API
class js_api:
    def __init__(self) -> None:
        pass
        
    def minimize(self) -> None:
        """
        最小化窗口
        :param: None
        :return: None
        """

        webview.windows[0].minimize()
        
    def close(self) -> None:
        """
        关闭当前窗口
        :param: None
        :return: None
        """

        webview.windows[0].destroy()

# 获取屏幕中心坐标。
def get_screen_center() -> tuple:
    """
    获取屏幕中心坐标, 并返回窗口中心坐标。
    :param: None
    :return: tuple
    """

    # 获取屏幕中心坐标
    user32 = ctypes.windll.user32

    # 获取屏幕宽度和高度
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # 计算窗口中心坐标
    x = (screen_width - 900) // 2
    y = (screen_height - 700) // 2

    return x, y

# 窗口关闭事件
def closed() -> None:
    """
    窗口关闭事件, 用于处理窗口关闭时的操作。
    :param: None
    :return: None
    """

    pass

def loaded() -> None:
    """
    窗口加载完成事件, 用于处理窗口加载完成后执行的操作。
    :param: None
    :return: None
    """

# 主函数
def main() -> None:
    """
    主函数, 启动Webview窗口。
    :param: None
    :return: None
    """
    
    ui_dir = os.path.dirname(__file__)
    index_html = os.path.join(ui_dir, "index.html")

    width = 900
    height = 700

    min_size = (800, 600)

    title = "Audio Downloader"
    
    center_x, center_y = get_screen_center()
    
    window = webview.create_window(
        x=center_x,
        y=center_y,
        title=title,
        width=width,
        height=height,
        url=index_html,
        resizable=True,
        frameless=True,
        js_api=js_api(),
        min_size=min_size,
    )

    # 绑定事件
    window.events.loaded += loaded
    window.events.closed += closed

    # 启动Webview循环
    webview.start(debug=False)


if __name__ == "__main__":
    main()