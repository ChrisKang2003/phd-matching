"""
静态抓取器
使用requests/httpx进行静态HTML抓取
"""
import sys
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


@dataclass
class FetchResult:
    """抓取结果"""
    url: str
    html: str
    status_code: int
    headers: Dict[str, str]
    fetched_at: datetime
    success: bool
    error: Optional[str] = None


class StaticFetcher:
    """静态抓取器 - 使用requests库"""
    
    def __init__(
        self,
        timeout: int = 30,
        retry_times: int = 3,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化静态抓取器
        
        Args:
            timeout: 请求超时时间（秒）
            retry_times: 重试次数
            logger: 日志记录器
        """
        self.timeout = timeout
        self.retry_times = retry_times
        self.logger = logger or logging.getLogger("static_fetcher")
        
        # 默认请求头
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def fetch(self, url: str, headers: Optional[Dict[str, str]] = None) -> FetchResult:
        """
        抓取URL的HTML内容
        
        Args:
            url: 要抓取的URL
            headers: 自定义请求头
            
        Returns:
            FetchResult: 抓取结果
        """
        request_headers = {**self.default_headers}
        if headers:
            request_headers.update(headers)
        
        last_error = None
        
        for attempt in range(self.retry_times):
            try:
                self.logger.debug(f"静态抓取尝试 {attempt + 1}/{self.retry_times}: {url}")
                
                response = requests.get(
                    url,
                    headers=request_headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                response.raise_for_status()
                
                # 调试输出：响应信息
                content_encoding = response.headers.get('Content-Encoding', 'none')
                content_type = response.headers.get('Content-Type', 'unknown')
                self.logger.info(
                    f"📡 响应信息 - Status: {response.status_code}, "
                    f"Content-Type: {content_type}, "
                    f"Content-Encoding: {content_encoding}, "
                    f"Content-Length: {response.headers.get('Content-Length', 'unknown')}"
                )
                
                # 检查是否有重定向
                final_url = response.url
                if final_url != url:
                    self.logger.info(f"URL 重定向: {url} -> {final_url}")
                
                # 检查内容类型
                if 'text/html' not in content_type.lower() and 'application/xhtml' not in content_type.lower():
                    self.logger.warning(f"非HTML内容类型: {content_type}")
                
                # 获取HTML内容（requests会自动处理gzip/deflate/br压缩，如果安装了brotli/brotlicffi库）
                html = response.text
                self.logger.info(f"📥 获取HTML内容: {len(html)} 字符")
                self.logger.info(f"   前100字符: {repr(html[:100])}")
                
                # 验证HTML内容是否有效（检测是否可能是未解压的二进制数据）
                if not html or len(html) < 100:
                    self.logger.warning(f"⚠️ 获取的HTML内容异常短: {len(html) if html else 0} 字符")
                else:
                    # 检查是否以HTML开头
                    html_start = html.strip()[:50].lower()
                    is_valid_html = html_start.startswith(('<!', '<html'))
                    self.logger.info(f"🔍 HTML验证 - 以HTML开头: {is_valid_html}")
                    self.logger.info(f"   前50字符: {repr(html_start[:50])}")
                    
                    # 检查可打印字符比例（即使HTML开头正确，也要检查整体）
                    printable_count = sum(1 for c in html[:500] if c.isprintable() or c.isspace())
                    printable_ratio = printable_count / min(500, len(html))
                    self.logger.info(f"   可打印字符比例: {printable_ratio:.2%} ({printable_count}/500)")
                    
                    # 只有在检测到问题时才手动解压
                    if not is_valid_html or printable_ratio < 0.7:
                        self.logger.warning(f"⚠️ 检测到问题 - HTML开头: {is_valid_html}, 可打印字符比例: {printable_ratio:.2%}")
                        
                        if printable_ratio < 0.7:
                            # 可能是未解压的二进制数据，尝试手动解压
                            self.logger.error(
                                f"⚠️ 检测到二进制数据（Content-Encoding: {content_encoding}），"
                                f"可打印字符比例: {printable_ratio:.2%}，尝试手动解压..."
                            )
                            
                            # 如果是Brotli压缩，尝试手动解压
                            if content_encoding.lower() == 'br':
                                try:
                                    # 尝试导入brotli（支持brotli和brotlicffi）
                                    try:
                                        import brotli
                                    except ImportError:
                                        import brotlicffi as brotli
                                    html = brotli.decompress(response.content).decode('utf-8')
                                    self.logger.info(f"✅ 使用brotli手动解压成功: {len(html)} 字符")
                                    # 再次验证
                                    if html.strip()[:50].lower().startswith(('<!', '<html')):
                                        self.logger.info("✅ 解压后的内容验证通过")
                                    else:
                                        raise ValueError("解压后的内容仍然不是有效的HTML")
                                except ImportError:
                                    self.logger.error("无法解压Brotli内容，请安装: pip install brotli 或 pip install brotlicffi")
                                    raise ValueError("无法解压Brotli压缩内容，请安装brotli或brotlicffi库")
                                except Exception as e:
                                    self.logger.error(f"手动解压Brotli失败: {e}")
                                    raise
                            else:
                                raise ValueError(f"获取的内容格式异常，可能是未正确解压的压缩数据")
                    else:
                        self.logger.debug("✅ HTML内容验证通过")
                
                # 检查是否需要JS渲染（简单检测）
                needs_js = self._check_needs_js(html)
                
                if needs_js:
                    self.logger.debug(f"检测到可能需要JS渲染: {url}")
                
                result = FetchResult(
                    url=final_url,  # 使用最终URL（可能被重定向）
                    html=html,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    fetched_at=datetime.now(),
                    success=True
                )
                
                self.logger.info(f"✅ 静态抓取成功: {final_url} ({len(html)} 字节)")
                return result
                
            except requests.RequestException as e:
                last_error = str(e)
                self.logger.warning(f"静态抓取失败 (尝试 {attempt + 1}/{self.retry_times}): {url}, 错误: {e}")
                
                if attempt < self.retry_times - 1:
                    continue
        
        # 所有重试都失败
        result = FetchResult(
            url=url,
            html="",
            status_code=0,
            headers={},
            fetched_at=datetime.now(),
            success=False,
            error=last_error
        )
        
        self.logger.error(f"❌ 静态抓取最终失败: {url}, 错误: {last_error}")
        return result
    
    def _check_needs_js(self, html: str) -> bool:
        """
        简单检测HTML是否需要JS渲染
        
        Args:
            html: HTML内容
            
        Returns:
            bool: 是否需要JS渲染
        """
        html_lower = html.lower()
        
        # 检查是否有实际内容（如果内容很少，可能需要JS渲染）
        # 这是最可靠的指标：如果body内容很少，说明可能是JS渲染的
        if '<body' in html_lower:
            body_start = html_lower.find('<body')
            body_end = html_lower.find('</body>')
            if body_start != -1 and body_end != -1:
                body_content = html[body_start:body_end]
                # 移除script和style标签
                import re
                body_content = re.sub(r'<script[^>]*>.*?</script>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
                body_content = re.sub(r'<style[^>]*>.*?</style>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
                
                # 如果body内容少于500字符，很可能需要JS渲染
                body_text_length = len(body_content.strip())
                if body_text_length < 500:
                    self.logger.debug(f"检测到body内容过少 ({body_text_length} 字符)，可能需要JS渲染")
                    return True
        
        # 检查常见的JS渲染特征（更严格的检查）
        # 注意：noscript标签太常见，不应该作为判断依据
        js_indicators = [
            '<script type="application/json"',  # React/Vue等框架的JSON数据
            'data-react-helmet',  # React Helmet
            'ng-app=',  # Angular应用（需要等号，更精确）
            'v-bind:',  # Vue绑定（需要冒号，更精确）
            'window.__INITIAL_STATE__',  # 常见的前端状态
            'window.__PRELOADED_STATE__',  # 预加载状态
            'id="root"',  # React根元素（通常意味着SPA）
            'id="app"',  # Vue/React应用根元素
        ]
        
        for indicator in js_indicators:
            if indicator.lower() in html_lower:
                self.logger.debug(f"检测到JS渲染特征: {indicator}")
                return True
        
        return False

