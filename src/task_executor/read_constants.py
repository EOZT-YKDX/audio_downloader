# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/29
# Program Name: task_executor - read_constants

import logging

from .constants import DEFAULT_TASK_BILIBILI_URL, DEFAULT_MAX_DOWNLOAD_WORKERS, DEFAULT_MAX_COMPRESS_WORKERS

# 读取配置参数
def read_constants(constants: dict, logger: logging.Logger) -> dict:
    """
    读取并发任务配置参数, 并验证配置。
    :param constants: 配置字典, 包含 task_bilibili_url, max_download_workers, max_compress_workers 等参数。
    :param logger: 日志记录器。
    :return: dict: 验证后的并发任务配置。
    """
    
    # 获取配置参数
    task_bilibili_url = constants.get("task_bilibili_url", DEFAULT_TASK_BILIBILI_URL)

    max_download_workers = constants.get("max_download_workers", DEFAULT_MAX_DOWNLOAD_WORKERS)
    max_compress_workers = constants.get("max_compress_workers", DEFAULT_MAX_COMPRESS_WORKERS)
    
    # 检查配置项是否有效
    if not isinstance(max_download_workers, int) or max_download_workers < 1:
        logger.error(f"最大下载工作线程数配置项无效，已设置为默认值")
        max_download_workers = DEFAULT_MAX_DOWNLOAD_WORKERS
        
    if not isinstance(max_compress_workers, int) or max_compress_workers < 1:
        logger.error(f"最大压缩工作线程数配置项无效，已设置为默认值")
        max_compress_workers = DEFAULT_MAX_COMPRESS_WORKERS


    if not isinstance(task_bilibili_url, str) or not task_bilibili_url:
        logger.error(f"Bilibili视频链接基础URL配置项无效, 已设置为默认值")
        task_bilibili_url = DEFAULT_TASK_BILIBILI_URL
    
    # 构建并发任务配置
    constants_result = {
        "task_bilibili_url": task_bilibili_url,

        "max_download_workers": max_download_workers,
        "max_compress_workers": max_compress_workers,
    }
    
    return constants_result
