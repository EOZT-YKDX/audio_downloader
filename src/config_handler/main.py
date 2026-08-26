# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/29
# Program Name: config_handler - main

import os
import logging

from datetime import datetime

from .config_updater import update_config
from .reader import read_config, read_constants

# 管理配置文件
def manage_config_files(config: dict, output_dir: str, logger: logging.Logger) -> dict:
    """
    管理配置文件，更新配置文件，读取配置文件。
    :param config: 配置字典。
    :param output_dir: 输出目录路径。
    :param logger: 日志记录器。
    :return: 配置字典。
    """

    start_time = datetime.now()

    if not os.path.isdir(output_dir):
        logger.error(f"配置文件输出目录无效: {output_dir}")
        return {}
    
    constants = config.get("constants", {})

    constants_data = read_constants(constants=constants, logger=logger)
    file_name = constants_data["file_name"]
    file_path = os.path.join(output_dir, file_name)

    # 更新配置文件
    update_config(config=config, constants=constants_data, output_path=file_path, logger=logger)
    
    # 读取配置文件
    config_result = read_config(input_path=file_path, logger=logger)

    logger.info(f"配置文件读取完成 - {file_name} - 累计时长: {datetime.now() - start_time}")
    return config_result