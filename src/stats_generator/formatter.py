# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/28
# Program Name: stats_generator - formatter

from datetime import datetime

# 格式化视频数据
def format_video_data(data: dict, constants: dict) -> str:
    """
    格式化视频数据为文本。
    :param data: 视频数据字典。
    :param constants: 配置参数。
    :return: 格式化后的文本。
    """

    file_info = []

    stats_play = constants["stats_play"]
    stats_coin = constants["stats_coin"]
    stats_title = constants["stats_title"]
    stats_cover = constants["stats_cover"]
    stats_reply = constants["stats_reply"]
    stats_share = constants["stats_share"]
    stats_collect = constants["stats_collect"]
    stats_danmaku = constants["stats_danmaku"]
    stats_pubtime = constants["stats_pubtime"]
    stats_duration = constants["stats_duration"]
    stats_thumb_up = constants["stats_thumb_up"]
    stats_dividing_line = constants["stats_dividing_line"]

    for bvid, video_info in data.items():
        current_time = datetime.now().strftime("%Y年-%m月-%d日 %H:%M:%S")

        file_info.append(f"""\
        《{video_info.get("title", stats_title)}》 ｜ 《{bvid}》
        
        **视频时长** ｜ {video_info.get("duration", stats_duration)}
        **发布日期** ｜ {video_info.get("pubtime", stats_pubtime)}
        **封面链接** ｜ {video_info.get("cover", stats_cover)}
        
        **核心数据**
        播放量: {video_info.get("play", stats_play)}
        评论数: {video_info.get("reply", stats_reply)} -*- 转发数: {video_info.get("share", stats_share)} -*- 弹幕数: {video_info.get("danmaku", stats_danmaku)}
        点赞数: {video_info.get("thumb_up", stats_thumb_up)} -*- 投币数: {video_info.get("coin", stats_coin)} -*- 收藏数: {video_info.get("collect", stats_collect)}
    
        **统计日期** ｜ {current_time}
    
        {stats_dividing_line}
        """)

    return "\n".join(file_info)