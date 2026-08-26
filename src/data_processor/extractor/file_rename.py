# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/22
# Date Modified: 2026/7/27
# Program Name: data_processor - extractor - file_rename

import os

# 重命名文件
def rename_file(dir_path: str, new_file: str, original_file: str) -> None:
    """
    重命名文件, 已存在该文件时会自动创建文件夹, 并将相同名称的文件移动到文件夹中, 重命名后的文件名按数字后缀命名。
    :param dir_path: 音频目录路径。
    :param new_file: 重命名后的文件名。
    :param original_file: 原始文件名。
    :return: None
    """

    new_path = os.path.join(dir_path, new_file)
    original_path = os.path.join(dir_path, original_file)

    if not os.path.isfile(original_path):
        raise FileNotFoundError(f"原始文件无效: {original_path}")

    # 如果新文件已存在
    if os.path.isfile(new_path):
        # 分离文件名和扩展名，创建文件夹名称
        folder_name = os.path.splitext(new_file)[0]
        folder_path = os.path.join(dir_path, folder_name)
        
        # 创建文件夹
        os.makedirs(folder_path, exist_ok=True)
        
        # 将已存在的同名文件移动到文件夹中
        existing_file_dest = os.path.join(folder_path, new_file)
        os.rename(new_path, existing_file_dest)
        
        # 将当前处理的原始文件移动到文件夹中
        original_file_dest = os.path.join(folder_path, original_file)
        os.rename(original_path, original_file_dest)
    else:
        # 文件不存在，直接重命名
        os.rename(original_path, new_path)