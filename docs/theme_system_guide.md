# 主题系统架构文档

## 📋 概述

Audio Downloader 使用基于 **CSS 文件切换** 的主题系统，完全消除了硬编码的主题变量。每个主题都有独立的 CSS 文件，通过动态替换 `<link>` 元素的 `href` 属性实现主题切换。

---

## 🏗️ 架构设计

### 文件结构

```
src/ui/frontend/
├── css/
│   ├── frame.css          # 基础框架样式（包含默认主题变量）
│   ├── content.css        # 内容样式
│   ├── theme-dark.css     # 深色主题变量
│   └── theme-light.css    # 浅色主题变量
├── js/
│   └── frame.js           # 主题管理逻辑
└── index.html             # 引入主题样式表
```

### 核心组件

1. **主题配置文件** (`theme-*.css`)
   - 每个主题一个独立的 CSS 文件
   - 定义所有 CSS 变量

2. **主题管理器** (`frame.js`)
   - `THEME_CONFIG`: 主题配置映射
   - `applyThemeMode()`: 应用主题模式（light/dark/system）
   - `switchTheme()`: 切换主题
   - `initSystemThemeWatcher()`: 监听系统主题变化

3. **样式表元素** (`<link id="theme-stylesheet">`)
   - 动态更新 `href` 属性切换主题

---

## 🎨 创建新主题

### 步骤 1: 创建主题 CSS 文件

在 `src/ui/frontend/css/` 目录下创建新的主题文件，例如 `theme-blue.css`：

```css
/* ============================================
   Audio Downloader - Blue Theme
   ============================================ */

:root {
    /* 背景色 */
    --bg-primary: #0a192f;
    --bg-secondary: #112240;
    --bg-tertiary: #233554;
    
    /* 文本色 */
    --text-primary: #ccd6f6;
    --text-secondary: #8892b0;
    
    /* 边框色 */
    --border-color: #1d3a5f;
    
    /* 强调色 */
    --primary-color: #64ffda;
    
    /* 状态色 */
    --success-color: #34c759;
    --warning-color: #ff9500;
    --error-color: #ff3b30;
}
```

### 步骤 2: 更新 THEME_CONFIG

在 `frame.js` 的 `THEME_CONFIG` 对象中添加新主题：

```javascript
const THEME_CONFIG = {
    dark: {
        file: 'css/theme-dark.css',
        label: '深色',
        isDark: true
    },
    light: {
        file: 'css/theme-light.css',
        label: '浅色',
        isDark: false
    },
    blue: {  // 新增主题
        file: 'css/theme-blue.css',
        label: '蓝色',
        isDark: true
    }
};
```

### 步骤 3: 添加主题切换按钮（可选）

在设置页面的 HTML 中添加新主题的切换按钮：

```html
<button class="theme-mode-btn" data-mode="blue">蓝色</button>
```

---

## 🔧 主题变量说明

### 必需变量

所有主题文件必须包含以下变量：

| 变量名 | 用途 | 示例值 |
|--------|------|--------|
| `--bg-primary` | 主背景色 | `#1c1c1e` |
| `--bg-secondary` | 次背景色 | `#2c2c2e` |
| `--bg-tertiary` | 第三背景色 | `#3a3a3c` |
| `--text-primary` | 主文本色 | `#ffffff` |
| `--text-secondary` | 次文本色 | `#8e8e93` |
| `--border-color` | 边框色 | `#38383a` |
| `--primary-color` | 强调色 | `#007aff` |

### 可选变量

| 变量名 | 用途 | 示例值 |
|--------|------|--------|
| `--success-color` | 成功状态色 | `#34c759` |
| `--warning-color` | 警告状态色 | `#ff9500` |
| `--error-color` | 错误状态色 | `#ff3b30` |

---

## 💡 使用示例

### JavaScript API

```javascript
// 切换主题
applyThemeMode('light');    // 浅色主题
applyThemeMode('dark');     // 深色主题
applyThemeMode('system');   // 跟随系统

// 获取当前主题
const theme = getCurrentTheme();  // 返回: 'dark' | 'light'

// 手动切换（绕过模式逻辑）
switchTheme('light');
```

