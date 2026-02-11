"""
页面内容保存器
负责保存页面的 HTML 内容和截图
"""
import sys
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from playwright.async_api import Page
from urllib.parse import urlparse
import requests

# 添加 utils 目录到路径
utils_path = Path(__file__).parent.parent.parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

from url_utils import url_to_folder_name
from core.exceptions import SaveError, BrowserNotRunningError, PageLoadError
from BrowserManager.base_manager import BaseBrowserManager
from core.browser_session import BrowserSession


class PageSaver:
    """页面内容保存器"""
    
    def __init__(
        self,
        output_dir: str,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化页面保存器
        
        Args:
            output_dir: 输出目录
            logger: 日志记录器
        """
        self.output_dir = Path(output_dir)
        self.logger = logger or logging.getLogger("page_saver")
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_file_paths(
        self, 
        url: str, 
        timestamp: Optional[datetime] = None
    ) -> tuple[str, str]:
        """
        生成 HTML 和截图文件路径
        
        Args:
            url: 页面 URL
            timestamp: 时间戳，如果为 None 则使用当前时间
            
        Returns:
            (html_path, screenshot_path): HTML 和截图文件路径元组
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # 生成文件名（基于时间戳）
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # 根据 URL 创建文件夹
        folder_name = url_to_folder_name(url)
        url_dir = self.output_dir / folder_name
        url_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件路径
        html_path = url_dir / f"{timestamp_str}.html"
        screenshot_path = url_dir / f"{timestamp_str}.png"
        
        return str(html_path), str(screenshot_path)
    
    async def save_html(self, page: Page, html_path: str) -> str:
        """
        保存页面 HTML
        
        Args:
            page: Playwright Page 对象
            html_path: HTML 文件保存路径
            
        Returns:
            保存的 HTML 文件路径
            
        Raises:
            SaveError: 保存失败
        """
        try:
            # 获取 HTML 内容
            html_content = await page.content()
            
            # 保存到文件
            html_file = Path(html_path)
            html_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"✅ HTML 已保存: {html_path}")
            return str(html_path)
            
        except Exception as e:
            raise SaveError(html_path, f"保存 HTML 失败: {str(e)}") from e
    
    async def save_screenshot(
        self,
        page: Page,
        screenshot_path: str,
        full_page: bool = True
    ) -> str:
        """
        保存页面截图
        
        Args:
            page: Playwright Page 对象
            screenshot_path: 截图文件保存路径
            full_page: 是否截取整个页面
            
        Returns:
            保存的截图文件路径
            
        Raises:
            SaveError: 保存失败
        """
        try:
            # 确保目录存在
            screenshot_file = Path(screenshot_path)
            screenshot_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存截图
            await page.screenshot(path=str(screenshot_path), full_page=full_page)
            
            self.logger.info(f"✅ 截图已保存: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            raise SaveError(screenshot_path, f"保存截图失败: {str(e)}") from e
    
    def save_url_html_simple(self, url: str, save_path: str) -> None:
        """
        使用 requests 库保存网页 HTML（简单快速版本）
        适用于静态页面或服务器端渲染的页面
        
        Args:
            url: 要保存的网页 URL
            save_path: HTML 文件保存路径
            
        Raises:
            SaveError: 保存失败
        """
        try:
            # 发送 HTTP 请求获取 HTML
            self.logger.info(f"正在获取网页: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 确保保存目录存在
            html_file = Path(save_path)
            html_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存 HTML 内容
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            self.logger.info(f"✅ HTML 已保存: {save_path}")
            
        except requests.RequestException as e:
            raise SaveError(save_path, f"获取网页失败: {str(e)}") from e
        except Exception as e:
            raise SaveError(save_path, f"保存 HTML 失败: {str(e)}") from e
    
    async def save_url_html_full(
        self, 
        url: str, 
        save_path: str, 
        browser_manager: BaseBrowserManager,
        wait_for_load: bool = True,
        wait_timeout: int = 10000
    ) -> None:
        """
        使用 Playwright 保存网页 HTML（完整渲染版本）
        适用于需要 JavaScript 渲染的动态页面
        
        Args:
            url: 要保存的网页 URL
            save_path: HTML 文件保存路径
            browser_manager: 浏览器管理器实例
            wait_for_load: 是否等待页面加载完成
            wait_timeout: 等待超时时间（毫秒）
            
        Raises:
            SaveError: 保存失败
            BrowserNotRunningError: 浏览器未运行
            PageLoadError: 页面加载失败
        """
        session = None
        page = None
        
        try:
            # 创建浏览器会话
            session = BrowserSession(
                browser_manager,
                self.logger,
                enable_anti_detection=True
            )
            
            # 打开 URL
            self.logger.info(f"正在打开网页: {url}")
            page = await session.open_url(
                url,
                wait_for_load=wait_for_load,
                wait_timeout=wait_timeout,
                wait_for_redirect=False
            )
            
            # 使用现有的 save_html 方法保存
            await self.save_html(page, save_path)
            
        except Exception as e:
            # 如果是已知异常，直接抛出
            if isinstance(e, (SaveError, BrowserNotRunningError, PageLoadError)):
                raise
            
            # 其他异常包装为 SaveError
            raise SaveError(save_path, f"保存网页 HTML 失败: {str(e)}") from e
            
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

