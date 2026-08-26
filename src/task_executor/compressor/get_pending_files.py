# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/28
# Date Modified: 2026/7/29
# Program Name: task_executor - compressor - get_pending_files

import os
import logging

from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen import File as MutagenFile

# 获取音频文件的标签
def _get_tags(file_path: str, logger: logging.Logger) -> str:
    """
    获取音频文件的标签, 包括 TIT3 标签和 SUBTITLE 标签。
    :param file_path: 音频文件路径。
    :param logger: 日志记录器。
    :return: 已压缩标签字符串。
    """

    # 使用 mutagen 通用加载器
    audio_file = MutagenFile(file_path, easy=False)

    if audio_file is None:
        logger.debug(f"无法识别的音频格式: {file_path}")
        return ""

    file_tag = ""

    # 检查 MP3 文件的 TIT3 标签
    if isinstance(audio_file, MP3):
        if audio_file.tags is None:
            return ""
        
        tit3_tags = audio_file.tags.getall("TIT3")

        if not tit3_tags:
            return ""
        
        file_tag = tit3_tags[0]

    # 检查 FLAC 文件的 SUBTITLE 标签
    if isinstance(audio_file, FLAC):
        subtitle = audio_file.get("SUBTITLE")

        if not subtitle:
            return ""
        
        file_tag = subtitle[0]

    return str(file_tag)

# 获取所有待压缩的音频文件
def get_pending_files(input_path: str, output_path: str, logger: logging.Logger) -> list:
    """
    获取所有待压缩的音频文件路径。
    :param input_path: 输入目录路径。
    :param output_path: 输出目录路径。
    :param logger: 日志记录器。
    :return: 待压缩音频文件路径列表。
    """
    
    if not os.path.isdir(input_path):
        logger.error(f"音频输入路径无效: {input_path}")
        return []

    if not os.path.isdir(output_path):
        logger.error(f"音频输出路径无效: {output_path}")
        return []

    input_tags = {}
    output_tags = {}

    pending_files = []

    # 获取输入目录下所有文件的标签
    for root, dirs, files in os.walk(input_path):
        for file in files:
            file_path = os.path.join(root, file)

            # 获取文件标签
            tags = _get_tags(file_path=file_path, logger=logger)
            
            if not tags:
                continue
            
            input_tags[tags] = file_path

    # 获取输出目录下所有文件的标签
    for root, dirs, files in os.walk(output_path):
        for file in files:
            file_path = os.path.join(root, file)

            # 获取文件标签
            tags = _get_tags(file_path=file_path, logger=logger)

            if not tags:
                continue

            output_tags[tags] = file_path

    # 过滤出未压缩的音频文件
    for tag in input_tags:
        if tag in output_tags:
            continue

        pending_files.append(input_tags[tag])

    return pending_files