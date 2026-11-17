# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/30
# Program Name: audio_compressor - constants

# 默认压缩后的文件名
DEFAULT_COMPRESSED_FILE_NAME = "未知名称"
# 压缩网站URL
DEFAULT_COMPRESSION_URL = "https://www.youcompress.com/zh-cn/"
# 默认浏览器 User-Agent
DEFAULT_BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"

# 默认Edge浏览器选项
DEFAULT_EDGE_ARGS = [
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
]

# 默认压缩超时配置
DEFAULT_COMPRESSION_TIMEOUT = {
    "seek_timeout": 10,
    "upload_timeout": 30,
    "submit_timeout": 30,
    "compress_timeout": 180,
    "download_timeout": 120,
}

# 默认实验选项
DEFAULT_EXPERIMENTAL_OPTIONS = {
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
}