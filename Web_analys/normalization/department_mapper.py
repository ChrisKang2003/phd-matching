"""
部门层级统一
统一不同学校的部门层级结构（School → College → Dept → Program）
"""
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


class DepartmentMapper:
    """部门层级映射器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化部门映射器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger("department_mapper")
    
    def normalize_hierarchy(
        self,
        department: str,
        university: str,
        college: Optional[str] = None,
        school: Optional[str] = None
    ) -> Dict[str, str]:
        """
        规范化部门层级
        
        Args:
            department: 部门名称
            university: 大学名称
            college: 学院名称（可选）
            school: 学院名称（可选，与college类似）
            
        Returns:
            Dict[str, str]: 规范化后的层级结构
                {
                    'university': '大学名称',
                    'school': '学院名称',
                    'college': '学院名称',
                    'department': '系名称',
                    'program': None
                }
        """
        normalized = {
            'university': university.strip() if university else '',
            'school': '',
            'college': '',
            'department': department.strip() if department else '',
            'program': None
        }
        
        # 处理college和school（有些学校用college，有些用school）
        if college:
            normalized['college'] = college.strip()
            normalized['school'] = college.strip()  # 统一使用school
        elif school:
            normalized['school'] = school.strip()
            normalized['college'] = school.strip()  # 也设置college
        
        return normalized
    
    def extract_hierarchy_from_text(self, text: str) -> Dict[str, Optional[str]]:
        """
        从文本中提取部门层级
        
        Args:
            text: 包含部门信息的文本
            
        Returns:
            Dict[str, Optional[str]]: 提取的层级信息
        """
        hierarchy = {
            'school': None,
            'college': None,
            'department': None,
            'program': None
        }
        
        # 简单的关键词匹配
        import re
        
        # 查找School
        school_match = re.search(r'School\s+of\s+([^,\n]+)', text, re.I)
        if school_match:
            hierarchy['school'] = school_match.group(1).strip()
        
        # 查找College
        college_match = re.search(r'College\s+of\s+([^,\n]+)', text, re.I)
        if college_match:
            hierarchy['college'] = college_match.group(1).strip()
        
        # 查找Department
        dept_match = re.search(r'Department\s+of\s+([^,\n]+)', text, re.I)
        if dept_match:
            hierarchy['department'] = dept_match.group(1).strip()
        
        return hierarchy

