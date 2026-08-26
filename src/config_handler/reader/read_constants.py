# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/23
# Program Name: config_handler - reader - read_constants

import logging

from ..constants import DEFAULT_ORIGINAL_CONFIG, DEFAULT_CONFIG_FILE_NAME

# 读取常量
def read_constants(constants: dict, logger: logging.Logger) -> dict:
    """
    读取配置常量。
    :param constants: 常量字典。
    :param logger: 日志记录器。
    :return: 常量字典。
    """
    
    # 获取配置参数
    file_name = constants.get("file_name", DEFAULT_CONFIG_FILE_NAME)
    original_config = constants.get("original_config", DEFAULT_ORIGINAL_CONFIG)

    # 校验配置参数
    if not isinstance(original_config, dict) or not original_config:
        logger.error(f"原始配置项无效, 已设置为默认值")
        original_config = DEFAULT_ORIGINAL_CONFIG

    if not isinstance(file_name, str) or not file_name:
        logger.error(f"配置文件名配置项无效, 已设置为默认值")
        file_name = DEFAULT_CONFIG_FILE_NAME

    # 构建常量字典
    constants_result = {
        "file_name": file_name,
        "original_config": original_config,
    }

    return constants_result