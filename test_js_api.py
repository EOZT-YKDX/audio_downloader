# -*- coding:utf-8 -*- #
# pywebview JS API 原理演示

import os
import webview
from pathlib import Path

class Api:
    def say_hello(self, name):
        """接收 JS 传递的参数并返回"""
        print(f"JS 调用 say_hello, 参数: {name}")
        return f"Hello, {name} from Python!"

    def get_data(self):
        """返回字典, 自动序列化为 JS 对象"""
        return {'x': 10, 'y': 20}

    def select_folder(self, current_path=""):
        """选择文件夹, 使用 os 模块处理路径"""
        try:
            initial_dir = current_path if current_path and os.path.isdir(current_path) else str(Path.home())
            
            file_path = webview.windows[0].create_file_dialog(
                dialog_type=webview.OPEN_DIALOG,
                directory=initial_dir
            )
            
            if file_path and len(file_path) > 0:
                selected_path = file_path[0]
                abs_path = os.path.abspath(selected_path)
                normalized_path = os.path.normpath(abs_path)
                print(f"选择的文件夹: {normalized_path}")
                return normalized_path
            
            return ""
        except Exception as e:
            print(f"选择文件夹失败: {e}")
            return ""

    def get_default_path(self):
        """使用 os 模块生成默认路径"""
        default_path = str(Path.home() / "Downloads" / "Audio")
        abs_path = os.path.abspath(default_path)
        normalized_path = os.path.normpath(abs_path)
        return normalized_path

api = Api()

html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Microsoft YaHei", sans-serif;
            padding: 20px;
            background: #1c1c1e;
            color: #fff;
        }
        button {
            padding: 10px 20px;
            margin: 10px 5px;
            border: none;
            border-radius: 6px;
            background: #007aff;
            color: #fff;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background: #0056b3;
        }
        .result {
            margin-top: 15px;
            padding: 15px;
            background: #2b2b2d;
            border-radius: 6px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .path-display {
            margin-top: 15px;
            padding: 15px;
            background: #2b2b2d;
            border-radius: 6px;
            border-left: 4px solid #007aff;
        }
        .path-display label {
            display: block;
            margin-bottom: 8px;
            color: #999;
            font-size: 12px;
        }
        .path-display input {
            width: 100%;
            padding: 10px;
            border: 1px solid #3a3a3c;
            border-radius: 4px;
            background: #3a3a3c;
            color: #fff;
            font-size: 14px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h2>pywebview JS API 原理演示</h2>
    
    <button onclick="callSayHello()">调用 say_hello</button>
    <button onclick="callGetData()">调用 get_data</button>
    <button onclick="callSelectFolder()">选择文件夹</button>
    <button onclick="callGetDefaultPath()">获取默认路径</button>
    
    <div class="result" id="result">等待调用...</div>
    
    <div class="path-display">
        <label>默认保存路径（使用 os 模块生成）</label>
        <input type="text" id="savePathInput" placeholder="点击按钮获取路径" readonly>
    </div>

    <script>
        async function callSayHello() {
            const msg = await window.pywebview.api.say_hello('World');
            document.getElementById('result').textContent = msg;
        }

        async function callGetData() {
            const data = await window.pywebview.api.get_data();
            document.getElementById('result').textContent = 
                `x: ${data.x}\\ny: ${data.y}\\n类型: ${typeof data}`;
        }

        async function callSelectFolder() {
            const currentPath = document.getElementById('savePathInput').value;
            const path = await window.pywebview.api.select_folder(currentPath);
            if (path) {
                document.getElementById('savePathInput').value = path;
                document.getElementById('result').textContent = `已选择:\\n${path}`;
            }
        }

        async function callGetDefaultPath() {
            const path = await window.pywebview.api.get_default_path();
            document.getElementById('savePathInput').value = path;
            document.getElementById('result').textContent = `默认路径:\\n${path}`;
        }
    </script>
</body>
</html>
'''

window = webview.create_window(
    'JS API Demo',
    html=html_content,
    js_api=api,
    width=800,
    height=600
)

webview.start(debug=True)