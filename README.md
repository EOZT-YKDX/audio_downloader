# Audio Downloader - B站收藏夹音频下载器

<p align="center">
  <img src="static/EOZT.png" alt="EOZT Logo" width="150" height="150">
</p>

<p align="center">
  <strong>一款B站(Bilibili) 收藏夹音频下载与处理工具</strong>
</p>

<p align="center">
  <a href="#特性">特性</a> •
  <a href="#系统架构">系统架构</a> •
  <a href="#安装指南">安装指南</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#配置说明">配置说明</a> •
  <a href="#项目结构">项目结构</a> •
  <a href="#核心功能">核心功能</a> •
  <a href="#技术栈">技术栈</a> •
  <a href="#许可证">许可证</a>
</p>

---

## 📖 项目简介

**Audio Downloader** 是一款专为 B站(Bilibili) 用户设计的自动化音频下载与处理工具。它能够：

- 🎯 通过 B站收藏夹ID (FID) 自动爬取收藏夹内的所有视频
- 🎵 自动将视频转换为高质量音频 (MP3 格式)
- 🏷️ 智能编辑音频元数据 (艺术家、版权、封面等)
- 📊 生成详细的视频数据统计报告
- 🗜️ 支持音频文件压缩处理
- 🔍 智能文件名提取与分类管理
- ⚡ 多线程并发下载与压缩，大幅提升处理效率
- 🔄 完善的错误处理与重试机制
- 📝 完整的日志记录系统 (终端 + 文件)

---

## ✨ 特性

### 🎯 核心功能

- **智能数据爬取**: 调用 B站 API 接口，自动获取收藏夹内所有视频信息
- **去重过滤**: 自动识别已下载的音频文件，避免重复下载
- **黑名单过滤**: 支持过滤特定标签的视频（如"伴奏"、"无损音质"等）
- **并发下载**: 多线程并发下载视频，支持自定义线程数
- **格式转换**: 自动将视频转换为 MP3 音频格式
- **元数据编辑**: 自动为音频文件添加完整的元数据（艺术家、版权、封面等）
- **音频压缩**: 支持音频文件压缩处理，节省存储空间
- **名称提取**: 智能从文件名中提取关键字，自动分类整理
- **统计报告**: 生成详细的视频数据统计报告（播放量、点赞数、评论数等）

### 🛡️ 可靠性

- **重试机制**: 网络请求、视频下载、格式转换等关键操作均支持指数退避重试
- **异常处理**: 完善的异常捕获与日志记录，确保程序稳定运行
- **数据验证**: 严格的参数验证与路径检查，防止无效数据导致程序崩溃
- **日志系统**: 双通道日志记录（终端 + 文件），支持日志轮转与备份

### ⚡ 性能优化

- **并发处理**: 下载与压缩任务均采用线程池并发执行
- **临时目录**: 使用临时目录管理中间文件，避免磁盘空间浪费
- **智能缓存**: 基于音频标签的智能去重，避免重复压缩

---

## 🏗️ 系统架构

### 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        Audio Downloader                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. 初始化阶段 (Initialization)                                  │
│     - 读取并更新配置文件                                          │
│     - 创建目录结构 (Log/Data/Music)                              │
│     - 配置日志系统 (终端 + 文件)                                  │
│     - 检测依赖工具 (FFmpeg, you-get)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. 数据爬取 (Data Crawling)                                     │
│     - 调用 B站 API 获取收藏夹数据                                 │
│     - 支持分页与重试机制                                          │
│     - 随机 User-Agent 防止反爬                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. 数据过滤与分类 (Data Filtering & Classification)             │
│     - 读取已下载音频标签，去重过滤                                │
│     - 黑名单标签过滤                                              │
│     - 无效字符过滤                                                │
│     - 数据格式化与分类                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. 统计报告生成 (Statistics Generation)                         │
│     - 格式化视频数据                                              │
│     - 生成统计报告文件                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. 并发下载 (Concurrent Download)                               │
│     - 多线程并发下载视频 (you-get)                                │
│     - 视频转音频 (FFmpeg)                                         │
│     - 自动编辑音频元数据 (mutagen)                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. 并发压缩 (Concurrent Compression)                            │
│     - 多线程并发压缩音频                                          │
│     - 智能去重 (基于音频标签)                                     │
│     - 下载压缩后的文件                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. 名称提取与分类 (Name Extraction & Classification)            │
│     - 正则表达式匹配关键字                                        │
│     - 智能重命名文件                                              │
│     - 自动创建文件夹分类管理                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 安装指南

