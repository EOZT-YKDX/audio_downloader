# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/8/24
# Program Name: network_client - crawler - request_handler

import logging
import requests

from fake_useragent import UserAgent

# 发送请求
def make_request(fid: str, constants: dict, logger: logging.Logger) -> dict:
    """
    发送HTTP请求到B站API。
    :param fid: B站收藏夹ID。
    :param constants: 请求配置, 包含 network_origin, network_referer, network_page_size, network_user_agent, network_crawl_timeout 等参数。
    :param logger: 日志记录器。
    :return: 响应结果。
    """

    network_origin = constants["network_origin"]
    network_referer = constants["network_referer"]
    network_page_size = constants["network_page_size"]
    network_user_agent = constants["network_user_agent"]
    network_crawl_timeout = constants["network_crawl_timeout"]

    url = f"https://api.bilibili.com/x/v1/medialist/resource/list?type=3&biz_id={fid}&ps={network_page_size}"
    
    # 随机生成UserAgent
    user_agent = UserAgent(fallback=network_user_agent)
    
    response = requests.get(
        url=url,
        timeout=network_crawl_timeout,
        headers={
            "Origin": network_origin,
            "Referer": network_referer,
            "User-Agent": user_agent.random,
        },
    )

    try:
        response_result = response.json()
        response_code = response_result.get("code")
    except requests.JSONDecodeError:
        logger.error(f"收藏夹 {fid} 数据爬取失败 - JSON 解析错误")
        return {}

    # 检查爬取结果
    if response.status_code == 200 and response_code == 0:
        logger.debug(f"收藏夹 {fid} 数据爬取成功 - 状态码: {response.status_code} - 响应代码: {response_code}")
        return response_result

    logger.error(f"收藏夹 {fid} 数据爬取失败 - 状态码: {response.status_code} - 响应代码: {response_code}")
    return {}