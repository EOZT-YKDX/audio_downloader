# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/28
# Program Name: stats_generator - main

import os
import logging

from datetime import datetime

from .writer import write_stats_to_file
from .formatter import format_video_data
from .read_constants import read_constants

# 生成统计信息
def generate_statistics(data: dict, output_path: str, constants: dict, logger: logging.Logger) -> None:
    """
    统计B站下载视频的数据信息。
    :param data: B站视频数据信息。
    :param output_path: 信息统计文件输出路径。
    :param constants: 配置参数。
    :param logger: 日志记录器。
    :return: None
    """

    start_time = datetime.now()

    if not os.path.isdir(output_path):
        logger.error(f"信息统计文件输出目录无效: {output_path}")
        return
    
    # 读取配置参数
    constants_result = read_constants(constants=constants, logger=logger)
    stats_file_name = constants_result["stats_file_name"]

    # 格式化数据
    formatted_data = format_video_data(data=data, constants=constants_result)

    create_time = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(output_path, f"{stats_file_name}_{create_time}.txt")
    
    # 写入文件
    write_stats_to_file(data=formatted_data, output_path=file_path, logger=logger)
    logger.info(f"信息统计完成 - 累计时长: {datetime.now() - start_time}")
