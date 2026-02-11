"""
人名解析
处理姓名格式、中间名、缩写等
"""
import sys
import re
import logging
from pathlib import Path
from typing import Dict, Optional, List

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


class NameParser:
    """人名解析器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化人名解析器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger("name_parser")
    
    def parse(self, name: str) -> Dict[str, str]:
        """
        解析姓名
        
        Args:
            name: 原始姓名
            
        Returns:
            Dict[str, str]: 解析后的姓名信息
                {
                    'full_name': '完整姓名',
                    'first_name': '名',
                    'last_name': '姓',
                    'middle_name': '中间名（如果有）',
                    'normalized': '规范化后的姓名（姓在前）'
                }
        """
        if not name:
            return {
                'full_name': '',
                'first_name': '',
                'last_name': '',
                'middle_name': '',
                'normalized': ''
            }
        
        # 清理姓名
        name = ' '.join(name.split())
        
        # 分割姓名
        parts = name.split()
        
        if len(parts) == 0:
            return {
                'full_name': name,
                'first_name': '',
                'last_name': '',
                'middle_name': '',
                'normalized': name
            }
        elif len(parts) == 1:
            # 只有一个部分，假设是姓
            return {
                'full_name': name,
                'first_name': '',
                'last_name': parts[0],
                'middle_name': '',
                'normalized': parts[0]
            }
        elif len(parts) == 2:
            # 两个部分：名 姓 或 姓 名
            # 假设是 名 姓（英文常见格式）
            return {
                'full_name': name,
                'first_name': parts[0],
                'last_name': parts[1],
                'middle_name': '',
                'normalized': f"{parts[1]}, {parts[0]}"  # 姓在前格式
            }
        else:
            # 三个或更多部分
            # 假设最后一个部分是姓，第一个部分是名，中间是中间名
            first_name = parts[0]
            last_name = parts[-1]
            middle_name = ' '.join(parts[1:-1]) if len(parts) > 2 else ''
            
            return {
                'full_name': name,
                'first_name': first_name,
                'last_name': last_name,
                'middle_name': middle_name,
                'normalized': f"{last_name}, {first_name} {middle_name}".strip()  # 姓在前格式
            }
    
    def normalize(self, name: str) -> str:
        """
        规范化姓名（姓在前格式）
        
        Args:
            name: 原始姓名
            
        Returns:
            str: 规范化后的姓名（姓在前）
        """
        parsed = self.parse(name)
        return parsed['normalized']
    
    def extract_initials(self, name: str) -> str:
        """
        提取姓名首字母
        
        Args:
            name: 姓名
            
        Returns:
            str: 首字母（如 "J. D. Smith" -> "JDS"）
        """
        parts = name.split()
        initials = [part[0].upper() for part in parts if part]
        return ''.join(initials)

