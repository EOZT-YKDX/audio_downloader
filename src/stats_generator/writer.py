# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/24
# Program Name: stats_generator - writer

import logging

# 写入统计文件
def write_stats_to_file(data: str, output_path: str, logger: logging.Logger) -> None:
    """
    将统计信息写入文件。
    :param data: 格式化后的数据。
    :param output_path: 输出文件路径。
    :param logger: 日志记录器。
    :return: None
    """

    try:
        with open(mode="a+", encoding="utf-8", file=output_path) as file:
            file.write(data)

        logger.debug(f"信息统计已写入文件: {output_path}")
    except Exception as error:
        logger.error(f"信息统计失败: {error}")
