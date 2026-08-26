# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/8/1
# Program Name: task_executor - compressor - compress_task

import os
import logging
import tempfile

from audio_compressor import compress_file
from network_client import download_compress_file

# 处理音频压缩任务
def process_audio_compression(file_path: str, output_path: str, constants: dict, logger: logging.Logger) -> str:
    """
    处理音频压缩任务，包括压缩音频和下载压缩后的文件。
    :param file_path: 待压缩的音频文件路径。
    :param output_path: 输出路径。
    :param constants: 配置字典。
    :param logger: 日志记录器。
    :return: 压缩后的文件路径。
    """
    
    file_name = os.path.basename(file_path)

    with tempfile.TemporaryDirectory() as temp_folder:
        logger.info(f"开始压缩文件: {file_name}")

        # 压缩文件
        download_link = compress_file(
            file_path=file_path,
            constants=constants,
            logger=logger,
        )

        if not download_link:
            return None

        # 下载压缩后的文件
        temp_file = download_compress_file(
            file_name=file_name,
            output_path=temp_folder,
            download_link=download_link,
            constants=constants,
            logger=logger,
        )

        # 构建目标路径
        final_file = os.path.join(output_path, file_name)

        # 移动到目标路径
        os.rename(temp_file, final_file)
        logger.debug(f"压缩文件: {file_name} 已移动到: {final_file}")
        
        return final_file
