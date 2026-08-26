# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/8/1
# Program Name: network_client - downloader - download_bilibili_video

import os
import time
import logging
import subprocess

from datetime import datetime

from ..read_constants import read_constants

# 下载B站视频
def download_bilibili_video(video_name: str, output_path: str, download_link: str, constants: dict, logger: logging.Logger) -> str:
    """
    通过 you-get 命令行工具下载B站视频。
    :param video_name: 视频名称。
    :param output_path: 视频输出路径。
    :param download_link: 包含bvid序列的下载链接。
    :param constants: 下载配置, 包含 network_retry, network_download_timeout 等参数。
    :param logger: 日志记录器。
    :return: 下载的文件路径。
    """

    start_time = datetime.now()

    if not os.path.isdir(output_path):
        logger.error(f"视频输出路径无效: {output_path}")
        return ""

    # 读取下载配置
    constants_result = read_constants(constants=constants, logger=logger)
    network_retry = constants_result["network_retry"]
    network_download_timeout = constants_result["network_download_timeout"]

    you_get_command = [
        "you-get",
        download_link,
        "--no-caption",
        "-O", video_name,
        "-o", output_path,
    ]

    # 重试机制
    for attempt in range(network_retry):
        try:
            command_result = subprocess.run(
                you_get_command,
                text=True,
                errors="replace",
                encoding="utf-8",
                capture_output=True,
                timeout=network_download_timeout
            )

            if not command_result.returncode == 0:
                continue

            # 查找下载的文件
            for file in os.listdir(output_path):
                if not file.startswith(video_name):
                    continue
                
                file_path = os.path.join(output_path, file)
                logger.debug(f"视频下载成功: {video_name} - 累计时长: {datetime.now() - start_time}")
                return file_path
        except Exception as error:
            logger.error(f"视频下载失败: {video_name}: {error}")
        
        if attempt < network_retry - 1:
            waiting_time = min(2 ** attempt, 5)
            logger.debug(f"视频下载失败: {video_name}, 等待 {waiting_time} 秒后开始第 {attempt + 1} 次重试")
            time.sleep(waiting_time)

    logger.error(f"B站视频下载重试次数过多, 已跳过本次下载: {video_name} - 累计时长: {datetime.now() - start_time}")
    return ""