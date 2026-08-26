# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/22
# Date Modified: 2026/7/27
# Program Name: data_processor - extractor - matcher

import re
import logging

# 从文件名中提取有效关键字
def extract_keywords(file: str, constants: dict, logger: logging.Logger) -> list:
    """
    从文件名中提取有效关键字, 并返回匹配项列表。
    :param file: 原始文件名。
    :param constants: 配置参数字典, 包含 filter_labels, matching_methods 等参数。
    :param logger: 日志记录器。
    :return: 有效匹配项列表。
    """

    matches = []
    lower_labels = []

    filter_labels = constants["filter_labels"]
    matching_methods = constants["matching_methods"]

    # 转换黑名单标签为小写
    for label in filter_labels:
        lower_labels.append(label.lower())

    for method in matching_methods:
        # 跳过无效的正则表达式
        try:
            pattern = re.compile(method)
        except Exception as error:
            logger.error(f"无效的正则表达式: {method} - {error}")
            continue

        # 移除首尾空格
        handled_file = file.strip()

        # 使用正则表达式查找所有匹配项
        for match in pattern.findall(handled_file):
             # 处理元组类型的匹配结果
            if isinstance(match, tuple) and match:
                # 提取第一个捕获组
                match_result = match[0]
            else:
                match_result = match
            
            # 移除首尾空格
            handled_match = match_result.strip()
            # 转换为小写, 用于匹配黑名单标签
            lower_match = handled_match.lower()

            # 过滤空字符串和黑名单标签
            if not handled_match or lower_match in lower_labels:
                continue
            
            matches.append(handled_match)

    return matches
