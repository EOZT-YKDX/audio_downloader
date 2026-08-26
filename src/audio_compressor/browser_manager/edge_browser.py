# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/8/5
# Program Name: audio_compressor - browser_manager - edge_browser

import os
import time
import logging
import msedgedriver

from datetime import datetime
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.edge.options import Options

# 获取随机浏览器 User-Agent
def _get_user_agent(constants: dict, logger: logging.Logger) -> str:
    """
    获取随机浏览器 User-Agent, 获取失败时返回默认 User-Agent。
    :param constants: 浏览器配置字典, 包含 browser_user_agent 等参数。
    :param logger: 日志记录器。
    :return: 随机 User-Agent。
    """
    
    # 读取配置参数
    browser_user_agent = constants["browser_user_agent"]
    
    ua = UserAgent(fallback=browser_user_agent)
    ua_random = ua.random

    if ua_random:
        logger.debug(f"随机 User-Agent 获取成功 - {ua_random}")
        return ua_random
    else:
        logger.error(f"随机 User-Agent 获取失败, 使用默认 User-Agent - {browser_user_agent}")
        return browser_user_agent

# 设置Edge浏览器选项
def _set_edge_options(constants: dict, logger: logging.Logger) -> Options:
    """
    设置Edge浏览器选项, 包括页面加载策略、用户代理、浏览器选项、实验选项等参数。
    :param constants: 浏览器配置字典, 包含 edge_args, experimental_options 等参数。
    :param logger: 日志记录器。
    :return: 设置后的Edge浏览器选项对象。
    """

    start_time = datetime.now()

    # 读取配置参数
    edge_args = constants["edge_args"]
    experimental_options = constants["experimental_options"]

    # 浏览器选项配置
    edge_options = Options()
    # 设置页面加载策略为 eager 以减少页面加载时间
    edge_options.page_load_strategy = "eager"

    ua = _get_user_agent(constants=constants, logger=logger)
    # 设置用户代理
    edge_options.add_argument(f"user-agent={ua}")

    # 添加浏览器选项
    for arg in edge_args:
        edge_options.add_argument(arg)
    
    # 设置实验选项
    edge_options.add_experimental_option("prefs", experimental_options)

    logger.debug(f"Edge浏览器选项设置成功 - 累计时长: {datetime.now() - start_time}")
    return edge_options

# 初始化Edge浏览器
def init_edge_browser(constants: dict, logger: logging.Logger) -> webdriver.Edge:
    """
    初始化Edge浏览器, 用于访问目标 URL。
    :param constants: 浏览器配置字典, 包含 install_retry, driver_install_path, browser_user_agent,
    edge_args, experimental_options, compression_url 等参数。
    :param logger: 日志记录器。
    :return: 初始化后的Edge浏览器对象。 
    """

    start_time = datetime.now()

    # 读取配置参数
    compression_url = constants["compression_url"]
    
    # 设置Edge浏览器选项
    edge_options = _set_edge_options(constants=constants, logger=logger)

    # 获取Edge浏览器实例
    browser = webdriver.Edge(options=edge_options)

    # 访问目标 URL
    browser.get(compression_url)

    logger.info(f"Edge浏览器初始化成功 - 累计时长: {datetime.now() - start_time}")
    return browser

# 关闭Edge浏览器
def close_edge_browser(browser: webdriver.Edge, logger: logging.Logger) -> None:
    """
    关闭Edge浏览器, 释放资源。
    :param browser: Edge浏览器实例对象。
    :param logger: 日志记录器。
    :return: None
    """
    
    start_time = datetime.now()

    if not browser:
        logger.info("无Edge浏览器实例, 无需关闭")
        return

    try:
        browser.quit()
        logger.info(f"成功关闭Edge浏览器 - 累计时长: {datetime.now() - start_time}")
    except Exception as error:
        logger.error(f"关闭Edge浏览器时失败: {error}")