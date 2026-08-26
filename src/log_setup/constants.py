# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/23
# Date Modified: 2026/7/29
# Program Name: log_setup - constants

"""
默认常量配置模块。
提供日志配置常量和安全的日志记录器获取方法。
"""

import logging

DEFAULT_LOGGER_NAME = "AudioDownloader"
# 创建日志记录器
LOGGER = logging.getLogger(DEFAULT_LOGGER_NAME)

DEFAULT_LOGGER_ENCODING = "UTF-8"
DEFAULT_LOGGER_LEVEL = logging.DEBUG

DEFAULT_LOGGER_BACKUP_COUNT = 5
DEFAULT_LOGGER_MAX_BYTES = 5*1024*1024 # 5MB
DEFAULT_LOGGER_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"