# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/29
# Program Name: task_executor - downloader - main

import os
import logging

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .formatter import formatted_link
from ..read_constants import read_constants
from .download_task import process_video_download

# 并发下载视频
def concurrent_download(data: dict, output_path: str, constants: dict, logger: logging.Logger) -> None:
    """
    并发处理视频下载, 支持自定义配置和日志记录。
    :param data: 视频数据字典, 包含待下载的视频信息。
    :param output_path: 输出路径。
    :param constants: 配置字典。
    :param logger: 日志记录器。
    :return: None
    """

    start_time = datetime.now()
    
    if not data:
        return
    
    if not os.path.isdir(output_path):
        logger.error(f"音频输出目录无效: {output_path}")
        return

    failed = 0
    successed = 0
    futures = []

    # 读取配置
    constants_result = read_constants(constants=constants, logger=logger)
    max_workers = constants_result["max_download_workers"]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        
        for bvid, video_data in data.items():
            video_name = video_data.get("title", "未知标题")
            download_link = formatted_link(bvid=bvid, constants=constants, logger=logger)
            
            future = executor.submit(
                process_video_download,
                download_link=download_link,
                video_name=video_name,
                output_path=output_path,
                constants=constants,
                logger=logger,
            )
            futures[future] = video_name
        
        # 遍历已完成的任务，处理结果
        for future in as_completed(futures):
            video_name = futures[future]
            try:
                # 获取任务执行结果
                result = future.result()
                
                if result:
                    logger.debug(f"下载任务完成: {video_name}")
                    successed += 1
                else:
                    logger.error(f"下载任务失败: {video_name}")
                    failed += 1
                    
            except Exception as error:
                logger.error(f"下载任务执行执行异常: {video_name} - {error}")
                failed += 1
    
    # 统计下载结果
    total = len(futures)

    if total:
        logger.info(f"并发下载完成 - 总数: {total} - 成功: {successed} - 失败: {failed} - 累计时长: {datetime.now() - start_time}")