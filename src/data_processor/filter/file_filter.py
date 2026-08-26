# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/30
# Program Name: data_processor - filter - file_filter

import logging

# 过滤媒体标题中的无效字符
def _filter_invalid_chars(title: str, filter_invalid_chars: set) -> str:
    """
    过滤标题中的无效字符, 返回过滤后的标题。
    :param title: 原始标题。
    :param filter_invalid_chars: 需要过滤的无效字符集合。
    :return: 过滤后的标题。
    """

    temp_title_list = []

    for character in title:
        if character in filter_invalid_chars:
            continue

        temp_title_list.append(character)

    filter_title = "".join(temp_title_list)
    return filter_title

# 获取待下载的媒体数据
def get_pending_download(media_data: list, existing_tags: set, constants: dict, logger: logging.Logger) -> dict:
    """
    过滤媒体数据，返回待下载的数据。
    :param media_data: 媒体数据列表。
    :param existing_tags: 已下载标签集合。
    :param constants: 配置字典。
    :param logger: 日志记录器。
    :return: 待下载的媒体数据字典。
    """

    media_result = {}

    filter_title = constants["filter_title"]
    filter_invalid_chars = constants["filter_invalid_chars"]

    for media in media_data:
        bvid = media.get("bv_id")
        
        if not bvid:
            continue

        title = media.get("title", filter_title)

        # 过滤无效字符
        media_title = _filter_invalid_chars(title=title, filter_invalid_chars=filter_invalid_chars)

        if media_title in existing_tags:
            logger.debug(f"视频标题已存在: {media_title}")
            continue
        
        media_result[bvid] = media
        media_result[bvid]["title"] = media_title

    return media_result