### CSS 中使用主题变量

```css
.my-component {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

.my-button {
    background: var(--primary-color);
    color: white;
}
```

### 根据主题应用不同样式

```css
/* 深色主题下的特殊样式 */
[data-theme="dark"] .my-component {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

/* 浅色主题下的特殊样式 */
[data-theme="light"] .my-component {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
```

---

## 🔄 主题切换流程

```
用户点击主题按钮
    ↓
initThemeModeButtons() 触发
    ↓
applyThemeMode(mode)
    ↓
[如果是 system 模式]
    ↓
检测系统主题偏好
    ↓
switchTheme(themeName)
    ↓
更新 <link id="theme-stylesheet"> 的 href
    ↓
浏览器加载新主题 CSS 文件
    ↓
CSS 变量自动更新
    ↓
页面样式实时更新
```

---

## 🎯 优势

### ✅ 相比硬编码的优势

1. **零硬编码**: 所有主题变量都在独立文件中
2. **易于扩展**: 添加新主题只需创建 CSS 文件
3. **性能更好**: 浏览器原生 CSS 变量更新比 JS 设置更快
4. **维护简单**: 修改主题只需编辑 CSS 文件
5. **类型安全**: CSS 文件可以被 linter 检查
6. **支持预览**: 可以单独打开主题文件预览效果

### 📊 性能对比

| 方式 | 切换速度 | 内存占用 | 可维护性 |
|------|----------|----------|----------|
| 硬编码 (旧) | 慢 (多次 DOM 操作) | 高 (JS 对象) | 低 |
| CSS 文件 (新) | 快 (浏览器原生) | 低 (CSSOM) | 高 |

---

## 🧪 测试

使用主题测试工具验证主题系统：

```bash
# 打开测试页面
tests/theme_test.html
```

测试项目：
- ✅ 主题切换功能
- ✅ CSS 变量更新
- ✅ 组件样式适配
- ✅ 系统主题跟随
- ✅ 主题文件加载

---

## 📝 最佳实践

### 1. 命名规范

- 主题文件命名: `theme-{name}.css`
- 变量命名: `--{category}-{property}` (如 `--bg-primary`)

### 2. 变量组织

```css
:root {
    /* 背景色 */
    --bg-primary: #...;
    --bg-secondary: #...;
    
    /* 文本色 */
    --text-primary: #...;
    --text-secondary: #...;
    
    /* 边框色 */
    --border-color: #...;
    
    /* 强调色 */
    --primary-color: #...;
    
    /* 状态色 */
    --success-color: #...;
    --warning-color: #...;
    --error-color: #...;
}
```

### 3. 颜色选择

- 使用设计系统颜色（如 Material Design、Apple HIG）
- 确保对比度符合 WCAG 2.1 标准（至少 4.5:1）
- 避免使用纯黑 (#000000) 或纯白 (#ffffff)

### 4. 主题预览

创建主题时，使用 `tests/theme_test.html` 预览效果：
1. 修改主题 CSS 文件
2. 刷新测试页面
3. 检查所有组件样式
4. 验证对比度

---

## 🔮 未来扩展

### 计划功能

1. **自定义主题编辑器**: 可视化编辑主题变量
2. **主题导入/导出**: 支持 JSON 格式的主题配置
3. **主题市场**: 用户分享自定义主题
4. **渐变背景**: 支持渐变主题背景
5. **动画过渡**: 主题切换时的平滑过渡动画

### 自定义主题 API

```javascript
// 未来可能支持的功能
createCustomTheme({
    name: 'My Theme',
    variables: {
        '--bg-primary': '#...',
        '--text-primary': '#...',
        // ...
    }
});

// 导入主题
importTheme('theme.json');

// 导出主题
exportTheme();
```

---

## 📚 相关资源

- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [CSS Color Module](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value)
- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**文档版本**: 1.0  
**最后更新**: 2026-09-13  
**维护人员**: AI Assistant