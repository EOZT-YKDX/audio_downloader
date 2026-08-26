# -*- coding:utf-8 -*-

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/23
# Date Modified: 2026/7/28
# Program Name: log_setup - file_log

import os
import logging

from datetime import datetime
from logging.handlers import RotatingFileHandler

from .read_constants import read_constants

# 文件日志
def setup_file_log(output_path: str, constants: dict) -> logging.Logger:
    """
    配置日志记录器的文件输出流。
    :param output_path: 日志文件的输出路径。
    :param constants: 日志文件的配置参数, 包含 logger, logger_name, logger_format, logger_level, logger_encoding, logger_max_bytes, logger_backup_count 等参数。
    :return: 配置好的日志记录器。
    """

    start_time = datetime.now()

    existing_file_handler = False

    constants_result = read_constants(constants=constants)
    logger = constants_result["logger"]
    logger_name = constants_result["logger_name"]
    logger_level = constants_result["logger_level"]
    logger_format = constants_result["logger_format"]
    logger_encoding = constants_result["logger_encoding"]
    logger_max_bytes = constants_result["logger_max_bytes"]
    logger_backup_count = constants_result["logger_backup_count"]

    # 检查输出目录是否存在
    if not os.path.isdir(output_path):
        logger.error(f"输出目录无效: {output_path}")
        return logger

    # 文件输出流
    file_handler = RotatingFileHandler(
        encoding=logger_encoding,                           # 编码格式
        maxBytes=logger_max_bytes,                          # 单个日志文件大小
        backupCount=logger_backup_count,                    # 备份数量
        filename=os.path.join(output_path, logger_name),    # 日志文件路径
    )

    # 设置文件日志等级
    file_handler.setLevel(logger_level)
    # 设置文件日志格式
    file_handler.setFormatter(logger_format)
    
    # 检测是否已存在相同类型的 FileHandler，避免重复添加
    for handler in logger.handlers:
        if not isinstance(handler, RotatingFileHandler):
            continue
        
        existing_file_handler = True
        break
        
    if not existing_file_handler:
        # 将文件处理器添加到文件日志记录器
        logger.addHandler(file_handler)

    logger.debug(f"文件日志配置完成 - 累计时长: {datetime.now() - start_time}")
    return logger