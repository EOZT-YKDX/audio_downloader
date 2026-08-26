# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/29
# Program Name: task_executor - compressor - main

import os
import logging

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..read_constants import read_constants
from .get_pending_files import get_pending_files
from .compress_task import process_audio_compression

# 并发压缩音频
def concurrent_compression(input_path: str, output_path: str, constants: dict, logger: logging.Logger) -> None:
    """
    并发处理音频压缩, 支持自定义配置和日志记录。
    :param input_path: 输入路径, 包含待压缩的音频文件。
    :param output_path: 输出路径。
    :param constants: 配置字典, 包含 max_compress_workers 等参数。
    :param logger: 日志记录器。
    :return: None
    """

    start_time = datetime.now()
    
    # 参数验证
    if not os.path.isdir(input_path):
        logger.error(f"音频输入目录无效: {input_path}")
        return
    
    if not os.path.isdir(output_path):
        logger.error(f"音频输出目录无效: {output_path}")
        return

    failed = 0
    skipped = 0
    successed = 0
    
    futures = []
    
    # 读取配置
    constants_result = read_constants(constants=constants, logger=logger)
    max_workers = constants_result["max_compress_workers"]
    
    # 获取所有待压缩的音频文件
    pending_files = get_pending_files(input_path=input_path, output_path=output_path, logger=logger)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有压缩任务到线程池
        for file_path in pending_files:
            # 为每个压缩任务创建一个 future
            future = executor.submit(
                process_audio_compression,
                file_path=file_path,
                output_path=output_path,
                constants=constants,
                logger=logger,
            )
            futures.append(future)
        
        # 遍历已完成的任务，处理结果
        for future in as_completed(futures):
            try:
                # 获取任务执行结果
                result = future.result()
                
                if result:
                    logger.debug(f"压缩任务完成: {result}")
                    successed += 1
                else:
                    logger.error(f"压缩任务失败")
                    failed += 1
                    
            except Exception as error:
                logger.error(f"压缩任务执行异常: {error}")
                failed += 1
    
    # 统计压缩结果
    total = len(pending_files)

    if total:
        logger.info(f"并发压缩完成 - 总数: {total} - 成功: {successed} - 失败: {failed} - 跳过: {skipped} - 累计时长: {datetime.now() - start_time}")