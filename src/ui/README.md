# UI 模块结构说明

## 📁 目录结构

```
ui/
├── __init__.py                      # 模块入口，导出所有公共接口
├── ui_launcher.py                   # 主入口文件（窗口创建与 API 聚合）
│
├── api/                             # API 桥接层（供前端 JS 调用）
│   ├── __init__.py
│   ├── task_api.py                 # 任务管理 API
│   ├── settings_api.py             # 设置管理 API
│   └── window_api.py               # 窗口控制 API
│
├── validators/                      # 数据验证器
│   ├── __init__.py
│   ├── path_validator.py           # 路径与任务名称验证
│   ├── url_validator.py            # URL 格式验证
│   └── settings_validator.py       # 设置数据验证
│
├── handlers/                        # 业务逻辑处理器
│   ├── __init__.py
│   ├── task_handler.py             # 任务创建与执行管理
│   └── file_handler.py             # 文件选择与图片处理
│
├── config/                          # 配置管理
│   ├── __init__.py
│   └── settings_manager.py         # 设置加载/保存/更新
│
└── frontend/                        # 前端资源
    ├── index.html                   # 主页面
    ├── css/
    │   ├── frame.css               # 框架样式（布局、主题、组件）
    │   └── content.css             # 内容样式（任务列表、进度条）
    └── js/
        ├── frame.js                # 框架交互（窗口控制、设置管理）
        └── content.js              # 内容交互（任务列表管理）
```

## 🏗️ 架构设计

### 分层架构

```
┌─────────────────────────────────────────┐
│         Frontend (HTML/CSS/JS)          │  ← 视图层
├─────────────────────────────────────────┤
│              API Layer                  │  ← API 桥接层
│   (TaskApi, SettingsApi, WindowApi)     │
├─────────────────────────────────────────┤
│           Handler Layer                 │  ← 业务逻辑层
│      (TaskHandler, FileHandler)         │
├─────────────────────────────────────────┤
│          Validator Layer                │  ← 数据验证层
│  (PathValidator, UrlValidator, etc.)    │
├─────────────────────────────────────────┤
│           Config Layer                  │  ← 配置管理层
│        (SettingsManager)                │
└─────────────────────────────────────────┘
```

## 📦 模块说明

### 1. **api/** - API 桥接层

负责将后端功能暴露给前端 JavaScript，通过 pywebview 的 JS API 机制实现双向通信。

- **TaskApi**: 任务创建、查询、暂停、删除
- **SettingsApi**: 设置读取、保存、验证
- **WindowApi**: 窗口移动、最小化、关闭、文件选择

### 2. **validators/** - 数据验证器

提供独立的数据验证功能，确保所有用户输入符合规范。

- **PathValidator**: 路径合法性、长度、非法字符检查
- **UrlValidator**: URL 协议、长度、格式验证，支持批量验证
- **SettingsValidator**: 设置数据全面验证（主题、颜色、格式等）

### 3. **handlers/** - 业务逻辑处理器

实现核心业务逻辑，处理任务的创建、执行、文件操作等。

- **TaskHandler**: 任务生命周期管理（创建、执行、状态更新）
- **FileHandler**: 文件对话框、图片读取与 base64 转换

### 4. **config/** - 配置管理

负责应用设置的持久化存储。

- **SettingsManager**: JSON 文件读写、默认值管理、设置更新

### 5. **frontend/** - 前端资源

用户界面相关文件，包括 HTML 结构、CSS 样式和 JavaScript 交互逻辑。

## 🔄 数据流

```
用户操作 (前端)
    ↓
JavaScript 调用 pywebview API
    ↓
UiApi 代理方法 (ui_launcher.py)
    ↓
API 层 (api/*.py)
    ↓
Handler 层 (handlers/*.py)
    ↓
Validator 层 (validators/*.py) → 验证失败则返回错误
    ↓
Config 层 (config/*.py) → 持久化存储
    ↓
返回结果 → 前端更新 UI
```

## 💡 设计优势

### 1. **单一职责原则**
每个模块只负责一个明确的功能领域，便于理解和维护。

### 2. **依赖注入**
通过构造函数注入依赖，降低模块间耦合度。

```python
# 示例：TaskHandler 依赖注入
task_handler = TaskHandler(settings_manager, logger)
```

### 3. **组合模式**
UiApi 类通过组合各 API 模块实现功能聚合，而非继承。

```python
class UiApi:
    def __init__(self):
        self.task_api = TaskApi(...)
        self.settings_api = SettingsApi(...)
        self.window_api = WindowApi(...)
```

### 4. **可测试性**
每个模块都可独立测试，无需启动完整的 UI 应用。

## 🚀 使用示例

### 导入模块

```python
# 方式 1：从主入口导入
from ui import create_window
create_window()

# 方式 2：导入特定模块
from ui.validators import PathValidator
from ui.config import SettingsManager
from ui.handlers import TaskHandler
```

### 独立使用验证器

```python
from ui.validators import PathValidator, UrlValidator

path_validator = PathValidator()
is_valid, cleaned_path = path_validator.validate("/some/path")

url_validator = UrlValidator()
is_valid, cleaned_url = url_validator.validate("https://example.com")
```

### 独立使用设置管理器

```python
from ui.config import SettingsManager

data_dir = SettingsManager.get_data_dir()
settings_mgr = SettingsManager(data_dir)
settings = settings_mgr.load()
settings_mgr.update({"themeMode": "dark"})
settings_mgr.save()
```

## 🔧 扩展指南

### 添加新的验证器

1. 在 `validators/` 目录创建新文件
2. 实现验证方法，返回 `(bool, data)` 元组
3. 在 `validators/__init__.py` 中导出

### 添加新的 API

1. 在 `api/` 目录创建新文件
2. 实现 API 方法，接收必要依赖
3. 在 `api/__init__.py` 中导出
4. 在 `UiApi` 类中添加代理方法

### 添加新的处理器

1. 在 `handlers/` 目录创建新文件
2. 实现业务逻辑
3. 在 `handlers/__init__.py` 中导出

## 📝 注意事项

1. **路径引用**: 模块内使用相对导入（`from ..validators import ...`）
2. **线程安全**: 任务执行在独立线程中，注意共享数据的同步
3. **错误处理**: 所有公共方法都应返回统一格式的结果字典
4. **日志记录**: 使用注入的 logger 或 `logging.getLogger(__name__)`

## 🎯 后续优化建议

1. **事件系统**: 实现任务状态变更的事件推送机制
2. **异步支持**: 考虑使用 asyncio 替代 threading
3. **单元测试**: 为每个模块编写完整的测试用例
4. **类型注解**: 添加完整的类型提示支持
5. **国际化**: 实现真正的多语言支持