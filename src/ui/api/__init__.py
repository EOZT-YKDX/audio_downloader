# -*- coding:utf-8 -*- #

"""UI API 桥接模块"""

from .task_api import TaskApi
from .settings_api import SettingsApi
from .window_api import WindowApi

__all__ = ["TaskApi", "SettingsApi", "WindowApi"]