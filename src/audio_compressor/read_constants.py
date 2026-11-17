# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/11/17
# Program Name: audio_compressor - read_constants

import logging

from .constants import (
    DEFAULT_COMPRESSED_FILE_NAME, DEFAULT_COMPRESSION_URL, DEFAULT_BROWSER_USER_AGENT,
    DEFAULT_EDGE_ARGS, DEFAULT_COMPRESSION_TIMEOUT, DEFAULT_EXPERIMENTAL_OPTIONS
    )

# 校验超时时间参数
def _validate_timeout(timeout: dict, logger: logging.Logger) -> dict:
    """
    校验超时时间参数, 并返回校验后的超时时间字典。
    :param timeout: 超时时间字典。
    :param logger: 日志记录器。
    :return: 校验后的超时时间字典。
    """

    # 获取超时时间配置项
    seek_timeout = timeout.get("seek_timeout", DEFAULT_COMPRESSION_TIMEOUT["seek_timeout"])
    upload_timeout = timeout.get("upload_timeout", DEFAULT_COMPRESSION_TIMEOUT["upload_timeout"])
    submit_timeout = timeout.get("submit_timeout", DEFAULT_COMPRESSION_TIMEOUT["submit_timeout"])
    compress_timeout = timeout.get("compress_timeout", DEFAULT_COMPRESSION_TIMEOUT["compress_timeout"])
    download_timeout = timeout.get("download_timeout", DEFAULT_COMPRESSION_TIMEOUT["download_timeout"])

    # 检查超时时间配置项是否有效
    if not isinstance(seek_timeout, int) or seek_timeout <= 0:
        logger.error(f"seek_timeout超时时间配置项无效, 已设置为默认值")
        seek_timeout = DEFAULT_COMPRESSION_TIMEOUT["seek_timeout"]
    
    if not isinstance(upload_timeout, int) or upload_timeout <= 0:
        logger.error(f"upload_timeout超时时间配置项无效, 已设置为默认值")
        upload_timeout = DEFAULT_COMPRESSION_TIMEOUT["upload_timeout"]
    
    if not isinstance(submit_timeout, int) or submit_timeout <= 0:
        logger.error(f"submit_timeout超时时间配置项无效, 已设置为默认值")
        submit_timeout = DEFAULT_COMPRESSION_TIMEOUT["submit_timeout"]
    
    if not isinstance(compress_timeout, int) or compress_timeout <= 0:
        logger.error(f"compress_timeout超时时间配置项无效, 已设置为默认值")
        compress_timeout = DEFAULT_COMPRESSION_TIMEOUT["compress_timeout"]

    if not isinstance(download_timeout, int) or download_timeout <= 0:
        logger.error(f"download_timeout超时时间配置项无效, 已设置为默认值")
        download_timeout = DEFAULT_COMPRESSION_TIMEOUT["download_timeout"]

    # 构建超时时间字典
    timeout_result = {
        "seek_timeout": seek_timeout,
        "upload_timeout": upload_timeout,
        "submit_timeout": submit_timeout,
        "compress_timeout": compress_timeout,
        "download_timeout": download_timeout,
    }

    return timeout_result

# 读取配置文件
def read_constants(constants: dict, logger: logging.Logger) -> dict:
    """
    读取配置文件, 返回配置字典。
    :param constants: 配置字典。
    :param logger: 日志记录器。
    :return: 配置字典。
    """
    
    # 获取配置参数
    compressed_file_name = constants.get("compressed_file_name", DEFAULT_COMPRESSED_FILE_NAME)

    compression_url = constants.get("compression_url", DEFAULT_COMPRESSION_URL)
    browser_user_agent = constants.get("browser_user_agent", DEFAULT_BROWSER_USER_AGENT)

    edge_args = constants.get("edge_args", DEFAULT_EDGE_ARGS)
    experimental_options = constants.get("experimental_options", DEFAULT_EXPERIMENTAL_OPTIONS)

    compression_timeout = constants.get("compression_timeout", DEFAULT_COMPRESSION_TIMEOUT)
    
    # 校验配置
    if not isinstance(compressed_file_name, str) or not compressed_file_name:
        logger.error(f"压缩后的文件名配置项无效, 已设置为默认值")
        compressed_file_name = DEFAULT_COMPRESSED_FILE_NAME

    if not isinstance(browser_user_agent, str) or not browser_user_agent:
        logger.error(f"浏览器User-Agent配置项无效, 已设置为默认值")
        browser_user_agent = DEFAULT_BROWSER_USER_AGENT

    if not isinstance(compression_url, str) or not compression_url:
        logger.error(f"压缩网站URL配置项无效, 已设置为默认值")
        compression_url = DEFAULT_COMPRESSION_URL

    if not isinstance(edge_args, list) or not edge_args:
        logger.error(f"Edge参数配置项无效, 已设置为默认值")
        edge_args = DEFAULT_EDGE_ARGS
    
    if not isinstance(experimental_options, dict) or not experimental_options:
        logger.error(f"实验选项配置项无效, 已设置为默认值")
        experimental_options = DEFAULT_EXPERIMENTAL_OPTIONS

    # 校验超时时间参数
    compression_timeout = _validate_timeout(timeout=compression_timeout, logger=logger)

    # 构建配置字典
    constants_result = {
        "compressed_file_name": compressed_file_name,

        "compression_url": compression_url,
        "browser_user_agent": browser_user_agent,

        "edge_args": edge_args,
        "experimental_options": experimental_options,

        "compression_timeout": compression_timeout,
    }

    return constants_result