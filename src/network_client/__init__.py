# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/26
# Program Name: network_client - __init__

from .crawler import crawl_favorites
from .downloader import download_compress_file, download_bilibili_video

__all__ = [
    "crawl_favorites",
    "download_compress_file",
    "download_bilibili_video",
]