# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/26
# Program Name: task_executor - downloader - download_task

import logging
import tempfile

from metadata_editor import set_audio_metadata
from data_processor import convert_video_to_audio
from network_client import download_bilibili_video

# 处理视频下载任务
def process_video_download(download_link: str, video_name: str, output_path: str, constants: dict, logger: logging.Logger) -> str:
    """
    处理视频下载任务，包括下载视频、格式转换和处理音轨元数据。
    :param download_link: 视频下载链接。
    :param video_name: 视频标题。
    :param output_path: 输出路径。
    :param constants: 配置字典, 包含 max_download_workers 等参数。
    :param logger: 日志记录器。
    :return: 下载的音频文件路径。
    """
    
    with tempfile.TemporaryDirectory() as temp_folder:
        logger.info(f"开始下载视频: {video_name}")
        
        # 下载视频
        file_path = download_bilibili_video(
            video_name=video_name,
            output_path=temp_folder,
            download_link=download_link,
            constants=constants,
            logger=logger,
        )

        if not file_path:
            return ""

        # 格式转换
        output_file = convert_video_to_audio(
            input_path=file_path,
            output_path=output_path,
            constants=constants,
            logger=logger,
        )
        
        if not output_file:
            return ""
        
        # 处理音轨元数据
        set_audio_metadata(
            input_path=output_file,
            constants=constants,
            logger=logger,
        )
        
        return output_file