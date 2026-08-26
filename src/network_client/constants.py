# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/29
# Program Name: network_client - constants

"""
网络操作常量定义
用于定义网络操作相关的常量，如重试次数、分页大小、超时时间等。
"""

# 重试次数
DEFAULT_NETWORK_RETRY = 3

# 分页大小
DEFAULT_NETWORK_PAGE_SIZE = 200

# 请求头
DEFAULT_NETWORK_ORIGIN = "https://www.bilibili.com"
DEFAULT_NETWORK_REFERER = "https://www.bilibili.com"

# B站API
DEFAULT_NETWORK_VIDEO_URL = "https://www.bilibili.com/video/"
DEFAULT_NETWORK_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"

# 网络操作超时时间
DEFAULT_NETWORK_CRAWL_TIMEOUT = 10
DEFAULT_NETWORK_DOWNLOAD_TIMEOUT = 100