# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/27
# Program Name: app_initializer - read_constants

import logging

from .constants import DEFAULT_SUBDIRECTORY, DEFAULT_INIT_DIR_NAME, DEFAULT_DEPENDENCY_TOOLS

# 读取配置参数
def read_constants(constants: dict, logger: logging.Logger) -> dict:
    """
    读取配置参数, 并处理缺失或错误的配置项。
    :param constants: 配置文件内容。
    :param logger: 日志记录器。
    :return: 配置字典。
    """
    
    # 获取配置参数
    subdirectory = constants.get("subdirectory", DEFAULT_SUBDIRECTORY)
    dir_init_name = constants.get("dir_init_name", DEFAULT_INIT_DIR_NAME)
    dependency_tools = constants.get("dependency_tools", DEFAULT_DEPENDENCY_TOOLS)

    # 检查配置项是否有效
    if not isinstance(subdirectory, dict) or not subdirectory:
        logger.error(f"子目录配置项无效, 已设置为默认值")
        subdirectory = DEFAULT_SUBDIRECTORY
        
    if not isinstance(dependency_tools, list) or not dependency_tools:
        logger.error(f"依赖工具配置项无效, 已设置为默认值")
        dependency_tools = DEFAULT_DEPENDENCY_TOOLS

    if not isinstance(dir_init_name, str) or not dir_init_name:
        logger.error(f"初始化目录名称配置项无效, 已设置为默认值")
        dir_init_name = DEFAULT_INIT_DIR_NAME

    # 构建配置字典
    constants_result = {
        "subdirectory": subdirectory,
        "dir_init_name": dir_init_name,
        "dependency_tools": dependency_tools,
    }
    
    return constants_result