# -*- coding:utf-8 -*- #

"""设置 API"""

import logging


class SettingsApi:
    """设置管理 API（供前端 JS 调用）"""

    def __init__(self, settings_manager, settings_validator, file_handler):
        """
        初始化设置 API
        
        Args:
            settings_manager: 设置管理器实例
            settings_validator: 设置验证器实例
            file_handler: 文件处理器实例
        """
        self.settings_manager = settings_manager
        self.settings_validator = settings_validator
        self.file_handler = file_handler
        self.logger = logging.getLogger(__name__)

    def get_settings(self):
        """获取当前设置"""
        return self.settings_manager.get_all()

    def save_settings(self, settings):
        """保存设置到内存和文件"""
        try:
            valid, validated_settings, errors = self.settings_validator.validate_settings(settings)
            if not valid:
                error_msg = "; ".join(errors) if errors else "设置验证失败"
                self.logger.error(f"保存设置失败: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "errors": errors
                }
            
            self.settings_manager.update(validated_settings)
            self.settings_manager.save()
            self.logger.info("设置已保存并验证通过")
            return {
                "success": True,
                "message": "设置已保存"
            }
        except Exception as e:
            self.logger.error(f"保存设置异常: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"保存设置失败: {str(e)}"
            }

    def get_bg_image_data(self, image_path):
        """根据图片路径返回 base64 编码"""
        return self.file_handler.get_image_data(image_path)

    def get_default_path(self):
        """获取默认保存路径"""
        from ..validators.path_validator import PathValidator
        return PathValidator.get_default_path()

    def reset_settings(self):
        """恢复默认设置"""
        try:
            success = self.settings_manager.reset_to_defaults()
            if success:
                self.logger.info("设置已恢复为默认值")
                return {"success": True}
            else:
                return {"success": False, "error": "恢复默认设置失败"}
        except Exception as e:
            self.logger.error(f"恢复默认设置失败: {e}")
            return {"success": False, "error": str(e)}