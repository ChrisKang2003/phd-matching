"""
动态抓取器
使用Playwright进行动态渲染
"""
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

from BrowserManager.base_manager import BaseBrowserManager
from core.browser_session import BrowserSession
from core.exceptions import BrowserNotRunningError, PageLoadError
from fetcher.static_fetcher import FetchResult


class DynamicFetcher:
    """动态抓取器 - 使用Playwright"""
    
    def __init__(
        self,
        browser_manager: BaseBrowserManager,
        wait_for_load: bool = True,
        wait_timeout: int = 10000,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化动态抓取器
        
        Args:
            browser_manager: 浏览器管理器
            wait_for_load: 是否等待页面加载完成
            wait_timeout: 等待超时时间（毫秒）
            logger: 日志记录器
        """
        self.browser_manager = browser_manager
        self.wait_for_load = wait_for_load
        self.wait_timeout = wait_timeout
        self.logger = logger or logging.getLogger("dynamic_fetcher")
    
    async def fetch(self, url: str) -> FetchResult:
        """
        使用浏览器抓取URL的HTML内容
        
        Args:
            url: 要抓取的URL
            
        Returns:
            FetchResult: 抓取结果
        """
        session = None
        page = None
        
        try:
            # 创建浏览器会话
            session = BrowserSession(
                self.browser_manager,
                self.logger,
                enable_anti_detection=True
            )
            
            # 打开URL
            self.logger.info(f"动态抓取: {url}")
            page = await session.open_url(
                url,
                wait_for_load=self.wait_for_load,
                wait_timeout=self.wait_timeout,
                wait_for_redirect=False
            )
            
            # 获取HTML内容
            html = await page.content()
            current_url = page.url
            
            # 获取响应头（Playwright不直接提供，使用默认值）
            headers = {
                'Content-Type': 'text/html',
                'URL': current_url
            }
            
            result = FetchResult(
                url=current_url,
                html=html,
                status_code=200,  # Playwright不提供状态码，假设成功
                headers=headers,
                fetched_at=datetime.now(),
                success=True
            )
            
            self.logger.info(f"✅ 动态抓取成功: {url} ({len(html)} 字节)")
            return result
            
        except (BrowserNotRunningError, PageLoadError) as e:
            self.logger.error(f"❌ 动态抓取失败: {url}, 错误: {e}")
            return FetchResult(
                url=url,
                html="",
                status_code=0,
                headers={},
                fetched_at=datetime.now(),
                success=False,
                error=str(e)
            )
            
        except Exception as e:
            self.logger.error(f"❌ 动态抓取异常: {url}, 错误: {e}", exc_info=True)
            return FetchResult(
                url=url,
                html="",
                status_code=0,
                headers={},
                fetched_at=datetime.now(),
                success=False,
                error=str(e)
            )
            
        finally:
            # 清理资源
            if page:
                try:
                    await page.close()
                except Exception as e:
                    self.logger.warning(f"关闭页面时出错: {e}")
            
            if session:
                try:
                    await session.close()
                except Exception as e:
                    self.logger.warning(f"关闭会话时出错: {e}")

