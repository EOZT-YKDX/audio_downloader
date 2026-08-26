# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/29
# Program Name: stats_generator - read_constants

import logging

from .constants import (
    DEFAULT_STATS_COIN, DEFAULT_STATS_PLAY, DEFAULT_STATS_REPLY, DEFAULT_STATS_SHARE,
    DEFAULT_STATS_DANMAKU, DEFAULT_STATS_COLLECT, DEFAULT_STATS_THUMB_UP, DEFAULT_STATS_BVID, DEFAULT_STATS_TITLE,
    DEFAULT_STATS_COVER, DEFAULT_STATS_DURATION, DEFAULT_STATS_PUBTIME, DEFAULT_STATS_FILE_NAME, DEFAULT_STATS_DIVIDING_LINE
    )

# 读取配置参数
def read_constants(constants: dict, logger: logging.Logger) -> dict:
    """
    读取信息统计配置参数。
    :param constants: 配置字典, 包含 stats_coin, stats_play, stats_bvid, stats_title, stats_cover, stats_reply,
    stats_share, stats_collect, stats_danmaku, stats_pubtime, stats_duration, stats_thumb_up, stats_file_name, stats_dividing_line 等参数。
    :param logger: 日志记录器。
    :return: dict: 验证后的统计配置。
    """
    
    # 获取配置参数
    stats_coin = constants.get("stats_coin", DEFAULT_STATS_COIN)
    stats_play = constants.get("stats_play", DEFAULT_STATS_PLAY)
    stats_reply = constants.get("stats_reply", DEFAULT_STATS_REPLY)
    stats_share = constants.get("stats_share", DEFAULT_STATS_SHARE)
    stats_collect = constants.get("stats_collect", DEFAULT_STATS_COLLECT)
    stats_danmaku = constants.get("stats_danmaku", DEFAULT_STATS_DANMAKU)
    stats_thumb_up = constants.get("stats_thumb_up", DEFAULT_STATS_THUMB_UP)

    stats_bvid = constants.get("stats_bvid", DEFAULT_STATS_BVID)
    stats_title = constants.get("stats_title", DEFAULT_STATS_TITLE)
    stats_cover = constants.get("stats_cover", DEFAULT_STATS_COVER)

    stats_pubtime = constants.get("stats_pubtime", DEFAULT_STATS_PUBTIME)
    stats_duration = constants.get("stats_duration", DEFAULT_STATS_DURATION)

    stats_file_name = constants.get("stats_file_name", DEFAULT_STATS_FILE_NAME)
    stats_dividing_line = constants.get("stats_dividing_line", DEFAULT_STATS_DIVIDING_LINE)
 
    # 检查配置项是否有效
    if not isinstance(stats_coin, int):
        logger.error(f"硬币数量配置项无效, 已设置为默认值")
        stats_coin = DEFAULT_STATS_COIN

    if not isinstance(stats_play, int):
        logger.error(f"播放数量配置项无效, 已设置为默认值")
        stats_play = DEFAULT_STATS_PLAY

    if not isinstance(stats_reply, int):
        logger.error(f"回复数量配置项无效, 已设置为默认值")
        stats_reply = DEFAULT_STATS_REPLY

    if not isinstance(stats_share, int):
        logger.error(f"分享数量配置项无效, 已设置为默认值")
        stats_share = DEFAULT_STATS_SHARE

    if not isinstance(stats_danmaku, int):
        logger.error(f"弹幕数量配置项无效, 已设置为默认值")
        stats_danmaku = DEFAULT_STATS_DANMAKU

    if not isinstance(stats_collect, int):
        logger.error(f"收藏数量配置项无效, 已设置为默认值")
        stats_collect = DEFAULT_STATS_COLLECT

    if not isinstance(stats_thumb_up, int):
        logger.error(f"点赞数量配置项无效, 已设置为默认值")
        stats_thumb_up = DEFAULT_STATS_THUMB_UP


    if not isinstance(stats_bvid, str) or not stats_bvid:
        logger.error(f"BVID配置项无效, 已设置为默认值")
        stats_bvid = DEFAULT_STATS_BVID

    if not isinstance(stats_title, str) or not stats_title:
        logger.error(f"标题配置项无效, 已设置为默认值")
        stats_title = DEFAULT_STATS_TITLE

    if not isinstance(stats_cover, str) or not stats_cover:
        logger.error(f"封面配置项无效, 已设置为默认值")
        stats_cover = DEFAULT_STATS_COVER


    if not isinstance(stats_duration, str) or not stats_duration:
        logger.error(f"时长配置项无效, 已设置为默认值")
        stats_duration = DEFAULT_STATS_DURATION

    if not isinstance(stats_pubtime, str) or not stats_pubtime:
        logger.error(f"发布时间配置项无效, 已设置为默认值")
        stats_pubtime = DEFAULT_STATS_PUBTIME


    if not isinstance(stats_file_name, str) or not stats_file_name:
        logger.error(f"统计文件名配置项无效, 已设置为默认值")
        stats_file_name = DEFAULT_STATS_FILE_NAME
    
    if not isinstance(stats_dividing_line, dict) or not stats_dividing_line:
        logger.error(f"分隔线配置项无效, 已设置为默认值")
        stats_dividing_line = DEFAULT_STATS_DIVIDING_LINE

    # 格式化分隔线
    filler = stats_dividing_line["filler"]
    length = stats_dividing_line["length"]
    stats_dividing_line = filler.center(length, filler)

    # 构建配置结果
    constants_result = {
        "stats_coin": stats_coin,
        "stats_play": stats_play,
        "stats_reply": stats_reply,
        "stats_share": stats_share,
        "stats_collect": stats_collect,
        "stats_danmaku": stats_danmaku,
        "stats_thumb_up": stats_thumb_up,

        "stats_bvid": stats_bvid,
        "stats_title": stats_title,
        "stats_cover": stats_cover,

        "stats_pubtime": stats_pubtime,
        "stats_duration": stats_duration,

        "stats_file_name": stats_file_name,
        "stats_dividing_line": stats_dividing_line,
    }
    
    return constants_result
