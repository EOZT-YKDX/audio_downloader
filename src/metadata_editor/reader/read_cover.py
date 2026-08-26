# -*- coding:utf-8 -*-

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/3
# Date Modified: 2026/7/24
# Program Name: metadata_editor - reader - read_cover

import logging
import filetype

# 读取封面数据
def read_cover(cover_file: str, logger: logging.Logger) -> dict:
    """
    读取封面数据, 并返回封面数据的字节流和封面类型。
    :param cover_file: 封面文件路径。
    :param logger: 日志记录器。
    :return: 封面数据的字典，包含封面数据的字节流和封面类型。
    """

    try:
        cover_type = filetype.guess_mime(cover_file)

        # 检查封面文件类型是否为图片
        if not filetype.is_image(cover_file):
            logger.error(f"封面非图片类型: {cover_type} - {cover_file}")
            return {}

        with open(file=cover_file, mode="rb") as cover_info:
            cover_data = cover_info.read()

        cover_result = {
            "cover_data": cover_data,
            "cover_type": cover_type
            }       

        return cover_result
    except Exception as error:
        logger.error(f"封面文件数据读取失败: {error}")
        return {}
