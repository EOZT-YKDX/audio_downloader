# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/26
# Program Name: network_client - downloader - formatter

import re
import logging

from urllib.parse import urlparse

# 提取视频ID
def _extract_video_id(url: str) -> str:
    """
    从URL中提取视频ID。
    :param url: 包含视频ID的URL。
    :return: 提取的视频ID。
    """

    # 如果是纯ID，直接返回
    if re.match(r'^BV[0-9A-Za-z]{10}$', url.strip()):
        return url.strip()
    
    # 如果是av号，直接返回
    if re.match(r'^av\d+$', url.strip()):
        return url.strip()
    
    # 解析URL
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').split('/')
    
    for part in path_parts:
        if re.match(r'^BV[0-9A-Za-z]{10}$', part):
            return part
        
        if re.match(r'^av\d+$', part):
            return part
    
    return None

# 格式化下载链接
def formatted_link(bvid: str, constants: dict, logger: logging.Logger) -> str:
    """
    格式化下载链接确保其包含完整的bilibili视频链接。
    :param bvid: 视频ID或av号。
    :param constants: 配置字典, 包含 task_bilibili_url 等参数。
    :param logger: 日志记录器。
    :return: 格式化后的下载链接。
    """

    if not isinstance(bvid, str):
        logger.error("视频ID必须为字符串")
        return ""

    url = bvid.strip()
    parsed = urlparse(url)
    network_video_url = constants["network_video_url"]

    # 如果已经是完整URL，直接返回URL
    if parsed.scheme in ("http", "https") and parsed.netloc.endswith("bilibili.com") and "/video/" in parsed.path:
        return url
    
    # 提取视频ID
    video_id = _extract_video_id(url=url)
    
    if not video_id:
        logger.error(f"无法识别的B站视频链接格式: {url}")
        return ""
    
    # 构建基础URL
    base_url = f"{network_video_url}{video_id}"
    
    return base_url