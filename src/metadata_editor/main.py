# -*- coding:utf-8 -*-

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/4
# Date Modified: 2026/7/28
# Program Name: set_audio_metadata - main

import os
import logging

from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from datetime import datetime
from mutagen import File as MutagenFile

from .reader import read_cover
from .reader import read_constants
from .formats import set_mp3_metadata
from .formats import set_flac_metadata

# 设置音频元数据
def set_audio_metadata(input_path: str, constants: dict, logger: logging.Logger) -> None:
    """
    设置音频元数据, 支持 MP3, FLAC 等格式。
    :param input_path: 音频文件路径。
    :param constants: 音轨元数据, 包含 metadata_file_name, metadata_mp3_tag, metadata_flac_tag, metadata_cover_file, metadata_cover_type 等参数。
    :param logger: 日志记录器。
    :return: None
    """

    start_time = datetime.now()

    if not os.path.isfile(input_path):
        logger.error(f"音频文件路径错误: {input_path}")
        return
    
    # 获取文件名
    file_name = os.path.basename(input_path)
    file_name_without_ext = os.path.splitext(file_name)[0]
    
    # 创建配置副本，避免修改外部字典
    constants_copy = dict(constants)
    constants_copy["metadata_file_name"] = file_name_without_ext
    
    # 读取配置文件
    constants_data = read_constants(constants=constants_copy, logger=logger)
    cover_file = constants_data["metadata_cover_file"]

    # 读取封面数据
    cover_info = read_cover(cover_file=cover_file, logger=logger)
    constants_data["metadata_cover_file"] = cover_info.get("cover_data", "")
    constants_data["metadata_cover_type"] = cover_info.get("cover_type", "")

    try:
        # 使用 mutagen 通用加载器加载音频文件
        audio_file = MutagenFile(input_path, easy=False)
        
        if audio_file is None:
            logger.debug(f"无法识别的音频格式: {file_name}")
            return

        # MP3 处理
        if isinstance(audio_file, MP3):
            # 获取 MP3 文件的 ID3 标签对象
            if not audio_file.tags:
                audio_file.add_tags()

            set_mp3_metadata(audio_file=audio_file.tags, constants=constants_data)
            # 保存音频文件，指定 ID3v2.3 版本以确保兼容性
            audio_file.save(v2_version=3)
        # FLAC 处理
        elif isinstance(audio_file, FLAC):
            set_flac_metadata(audio_file=audio_file, constants=constants_data)
            audio_file.save()
        else:
            logger.error(f"音频格式无效: {file_name}")
            return

        logger.info(f"音频文件元数据处理完成: {file_name} - 累计时长: {datetime.now() - start_time}")
    except Exception as error:
        logger.error(f"音频文件元数据处理失败: {file_name} - {error}")
        return