# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/11/17
# Program Name: task_executor - compressor - compress_task

import os
import shutil
import logging
import tempfile

from audio_compressor import compress_file

# 将下载文件移动到输出目录
def _move_to_output(source_file: str, output_path: str, file_name: str, logger: logging.Logger) -> str:
    """
    将压缩后的文件移动到输出目录, 目标文件已存在时先删除。
    :param source_file: 源文件路径。
    :param output_path: 输出目录。
    :param file_name: 目标文件名。
    :param logger: 日志记录器。
    :return: 目标文件路径, 失败时返回空字符串。
    """

    final_file = os.path.join(output_path, file_name)

    try:
        # 目标文件已存在时先删除, 避免移动失败
        if os.path.isfile(final_file):
            os.remove(final_file)
            logger.debug(f"已删除已存在的目标文件: {final_file}")

        # 优先使用移动, 跨盘时自动复制后删除源文件
        shutil.move(source_file, final_file)
        logger.debug(f"压缩文件已移动到: {final_file}")
        return final_file
    except Exception as error:
        logger.error(f"压缩文件移动失败: {source_file} - {error}")
        return ""

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

        # 压缩文件, 浏览器下载器将文件存入临时目录
        download_result = compress_file(
            file_path=file_path,
            constants=constants,
            logger=logger,
            download_dir=temp_folder,
        )

        if not download_result:
            return None

        # 移动到目标路径
        final_file = _move_to_output(
            source_file=download_result,
            output_path=output_path,
            file_name=file_name,
            logger=logger,
        )

        return final_file if final_file else None