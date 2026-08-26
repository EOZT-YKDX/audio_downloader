# -*- coding:utf-8 -*-

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/8/5
# Program Name: app_initializer - constants

"""
应用引导常量配置模块。
提供初始化配置常量和安全的初始化函数。
"""

import os

# 默认初始化目录名称
DEFAULT_INIT_DIR_NAME = "AudioDownloader"

# 默认依赖工具
DEFAULT_DEPENDENCY_TOOLS = ["ffmpeg", "you-get"]

# 默认子目录结构
DEFAULT_SUBDIRECTORY = {
    "log": "Log",
    "data": "Data",
    "audio_orig": os.path.join("Music", "OriginalAudio"),
    "audio_comp": os.path.join("Music", "CompressedAudio"),
}

