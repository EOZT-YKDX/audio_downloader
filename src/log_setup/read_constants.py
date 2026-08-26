# -*- coding:utf-8 -*-

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/23
# Date Modified: 2026/8/3
# Program Name: log_setup - read_constants

import codecs
import logging

from datetime import datetime

from .constants import (
    LOGGER, DEFAULT_LOGGER_NAME, DEFAULT_LOGGER_LEVEL, DEFAULT_LOGGER_FORMAT,
    DEFAULT_LOGGER_BACKUP_COUNT, DEFAULT_LOGGER_ENCODING, DEFAULT_LOGGER_MAX_BYTES,
    )

# 读取配置参数
def read_constants(constants: dict) -> dict:
    """
    读取日志配置文件，返回日志配置参数的字典。
    :param constants: 日志配置参数, 包含 logger, logger_name, logger_format, logger_level, logger_encoding, logger_max_bytes, logger_backup_count 等参数。
    :return: 日志配置参数的字典。
    """

    # 获取配置参数
    logger = constants.get("logger", LOGGER)

    logger_name = constants.get("logger_name", DEFAULT_LOGGER_NAME)
    logger_level_str = constants.get("logger_level", DEFAULT_LOGGER_LEVEL)
    logger_encoding = constants.get("logger_encoding", DEFAULT_LOGGER_ENCODING)

    logger_format = constants.get("logger_format", DEFAULT_LOGGER_FORMAT)
    logger_max_bytes = constants.get("logger_max_bytes", DEFAULT_LOGGER_MAX_BYTES)
    logger_backup_count = constants.get("logger_backup_count", DEFAULT_LOGGER_BACKUP_COUNT)
    
    # 检查参数是否有效
    if not isinstance(logger, logging.Logger) or not logger:
        logger = LOGGER

    
    if not isinstance(logger_name, str) or not logger_name:
        logger_name = DEFAULT_LOGGER_NAME

    if not isinstance(logger_encoding, str) or not logger_encoding:
        logger_encoding = DEFAULT_LOGGER_ENCODING

    
    if not isinstance(logger_format, str) or not logger_format:
        logger_format = DEFAULT_LOGGER_FORMAT

    if not isinstance(logger_backup_count, int) or not 0 < logger_backup_count < 20:
        logger_backup_count = DEFAULT_LOGGER_BACKUP_COUNT

    if not isinstance(logger_max_bytes, int) or not 0 < logger_max_bytes < 100*1024*1024:
        logger_max_bytes = DEFAULT_LOGGER_MAX_BYTES


     # 将日志级别字符串转换为整数
    if isinstance(logger_level_str, int):
        logger_level = logger_level_str
    elif isinstance(logger_level_str, str):
        logger_level = getattr(logging, logger_level_str, DEFAULT_LOGGER_LEVEL)
    else:
        logger_level = DEFAULT_LOGGER_LEVEL

    # 设置日志记录器等级
    logger.setLevel(logger_level)
    # 日志文件名
    log_name = f"{logger_name}{datetime.now().strftime('%Y-%m-%d')}.log"
    
    try:
        # 处理日志格式
        processed_log_format = logging.Formatter(logger_format)
    except Exception as error:
        logger_format = DEFAULT_LOGGER_FORMAT
        processed_log_format = logging.Formatter(logger_format)

    # 检查编码是否有效
    try:
        codecs.lookup(logger_encoding)
    except Exception as error:
        logger_encoding = DEFAULT_LOGGER_ENCODING

    constants_result = {
        "logger": logger,

        "logger_name": log_name,
        "logger_level": logger_level,
        "logger_encoding": logger_encoding,

        "logger_max_bytes": logger_max_bytes,
        "logger_format": processed_log_format,
        "logger_backup_count": logger_backup_count,
    }
    
    return constants_result
