# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/26
# Program Name: network_client - downloader - __init__

from .download_compress_file import download_compress_file
from .download_bilibili_video import download_bilibili_video

__all__ = [
    "download_compress_file",
    "download_bilibili_video",
]