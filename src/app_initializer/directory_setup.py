# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/30
# Program Name: app_initializer - directory_setup

import os
import logging

# 创建目录
def create_directory(dir_name: str, output_path: str, subdirectory: dict, logger: logging.Logger) -> dict:
    """
    自动创建文件夹，返回绝对路径。
    :param dir_name: 目录名称。
    :param output_path: 输出路径。
    :param subdirectory: 子目录结构。
    :param logger: 日志记录器。
    :return: 初始化后的路径字典。
    """

    subdirectory_result = {}
    dir_path = os.path.join(output_path, dir_name)

    # 路径拼接
    for key, value in subdirectory.items():
        if not key or not value:
            continue

        try:
            subdirectory_result[key] = os.path.join(dir_path, value)
        except Exception as error:
            logger.error(f"路径拼接错误: {error} - {value}")

    # 创建子目录
    for key, value in list(subdirectory_result.items()):
        # 跳过已存在的目录
        if os.path.isdir(value):
            continue

        try:
            os.makedirs(value, exist_ok=True)
            logger.debug(f"已创建目录: {value}")
        except Exception as error:
            logger.error(f"目录创建失败: {error} - {value}")
            subdirectory_result.pop(key)

    logger.debug(f"路径初始化已完成")
    return subdirectory_result
