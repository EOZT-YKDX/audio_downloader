# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/7/29
# Program Name: main

from datetime import datetime

from network_client import crawl_favorites
from app_initializer import initialize_app
from config_handler import manage_config_files
from stats_generator import generate_statistics
from log_setup import setup_file_log, setup_terminal_log
from task_executor import concurrent_download, concurrent_compression
from data_processor import filter_and_classify_data, extract_and_rename_files

# 主函数
def main(fid: str, output_dir: str, config: dict) -> None:
    """
    主函数，负责初始化、日志配置、数据爬取、并发下载和压缩。
    :param fid: B站收藏夹ID, 用于获取收藏列表。
    :param output_dir: 输出目录, 用于存储下载的文件。
    :param config: 配置字典, 包含程序运行时的参数。
    :return: None
    """

    start_time = datetime.now()

    # 创建终端日志
    terminal_logger = setup_terminal_log(constants=config)

    # 读取配置文件
    config_result = manage_config_files(config=config, output_dir=output_dir, logger=terminal_logger)

    # 初始化配置文件目录
    init_result = initialize_app(output_path=output_dir, constants=config_result, logger=terminal_logger)

    dir_result = init_result.get("dir_result", {})
    log_path = dir_result.get("log")
    data_path = dir_result.get("data")
    audio_orig_path = dir_result.get("audio_orig")
    audio_comp_path = dir_result.get("audio_comp")

    # 创建文件日志
    file_logger = setup_file_log(output_path=log_path, constants=config_result)

    # 爬取目标fid的数据
    crawl_data = crawl_favorites(fid=fid, constants=config_result, logger=file_logger)

    # 数据分类并过滤无效数据
    process_data = filter_and_classify_data(data=crawl_data, dir_path=audio_orig_path, constants=config_result, logger=file_logger)

    # 统计信息
    generate_statistics(data=process_data, output_path=data_path, constants=config_result, logger=file_logger)

    # 并发下载
    concurrent_download(data=process_data, output_path=audio_orig_path, constants=config_result, logger=file_logger)

    # 并发压缩
    concurrent_compression(input_path=audio_orig_path, output_path=audio_comp_path, constants=config_result, logger=file_logger)

    # 名称提取
    for folder_path in [audio_orig_path, audio_comp_path]:
        extract_and_rename_files(dir_path=folder_path, constants=config_result, logger=file_logger)

    file_logger.warning(f"AudioDownloader 运行完成 - 累计时长: {datetime.now() - start_time}")

if __name__ == "__main__":
    fid = "3570962345"
    config = {}
    output_dir = r"C:\Users\Lenovo\Downloads\音频下载"

    main(fid=fid, output_dir=output_dir, config=config)