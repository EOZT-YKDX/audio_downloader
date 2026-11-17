# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/11/17
# Date Modified: 2026/11/17
# Program Name: audio_compressor - download_manager

import os
import time
import logging

from datetime import datetime

# 浏览器未完成下载的临时文件后缀
_PARTIAL_SUFFIXES = (".crdownload", ".part", ".tmp", ".download")

# 获取下载目录内的文件快照
def snapshot_directory(download_dir: str, logger: logging.Logger) -> set:
    """
    获取下载目录内的文件快照, 用于识别本次新增的下载文件。
    :param download_dir: 下载目录。
    :param logger: 日志记录器。
    :return: 文件名集合。
    """

    if not os.path.isdir(download_dir):
        logger.error(f"下载目录无效: {download_dir}")
        return set()

    try:
        return set(os.listdir(download_dir))
    except Exception as error:
        logger.error(f"下载目录读取失败: {download_dir} - {error}")
        return set()

# 等待浏览器下载完成
def wait_for_download(download_dir: str, before_files: set, timeout: int, logger: logging.Logger) -> str:
    """
    等待浏览器下载完成, 并返回下载完成的文件路径。
    :param download_dir: 下载目录。
    :param before_files: 点击下载按键前的文件快照。
    :param timeout: 下载超时时间。
    :param logger: 日志记录器。
    :return: 下载完成的文件路径, 超时或失败时返回空字符串。
    """

    start_time = datetime.now()

    if not os.path.isdir(download_dir):
        logger.error(f"下载目录无效: {download_dir}")
        return ""

    deadline = time.time() + timeout

    stable_file = ""
    stable_size = -1
    stable_count = 0

    while time.time() < deadline:
        current_files = snapshot_directory(download_dir=download_dir, logger=logger)

        # 检查是否仍有未完成的临时文件
        partial_files = [name for name in current_files if name.lower().endswith(_PARTIAL_SUFFIXES)]

        # 筛选本次新增的已下载文件
        new_files = [
            name for name in current_files
            if name not in before_files and not name.lower().endswith(_PARTIAL_SUFFIXES)
        ]

        if new_files and not partial_files:
            # 取最新修改的文件, 避免同名文件被浏览器追加序号后缀导致定位失败
            file_path = os.path.join(
                download_dir,
                max(new_files, key=lambda name: os.path.getmtime(os.path.join(download_dir, name))),
            )

            try:
                file_size = os.path.getsize(file_path)
            except Exception:
                file_size = -1

            # 文件大小连续两次保持不变, 判定下载完成
            if file_path == stable_file and file_size == stable_size and file_size > 0:
                stable_count += 1

                if stable_count >= 2:
                    logger.debug(f"浏览器下载完成: {file_path} - 累计时长: {datetime.now() - start_time}")
                    return file_path
            else:
                stable_file = file_path
                stable_size = file_size
                stable_count = 0

        time.sleep(1)

    logger.error(f"浏览器下载超时: {download_dir} - 累计时长: {datetime.now() - start_time}")
    return ""