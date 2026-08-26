# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/28
# Program Name: network_client - crawler - main

import time
import logging

from datetime import datetime

from .request_handler import make_request
from ..read_constants import read_constants

# 爬取收藏夹数据
def crawl_favorites(fid: str, constants: dict, logger: logging.Logger) -> dict:
    """
    调用B站的api接口, 通过fid爬取收藏夹的相关数据。
    :param fid: B站收藏夹特定序列。
    :param constants: 爬取配置,包含 network_retry 等参数。
    :param logger: 日志记录器。
    :return: dict: 返回爬取的收藏夹数据。
    """

    start_time = datetime.now()

    # 读取爬取配置
    crawl_config = read_constants(constants=constants, logger=logger)
    network_retry = crawl_config["network_retry"]

    # 重试机制
    for attempt in range(network_retry):
        try:
            response_result = make_request(fid=fid, logger=logger, constants=crawl_config)
            
            if isinstance(response_result, dict) and response_result:
                logger.info(f"收藏夹 {fid} 数据爬取成功 - 累计时长: {datetime.now() - start_time}")
                return response_result
            
        except Exception as error:
            logger.error(f"收藏夹 {fid} 数据爬取错误: {error}")
        
        if attempt < network_retry - 1:
            waiting_time = min(2 ** attempt, 5)
            
            logger.info(f"等待 {waiting_time} 秒后数据爬取启动第 {attempt + 1} 次重试")
            time.sleep(waiting_time)

    logger.error(f"收藏夹 {fid} 数据爬取重试次数过多，已停止本次爬取 - 累计时长: {datetime.now() - start_time}")
    return {}