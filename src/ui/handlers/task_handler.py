# -*- coding:utf-8 -*- #

"""任务处理器"""

import os
import uuid
import logging
import threading
from datetime import datetime


class TaskHandler:
    """下载任务处理与执行管理器"""

    def __init__(self, settings_manager, logger=None):
        """
        初始化任务处理器
        
        Args:
            settings_manager: 设置管理器实例
            logger: 日志记录器
        """
        self.settings_manager = settings_manager
        self.logger = logger or logging.getLogger(__name__)
        self.tasks = []

    def create_task(self, task_data, validators):
        """
        创建下载任务
        
        Args:
            task_data: 任务数据字典
            validators: 验证器字典 (path_validator, url_validator, settings_validator)
            
        Returns:
            dict: {"success": bool, "task_id": str, "error": str}
        """
        try:
            if not isinstance(task_data, dict):
                self.logger.error("任务数据格式错误")
                return {"success": False, "error": "任务数据格式错误"}
            
            task_id = str(uuid.uuid4())[:8]
            task_type = task_data.get("type", "link")
            
            if task_type not in ["link", "favorite"]:
                self.logger.warning(f"不支持的任务类型: {task_type}")
                return {"success": False, "error": "不支持的任务类型"}
            
            valid_name, task_name = validators["path_validator"].validate_task_name(
                task_data.get("taskName", "下载任务")
            )
            if not valid_name:
                return {"success": False, "error": "任务名称包含非法字符"}
            
            valid_path, save_path = validators["path_validator"].validate(
                task_data.get("savePath") or self.settings_manager.get("savePath", ""),
                allow_empty=False
            )
            if not valid_path:
                return {"success": False, "error": "保存路径不合法"}
            
            valid_conflict, conflict_action = validators["settings_validator"].validate_conflict_action(
                task_data.get("conflictAction", "skip")
            )
            
            valid_speed, speed_limit = validators["settings_validator"].validate_speed_limit(
                task_data.get("speedLimit", 0)
            )
            
            try:
                concurrent = int(task_data.get("concurrentTasks") or self.settings_manager.get("concurrentTasks", 3))
                if not (1 <= concurrent <= 10):
                    concurrent = 3
            except (ValueError, TypeError):
                concurrent = 3

            new_task = {
                "id": task_id,
                "name": task_name,
                "type": task_type,
                "status": "pending",
                "progress": 0,
                "total": 0,
                "completed": 0,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "save_path": save_path,
                "conflict_action": conflict_action,
                "speed_limit": speed_limit,
            }

            if task_type == "link":
                if not self._process_link_task(task_data, new_task, validators["url_validator"]):
                    return {"success": False, "error": new_task.get("error", "链接处理失败")}
                
            elif task_type == "favorite":
                if not self._process_favorite_task(task_data, new_task, validators["settings_validator"]):
                    return {"success": False, "error": new_task.get("error", "收藏夹处理失败")}

            self.tasks.append(new_task)
            self.logger.info(f"任务已添加: {task_name} (ID: {task_id}, 类型: {task_type})")

            thread = threading.Thread(
                target=self._execute_download,
                args=(new_task, task_data),
                daemon=True
            )
            thread.start()

            return {"success": True, "task_id": task_id}

        except Exception as e:
            self.logger.error(f"添加任务失败: {e}")
            return {"success": False, "error": str(e)}

    def get_tasks(self):
        """获取任务列表"""
        return self.tasks

    def start_task(self, task_id):
        """启动任务"""
        if not task_id or not isinstance(task_id, str):
            return {"success": False, "error": "任务 ID 格式错误"}
        
        if len(task_id) > 20:
            return {"success": False, "error": "任务 ID 格式错误"}
        
        for task in self.tasks:
            if task["id"] == task_id:
                if task["status"] in ["pending", "paused"]:
                    task["status"] = "downloading"
                    self.logger.info(f"任务已启动: {task_id}")
                    return {"success": True}
                elif task["status"] == "downloading":
                    return {"success": True}
        return {"success": False, "error": "任务不存在"}

    def pause_task(self, task_id):
        """暂停/恢复任务"""
        if not task_id or not isinstance(task_id, str):
            return {"success": False, "error": "任务 ID 格式错误"}
        
        if len(task_id) > 20:
            return {"success": False, "error": "任务 ID 格式错误"}
        
        for task in self.tasks:
            if task["id"] == task_id:
                if task["status"] == "downloading":
                    task["status"] = "paused"
                    self.logger.info(f"任务已暂停: {task_id}")
                elif task["status"] == "paused":
                    task["status"] = "downloading"
                    self.logger.info(f"任务已恢复: {task_id}")
                return {"success": True}
        return {"success": False, "error": "任务不存在"}

    def delete_task(self, task_id):
        """删除任务"""
        if not task_id or not isinstance(task_id, str):
            return {"success": False, "error": "任务 ID 格式错误"}
        
        if len(task_id) > 20:
            return {"success": False, "error": "任务 ID 格式错误"}
        
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                removed = self.tasks.pop(i)
                self.logger.info(f"任务已删除: {task_id}")
                return {"success": True}
        return {"success": False, "error": "任务不存在"}

    def update_status(self, task_id, status, progress):
        """更新任务状态"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = status
                task["progress"] = progress
                if status == "completed":
                    task["completed"] = task.get("total", 0)
                break

    def update_completed(self, task_id, completed):
        """更新已完成数量"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = completed
                total = task.get("total", 1)
                task["progress"] = int((completed / total) * 100) if total > 0 else 0
                break

    def update_speed(self, task_id, speed):
        """更新下载速度"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["speed"] = speed
                break

    def update_size(self, task_id, size):
        """更新文件大小"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["size"] = size
                break

    def _process_link_task(self, task_data, new_task, url_validator):
        """处理链接类型任务"""
        links = task_data.get("links", [])
        if not isinstance(links, list):
            new_task["error"] = "i18n:add_task.validation.links_format_error"
            return False
        
        if len(links) == 0:
            new_task["error"] = "i18n:add_task.validation.links_empty"
            return False
        
        if len(links) > 100:
            self.logger.warning(f"单次任务链接数过多: {len(links)}")
            new_task["error"] = "i18n:add_task.validation.links_too_many"
            return False
        
        validated_links, invalid_links = url_validator.validate_batch(links)
        
        if len(validated_links) == 0:
            new_task["error"] = "i18n:add_task.validation.no_valid_links"
            return False
        
        new_task["total"] = len(validated_links)
        new_task["links"] = validated_links
        return True

    def _process_favorite_task(self, task_data, new_task, settings_validator):
        """处理收藏夹类型任务"""
        valid_fid, fid = settings_validator.validate_favorite_id(task_data.get("fid", ""))
        if not valid_fid:
            new_task["error"] = "收藏夹 ID 格式错误"
            return False
        
        new_task["fid"] = fid
        new_task["total"] = 1
        return True

    def _execute_download(self, task, task_data):
        """执行下载任务（后台线程）"""
        task_id = task["id"]
        save_path = task.get("save_path", "")
        config = {}

        try:
            self.update_status(task_id, "downloading", 0)

            if task["type"] == "favorite":
                self._execute_favorite_download(task_id, task, save_path, config)
            elif task["type"] == "link":
                self._execute_link_download(task_id, task, save_path)

        except Exception as e:
            self.logger.error(f"下载任务执行失败: {e}")
            self.update_status(task_id, "failed", 0)

    def _execute_favorite_download(self, task_id, task, save_path, config):
        """执行收藏夹下载"""
        from main import main as run_downloader
        
        fid = task.get("fid", "")
        if fid:
            self.logger.info(f"开始下载收藏夹: {fid}")
            os.makedirs(save_path, exist_ok=True)
            run_downloader(fid=fid, output_dir=save_path, config=config)
            self.update_status(task_id, "completed", 100)
            self.logger.info(f"收藏夹下载完成: {fid}")
        else:
            self.update_status(task_id, "failed", 0)
            self.logger.error("收藏夹 ID 为空")

    def _execute_link_download(self, task_id, task, save_path):
        """执行链接下载"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from network_client import download_bilibili_video
        from network_client.read_constants import read_constants
        
        links = task.get("links", [])
        self.logger.info(f"开始下载链接: {len(links)} 个")
        os.makedirs(save_path, exist_ok=True)

        total = len(links)
        for i, link in enumerate(links):
            link = link.strip()
            if not link:
                continue

            progress = int((i / total) * 100)
            self.update_status(task_id, "downloading", progress)
            self.logger.info(f"正在下载链接 {i+1}/{total}: {link}")
            
            # 判断是否为B站链接
            if 'bilibili.com' in link or 'b23.tv' in link or link.startswith('BV'):
                # 构建完整的B站URL
                if link.startswith('BV'):
                    download_url = f"https://www.bilibili.com/video/{link}"
                else:
                    download_url = link
                
                # 获取视频名称
                video_name = f"video_{i+1}"
                
                # 读取下载配置
                config = {}
                constants_result = read_constants(constants=config, logger=self.logger)
                
                # 下载视频
                file_path = download_bilibili_video(
                    video_name=video_name,
                    output_path=save_path,
                    download_link=download_url,
                    constants=config,
                    logger=self.logger,
                )
                
                if file_path:
                    self.logger.info(f"视频下载成功: {file_path}")
                else:
                    self.logger.error(f"视频下载失败: {link}")
            else:
                self.logger.info(f"跳过非B站链接: {link}")
            
            self.update_completed(task_id, i + 1)

        self.update_status(task_id, "completed", 100)
        self.logger.info("链接下载完成")