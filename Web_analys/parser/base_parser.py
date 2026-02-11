"""
基础解析器接口
定义解析器的通用接口
"""
import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


class BaseParser(ABC):
    """基础解析器接口"""
    
    @abstractmethod
    def parse(self, html: str, url: str) -> Dict[str, Any]:
        """
        解析HTML内容
        
        Args:
            html: HTML内容
            url: 页面URL
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        pass
    
    @abstractmethod
    def get_confidence(self, html: str, url: str) -> float:
        """
        获取解析置信度（0-1之间）
        
        Args:
            html: HTML内容
            url: 页面URL
            
        Returns:
            float: 置信度（0-1）
        """
        pass
    
    def extract_structured_fields(self, html: str) -> Dict[str, Any]:
        """
        提取结构化字段（name, title, email, links, affiliation）
        
        Args:
            html: HTML内容
            
        Returns:
            Dict[str, Any]: 结构化字段
        """
        return {}
    
    def extract_text_fields(self, html: str) -> Dict[str, Any]:
        """
        提取文本字段（bio, research summary, publication snippets）
        
        Args:
            html: HTML内容
            
        Returns:
            Dict[str, Any]: 文本字段
        """
        return {}

