# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/27
# Program Name: audio_compressor - website_interaction

import time
import logging

from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.by import By

# 上传文件
def upload_file(browser: webdriver.Edge, file_path: str, constants: dict, logger: logging.Logger) -> bool:
    """
    将文件上传到压缩网站, 并等待上传完成。
    :param browser: 浏览器实例。
    :param file_path: 文件路径。
    :param constants: 配置字典，包含 compression_timeout, compressed_file_name 等参数。
    :param logger: 日志记录器。
    :return: 是否上传成功。
    """

    # 读取配置参数
    compression_timeout = constants["compression_timeout"]
    compressed_file_name = constants["compressed_file_name"]

    # 获取超时时间
    upload_timeout = compression_timeout["upload_timeout"]

    try:
        # 等待上传按钮加载
        upfile_button = ui.WebDriverWait(browser, upload_timeout).until(
            lambda d: d.find_element(By.NAME, "upfile")
        )

        # 上传文件
        upfile_button.send_keys(file_path)
        logger.debug(f"文件上传成功 - {compressed_file_name}")
        return True
    except Exception as error:
        logger.error(f"文件上传失败 - {compressed_file_name}: {error}")
        return False

# 提交压缩请求
def submit_compression_request(browser: webdriver.Edge, constants: dict, logger: logging.Logger) -> bool:
    """
    提交压缩请求, 并等待压缩完成。
    :param browser: 浏览器实例。
    :param constants: 配置字典，包含 compression_timeout, compressed_file_name 等参数。
    :param logger: 日志记录器。
    :return: 是否提交成功。
    """

    # 读取配置参数
    compression_timeout = constants["compression_timeout"]
    compressed_file_name = constants["compressed_file_name"]
    
    # 获取超时时间
    submit_timeout = compression_timeout["submit_timeout"]
    compress_timeout = compression_timeout["compress_timeout"]

    try:
        # 等待提交按钮加载
        submit_button = ui.WebDriverWait(browser, submit_timeout).until(
            lambda d: d.find_element(By.ID, "submitbutton")
        )

        # 提交文件
        submit_button.click()

        # 等待压缩完成提示
        ui.WebDriverWait(browser, compress_timeout).until(
            lambda d: d.find_element(By.CLASS_NAME, "result-message")
        )
        logger.debug(f"压缩请求提交成功 - {compressed_file_name}")
        return True
    except Exception as error:
        logger.error(f"压缩请求提交失败 - {compressed_file_name}: {error}")
        return False

# 获取压缩后的文件链接
def get_compressed_file_link(browser: webdriver.Edge, constants: dict, logger: logging.Logger) -> str:
    """
    获取压缩后的文件链接, 用于下载压缩后的文件。
    :param browser: 浏览器实例。
    :param constants: 配置字典，包含 get_link_retry, compression_timeout, compressed_file_name 等参数。
    :param logger: 日志记录器。
    :return: 压缩后的文件链接。
    """
    
    # 读取配置参数
    get_link_retry = constants["get_link_retry"]
    compression_timeout = constants["compression_timeout"]
    compressed_file_name = constants["compressed_file_name"]

    # 获取超时时间
    seek_timeout = compression_timeout["seek_timeout"]
    
    for attempt in range(get_link_retry):
        try:
            # 查找下载链接
            download_link = ui.WebDriverWait(
                browser, seek_timeout
            ).until(lambda d: d.find_element(By.XPATH, "//a[contains(@href, \"download.php\")]"))

            href = download_link.get_attribute("href")
            return href
        except Exception:
            logger.debug(f"未找到指定的下载链接, 开始查找指定的状态提示元素 - {compressed_file_name}")
        
        try:
            element = browser.find_element(By.XPATH, "/html/body/section[1]/div/div/div[2]/div[2]")
            element_text = element.text

            if "已完成：文件已经压缩完成" in element_text:
                logger.debug(f"文件已经过压缩，无需重复压缩: {compressed_file_name}")
                return ""
        
            if "错误：不支持文件扩展名" in element_text:
                logger.error(f"压缩文件链接获取失败: 文件扩展名不支持 - {compressed_file_name}")
                return ""
        except Exception:
            logger.debug(f"未找到指定的状态提示元素 - {compressed_file_name}")
        
        if attempt < get_link_retry - 1:
            waiting_time = min(2 ** attempt, 5)
            
            logger.debug(f"压缩文件链接获取失败, 等待 {waiting_time} 秒后开始第 {attempt + 1} 次重试 - {compressed_file_name}")
            time.sleep(waiting_time)

    logger.error(f"压缩文件链接获取尝试次数超过 {get_link_retry} 次, 已停止本次压缩 - {compressed_file_name}")
    return ""
