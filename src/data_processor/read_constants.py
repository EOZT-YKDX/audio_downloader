# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/27
# Program Name: data_processor - read_constants

import logging

from .constants import (
    DEFAULT_CONVERT_RETRY, DEFAULT_CONVERT_AUDIO_FORMAT,
    DEFAULT_FILTER_BVID, DEFAULT_FILTER_TITLE, DEFAULT_FILTER_COVER,
    DEFAULT_MEDIA_DURATION, DEFAULT_MEDIA_PUBTIME, DEFAULT_FILTER_INVALID_CHARS, DEFAULT_MATCHING_METHODS,
    DEFAULT_CNT_INFO_FIELDS, DEFAULT_FILTER_LABELS
)

# 读取配置参数
def read_constants(constants: dict, logger: logging.Logger) -> dict:
    """
    读取配置参数, 并验证参数是否有效。
    :param constants: 配置字典, 包含 convert_retry, convert_audio_format, filter_bvid, filter_title, filter_cover,
    media_pubtime, media_duration, filter_labels, filter_invalid_chars, cnt_info_fields, matching_methods 等参数。
    :param logger: 日志记录器。
    :return: dict: 验证后的分类配置。
    """

    # 获取配置参数
    convert_retry = constants.get("convert_retry", DEFAULT_CONVERT_RETRY)
    convert_audio_format = constants.get("convert_audio_format", DEFAULT_CONVERT_AUDIO_FORMAT)

    filter_bvid = constants.get("filter_bvid", DEFAULT_FILTER_BVID)
    filter_title = constants.get("filter_title", DEFAULT_FILTER_TITLE)
    filter_cover = constants.get("filter_cover", DEFAULT_FILTER_COVER)

    media_pubtime = constants.get("media_pubtime", DEFAULT_MEDIA_PUBTIME)
    media_duration = constants.get("media_duration", DEFAULT_MEDIA_DURATION)

    filter_labels = constants.get("filter_labels", DEFAULT_FILTER_LABELS)
    filter_invalid_chars = constants.get("filter_invalid_chars", DEFAULT_FILTER_INVALID_CHARS)
    
    cnt_info_fields = constants.get("cnt_info_fields", DEFAULT_CNT_INFO_FIELDS)
    matching_methods = constants.get("matching_methods", DEFAULT_MATCHING_METHODS)

    # 检查参数是否有效
    if not isinstance(convert_retry, int) or convert_retry <= 0:
        convert_retry = DEFAULT_CONVERT_RETRY
        logger.error(f"转换重试次数配置项无效 - 已设置为默认值")
        
    if not isinstance(convert_audio_format, str) or not convert_audio_format:
        convert_audio_format = DEFAULT_CONVERT_AUDIO_FORMAT
        logger.error(f"转换音频格式配置项无效 - 已设置为默认值")
        

    if not isinstance(filter_bvid, str) or not filter_bvid:
        filter_bvid = DEFAULT_FILTER_BVID
        logger.error(f"过滤BVID配置项无效 - 已设置为默认值")
        
    if not isinstance(filter_title, str) or not filter_title:
        filter_title = DEFAULT_FILTER_TITLE
        logger.error(f"过滤标题配置项无效 - 已设置为默认值")
        
    if not isinstance(filter_cover, str) or not filter_cover:
        filter_cover = DEFAULT_FILTER_COVER
        logger.error(f"过滤封面配置项无效 - 已设置为默认值")

    
    if not isinstance(media_duration, str) or not media_duration:
        media_duration = DEFAULT_MEDIA_DURATION
        logger.error(f"时长配置项无效 - 已设置为默认值")
    
    if not isinstance(media_pubtime, str) or not media_pubtime:
        media_pubtime = DEFAULT_MEDIA_PUBTIME
        logger.error(f"发布时间配置项无效 - 已设置为默认值")


    if not isinstance(filter_labels, list) or not filter_labels:
        filter_labels = DEFAULT_FILTER_LABELS
        logger.error(f"过滤标签格式无效 - 已恢复为默认值")
    
    if not isinstance(filter_invalid_chars, str) or not filter_invalid_chars:
        filter_invalid_chars = DEFAULT_FILTER_INVALID_CHARS
        logger.error(f"过滤无效字符配置项无效 - 已设置为默认值")
        
    
    if not isinstance(cnt_info_fields, list) or not cnt_info_fields:
        cnt_info_fields = DEFAULT_CNT_INFO_FIELDS
        logger.error(f"计数字段格式无效 - 已恢复为默认值")
    
    
    if not isinstance(matching_methods, list) or not matching_methods:
        matching_methods = DEFAULT_MATCHING_METHODS
        logger.error(f"匹配方法格式无效 - 已恢复为默认值")

    # 合并配置参数
    classifier_config = {
        "convert_retry": convert_retry,
        "convert_audio_format": convert_audio_format,
        
        "filter_bvid": filter_bvid,
        "filter_title": filter_title,
        "filter_cover": filter_cover,

        "media_pubtime": media_pubtime,
        "media_duration": media_duration,

        "filter_labels": filter_labels,
        "filter_invalid_chars": filter_invalid_chars,
        
        "cnt_info_fields": cnt_info_fields,
        "matching_methods": matching_methods,
    }
    
    return classifier_config