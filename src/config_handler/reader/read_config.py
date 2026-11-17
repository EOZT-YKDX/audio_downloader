# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/8/3
# Date Modified: 2026/8/31
# Program Name: config_handler - reader - read_config

import os
import yaml
import logging

# 读取配置文件
def read_config(input_path: str, logger: logging.Logger) -> dict:
    """
    读取配置文件。
    :param input_path: 配置文件路径。
    :param logger: 日志记录器。
    :return: 配置字典。
    """

    if not os.path.isfile(input_path):
        logger.error(f"配置文件不存在: {input_path}")
        return {}

    try:
        with open(mode="r", encoding="utf-8", file=input_path) as file:
            config = yaml.safe_load(file)

        if not config:
            logger.error(f"无法读取配置文件: {input_path}")
            return {}
        
        return config
    except Exception as error:
        logger.error(f"无法读取配置文件: {input_path} - {error}")
        return {}