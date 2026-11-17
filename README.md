# Audio Downloader

<p align="center">
  <strong>B站收藏夹音频批量处理工具 —— 爬取 · 去重 · 下载 · 转码 · 写标签 · 在线压缩 · 自动归档</strong>
</p>

<p align="center">
  <a href="#项目简介">项目简介</a> •
  <a href="#系统架构">系统架构</a> •
  <a href="#安装指南">安装指南</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#配置说明">配置说明</a> •
  <a href="#核心流程">核心流程</a> •
  <a href="#项目结构">项目结构</a> •
  <a href="#技术栈">技术栈</a> •
  <a href="#常见问题">常见问题</a> •
  <a href="#许可证">许可证</a>
</p>

---

> ⚠️ **免责声明**
> 本工具仅用于**个人学习与备份已获授权访问的内容**。请遵守 B站用户协议与相关法律法规，
> 不得将下载内容用于商业用途或二次传播，使用者需自行承担全部法律责任。

---

## 项目简介

**Audio Downloader** 是一条面向 B站（哔哩哔哩）收藏夹的**音频生产流水线**。以收藏夹 ID 为输入，
自动完成从数据爬取到文件归档的全链路，并提供两套运行入口：**命令行流水线** 与
**桌面图形界面（pywebview）**。

它不是一个简单的下载器，而是一个**分阶段的数据管道**：每个阶段都是
「入参 dict + logger → 出参 dict」的独立模块，由统一的配置字典串联，
任一阶段失败只影响当前条目，不阻断整体流程。

核心能力：

- 🎯 调用 B站 API 拉取收藏夹媒体条目（单次请求最多 200 条，带指数退避重试）
- 🧹 基于**音频内部标签**智能去重，用户改文件名也不会重复下载
- 🚫 基于 21 条默认黑名单标签过滤不需要的内容（伴奏、无损音质、日推等）
- ⚡ 双线程池并发：下载池与压缩池独立配置、互不阻塞
- 🏷️ 自动写入艺术家、编码者、版权、封面等 8 项 MP3 / 7 项 FLAC 标签
- 🗜️ 通过 Selenium 驱动 Edge 调用在线压缩服务缩减音频体积
- 📊 生成含播放量、点赞、投币、收藏等 7 项指标的统计报告
- 🗂️ 用正则提取 `()`、`[]`、`《》`、`【】` 中的关键词重命名，重名自动建夹归档
- 🖥️ 深/浅主题、中/英/日三语、无边框拖拽的桌面界面

---

## 系统架构

### 分层结构

```
┌──────────────────────────────────────────────────────────────────┐
│                        入口层 (Entry)                            │
│   src/main.py（命令行流水线）      src/ui/ui_launcher.py（GUI）   │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                   基础设施层 (Infrastructure)                    │
│   app_initializer  │  config_handler  │  log_setup               │
│   依赖检测 / 建目录 │  YAML 三层合并    │  终端 + 文件轮转日志     │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                    业务能力层 (Capability)                        │
│   network_client      data_processor      metadata_editor        │
│   爬取 / 下载          过滤 / 转换 / 提取   标签与封面            │
│                                                                  │
│   audio_compressor                    stats_generator            │
│   Selenium 在线压缩                    统计报告                  │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                      调度层 (Scheduling)                         │
│   task_executor：下载线程池 + 压缩线程池                          │
└──────────────────────────────────────────────────────────────────┘
```

### 统一模块骨架

全部业务模块遵循同一范式，理解一个即可掌握全部：

```
module/
├── constants.py        # 内置默认值（DEFAULT_*）
├── read_constants.py   # 读取 + 类型校验 + 非法值回退默认
├── main.py             # 对外唯一入口函数
├── 子功能/              # 按职责拆分
└── __init__.py         # 用 __all__ 收敛公开接口
```

这套「`constants` + `read_constants`」组合是全项目的核心工程约定：
**任何配置项在使用前必须过一遍校验器**，类型或范围不合法就记录 `error` 日志并回落默认值。
这让系统对残缺配置具备强韧性，也是它能容忍 GUI 传来的半结构化参数的原因。

### 数据流

