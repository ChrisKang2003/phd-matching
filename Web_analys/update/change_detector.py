"""
变更检测
通过hash检测页面内容是否发生变化
"""
import sys
import logging
from pathlib import Path
from typing import Optional

# 添加 utils 目录到路径
utils_path = Path(__file__).parent.parent.parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

try:
    from utils.hash_utils import calculate_content_hash
except ImportError:
    from hash_utils import calculate_content_hash


class ChangeDetector:
    """变更检测器"""
    
    def __init__(
        self,
        exclude_tags: Optional[list] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化变更检测器
        
        Args:
            exclude_tags: 要排除的标签列表（如时间、脚注、导航等）
            logger: 日志记录器
        """
        self.exclude_tags = exclude_tags or ['time', 'footer', 'nav', 'script', 'style', 'meta']
        self.logger = logger or logging.getLogger("change_detector")
    
    def calculate_hash(self, html: str) -> str:
        """
        计算HTML内容的hash值
        
        Args:
            html: HTML内容
            
        Returns:
            str: hash值
        """
        return calculate_content_hash(html, self.exclude_tags)
    
    def is_changed(self, current_html: str, previous_hash: str) -> bool:
        """
        检测内容是否发生变化
        
        Args:
            current_html: 当前HTML内容
            previous_hash: 之前的hash值
            
        Returns:
            bool: 是否发生变化
        """
        current_hash = self.calculate_hash(current_html)
        changed = current_hash != previous_hash
        
        if changed:
            self.logger.debug(f"检测到内容变化: {previous_hash[:8]} -> {current_hash[:8]}")
        else:
            self.logger.debug(f"内容未变化: {current_hash[:8]}")
        
        return changed

