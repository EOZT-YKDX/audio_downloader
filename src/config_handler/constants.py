# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/8/5
# Program Name: config_handler - constants

import os
import logging

# 配置文件名
DEFAULT_CONFIG_FILE_NAME = "audio_downloader_config.yaml"

# 默认配置
DEFAULT_ORIGINAL_CONFIG = {
    # ================== app_initializer ==================
    "dir_init_name": "AudioDownloader",                             # 默认应用初始化目录名
    
    "dependency_tools": ["ffmpeg", "you-get"],                      # 默认依赖工具列表
    
    "subdirectory": {                                               # 默认子目录配置
        "log": "Log",                                               # 日志目录名
        "data": "Data",                                             # 数据目录名
        "audio_orig": os.path.join("Music", "OriginalAudio"),       # 原始音频目录名
        "audio_comp": os.path.join("Music", "CompressedAudio"),     # 压缩音频目录名
    },

    # ================== audio_compressor ==================
    "install_retry": 3,                                        # 默认安装重试次数
    "get_link_retry": 3,                                       # 默认获取链接重试次数

    "driver_install_path": r".",                               # 默认驱动安装路径

    "compressed_file_name": "未知名称",                        # 默认压缩文件名

    "compression_url": "https://www.youcompress.com/zh-cn/",   # 默认压缩网站URL
    "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0", # 默认浏览器 User-Agent

    "edge_args": [                                             # 默认浏览器参数
        "--headless=new",                                      # 启用无头模式
        "--window-position=-32000,-32000",                     # 设置窗口位置为隐藏(临时)

        "--incognito",                                         # 启用无痕模式
        "--no-sandbox",                                        # 禁用沙箱模式
        "--disable-gpu",                                       # 禁用GPU加速
        "--disable-sync",                                      # 禁用同步功能
        "--no-first-run",                                      # 禁用首次运行
        "--disable-d3d11",                                     # 禁用Direct3D
        "--disable-logging",                                   # 禁用日志记录
        "--disable-3d-apis",                                   # 禁用3D图形
        "--disable-plugins",                                   # 禁用所有插件
        "--disable-breakpad",                                  # 禁用崩溃报告
        "--disable-canvas-aa",                                 # 禁用抗锯齿
        "--disable-translate",                                 # 禁用翻译
        "--disable-extensions",                                # 禁用所有扩展
        "--enable-fast-unload",                                # 启用快速加载页面
        "--disable-hang-monitor",                              # 禁用挂起监控器
        "--disable-dev-shm-usage",                             # 禁用 /dev/shm 使用
        "--disable-notifications",                             # 禁用通知
        "--remote-debugging-port=0",                           # 禁用远程调试端口
        "--disable-background-timer",                          # 禁用后台计时器
        "--disable-component-update",                          # 禁止组件自动更新
        "--disable-software-rasterizer",                       # 禁用备用呈现器
        "--enable-parallel-downloading",                       # 启用并行下载
        "--disable-background-networking",                     # 禁用后台网络
        "--enable-features=NetworkService",                    # 启用网络服务
        "--disable-offer-upload-credit-cards",                 # 禁用信用卡填充
        "--blink-settings=imagesEnabled=false",                # 禁用图像加载
        "--disable-background-timer-throttling",               # 禁用后台计时器
        "--disable-features=RendererCodeIntegrity",            # 禁用渲染器检查
        "--disable-blink-features=AutomationControlled",       # 禁用自动化控制特征
        "--disable-features=msEdgePreloadMediaEngagementData", # 禁用预加载媒体参与数据特征
        ],

    "compression_timeout": {                                   # 默认压缩超时配置
        "seek_timeout": 10,                                    # 默认定位超时时间
        "upload_timeout": 10,                                  # 默认上传超时时间
        "submit_timeout": 10,                                  # 默认提交超时时间
        "compress_timeout": 20,                                # 默认压缩超时时间
        },

    "experimental_options": {                                               # 默认实验性选项
        "safebrowsing.enabled": False,                                      # 禁用安全浏览
        "useAutomationExtension": False,                                    # 禁用自动化扩展
        "download.directory_upgrade": True,                                 # 允许下载到指定目录
        "credentials_enable_service": False,                                # 禁用密码保存提示
        "download.prompt_for_download": False,                              # 禁用下载提示
        "profile.password_manager_enabled": False,                          # 禁用密码管理器
        "profile.default_content_settings.popups": 0,                       # 禁用弹窗
        "profile.managed_default_content_settings.geolocation": 2,          # 禁用地理位置
        "profile.managed_default_content_settings.media_stream": 2,         # 禁用媒体流
        "profile.managed_default_content_settings.notifications": 2,        # 禁用通知
        "profile.managed_default_content_settings.media_stream_mic": 2,     # 禁用麦克风
        "profile.managed_default_content_settings.media_stream_camera": 2,  # 禁用摄像头
        },

    # ==================== data_processor ====================
    "convert_retry": 3,                         # 默认转换重试次数
    "convert_audio_format": ".mp3",             # 默认转换音频格式

    "filter_bvid": "未知BVID",                  # 默认BVID
    "filter_title": "未知标题",                 # 默认标题
    "filter_cover": "未知封面",                 # 默认封面

    "media_duration": "00:00:00",               # 默认时长
    "media_pubtime": "0000-00-00 00:00:00",     # 默认发布时间

    "filter_invalid_chars": r'\/:*?"<>|',       # 默认无效字符

    "matching_methods": [                       # 默认匹配方法
        r"\((.*?)\)",                           # 英文圆括号
        r"\[(.*?)\]",                           # 英文方括号
        r"\《(.*?)\》",                         # 中文书名号
        r"\【(.*?)\】",                         # 中文方括号
        ],

    "filter_labels": [                          # 默认过滤标签
        "伴奏", "音质", "歌词版", "完整版", "OST",
        "无损音质", "feat.", "音乐推荐", "动态歌词",
        "每日后朋", "日推歌单", "4K60帧", "4K高码率",
        "纯音乐分享", "studio", "hi-res", "动态歌词排版",
        "hi-res无损", "hi-res百万级录音棚试听","补档", 
        "日推", 
        ],

    "cnt_info_fields": [                        # 默认计数字段
        "coin",                                 # 硬币
        "play",                                 # 播放量
        "reply",                                # 评论数
        "share",                                # 分享数
        "danmaku",                              # 弹幕数
        "collect",                              # 收藏数
        "thumb_up",                             # 点赞数
        ],

    # ====================== log_setup ======================
    "logger": None,                                           # 默认日志记录器
    
    "logger_encoding": "UTF-8",                               # 默认日志记录器编码
    "logger_level": logging.DEBUG,                            # 默认日志记录器级别
    "logger_name": "AudioDownloader",                         # 默认日志记录器名称

    "logger_backup_count": 5,                                 # 默认日志记录器备份数量
    "logger_max_bytes": 5*1024*1024,                          # 默认日志记录器最大字节数
    "logger_format": "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s", # 默认日志记录器格式

    # =================== metadata_editor ===================
    "metadata_file_name": "未知名称",                                                                           # 默认元数据文件名

    "metadata_encoder": "YKDX",                                                                                 # 默认元数据编码人员
    "metadata_publisher": "YKDX",                                                                               # 默认元数据发布者
    "metadata_artist": "EOZT-YKDX出品",                                                                         # 默认元数据歌手
    "metadata_copyright": "©EOZT 2025-2026",                                                                    # 默认元数据版权信息
    "metadata_author_url": "https://github.com/EOZT-YKDX",                                                      # 默认元数据作者URL
    "metadata_cover_file": r"audio_downloader\static\EOZT.png",                                                 # 默认元数据封面文件

    "metadata_mp3_tag": ["TIT3", "TDRC", "TPE1", "TENC", "TPUB", "TCOP", "APIC", "WOAR"],                       # 默认元数据MP3标签
    "metadata_flac_tag": ["SUBTITLE", "ARTIST", "ENCODER", "COPYRIGHT", "DESCRIPTION", "ORGANIZATION", "DATE"], # 默认元数据FLAC标签

    # =================== network_client ===================
    "network_retry": 5,                                        # 默认网络重试次数
    "network_page_size": 200,                                  # 默认网络分页大小

    "network_crawl_timeout": 10,                               # 默认网络爬取超时时间
    "network_download_timeout": 150,                           # 默认网络下载超时时间

    "network_origin": "https://www.bilibili.com",              # 默认网络origin
    "network_referer": "https://www.bilibili.com",             # 默认网络referer

    "network_video_url": "https://www.bilibili.com/video/",    # 默认网络视频URL
    "network_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0", # 默认网络用户代理

    # =================== stats_generator ===================
    "stats_file_name": "信息统计",                              # 默认信息统计文件名

    "stats_coin": 0,                                            # 默认硬币数
    "stats_play": 0,                                            # 默认播放量
    "stats_reply": 0,                                           # 默认评论数
    "stats_share": 0,                                           # 默认分享数
    "stats_collect": 0,                                         # 默认收藏数
    "stats_danmaku": 0,                                         # 默认弹幕数
    "stats_thumb_up": 0,                                        # 默认点赞数

    "stats_bvid": "未知bvid",                                   # 默认视频bvid
    "stats_title": "未知标题",                                  # 默认视频标题
    "stats_cover": "未知封面",                                  # 默认视频封面

    "stats_duration": "00:00:00",                               # 默认视频时长
    "stats_pubtime": "0000-00-00 00:00:00",                     # 默认视频发布时间时间

    "stats_dividing_line":  {"filler": "-", "length": 150},    # 默认信息统计分隔线
    
    # ==================== task_executor ===================
    "max_download_workers": 8,                                  # 默认最大下载工作线程数
    "max_compress_workers": 10,                                  # 默认最大压缩工作线程数
}