```
B站收藏夹 (fid)
      │
      ▼
network_client.crawl_favorites                 拉取 mediaList
      │
      ▼
data_processor.filter_and_classify_data
      ├─ filter/tag_reader.get_existing_tags   读本地已下载标签
      ├─ filter/file_filter.get_pending_download  标签去重 + 黑名单过滤
      └─ filter/media_data_processor           字段清洗与统一结构
      │
      ▼
stats_generator.generate_statistics            Data/信息统计_YYYY-MM-DD.txt
      │
      ▼
task_executor.concurrent_download              下载池（max_download_workers）
      └─ download_task.process_video_download
           ├─ you-get 下载视频 → 临时目录
           ├─ ffmpeg 提取音频 → Music/OriginalAudio
           └─ mutagen 写入元数据标签
      │
      ▼
task_executor.concurrent_compression           压缩池（max_compress_workers）
      ├─ compressor/get_pending_files          原始目录 vs 压缩目录标签差集
      └─ compress_task.process_audio_compression
           ├─ Edge 上传 → 提交 → 等待结果
           └─ 下载压缩结果 → Music/CompressedAudio
      │
      ▼
data_processor.extract_and_rename_files        关键词重命名 + 重名建夹归档
```

---

## 安装指南

### 环境要求

| 项目 | 要求 |
|---|---|
| Python | >= 3.10 |
| 操作系统 | **Windows**（GUI 依赖 `ctypes.wintypes`，压缩依赖 Edge） |
| 外部命令 | `ffmpeg`、`you-get` 需在 `PATH` 中可用 |
| 浏览器 | Microsoft Edge（驱动由 Selenium Manager 自动匹配下载） |

### 1. 安装外部工具

```powershell
# ffmpeg（推荐 winget）
winget install Gyan.FFmpeg

# you-get（也可用 pip 安装）
pip install you-get

# 验证
ffmpeg -version
you-get --version
```

### 2. 安装 Python 依赖

```powershell
git clone <repository-url>
cd audio_downloader

python -m venv .venv
.venv\Scripts\Activate.ps1

# 仅运行依赖
pip install -e .

# 含开发工具（pytest / black / ruff / mypy）
pip install -e ".[dev]"
```

### 3. 验证安装

```powershell
python -c "import webview, mutagen, selenium, yaml, requests, filetype; print('依赖安装成功')"
```

---

## 快速开始

> 📌 **重要**：本项目的两个入口都依赖「以 `src` 为工作目录」的运行方式。
> - 业务层模块之间使用裸模块名导入（`from config_handler import ...`），需要 `src` 在 `sys.path`；
> - `ui_launcher.py` 内部使用 `from validators import ...` 这类**以 `src/ui` 为根**的顶层导入。
>
> 因此 `pyproject.toml` 刻意**未声明** `console_scripts`，请按下面的脚本方式启动。

### 方式一：图形界面（推荐）

```powershell
cd src
python ui/ui_launcher.py
```

窗口规格：900×700（最小 800×600）、无边框、居中显示、背景色 `#1c1c1e`。
界面包含三个页面：**下载任务** / **添加任务** / **设置**。

界面能力：

- 添加任务支持两种类型：`link`（单个 B站视频链接）与 `favorite`（收藏夹 ID）
- 任务状态机：`pending → downloading → completed / failed`（`paused` 为标记态）
- 设置项涵盖主题模式、主题色、背景类型与图片、输出格式、保存路径、
  并发任务数、并发压缩数、语言、时间/日期格式、通知样式与位置、免打扰时段
- `save_settings` 先经 `SettingsValidator` 校验，再写入内存与
  `%LOCALAPPDATA%\AudioDownloader\audio_downloader_ui_settings.json`

> 修改 `savePath` **不会**迁移已有的 `AudioDownloader/` 目录，也不会重建日志处理器；
> 它只影响此后新建任务的默认落盘位置，历史文件仍留在原路径。

### 方式二：命令行流水线

