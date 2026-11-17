# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: 1.0.0
# Date Creation: 2026/7/20
# Date Modified: 2026/11/17
# Program Name: audio_compressor - website_interaction

import time
import logging

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

# 上传文件输入框候选定位策略
_UPLOAD_LOCATORS = [
    (By.CSS_SELECTOR, "input[type='file']"),
    (By.NAME, "upfile"),
    (By.CSS_SELECTOR, "input[name*='file']"),
]

# 提交按钮候选定位策略
_SUBMIT_LOCATORS = [
    (By.ID, "submitbutton"),
    (By.CSS_SELECTOR, "input[type='submit']"),
    (By.CSS_SELECTOR, "button[type='submit']"),
    (By.XPATH, "//*[contains(@id, 'submit') or contains(@class, 'submit')]"),
]

# 压缩完成信号候选定位策略
# 站点为纯前端压缩, 蓝色下载链接为 blob 地址, 以 download 属性识别
_RESULT_LOCATORS = [
    (By.XPATH, "//div[contains(@class, 'success-message')]//a[@download]"),
    (By.CSS_SELECTOR, "a[download]"),
    (By.CSS_SELECTOR, "a[href^='blob:']"),
    (By.CSS_SELECTOR, "div.success-message"),
    (By.CLASS_NAME, "result-message"),
]

# 下载链接候选定位策略
# 站点为纯前端压缩, 蓝色下载链接为 blob 地址, 以 download 属性识别
_DOWNLOAD_LOCATORS = [
    (By.XPATH, "//div[contains(@class, 'success-message')]//a[@download]"),
    (By.CSS_SELECTOR, "a[download]"),
    (By.CSS_SELECTOR, "a[href^='blob:']"),
    (By.XPATH, "//a[contains(., '下载')]"),
    (By.XPATH, "//*[@id='main']/section[1]/div/div/div[2]/div[2]/div/div[2]/a"),
]

# 按候选策略依次查找元素
def _find_element(browser: webdriver.Edge, locators: list, timeout: int, logger: logging.Logger):
    """
    按候选定位策略依次查找元素, 返回首个命中的元素。
    :param browser: 浏览器实例。
    :param locators: 候选定位策略列表, 元素为 (定位方式, 定位值)。
    :param timeout: 最长等待时间。
    :param logger: 日志记录器。
    :return: 命中的元素, 全部失败时返回 None。
    """

    deadline = time.time() + timeout

    while True:
        for by, value in locators:
            try:
                element = browser.find_element(by, value)

                if element:
                    logger.debug(f"元素定位成功 - {by}: {value}")
                    return element
            except Exception:
                continue

        if time.time() >= deadline:
            return None

        time.sleep(0.5)

# 记录页面可交互元素, 便于站点改版后修正定位策略
def _log_page_diagnosis(browser: webdriver.Edge, logger: logging.Logger) -> None:
    """
    记录页面地址、input、a 元素、iframe 数量以及正文内容, 用于站点改版后的定位修正。
    :param browser: 浏览器实例。
    :param logger: 日志记录器。
    :return: None
    """

    try:
        logger.debug(f"页面地址 - {browser.current_url}")
    except Exception as error:
        logger.error(f"页面地址获取失败: {error}")

    try:
        inputs = browser.find_elements(By.TAG_NAME, "input")
        input_info = [(i.get_attribute("type"), i.get_attribute("name"), i.get_attribute("id")) for i in inputs]
        logger.debug(f"页面 input 元素 - {input_info}")
    except Exception as error:
        logger.error(f"页面 input 元素获取失败: {error}")

    try:
        links = browser.find_elements(By.TAG_NAME, "a")
        link_info = [(a.get_attribute("href"), a.get_attribute("download"), a.text[:30]) for a in links][:20]
        logger.debug(f"页面 a 元素 - {link_info}")
    except Exception as error:
        logger.error(f"页面 a 元素获取失败: {error}")

    try:
        iframes = browser.find_elements(By.TAG_NAME, "iframe")
        logger.debug(f"页面 iframe 数量 - {len(iframes)}")
    except Exception as error:
        logger.error(f"页面 iframe 获取失败: {error}")

    try:
        body = browser.find_element(By.TAG_NAME, "body")
        logger.debug(f"页面正文内容 - {body.text[:800]}")
    except Exception as error:
        logger.error(f"页面正文内容获取失败: {error}")

# 检查文件是否已挂载到上传框
def _wait_file_attached(browser: webdriver.Edge, file_input, timeout: int, logger: logging.Logger) -> bool:
    """
    等待上传框完成文件挂载, 避免上传未就绪就点击提交。
    :param browser: 浏览器实例。
    :param file_input: 上传框元素。
    :param timeout: 最长等待时间。
    :param logger: 日志记录器。
    :return: 文件是否已挂载。
    """

    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            files_length = browser.execute_script(
                "return arguments[0].files ? arguments[0].files.length : 0;", file_input
            )

            if files_length and int(files_length) > 0:
                logger.debug(f"上传框已挂载文件, 数量: {files_length}")
                return True
        except Exception as error:
            logger.debug(f"上传框文件状态读取失败: {error}")

        time.sleep(0.5)

    logger.error("上传框未挂载文件, 等待超时")
    return False

