# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/22
# Date Modified: 2026/7/29
# Program Name: data_processor - extractor - main

import os
import logging

from datetime import datetime

from .file_rename import rename_file
from .matcher import extract_keywords
from ..read_constants import read_constants

# 提取音频名称并重命名文件
def extract_and_rename_files(dir_path: str, constants: dict, logger: logging.Logger) -> None:
    """
    提取音频名称并重命名文件, 当出现相同名称时，停止重命名，将文件移动到对应文件夹中。
    :param dir_path: 音频目录路径。
    :param constants: 配置参数字典。
    :param logger: 日志记录器，用于记录处理过程中的信息。
    :return: None
    """

    start_time = datetime.now()

    if not os.path.isdir(dir_path):
        logger.error(f"音频目录路径无效: {dir_path}")
        return
    
    moved = 0
    failed = 0
    succeeded = 0
    invalidity = 0

    # 读取配置参数
    constants_result = read_constants(constants=constants, logger=logger)

    # 建立原始文件的映射
    file_mapping = {}

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)

            # 跳过目录
            if os.path.isdir(file_path):
                continue
                
            try:
                matches = extract_keywords(file=file, constants=constants_result, logger=logger)
            except Exception as error:
                logger.error(f"提取关键字失败: {error}")
                failed += 1
                continue

            if not matches:
                logger.debug(f"未找到有效匹配: {file}")
                invalidity += 1
                continue
            
            # 格式化文件名, 同时移除重复项
            file_suffix = os.path.splitext(file)[1]
            file_name = list(dict.fromkeys(matches))
            new_file = " - ".join(file_name) + file_suffix

            # 添加到映射
            if new_file not in file_mapping:
                file_mapping[new_file] = []

            file_mapping[new_file].append(file_path)

    # 处理映射
    for new_file, original_paths in file_mapping.items():
        if len(original_paths) > 1:
            # 有重复名称，创建文件夹并移动所有文件, 保留原文件名
            folder_name = os.path.splitext(new_file)[0]
            folder_path = os.path.join(dir_path, folder_name)
            
            # 创建文件夹
            os.makedirs(folder_path, exist_ok=True)
            
            for original_path in original_paths:
                original_file = os.path.basename(original_path)
                dest_path = os.path.join(folder_path, original_file)
                
                # 检查是否已经在目标文件夹中
                if os.path.dirname(original_path) == folder_path:
                    logger.debug(f"文件已在目标文件夹中: {original_file}")
                    moved += 1
                    continue
                
                try:
                    os.rename(original_path, dest_path)
                    logger.info(f"文件移动成功: {original_file} -> {folder_name}/{original_file}")
                    moved += 1
                except Exception as error:
                    logger.error(f"文件移动失败: {error}")
                    failed += 1
        else:
            # 直接重命名
            original_path = original_paths[0]
            original_file = os.path.basename(original_path)

            try:
                rename_file(dir_path=dir_path, new_file=new_file, original_file=original_file)
                logger.info(f"文件重命名成功: {original_file} -> {new_file}")
                succeeded += 1
            except Exception as error:
                logger.error(f"文件重命名失败: {error}")
                failed += 1

    total = succeeded + moved + failed + invalidity
    logger.info(f"名称重命名完成 - 总计: {total} - 成功: {succeeded} 移动: {moved} 失败: {failed} 无效: {invalidity} - 累计时长: {datetime.now() - start_time}")