编辑 [src/main.py](file:///c:/programming/Python-Project/Project/audio_downloader/src/main.py) 的 `__main__` 块参数后运行：

```powershell
cd src
python main.py
```

也可在交互式环境中调用（需先进入 `src` 目录）：

```python
from main import main

main(
    fid="3570962345",                                  # B站收藏夹 ID
    output_dir=r"C:\Users\YourName\Downloads\音频下载",  # 输出根目录（必须已存在）
    config={},                                          # 自定义配置（可选）
)
```

### 输出目录结构

**命令行入口**：配置文件写到 `output_dir` 本身，运行期目录写到 `<output_dir>/AudioDownloader/`：

```
<output_dir>/
├── audio_downloader_config.yaml  # 合并后的完整配置（manage_config_files 写入）
└── AudioDownloader/              # dir_init_name，由 initialize_app 创建
    ├── Log/                      # 日志，轮转 5MB × 5 份
    ├── Data/                     # 统计报告 信息统计_YYYY-MM-DD.txt
    └── Music/
        ├── OriginalAudio/        # 原始音频（转码后、已写标签）
        └── CompressedAudio/      # 压缩后音频
```

**GUI 入口**：启动过程本身不调用 `manage_config_files`，因此仅打开界面不会产生 YAML；
但 `favorite` 类型任务在后台线程里会 `from main import main` 并调用完整流水线，
所以一旦执行过收藏夹任务，`<savePath>/` 下同样会出现 `audio_downloader_config.yaml` 与 `AudioDownloader/` 目录。
`link` 类型任务只调用 `download_bilibili_video`：会对 `savePath` 做一次 `os.makedirs(exist_ok=True)`，
但不写 YAML、不创建 `AudioDownloader/` 子目录树。

GUI 的设置文件独立存放于 `%LOCALAPPDATA%\AudioDownloader\audio_downloader_ui_settings.json`。

---

## 配置说明

### 配置合并层级

配置文件由 [config_updater.py](file:///c:/programming/Python-Project/Project/audio_downloader/src/config_handler/config_updater.py) 生成，优先级**从低到高**：

```
内置默认配置（DEFAULT_ORIGINAL_CONFIG）
    ↑ 浅合并
磁盘上已存在的 YAML
    ↑ 递归深度合并
各模块内置常量（constants 参数）
    ↑ 递归深度合并
运行时传入的 config 参数（最高优先级）
```

需要注意两层的合并方式不同：

- **默认配置与磁盘 YAML** 之间使用 `{**default_config, **existing_config}`，属于**浅合并**。
  因此若 YAML 中存在嵌套字典（如 `subdirectory`、`compression_timeout`），会整体替换默认字典，
  而不是逐键覆盖——想只改其中一个子键，必须把该嵌套字典的其余键一并写出。
- **`constants` 与运行时 `config`** 两层使用 `_deep_update_config` 递归合并，
  键名匹配不区分大小写，顶层未命中时还会递归搜索嵌套字典，因此这两个入参可以只写要改的键。

YAML 以 `allow_unicode=True, sort_keys=False, SafeDumper` 写出，键序与源码一致，便于人工比对。

### 主要配置项

#### 初始化与目录

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `dir_init_name` | str | `AudioDownloader` | 运行期根目录名 |
| `dependency_tools` | list | `["ffmpeg", "you-get"]` | 启动时用 `shutil.which` 检测的外部命令 |
| `subdirectory` | dict | `log=Log`、`data=Data`、`audio_orig=Music/OriginalAudio`、`audio_comp=Music/CompressedAudio` | 子目录映射 |

#### 网络与爬取

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `network_retry` | int | `5` | 网络操作重试次数 |
| `network_page_size` | int | `200` | 单次请求返回的条目数，校验范围为 1~200 |
| `network_crawl_timeout` | int | `10` | 爬取超时（秒） |
| `network_download_timeout` | int | `150` | 下载超时（秒） |
| `network_origin` | str | `https://www.bilibili.com` | 请求 Origin |
| `network_referer` | str | `https://www.bilibili.com` | 请求 Referer |
| `network_video_url` | str | `https://www.bilibili.com/video/` | 视频链接前缀 |
| `network_user_agent` | str | Edge 134 UA | 固定 User-Agent |

#### 并发调度

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `max_download_workers` | int | `8` | 下载线程池大小 |
| `max_compress_workers` | int | `10` | 压缩线程池大小 |

> ⚠️ `task_executor/constants.py` 内另有 `5 / 8` 的兜底常量，但该值仅在配置字典**缺少对应键**时生效。
> 由于 `config_handler` 的默认配置始终注入 `8 / 10`，实际生效值以本表为准。

#### 数据处理

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `convert_retry` | int | `3` | 格式转换重试次数 |
| `convert_audio_format` | str | `.mp3` | 目标音频格式 |
| `filter_bvid` | str | `未知BVID` | 缺少 bvid 字段时的兜底值 |
| `filter_title` | str | `未知标题` | 缺少 title 字段时的兜底值 |
| `filter_cover` | str | `未知封面` | 缺少 cover 字段时的兜底值 |
| `media_duration` | str | `00:00:00` | 缺少时长字段时的兜底值 |
| `media_pubtime` | str | `0000-00-00 00:00:00` | 缺少发布时间字段时的兜底值 |
| `filter_invalid_chars` | str | `\/:*?"<>\|` | 文件名非法字符集 |
| `matching_methods` | list | 4 条正则 | 关键词提取规则（`()`、`[]`、`《》`、`【】`） |
| `filter_labels` | list | 21 条标签 | 黑名单标签（大小写不敏感匹配） |
| `cnt_info_fields` | list | 7 个字段 | 统计指标：`coin`/`play`/`reply`/`share`/`danmaku`/`collect`/`thumb_up` |

#### 音频压缩（浏览器自动化）

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `compression_url` | str | `https://www.youcompress.com/zh-cn/` | 压缩站点地址 |
| `compressed_file_name` | str | `未知名称` | 无法解析文件名时的兜底名 |
| `edge_args` | list | 32 个参数 | Edge 启动参数（无头/无痕/禁图/禁插件/禁 GPU 等） |
| `experimental_options` | dict | 12 项 | 浏览器 prefs（禁用下载提示、密码保存、地理定位、媒体流等） |
| `compression_timeout` | dict | 见下表 | 各阶段超时（秒） |

`compression_timeout` 实际默认值：

| 键 | 默认值 | 含义 |
|---|---|---|
| `seek_timeout` | 10 | 元素定位超时 |
| `upload_timeout` | 30 | 文件上传超时 |
| `submit_timeout` | 30 | 提交表单超时 |
| `compress_timeout` | 180 | 等待压缩完成超时 |
| `download_timeout` | 120 | 结果文件下载超时 |

#### 日志

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `logger_name` | str | `AudioDownloader` | 记录器名与日志文件名 |
| `logger_level` | int | `10`（DEBUG） | 日志级别 |
| `logger_encoding` | str | `UTF-8` | 文件编码 |
| `logger_max_bytes` | int | `5242880` | 单文件上限（5MB） |
| `logger_backup_count` | int | `5` | 轮转备份数量 |
| `logger_format` | str | 见下 | 日志格式 |

日志格式包含模块、函数名与行号，便于在并发线程池中定位具体 worker：

```
%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s
```

#### 元数据

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `metadata_file_name` | str | `未知名称` | 无法解析文件名时的兜底名 |
| `metadata_artist` | str | `EOZT-YKDX出品` | 艺术家（`TPE1` / `ARTIST`） |
| `metadata_encoder` | str | `YKDX` | 编码者（`TENC` / `ENCODER`） |
| `metadata_publisher` | str | `YKDX` | 发布者（`TPUB` / `ORGANIZATION`） |
| `metadata_copyright` | str | `©EOZT 2025-2026` | 版权（`TCOP` / `COPYRIGHT`） |
| `metadata_author_url` | str | `https://github.com/EOZT-YKDX` | 作者链接（`WOAR`） |
| `metadata_cover_file` | str | `audio_downloader\static\EOZT.png` | 封面图路径（`APIC`） |
| `metadata_mp3_tag` | list | 8 项 | MP3 标签白名单 |
| `metadata_flac_tag` | list | 7 项 | FLAC 标签白名单 |

> ⚠️ `metadata_cover_file` 默认是**相对路径**，按进程当前工作目录解析。
> 按推荐方式 `cd src && python main.py` 启动时，它会指向 `src/audio_downloader/static/EOZT.png`（并不存在），
> `read_cover` 随即返回空字典并跳过 `APIC` 写入——封面不会生效。
> 需要封面时请把该值改为 `static/EOZT.png` 的绝对路径，或相对 CWD 的正确路径。

#### 统计报告

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stats_file_name` | str | `信息统计` | 报告文件名前缀，实际文件为 `信息统计_YYYY-MM-DD.txt` |
| `stats_dividing_line` | dict | `{"filler": "-", "length": 150}` | 分隔线填充字符与宽度，读取时展开为字符串 |
| `stats_coin` / `stats_play` / `stats_reply` / `stats_share` / `stats_collect` / `stats_danmaku` / `stats_thumb_up` | int | `0` | 各项计数指标的累加初值 |
| `stats_bvid` / `stats_title` / `stats_cover` | str | `未知bvid` / `未知标题` / `未知封面` | 字段缺失时的兜底值 |
| `stats_duration` / `stats_pubtime` | str | `00:00:00` / `0000-00-00 00:00:00` | 时长与发布时间的兜底值 |

> 报告以 `a+` 追加模式写入，同一天多次运行会累积到同一个文件中。

### 自定义配置示例

```python
config = {
    "max_download_workers": 4,
    "max_compress_workers": 6,
    "convert_audio_format": ".flac",
    "filter_labels": ["伴奏", "音质"],
    "logger_level": 20,          # INFO
    "network_retry": 3,
}

main(fid="3570962345", output_dir=r"C:\Users\YourName\Downloads\音频下载", config=config)
```

### 界面设置项

| 键 | 默认值 | 有效值 |
|---|---|---|
| `themeMode` | `system` | `light` / `dark` / `system` |
| `themeColor` | `#007aff` | 任意十六进制色值 |
| `bgType` | `image` | `solid` / `image` |
| `bgImagePath` | `static/山-极简主义.png` | 任意图片路径 |
| `outputFormat` | `mp3` | `mp3` / `flac` / `wav` / `aac` / `ogg` |
| `savePath` | `~/Downloads` | 已存在的目录 |
| `concurrentTasks` | `3` | 正整数 |
| `concurrentCompressTasks` | `5` | 正整数 |
| `language` | `zh` | `zh` / `en` / `ja` |
| `timeFormat` | `24` | `12` / `24` |
| `dateFormat` | `YMD` | `YMD` / `MDY` / `DMY` |
| `notifyStyle` | `banner` | `banner` / `silent` / `badge` |
| `notifyPosition` | `center` | `center` / `corner` |
| `soundNotify` | `false` | 布尔 |
| `previewContent` | `true` | 布尔 |
| `dndMode` | `false` | 布尔 |
| `dndStart` / `dndEnd` | `22:00` / `08:00` | `HH:MM` |

> 默认背景图 `static/山-极简主义.png` 需自行提供；缺失时背景回退为纯色，不影响其他功能。

---

## 核心流程

### 1. 应用初始化

[initialize_app](file:///c:/programming/Python-Project/Project/audio_downloader/src/app_initializer/main.py) 校验 `output_path` 是否为已存在目录 →
用 `shutil.which` 检测 `ffmpeg` / `you-get` 并记录绝对路径 → 按 `subdirectory` 递归创建目录树。
目录创建失败时返回空字典，上层据此判断是否继续。

### 2. 配置管理

[manage_config_files](file:///c:/programming/Python-Project/Project/audio_downloader/src/config_handler/main.py) 先做默认配置与磁盘 YAML 的浅合并，
再用 `_deep_update_config` 叠加 `constants` 与运行时 `config`，最后写回 YAML 并回读，
确保后续所有模块拿到的是**完整且已落盘**的配置快照。

### 3. 数据爬取

[crawl_favorites](file:///c:/programming/Python-Project/Project/audio_downloader/src/network_client/crawler/main.py)
请求媒体列表接口，用 `ps` 参数一次取回 `network_page_size` 条记录（上限 200），
配合 `fake-useragent` 随机 UA 与 `min(2 ** attempt, 5)` 指数退避重试，最多 `network_retry` 次。

> ⚠️ 当前实现**只请求单页**，没有翻页循环。收藏夹条目超过 `network_page_size` 时，
> 超出部分不会被处理；这也是 FAQ 中「收藏夹条目不全」的根因。

### 4. 过滤与去重

[filter_and_classify_data](file:///c:/programming/Python-Project/Project/audio_downloader/src/data_processor/filter/main.py)：

1. [tag_reader](file:///c:/programming/Python-Project/Project/audio_downloader/src/data_processor/filter/tag_reader.py) 用 `os.walk` 递归扫描目标目录，读取每个音频的
   `TIT3`（MP3）/ `SUBTITLE`（FLAC）标签，收集为 `set`
2. [file_filter](file:///c:/programming/Python-Project/Project/audio_downloader/src/data_processor/filter/file_filter.py) 将远端标题过滤非法字符后与该集合求差集，剔除已下载条目
3. 按 `filter_labels` 剔除黑名单命中的标题（大小写不敏感）
4. [media_data_processor](file:///c:/programming/Python-Project/Project/audio_downloader/src/data_processor/filter/media_data_processor.py) 清洗字段并生成统一结构

> **设计要点**：去重主键是**音频内部的标签**而非文件名。
> 用户手动改名不会导致重复下载；反之若用第三方工具清空标签，则会重新下载。

### 5. 并发下载与转换

[concurrent_download](file:///c:/programming/Python-Project/Project/audio_downloader/src/task_executor/downloader/main.py)
把每个条目提交到 `max_download_workers` 大小的线程池，单任务内部依次执行：

```
you-get 下载视频（tempfile.TemporaryDirectory 隔离）
      ↓
ffmpeg -y -i <input> -vn -ac 2 -f <convert_audio_format>  提取音频
      ↓
mutagen 写入 TIT3/TPE1/TENC/TPUB/TCOP/APIC/WOAR/TDRC
```

`-f` 的值取自 `convert_audio_format`（默认 `mp3`），即去掉前导点后的格式名；
重试次数由 `convert_retry` 控制，间隔为 `min(2 ** attempt, 5)` 秒。

任一环节失败只跳过当前条目，不影响其余任务；临时目录在函数退出时自动清理。

### 6. 并发压缩

[concurrent_compression](file:///c:/programming/Python-Project/Project/audio_downloader/src/task_executor/compressor/main.py)
先用 [get_pending_files](file:///c:/programming/Python-Project/Project/audio_downloader/src/task_executor/compressor/get_pending_files.py)
通过标签比对算出「原始目录有、压缩目录无」的差集，实现**断点续压**——中断后重跑只处理未压缩的文件。

单文件流程（[compress_task.py](file:///c:/programming/Python-Project/Project/audio_downloader/src/task_executor/compressor/compress_task.py) 为每个文件创建 `TemporaryDirectory`）：

```
启动 Edge（无头，下载目录 = 临时目录）
      ↓
上传文件（多候选定位：input[type=file] / name=upfile / name*=file）
      ↓
提交表单（多候选定位：id=submitbutton / input[type=submit] / button[type=submit]）
      ↓
点击下载按钮（多候选定位：a[@download] / a[href^='blob:'] ...）
      ↓
浏览器下载到临时目录（wait_for_download 按文件大小稳定度判定完成）
      ↓
移动到 Music/CompressedAudio
      ↓
关闭浏览器
```

元素定位失败时会遍历 iframe、输出页面正文快照与诊断日志，便于排查站点改版。

> `network_client.download_compress_file` 是另一条基于 `requests` 的流式下载实现
> （`stream=True` + 8KB 分块），但当前压缩流程**并未调用它**，仅作为公开接口保留。

> ⚠️ 该阶段强依赖第三方站点 `youcompress.com` 的可用性与页面结构。
> 站点改版或服务异常会直接导致压缩失败，失败项记录日志后跳过。

### 7. 重命名与归档

[extract_and_rename_files](file:///c:/programming/Python-Project/Project/audio_downloader/src/data_processor/extractor/main.py)
用 `matching_methods` 的 4 条正则提取关键词，以 `" - "` 连接成新文件名。
若目标名已存在，则**创建以该名为名的文件夹**，把已存在文件与当前文件一并移入，
保留各自原始文件名——这比 `xxx(1).mp3` 更符合「同曲多版本」的语义。

### 8. GUI 任务生命周期

`TaskHandler` 支持两类任务：

| 类型 | 输入 | 执行 |
|---|---|---|
| `link` | B站视频链接（最多 100 条） | 逐条调用 `download_bilibili_video`，产物为 `savePath` 下的视频文件，**不做转码与标签写入** |
| `favorite` | 收藏夹 ID | 走完整流水线（爬取→过滤→下载→压缩→重命名） |

任务级附加字段（由前端「添加任务」页提交，经校验器归一化后存入任务对象）：

| 字段 | 校验规则 | 说明 |
|---|---|---|
| `taskName` | `PathValidator.validate_task_name` | 任务名，非法字符将被拒绝 |
| `savePath` | `PathValidator.validate` | 必填且必须是已存在目录，为空时回退全局 `savePath` |
| `speedLimit` | `VALID_SPEED_LIMITS` = `0/500/1024/2048/5120` | 下载限速（KB/s），非法值归一为 `0` |
| `conflictAction` | `VALID_CONFLICT_ACTIONS` = `skip/overwrite/rename` | 同名冲突处理，非法值归一为 `skip` |
| `concurrentTasks` | 整数且 `1 <= n <= 10` | 任务并发数，越界或非数字时归一为 `3` |

> ⚠️ 这些任务级字段目前只写入任务对象并展示在界面，**未参与实际执行**：
> `_execute_download` 调用下载器时传入的 `config` 是空字典 `{}`，
> 因此 `speedLimit` / `conflictAction` / `concurrentTasks` 不会影响 `you-get` 与线程池行为。

后台线程执行任务并实时回写 `status` / `progress`；前端每秒轮询 `get_tasks()`，
**帧间 diff 后才重渲染**，避免无意义的 DOM 重建。

---

## 项目结构

```
audio_downloader/
├── pyproject.toml                     # 项目元数据、依赖、工具链配置
├── README.md                          # 本文件
├── .gitignore                         # 版本控制忽略规则
│
├── static/
│   └── EOZT.png                       # 默认封面图（写入 APIC 标签）
│
├── docs/                              # 设计与分析文档
│   ├── 项目报告.txt
│   ├── 项目结构.txt
│   ├── memory_leak_fix_report.md      # 前端内存泄漏修复记录
│   └── theme_system_guide.md          # 主题系统说明
│
├── tests/                             # 测试与 UI 原型
│   ├── test_metadata_editor/
│   │   └── test_main.py               # 元数据批量写入脚本（非 pytest 用例）
│   └── test_ui/                       # 界面静态原型（HTML/CSS 手工预览）
│       ├── index.html
│       ├── framework.css
│       ├── main_interface/
│       └── settings_interface/
│
└── src/
    ├── main.py                        # 命令行流水线入口
    │
    ├── app_initializer/               # 初始化：依赖检测、目录创建
    │   ├── constants.py
    │   ├── dependency_check.py
    │   ├── directory_setup.py
    │   ├── main.py
    │   └── read_constants.py
    │
    ├── config_handler/                # 配置：YAML 读写与深度合并
    │   ├── constants.py               #   全量默认配置（60 个配置键）
    │   ├── config_updater.py
    │   ├── main.py
    │   └── reader/
    │
    ├── log_setup/                     # 日志：终端 + 文件轮转
    │   ├── constants.py
    │   ├── terminal_log.py
    │   ├── file_log.py
    │   └── read_constants.py
    │
    ├── network_client/                # 网络：爬虫 + 下载器
    │   ├── crawler/                   #   收藏夹数据爬取
    │   │   ├── main.py
    │   │   └── request_handler.py
    │   └── downloader/                #   you-get 下载 / 通用文件下载
    │       ├── download_bilibili_video.py
    │       └── download_compress_file.py
    │
    ├── task_executor/                 # 调度：下载与压缩线程池
    │   ├── downloader/                #   download_task / formatter
    │   └── compressor/                #   compress_task / get_pending_files
    │
    ├── data_processor/                # 数据：过滤 / 转换 / 提取
    │   ├── filter/                    #   去重、黑名单、数据清洗
    │   │   ├── file_filter.py
    │   │   ├── tag_reader.py
    │   │   └── media_data_processor.py
    │   ├── converter/                 #   ffmpeg 视频转音频
    │   └── extractor/                 #   关键词提取与重命名
    │       ├── matcher.py
    │       └── file_rename.py
    │
    ├── audio_compressor/              # 压缩：Selenium + Edge 自动化
    │   ├── browser_manager/           #   Edge 初始化与生命周期
    │   ├── website_interaction.py     #   多候选元素定位与页面诊断
    │   └── download_manager.py        #   下载完成检测与文件快照
    │
    ├── metadata_editor/               # 元数据：MP3 / FLAC 标签与封面
    │   ├── formats/                   #   mp3.py / flac.py
    │   ├── reader/                    #   read_cover.py
    │   └── main.py
    │
    ├── stats_generator/               # 统计：格式化与报告写入
    │   ├── formatter.py
    │   └── writer.py
    │
    └── ui/                            # 图形界面（pywebview）
        ├── ui_launcher.py             #   窗口创建与 API 聚合
        ├── README.md                  #   UI 模块说明
        ├── api/                       #   前端 JS 桥接（task / settings / window）
        ├── handlers/                  #   task_handler / file_handler
        ├── validators/                #   path / url / settings / bilibili_parser
        ├── config/                    #   settings_manager
        └── frontend/                  #   HTML / CSS / JS / locales
            ├── index.html
            ├── css/                   #   frame / content / theme-dark / theme-light
            ├── js/                    #   frame / content / i18n
            └── locales/               #   zh.json / en.json / ja.json
```

---

## 技术栈

### 运行依赖

| 依赖 | 版本 | 用途 |
|---|---|---|
| `requests` | >=2.31.0 | HTTP 请求（收藏夹爬取、`download_compress_file` 流式下载） |
| `PyYAML` | >=6.0 | 配置文件读写与深度合并 |
| `mutagen` | >=1.47.0 | MP3 / FLAC 标签与封面读写 |
| `filetype` | >=1.2.0 | 封面图片 MIME 类型嗅探 |
| `fake-useragent` | >=1.4.0 | 随机 User-Agent |
| `selenium` | >=4.15.0 | 浏览器自动化（Edge 驱动由 Selenium Manager 托管） |
| `pywebview` | >=4.4.0 | 桌面窗口与 JS↔Python 桥接 |
| `you-get` | >=0.4.1700 | B站视频下载（子进程调用） |

### 外部工具

- `ffmpeg` —— 视频提取音频
- `Microsoft Edge` —— 在线压缩流程

### 标准库要点

| 模块 | 用途 |
|---|---|
| `concurrent.futures` | `ThreadPoolExecutor` 下载/压缩线程池 |
| `logging.handlers.RotatingFileHandler` | 日志文件轮转 |
| `tempfile.TemporaryDirectory` | 视频与压缩中间文件隔离 |
| `subprocess` | `you-get` / `ffmpeg` 命令调用 |
| `ctypes.wintypes` | GUI 窗口拖动与最小化控制 |
| `shutil.which` | 外部命令可用性检测 |

### 开发工具

```powershell
# 代码格式化
black src tests

# 静态检查（规则选择位于 [tool.ruff.lint]）
ruff check src tests

# 类型检查
mypy src

# 测试
pytest
```

---

## 常见问题

| 问题 | 原因与处理 |
|---|---|
| `ModuleNotFoundError: config_handler` | 未在 `src` 目录下启动。请 `cd src` 后再运行 |
| `ModuleNotFoundError: validators` | `ui_launcher.py` 需要以 `src/ui` 为导入根。请用 `python ui/ui_launcher.py` |
| 启动即报「初始化目录无效」 | `output_dir` 必须是**已存在**的目录，程序不会自动创建根目录 |
| 收藏夹返回错误码 | B站接口仅能读取公开或已授权访问的收藏夹，私密收藏夹不可读 |
| 收藏夹条目不全 | 爬取只请求单页且 `network_page_size` 校验上限为 200，超过 200 条的收藏夹无法一次取全，需分批处理 |
| 压缩阶段全部失败 | `youcompress.com` 为外部服务，页面结构变更会导致自动化失效；查看日志中的页面正文快照定位卡点 |
| 压缩时内存占用高 | 每个压缩任务独立启停 Edge，峰值进程数等于 `max_compress_workers`，建议下调至 2~4 |
| 首次压缩提示驱动下载失败 | Edge 驱动由 Selenium Manager 联网下载，需保证网络可达且当前用户具备缓存目录写入权限 |
| 音频没有封面 | `metadata_cover_file` 是相对路径，`cd src` 启动时会解析到不存在的 `src/audio_downloader/static/EOZT.png`；改为绝对路径即可 |
| 重命名失败 | Windows 路径长度或非法字符限制；可扩展 `filter_invalid_chars` |
| 暂停后任务仍在下载 | 当前 `pause_task` 仅切换 `status` 标记，后台线程不会真正中断 |
| 重复下载已存在的音频 | 标签被第三方工具清空后，去重依据（`TIT3` / `SUBTITLE`）丢失 |

### 已知限制

1. **仅支持 Windows**：GUI 窗口控制依赖 `ctypes.wintypes`，压缩流程依赖 Edge。
2. **不可作为库安装使用**：业务层裸模块名导入 + UI 层以 `src/ui` 为根的单层导入，
   二者混用导致只能以脚本方式启动。
3. **GUI 链接任务与收藏夹任务行为不对称**：`link` 类型直接调用视频下载，
   不经过 ffmpeg 转码与元数据写入，产出为视频而非成品音频。
4. **任务级参数未生效**：`speedLimit` / `conflictAction` / `concurrentTasks`
   只做校验与展示，`_execute_download` 传给下载器的 `config` 恒为空字典 `{}`。
5. **收藏夹只取单页**：无翻页循环，`network_page_size` 校验上限 200，
   更大的收藏夹无法一次处理完。
6. **默认封面路径失效**：`metadata_cover_file` 为相对路径，按推荐方式从 `src` 启动时找不到文件，
   需手动改为绝对路径才会写入 `APIC`。
7. **测试覆盖不足**：`tests/test_metadata_editor/test_main.py` 是带硬编码路径的批处理脚本，
   不含 `assert`，`pytest` 无法收集为有效用例；重构缺少回归安全网。
8. **第三方站点脆弱性**：压缩能力完全依赖 `youcompress.com` 的页面结构。

---

## 许可证

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。

Copyright (c) YKDX