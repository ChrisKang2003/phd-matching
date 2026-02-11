"""
重试策略
实现指数退避、最大重试次数、黑名单机制
"""
import sys
import logging
import asyncio
from pathlib import Path
from typing import Set, Optional
from datetime import datetime, timedelta

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


class RetryStrategy:
    """重试策略管理器"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化重试策略
        
        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            exponential_base: 指数退避的底数
            logger: 日志记录器
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.logger = logger or logging.getLogger("retry_strategy")
        self._blacklist: Set[str] = set()  # URL黑名单
        self._blacklist_until: Dict[str, datetime] = {}  # 临时黑名单（带过期时间）
    
    def calculate_delay(self, retry_count: int) -> float:
        """
        计算重试延迟时间（指数退避）
        
        Args:
            retry_count: 当前重试次数
            
        Returns:
            float: 延迟时间（秒）
        """
        delay = self.base_delay * (self.exponential_base ** retry_count)
        return min(delay, self.max_delay)
    
    async def wait_before_retry(self, retry_count: int) -> None:
        """
        在重试前等待（指数退避）
        
        Args:
            retry_count: 当前重试次数
        """
        delay = self.calculate_delay(retry_count)
        self.logger.debug(f"等待 {delay:.2f} 秒后重试（第 {retry_count} 次）")
        await asyncio.sleep(delay)
    
    def is_blacklisted(self, url: str) -> bool:
        """
        检查URL是否在黑名单中
        
        Args:
            url: 要检查的URL
            
        Returns:
            bool: 是否在黑名单中
        """
        # 检查永久黑名单
        if url in self._blacklist:
            return True
        
        # 检查临时黑名单
        if url in self._blacklist_until:
            if datetime.now() < self._blacklist_until[url]:
                return True
            else:
                # 过期了，移除
                del self._blacklist_until[url]
        
        return False
    
    def add_to_blacklist(self, url: str, permanent: bool = False, until: Optional[datetime] = None):
        """
        将URL添加到黑名单
        
        Args:
            url: 要添加的URL
            permanent: 是否永久黑名单
            until: 临时黑名单的过期时间
        """
        if permanent:
            self._blacklist.add(url)
            self.logger.warning(f"将URL添加到永久黑名单: {url}")
        elif until:
            self._blacklist_until[url] = until
            self.logger.warning(f"将URL添加到临时黑名单，直到: {until}: {url}")
        else:
            # 默认临时黑名单1小时
            until = datetime.now() + timedelta(hours=1)
            self._blacklist_until[url] = until
            self.logger.warning(f"将URL添加到临时黑名单（1小时）: {url}")
    
    def remove_from_blacklist(self, url: str) -> bool:
        """
        从黑名单移除URL
        
        Args:
            url: 要移除的URL
            
        Returns:
            bool: 是否移除成功
        """
        removed = False
        
        if url in self._blacklist:
            self._blacklist.remove(url)
            removed = True
        
        if url in self._blacklist_until:
            del self._blacklist_until[url]
            removed = True
        
        if removed:
            self.logger.info(f"从黑名单移除URL: {url}")
        
        return removed
    
    def should_retry(self, retry_count: int, url: str) -> bool:
        """
        判断是否应该重试
        
        Args:
            retry_count: 当前重试次数
            url: 任务URL
            
        Returns:
            bool: 是否应该重试
        """
        # 检查黑名单
        if self.is_blacklisted(url):
            self.logger.debug(f"URL在黑名单中，不重试: {url}")
            return False
        
        # 检查重试次数
        if retry_count >= self.max_retries:
            self.logger.debug(f"已达到最大重试次数 {self.max_retries}，不重试")
            return False
        
        return True

