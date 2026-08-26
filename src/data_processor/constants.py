# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/27
# Program Name: data_processor - constants

"""
默认配置参数
"""

# 转换重试次数
DEFAULT_CONVERT_RETRY = 3

# 默认音频格式
DEFAULT_CONVERT_AUDIO_FORMAT = ".mp3"

# 默认BVID
DEFAULT_FILTER_BVID = "未知BVID"
# 默认标题
DEFAULT_FILTER_TITLE = "未知标题"
# 默认封面
DEFAULT_FILTER_COVER = "未知封面"

# 默认时长
DEFAULT_MEDIA_DURATION = "00:00:00"
# 默认发布时间
DEFAULT_MEDIA_PUBTIME = "0000-00-00 00:00:00"

# 默认无效字符
DEFAULT_FILTER_INVALID_CHARS = r'\/:*?"<>|'

# 默认匹配方法
DEFAULT_MATCHING_METHODS = [
    r"\((.*?)\)",       # 英文圆括号
    r"\[(.*?)\]",       # 英文方括号
    r"\《(.*?)\》",     # 中文书名号
    r"\【(.*?)\】",     # 中文方括号
]

# 默认计数字段
DEFAULT_CNT_INFO_FIELDS = [
    "coin",      # 硬币
    "play",      # 播放量
    "reply",     # 评论数
    "share",     # 分享数
    "danmaku",   # 弹幕数
    "collect",   # 收藏数
    "thumb_up",  # 点赞数
]

# 默认过滤标签
DEFAULT_FILTER_LABELS = [
    "伴奏", "音质", "歌词版", "完整版", "OST",
    "无损音质", "feat.", "音乐推荐", "动态歌词",
    "每日后朋", "日推歌单", "4K60帧", "4K高码率",
    "纯音乐分享", "studio", "hi-res", "动态歌词排版",
    "hi-res无损", "hi-res百万级录音棚试听","补档", 
    "日推", 
]