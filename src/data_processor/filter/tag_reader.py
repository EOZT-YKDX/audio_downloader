# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/22
# Date Modified: 2026/7/29
# Program Name: data_processor - filter - tag_reader

import os
import logging

from mutagen.id3 import ID3

# 获取已下载文件的标签
def get_existing_tags(dir_path: str, logger: logging.Logger) -> set:
    """
    获取已下载音频文件的标签集合，包括子目录下的所有文件。
    :param dir_path: 音频目录路径。
    :return: 已下载标签集合。
    """

    file_tag = set()

    if not os.path.isdir(dir_path):
        logger.error(f"音频保存目录路径无效: {dir_path}")
        return file_tag

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)

            if not os.path.isfile(file_path):
                continue
            
            try:
                audio_file = ID3(file_path)
                audio_tags = audio_file.getall("TIT3")

                tag = str(audio_tags[0])
            except Exception as error:
                logger.debug(f"标签读取出错: {file_path} - {error}")
                continue

            if not tag:
                continue

            file_tag.add(tag)

    return file_tag