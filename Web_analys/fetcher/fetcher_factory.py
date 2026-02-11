"""
抓取器工厂
自动选择静态或动态抓取器
"""
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Callable

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

from BrowserManager.base_manager import BaseBrowserManager
from fetcher.static_fetcher import StaticFetcher, FetchResult
from fetcher.dynamic_fetcher import DynamicFetcher


class FetcherFactory:
    """抓取器工厂 - 自动选择静态/动态抓取"""
    
    def __init__(
        self,
        browser_manager: Optional[BaseBrowserManager] = None,
        prefer_static: bool = True,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
        browser_manager_factory: Optional[Callable[[], Optional[BaseBrowserManager]]] = None
    ):
        """
        初始化抓取器工厂
        
        Args:
            browser_manager: 浏览器管理器（用于动态抓取，可选，可延迟创建）
            prefer_static: 是否优先使用静态抓取
            config: 配置字典
            logger: 日志记录器
            browser_manager_factory: 浏览器管理器工厂函数（延迟创建时使用）
        """
        self.browser_manager = browser_manager
        self.prefer_static = prefer_static
        self.config = config or {}
        self.logger = logger or logging.getLogger("fetcher_factory")
        self.browser_manager_factory = browser_manager_factory
        
        # 创建静态抓取器
        self.static_fetcher = StaticFetcher(
            timeout=self.config.get('timeout', 30),
            retry_times=self.config.get('retry_times', 3),
            logger=self.logger
        )
        
        # 创建动态抓取器（如果提供了浏览器管理器）
        self.dynamic_fetcher = None
        if self.browser_manager:
            self.dynamic_fetcher = DynamicFetcher(
                browser_manager=self.browser_manager,
                wait_for_load=self.config.get('wait_for_load', True),
                wait_timeout=self.config.get('wait_timeout', 10000),
                logger=self.logger
            )
    
    def _ensure_browser_manager(self) -> bool:
        """
        确保浏览器管理器已创建（延迟创建）
        
        Returns:
            bool: 是否成功创建浏览器管理器
        """
        if self.browser_manager:
            return True
        
        if self.browser_manager_factory:
            try:
                self.browser_manager = self.browser_manager_factory()
                if self.browser_manager:
                    # 创建动态抓取器
                    self.dynamic_fetcher = DynamicFetcher(
                        browser_manager=self.browser_manager,
                        wait_for_load=self.config.get('wait_for_load', True),
                        wait_timeout=self.config.get('wait_timeout', 10000),
                        logger=self.logger
                    )
                    return True
            except Exception as e:
                self.logger.error(f"延迟创建浏览器管理器失败: {e}")
                return False
        
        return False
    
    async def fetch(self, url: str, force_dynamic: bool = False) -> FetchResult:
        """
        抓取URL（自动选择静态或动态）
        
        Args:
            url: 要抓取的URL
            force_dynamic: 是否强制使用动态抓取
            
        Returns:
            FetchResult: 抓取结果
        """
        # 如果强制使用动态抓取
        if force_dynamic:
            if self.dynamic_fetcher:
                self.logger.info(f"强制使用动态抓取: {url}")
                return await self.dynamic_fetcher.fetch(url)
            else:
                self.logger.warning(f"未提供浏览器管理器，无法使用动态抓取，回退到静态抓取: {url}")
                return self.static_fetcher.fetch(url)
        
        # 优先使用静态抓取
        if self.prefer_static:
            result = self.static_fetcher.fetch(url)
            
            # 如果静态抓取成功，检查是否需要JS渲染
            if result.success:
                needs_js = self.static_fetcher._check_needs_js(result.html)
                
                if needs_js:
                    # 需要JS渲染，延迟创建浏览器管理器
                    if self._ensure_browser_manager() and self.dynamic_fetcher:
                        self.logger.info(f"⚠️  检测到需要JS渲染，切换到动态抓取: {url}")
                        self.logger.debug(f"   静态抓取大小: {len(result.html)} 字节")
                        dynamic_result = await self.dynamic_fetcher.fetch(url)
                        self.logger.debug(f"   动态抓取大小: {len(dynamic_result.html)} 字节")
                        return dynamic_result
                    else:
                        self.logger.warning(f"需要JS渲染但无法创建浏览器管理器，使用静态抓取结果: {url}")
                else:
                    self.logger.debug(f"✅ 静态抓取内容完整，无需JS渲染: {url} ({len(result.html)} 字节)")
                
                return result
            else:
                # 静态抓取失败，尝试动态抓取（延迟创建浏览器管理器）
                if self._ensure_browser_manager() and self.dynamic_fetcher:
                    self.logger.info(f"静态抓取失败，尝试动态抓取: {url}")
                    return await self.dynamic_fetcher.fetch(url)
                else:
                    self.logger.warning(f"静态抓取失败且无法创建浏览器管理器: {url}")
                    return result
        else:
            # 优先使用动态抓取（延迟创建浏览器管理器）
            if self._ensure_browser_manager() and self.dynamic_fetcher:
                return await self.dynamic_fetcher.fetch(url)
            else:
                self.logger.warning(f"未提供浏览器管理器，回退到静态抓取: {url}")
                return self.static_fetcher.fetch(url)
    
    def get_static_fetcher(self) -> StaticFetcher:
        """获取静态抓取器"""
        return self.static_fetcher
    
    def get_dynamic_fetcher(self) -> Optional[DynamicFetcher]:
        """获取动态抓取器"""
        return self.dynamic_fetcher

