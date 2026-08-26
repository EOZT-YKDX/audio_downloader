# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/8/24
# Program Name: data_processor - converter - main

import os
import time
import logging
import subprocess

from datetime import datetime

from ..read_constants import read_constants

# 视频转音频处理
def convert_video_to_audio(input_path: str, output_path: str, constants: dict, logger: logging.Logger) -> str:
    """
    通过 ffmpeg 命令行工具将视频文件转换为音频文件。
    :param input_path: 视频输入路径。
    :param output_path: 音频输出路径。
    :param constants: 转换配置。
    :param logger: 日志记录器。
    :return: 转换后的音频文件路径。
    """

    start_time = datetime.now()

    if not os.path.isfile(input_path):
        logger.error(f"输入文件路径无效: {input_path}")
        return ""

    if not os.path.isdir(output_path):
        logger.error(f"输出目录路径无效: {output_path}")
        return ""
    
    # 读取转换配置
    constants_result = read_constants(constants=constants, logger=logger)
    convert_retry = constants_result["convert_retry"]
    convert_audio_format = constants_result["convert_audio_format"]

    # 获取文件名称
    file_name = os.path.basename(input_path)
    # 格式化后缀
    formatted_suffix = convert_audio_format.lstrip(".")

    # 构建输出文件路径
    output_file_suffix = f".{formatted_suffix}"
    output_file_name = os.path.splitext(file_name)[0]
    output_file = os.path.join(output_path, output_file_name + output_file_suffix)

    ffmpeg_command = [
        "ffmpeg",                   # 调用 ffmpeg 命令行工具
        "-y",                       # 自动覆盖输出文件,不会提示用户确认
        "-i", input_path,           # 输入文件的完整路径
        "-vn",                      # 禁用视频流,只处理音频
        "-ac", "2",                 # 置音频为2声道 - 立体声    
        "-f", formatted_suffix,     # 音频输出格式
        output_file,                # 输出文件的完整路径
    ]

    # 重试机制
    for attempt in range(convert_retry):
        command_result = subprocess.run(
            ffmpeg_command,
            text=True,              # 以文本模式处理输出
            errors="replace",       # 替换错误字符
            encoding="utf-8",       # 编码为 utf-8
            capture_output=True     # 捕获标准输出和错误输出
        )

        if command_result.returncode == 0:
            logger.info(f"视频转换音频成功: {file_name} - 累计时长: {datetime.now() - start_time}")
            return output_file

        if attempt < convert_retry - 1:
            waiting_time = min(2 ** attempt, 5)
            logger.debug(f"视频转换音频失败, 等待 {waiting_time} 秒后开始第 {attempt + 1} 次重试")
            time.sleep(waiting_time)
    
    logger.error(f"重试 {convert_retry} 次后, 视频 {file_name} 转换成音频失败, 已跳过本次转换")
    return ""