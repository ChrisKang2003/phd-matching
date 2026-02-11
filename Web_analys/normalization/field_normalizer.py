"""
字段规范化
统一不同学校的字段格式
"""
import sys
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


class FieldNormalizer:
    """字段规范化器"""
    
    # 职称映射表
    TITLE_MAPPING = {
        # 教授
        'professor': 'Professor',
        'prof.': 'Professor',
        'prof': 'Professor',
        'full professor': 'Professor',
        # 副教授
        'associate professor': 'Associate Professor',
        'assoc. prof.': 'Associate Professor',
        'assoc prof': 'Associate Professor',
        'associate prof': 'Associate Professor',
        # 助理教授
        'assistant professor': 'Assistant Professor',
        'asst. prof.': 'Assistant Professor',
        'asst prof': 'Assistant Professor',
        'assistant prof': 'Assistant Professor',
        # 讲师
        'lecturer': 'Lecturer',
        'senior lecturer': 'Senior Lecturer',
        # 兼职
        'adjunct professor': 'Adjunct Professor',
        'adjunct': 'Adjunct Professor',
        # 研究
        'research scientist': 'Research Scientist',
        'research professor': 'Research Professor',
        'research associate': 'Research Associate',
        'research assistant': 'Research Assistant',
    }
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化字段规范化器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger("field_normalizer")
    
    def normalize_title(self, title: str) -> Optional[str]:
        """
        规范化职称
        
        Args:
            title: 原始职称
            
        Returns:
            Optional[str]: 规范化后的职称
        """
        if not title:
            return None
        
        title_lower = title.lower().strip()
        
        # 直接匹配
        if title_lower in self.TITLE_MAPPING:
            return self.TITLE_MAPPING[title_lower]
        
        # 模糊匹配
        for key, value in self.TITLE_MAPPING.items():
            if key in title_lower:
                return value
        
        # 如果都不匹配，返回原始值（首字母大写）
        return title.strip().title()
    
    def normalize_department(self, department: str) -> Optional[str]:
        """
        规范化部门名称
        
        Args:
            department: 原始部门名称
            
        Returns:
            Optional[str]: 规范化后的部门名称
        """
        if not department:
            return None
        
        # 移除多余空格
        normalized = ' '.join(department.split())
        
        # 统一常见缩写
        abbreviations = {
            'CS': 'Computer Science',
            'EE': 'Electrical Engineering',
            'CE': 'Computer Engineering',
            'ME': 'Mechanical Engineering',
            'IS': 'Information Systems',
            'AI': 'Artificial Intelligence',
            'ML': 'Machine Learning',
        }
        
        # 如果整个字符串是缩写，展开
        if normalized.upper() in abbreviations:
            return abbreviations[normalized.upper()]
        
        return normalized
    
    def normalize(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        规范化实体字段
        
        Args:
            entity: 原始实体数据
            
        Returns:
            Dict[str, Any]: 规范化后的实体数据
        """
        normalized = entity.copy()
        
        # 规范化职称
        if 'title' in normalized:
            normalized['title'] = self.normalize_title(normalized['title'])
        
        # 规范化部门
        if 'department' in normalized:
            normalized['department'] = self.normalize_department(normalized['department'])
        
        # 规范化大学名称（移除多余空格）
        if 'university' in normalized:
            normalized['university'] = ' '.join(normalized['university'].split())
        
        return normalized

