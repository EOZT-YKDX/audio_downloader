# -*- coding:utf-8 -*- #

"""任务 API"""

import logging


class TaskApi:
    """任务管理 API（供前端 JS 调用）"""

    def __init__(self, task_handler):
        """
        初始化任务 API
        
        Args:
            task_handler: 任务处理器实例
        """
        self.task_handler = task_handler
        self.logger = logging.getLogger(__name__)

    def get_tasks(self):
        """获取任务列表"""
        return self.task_handler.get_tasks()

    def start_download(self, task_data):
        """开始下载任务"""
        return self.task_handler.create_task(task_data, self._get_validators())

    def start_task(self, task_id):
        """启动任务"""
        return self.task_handler.start_task(task_id)

    def pause_task(self, task_id):
        """暂停/恢复任务"""
        return self.task_handler.pause_task(task_id)

    def delete_task(self, task_id):
        """删除任务"""
        return self.task_handler.delete_task(task_id)

    def parse_bilibili_links(self, urls):
        """解析B站链接"""
        validators = self._get_validators()
        bilibili_parser = validators.get("bilibili_parser")
        if not bilibili_parser:
            return {"success": False, "error": "i18n:parse.parser_not_initialized"}
        
        results = bilibili_parser.parse_batch(urls)
        return {"success": True, "results": results}

    def parse_bilibili_favorites(self, fid):
        """解析B站收藏夹"""
        validators = self._get_validators()
        bilibili_parser = validators.get("bilibili_parser")
        if not bilibili_parser:
            return {"success": False, "error": "i18n:parse.parser_not_initialized"}
        
        result = bilibili_parser.parse_favorites(fid)
        if result:
            return {"success": True, "result": result}
        return {"success": False, "error": "i18n:parse.favorite_failed"}

    def _get_validators(self):
        """获取验证器字典（由父类注入）"""
        return getattr(self, '_validators', {})

    def set_validators(self, validators):
        """
        设置验证器字典
        
        Args:
            validators: 包含 path_validator, url_validator, settings_validator 的字典
        """
        self._validators = validators