# 等待元素可点击
def _wait_element_clickable(browser: webdriver.Edge, element, timeout: int, logger: logging.Logger) -> bool:
    """
    等待元素变为可见且可用, 避免点击处于禁用状态的按钮。
    :param browser: 浏览器实例。
    :param element: 待检查的元素。
    :param timeout: 最长等待时间。
    :param logger: 日志记录器。
    :return: 元素是否可点击。
    """

    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            if element.is_displayed() and element.is_enabled():
                return True

            logger.debug(f"元素暂不可点击 - 可见: {element.is_displayed()} - 可用: {element.is_enabled()}")
        except Exception:
            pass

        time.sleep(0.5)

    return False

# 点击元素, 原生点击失败时回退到 JS 点击
def _click_element(browser: webdriver.Edge, element, logger: logging.Logger) -> bool:
    """
    点击元素, 原生点击失败时回退到 JS 点击。
    :param browser: 浏览器实例。
    :param element: 待点击的元素。
    :param logger: 日志记录器。
    :return: 是否点击成功。
    """

    try:
        element.click()
        return True
    except Exception as error:
        logger.debug(f"原生点击失败, 尝试使用 JS 点击: {error}")

    try:
        browser.execute_script("arguments[0].click();", element)
        return True
    except Exception as error:
        logger.error(f"JS 点击失败: {error}")
        return False

# 在全部 iframe 中查找元素
def _locate_in_any_frame(browser: webdriver.Edge, locators: list, timeout: int, logger: logging.Logger):
    """
    在主页面与全部 iframe 中查找元素, 找到时保持浏览器停留在对应 iframe 内。
    :param browser: 浏览器实例。
    :param locators: 候选定位策略列表。
    :param timeout: 最长等待时间。
    :param logger: 日志记录器。
    :return: (元素, iframe 序号), 未找到时返回 (None, None), 主页面命中时序号为 None。
    """

    deadline = time.time() + timeout
    last_progress_time = time.time()

    while True:
        element = _find_element(browser=browser, locators=locators, timeout=0, logger=logger)

        if element:
            return element, None

        try:
            iframes = browser.find_elements(By.TAG_NAME, "iframe")
        except Exception:
            iframes = []

        for index in range(len(iframes)):
            try:
                browser.switch_to.default_content()
                browser.switch_to.frame(index)

                element = _find_element(browser=browser, locators=locators, timeout=0, logger=logger)

                if element:
                    logger.debug(f"元素在 iframe 中定位成功 - 序号: {index}")
                    return element, index
            except Exception:
                continue

        try:
            browser.switch_to.default_content()
        except Exception:
            pass

        if time.time() >= deadline:
            return None, None

        # 每 5 秒输出一次进度, 用于判断压缩是否仍在推进
        if time.time() - last_progress_time >= 5:
            last_progress_time = time.time()

            try:
                browser.find_element(By.TAG_NAME, "body").text[:300]
            except Exception:
                logger.debug(f"等待元素中 - 剩余: {int(deadline - time.time())} 秒")

        time.sleep(0.5)

# 等待压缩完成信号
def _wait_compression_signal(browser: webdriver.Edge, timeout: int, logger: logging.Logger) -> bool:
    """
    等待压缩完成信号, 同时覆盖主页面与 iframe。
    :param browser: 浏览器实例。
    :param timeout: 最长等待时间。
    :param logger: 日志记录器。
    :return: 是否检测到压缩完成信号。
    """

    start_time = datetime.now()

    element, frame_index = _locate_in_any_frame(
        browser=browser, locators=_RESULT_LOCATORS, timeout=timeout, logger=logger
    )

    try:
        browser.switch_to.default_content()
    except Exception:
        pass

    if element is not None:
        logger.debug(f"压缩完成信号已检测到 - 累计时长: {datetime.now() - start_time}")

    return element is not None

