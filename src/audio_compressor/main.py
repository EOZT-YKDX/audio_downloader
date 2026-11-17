# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/11/17
# Program Name: audio_compressor - main

import os
import logging

from datetime import datetime

from .read_constants import read_constants
from .browser_manager import init_edge_browser, close_edge_browser
from .download_manager import snapshot_directory, wait_for_download
from .website_interaction import upload_file, submit_compression_request, click_download_button

# 压缩文件
def compress_file(file_path: str, constants: dict, logger: logging.Logger, download_dir: str) -> str:
    """
    压缩文件, 并返回浏览器下载完成的文件路径。
    :param file_path: 文件存储路径。
    :param constants: 配置字典，包含 browser_user_agent, edge_args, experimental_options,
    compression_url, compressed_file_name, compression_timeout 等参数。
    :param logger: 日志记录器。
    :param download_dir: 浏览器下载目录, 用于存放压缩后的文件。
    :return: 下载完成的文件路径, 失败时返回空字符串。
    """

    start_time = datetime.now()

    # 校验文件是否存在
    if not os.path.isfile(file_path):
        logger.error(f"待压缩文件不存在 - {file_path}")
        return ""

    # 校验下载目录, 不存在时自动创建
    if not download_dir:
        logger.error("浏览器下载目录未指定")
        return ""

    try:
        os.makedirs(download_dir, exist_ok=True)
    except Exception as error:
        logger.error(f"浏览器下载目录创建失败: {download_dir} - {error}")
        return ""

    browser = None

    # 设置文件名
    file_name = os.path.basename(file_path)
    
    constants_copy = constants.copy()
    constants_copy["compressed_file_name"] = file_name

    # 读取配置文件
    constants_result = read_constants(constants=constants_copy, logger=logger)

    try:
        # 初始化Edge浏览器
        browser = init_edge_browser(constants=constants_result, logger=logger, download_dir=download_dir)

        if not browser:
            return ""
    
        # 上传文件
        upload_result = upload_file(browser=browser, file_path=file_path, constants=constants_result, logger=logger)
        
        if not upload_result:
            return ""

        # 提交压缩请求
        submit_result = submit_compression_request(browser=browser, constants=constants_result, logger=logger)

        if not submit_result:
            return ""

        # 记录下载目录快照, 用于识别本次新增的下载文件
        before_files = snapshot_directory(download_dir=download_dir, logger=logger)

        # 点击下载按键
        download_result = click_download_button(browser=browser, constants=constants_result, logger=logger)

        if not download_result:
            return ""

        # 读取下载超时时间
        download_timeout = constants_result["compression_timeout"]["download_timeout"]

        # 等待浏览器下载完成
        downloaded_file = wait_for_download(
            download_dir=download_dir,
            before_files=before_files,
            timeout=download_timeout,
            logger=logger,
        )

        if not downloaded_file:
            return ""

        logger.info(f"文件压缩完成 - {file_name} - 累计时长: {datetime.now() - start_time}")
        return downloaded_file
    except Exception as error:
        logger.error(f"文件压缩过程发生错误: {file_name} - {error}")
        return ""
    finally:
        # 关闭Edge浏览器
        close_edge_browser(browser=browser, logger=logger)