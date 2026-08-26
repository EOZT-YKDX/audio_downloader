# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/29
# Program Name: config_handler - config_updater

import os
import yaml
import logging

# 深度更新配置
def _deep_update_config(base_config: dict, updates: dict) -> dict:
    """
    递归深度更新配置字典，支持跨层级键匹配。
    :param base_config: 基础配置字典。
    :param updates: 更新配置字典。
    :return: 更新后的配置字典。
    """

    for key, value in updates.items():
        # 尝试在base_config中找到匹配的键
        matched_key = None

        for base_key in base_config:
            if base_key.lower() == key.lower():
                matched_key = base_key
                break

        if matched_key is not None:
            # 如果两者都是字典，递归更新
            if isinstance(value, dict) and isinstance(base_config[matched_key], dict):
                _deep_update_config(base_config=base_config[matched_key], updates=value)
            else:
                base_config[matched_key] = value
        else:
            # 如果顶层找不到，尝试在嵌套字典中搜索
            _search_and_update(config=base_config, key=key, value=value)

    return base_config

# 搜索并更新嵌套字典
def _search_and_update(config: dict, key: str, value: any) -> bool:
    """
    在嵌套字典中搜索键并更新。
    :param config: 配置字典。
    :param key: 要搜索的键。
    :param value: 要更新的值。
    :return: 是否找到并更新。
    """

    for config_key, config_value in config.items():
        if config_key.lower() == key.lower():
            config[config_key] = value
            return True

        if not isinstance(config_value, dict):
            continue

        if _search_and_update(config=config_value, key=key, value=value):
            return True

    return False

# 更新配置
def update_config(config: dict, constants: dict, output_path: str, logger: logging.Logger) -> None:
    """
    更新配置文件，如果文件不存在则创建默认配置。
    :param config: 配置字典。
    :param constants: 常量配置, 包含 original_config 等参数。
    :param output_path: 配置文件路径。
    :param logger: 日志记录器。
    :return: None
    """

    file_name = os.path.basename(output_path)
    default_config = constants["original_config"]

    try:
        if os.path.isfile(output_path):
            with open(file=output_path, encoding="utf-8", mode="r") as file:
                existing_config = yaml.safe_load(file)
        else:
            existing_config = {}

        # 合并配置
        merged_config = {**default_config, **existing_config}

        # 使用 constants 深度更新配置
        if constants:
            _deep_update_config(base_config=merged_config, updates=constants)

        # 使用 config 参数深度更新配置
        if config:
            _deep_update_config(base_config=merged_config, updates=config)

        # 写入配置文件
        with open(mode="w", encoding="utf-8", file=output_path) as file:
            yaml.dump(
                indent=4,                   # 缩进宽度
                stream=file,                # 输出目标
                sort_keys=False,            # 不排序键
                data=merged_config,         # 待序列化数据
                allow_unicode=True,         # 允许使用Unicode字符
                Dumper=yaml.SafeDumper,     # 安全的序列化器
            )
            logger.debug(f"配置文件已更新: {file_name}")
    except Exception as error:
        logger.error(f"配置文件更新失败: {file_name} - {error}")