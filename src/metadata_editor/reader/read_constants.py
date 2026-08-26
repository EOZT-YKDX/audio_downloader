# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/28
# Program Name: metadata_editor - read_constants

import logging

from ..constants import (
    DEFAULT_METADATA_FILE_NAME, DEFAULT_METADATA_MP3_TAG, DEFAULT_METADATA_FLAC_TAG,
    DEFAULT_METADATA_ENCODER, DEFAULT_METADATA_PUBLISHER, DEFAULT_METADATA_ARTIST, DEFAULT_METADATA_COPYRIGHT,
    DEFAULT_METADATA_AUTHOR_URL, DEFAULT_METADATA_COVER_FILE
    )

# 读取配置参数
def read_constants(constants: dict, logger: logging.Logger) -> dict:
    """
    读取音轨元数据配置参数, 并验证参数是否有效。
    :param constants: 配置字典, 包含 metadata_file_name, metadata_mp3_tag, metadata_flac_tag, metadata_artist, metadata_encoder,
    metadata_publisher, metadata_copyright, metadata_author_url, metadata_cover_file 等参数。
    :param logger: 日志记录器。
    :return: dict: 验证后的音轨元数据配置。
    """

    # 获取配置参数
    metadata_file_name = constants.get("metadata_file_name", DEFAULT_METADATA_FILE_NAME)

    metadata_mp3_tag = constants.get("metadata_mp3_tag", DEFAULT_METADATA_MP3_TAG)
    metadata_flac_tag = constants.get("metadata_flac_tag", DEFAULT_METADATA_FLAC_TAG)

    metadata_artist = constants.get("metadata_artist", DEFAULT_METADATA_ARTIST)
    metadata_encoder = constants.get("metadata_encoder", DEFAULT_METADATA_ENCODER)
    metadata_publisher = constants.get("metadata_publisher", DEFAULT_METADATA_PUBLISHER)
    metadata_copyright = constants.get("metadata_copyright", DEFAULT_METADATA_COPYRIGHT)
    metadata_author_url = constants.get("metadata_author_url", DEFAULT_METADATA_AUTHOR_URL)
    metadata_cover_file = constants.get("metadata_cover_file", DEFAULT_METADATA_COVER_FILE)
    
    # 检查参数是否有效
    if not isinstance(metadata_file_name, str) or not metadata_file_name:
        metadata_file_name = DEFAULT_METADATA_FILE_NAME
        logger.error(f"文件名配置项无效 - 已设置为默认值")


    if not isinstance(metadata_mp3_tag, list) or not metadata_mp3_tag:
        metadata_mp3_tag = DEFAULT_METADATA_MP3_TAG
        logger.error(f"MP3标签配置项无效 - 已设置为默认值")

    if not isinstance(metadata_flac_tag, list) or not metadata_flac_tag:
        metadata_flac_tag = DEFAULT_METADATA_FLAC_TAG
        logger.error(f"FLAC标签配置项无效 - 已设置为默认值")


    if not isinstance(metadata_encoder, str) or not metadata_encoder:
        metadata_encoder = DEFAULT_METADATA_ENCODER
        logger.error(f"编码器配置项无效 - 已设置为默认值")

    if not isinstance(metadata_publisher, str) or not metadata_publisher:
        metadata_publisher = DEFAULT_METADATA_PUBLISHER
        logger.error(f"发布者配置项无效 - 已设置为默认值")

    if not isinstance(metadata_artist, str) or not metadata_artist:
        metadata_artist = DEFAULT_METADATA_ARTIST
        logger.error(f"艺术家配置项无效 - 已设置为默认值")

    if not isinstance(metadata_copyright, str) or not metadata_copyright:
        metadata_copyright = DEFAULT_METADATA_COPYRIGHT
        logger.error(f"版权信息配置项无效 - 已设置为默认值")

    if not isinstance(metadata_author_url, str) or not metadata_author_url:
        metadata_author_url = DEFAULT_METADATA_AUTHOR_URL
        logger.error(f"作者链接配置项无效 - 已设置为默认值")

    if not isinstance(metadata_cover_file, str) or not metadata_cover_file:
        metadata_cover_file = DEFAULT_METADATA_COVER_FILE
        logger.error(f"封面文件配置项无效 - 已设置为默认值")

    # 构建配置字典
    constants_result = {
        "metadata_file_name": metadata_file_name,
        
        "metadata_artist": metadata_artist,
        "metadata_encoder": metadata_encoder,
        "metadata_publisher": metadata_publisher,
        "metadata_copyright": metadata_copyright,
        "metadata_author_url": metadata_author_url,
        "metadata_cover_file": metadata_cover_file,
        
        "metadata_mp3_tag": metadata_mp3_tag,
        "metadata_flac_tag": metadata_flac_tag,
    }
    
    return constants_result
