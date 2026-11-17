# -*- coding:utf-8 -*- #

"""URL 验证器"""

import re
import logging


class UrlValidator:
    """URL 验证工具类"""

    MAX_URL_LENGTH = 2048
    SUPPORTED_PROTOCOLS = ['http://', 'https://', 'ftp://', 'bilibili.com']
    BVID_PATTERN = re.compile(r'^BV1[A-Za-z0-9]{9}$')

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def validate(self, url):
        """
        验证 URL 格式
        
        Args:
            url: 待验证的 URL 字符串
            
        Returns:
            tuple: (是否有效, 清理后的 URL)
        """
        if not url or not url.strip():
            return False, ""
        
        url = url.strip()
        
        if len(url) > self.MAX_URL_LENGTH:
            self.logger.warning(f"URL 过长: {len(url)} 字符")
            return False, ""
        
        # 支持直接输入 BV 号
        if self.BVID_PATTERN.match(url):
            return True, url
        
        url_lower = url.lower()
        if not any(url_lower.startswith(proto) for proto in self.SUPPORTED_PROTOCOLS):
            self.logger.warning(f"URL 协议不支持: {url[:50]}...")
            return False, ""
        
        return True, url

    def validate_batch(self, urls):
        """
        批量验证 URL 列表
        
        Args:
            urls: URL 列表
            
        Returns:
            tuple: (有效 URL 列表, 无效 URL 列表)
        """
        valid_urls = []
        invalid_urls = []
        
        for url in urls:
            is_valid, cleaned_url = self.validate(url)
            if is_valid:
                valid_urls.append(cleaned_url)
            else:
                invalid_urls.append(url)
                self.logger.warning(f"跳过无效链接: {url[:50]}...")
        
        return valid_urls, invalid_urls