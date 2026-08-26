# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/27
# Program Name: audio_compressor - main

import os
import logging

from datetime import datetime

from .read_constants import read_constants
from .browser_manager import init_edge_browser, close_edge_browser
from .website_interaction import upload_file, submit_compression_request, get_compressed_file_link

# 压缩文件
def compress_file(file_path: str, constants: dict, logger: logging.Logger) -> str:
    """
    压缩文件, 并返回压缩后的文件下载链接。
    :param file_path: 文件存储路径。
    :param constants: 配置字典，包含 install_retry, driver_install_path, browser_user_agent,
    edge_args, experimental_options, compression_url, compressed_file_name, compression_timeout_timeout, get_link_retry 等参数。
    :param logger: 日志记录器。
    :return: 压缩后的文件下载链接。
    """

    start_time = datetime.now()

    # 校验文件是否存在
    if not os.path.isfile(file_path):
        logger.error(f"待压缩文件不存在 - {file_path}")
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
        browser = init_edge_browser(constants=constants_result, logger=logger)

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
        
        # 获取压缩文件下载链接
        download_link = get_compressed_file_link(browser=browser, constants=constants_result, logger=logger)

        if download_link:
            logger.info(f"文件压缩完成 - {file_name} - 累计时长: {datetime.now() - start_time}")
            return download_link
        
        return ""
    except Exception as error:
        logger.error(f"文件压缩过程发生错误: {file_name} - {error}")
        return ""
    finally:
        # 关闭Edge浏览器
        close_edge_browser(browser=browser, logger=logger)