# 上传文件
def upload_file(browser: webdriver.Edge, file_path: str, constants: dict, logger: logging.Logger) -> bool:
    """
    将文件上传到压缩网站, 并等待上传完成。
    :param browser: 浏览器实例。
    :param file_path: 文件路径。
    :param constants: 配置字典，包含 compression_timeout, compressed_file_name 等参数。
    :param logger: 日志记录器。
    :return: 是否上传成功。
    """

    # 读取配置参数
    compression_timeout = constants["compression_timeout"]
    compressed_file_name = constants["compressed_file_name"]

    # 获取超时时间
    upload_timeout = compression_timeout["upload_timeout"]

    try:
        # 等待上传按钮加载
        upfile_button = _find_element(
            browser=browser, locators=_UPLOAD_LOCATORS, timeout=upload_timeout, logger=logger
        )

        if not upfile_button:
            _log_page_diagnosis(browser=browser, logger=logger)
            logger.error(f"文件上传失败, 未找到上传输入框 - {compressed_file_name}")
            return False

        # 上传文件
        upfile_button.send_keys(file_path)

        # 确认文件已挂载到上传框
        if not _wait_file_attached(
            browser=browser, file_input=upfile_button, timeout=upload_timeout, logger=logger
        ):
            _log_page_diagnosis(browser=browser, logger=logger)
            logger.error(f"文件上传失败, 文件未挂载到上传框 - {compressed_file_name}")
            return False

        logger.debug(f"文件上传成功 - {compressed_file_name}")
        return True
    except Exception as error:
        logger.error(f"文件上传失败 - {compressed_file_name}: {error}")
        return False

# 提交压缩请求
def submit_compression_request(browser: webdriver.Edge, constants: dict, logger: logging.Logger) -> bool:
    """
    提交压缩请求, 并等待压缩完成。兼容选择文件后自动提交的站点。
    :param browser: 浏览器实例。
    :param constants: 配置字典，包含 compression_timeout, compressed_file_name 等参数。
    :param logger: 日志记录器。
    :return: 是否提交成功。
    """

    # 读取配置参数
    compression_timeout = constants["compression_timeout"]
    compressed_file_name = constants["compressed_file_name"]
    
    # 获取超时时间
    submit_timeout = compression_timeout["submit_timeout"]
    compress_timeout = compression_timeout["compress_timeout"]

    try:
        # 等待提交按钮加载, 未找到时不视为失败, 站点可能为自动提交
        submit_button = _find_element(
            browser=browser, locators=_SUBMIT_LOCATORS, timeout=submit_timeout, logger=logger
        )

        if submit_button:
            # 等待按钮变为可点击, 避免点击处于禁用状态的按钮
            clickable = _wait_element_clickable(
                browser=browser, element=submit_button, timeout=submit_timeout, logger=logger
            )

            if not clickable:
                logger.debug(f"提交按钮不可点击, 尝试强制点击 - {compressed_file_name}")

            if not _click_element(browser=browser, element=submit_button, logger=logger):
                logger.debug(f"提交按钮点击未成功, 继续等待压缩结果 - {compressed_file_name}")
        else:
            logger.debug(f"未找到提交按钮, 按自动提交处理 - {compressed_file_name}")

        # 等待压缩完成信号, 覆盖主页面与 iframe
        if not _wait_compression_signal(browser=browser, timeout=compress_timeout, logger=logger):
            _log_page_diagnosis(browser=browser, logger=logger)
            logger.error(f"未检测到压缩完成信号 - {compressed_file_name}")
            return False

        logger.debug(f"压缩请求提交成功 - {compressed_file_name}")
        return True
    except Exception as error:
        _log_page_diagnosis(browser=browser, logger=logger)
        logger.error(f"压缩请求提交失败 - {compressed_file_name}: {error}")
        return False

# 点击下载按钮
def click_download_button(browser: webdriver.Edge, constants: dict, logger: logging.Logger) -> bool:
    """
    点击下载按钮, 开始下载压缩后的文件。
    :param browser: 浏览器实例。
    :param constants: 配置字典，包含 compression_timeout, compressed_file_name 等参数。
    :param logger: 日志记录器。
    :return: 是否点击成功。
    """
    
    # 读取配置参数
    compression_timeout = constants["compression_timeout"]
    compressed_file_name = constants["compressed_file_name"]
    
    # 获取超时时间
    seek_timeout = compression_timeout["seek_timeout"]
    
    try:
        # 等待下载按钮加载, 覆盖主页面与 iframe
        download_button, frame_index = _locate_in_any_frame(
            browser=browser, locators=_DOWNLOAD_LOCATORS, timeout=seek_timeout, logger=logger
        )

        if not download_button:
            _log_page_diagnosis(browser=browser, logger=logger)
            logger.error(f"未找到下载按钮 - {compressed_file_name}")
            return False

        try:
            logger.debug(
                f"下载链接属性 - href: {download_button.get_attribute('href')} "
                f"- download: {download_button.get_attribute('download')}"
            )
        except Exception as error:
            logger.debug(f"下载链接属性读取失败: {error}")

        if not _click_element(browser=browser, element=download_button, logger=logger):
            logger.error(f"下载按钮点击失败 - {compressed_file_name}")
            return False

        logger.debug(f"下载按钮点击成功 - 序号: {frame_index} - {compressed_file_name}")
        return True
    except Exception as error:
        logger.error(f"下载按钮点击失败 - {compressed_file_name}: {error}")
        return False