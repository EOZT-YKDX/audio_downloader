# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/29
# Program Name: network_client - read_constants

import logging

from .constants import (
    DEFAULT_NETWORK_RETRY, DEFAULT_NETWORK_PAGE_SIZE,
    DEFAULT_NETWORK_CRAWL_TIMEOUT, DEFAULT_NETWORK_DOWNLOAD_TIMEOUT,
    DEFAULT_NETWORK_VIDEO_URL, DEFAULT_NETWORK_USER_AGENT, DEFAULT_NETWORK_ORIGIN, DEFAULT_NETWORK_REFERER,
    )

# 读取配置参数
def read_constants(constants: dict, logger: logging.Logger) -> dict:
    """
    读取配置参数, 并验证配置。
    :param constants: 配置字典, 包含 network_retry, network_page_size, network_api_url, network_video_url,
    network_crawl_timeout, network_download_timeout, network_origin, network_referer, network_user_agent 等参数。
    :param logger: 日志记录器。
    :return: dict: 验证后的爬取配置。
    """
    
    # 获取配置参数
    network_retry = constants.get("network_retry", DEFAULT_NETWORK_RETRY)
    network_page_size = constants.get("network_page_size", DEFAULT_NETWORK_PAGE_SIZE)

    network_video_url = constants.get("network_video_url", DEFAULT_NETWORK_VIDEO_URL)
    network_user_agent = constants.get("network_user_agent", DEFAULT_NETWORK_USER_AGENT)

    network_crawl_timeout = constants.get("network_crawl_timeout", DEFAULT_NETWORK_CRAWL_TIMEOUT)
    network_download_timeout = constants.get("network_download_timeout", DEFAULT_NETWORK_DOWNLOAD_TIMEOUT)

    network_origin = constants.get("network_origin", DEFAULT_NETWORK_ORIGIN)
    network_referer = constants.get("network_referer", DEFAULT_NETWORK_REFERER)

    # 检查配置项是否有效
    if not isinstance(network_retry, int) or not 1 <= network_retry <= 5:
        logger.error(f"重试次数配置项无效, 已设置为默认值")
        network_retry = DEFAULT_NETWORK_RETRY
    
    if not isinstance(network_page_size, int) or not 1 <= network_page_size <= 200:
        logger.error(f"视频分页大小配置项不在有效范围内 [1, 200]，已设置为默认值")
        network_page_size = DEFAULT_NETWORK_PAGE_SIZE


    if not isinstance(network_origin, str) or not network_origin:
        logger.error(f"Origin配置项无效, 已设置为默认值")
        network_origin = DEFAULT_NETWORK_ORIGIN
    
    if not isinstance(network_referer, str) or not network_referer:
        logger.error(f"Referer配置项无效, 已设置为默认值")
        network_referer = DEFAULT_NETWORK_REFERER


    if not isinstance(network_user_agent, str) or not network_user_agent:
        logger.error(f"用户代理配置项无效, 已设置为默认值")
        network_user_agent = DEFAULT_NETWORK_USER_AGENT

    if not isinstance(network_video_url, str) or not network_video_url:
        logger.error(f"视频 URL配置项无效, 已设置为默认值")
        network_video_url = DEFAULT_NETWORK_VIDEO_URL


    if not isinstance(network_crawl_timeout, int) or not 0 <= network_crawl_timeout <= 10:
        logger.error(f"爬取超时时间配置项不在有效范围内 [0, 10]，已设置为默认值")
        network_crawl_timeout = DEFAULT_NETWORK_CRAWL_TIMEOUT
    
    if not isinstance(network_download_timeout, int) or not 15 <= network_download_timeout <= 200:
        logger.error(f"下载超时时间配置项不在有效范围内 [15, 200]，已设置为默认值")
        network_download_timeout = DEFAULT_NETWORK_DOWNLOAD_TIMEOUT
    
    # 构建配置字典
    constants_result = {
        "network_retry": network_retry,
        "network_page_size": network_page_size,

        "network_origin": network_origin,
        "network_referer": network_referer,
        
        "network_video_url": network_video_url,
        "network_user_agent": network_user_agent,

        "network_crawl_timeout": network_crawl_timeout,
        "network_download_timeout": network_download_timeout,
    }

    return constants_result
