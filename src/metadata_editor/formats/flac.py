# -*- coding:utf-8 -*-

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/3
# Date Modified: 2026/7/28
# Program Name: metadata_editor - formats - flac

from datetime import datetime
from mutagen.flac import FLAC, Picture

# 设置 FLAC 文件
def set_flac_metadata(audio_file: FLAC, constants: dict) -> None:
    """
    设置 FLAC 文件的元数据。
    :param audio_file: mutagen.flac.FLAC 对象。
    :param constants: 配置参数, 包含 metadata_file_name, metadata_flac_tag, metadata_artist, metadata_encoder,
    metadata_publisher, metadata_copyright, metadata_author_url, metadata_cover_file, metadata_cover_type 等参数。
    """
    
    # 读取配置信息
    metadata_artist = constants["metadata_artist"]
    metadata_encoder = constants["metadata_encoder"]
    metadata_flac_tag = constants["metadata_flac_tag"]
    metadata_file_name= constants["metadata_file_name"]
    metadata_copyright = constants["metadata_copyright"]
    metadata_publisher = constants["metadata_publisher"]
    metadata_author_url = constants["metadata_author_url"]
    metadata_cover_file = constants["metadata_cover_file"]
    metadata_cover_type = constants["metadata_cover_type"]

    # 删除旧标签
    for tag in metadata_flac_tag:
        if tag not in audio_file:
            continue

        del audio_file[tag]
    
    # 设置封面
    if metadata_cover_file and metadata_cover_type:
        # 清空现有封面
        audio_file.clear_pictures()
        
        # 添加封面
        pic = Picture()
        pic.type = 3 
        pic.data = metadata_cover_file
        pic.mime = metadata_cover_type
        audio_file.add_picture(pic)
    
    # 设置唯一源名称, 过滤掉已下载的音频
    if not audio_file.get("SUBTITLE"):
        # 设置标题
        audio_file["SUBTITLE"] = metadata_file_name
    
    # 设置艺术家
    audio_file["ARTIST"] = metadata_artist
    # 设置编码人员
    audio_file["ENCODER"] = metadata_encoder
    # 设置版权
    audio_file["COPYRIGHT"] = metadata_copyright
    # 设置作者官网
    audio_file["DESCRIPTION"] = metadata_author_url
    # 设置发布者
    audio_file["ORGANIZATION"] = metadata_publisher
    # 设置年份
    audio_file["DATE"] = str(datetime.now().year)
