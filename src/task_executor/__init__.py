# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/26
# Program Name: task_executor - __init__

from .downloader import concurrent_download
from .compressor import concurrent_compression

__all__ = [
    "concurrent_download",
    "concurrent_compression",
]