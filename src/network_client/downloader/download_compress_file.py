# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/28
# Program Name: network_client - downloader - download_compress_file

import os
import time
import logging
import requests

from datetime import datetime

from ..read_constants import read_constants

# 下载压缩文件
def download_compress_file(file_name: str, output_path: str, download_link: str, constants: dict, logger: logging.Logger) -> str:
    """
    通过 requests 下载通用文件。
    :param file_name: 文件名称。
    :param output_path: 文件输出路径。
    :param download_link: 下载链接。
    :param constants: 下载配置。
    :param logger: 日志记录器。
    :return: 下载的文件路径。
    """

    start_time = datetime.now()

    if not os.path.isdir(output_path):
        logger.error(f"文件输出路径无效: {output_path}")
        return ""

    # 读取下载配置
    constants_result = read_constants(constants=constants, logger=logger)
    network_retry = constants_result["network_retry"]
    network_origin = constants_result["network_origin"]
    network_referer = constants_result["network_referer"]
    network_user_agent = constants_result["network_user_agent"]
    network_download_timeout = constants_result["network_download_timeout"]

    logger.info(f"开始下载压缩文件: {file_name}")
    output_file = os.path.join(output_path, file_name)

    # 设置浏览器请求头
    headers = {
        "Origin": network_origin,
        "Referer": network_referer,
        "User-Agent": network_user_agent,
    }

    # 重试机制
    for attempt in range(network_retry):
        try:            
            response = requests.get(download_link, headers=headers, timeout=network_download_timeout, stream=True)
            response.raise_for_status()

            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            if os.path.isfile(output_file):
                logger.debug(f"文件下载成功: {file_name} - 累计时长: {datetime.now() - start_time}")
                return output_file
        except Exception as error:
            logger.error(f"压缩文件下载失败: {error}")

        if attempt < network_retry - 1:
            waiting_time = min(2 ** attempt, network_download_timeout)
            logger.debug(f"压缩文件下载失败, 等待 {waiting_time} 秒后开始第 {attempt + 1} 次重试")
            time.sleep(waiting_time)

    logger.error(f"文件下载重试过多，已跳过本次下载: {file_name} - 累计时长: {datetime.now() - start_time}")
    return ""