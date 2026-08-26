# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/30
# Program Name: app_initializer - dependency_check

import shutil
import logging

# 检测依赖工具
def check_dependency_tools(dependency_tools: list, logger: logging.Logger) -> dict:
    """
    检测系统环境是否包含依赖工具。
    :param dependency_tools: 依赖工具列表。
    :param logger: 日志记录器。
    :return: 依赖工具绝对路径字典。
    """

    failed = 0
    succeed = 0

    tool_list = {}
    missing_tools = []

    for tool in dependency_tools:
        tool_result = shutil.which(tool)

        if not tool_result:
            missing_tools.append(tool)
            failed += 1
            continue

        succeed += 1
        tool_list[tool] = tool_result
        logger.debug(f"{tool} 的绝对路径: {tool_result}")

    if missing_tools:
        logger.error(f"未找到以下依赖工具: {missing_tools}")

    logger.debug(f"依赖工具检测完成 - 总计: {len(dependency_tools)} - 成功: {succeed} - 失败: {failed}")

    check_result = {
        "status": failed == 0,
        "tool_list": tool_list,
        "missing_tools": missing_tools,
    }
    return check_result
