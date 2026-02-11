"""
邮箱还原
处理各种邮箱格式（隐藏、拆分、图片等）
"""
import sys
import re
import logging
from pathlib import Path
from typing import Optional

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


class EmailRestorer:
    """邮箱还原器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化邮箱还原器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger("email_restorer")
    
    def restore(self, email_text: str) -> Optional[str]:
        """
        还原邮箱地址
        
        处理格式：
        - "name [at] uni [dot] edu"
        - "name at uni dot edu"
        - JavaScript拼接的邮箱
        - 标准邮箱格式
        
        Args:
            email_text: 邮箱文本
            
        Returns:
            Optional[str]: 还原后的邮箱地址
        """
        if not email_text:
            return None
        
        email_text = email_text.strip()
        
        # 标准邮箱格式
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, email_text)
        if match:
            return match.group(0).lower()
        
        # 处理 "name [at] uni [dot] edu" 格式
        email_text = email_text.replace('[at]', '@')
        email_text = email_text.replace('[dot]', '.')
        email_text = email_text.replace(' at ', '@')
        email_text = email_text.replace(' dot ', '.')
        email_text = email_text.replace(' AT ', '@')
        email_text = email_text.replace(' DOT ', '.')
        
        # 再次尝试匹配
        match = re.search(email_pattern, email_text)
        if match:
            return match.group(0).lower()
        
        # 处理空格分隔的邮箱（如 "name @ uni . edu"）
        email_text = email_text.replace(' @ ', '@')
        email_text = email_text.replace(' . ', '.')
        email_text = email_text.replace(' @', '@')
        email_text = email_text.replace('@ ', '@')
        email_text = email_text.replace(' .', '.')
        email_text = email_text.replace('. ', '.')
        
        # 最后尝试匹配
        match = re.search(email_pattern, email_text)
        if match:
            return match.group(0).lower()
        
        self.logger.warning(f"无法还原邮箱: {email_text}")
        return None
    
    def extract_from_html(self, html: str) -> Optional[str]:
        """
        从HTML中提取邮箱
        
        Args:
            html: HTML内容
            
        Returns:
            Optional[str]: 邮箱地址
        """
        # 查找mailto链接
        mailto_pattern = r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
        match = re.search(mailto_pattern, html, re.I)
        if match:
            return match.group(1).lower()
        
        # 查找文本中的邮箱
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, html)
        if match:
            return match.group(0).lower()
        
        return None

