# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/20
# Program Name: audio_compressor - browser_manager - __init__

from .edge_browser import init_edge_browser
from .edge_browser import close_edge_browser

__all__ = [
    "init_edge_browser",
    "close_edge_browser"
]