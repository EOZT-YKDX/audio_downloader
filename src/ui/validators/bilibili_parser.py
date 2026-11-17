# -*- coding:utf-8 -*- #

"""B站链接解析器"""

import re
import logging
import requests

from fake_useragent import UserAgent


class BilibiliParser:
    """B站链接解析工具类"""

    BILIBILI_VIDEO_PATTERNS = [
        # BV号: https://www.bilibili.com/video/BV1xx411c7mD
        re.compile(r'bilibili\.com/video/(BV\w+)'),
        # AV号: https://www.bilibili.com/video/av12345678
        re.compile(r'bilibili\.com/video/(?:av|AV)(\d+)'),
        # 短链接: https://b23.tv/xxxxx
        re.compile(r'b23\.tv/(\w+)'),
        # 分享链接: https://www.bilibili.com/video/BV1xx411c7mD/?share_source=xxx
        re.compile(r'bilibili\.com/video/(BV\w+)\?'),
    ]

    BVID_PATTERN = re.compile(r'^BV1[A-Za-z0-9]{9}$')

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def is_bilibili_url(self, url):
        """判断是否为B站链接"""
        url_lower = url.lower()
        return 'bilibili.com' in url_lower or 'b23.tv' in url_lower

    def extract_bvid(self, url):
        """从URL中提取BV号"""
        for pattern in self.BILIBILI_VIDEO_PATTERNS:
            match = pattern.search(url)
            if match:
                vid = match.group(1)
                # 如果是AV号，需要转换为BV号
                if vid.isdigit():
                    return self.aid_to_bvid(int(vid))
                return vid
        return None

    def parse_video(self, bvid):
        """
        解析B站视频信息
        
        Args:
            bvid: B站视频BV号
            
        Returns:
            dict: 视频信息，包含 title, author, duration, view, danmaku, reply, pubdate 等
        """
        if not bvid:
            return None

        try:
            url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            
            user_agent = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            response = requests.get(
                url=url,
                timeout=10,
                headers={
                    "Referer": "https://www.bilibili.com",
                    "User-Agent": user_agent.random,
                },
            )

            if response.status_code != 200:
                self.logger.warning(f"B站API请求失败: {response.status_code}")
                return None

            result = response.json()
            
            if result.get("code") != 0:
                self.logger.warning(f"B站API返回错误: {result.get('message')}")
                return None

            data = result.get("data", {})
            if not data:
                return None

            return {
                "bvid": data.get("bvid", bvid),
                "title": data.get("title", "未知标题"),
                "author": data.get("owner", {}).get("name", "未知作者"),
                "duration": self._format_duration(data.get("duration", 0)),
                "view": self._format_count(data.get("stat", {}).get("view", 0)),
                "danmaku": self._format_count(data.get("stat", {}).get("danmaku", 0)),
                "reply": self._format_count(data.get("stat", {}).get("reply", 0)),
                "pubdate": self._format_date(data.get("pubdate", 0)),
                "desc": data.get("desc", "")[:100],
            }

        except Exception as e:
            self.logger.error(f"解析B站视频失败: {e}")
            return None

    def parse_batch(self, urls):
        """
        批量解析B站链接
        
        Args:
            urls: URL列表
            
        Returns:
            list: 解析结果列表
        """
        results = []
        for url in urls:
            url = url.strip()
            if not url:
                continue
            
            # 直接输入BV号
            if self.BVID_PATTERN.match(url):
                video_info = self.parse_video(url)
                if video_info:
                    video_info["url"] = url
                    video_info["type"] = "video"
                    results.append(video_info)
                else:
                    results.append({
                        "url": url,
                        "bvid": url,
                        "type": "video",
                        "error": "解析失败",
                    })
                continue
            
            if not self.is_bilibili_url(url):
                results.append({
                    "url": url,
                    "type": "unknown",
                    "error": "非B站链接",
                })
                continue

            bvid = self.extract_bvid(url)
            if not bvid:
                results.append({
                    "url": url,
                    "type": "unknown",
                    "error": "无法提取视频ID",
                })
                continue

            video_info = self.parse_video(bvid)
            if video_info:
                video_info["url"] = url
                video_info["type"] = "video"
                results.append(video_info)
            else:
                results.append({
                    "url": url,
                    "bvid": bvid,
                    "type": "video",
                    "error": "解析失败",
                })

        return results

    @staticmethod
    def _format_duration(seconds):
        """格式化时长"""
        if not seconds:
            return "00:00"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def _format_count(num):
        """格式化数字"""
        if num >= 10000:
            return f"{num / 10000:.1f}万"
        return str(num)

    @staticmethod
    def _format_date(timestamp):
        """格式化日期"""
        if not timestamp:
            return "未知"
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

    @staticmethod
    def aid_to_bvid(aid):
        """AV号转BV号"""
        table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
        tr = {}
        for i in range(58):
            tr[table[i]] = i
        
        s = [11, 10, 3, 8, 4, 6]
        xor = 177451812
        add = 8728348608
        
        aid = (aid ^ xor) + add
        r = list("BV1  4 1 7  ")
        for i in range(6):
            r[s[i]] = table[aid // 58 ** i % 58]
        
        return "".join(r)

    def parse_favorites(self, fid):
        """
        解析B站收藏夹信息
        
        Args:
            fid: 收藏夹ID
            
        Returns:
            dict: 收藏夹信息，包含 title, media_count, media_list 等
        """
        if not fid:
            return None

        try:
            # 先获取收藏夹基本信息
            info_url = f"https://api.bilibili.com/x/v3/fav/folder/info?media_id={fid}"
            
            user_agent = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            info_response = requests.get(
                url=info_url,
                timeout=10,
                headers={
                    "Referer": "https://www.bilibili.com",
                    "User-Agent": user_agent.random,
                },
            )

            if info_response.status_code != 200:
                self.logger.warning(f"收藏夹信息API请求失败: {info_response.status_code}")
                return None

            info_result = info_response.json()
            if info_result.get("code") != 0:
                self.logger.warning(f"收藏夹信息API返回错误: {info_result.get('message')}")
                return None

            folder_info = info_result.get("data", {})
            if not folder_info:
                return None

            fav_title = folder_info.get("title", "未知收藏夹")
            media_count = folder_info.get("media_count", 0)
            upper_name = folder_info.get("upper", {}).get("name", "未知用户")

            # 获取收藏夹内媒体列表（最多获取前20个）
            media_list_url = f"https://api.bilibili.com/x/v3/fav/resource/list?media_id={fid}&pn=1&ps=20&platform=web"
            
            media_response = requests.get(
                url=media_list_url,
                timeout=10,
                headers={
                    "Referer": "https://www.bilibili.com",
                    "User-Agent": user_agent.random,
                },
            )

            media_list = []
            if media_response.status_code == 200:
                media_result = media_response.json()
                if media_result.get("code") == 0:
                    data = media_result.get("data")
                    if data:
                        medias = data.get("medias") or []
                        for media in medias:
                            if media.get("type") == 2:  # 视频类型
                                media_list.append({
                                    "bvid": media.get("bvid", ""),
                                    "title": media.get("title", "未知标题"),
                                    "author": media.get("upper", {}).get("name", "未知作者"),
                                    "duration": self._format_duration(media.get("duration", 0)),
                                    "view": self._format_count(media.get("cnt_info", {}).get("play", 0)),
                                    "pubdate": self._format_date(media.get("pubtime", 0)),
                                })

            return {
                "fid": fid,
                "title": fav_title,
                "upper_name": upper_name,
                "media_count": media_count,
                "media_list": media_list,
                "display_count": len(media_list),
            }

        except Exception as e:
            self.logger.error(f"解析B站收藏夹失败: {e}")
            return None