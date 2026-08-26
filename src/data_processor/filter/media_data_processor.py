# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/22
# Date Modified: 2026/7/27
# Program Name: data_processor - filter - media_data_processor

import logging

from datetime import datetime, timedelta

# 处理媒体数据
def process_media_data(filtered_media: dict, constants: dict, logger: logging.Logger) -> dict:
    """
    处理过滤后的媒体数据，提取核心字段并格式化。
    :param filtered_media: 过滤后的媒体数据。
    :param constants: 配置字典。
    :param logger: 日志记录器。
    :return: 处理后的媒体数据。
    """

    media_result = {}

    filter_title = constants["filter_title"]
    filter_cover = constants["filter_cover"]
    media_pubtime = constants["media_pubtime"]
    media_duration = constants["media_duration"]
    cnt_info_fields = constants["cnt_info_fields"]

    for bvid, media in filtered_media.items():
        media_result[bvid] = {}
        cnt_info = media.get("cnt_info", {})

        # 处理核心数据
        for field in cnt_info_fields:
            media_result[bvid][field] = cnt_info.get(field, "0")

        # 处理标题
        media_title = media.get("title", filter_title)
        media_result[bvid]["title"] = media_title
        
        # 处理封面
        media_cover = media.get("cover", filter_cover)
        media_result[bvid]["cover"] = media_cover

        # 处理视频时长
        try:
            media_result[bvid]["duration"] = media_duration
            duration_value = media.get("duration")

            if duration_value:
                duration_value = int(duration_value)
                media_result[bvid]["duration"] = (datetime.min + timedelta(seconds=duration_value)).strftime("%H:%M:%S")
        except Exception as error:
            logger.error(f"{media_title} - 视频时长处理失败: {error}")

        # 处理发布日期
        try:
            media_result[bvid]["pubtime"] = media_pubtime
            pubtime_value = media.get("pubtime")
            
            if pubtime_value:
                media_result[bvid]["pubtime"] = datetime.fromtimestamp(pubtime_value).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as error:
            logger.error(f"{media_title} - 发布日期处理失败: {error}")

    return media_result