### 环境要求

- **Python**: >= 3.10
- **操作系统**: Windows / Linux / macOS
- **依赖工具**:
  - [FFmpeg](https://ffmpeg.org/) - 视频转音频
  - [you-get](https://github.com/soimort/you-get) - B站视频下载

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd audio_downloader
```

#### 2. 安装 Python 依赖

```bash
pip install -e .
```

或者手动安装依赖：

```bash
pip install requests PyYAML mutagen selenium msedgedriver fake-useragent filetype you-get
```

#### 3. 安装依赖工具

**安装 FFmpeg:**

- **Windows**: 
  ```bash
  # 使用 winget
  winget install Gyan.FFmpeg
  
  # 或使用 choco
  choco install ffmpeg
  ```

- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update && sudo apt install ffmpeg
  ```

- **macOS**:
  ```bash
  brew install ffmpeg
  ```

**安装 you-get:**

```bash
pip install you-get
```

#### 4. 验证安装

```bash
ffmpeg -version
you-get --version
```

---

## 🚀 快速开始

### 基本用法

```python
from src.main import main

# 配置参数
fid = "3570962345"                    # B站收藏夹ID
output_dir = r"C:\Users\YourName\Downloads\AudioDownloader"  # 输出目录
config = {}                           # 自定义配置 (可选)

# 运行程序
main(fid=fid, output_dir=output_dir, config=config)
```

### 命令行使用

直接运行主程序：

```bash
python src/main.py
```

### 自定义配置

```python
config = {
    "max_download_workers": 10,       # 最大下载线程数
    "max_compress_workers": 12,       # 最大压缩线程数
    "network_retry": 5,               # 网络重试次数
    "convert_retry": 5,               # 转换重试次数
    "metadata_artist": "自定义艺术家", # 自定义艺术家名称
    # ... 更多配置项
}

main(fid="your_fid", output_dir="your_output_dir", config=config)
```

---

## ⚙️ 配置说明

### 配置文件

程序会自动生成 YAML 格式的配置文件：`audio_downloader_config.yaml`

### 主要配置项

#### 应用初始化配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `dir_init_name` | str | "AudioDownloader" | 应用初始化目录名 |
| `dependency_tools` | list | ["ffmpeg", "you-get"] | 依赖工具列表 |
| `subdirectory` | dict | - | 子目录配置 |
| `subdirectory.log` | str | "Log" | 日志目录名 |
| `subdirectory.data` | str | "Data" | 数据目录名 |
| `subdirectory.audio_orig` | str | "Music/OriginalAudio" | 原始音频目录 |
| `subdirectory.audio_comp` | str | "Music/CompressedAudio" | 压缩音频目录 |

#### 网络配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `network_retry` | int | 2 | 网络请求重试次数 |
| `network_page_size` | int | 200 | API 分页大小 |
| `network_crawl_timeout` | int | 10 | 爬取超时时间 (秒) |
| `network_download_timeout` | int | 100 | 下载超时时间 (秒) |
| `network_origin` | str | "https://www.bilibili.com" | 请求 Origin 头 |
| `network_referer` | str | "https://www.bilibili.com" | 请求 Referer 头 |
| `network_user_agent` | str | - | 用户代理字符串 |

#### 数据处理配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `convert_retry` | int | 3 | 视频转音频重试次数 |
| `convert_audio_format` | str | ".mp3" | 输出音频格式 |
| `filter_invalid_chars` | str | `\/:*?"<>|` | 文件名无效字符 |
| `filter_labels` | list | ["伴奏", "音质", ...] | 黑名单标签列表 |
| `matching_methods` | list | [正则表达式列表] | 文件名匹配正则 |
| `cnt_info_fields` | list | ["coin", "play", ...] | 统计字段列表 |

#### 任务执行配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `max_download_workers` | int | 5 | 最大下载线程数 |
| `max_compress_workers` | int | 8 | 最大压缩线程数 |

#### 元数据配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `metadata_artist` | str | "EOZT-YKDX出品" | 艺术家名称 |
| `metadata_encoder` | str | "YKDX" | 编码人员 |
| `metadata_publisher` | str | "YKDX" | 发布者 |
| `metadata_copyright` | str | "©EOZT 2025-2026" | 版权信息 |
| `metadata_author_url` | str | "https://github.com/EOZT-YKDX" | 作者 URL |
| `metadata_cover_file` | str | "audio_downloader\static\EOZT.png" | 封面文件路径 |

#### 日志配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `logger_level` | int | logging.DEBUG | 日志级别 |
| `logger_name` | str | "AudioDownloader" | 日志记录器名称 |
| `logger_encoding` | str | "UTF-8" | 日志编码 |
| `logger_max_bytes` | int | 5*1024*1024 | 单文件最大大小 (5MB) |
| `logger_backup_count` | int | 5 | 日志备份数量 |
| `logger_format` | str | - | 日志格式字符串 |

---

## 📂 项目结构

### 源代码结构

```
audio_downloader/
├── src/
│   ├── main.py                          # 主程序入口
│   ├── app_initializer/                 # 应用初始化模块
│   │   ├── main.py                      # 初始化逻辑
│   │   ├── directory_setup.py           # 目录创建
│   │   ├── dependency_check.py          # 依赖检测
│   │   └── read_constants.py            # 配置读取
│   ├── config_handler/                  # 配置管理模块
│   │   ├── main.py                      # 配置管理逻辑
│   │   ├── config_updater.py            # 配置更新
│   │   └── reader/                      # 配置读取器
│   ├── network_client/                  # 网络客户端模块
│   │   ├── crawler/                     # 爬虫子模块
│   │   │   ├── main.py                  # 爬取逻辑
│   │   │   └── request_handler.py       # 请求处理
│   │   └── downloader/                  # 下载子模块
│   │       ├── download_bilibili_video.py # B站视频下载
│   │       └── download_compress_file.py  # 压缩文件下载
│   ├── data_processor/                  # 数据处理模块
│   │   ├── filter/                      # 过滤器
│   │   │   ├── main.py                  # 过滤逻辑
│   │   │   ├── file_filter.py           # 文件过滤
│   │   │   └── tag_reader.py            # 标签读取
│   │   ├── converter/                   # 转换器
│   │   │   └── main.py                  # 视频转音频
│   │   └── extractor/                   # 提取器
│   │       ├── main.py                  # 名称提取逻辑
│   │       ├── file_rename.py           # 文件重命名
│   │       └── matcher.py               # 关键字匹配
│   ├── task_executor/                   # 任务执行模块
│   │   ├── downloader/                  # 下载执行器
│   │   │   ├── main.py                  # 并发下载逻辑
│   │   │   └── download_task.py         # 下载任务处理
│   │   └── compressor/                  # 压缩执行器
│   │       ├── main.py                  # 并发压缩逻辑
│   │       └── compress_task.py         # 压缩任务处理
│   ├── stats_generator/                 # 统计生成模块
│   │   ├── main.py                      # 统计逻辑
│   │   ├── formatter.py                 # 数据格式化
│   │   └── writer.py                    # 文件写入
│   ├── log_setup/                       # 日志配置模块
│   │   ├── file_log.py                  # 文件日志
│   │   └── terminal_log.py              # 终端日志
│   ├── metadata_editor/                 # 元数据编辑模块
│   │   ├── main.py                      # 元数据编辑逻辑
│   │   ├── formats/                     # 格式处理器
│   │   │   ├── mp3.py                   # MP3 格式
│   │   │   └── flac.py                  # FLAC 格式
│   │   └── reader/                      # 读取器
│   │       └── read_cover.py            # 封面读取
│   └── audio_compressor/                # 音频压缩模块
│       ├── main.py                      # 压缩逻辑
│       ├── browser_manager/             # 浏览器管理
│       │   └── edge_browser.py          # Edge 浏览器
│       └── website_interaction.py       # 网站交互
├── static/                              # 静态资源
│   └── EOZT.png                         # 默认封面
├── tests/                               # 测试目录
├── docs/                                # 文档目录
├── pyproject.toml                       # 项目配置
├── .gitignore                           # Git 忽略规则
└── README.md                            # 项目说明
```

### 输出目录结构

程序运行后会自动创建以下目录结构：

```
<output_dir>/
└── AudioDownloader/
    ├── Log/                          # 日志目录
    │   └── AudioDownloader           # 日志文件 (自动轮转)
    ├── Data/                         # 数据目录
    │   └── 信息统计_2026-07-29.txt   # 统计报告文件
    └── Music/
        ├── OriginalAudio/            # 原始音频目录
        │   ├── 歌曲1.mp3
        │   ├── 歌曲2.mp3
        │   └── ...
        └── CompressedAudio/          # 压缩音频目录
            ├── 歌曲1.mp3
            ├── 歌曲2.mp3
            └── ...
```

### 音频元数据

每个音频文件都包含以下元数据：

**MP3 格式:**
- `TIT3` - 子标题 (用于去重)
- `TPE1` - 艺术家
- `TENC` - 编码人员
- `TPUB` - 发布者
- `TCOP` - 版权信息
- `APIC` - 封面图片
- `WOAR` - 作者官方 URL
- `TDRC` - 年份

**FLAC 格式:**
- `SUBTITLE` - 子标题 (用于去重)
- `ARTIST` - 艺术家
- `ENCODER` - 编码人员
- `ORGANIZATION` - 发布者
- `COPYRIGHT` - 版权信息
- `DESCRIPTION` - 作者官方 URL
- `DATE` - 年份
- `PICTURE` - 封面图片

---

## 🎯 核心功能

### 1. 数据爬取

通过 B站 API 接口获取收藏夹数据：

- **API 端点**: `https://api.bilibili.com/x/v1/medialist/resource/list`
- **参数**: 
  - `type=3` - 收藏夹类型
  - `biz_id={fid}` - 收藏夹ID
  - `ps={page_size}` - 每页数量
- **特性**:
  - 随机 User-Agent 防止反爬
  - 指数退避重试机制
  - 完整的错误处理

### 2. 智能过滤

多层次数据过滤机制：

- **去重过滤**: 读取已下载音频的 `TIT3`/`SUBTITLE` 标签，避免重复下载
- **黑名单过滤**: 过滤包含特定标签的视频（如"伴奏"、"无损音质"等）
- **字符过滤**: 移除文件名中的无效字符 (`\/:*?"<>|`)
- **空数据过滤**: 自动跳过无效或空数据

### 3. 并发下载

使用线程池实现并发下载：

```python
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {
        executor.submit(process_video_download, ...): video_name
        for bvid, video_data in data.items()
    }
    
    for future in as_completed(futures):
        # 处理下载结果
```

**下载流程**:
1. 下载视频到临时目录 (you-get)
2. 转换为音频格式 (FFmpeg)
3. 编辑音频元数据 (mutagen)
4. 移动到输出目录
5. 清理临时文件

### 4. 音频压缩

支持音频文件压缩处理：

- **智能去重**: 基于音频标签 (`TIT3`/`SUBTITLE`) 避免重复压缩
- **并发处理**: 多线程并发压缩任务
- **自动下载**: 压缩完成后自动下载压缩文件

### 5. 名称提取与分类

智能文件名处理：

- **正则匹配**: 支持多种括号格式 `()`, `[]`, `《》`, `【】`
- **关键字提取**: 从文件名中提取有效关键字
- **自动分类**: 遇到同名文件时自动创建文件夹分类管理
- **黑名单过滤**: 过滤黑名单标签

### 6. 统计报告

生成详细的视频数据统计：

```
《视频标题》 ｜ 《BVxxxxxxxxxx》

**视频时长** ｜ 00:00:00
**发布日期** ｜ 2026-07-29 00:00:00
**封面链接** ｜ https://xxx

**核心数据**
播放量: 0
评论数: 0 -*- 转发数: 0 -*- 弹幕数: 0
点赞数: 0 -*- 投币数: 0 -*- 收藏数: 0

**统计日期** ｜ 2026年-07月-29日 00:00:00

------------------------------------------------------------------------------------------------------------------------------------------------------
```

---

## 🛠️ 技术栈

### Python 依赖包

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| `requests` | >=2.31.0 | HTTP 请求 |
| `PyYAML` | >=6.0 | YAML 配置文件处理 |
| `mutagen` | >=1.47.0 | 音频元数据编辑 |
| `selenium` | >=4.15.0 | 浏览器自动化 (音频压缩) |
| `msedgedriver` | >=120.0.0 | Edge 浏览器驱动 |
| `fake-useragent` | >=1.4.0 | 随机 User-Agent 生成 |
| `filetype` | >=1.2.0 | 文件类型检测 |
| `you-get` | >=0.4.17 | B站视频下载 |

### 外部工具

| 工具 | 用途 |
|------|------|
| [FFmpeg](https://ffmpeg.org/) | 视频转音频格式转换 |
| [you-get](https://github.com/soimort/you-get) | B站视频下载 |

### Python 标准库

- `concurrent.futures` - 线程池并发执行
- `subprocess` - 调用外部命令行工具
- `logging` - 日志记录系统
- `os` / `pathlib` - 文件系统操作
- `re` - 正则表达式匹配
- `tempfile` - 临时目录管理
- `datetime` - 时间处理
- `yaml` - 配置文件解析

---

## 📊 性能指标

### 并发性能

- **下载线程数**: 默认 5 线程 (可自定义)
- **压缩线程数**: 默认 8 线程 (可自定义)
- **内存占用**: 低内存占用，使用临时目录管理中间文件
- **磁盘 I/O**: 优化的文件读写操作，减少不必要的磁盘写入

### 可靠性指标

- **重试机制**: 所有网络操作均支持指数退避重试
- **错误恢复**: 单个任务失败不影响其他任务执行
- **数据完整性**: 严格的文件验证与校验机制

---

## 🔧 开发指南

### 代码规范

- 遵循 PEP 8 编码规范
- 使用类型提示 (Type Hints)
- 完整的文档字符串 (Docstrings)
- 统一的命名规范

### 添加新功能

1. 在对应模块下创建新文件
2. 在模块的 `__init__.py` 中导出新函数
3. 在 `constants.py` 中添加默认配置
4. 在 `main.py` 中集成新功能

### 调试技巧

- 查看 `Log/AudioDownloader` 目录下的日志文件
- 设置 `logger_level` 为 `logging.DEBUG` 获取详细日志
- 使用 `config` 参数覆盖默认配置进行测试

---

## 🐛 常见问题

### Q: 下载失败怎么办？

A: 检查以下几点：
1. 确认 `ffmpeg` 和 `you-get` 已正确安装并添加到 PATH
2. 检查网络连接是否正常
3. 查看日志文件中的错误信息

### Q: 如何修改输出目录？

A: 在调用 `main()` 函数时修改 `output_dir` 参数：

```python
main(fid="your_fid", output_dir=r"D:\MyMusic", config={})
```

### Q: 如何自定义艺术家名称？

A: 通过 `config` 参数覆盖默认配置：

```python
config = {
    "metadata_artist": "我的艺术家名称",
    "metadata_publisher": "我的发布者",
}
main(fid="your_fid", output_dir="output", config=config)
```

### Q: 如何过滤特定标签？

A: 修改 `filter_labels` 配置：

```python
config = {
    "filter_labels": ["伴奏", "音质", "自定义标签"],
}
main(fid="your_fid", output_dir="output", config=config)
```

### Q: 日志文件在哪里？

A: 日志文件位于 `<output_dir>/AudioDownloader/Log/` 目录下，支持自动轮转与备份。

---

## 📝 更新日志

### v1.0.0 (2026-07-29)

- ✨ 初始版本发布
- 🎯 支持 B站收藏夹数据爬取
- 🎵 视频转音频格式转换
- 🏷️ 音频元数据编辑 (MP3/FLAC)
- 📊 视频数据统计报告生成
- 🗜️ 音频文件压缩处理
- 🔍 智能文件名提取与分类
- ⚡ 多线程并发下载与压缩
- 🛡️ 完善的错误处理与重试机制
- 📝 双通道日志系统 (终端 + 文件)

---

## 👨‍💻 作者

**YKDX** - EOZT 团队

- GitHub: [EOZT-YKDX](https://github.com/EOZT-YKDX)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 鸣谢

- [Bilibili](https://www.bilibili.com/) - 提供 API 接口
- [FFmpeg](https://ffmpeg.org/) - 强大的音视频处理工具
- [you-get](https://github.com/soimort/you-get) - 优秀的网络视频下载器
- [mutagen](https://mutagen.readthedocs.io/) - 音频元数据处理库

---

<p align="center">
  <strong>⭐ 如果这个项目对你有帮助，请给一个 Star 支持一下！⭐</strong>
</p>