# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/27
# Program Name: app_initializer - main

import os
import logging

from datetime import datetime

from .read_constants import read_constants
from .directory_setup import create_directory
from .dependency_check import check_dependency_tools

# 初始化应用程序
def initialize_app(output_path: str, constants: dict, logger: logging.Logger) -> dict:
    """
    初始化应用程序, 负责配置读取, 依赖检测和目录创建。
    :param output_path: 输出路径。
    :param constants: 配置常量字典, 包含dependency_tools, dir_name, subdirectory等参数。
    :param logger: 日志记录器。
    :return: 初始化结果字典。
    """

    start_time = datetime.now()

    if not os.path.isdir(output_path):
        logger.error(f"初始化目录无效: {output_path}")
        return {}

    # 读取配置文件
    initialize_constants = read_constants(constants=constants, logger=logger)
    subdirectory = initialize_constants["subdirectory"]
    dir_init_name = initialize_constants["dir_init_name"]
    dependency_tools = initialize_constants["dependency_tools"]

    # 检测依赖工具
    detect_result = check_dependency_tools(dependency_tools=dependency_tools, logger=logger)
    # 创建目录结构
    dir_result = create_directory(dir_name=dir_init_name, output_path=output_path, subdirectory=subdirectory, logger=logger)

    init_result = {
        "dir_result": dir_result,
        "detect_result": detect_result,
    }
    
    logger.info(f"{dir_init_name} 初始化已完成 - 累计时长: {datetime.now() - start_time}")
    return init_result