# -*- coding:utf-8 -*-

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/23
# Date Modified: 2026/7/28
# Program Name: log_setup - terminal_log

import logging

from datetime import datetime

from .read_constants import read_constants

# 终端日志
def setup_terminal_log(constants: dict) -> logging.Logger:
    """
    配置日志记录器的终端输出流。
    :param constants: 日志终端的配置参数, 包含 logger, logger_level, logger_format 等参数。
    :return: 配置好的日志记录器。
    """

    start_time = datetime.now()

    existing_stream_handler = False

    constants_result = read_constants(constants=constants)
    logger = constants_result["logger"]
    logger_level = constants_result["logger_level"]
    logger_format = constants_result["logger_format"]

    # 终端输出流
    terminal_handler = logging.StreamHandler()
    
    # 设置终端日志等级
    terminal_handler.setLevel(logger_level)
    # 设置终端日志格式
    terminal_handler.setFormatter(logger_format)

    # 检测是否已存在相同类型的 StreamHandler，避免重复添加
    for handler in logger.handlers:
        if not isinstance(handler, logging.StreamHandler):
            continue
        
        existing_stream_handler = True
        break
    
    if not existing_stream_handler:
        # 将日志记录器添加到终端日志记录器
        logger.addHandler(terminal_handler)

    logger.debug(f"终端日志配置完成 - 累计时长: {datetime.now() - start_time}")
    return logger

