# -*- coding:utf-8 -*-

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/3
# Date Modified: 2026/7/28
# Program Name: metadata_editor - formats - mp3

from datetime import datetime
from mutagen.id3 import ID3, TPE1, TIT3, TPUB, TDRC, TCOP, APIC, TENC, WOAR

# 设置 MP3 文件
def set_mp3_metadata(audio_file: ID3, constants: dict) -> None:
    """
    设置 MP3 文件的元数据。
    :param audio_file: mutagen.id3.ID3 对象。
    :param constants: 配置字典, 包含 metadata_file_name, metadata_cover_file, metadata_cover_type, metadata_artist,
    metadata_encoder, metadata_copyright, metadata_author_url, metadata_publisher, metadata_mp3_tag 等参数。
    """

    # 读取配置信息
    metadata_artist = constants["metadata_artist"]
    metadata_mp3_tag = constants["metadata_mp3_tag"]
    metadata_encoder = constants["metadata_encoder"]
    metadata_file_name= constants["metadata_file_name"]
    metadata_copyright = constants["metadata_copyright"]
    metadata_publisher = constants["metadata_publisher"]
    metadata_cover_file = constants["metadata_cover_file"]
    metadata_cover_type = constants["metadata_cover_type"]
    metadata_author_url = constants["metadata_author_url"]

    # 删除旧标签
    for tag in metadata_mp3_tag:
        audio_file.delall(tag)
    
    # 设置唯一源名称，过滤掉已下载的音频
    if not audio_file.getall("TIT3"):
        audio_file.add(TIT3(encoding=3, text=metadata_file_name))
        
    # 设置封面
    if metadata_cover_file and metadata_cover_type:
        # 删除旧封面
        audio_file.delall("APIC")
        # 添加新封面
        audio_file.add(APIC(type=3, encoding=3, desc="Cover", mime=metadata_cover_type, data=metadata_cover_file))

    # 设置艺术家
    audio_file.add(TPE1(encoding=3, text=metadata_artist))
    # 设置编码人员
    audio_file.add(TENC(encoding=3, text=metadata_encoder))
    # 设置版权
    audio_file.add(TCOP(encoding=3, text=metadata_copyright))
    # 设置出版社
    audio_file.add(TPUB(encoding=3, text=metadata_publisher))
    # 设置作者 URL
    audio_file.add(WOAR(encoding=3, url=metadata_author_url))
    # 设置年份
    audio_file.add(TDRC(encoding=3, text=str(datetime.now().year)))
