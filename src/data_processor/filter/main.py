# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/27
# Program Name: data_processor - filter - main

import os
import logging

from datetime import datetime

from .tag_reader import get_existing_tags
from ..read_constants import read_constants
from .file_filter import get_pending_download
from .media_data_processor import process_media_data

# 过滤和分类数据
def filter_and_classify_data(data: dict, dir_path: str, constants: dict, logger: logging.Logger) -> dict:
    """
    处理收藏夹数据，返回过滤和分类后的数据。
    :param data: 收藏夹数据。
    :param dir_path: 音乐文件存储路径，用于过滤掉已下载的音频。
    :param constants: 配置文件。
    :param logger: 日志记录器。
    :return: 处理且分类后的收藏夹数据。
    """

    start_time = datetime.now()

    if not os.path.isdir(dir_path):
        logger.error(f"音频目录路径无效: {dir_path}")
        return {}

    media_data = data.get("data", {}).get("mediaList", [])

    if not media_data:
        logger.info("收藏夹媒体数据为空, 无待下载的视频")
        return {}

    # 读取配置
    constants_result = read_constants(constants=constants, logger=logger)
    
    # 获取已下载文件的标签
    existing_tags = get_existing_tags(dir_path=dir_path, logger=logger)

    # 过滤待下载的媒体数据
    filtered_media = get_pending_download(media_data=media_data, existing_tags=existing_tags, constants=constants_result, logger=logger)

    # 处理过滤后的媒体数据
    media_result = process_media_data(filtered_media=filtered_media, constants=constants_result, logger=logger)
    
    logger.info(f"视频数据处理完成 - 待下载数量: {len(media_result)} - 累计时长: {datetime.now() - start_time}")
    return media_result