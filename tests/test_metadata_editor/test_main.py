# -*- coding:utf-8 -*-

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/8/3
# Date Modified: 2026/8/5
# Program Name: tests - test_metadata_editor - test_main

import os
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))

from src.log_setup import setup_terminal_log
from src.metadata_editor import set_audio_metadata

constants = {}
dir_path = r"C:\Users\Lenovo\Music"
logger = setup_terminal_log(constants=constants)

for root, dirs, files in os.walk(dir_path):
    new_constants = {
        "metadata_artist": os.path.basename(root),
    }

    for file in files:
        input_path = os.path.join(root, file)

        if not os.path.isfile(input_path):
            continue

        set_audio_metadata(input_path=input_path, constants=new_constants, logger=logger)

