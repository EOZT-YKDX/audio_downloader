# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/24
# Date Modified: 2026/7/24
# Program Name: metadata_editor - formats - __init__

from .mp3 import set_mp3_metadata
from .flac import set_flac_metadata

__all__ = [
    "set_mp3_metadata",
    "set_flac_metadata",
]
