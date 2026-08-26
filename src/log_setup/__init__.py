# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/23
# Date Modified: 2026/7/23
# Program Name: log_setup - __init__

from .file_log import setup_file_log
from .terminal_log import setup_terminal_log

__all__ = [
    "setup_file_log",
    "setup_terminal_log"
]
